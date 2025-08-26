"""
Bloom filter implementation.
"""

import hashlib

class BloomFilter:
    """
    Implements a Bloom filter for efficient membership testing.
    
    Attributes:
        m_bits (int): Size of the bit array in bits.
        k (int): Number of hash functions.
        bit_array (list): Bit array for the filter.
    """
    
    def __init__(self, m_bits=2048, k=3):
        """
        Initialize a new Bloom filter.
        
        Args:
            m_bits (int, optional): Size of the bit array. Defaults to 2048.
            k (int, optional): Number of hash functions. Defaults to 3.
        """
        self.m_bits = m_bits
        self.k = k
        self.bit_array = [0] * m_bits
    
    def add(self, item: bytes):
        """
        Add an item to the filter.
        
        Args:
            item (bytes): Item to add as bytes.
        """
        if not isinstance(item, bytes):
            raise TypeError("Item must be bytes")
            
        for i in range(self.k):
            index = self._hash(item, i)
            self.bit_array[index] = 1
    
    def might_contain(self, item: bytes) -> bool:
        """
        Check if an item might be in the filter.
        Bloom filters guarantee no false negatives but may have false positives.
        
        Args:
            item (bytes): Item to check as bytes.
            
        Returns:
            bool: True if the item might be in the filter, False if it definitely is not.
        """
        if not isinstance(item, bytes):
            raise TypeError("Item must be bytes")
            
        for i in range(self.k):
            index = self._hash(item, i)
            if self.bit_array[index] == 0:
                return False
        return True
    
    def _hash(self, item: bytes, seed: int) -> int:
        """
        Hash function for the bloom filter using SHA-256 with different seeds.
        
        Args:
            item (bytes): Item to hash.
            seed (int): Seed for the hash function.
            
        Returns:
            int: Hash value (index in bit array).
        """
        # Use SHA-256 with different seeds by prepending the seed to the item
        seed_bytes = str(seed).encode('utf-8')
        hash_input = seed_bytes + item
        hash_value = int(hashlib.sha256(hash_input).hexdigest(), 16)
        return hash_value % self.m_bits
