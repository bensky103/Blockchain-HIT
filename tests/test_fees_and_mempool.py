"""
Tests for fee policies and mempool functionality.
"""

import unittest
from ..core.tx import Tx
from ..core.block import Block
from ..core.chain import Blockchain
from ..core.fees import BLOCK_REWARD, BASE_FEE, TIP
from ..node.mempool import Mempool
from ..crypto import keys

class TestFeesAndMempool(unittest.TestCase):
    """Tests for fee policies and mempool functionality."""
    
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
        
    def test_mempool_accept_valid_tx(self):
        """Test that valid transactions are accepted in mempool."""
        # Create a valid transaction
        tx = Tx(
            sender="alice",
            recipient="bob",
            amount=50,
            nonce=1,
            base_fee=BASE_FEE,
            tip=TIP
        )
        
        # Transaction should be accepted (alice has enough funds)
        self.assertTrue(self.mempool.accept(tx))
        self.assertEqual(self.mempool.size(), 1)
        
    def test_mempool_reject_insufficient_funds(self):
        """Test that transactions with insufficient funds are rejected."""
        # Create a transaction with amount exceeding balance
        tx = Tx(
            sender="charlie",
            recipient="bob",
            amount=200,  # charlie only has 200, can't afford fees
            nonce=1,
            base_fee=BASE_FEE,
            tip=TIP
        )
        
        # Transaction should be rejected (insufficient funds)
        self.assertFalse(self.mempool.accept(tx))
        self.assertEqual(self.mempool.size(), 0)
        
    def test_mempool_reject_duplicate(self):
        """Test that duplicate transactions are rejected."""
        # Create a transaction
        tx = Tx(
            sender="alice",
            recipient="bob",
            amount=50,
            nonce=1,
            base_fee=BASE_FEE,
            tip=TIP
        )
        
        # First submission should be accepted
        self.assertTrue(self.mempool.accept(tx))
        
        # Duplicate submission (same tx_id) should be rejected
        self.assertFalse(self.mempool.accept(tx))
        self.assertEqual(self.mempool.size(), 1)
        
    def test_mempool_get_batch(self):
        """Test retrieving transactions in FIFO order."""
        # Create transactions
        tx1 = Tx(sender="alice", recipient="bob", amount=10, nonce=1)
        tx2 = Tx(sender="alice", recipient="bob", amount=20, nonce=2)
        tx3 = Tx(sender="alice", recipient="bob", amount=30, nonce=3)
        tx4 = Tx(sender="bob", recipient="charlie", amount=5, nonce=1)
        tx5 = Tx(sender="bob", recipient="charlie", amount=10, nonce=2)
        
        # Add transactions to mempool
        self.mempool.accept(tx1)
        self.mempool.accept(tx2)
        self.mempool.accept(tx3)
        self.mempool.accept(tx4)
        self.mempool.accept(tx5)
        
        # Get a batch with limit=3
        batch = self.mempool.get_batch(max_txs=3)
        
        # Should return first 3 transactions in FIFO order
        self.assertEqual(len(batch), 3)
        self.assertEqual(batch[0].tx_id, tx1.tx_id)
        self.assertEqual(batch[1].tx_id, tx2.tx_id)
        self.assertEqual(batch[2].tx_id, tx3.tx_id)
        
        # Mempool should have 2 transactions left
        self.assertEqual(self.mempool.size(), 2)
        
    def test_apply_block_with_fees(self):
        """Test applying a block with transaction fees."""
        # Create transactions
        priv_key_alice, _ = keys.generate_key_pair()
        priv_key_bob, _ = keys.generate_key_pair()

        tx1 = Tx(sender="alice", recipient="bob", amount=50, nonce=1)
        tx1.sign(priv_key_alice)
        tx2 = Tx(sender="bob", recipient="charlie", amount=25, nonce=1)
        tx2.sign(priv_key_bob)
        
        # Create a block with these transactions
        latest_block = self.blockchain.get_latest_block()
        block = Block(
            header=Block.create_header(
                index=latest_block.header.index + 1,
                prev_hash=latest_block.block_hash,
                miner_address="miner"
            ),
            txs=[tx1, tx2]
        )
        
        # Apply the block
        self.blockchain.apply_block(block, "miner")
        
        # Check balances after applying block
        # Alice: 1000 - (50 + BASE_FEE + TIP) = 1000 - 55 = 945
        self.assertEqual(self.blockchain.balances["alice"], 945)
        
        # Bob: 500 + 50 (from alice) - (25 + BASE_FEE + TIP) = 500 + 50 - 30 = 520
        self.assertEqual(self.blockchain.balances["bob"], 520)
        
        # Charlie: 200 + 25 (from bob) = 225
        self.assertEqual(self.blockchain.balances["charlie"], 225)
        
        # Miner: 0 + TIP*2 (from 2 txs) + BLOCK_REWARD = 0 + 6 + 50 = 56
        self.assertEqual(self.blockchain.balances["miner"], 56)
        
        # Check burned fees and mined coins
        self.assertEqual(self.blockchain.total_burned, BASE_FEE * 2)  # 2 transactions
        self.assertEqual(self.blockchain.total_mined, BLOCK_REWARD)  # 1 block
        
    def test_blockchain_invariants(self):
        """Test blockchain invariants after multiple blocks."""
        # Create and apply several blocks
        miner_addr = "miner"
        
        # Add transactions to mempool
        priv_key_alice, _ = keys.generate_key_pair()
        priv_key_bob, _ = keys.generate_key_pair()
        txs = [
            Tx(sender="alice", recipient="bob", amount=10, nonce=1, private_key=priv_key_alice),
            Tx(sender="alice", recipient="bob", amount=20, nonce=2, private_key=priv_key_alice),
            Tx(sender="alice", recipient="charlie", amount=30, nonce=3, private_key=priv_key_alice),
            Tx(sender="bob", recipient="charlie", amount=15, nonce=1, private_key=priv_key_bob),
        ]
        
        for tx in txs:
            self.mempool.accept(tx)
            
        # Create blocks with transactions from mempool
        for i in range(2):  # Create 2 blocks
            latest_block = self.blockchain.get_latest_block()
            batch = self.mempool.get_batch(max_txs=2)  # 2 txs per block
            
            block = Block(
                header=Block.create_header(
                    index=latest_block.header.index + 1,
                    prev_hash=latest_block.block_hash,
                    miner_address=miner_addr
                ),
                txs=batch
            )
            
            self.blockchain.add_block(block, miner_addr)
        
        # Calculate expected results
        expected_burn = BASE_FEE * 4  # 4 transactions
        expected_mined = BLOCK_REWARD * 2  # 2 blocks
        
        # Verify invariants
        self.assertEqual(self.blockchain.total_burned, expected_burn)
        self.assertEqual(self.blockchain.total_mined, expected_mined)
        
        # Sum of all balances should equal initial sum plus mined coins minus burned
        initial_sum = sum(self.initial_balances.values())
        current_sum = sum(self.blockchain.balances.values())
        
        self.assertEqual(current_sum, initial_sum + expected_mined - expected_burn)

if __name__ == '__main__':
    unittest.main()
