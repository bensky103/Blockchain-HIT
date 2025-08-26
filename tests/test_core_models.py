"""
Tests for core blockchain models.
"""

import os
import sys
import json
import hashlib
import pytest

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.tx import Tx
from core.block import Block, BlockHeader
from core.chain import Blockchain


class TestTransaction:
    """Tests for the Tx class."""
    
    def test_tx_serialization(self):
        """Test deterministic transaction serialization."""
        # Create a transaction
        tx = Tx(
            sender="alice",
            recipient="bob",
            amount=100,
            nonce=1,
            base_fee=2,
            tip=3
        )
        
        # Convert to dict and back
        tx_dict = tx.to_dict()
        tx2 = Tx.from_dict(tx_dict)
        
        # Verify equality
        assert tx.sender == tx2.sender
        assert tx.recipient == tx2.recipient
        assert tx.amount == tx2.amount
        assert tx.nonce == tx2.nonce
        assert tx.base_fee == tx2.base_fee
        assert tx.tip == tx2.tip
        assert tx.tx_id == tx2.tx_id
    
    def test_tx_id_deterministic(self):
        """Test that tx_id is deterministic and doesn't include signature."""
        # Create transactions with same data but different signatures
        tx1 = Tx(
            sender="alice",
            recipient="bob",
            amount=100,
            nonce=1,
            base_fee=2,
            tip=3,
            signature=None
        )
        
        tx2 = Tx(
            sender="alice",
            recipient="bob",
            amount=100,
            nonce=1,
            base_fee=2,
            tip=3,
            signature="some_signature"
        )
        
        # tx_id should be the same (signature not included)
        assert tx1.tx_id == tx2.tx_id
        
        # Manual calculation of tx_id
        tx_dict = {
            "sender": "alice",
            "recipient": "bob",
            "amount": 100,
            "nonce": 1,
            "base_fee": 2,
            "tip": 3
        }
        canonical_json = json.dumps(tx_dict, sort_keys=True, separators=(',', ':'))
        manual_tx_id = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
        
        assert tx1.tx_id == manual_tx_id


class TestBlock:
    """Tests for the Block and BlockHeader classes."""
    
    def test_block_header_serialization(self):
        """Test block header serialization."""
        # Create a block header
        header = BlockHeader(
            index=1,
            prev_hash="previous_hash",
            merkle_root="merkle_root",
            timestamp=1630000000,
            nonce=12345,
            miner_address="miner1"
        )
        
        # Convert to dict and back
        header_dict = header.to_dict()
        header2 = BlockHeader.from_dict(header_dict)
        
        # Verify equality
        assert header.index == header2.index
        assert header.prev_hash == header2.prev_hash
        assert header.merkle_root == header2.merkle_root
        assert header.timestamp == header2.timestamp
        assert header.nonce == header2.nonce
        assert header.miner_address == header2.miner_address
    
    def test_block_hash_deterministic(self):
        """Test deterministic block hash calculation."""
        # Create a block header
        header = BlockHeader(
            index=1,
            prev_hash="previous_hash",
            merkle_root="merkle_root",
            timestamp=1630000000,
            nonce=12345,
            miner_address="miner1"
        )
        
        # Calculate hash
        block_hash = header.calculate_hash()
        
        # Calculate hash manually
        header_dict = header.to_dict()
        canonical_json = json.dumps(header_dict, sort_keys=True, separators=(',', ':'))
        manual_hash = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
        
        assert block_hash == manual_hash
    
    def test_block_serialization(self):
        """Test block serialization."""
        # Create transactions
        tx1 = Tx("alice", "bob", 100, 1)
        tx2 = Tx("bob", "charlie", 50, 2)
        
        # Create block header
        header = BlockHeader(
            index=1,
            prev_hash="previous_hash",
            merkle_root="merkle_root",
            timestamp=1630000000,
            nonce=12345,
            miner_address="miner1"
        )
        
        # Create block
        block = Block(header=header, txs=[tx1, tx2])
        
        # Convert to dict and back
        block_dict = block.to_dict()
        block2 = Block.from_dict(block_dict)
        
        # Verify header equality
        assert block.header.index == block2.header.index
        assert block.header.prev_hash == block2.header.prev_hash
        assert block.header.merkle_root == block2.header.merkle_root
        
        # Verify transactions equality
        assert len(block.txs) == len(block2.txs)
        assert block.txs[0].tx_id == block2.txs[0].tx_id
        assert block.txs[1].tx_id == block2.txs[1].tx_id


class TestBlockchain:
    """Tests for the Blockchain class."""
    
    def test_genesis_block_creation(self):
        """Test genesis block creation."""
        # Create blockchain and add genesis block
        blockchain = Blockchain()
        initial_balances = {
            "alice": 100,
            "bob": 50,
            "charlie": 75
        }
        
        genesis_block = blockchain.add_genesis(initial_balances)
        
        # Verify genesis block
        assert len(blockchain.blocks) == 1
        assert blockchain.blocks[0].header.index == 0
        assert blockchain.blocks[0].header.prev_hash == "0" * 64
        
        # Verify balances
        assert blockchain.balances == initial_balances
    
    def test_validate_block_structure(self):
        """Test block structure validation."""
        # Create blockchain and add genesis block
        blockchain = Blockchain()
        blockchain.add_genesis({"alice": 100})
        
        # Create valid next block
        valid_header = BlockHeader(
            index=1,
            prev_hash=blockchain.blocks[0].block_hash,
            merkle_root="merkle_root",
            timestamp=1630000000,
            nonce=12345,
            miner_address="miner1"
        )
        valid_block = Block(header=valid_header, txs=[])
        
        # Create invalid block (wrong index)
        invalid_header1 = BlockHeader(
            index=2,  # Should be 1
            prev_hash=blockchain.blocks[0].block_hash,
            merkle_root="merkle_root",
            timestamp=1630000000,
            nonce=12345,
            miner_address="miner1"
        )
        invalid_block1 = Block(header=invalid_header1, txs=[])
        
        # Create invalid block (wrong prev_hash)
        invalid_header2 = BlockHeader(
            index=1,
            prev_hash="wrong_hash",
            merkle_root="merkle_root",
            timestamp=1630000000,
            nonce=12345,
            miner_address="miner1"
        )
        invalid_block2 = Block(header=invalid_header2, txs=[])
        
        # Verify validation
        assert blockchain.validate_block_structure(valid_block) is True
        assert blockchain.validate_block_structure(invalid_block1) is False
        assert blockchain.validate_block_structure(invalid_block2) is False
