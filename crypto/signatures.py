# NOT FOR PRODUCTION
# This is a simplified implementation for educational purposes.

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature

def sign_data(private_key, data: bytes) -> bytes:
    """Signs data using the private key."""
    return private_key.sign(data, ec.ECDSA(hashes.SHA256()))

def verify_signature(public_key, signature: bytes, data: bytes) -> bool:
    """Verifies a signature using the public key."""
    try:
        public_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False
