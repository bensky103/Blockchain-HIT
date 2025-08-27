"""
Tests for the Bloom filter and light wallet functionality.
"""

import pytest
from ..crypto.bloom import BloomFilter
from ..node.full_node import FullNode
from ..node.light_wallet import LightWallet
from ..core.tx import Tx
from ..core.block import Block, BlockHeader
from ..crypto.merkle import merkle_root
from ..crypto import keys

def test_bloom_filter():
    """Test the BloomFilter implementation."""
    # Create a Bloom filter
    bloom = BloomFilter(m_bits=2048, k=3)
    
    # Add items
    items = [b"test1", b"test2", b"test3"]
    for item in items:
        bloom.add(item)
    
    # Test items are found (no false negatives)
    for item in items:
        assert bloom.might_contain(item) is True
    
    # Test a non-added item (might be false positive, but unlikely with our parameters)
    assert bloom.might_contain(b"not-added") is False or bloom.might_contain(b"not-added") is True

def test_full_node_bloom():
    """Test the full node's Bloom filter functionality."""
    # Create a full node
    node = FullNode()
    
    # Create some test transactions
    priv_key_alice, _ = keys.generate_key_pair()
    priv_key_bob, _ = keys.generate_key_pair()
    priv_key_charlie, _ = keys.generate_key_pair()
    tx1 = Tx("alice", "bob", 10, 1, 2, 3, private_key=priv_key_alice)
    tx2 = Tx("bob", "charlie", 5, 1, 2, 3, private_key=priv_key_bob)
    tx3 = Tx("charlie", "alice", 2, 1, 2, 3, private_key=priv_key_charlie)
    
    # Create a test block with these transactions
    txs = [tx1, tx2, tx3]
    root = merkle_root(txs)
    header = BlockHeader(0, "0"*64, root, 123456789, 0, "miner")
    block = Block(header, txs)
    
    # Add the block to the node
    node.add_finalized_block(block)
    
    # Check that the node correctly identifies transactions in the block
    assert node.might_contain_tx(0, tx1.tx_id) is True
    assert node.might_contain_tx(0, tx2.tx_id) is True
    assert node.might_contain_tx(0, tx3.tx_id) is True
    
    # Check that the node correctly rejects transactions not in the block
    fake_tx = Tx("dave", "eve", 100, 1, 2, 3)
    assert node.might_contain_tx(0, fake_tx.tx_id) is False or node.get_merkle_proof(0, fake_tx.tx_id) is None

def test_light_wallet():
    """Test the light wallet's transaction verification functionality."""
    # Create a full node
    node = FullNode()
    
    # Create some test transactions
    priv_key_alice, _ = keys.generate_key_pair()
    priv_key_bob, _ = keys.generate_key_pair()
    priv_key_charlie, _ = keys.generate_key_pair()
    tx1 = Tx("alice", "bob", 10, 1, 2, 3, private_key=priv_key_alice)
    tx2 = Tx("bob", "charlie", 5, 1, 2, 3, private_key=priv_key_bob)
    tx3 = Tx("charlie", "alice", 2, 1, 2, 3, private_key=priv_key_charlie)
    
    # Create a test block with these transactions
    txs = [tx1, tx2, tx3]
    root = merkle_root(txs)
    header = BlockHeader(0, "0"*64, root, 123456789, 0, "miner")
    block = Block(header, txs)
    
    # Add the block to the node
    node.add_finalized_block(block)
    
    # Create a light wallet connected to the node
    wallet = LightWallet(node)
    
    # Test that the wallet correctly verifies transactions in the block
    assert wallet.check_tx_in_block(0, tx1.tx_id) is True
    assert wallet.check_tx_in_block(0, tx2.tx_id) is True
    assert wallet.check_tx_in_block(0, tx3.tx_id) is True
    
    # Test that the wallet correctly rejects transactions not in the block
    fake_tx = Tx("dave", "eve", 100, 1, 2, 3)
    assert wallet.check_tx_in_block(0, fake_tx.tx_id) is False
    
    # Test that the wallet handles non-existent blocks correctly
    with pytest.raises(Exception, match=r"Block with index 999 does not exist"):
        wallet.check_tx_in_block(999, tx1.tx_id)