"""
Merkle tree module for building deterministic binary Merkle trees.

Implements:
- Leaf nodes: SHA-256(0x00 || canonical_bytes)
- Internal nodes: SHA-256(0x01 || left || right)
- Leaves ordered by canonical path (UTF-8 lexicographic)
"""

import hashlib
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple


class MerkleTree:
    """Binary Merkle tree with deterministic construction."""
    
    def __init__(self):
        self.leaves: List[Tuple[str, str]] = []  # [(path, hash), ...]
        self.root: str = ""
        self.tree_levels: List[List[str]] = []
        
    def add_leaf(self, path: str, leaf_hash: str) -> None:
        """
        Add a leaf to the tree.
        
        Args:
            path: Canonical path (will be sorted lexicographically)
            leaf_hash: Hash of canonical bytes (not yet prefixed)
        """
        self.leaves.append((path, leaf_hash))
    
    def build(self) -> str:
        """
        Build the Merkle tree and return the root hash.
        
        Returns:
            Root hash as hex string
        """
        if not self.leaves:
            # Empty tree has a special root
            return hashlib.sha256(b'').hexdigest()
        
        # Sort leaves by path (UTF-8 lexicographic)
        self.leaves.sort(key=lambda x: x[0])
        
        # Build leaf level with 0x00 prefix
        current_level = []
        for path, leaf_hash in self.leaves:
            # Leaf = SHA-256(0x00 || canonical_bytes_hash)
            # We already have the hash, so we prefix and hash again
            leaf_data = b'\x00' + bytes.fromhex(leaf_hash)
            leaf_node_hash = hashlib.sha256(leaf_data).hexdigest()
            current_level.append(leaf_node_hash)
        
        self.tree_levels = [current_level.copy()]
        
        # Build upper levels
        while len(current_level) > 1:
            next_level = []
            
            # Process pairs
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                
                if i + 1 < len(current_level):
                    right = current_level[i + 1]
                else:
                    # Odd number of nodes: duplicate last node
                    right = left
                
                # Internal node = SHA-256(0x01 || left || right)
                internal_data = b'\x01' + bytes.fromhex(left) + bytes.fromhex(right)
                internal_hash = hashlib.sha256(internal_data).hexdigest()
                next_level.append(internal_hash)
            
            self.tree_levels.append(next_level.copy())
            current_level = next_level
        
        self.root = current_level[0]
        return self.root
    
    def get_inclusion_proof(self, path: str) -> Dict[str, Any]:
        """
        Get inclusion proof for a specific path.
        
        Args:
            path: Path to get proof for
            
        Returns:
            Proof as dictionary with path, leaf_hash, proof_hashes, and root
        """
        # Find the index of the leaf
        leaf_index = None
        leaf_hash = None
        for i, (p, h) in enumerate(self.leaves):
            if p == path:
                leaf_index = i
                leaf_hash = h
                break
        
        if leaf_index is None:
            raise ValueError(f"Path not found in tree: {path}")
        
        # Build proof path
        proof_hashes = []
        index = leaf_index
        
        for level in self.tree_levels[:-1]:  # Exclude root level
            # Determine sibling index
            if index % 2 == 0:
                # Left child, sibling is right
                sibling_index = index + 1
                if sibling_index < len(level):
                    proof_hashes.append({
                        'position': 'right',
                        'hash': level[sibling_index]
                    })
                else:
                    # No sibling (odd number), duplicate self
                    proof_hashes.append({
                        'position': 'right',
                        'hash': level[index]
                    })
            else:
                # Right child, sibling is left
                sibling_index = index - 1
                proof_hashes.append({
                    'position': 'left',
                    'hash': level[sibling_index]
                })
            
            # Move to parent level
            index = index // 2
        
        return {
            'path': path,
            'leaf_hash': leaf_hash,
            'proof': proof_hashes,
            'root': self.root
        }
    
    def export_proofs_jsonl(self, output_path: Path) -> None:
        """
        Export inclusion proofs for all leaves as JSONL.
        
        Args:
            output_path: Path to output JSONL file
        """
        with open(output_path, 'w') as f:
            for path, _ in self.leaves:
                proof = self.get_inclusion_proof(path)
                f.write(json.dumps(proof, separators=(',', ':')) + '\n')


def build_merkle_tree_from_files(file_hashes: List[Tuple[str, str]]) -> MerkleTree:
    """
    Build a Merkle tree from a list of file paths and their hashes.
    
    Args:
        file_hashes: List of (canonical_path, hash) tuples
        
    Returns:
        Built MerkleTree
    """
    tree = MerkleTree()
    for path, hash_value in file_hashes:
        tree.add_leaf(path, hash_value)
    tree.build()
    return tree


def verify_inclusion_proof(proof: Dict[str, Any]) -> bool:
    """
    Verify a Merkle inclusion proof.
    
    Args:
        proof: Proof dictionary with path, leaf_hash, proof, and root
        
    Returns:
        True if proof is valid
    """
    # Start with leaf hash
    leaf_data = b'\x00' + bytes.fromhex(proof['leaf_hash'])
    current_hash = hashlib.sha256(leaf_data).hexdigest()
    
    # Apply proof hashes
    for step in proof['proof']:
        if step['position'] == 'left':
            # Sibling is on left
            internal_data = b'\x01' + bytes.fromhex(step['hash']) + bytes.fromhex(current_hash)
        else:
            # Sibling is on right
            internal_data = b'\x01' + bytes.fromhex(current_hash) + bytes.fromhex(step['hash'])
        
        current_hash = hashlib.sha256(internal_data).hexdigest()
    
    # Check if we arrived at the root
    return current_hash == proof['root']
