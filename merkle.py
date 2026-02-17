"""
Merkle tree builder following binary Merkle tree specification.

This module implements a deterministic binary Merkle tree with:
- Leaf nodes: sha256(0x00 || canonical_bytes)
- Internal nodes: sha256(0x01 || left_hash || right_hash)
- Leaves ordered by canonical path (UTF-8 lexicographic)
- JSONL inclusion proofs output

Author: Orthogonal Engineering
Date: 2026-02-16
Version: 1.0.0
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple

from hasher import sha256_hex


class MerkleNode:
    """Represents a node in the Merkle tree."""
    
    def __init__(self, hash_value: str, left=None, right=None, path: str = None):
        """
        Initialize Merkle node.
        
        Args:
            hash_value: Hash value of this node
            left: Left child node
            right: Right child node
            path: File path for leaf nodes
        """
        self.hash_value = hash_value
        self.left = left
        self.right = right
        self.path = path
        self.is_leaf = (left is None and right is None)


class MerkleTreeBuilder:
    """Build binary Merkle trees with inclusion proofs."""
    
    def __init__(self):
        """Initialize Merkle tree builder."""
        self.leaves: List[MerkleNode] = []
        self.root: MerkleNode = None
    
    def add_leaf(self, canonical_path: str, canonical_bytes: bytes) -> None:
        """
        Add a leaf node to the tree.
        
        Leaf hash = sha256(0x00 || canonical_bytes)
        
        Args:
            canonical_path: Canonical path for ordering
            canonical_bytes: Canonicalized file content
        """
        # Compute leaf hash: sha256(0x00 || data)
        leaf_data = b'\x00' + canonical_bytes
        leaf_hash = sha256_hex(leaf_data)
        
        leaf = MerkleNode(leaf_hash, path=canonical_path)
        self.leaves.append(leaf)
    
    def build_tree(self) -> str:
        """
        Build the Merkle tree and return the root hash.
        
        Leaves are ordered by canonical path (UTF-8 lexicographic).
        Internal nodes: sha256(0x01 || left_hash || right_hash)
        
        Returns:
            Root hash as hexadecimal string
        """
        if not self.leaves:
            # Empty tree
            return sha256_hex(b'')
        
        # Sort leaves by canonical path (UTF-8 lexicographic)
        sorted_leaves = sorted(self.leaves, key=lambda n: n.path.encode('utf-8'))
        
        # Build tree bottom-up
        current_level = sorted_leaves
        
        while len(current_level) > 1:
            next_level = []
            
            # Process pairs
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                
                if i + 1 < len(current_level):
                    # We have a pair
                    right = current_level[i + 1]
                else:
                    # Odd number of nodes, duplicate the last one
                    right = current_level[i]
                
                # Compute internal node hash: sha256(0x01 || left_hash || right_hash)
                internal_data = b'\x01' + bytes.fromhex(left.hash_value) + bytes.fromhex(right.hash_value)
                internal_hash = sha256_hex(internal_data)
                
                internal_node = MerkleNode(internal_hash, left, right)
                next_level.append(internal_node)
            
            current_level = next_level
        
        self.root = current_level[0]
        return self.root.hash_value
    
    def generate_inclusion_proof(self, target_path: str) -> Dict:
        """
        Generate inclusion proof for a specific file.
        
        Args:
            target_path: Canonical path of the file
            
        Returns:
            Inclusion proof dictionary with path, sibling hashes, and directions
        """
        if not self.root:
            raise ValueError("Tree must be built before generating proofs")
        
        # Find the leaf
        target_leaf = None
        sorted_leaves = sorted(self.leaves, key=lambda n: n.path.encode('utf-8'))
        
        for i, leaf in enumerate(sorted_leaves):
            if leaf.path == target_path:
                target_leaf = leaf
                break
        
        if not target_leaf:
            raise ValueError(f"Path not found in tree: {target_path}")
        
        # Build proof by traversing from leaf to root
        proof = {
            'path': target_path,
            'leaf_hash': target_leaf.hash_value,
            'siblings': [],
            'root_hash': self.root.hash_value
        }
        
        # Reconstruct path to root
        current_level = sorted_leaves
        current_index = sorted_leaves.index(target_leaf)
        
        while len(current_level) > 1:
            # Determine sibling
            if current_index % 2 == 0:
                # We're the left child
                if current_index + 1 < len(current_level):
                    sibling_hash = current_level[current_index + 1].hash_value
                    direction = 'right'
                else:
                    # Duplicate ourselves
                    sibling_hash = current_level[current_index].hash_value
                    direction = 'right'
            else:
                # We're the right child
                sibling_hash = current_level[current_index - 1].hash_value
                direction = 'left'
            
            proof['siblings'].append({
                'hash': sibling_hash,
                'direction': direction
            })
            
            # Move up to parent level
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                if i + 1 < len(current_level):
                    right = current_level[i + 1]
                else:
                    right = current_level[i]
                
                internal_data = b'\x01' + bytes.fromhex(left.hash_value) + bytes.fromhex(right.hash_value)
                internal_hash = sha256_hex(internal_data)
                internal_node = MerkleNode(internal_hash, left, right)
                next_level.append(internal_node)
            
            current_level = next_level
            current_index = current_index // 2
        
        return proof
    
    def write_proofs(self, output_path: Path) -> None:
        """
        Write inclusion proofs for all leaves to JSONL file.
        
        Args:
            output_path: Path to output JSONL file
        """
        if not self.root:
            raise ValueError("Tree must be built before writing proofs")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            for leaf in self.leaves:
                proof = self.generate_inclusion_proof(leaf.path)
                f.write(json.dumps(proof) + '\n')


def verify_inclusion_proof(proof: Dict) -> bool:
    """
    Verify an inclusion proof.
    
    Args:
        proof: Inclusion proof dictionary
        
    Returns:
        True if proof is valid, False otherwise
    """
    # Start with leaf hash
    current_hash = proof['leaf_hash']
    
    # Apply siblings to reconstruct root
    for sibling in proof['siblings']:
        sibling_hash = sibling['hash']
        direction = sibling['direction']
        
        if direction == 'right':
            # Sibling is on the right
            internal_data = b'\x01' + bytes.fromhex(current_hash) + bytes.fromhex(sibling_hash)
        else:
            # Sibling is on the left
            internal_data = b'\x01' + bytes.fromhex(sibling_hash) + bytes.fromhex(current_hash)
        
        current_hash = sha256_hex(internal_data)
    
    # Check if we reached the correct root
    return current_hash == proof['root_hash']
