"""
Light wallet implementation.
"""

from typing import Optional, List, Tuple
from ..crypto.merkle import verify_proof
from ..crypto import keys
from ..core.tx import Tx
from ..core.fees import suggest_tip, BASE_FEE
from ..crypto import segwit

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
        """Generate a new ECDSA key pair and derive the wallet address."""
        priv, pub = keys.generate_key_pair()
        self.private_key = priv
        self.public_key = keys.serialize_public_key(pub)
        self.address = keys.get_address_from_pubkey(pub)
        return self.address
    
    def get_balance(self):
        """
        Get the current balance from the connected node.
        
        Returns:
            float: Current balance.
        """
        if not self.full_node:
            return self.balance
        # Query authoritative balance from connected full node blockchain
        self.balance = self.full_node.blockchain.get_balance(self.address) if self.address else 0
        return self.balance
    
    def create_transaction(self, recipient: str, amount: int, tip: Optional[int] = None, base_fee: int = BASE_FEE) -> Tx:
        """Create, sign (detached), and return a transaction ready for broadcast.

        Nonce heuristic: count prior sent transactions by this wallet in chain + mempool size.
        (Simplified; a production system would track per-sender nonce precisely.)
        """
        if not self.private_key or not self.address:
            raise ValueError("Wallet keys not generated")
        if not self.full_node:
            raise ValueError("Light wallet not connected to a full node")

        # Determine nonce: naive scan of blockchain for sender transactions
        nonce = 0
        for blk in self.full_node.blockchain.blocks:
            for tx in blk.txs:
                if tx.sender == self.address:
                    nonce = max(nonce, tx.nonce + 1)

        # Dynamic tip suggestion if not provided
        if tip is None:
            tip = suggest_tip(self.full_node.mempool.size())

        tx = Tx(
            sender=self.address,
            recipient=recipient,
            amount=amount,
            nonce=nonce,
            base_fee=base_fee,
            tip=tip
        )
        # Sign with detachment
        tx.sign(self.private_key, detach=True)
        # Ensure signature detached (Tx.sign stores in segwit store)
        # For belt and suspenders, fetch and confirm presence
        if not segwit.get_signature(tx.tx_id):
            raise RuntimeError("Detached signature missing after signing")
        # Local optimistic balance update (not authoritative)
        self.balance -= (amount + base_fee + tip)
        self.transactions.append(tx.tx_id)
        return tx
    
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
        
        # Step 1: Check Bloom filter
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
