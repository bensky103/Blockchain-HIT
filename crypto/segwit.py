# NOT FOR PRODUCTION
# This is a simplified implementation for educational purposes.

from typing import Dict, Optional

# A simple in-memory store for signatures, mapping tx_id to signature.
# In a real system, this would be a persistent, distributed database.
SIGNATURE_STORE: Dict[str, bytes] = {}

def store_signature(tx_id: str, signature: bytes):
    """Stores a signature in the external store."""
    SIGNATURE_STORE[tx_id] = signature

def get_signature(tx_id: str) -> Optional[bytes]:
    """Retrieves a signature from the external store."""
    return SIGNATURE_STORE.get(tx_id)

def clear_store():
    """Clears the signature store (for testing)."""
    SIGNATURE_STORE.clear()
