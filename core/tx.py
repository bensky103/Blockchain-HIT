"""
Transaction implementation for blockchain.
"""

import json
import hashlib
from typing import Optional, Dict, Any

class Tx:
    """
    Represents a transaction in the blockchain.
    
    Attributes:
        sender (str): Sender's address.
        recipient (str): Recipient's address.
        amount (int): Amount being transferred.
        nonce (int): Transaction sequence number for the sender.
        base_fee (int): Base fee for the transaction (EIP-1559 style).
        tip (int): Priority fee/tip for miners (EIP-1559 style).
        tx_id (str): SHA-256 hash of the canonical JSON representation.
        signature (Optional[str]): Digital signature of the transaction.
    """
    
    def __init__(
        self, 
        sender: str, 
        recipient: str, 
        amount: int, 
        nonce: int, 
        base_fee: int = 2, 
        tip: int = 3, 
        tx_id: Optional[str] = None,
        signature: Optional[str] = None
    ):
        """
        Initialize a new Transaction.
        
        Args:
            sender (str): Sender's address.
            recipient (str): Recipient's address.
            amount (int): Amount being transferred.
            nonce (int): Transaction sequence number for the sender.
            base_fee (int, optional): Base fee for the transaction. Defaults to 2.
            tip (int, optional): Priority fee/tip for miners. Defaults to 3.
            tx_id (Optional[str], optional): Transaction ID. If None, will be computed.
            signature (Optional[str], optional): Digital signature. Defaults to None.
        """
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.nonce = nonce
        self.base_fee = base_fee
        self.tip = tip
        self.signature = signature
        
        # Generate tx_id if not provided
        if tx_id is None:
            self.tx_id = self._calculate_tx_id()
        else:
            self.tx_id = tx_id
    
    def _calculate_tx_id(self) -> str:
        """
        Calculate the deterministic transaction ID.
        
        Returns:
            str: SHA-256 hash of the canonical JSON representation.
        """
        # Create a dictionary excluding the signature
        tx_dict = self.to_dict(include_signature=False)
        
        # Convert to canonical JSON (sorted keys, no whitespace)
        canonical_json = json.dumps(tx_dict, sort_keys=True, separators=(',', ':'))
        
        # Calculate SHA-256 hash
        return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
    
    def to_dict(self, include_signature: bool = True) -> Dict[str, Any]:
        """
        Convert transaction to dictionary.
        
        Args:
            include_signature (bool, optional): Whether to include the signature. 
                                               Defaults to True.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the transaction.
        """
        result = {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "nonce": self.nonce,
            "base_fee": self.base_fee,
            "tip": self.tip,
        }
        
        # Only include signature if requested and it exists
        if include_signature and self.signature is not None:
            result["signature"] = self.signature
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Tx':
        """
        Create a transaction from dictionary.
        
        Args:
            data (Dict[str, Any]): Dictionary representation of the transaction.
        
        Returns:
            Tx: New transaction instance.
        """
        # Extract required fields
        sender = data["sender"]
        recipient = data["recipient"]
        amount = data["amount"]
        nonce = data["nonce"]
        
        # Extract optional fields with defaults
        base_fee = data.get("base_fee", 2)
        tip = data.get("tip", 3)
        signature = data.get("signature")
        tx_id = data.get("tx_id")
        
        # Create and return new transaction
        return cls(
            sender=sender,
            recipient=recipient,
            amount=amount,
            nonce=nonce,
            base_fee=base_fee,
            tip=tip,
            tx_id=tx_id,
            signature=signature
        )
    
    def sign(self, private_key: str) -> None:
        """
        Sign the transaction with the private key.
        
        Args:
            private_key (str): The private key to sign the transaction with.
        """
        # TODO: Implement transaction signing
        pass
    
    def verify_signature(self) -> bool:
        """
        Verify the signature of this transaction.
        
        Returns:
            bool: Whether the signature is valid.
        """
        # TODO: Implement signature verification
        pass
