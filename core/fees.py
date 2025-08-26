"""
Fee policy and calculation helpers for the blockchain.
"""

from typing import Tuple, Dict
from .tx import Tx

# Constants
BLOCK_REWARD = 50  # Reward for mining a block
BASE_FEE = 2       # Base fee that gets burned (EIP-1559 style)
TIP = 3            # Default tip/priority fee for miners

def calculate_transaction_fees(tx: Tx) -> Tuple[int, int]:
    """
    Calculate the base fee (burned) and tip (to miner) for a transaction.
    
    Args:
        tx (Tx): The transaction to calculate fees for.
        
    Returns:
        Tuple[int, int]: (base_fee, tip) to be deducted from sender
    """
    return tx.base_fee, tx.tip

def calculate_transaction_cost(tx: Tx) -> int:
    """
    Calculate the total cost of a transaction (amount + fees).
    
    Args:
        tx (Tx): The transaction to calculate cost for.
        
    Returns:
        int: Total cost to the sender (amount + base_fee + tip)
    """
    return tx.amount + tx.base_fee + tx.tip

def apply_transaction_fees(
    balances: Dict[str, int], 
    tx: Tx,
    miner_address: str
) -> Dict[str, int]:
    """
    Apply the transaction fees to the balances.
    
    Args:
        balances (Dict[str, int]): Current account balances.
        tx (Tx): The transaction being processed.
        miner_address (str): Address of the miner to credit the tip.
        
    Returns:
        Dict[str, int]: Updated balances after applying fees.
    """
    # Make a copy to avoid modifying the original
    updated_balances = balances.copy()
    
    # Deduct amount and fees from sender
    sender_balance = updated_balances.get(tx.sender, 0)
    updated_balances[tx.sender] = sender_balance - calculate_transaction_cost(tx)
    
    # Credit amount to recipient
    recipient_balance = updated_balances.get(tx.recipient, 0)
    updated_balances[tx.recipient] = recipient_balance + tx.amount
    
    # Credit tip to miner
    miner_balance = updated_balances.get(miner_address, 0)
    updated_balances[miner_address] = miner_balance + tx.tip
    
    # Note: The base_fee is implicitly burned by not being credited to anyone
    
    return updated_balances

def apply_block_reward(balances: Dict[str, int], miner_address: str) -> Dict[str, int]:
    """
    Apply the block reward to the miner.
    
    Args:
        balances (Dict[str, int]): Current account balances.
        miner_address (str): Address of the miner to credit the reward.
        
    Returns:
        Dict[str, int]: Updated balances after applying the reward.
    """
    # Make a copy to avoid modifying the original
    updated_balances = balances.copy()
    
    # Credit the block reward to the miner
    miner_balance = updated_balances.get(miner_address, 0)
    updated_balances[miner_address] = miner_balance + BLOCK_REWARD
    
    return updated_balances
