"""
Light wallet implementation.
"""

from typing import Optional, List, Tuple
from ..crypto.merkle import verify_proof

class LightWallet:
    """
    Represents a lightweight wallet that doesn't store the full blockchain.
    
    Attributes:
        address (str): Wallet address.
        public_key (str): Public key.
        private_key (str): Private key (should be encrypted in production).
        balance (float): Current balance.
        transactions (list): List of wallet transactions.
        full_node: Reference to a FullNode instance this wallet is connected to.
    """
    
    def __init__(self, full_node=None):
        """
        Initialize a new light wallet.
        
        Args:
            full_node (FullNode, optional): Full node to connect to.
        """
        self.address = None
        self.public_key = None
        self.private_key = None
        self.balance = 0.0
        self.transactions = []
        self.full_node = full_node
    
    def generate_keys(self):
        """Generate a new key pair and address."""
        # TODO: Implement key generation
        pass
    
    def get_balance(self):
        """
        Get the current balance from the connected node.
        
        Returns:
            float: Current balance.
        """
        # TODO: Implement balance query from connected node
        return self.balance
    
    def create_transaction(self, recipient, amount, fee=None):
        """
        Create a new transaction.
        
        Args:
            recipient (str): Recipient's address.
            amount (float): Amount to send.
            fee (float, optional): Transaction fee.
            
        Returns:
            Transaction: The created transaction.
        """
        # TODO: Implement transaction creation
        pass
    
    def check_tx_in_block(self, block_index: int, tx_id: str) -> bool:
        """
        Check if a transaction is in a specific block using a two-step verification:
        1. Check Bloom filter (cheap, may have false positives)
        2. If Bloom filter says "maybe", verify with Merkle proof (expensive but accurate)
        
        Args:
            block_index (int): Index of the block to check.
            tx_id (str): ID of the transaction to check for.
            
        Returns:
            bool: True if the transaction is in the block, False otherwise.
            
        Raises:
            ValueError: If the wallet is not connected to a full node.
            Exception: If the specified block doesn't exist.
        """
        if not self.full_node:
            raise ValueError("Light wallet not connected to a full node")
        
        # First explicitly check if block exists to properly raise an exception
        # for non-existent blocks
        block = self.full_node.blockchain.get_block_by_index(block_index)
        if block is None:
            raise Exception(f"Block with index {block_index} does not exist")
        
        # Step 1: Check Bloom filter (this won't raise exceptions for non-existent blocks)
        if not self.full_node.might_contain_tx(block_index, tx_id):
            # Bloom filters guarantee no false negatives, so if it says "no", it's definitely not there
            return False
        
        # Step 2: Bloom filter said "maybe", so get Merkle proof for verification
        proof = self.full_node.get_merkle_proof(block_index, tx_id)
        
        if proof is None:
            # No proof means the transaction is not in the block (Bloom filter had a false positive)
            return False
        
        # Verify the Merkle proof
        return verify_proof(block.header.merkle_root, tx_id, proof)
