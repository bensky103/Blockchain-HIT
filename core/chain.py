"""
Blockchain implementation.
"""

from typing import List, Dict, Optional, Union, Any
from .block import Block, BlockHeader
from .tx import Tx

class Blockchain:
    """
    Represents a blockchain.
    
    Attributes:
        blocks (List[Block]): List of blocks in the chain.
        balances (Dict[str, int]): Current account balances.
        total_burned (int): Total fees burned (EIP-1559 style).
        total_mined (int): Total new coins mined.
        difficulty (int): Mining difficulty.
    """
    
    def __init__(self, difficulty: int = 4):
        """
        Initialize a new blockchain.
        
        Args:
            difficulty (int, optional): Mining difficulty.
        """
        self.blocks: List[Block] = []
        self.balances: Dict[str, int] = {}
        self.total_burned: int = 0
        self.total_mined: int = 0
        self.difficulty: int = difficulty
    
    def add_genesis(self, initial_balances: Dict[str, int], miner_address: str = "genesis") -> Block:
        """
        Add the genesis block with initial account balances.
        
        Args:
            initial_balances (Dict[str, int]): Initial account balances.
            miner_address (str, optional): Address to receive mining reward. Defaults to "genesis".
            
        Returns:
            Block: The genesis block.
        """
        if self.blocks:
            raise ValueError("Genesis block already exists")
        
        # Set initial balances
        self.balances = initial_balances.copy()
        
        # Create genesis block
        genesis_block = Block.create_genesis_block(miner_address)
        
        # Add to chain
        self.blocks.append(genesis_block)
        
        return genesis_block
    
    def validate_block_structure(self, block: Block) -> bool:
        """
        Validate the structure of a block (without validating transactions or mining).
        
        Validation rules:
        - Block has required attributes
        - Header has required fields
        - Block index is correct (sequential)
        - Previous hash matches the hash of the last block in chain
        - Block has at most 4 transactions
        
        Args:
            block (Block): The block to validate.
            
        Returns:
            bool: Whether the block has a valid structure.
        """
        # Check if the block has required attributes
        if not hasattr(block, 'header') or not hasattr(block, 'txs'):
            return False
        
        # Check header structure
        header = block.header
        required_header_attrs = ['index', 'prev_hash', 'merkle_root', 'timestamp', 
                                'nonce', 'miner_address']
        
        for attr in required_header_attrs:
            if not hasattr(header, attr):
                return False
        
        # Verify the block's index is correct
        if len(self.blocks) > 0:
            expected_index = self.blocks[-1].header.index + 1
            if header.index != expected_index:
                return False
        
        # Verify the previous hash points to the previous block
        if len(self.blocks) > 0:
            if header.prev_hash != self.blocks[-1].block_hash:
                return False
        
        # Verify the block has at most 4 transactions
        if len(block.txs) > 4:
            return False
                
        # Basic validation passed
        return True
    
    def apply_block(self, block: Block, miner_addr: str) -> bool:
        """
        Apply a block to the blockchain, including transaction effects and fees.
        
        For each included transaction:
          - Deduct amount + BASE_FEE + TIP from sender
          - Add amount to recipient
          - Add TIP to miner
          - Implicitly burn BASE_FEE
        After all transactions:
          - Add BLOCK_REWARD to miner
        
        Args:
            block (Block): The block to apply.
            miner_addr (str): Address of the miner who mined this block.
            
        Returns:
            bool: Whether the block was successfully applied.
        """
        # Validate block structure
        if not self.validate_block_structure(block):
            return False
        
        # Temporary copy of balances to validate and apply changes atomically
        temp_balances = self.balances.copy()
        
        # Track total burned and mined in this block
        block_burned = 0
        
        # Process each transaction in the block
        for tx in block.txs:
            # Skip invalid transactions
            if tx.sender not in temp_balances:
                continue
                
            # Check sender has enough funds
            sender_balance = temp_balances.get(tx.sender, 0)
            total_cost = tx.amount + tx.base_fee + tx.tip
            
            if sender_balance < total_cost:
                # Invalid transaction, don't include in block
                continue
            
            # Deduct amount + fees from sender
            temp_balances[tx.sender] = sender_balance - total_cost
            
            # Credit amount to recipient
            recipient_balance = temp_balances.get(tx.recipient, 0)
            temp_balances[tx.recipient] = recipient_balance + tx.amount
            
            # Credit tip to miner
            miner_balance = temp_balances.get(miner_addr, 0)
            temp_balances[miner_addr] = miner_balance + tx.tip
            
            # Track burned base fees
            block_burned += tx.base_fee
        
        # Apply block reward to miner
        miner_balance = temp_balances.get(miner_addr, 0)
        temp_balances[miner_addr] = miner_balance + 50  # BLOCK_REWARD
        
        # Update blockchain state
        self.balances = temp_balances
        self.total_burned += block_burned
        self.total_mined += 50  # BLOCK_REWARD
        
        # Add block to chain
        self.blocks.append(block)
        
        return True
        
    def add_block(self, block: Block, miner_addr: str) -> bool:
        """
        Validate and add a block to the blockchain.
        
        This method performs validation before applying the block:
        1. Validates the block structure
        2. Applies the block effects (transactions, fees, rewards)
        
        Args:
            block (Block): The block to add.
            miner_addr (str): Address of the miner who mined this block.
            
        Returns:
            bool: Whether the block was successfully added.
        """
        # First validate the block structure
        if not self.validate_block_structure(block):
            return False
        
        # Then apply the block (which will also validate transactions)
        return self.apply_block(block, miner_addr)
    
    def get_latest_block(self) -> Optional[Block]:
        """
        Get the latest block in the chain.
        
        Returns:
            Optional[Block]: The latest block, or None if the chain is empty.
        """
        return self.blocks[-1] if self.blocks else None
    
    def get_block_by_index(self, index: int) -> Optional[Block]:
        """
        Get a block by its index.
        
        Args:
            index (int): The index of the block to retrieve.
            
        Returns:
            Optional[Block]: The block at the specified index, or None if not found.
        """
        if 0 <= index < len(self.blocks):
            return self.blocks[index]
        return None
    
    def get_balance(self, address: str) -> int:
        """
        Get the balance of an account.
        
        Args:
            address (str): The account address.
            
        Returns:
            int: The account balance.
        """
        return self.balances.get(address, 0)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert blockchain to dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the blockchain.
        """
        return {
            "blocks": [block.to_dict() for block in self.blocks],
            "balances": self.balances,
            "total_burned": self.total_burned,
            "total_mined": self.total_mined,
            "difficulty": self.difficulty
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Blockchain':
        """
        Create a blockchain from dictionary.
        
        Args:
            data (Dict[str, Any]): Dictionary representation of the blockchain.
            
        Returns:
            Blockchain: New blockchain instance.
        """
        blockchain = cls(difficulty=data.get("difficulty", 4))
        blockchain.blocks = [Block.from_dict(block_data) for block_data in data["blocks"]]
        blockchain.balances = data["balances"]
        blockchain.total_burned = data["total_burned"]
        blockchain.total_mined = data["total_mined"]
        
        return blockchain
