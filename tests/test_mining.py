"""
Tests for mining functionality.
"""

import unittest
from ..core.tx import Tx
from ..core.block import Block
from ..core.chain import Blockchain
from ..core.fees import BLOCK_REWARD, BASE_FEE, TIP
from ..node.mempool import Mempool
from ..node.mining import build_candidate_block, mine_block
from ..crypto import keys

class TestMining(unittest.TestCase):
    """Tests for mining functionality."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create a blockchain with initial balances
        self.blockchain = Blockchain()
        self.initial_balances = {
            "alice": 1000,
            "bob": 500,
            "charlie": 200,
            "miner": 0
        }
        self.blockchain.add_genesis(self.initial_balances)
        
        # Create a mempool linked to blockchain balances
        self.mempool = Mempool(self.blockchain.balances)
        
        # Add some transactions to the mempool
        priv_key_alice, _ = keys.generate_key_pair()
        priv_key_bob, _ = keys.generate_key_pair()
        priv_key_charlie, _ = keys.generate_key_pair()
        txs = [
            Tx(sender="alice", recipient="bob", amount=10, nonce=1, private_key=priv_key_alice),
            Tx(sender="alice", recipient="bob", amount=20, nonce=2, private_key=priv_key_alice),
            Tx(sender="bob", recipient="charlie", amount=5, nonce=1, private_key=priv_key_bob),
            Tx(sender="bob", recipient="alice", amount=15, nonce=2, private_key=priv_key_bob),
            Tx(sender="charlie", recipient="alice", amount=10, nonce=1, private_key=priv_key_charlie),
        ]
        
        for tx in txs:
            self.mempool.accept(tx)
    
    def test_mine_once(self):
        """Test mining a single block."""
        # Get the initial chain length
        initial_length = len(self.blockchain.blocks)
        
        # Get the previous block
        prev_block = self.blockchain.get_latest_block()
        
        # Get transaction batch from mempool (up to 4)
        tx_batch = self.mempool.get_batch(max_txs=4)
        self.assertTrue(len(tx_batch) > 0, "Should have transactions in batch")
        self.assertLessEqual(len(tx_batch), 4, "Should have at most 4 transactions")
        
        # Build candidate block
        candidate_block = build_candidate_block(
            prev_block=prev_block,
            miner_address="miner",
            mempool_batch=tx_batch
        )
        
        # Mine the block with low difficulty for testing
        success = mine_block(candidate_block, difficulty=2)
        self.assertTrue(success, "Mining should succeed")
        
        # Add the block to the chain
        self.assertTrue(
            self.blockchain.add_block(candidate_block, "miner"),
            "Block should be added successfully"
        )
        
        # Verify chain grew by 1
        self.assertEqual(len(self.blockchain.blocks), initial_length + 1, 
                         "Chain should grow by 1 block")
    
    def test_reject_oversized_block(self):
        """Test that blocks with more than 4 transactions are rejected."""
        # Get the previous block
        prev_block = self.blockchain.get_latest_block()
        
        # Create more than 4 transactions
        oversized_batch = [
            Tx(sender="alice", recipient="bob", amount=1, nonce=10),
            Tx(sender="alice", recipient="bob", amount=2, nonce=11),
            Tx(sender="alice", recipient="bob", amount=3, nonce=12),
            Tx(sender="alice", recipient="bob", amount=4, nonce=13),
            Tx(sender="alice", recipient="bob", amount=5, nonce=14),  # 5th tx makes it too big
        ]
        
        # Build candidate block with too many transactions
        candidate_block = build_candidate_block(
            prev_block=prev_block,
            miner_address="miner",
            mempool_batch=oversized_batch
        )
        
        # Try to add the block (should fail validation)
        self.assertFalse(
            self.blockchain.add_block(candidate_block, "miner"),
            "Block with > 4 transactions should be rejected"
        )

if __name__ == '__main__':
    unittest.main()
