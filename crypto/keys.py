# NOT FOR PRODUCTION
# This is a simplified implementation for educational purposes.

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend

def generate_key_pair():
    """Generates a new ECDSA key pair."""
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    public_key = private_key.public_key()
    return private_key, public_key

def serialize_public_key(public_key):
    """Serializes a public key to a PEM-encoded string."""
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

def serialize_private_key(private_key):
    """Serializes a private key to a PEM-encoded string."""
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')

def deserialize_public_key(pem_data):
    """Deserializes a public key from a PEM-encoded string."""
    return serialization.load_pem_public_key(pem_data.encode('utf-8'), default_backend())

def deserialize_private_key(hex_data):
    """Deserializes a private key from a hex string."""
    private_value = int(hex_data, 16)
    return ec.derive_private_key(private_value, ec.SECP256R1(), default_backend())

def get_address_from_pubkey(public_key):
    """Derives a simplified address from the public key."""
    pem = serialize_public_key(public_key)
    h = hashes.Hash(hashes.SHA256(), backend=default_backend())
    h.update(pem.encode('utf-8'))
    return h.finalize().hex()[:20]
