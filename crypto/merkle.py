"""
Merkle tree implementation.
"""

import hashlib
from typing import List, Tuple, Union
from ..core.tx import Tx

def _hash_tx_id(tx_id: str) -> str:
    """
    Hash a transaction ID using SHA-256.
    
    Args:
        tx_id (str): Transaction ID to hash.
        
    Returns:
        str: SHA-256 hash of the transaction ID as hexadecimal string.
    """
    return hashlib.sha256(tx_id.encode('utf-8')).hexdigest()

def merkle_root(txs: List[Tx]) -> str:
    """
    Calculate the Merkle root for a list of transactions.
    
    Args:
        txs (List[Tx]): List of transactions.
        
    Returns:
        str: Merkle root hash as hexadecimal string.
    """
    if not txs:
        return hashlib.sha256(b'').hexdigest()
    
    # Extract tx_ids and hash them to get leaf nodes
    leaves = [_hash_tx_id(tx.tx_id) for tx in txs]
    
    # Build the tree
    return _build_merkle_tree(leaves)

def _build_merkle_tree(nodes: List[str]) -> str:
    """
    Build a Merkle tree from a list of nodes and return the root hash.
    
    Args:
        nodes (List[str]): List of node hashes.
        
    Returns:
        str: Root hash of the Merkle tree.
    """
    if len(nodes) == 1:
        return nodes[0]
    
    new_level = []
    # Process nodes in pairs
    for i in range(0, len(nodes), 2):
        if i + 1 < len(nodes):
            # Hash the concatenation of two adjacent nodes
            new_level.append(hashlib.sha256((nodes[i] + nodes[i + 1]).encode('utf-8')).hexdigest())
        else:
            # Odd number of nodes, duplicate the last one
            new_level.append(hashlib.sha256((nodes[i] + nodes[i]).encode('utf-8')).hexdigest())
    
    # Recursively build the tree
    return _build_merkle_tree(new_level)

def merkle_proof(txs: List[Tx], target_tx_id: str) -> List[Tuple[str, str]]:
    """
    Generate a Merkle proof for a transaction.
    
    Args:
        txs (List[Tx]): List of transactions in the block.
        target_tx_id (str): ID of the transaction to generate the proof for.
        
    Returns:
        List[Tuple[str, str]]: List of (side, sibling_hash) tuples where side is 'left' or 'right'.
    """
    # Extract and hash tx_ids to get leaf nodes
    leaves = [_hash_tx_id(tx.tx_id) for tx in txs]
    
    # Find the index of the target transaction
    target_hash = _hash_tx_id(target_tx_id)
    try:
        target_index = leaves.index(target_hash)
    except ValueError:
        # Transaction not in list
        return []
    
    return _build_proof(leaves, target_index)

def _build_proof(nodes: List[str], target_index: int) -> List[Tuple[str, str]]:
    """
    Build a Merkle proof for a target node at the given index.
    
    Args:
        nodes (List[str]): List of node hashes.
        target_index (int): Index of the target node.
        
    Returns:
        List[Tuple[str, str]]: List of (side, sibling_hash) tuples.
    """
    if len(nodes) == 1:
        return []
    
    proof = []
    level = nodes
    current_index = target_index
    
    while len(level) > 1:
        new_level = []
        
        # Figure out which node in the pair is the sibling
        is_right_node = current_index % 2 == 1  # If index is odd, it's the right node of a pair
        pair_start_idx = current_index - 1 if is_right_node else current_index
        sibling_index = current_index + 1 if not is_right_node else current_index - 1
        
        # Handle edge case when last node in odd-length level
        if sibling_index >= len(level):
            sibling_index = current_index  # Duplicate the current node
        
        # Add the sibling to the proof with correct side indication
        side = 'left' if is_right_node else 'right'
        proof.append((side, level[sibling_index]))
        
        # Build the next level of the tree
        for i in range(0, len(level), 2):
            if i + 1 < len(level):
                # Hash the concatenation of two adjacent nodes
                new_level.append(hashlib.sha256((level[i] + level[i + 1]).encode('utf-8')).hexdigest())
            else:
                # Odd number of nodes, duplicate the last one
                new_level.append(hashlib.sha256((level[i] + level[i]).encode('utf-8')).hexdigest())
        
        # Update the index for the next level
        current_index = pair_start_idx // 2
        level = new_level
        
    return proof

def verify_proof(root: str, target_tx_id: str, proof: List[Tuple[str, str]]) -> bool:
    """
    Verify a Merkle proof.
    
    Args:
        root (str): Merkle root hash.
        target_tx_id (str): ID of the transaction to verify.
        proof (List[Tuple[str, str]]): List of (side, sibling_hash) tuples.
        
    Returns:
        bool: Whether the proof is valid.
    """
    # Start with the hash of the target transaction
    current = _hash_tx_id(target_tx_id)
    
    # If no proof is provided but we're asked to verify against the root,
    # this could be the case of a single-transaction block
    if not proof and len(current) == len(root):
        # If there's only one transaction, its hash is the Merkle root
        return current == root
    
    # Apply each step in the proof
    for side, sibling in proof:
        if side == 'left':
            # Sibling is on the left, so it comes first in the concatenation
            current = hashlib.sha256((sibling + current).encode('utf-8')).hexdigest()
        else:
            # Sibling is on the right, so it comes second
            current = hashlib.sha256((current + sibling).encode('utf-8')).hexdigest()
    
    # Check if the final hash matches the root
    return current == root
