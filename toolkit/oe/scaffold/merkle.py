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
        # TODO: Expand is_leaf() - stub detected by Yeshua Agent
        return self.left is None and self.right is None


class MerkleTree:
    """Binary Merkle tree for file integrity verification."""
    
    def __init__(self, root: MerkleNode, leaves: List[MerkleNode]):
        self.root = root
        self.leaves = leaves
    
    def get_root_hash(self) -> str:
        """Get the root hash of the tree."""
        return self.root.hash
    
    def get_proof(self, file_path: str) -> Optional[dict]:
        """
        Generate inclusion proof for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Proof dictionary or None if file not in tree
        """
        # Find the leaf for this file
        leaf_index = None
        for i, leaf in enumerate(self.leaves):
            if leaf.file_path == file_path:
                leaf_index = i
                break
        
        if leaf_index is None:
            return None
        
        # Build proof by traversing tree
        proof = {
            "file_path": file_path,
            "leaf_hash": self.leaves[leaf_index].hash,
            "root_hash": self.root.hash,
            "proof_path": []
        }
        
        # Generate sibling hashes along path to root
        # This is a simplified proof - in production, you'd track siblings
        proof["proof_path"] = self._build_proof_path(leaf_index, len(self.leaves))
        
        return proof
    
    def _build_proof_path(self, leaf_index: int, total_leaves: int) -> List[dict]:
        """
        Build proof path for a leaf.
        
        This is a simplified implementation that documents the structure.
        A full implementation would traverse the actual tree structure.
        """
        proof_path = []
        index = leaf_index
        level_size = total_leaves
        
        while level_size > 1:
            # Determine sibling position
            is_left = index % 2 == 0
            sibling_index = index + 1 if is_left else index - 1
            
            if sibling_index < level_size:
                proof_path.append({
                    "position": "right" if is_left else "left",
                    "sibling_index": sibling_index
                })
            
            # Move to parent level
            index = index // 2
            level_size = (level_size + 1) // 2
        
        return proof_path


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


def build_merkle_tree(file_paths: List[Union[str, Path]]) -> MerkleTree:
    """
    Build binary Merkle tree from list of file paths.
    
    Files are sorted by canonical path (UTF-8 lexicographic order) before
    building the tree to ensure deterministic structure.
    
    Args:
        file_paths: List of file paths to include in tree
        
    Returns:
        MerkleTree object with root and leaves
        
    Raises:
        ValueError: If file_paths is empty
    """
    if not file_paths:
        raise ValueError("Cannot build Merkle tree from empty file list")
    
    # Convert to Path objects and sort by canonical path
    paths = [Path(p) for p in file_paths]
    paths.sort(key=lambda p: str(p.resolve()))
    
    # Build leaf nodes
    leaves = []
    for path in paths:
        canonical_bytes = canonical_byte_representation(path)
        leaf_hash = compute_leaf_hash(canonical_bytes)
        leaf = MerkleNode(leaf_hash, file_path=str(path))
        leaves.append(leaf)
    
    # Build tree bottom-up
    current_level = leaves[:]
    
    while len(current_level) > 1:
        next_level = []
        
        # Pair up nodes and create parents
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            
            if i + 1 < len(current_level):
                right = current_level[i + 1]
            else:
                # Odd number of nodes: duplicate last node
                right = current_level[i]
            
            # Create parent node
            parent_hash = compute_internal_hash(left.hash, right.hash)
            parent = MerkleNode(parent_hash, left=left, right=right)
            next_level.append(parent)
        
        current_level = next_level
    
    # Root is the only remaining node
    root = current_level[0]
    
    return MerkleTree(root, leaves)


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
