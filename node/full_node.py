"""
Full node implementation.
"""

from typing import List, Tuple, Optional, Dict
from ..core.chain import Blockchain
from ..core.tx import Tx
from ..core.block import Block
from .mempool import Mempool
from ..crypto.merkle import merkle_proof, verify_proof
from ..crypto.bloom import BloomFilter

class FullNode:
    """
    Represents a full node in the blockchain network.
    
    Attributes:
        blockchain (Blockchain): The blockchain instance.
        mempool (Mempool): The memory pool for unconfirmed transactions.
        peers (list): List of connected peer nodes.
        block_blooms (Dict[int, BloomFilter]): Bloom filters for finalized blocks.
    """
    
    def __init__(self):
        """Initialize a new full node."""
        self.blockchain = Blockchain()
        self.mempool = Mempool()
        self.peers = []
        # Dictionary to store Bloom filters for each block indexed by block index
        self.block_blooms: Dict[int, BloomFilter] = {}
    
    def add_peer(self, peer_address):
        """
        Add a peer to the network.
        
        Args:
            peer_address (str): Address of the peer.
        """
        if peer_address not in self.peers:
            self.peers.append(peer_address)
    
    def broadcast_transaction(self, transaction):
        """
        Broadcast a transaction to all peers.
        
        Args:
            transaction: The transaction to broadcast.
        """
        # TODO: Implement peer-to-peer communication
        self.mempool.add_transaction(transaction)
    
    def sync_blockchain(self):
        """
        Synchronize the blockchain with peers.
        """
        # TODO: Implement blockchain synchronization
        pass
    
    def build_bloom_filter(self, block: Block) -> BloomFilter:
        """
        Build a Bloom filter for all transaction IDs in a block.
        
        Args:
            block (Block): The block to build a Bloom filter for.
            
        Returns:
            BloomFilter: A Bloom filter containing all transaction IDs in the block.
        """
        bloom = BloomFilter(m_bits=2048, k=3)
        
        # Add all transaction IDs to the Bloom filter
        for tx in block.txs:
            bloom.add(tx.tx_id.encode('utf-8'))
            
        return bloom
    
    def add_finalized_block(self, block: Block) -> None:
        """
        Add a finalized block to the blockchain and build a Bloom filter for it.
        
        Args:
            block (Block): The finalized block to add.
        """
        # Add block to blockchain (assuming the blockchain.add_block method exists)
        # In a real implementation, you would verify the block first
        if hasattr(self.blockchain, 'add_block'):
            # Use the miner_address from the block header as the miner_addr parameter
            self.blockchain.add_block(block, block.header.miner_address)
        elif len(self.blockchain.blocks) == 0 and block.header.index == 0:
            # Genesis block
            self.blockchain.blocks.append(block)
        else:
            # Simple append if add_block doesn't exist
            self.blockchain.blocks.append(block)
        
        # Build and store Bloom filter
        bloom = self.build_bloom_filter(block)
        self.block_blooms[block.header.index] = bloom
    
    def might_contain_tx(self, block_index: int, tx_id: str) -> bool:
        """
        Check if a block might contain a transaction using Bloom filter.
        
        Args:
            block_index (int): Index of the block to check.
            tx_id (str): Transaction ID to check for.
            
        Returns:
            bool: True if the transaction might be in the block, False if definitely not.
            
        Note:
            This will not raise an exception if the block doesn't exist, as it's meant
            to be a fast check. For error handling on non-existent blocks, use get_block_by_index.
        """
        # Check if we have a Bloom filter for this block
        if block_index not in self.block_blooms:
            # If the block exists in the blockchain but we don't have a Bloom filter,
            # create one now
            block = self.blockchain.get_block_by_index(block_index)
            if block:
                self.block_blooms[block_index] = self.build_bloom_filter(block)
            else:
                # If the block doesn't exist in the blockchain, don't throw an exception
                # just return False as this is a quick check method
                return False
        
        # Check if the transaction might be in the block using the Bloom filter
        return self.block_blooms[block_index].might_contain(tx_id.encode('utf-8'))
    
    def get_merkle_proof(self, block_index: int, tx_id: str) -> Optional[List[Tuple[str, str]]]:
        """
        Get a Merkle proof for a transaction in a specific block.
        
        Args:
            block_index (int): Index of the block containing the transaction.
            tx_id (str): ID of the transaction to get proof for.
            
        Returns:
            Optional[List[Tuple[str, str]]]: Merkle proof as list of (side, sibling_hash) tuples,
                                           or None if the block or transaction doesn't exist.
        """
        # Get the block at the given index
        block = self.blockchain.get_block_by_index(block_index)
        if block is None:
            return None
        
        # Generate and return the Merkle proof for the transaction
        proof = merkle_proof(block.txs, tx_id)
        
        # If proof is empty, the transaction is not in the block
        if not proof:
            return None
            
        return proof
