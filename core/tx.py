"""
Transaction implementation for blockchain.
"""

import json
import hashlib
from typing import Optional, Dict, Any
from blockchain_lab.crypto import keys, signatures, segwit

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
        sender_pubkey (Optional[str]): Public key of the sender.
        signature (Optional[bytes]): Digital signature of the transaction.
        tx_id (str): SHA-256 hash of the canonical JSON representation.
    """
    
    def __init__(
        self, 
        sender: str, 
        recipient: str, 
        amount: int, 
        nonce: int, 
        base_fee: int = 2, 
        tip: int = 3, 
        sender_pubkey: Optional[str] = None,
        signature: Optional[bytes] = None,
        tx_id: Optional[str] = None,
        private_key: Optional[Any] = None
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
            sender_pubkey (Optional[str], optional): Public key of the sender.
            signature (Optional[bytes], optional): Digital signature. Defaults to None.
            tx_id (Optional[str], optional): Transaction ID. If None, will be computed.
            private_key (Optional[Any], optional): If provided, sign the transaction.
        """
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.nonce = nonce
        self.base_fee = base_fee
        self.tip = tip
        self.sender_pubkey = sender_pubkey
        self.signature = signature
        
        # Generate tx_id if not provided
        if tx_id is None:
            self.tx_id = self._calculate_tx_id()
        else:
            self.tx_id = tx_id
        
        if private_key:
            self.sign(private_key)

    def _calculate_tx_id(self) -> str:
        """
        Calculate the deterministic transaction ID.
        
        Returns:
            str: SHA-256 hash of the canonical JSON representation.
        """
        # Create a dictionary excluding the signature and pubkey
        tx_dict = self.to_dict(include_signature=False, include_pubkey=False)
        
        # Convert to canonical JSON (sorted keys, no whitespace)
        canonical_json = json.dumps(tx_dict, sort_keys=True, separators=(',', ':'))
        
        # Calculate SHA-256 hash
        return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

    def get_preimage(self) -> bytes:
        """
        Get the transaction data to be signed (preimage).
        """
        tx_dict = self.to_dict(include_signature=False, include_pubkey=False)
        canonical_json = json.dumps(tx_dict, sort_keys=True, separators=(',', ':'))
        return canonical_json.encode('utf-8')

    def to_dict(self, include_signature: bool = True, include_pubkey: bool = True) -> Dict[str, Any]:
        """
        Convert transaction to dictionary.
        
        Args:
            include_signature (bool, optional): Whether to include the signature. 
            include_pubkey (bool, optional): Whether to include the sender's public key.
        
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
        
        if include_pubkey and self.sender_pubkey is not None:
            result["sender_pubkey"] = self.sender_pubkey
            
        if include_signature and self.signature is not None:
            result["signature"] = self.signature.hex()
            
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
        sender_pubkey = data.get("sender_pubkey")
        signature_hex = data.get("signature")
        signature = bytes.fromhex(signature_hex) if signature_hex else None
        tx_id = data.get("tx_id")
        
        # Create and return new transaction
        return cls(
            sender=sender,
            recipient=recipient,
            amount=amount,
            nonce=nonce,
            base_fee=base_fee,
            tip=tip,
            sender_pubkey=sender_pubkey,
            signature=signature,
            tx_id=tx_id
        )
    
    def sign(self, private_key, detach: bool = False) -> None:
        """Sign the transaction with the private key.

        If detach=True, store signature in external segwit store and clear the in-memory
        signature (full SegWit style separation) so block / mempool objects remain lean.
        """
        self.sender_pubkey = keys.serialize_public_key(private_key.public_key())
        preimage = self.get_preimage()
        sig = signatures.sign_data(private_key, preimage)
        if detach:
            segwit.store_signature(self.tx_id, sig)
            self.signature = None
        else:
            self.signature = sig
    
    def verify_signature(self) -> bool:
        """Verify the transaction signature.

        Accepts either an attached signature (legacy) or one stored externally
        in the segwit store keyed by tx_id. Returns False if neither present.
        """
        if not self.sender_pubkey:
            return False
        # Prefer attached signature, else fetch from store
        sig = self.signature or segwit.get_signature(self.tx_id)
        if not sig:
            return False
        public_key = keys.deserialize_public_key(self.sender_pubkey)
        preimage = self.get_preimage()
        return signatures.verify_signature(public_key, sig, preimage)

