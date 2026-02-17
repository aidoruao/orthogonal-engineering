"""
Merkle Tree Module

Implements binary Merkle tree construction with:
- Leaf nodes: SHA-256(0x00 || canonical_bytes)
- Internal nodes: SHA-256(0x01 || left_hash || right_hash)
- Leaves ordered by canonical path (UTF-8 lexicographic)
- JSONL inclusion proofs
"""

import hashlib
import json
import os
from pathlib import Path
from typing import List, Tuple, Union, Optional

from .canonicalizer import canonical_byte_representation
from .hasher import compute_hash


class MerkleNode:
    """Represents a node in the Merkle tree."""
    
    def __init__(self, hash_value: str, left: Optional['MerkleNode'] = None, 
                 right: Optional['MerkleNode'] = None, file_path: Optional[str] = None):
        self.hash = hash_value
        self.left = left
        self.right = right
        self.file_path = file_path  # Only set for leaf nodes
    
    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        return self.left is None and self.right is None


class MerkleTree:
    """Binary Merkle tree for file integrity verification."""
    
    def __init__(self, root: MerkleNode, leaves: List[MerkleNode], 
                 leaf_to_siblings: Optional[dict] = None):
        self.root = root
        self.leaves = leaves
        # Map from leaf index to list of sibling hashes along path to root
        self.leaf_to_siblings = leaf_to_siblings or {}
    
    def get_root_hash(self) -> str:
        """Get the root hash of the tree."""
        return self.root.hash
    
    def get_proof(self, file_path: str) -> Optional[dict]:
        """
        Generate inclusion proof for a file.
        
        The proof includes sibling hashes along the path from leaf to root,
        allowing cryptographic verification without the full tree.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Proof dictionary with sibling hashes or None if file not in tree
        """
        # Find the leaf for this file
        leaf_index = None
        for i, leaf in enumerate(self.leaves):
            if leaf.file_path == file_path:
                leaf_index = i
                break
        
        if leaf_index is None:
            return None
        
        # Build proof with actual sibling hashes
        proof = {
            "file_path": file_path,
            "leaf_hash": self.leaves[leaf_index].hash,
            "root_hash": self.root.hash,
            "proof_path": self.leaf_to_siblings.get(leaf_index, [])
        }
        
        return proof


def compute_leaf_hash(canonical_bytes: bytes) -> str:
    """
    Compute Merkle leaf hash: SHA-256(0x00 || canonical_bytes).
    
    Args:
        canonical_bytes: Canonical byte representation of file
        
    Returns:
        Lowercase hexadecimal hash
    """
    prefix = b'\x00'
    data = prefix + canonical_bytes
    return hashlib.sha256(data).hexdigest()


def compute_internal_hash(left_hash: str, right_hash: str) -> str:
    """
    Compute Merkle internal node hash: SHA-256(0x01 || left || right).
    
    Args:
        left_hash: Left child hash (hex string)
        right_hash: Right child hash (hex string)
        
    Returns:
        Lowercase hexadecimal hash
    """
    prefix = b'\x01'
    left_bytes = bytes.fromhex(left_hash)
    right_bytes = bytes.fromhex(right_hash)
    data = prefix + left_bytes + right_bytes
    return hashlib.sha256(data).hexdigest()


def build_merkle_tree(file_paths: List[Union[str, Path]], 
                     base_path: Optional[Union[str, Path]] = None) -> MerkleTree:
    """
    Build binary Merkle tree from list of file paths.
    
    Files are sorted by canonical path (UTF-8 lexicographic order) before
    building the tree to ensure deterministic structure across systems.
    
    Args:
        file_paths: List of file paths to include in tree
        base_path: Optional base path for computing relative canonical paths.
                  If not provided, uses common parent or absolute paths.
        
    Returns:
        MerkleTree object with root and leaves
        
    Raises:
        ValueError: If file_paths is empty
    """
    if not file_paths:
        raise ValueError("Cannot build Merkle tree from empty file list")
    
    # Convert to Path objects
    paths = [Path(p) for p in file_paths]
    
    # Determine base path for canonical ordering
    if base_path:
        base = Path(base_path)
    else:
        # Find common parent
        try:
            base = Path(os.path.commonpath([str(p.resolve()) for p in paths]))
        except ValueError:
            # No common path, use current directory
            base = Path.cwd()
    
    # Create canonical path strings for sorting (POSIX-style, relative)
    def get_canonical_path(p: Path) -> str:
        """Get canonical path string for deterministic sorting."""
        try:
            # Get relative path from base
            rel_path = p.resolve().relative_to(base.resolve())
        except ValueError:
            # If not relative to base, use absolute but normalized
            rel_path = p.resolve()
        
        # Convert to POSIX-style path string (forward slashes)
        return rel_path.as_posix()
    
    # Sort paths by canonical path string
    paths.sort(key=get_canonical_path)
    
    # Build leaf nodes
    leaves = []
    for path in paths:
        canonical_bytes = canonical_byte_representation(path)
        leaf_hash = compute_leaf_hash(canonical_bytes)
        leaf = MerkleNode(leaf_hash, file_path=str(path))
        leaves.append(leaf)
    
    # Track sibling hashes for each leaf during tree construction
    # Map from current level index to list of (sibling_hash, position) tuples
    leaf_to_siblings = {i: [] for i in range(len(leaves))}
    
    # Map from node hash to leaf indices it represents
    node_to_leaf_indices = {leaf.hash: [i] for i, leaf in enumerate(leaves)}
    
    # Build tree bottom-up, tracking siblings
    current_level = leaves[:]
    
    while len(current_level) > 1:
        next_level = []
        next_node_to_leaf_indices = {}
        
        # Pair up nodes and create parents
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            
            if i + 1 < len(current_level):
                right = current_level[i + 1]
            else:
                # Odd number of nodes: duplicate last node
                right = current_level[i]
            
            # Track siblings for all leaves in left and right subtrees
            left_indices = node_to_leaf_indices.get(left.hash, [])
            right_indices = node_to_leaf_indices.get(right.hash, [])
            
            # For each leaf in left subtree, right node is sibling
            for leaf_idx in left_indices:
                leaf_to_siblings[leaf_idx].append({
                    "sibling_hash": right.hash,
                    "position": "right"
                })
            
            # For each leaf in right subtree, left node is sibling
            for leaf_idx in right_indices:
                leaf_to_siblings[leaf_idx].append({
                    "sibling_hash": left.hash,
                    "position": "left"
                })
            
            # Create parent node
            parent_hash = compute_internal_hash(left.hash, right.hash)
            parent = MerkleNode(parent_hash, left=left, right=right)
            next_level.append(parent)
            
            # Track which leaves are under this parent
            parent_indices = left_indices + right_indices
            next_node_to_leaf_indices[parent_hash] = parent_indices
        
        current_level = next_level
        node_to_leaf_indices = next_node_to_leaf_indices
    
    # Root is the only remaining node
    root = current_level[0]
    
    return MerkleTree(root, leaves, leaf_to_siblings)



def write_proof_to_jsonl(proof: dict, output_path: Union[str, Path]) -> None:
    """
    Write inclusion proof to JSONL file.
    
    Args:
        proof: Proof dictionary from MerkleTree.get_proof()
        output_path: Path to output JSONL file
    """
    output_path = Path(output_path)
    
    # Append to JSONL file
    with open(output_path, "a", encoding="utf-8") as f:
        json.dump(proof, f, ensure_ascii=False)
        f.write("\n")


def write_all_proofs(tree: MerkleTree, output_path: Union[str, Path]) -> None:
    """
    Write all inclusion proofs to JSONL file.
    
    Args:
        tree: MerkleTree object
        output_path: Path to output JSONL file
    """
    output_path = Path(output_path)
    
    # Clear file if exists
    if output_path.exists():
        output_path.unlink()
    
    # Write proof for each leaf
    for leaf in tree.leaves:
        if leaf.file_path:
            proof = tree.get_proof(leaf.file_path)
            if proof:
                write_proof_to_jsonl(proof, output_path)
