"""
Block implementation for blockchain.
"""

import json
import hashlib
import time
from typing import List, Dict, Any, Optional
from .tx import Tx
from blockchain_lab.crypto.merkle import merkle_root as compute_merkle_root

class BlockHeader:
    """
    Represents a block header in the blockchain.
    
    Attributes:
        index (int): Block height/index in the chain.
        prev_hash (str): Hash of the previous block.
        merkle_root (str): Merkle root of transactions.
        timestamp (int): Unix timestamp of block creation.
        nonce (int): Nonce used for mining.
        miner_address (str): Address of the miner who created this block.
    """
    
    def __init__(
        self, 
        index: int, 
        prev_hash: str, 
        merkle_root: str, 
        timestamp: int, 
        nonce: int, 
        miner_address: str
    ):
        """
        Initialize a new BlockHeader.
        
        Args:
            index (int): Block height/index in the chain.
            prev_hash (str): Hash of the previous block.
            merkle_root (str): Merkle root of transactions.
            timestamp (int): Unix timestamp.
            nonce (int): Nonce for mining.
            miner_address (str): Address of the miner who created this block.
        """
        self.index = index
        self.prev_hash = prev_hash
        self.merkle_root = merkle_root
        self.timestamp = timestamp
        self.nonce = nonce
        self.miner_address = miner_address
        self.block_reward = 0
        self.burned_fees = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert block header to dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the block header.
        """
        return {
            "index": self.index,
            "prev_hash": self.prev_hash,
            "merkle_root": self.merkle_root,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "miner_address": self.miner_address,
            "block_reward": self.block_reward,
            "burned_fees": self.burned_fees
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BlockHeader':
        """
        Create a block header from dictionary.
        
        Args:
            data (Dict[str, Any]): Dictionary representation of the block header.
        
        Returns:
            BlockHeader: New block header instance.
        """
        new_header = cls(
            index=data["index"],
            prev_hash=data["prev_hash"],
            merkle_root=data["merkle_root"],
            timestamp=data["timestamp"],
            nonce=data["nonce"],
            miner_address=data["miner_address"]
        )
        new_header.block_reward = data.get("block_reward", 0)
        new_header.burned_fees = data.get("burned_fees", 0)
        return new_header
    
    def calculate_hash(self) -> str:
        """
        Calculate the hash of the block header.
        
        Returns:
            str: SHA-256 hash of the block header.
        """
        # Convert to canonical JSON (sorted keys, no whitespace)
        header_dict = self.to_dict()
        canonical_json = json.dumps(header_dict, sort_keys=True, separators=(',', ':'))
        
        # Calculate SHA-256 hash
        return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()


class Block:
    """
    Represents a block in the blockchain.
    
    Attributes:
        header (BlockHeader): Header of the block.
        txs (List[Tx]): List of transactions in the block.
    """
    
    def __init__(self, header: BlockHeader, txs: List[Tx]):
        """
        Initialize a new Block.
        
        Args:
            header (BlockHeader): Header of the block.
            txs (List[Tx]): List of transactions.
        """
        self.header = header
        self.txs = txs
    
    @property
    def block_hash(self) -> str:
        """
        Calculate the hash of the block (header only).
        
        Returns:
            str: Hash of the block.
        """
        return self.header.calculate_hash()
    
    def to_dict(self, include_witness: bool = False) -> Dict[str, Any]:
        """Convert block to dictionary.

        SegWit-style separation:
          - Transaction serialization excludes signatures & pubkeys (keeps txid stable / lean)
          - If include_witness=True, a separate 'witnesses' map (tx_id -> signature hex) is emitted.

        Args:
            include_witness (bool): Whether to include detached signatures map.

        Returns:
            Dict[str, Any]: Serialized block representation.
        """
        tx_dicts = [tx.to_dict(include_signature=False, include_pubkey=False) for tx in self.txs]
        block_dict: Dict[str, Any] = {
            "header": self.header.to_dict(),
            "txs": tx_dicts
        }
        if include_witness:
            witnesses: Dict[str, str] = {}
            for tx in self.txs:
                if tx.signature:
                    witnesses[tx.tx_id] = tx.signature.hex()
            if witnesses:
                block_dict["witnesses"] = witnesses
        return block_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Block':
        """Create a block instance from serialized dictionary.

        If a 'witnesses' map exists it will re-attach signatures to the Tx objects.
        """
        header = BlockHeader.from_dict(data["header"])
        witnesses: Dict[str, str] = data.get("witnesses", {})  # tx_id -> signature hex
        txs: List[Tx] = []
        for tx_data in data["txs"]:
            # Rehydrate transaction structure (signature excluded in canonical form)
            tx_obj = Tx.from_dict(tx_data)
            sig_hex = witnesses.get(tx_obj.tx_id)
            if sig_hex:
                tx_obj.signature = bytes.fromhex(sig_hex)
            txs.append(tx_obj)
        return cls(header=header, txs=txs)
    
    @classmethod
    def create_header(cls, index: int, prev_hash: str, miner_address: str, txs: Optional[List[Tx]] = None) -> BlockHeader:
        """Create a block header.

        If transactions are provided, compute a real Merkle root. Otherwise keep a placeholder
        (used mainly in tests that construct a header prior to attaching transactions).
        """
        if txs is not None:
            merkle_root_val = compute_merkle_root(txs)
        else:
            # Backwards compatible placeholder (still deterministic) – recommended to supply txs.
            merkle_root_val = hashlib.sha256(f"merkle_{index}".encode('utf-8')).hexdigest()
        return BlockHeader(
            index=index,
            prev_hash=prev_hash,
            merkle_root=merkle_root_val,
            timestamp=int(time.time()),
            nonce=0,
            miner_address=miner_address
        )
    
    @classmethod
    def create_genesis_block(cls, miner_address: str, initial_txs: List[Tx] = None) -> 'Block':
        """
        Create the genesis block.
        
        Args:
            miner_address (str): Address to receive the genesis block reward.
            initial_txs (List[Tx], optional): Initial transactions. Defaults to empty list.
        
        Returns:
            Block: Genesis block.
        """
        if initial_txs is None:
            initial_txs = []

        # Real Merkle root for provided initial transactions (empty list -> hash of empty list)
        merkle_root = compute_merkle_root(initial_txs)

        header = BlockHeader(
            index=0,
            prev_hash="0" * 64,  # 64 zeros for genesis block
            merkle_root=merkle_root,
            timestamp=int(time.time()),
            nonce=0,
            miner_address=miner_address
        )
        
        return cls(header=header, txs=initial_txs)
