"""
Memory pool for unconfirmed transactions.
"""

from typing import List, Dict, Set
from collections import deque
from ..core.tx import Tx
from ..core.fees import calculate_transaction_cost, BASE_FEE, TIP

class Mempool:
    """
    Represents the memory pool for unconfirmed transactions.
    
    A FIFO queue of unconfirmed transactions ready to be included in blocks.
    Transactions are validated before acceptance to ensure sender can afford them.
    
    Attributes:
        transactions (Dict[str, Tx]): Dictionary of unconfirmed transactions (tx_id -> tx).
        tx_queue (deque): Queue of transaction IDs in FIFO order.
        balances (Dict[str, int]): Reference to current blockchain balances.
    """
    
    def __init__(self, balances: Dict[str, int] = None):
        """
        Initialize a new memory pool.
        
        Args:
            balances (Dict[str, int], optional): Reference to blockchain balances for validation.
        """
        self.transactions: Dict[str, Tx] = {}  # tx_id -> tx
        self.tx_queue = deque()  # FIFO queue of tx_ids
        self.balances = balances or {}  # Reference to blockchain balances
    
    def accept(self, tx: Tx) -> bool:
        """
        Accept a transaction into the mempool if valid.
        
        Validates the transaction:
        - Rejects duplicates by tx_id
        - Ensures sender can afford amount + BASE_FEE + TIP
        
        Args:
            tx (Tx): The transaction to add.
            
        Returns:
            bool: Whether the transaction was accepted successfully.
        """
        # Reject if already in mempool (duplicate tx_id)
        if tx.tx_id in self.transactions:
            return False
        
        # Validate sender has sufficient funds
        sender_balance = self.balances.get(tx.sender, 0)
        total_cost = calculate_transaction_cost(tx)
        
        if sender_balance < total_cost:
            return False
            
        # Accept the transaction
        self.transactions[tx.tx_id] = tx
        self.tx_queue.append(tx.tx_id)
        
        return True
    
    def get_batch(self, max_txs: int = 4) -> List[Tx]:
        """
        Get a batch of transactions from the mempool (FIFO order).
        
        Args:
            max_txs (int, optional): Maximum number of transactions to return. Defaults to 4.
            
        Returns:
            List[Tx]: List of transactions, up to max_txs.
        """
        result = []
        tx_ids_to_remove = []
        
        # Try to get up to max_txs transactions
        for _ in range(min(max_txs, len(self.tx_queue))):
            tx_id = self.tx_queue.popleft()
            tx = self.transactions.get(tx_id)
            
            # Skip if somehow not in transactions dictionary (should never happen)
            if not tx:
                continue
                
            result.append(tx)
            tx_ids_to_remove.append(tx_id)
        
        # Remove returned transactions from the mempool
        for tx_id in tx_ids_to_remove:
            if tx_id in self.transactions:
                del self.transactions[tx_id]
        
        return result
    
    def update_balances(self, balances: Dict[str, int]) -> None:
        """
        Update the reference to blockchain balances.
        
        Args:
            balances (Dict[str, int]): Updated blockchain balances.
        """
        self.balances = balances
    
    def size(self) -> int:
        """
        Get the number of transactions in the mempool.
        
        Returns:
            int: Number of transactions.
        """
        return len(self.transactions)
    
    def clear(self) -> None:
        """Clear all transactions from the mempool."""
        self.transactions.clear()
        self.tx_queue.clear()
