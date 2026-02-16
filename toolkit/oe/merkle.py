"""
Merkle tree module for orthogonal-engineering.

Implements binary Merkle tree construction with the following specification:
- Leaf nodes: SHA-256(0x00 || canonical_bytes)
- Internal nodes: SHA-256(0x01 || left_hash || right_hash)
- Leaves ordered by canonical file path (UTF-8 lexicographic)
- Produces root hash and per-leaf inclusion proofs

Author: Orthogonal Engineering System
Date: 2026-02-16
Version: 1.0.0
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple, Union

from .canonicalizer import canonical_byte_representation, canonical_path


class MerkleNode:
    """Represents a node in the Merkle tree."""
    
    def __init__(self, hash_value: str, left=None, right=None, file_path: str = None):
        """
        Initialize Merkle node.
        
        Args:
            hash_value: Hash of this node
            left: Left child node (for internal nodes)
            right: Right child node (for internal nodes)
            file_path: Original file path (for leaf nodes)
        """
        self.hash = hash_value
        self.left = left
        self.right = right
        self.file_path = file_path
        
    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        return self.left is None and self.right is None


class MerkleTree:
    """Binary Merkle tree for file integrity verification."""
    
    def __init__(self, file_paths: List[Union[str, Path]], base_path: Union[str, Path] = None):
        """
        Build Merkle tree from files.
        
        Args:
            file_paths: List of file paths to include in tree
            base_path: Optional base path for canonical path generation
        """
        self.base_path = base_path
        self.file_paths = sorted([str(p) for p in file_paths])  # Sort for determinism
        self.leaves: List[MerkleNode] = []
        self.root: MerkleNode = None
        
        # Build the tree
        self._build_tree()
    
    def _build_tree(self):
        """Build the Merkle tree from files."""
        # Create leaf nodes
        leaf_data = []
        for file_path in self.file_paths:
            canon_path = canonical_path(file_path, self.base_path)
            leaf_data.append((canon_path, file_path))
        
        # Sort by canonical path for deterministic ordering
        leaf_data.sort(key=lambda x: x[0])
        
        # Generate leaf hashes
        for canon_path, file_path in leaf_data:
            canonical_bytes = canonical_byte_representation(file_path)
            leaf_hash = self._compute_leaf_hash(canonical_bytes)
            leaf_node = MerkleNode(leaf_hash, file_path=file_path)
            self.leaves.append(leaf_node)
        
        # Build tree from leaves
        if not self.leaves:
            raise ValueError("Cannot build Merkle tree with no files")
        
        self.root = self._build_tree_recursive(self.leaves)
    
    def _compute_leaf_hash(self, data: bytes) -> str:
        """
        Compute leaf node hash: SHA-256(0x00 || data).
        
        Args:
            data: Canonical bytes of file
            
        Returns:
            Lowercase hexadecimal hash
        """
        return hashlib.sha256(b'\x00' + data).hexdigest()
    
    def _compute_internal_hash(self, left_hash: str, right_hash: str) -> str:
        """
        Compute internal node hash: SHA-256(0x01 || left || right).
        
        Args:
            left_hash: Hash of left child (hex string)
            right_hash: Hash of right child (hex string)
            
        Returns:
            Lowercase hexadecimal hash
        """
        left_bytes = bytes.fromhex(left_hash)
        right_bytes = bytes.fromhex(right_hash)
        return hashlib.sha256(b'\x01' + left_bytes + right_bytes).hexdigest()
    
    def _build_tree_recursive(self, nodes: List[MerkleNode]) -> MerkleNode:
        """
        Recursively build Merkle tree from nodes.
        
        Args:
            nodes: List of nodes at current level
            
        Returns:
            Root node of (sub)tree
        """
        if len(nodes) == 1:
            return nodes[0]
        
        # Build next level
        next_level = []
        for i in range(0, len(nodes), 2):
            left = nodes[i]
            # If odd number of nodes, duplicate last node
            right = nodes[i + 1] if i + 1 < len(nodes) else nodes[i]
            
            parent_hash = self._compute_internal_hash(left.hash, right.hash)
            parent = MerkleNode(parent_hash, left=left, right=right)
            next_level.append(parent)
        
        return self._build_tree_recursive(next_level)
    
    def get_root_hash(self) -> str:
        """
        Get Merkle root hash.
        
        Returns:
            Root hash as lowercase hexadecimal string
        """
        return self.root.hash if self.root else ""
    
    def get_proof(self, file_path: Union[str, Path]) -> List[Tuple[str, str]]:
        """
        Get inclusion proof for a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of (position, hash) tuples representing proof path
            position is 'left' or 'right' indicating sibling position
            
        Raises:
            ValueError: If file not in tree
        """
        file_path = str(file_path)
        
        # Find leaf index
        leaf_index = None
        for i, leaf in enumerate(self.leaves):
            if leaf.file_path == file_path:
                leaf_index = i
                break
        
        if leaf_index is None:
            raise ValueError(f"File not in tree: {file_path}")
        
        # Build proof by traversing from leaf to root
        proof = []
        current_nodes = self.leaves[:]
        current_index = leaf_index
        
        while len(current_nodes) > 1:
            # Determine sibling
            if current_index % 2 == 0:
                # Current is left child
                sibling_index = current_index + 1 if current_index + 1 < len(current_nodes) else current_index
                sibling_hash = current_nodes[sibling_index].hash
                proof.append(('right', sibling_hash))
            else:
                # Current is right child
                sibling_index = current_index - 1
                sibling_hash = current_nodes[sibling_index].hash
                proof.append(('left', sibling_hash))
            
            # Move to parent level
            next_level = []
            for i in range(0, len(current_nodes), 2):
                left = current_nodes[i]
                right = current_nodes[i + 1] if i + 1 < len(current_nodes) else current_nodes[i]
                parent_hash = self._compute_internal_hash(left.hash, right.hash)
                parent = MerkleNode(parent_hash, left=left, right=right)
                next_level.append(parent)
            
            current_nodes = next_level
            current_index = current_index // 2
        
        return proof
    
    def verify_proof(self, file_path: Union[str, Path], proof: List[Tuple[str, str]]) -> bool:
        """
        Verify inclusion proof for a file.
        
        Args:
            file_path: Path to file
            proof: Inclusion proof from get_proof()
            
        Returns:
            True if proof is valid
        """
        # Compute leaf hash
        canonical_bytes = canonical_byte_representation(file_path)
        current_hash = self._compute_leaf_hash(canonical_bytes)
        
        # Apply proof steps
        for position, sibling_hash in proof:
            if position == 'left':
                current_hash = self._compute_internal_hash(sibling_hash, current_hash)
            else:  # 'right'
                current_hash = self._compute_internal_hash(current_hash, sibling_hash)
        
        return current_hash == self.get_root_hash()
    
    def export_proofs_jsonl(self, output_path: Union[str, Path]):
        """
        Export all inclusion proofs to JSONL file.
        
        Args:
            output_path: Path to output JSONL file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            for leaf in self.leaves:
                proof = self.get_proof(leaf.file_path)
                canon_path = canonical_path(leaf.file_path, self.base_path)
                
                record = {
                    'file_path': canon_path,
                    'leaf_hash': leaf.hash,
                    'proof': [{'position': pos, 'hash': h} for pos, h in proof],
                    'root_hash': self.get_root_hash()
                }
                
                f.write(json.dumps(record, sort_keys=True) + '\n')
