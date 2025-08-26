"""
Mining functionality for blockchain.
"""

import time
import hashlib
from typing import List
from ..core.block import Block, BlockHeader
from ..core.tx import Tx
from ..core.fees import BLOCK_REWARD, BASE_FEE, TIP
from ..node.mempool import Mempool
from ..crypto.merkle import merkle_root

def build_candidate_block(
    prev_block: Block, 
    miner_address: str,
    mempool_batch: List[Tx]
) -> Block:
    """
    Build a candidate block for mining.
    
    Args:
        prev_block (Block): The previous block in the chain.
        miner_address (str): Address to receive mining rewards.
        mempool_batch (List[Tx]): Batch of transactions from the mempool.
        
    Returns:
        Block: A candidate block ready for mining.
    """
    # Calculate the merkle root from the transactions
    real_merkle_root = merkle_root(mempool_batch)
    
    # Create block header
    header = BlockHeader(
        index=prev_block.header.index + 1,
        prev_hash=prev_block.block_hash,
        merkle_root=real_merkle_root,
        timestamp=int(time.time()),
        nonce=0,
        miner_address=miner_address
    )
    
    # Create the block with the header and transactions
    return Block(header=header, txs=mempool_batch)

def mine_block(block: Block, difficulty: int = 4) -> bool:
    """
    Mine a block by finding a valid hash with the required difficulty.
    
    Args:
        block (Block): The block to mine.
        difficulty (int, optional): Mining difficulty. Defaults to 4.
        
    Returns:
        bool: Whether mining was successful.
    """
    # Target pattern for proof-of-work (e.g., "0000" for difficulty=4)
    target = "0" * difficulty
    
    # Start with nonce = 0 and increment until a valid hash is found
    max_nonce = 10000000  # Prevent infinite loops during testing
    
    for nonce in range(max_nonce):
        # Update nonce in the block header
        block.header.nonce = nonce
        
        # Calculate block hash
        block_hash = block.block_hash
        
        # Check if hash meets difficulty target
        if block_hash.startswith(target):
            # Found a valid hash
            return True
    
    # Failed to find valid hash within max_nonce
    return False

def calculate_mining_reward(txs: List[Tx]) -> int:
    """
    Calculate the total mining reward including block reward and transaction tips.
    
    Args:
        txs (List[Tx]): Transactions included in the block.
        
    Returns:
        int: Total mining reward.
    """
    # Block reward is fixed
    total_reward = BLOCK_REWARD
    
    # Add up all tips from transactions
    for tx in txs:
        total_reward += tx.tip
    
    return total_reward

def calculate_burned_fees(txs: List[Tx]) -> int:
    """
    Calculate the total burned fees from transactions.
    
    Args:
        txs (List[Tx]): Transactions included in the block.
        
    Returns:
        int: Total burned fees.
    """
    return sum(tx.base_fee for tx in txs)
