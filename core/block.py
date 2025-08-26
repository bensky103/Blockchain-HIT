"""
Block implementation for blockchain.
"""

import json
import hashlib
import time
from typing import List, Dict, Any, Optional
from .tx import Tx

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
            "miner_address": self.miner_address
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
        return cls(
            index=data["index"],
            prev_hash=data["prev_hash"],
            merkle_root=data["merkle_root"],
            timestamp=data["timestamp"],
            nonce=data["nonce"],
            miner_address=data["miner_address"]
        )
    
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
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert block to dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the block.
        """
        return {
            "header": self.header.to_dict(),
            "txs": [tx.to_dict() for tx in self.txs]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Block':
        """
        Create a block from dictionary.
        
        Args:
            data (Dict[str, Any]): Dictionary representation of the block.
        
        Returns:
            Block: New block instance.
        """
        header = BlockHeader.from_dict(data["header"])
        txs = [Tx.from_dict(tx_data) for tx_data in data["txs"]]
        
        return cls(header=header, txs=txs)
    
    @classmethod
    def create_header(cls, index: int, prev_hash: str, miner_address: str) -> BlockHeader:
        """
        Create a block header with basic fields set.
        
        Args:
            index (int): Block height/index in the chain.
            prev_hash (str): Hash of the previous block.
            miner_address (str): Address of the miner.
            
        Returns:
            BlockHeader: Block header with defaults set.
        """
        # Create a temporary merkle root (proper implementation would build from txs)
        merkle_root = hashlib.sha256(f"merkle_{index}".encode('utf-8')).hexdigest()
        
        return BlockHeader(
            index=index,
            prev_hash=prev_hash,
            merkle_root=merkle_root,
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
            
        # Create a simple merkle root for genesis (hash of "genesis")
        merkle_root = hashlib.sha256("genesis".encode('utf-8')).hexdigest()
        
        header = BlockHeader(
            index=0,
            prev_hash="0" * 64,  # 64 zeros for genesis block
            merkle_root=merkle_root,
            timestamp=int(time.time()),
            nonce=0,
            miner_address=miner_address
        )
        
        return cls(header=header, txs=initial_txs)
