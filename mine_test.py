#!/usr/bin/env python3
"""
Simple CLI script to test mining functionality.
"""

import sys
import os
import time
import hashlib
import json

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class BlockHeader:
    def __init__(self, index, prev_hash, merkle_root, timestamp, nonce, miner_address):
        self.index = index
        self.prev_hash = prev_hash
        self.merkle_root = merkle_root
        self.timestamp = timestamp
        self.nonce = nonce
        self.miner_address = miner_address
    
    def to_dict(self):
        return {
            "index": self.index,
            "prev_hash": self.prev_hash,
            "merkle_root": self.merkle_root,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "miner_address": self.miner_address
        }

class Block:
    def __init__(self, header, txs=None):
        self.header = header
        self.txs = txs or []
    
    @property
    def block_hash(self):
        header_dict = self.header.to_dict()
        canonical_json = json.dumps(header_dict, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

def mine_test_block(miner_address, difficulty=2):
    """Mine a test block to demonstrate the mining functionality."""
    print(f"Mining a block for miner: {miner_address} with difficulty {difficulty}")
    
    # Create a genesis block header
    genesis_header = BlockHeader(
        index=0,
        prev_hash="0" * 64,
        merkle_root=hashlib.sha256("genesis".encode('utf-8')).hexdigest(),
        timestamp=int(time.time()),
        nonce=0,
        miner_address="genesis"
    )
    
    # Create the genesis block
    genesis_block = Block(header=genesis_header)
    print(f"Created genesis block with hash: {genesis_block.block_hash}")
    
    # Create a candidate block header for mining
    candidate_header = BlockHeader(
        index=1,
        prev_hash=genesis_block.block_hash,
        merkle_root=hashlib.sha256("transactions".encode('utf-8')).hexdigest(),
        timestamp=int(time.time()),
        nonce=0,
        miner_address=miner_address
    )
    
    # Create the candidate block
    candidate_block = Block(header=candidate_header)
    
    # Mine the block
    print("Mining block...")
    target = "0" * difficulty
    start_time = time.time()
    
    for nonce in range(1000000):
        candidate_block.header.nonce = nonce
        block_hash = candidate_block.block_hash
        
        if block_hash.startswith(target):
            end_time = time.time()
            print(f"Found valid hash after {nonce} attempts!")
            print(f"Block hash: {block_hash}")
            print(f"Mining time: {end_time - start_time:.2f} seconds")
            print(f"Mining reward: 50 coins")
            print(f"Miner address: {miner_address}")
            return True
    
    print("Failed to find a valid hash within the nonce range")
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mine_test.py <miner_address> [difficulty]")
        sys.exit(1)
        
    miner_address = sys.argv[1]
    difficulty = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    
    mine_test_block(miner_address, difficulty)
