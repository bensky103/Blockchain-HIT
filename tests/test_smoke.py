"""
Smoke test to verify that the environment is set up correctly.
"""

import os
import sys
import pytest

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import basic modules to ensure they're working
from blockchain_lab.core.block import Block
from blockchain_lab.core.chain import Blockchain

def test_project_structure():
    """Verify that the project structure is set up correctly."""
    # Get the parent directory (project root)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Check that the core directory exists
    assert os.path.isdir(os.path.join(project_root, 'core')), "Core directory not found"
    
    # Check that the node directory exists
    assert os.path.isdir(os.path.join(project_root, 'node')), "Node directory not found"
    
    # Check that the crypto directory exists
    assert os.path.isdir(os.path.join(project_root, 'crypto')), "Crypto directory not found"
    
    # Check that the sim directory exists
    assert os.path.isdir(os.path.join(project_root, 'sim')), "Sim directory not found"
    
    # Check that the cli directory exists
    assert os.path.isdir(os.path.join(project_root, 'cli')), "CLI directory not found"

def test_core_imports():
    """Verify that core modules can be imported."""
    # Test importing a module and creating a class instance
    from blockchain_lab.core.block import Block, BlockHeader
    
    # Create a block header first
    header = BlockHeader(
        index=1, 
        prev_hash="test", 
        merkle_root="test_merkle_root", 
        timestamp=123456, 
        nonce=0, 
        miner_address="test_miner"
    )
    
    # Then create a block using the header
    block = Block(header=header, txs=[])
    assert block.header.prev_hash == "test", "Block creation failed"
    
    # Test blockchain creation
    blockchain = Blockchain()
    assert len(blockchain.blocks) == 0, "Blockchain should be initialized with empty blocks list"

def test_environment():
    """Verify that the test environment is working."""
    assert True, "Test environment is working"
