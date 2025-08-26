"""
Tests for Merkle tree functionality.
"""

import unittest
from ..core.tx import Tx
from ..crypto.merkle import merkle_root, merkle_proof, verify_proof

class TestMerkle(unittest.TestCase):
    """Tests for Merkle tree functionality."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create some transactions for testing
        self.txs = [
            Tx(sender="alice", recipient="bob", amount=10, nonce=1),
            Tx(sender="bob", recipient="charlie", amount=20, nonce=1),
            Tx(sender="charlie", recipient="alice", amount=30, nonce=1),
            Tx(sender="dave", recipient="alice", amount=40, nonce=1)
        ]
        
    def test_merkle_root(self):
        """Test merkle root calculation."""
        # Calculate root for 4 transactions
        root = merkle_root(self.txs)
        
        # Root should be a hex string of length 64 (SHA-256)
        self.assertEqual(len(root), 64)
        
        # Root should be deterministic
        root2 = merkle_root(self.txs)
        self.assertEqual(root, root2)
        
        # Test with empty list
        empty_root = merkle_root([])
        self.assertEqual(len(empty_root), 64)
        
        # Test with single transaction
        single_root = merkle_root([self.txs[0]])
        self.assertEqual(len(single_root), 64)
        
        # Test with odd number of transactions
        odd_root = merkle_root(self.txs[0:3])  # First 3 transactions
        self.assertEqual(len(odd_root), 64)
    
    def test_merkle_proof(self):
        """Test merkle proof generation."""
        # Generate proof for a transaction in the list
        tx_id = self.txs[1].tx_id
        proof = merkle_proof(self.txs, tx_id)
        
        # Proof should have log2(n) steps
        self.assertEqual(len(proof), 2)  # For 4 transactions, we need 2 steps
        
        # Each step should have a side ('left' or 'right') and a hash (64 chars)
        for step in proof:
            self.assertIn(step[0], ['left', 'right'])
            self.assertEqual(len(step[1]), 64)
        
        # Test with transaction not in the list
        non_existent_tx = Tx(sender="eve", recipient="mallory", amount=100, nonce=1)
        empty_proof = merkle_proof(self.txs, non_existent_tx.tx_id)
        self.assertEqual(empty_proof, [])
    
    def test_verify_proof(self):
        """Test merkle proof verification."""
        # Get the root for all transactions
        root = merkle_root(self.txs)
        
        # Generate proof for a transaction
        tx_id = self.txs[2].tx_id
        proof = merkle_proof(self.txs, tx_id)
        
        # Verification should succeed for valid proof
        self.assertTrue(verify_proof(root, tx_id, proof))
        
        # Verification should fail for different transaction
        other_tx_id = self.txs[0].tx_id
        self.assertFalse(verify_proof(root, other_tx_id, proof))
        
        # Verification should fail for tampered root
        tampered_root = '0' * 64
        self.assertFalse(verify_proof(tampered_root, tx_id, proof))
        
        # Verification should fail for tampered proof
        if proof:
            tampered_proof = proof.copy()
            # Change the first step's side
            side, hash_val = tampered_proof[0]
            new_side = 'right' if side == 'left' else 'left'
            tampered_proof[0] = (new_side, hash_val)
            self.assertFalse(verify_proof(root, tx_id, tampered_proof))

if __name__ == '__main__':
    unittest.main()
