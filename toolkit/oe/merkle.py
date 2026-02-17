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
Merkle tree module for building deterministic binary Merkle trees.

Implements:
- Leaf nodes: SHA-256(0x00 || canonical_bytes)
- Internal nodes: SHA-256(0x01 || left || right)
- Leaves ordered by canonical path (UTF-8 lexicographic)
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
