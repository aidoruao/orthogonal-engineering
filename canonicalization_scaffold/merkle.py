"""
Merkle Tree Module

Builds binary Merkle tree using:
- Leaf nodes: SHA-256(0x00 || canonical_bytes)
- Internal nodes: SHA-256(0x01 || left_hash || right_hash)

Leaves are ordered by canonical path (UTF-8 lexicographic).
Produces root hash and per-leaf inclusion proofs exported as JSONL.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


class MerkleNode:
    """Represents a node in the Merkle tree."""
    
    def __init__(self, hash_value: str, left: Optional['MerkleNode'] = None, 
                 right: Optional['MerkleNode'] = None, file_path: Optional[str] = None):
        """
        Initialize a Merkle node.
        
        Args:
            hash_value: Hash value of this node
            left: Left child node (for internal nodes)
            right: Right child node (for internal nodes)
            file_path: Original file path (for leaf nodes only)
        """
        self.hash = hash_value
        self.left = left
        self.right = right
        self.file_path = file_path
        self.is_leaf = (left is None and right is None)


class MerkleTree:
    """
    Binary Merkle tree for file verification.
    """
    
    def __init__(self):
        """Initialize an empty Merkle tree."""
        self.root: Optional[MerkleNode] = None
        self.leaves: List[MerkleNode] = []
        self.leaf_map: Dict[str, int] = {}  # Maps file path to leaf index
    
    @staticmethod
    def _hash_leaf(canonical_bytes: bytes) -> str:
        """
        Compute leaf node hash: SHA-256(0x00 || canonical_bytes).
        
        Args:
            canonical_bytes: Canonical bytes of file
            
        Returns:
            Hex lowercase hash
        """
        return hashlib.sha256(b'\x00' + canonical_bytes).hexdigest()
    
    @staticmethod
    def _hash_internal(left_hash: str, right_hash: str) -> str:
        """
        Compute internal node hash: SHA-256(0x01 || left || right).
        
        Args:
            left_hash: Hash of left child (hex string)
            right_hash: Hash of right child (hex string)
            
        Returns:
            Hex lowercase hash
        """
        left_bytes = bytes.fromhex(left_hash)
        right_bytes = bytes.fromhex(right_hash)
        return hashlib.sha256(b'\x01' + left_bytes + right_bytes).hexdigest()
    
    def _build_tree_level(self, nodes: List[MerkleNode]) -> List[MerkleNode]:
        """
        Build one level of the tree from a list of nodes.
        
        Args:
            nodes: List of nodes at current level
            
        Returns:
            List of parent nodes
        """
        if len(nodes) == 0:
            return []
        
        if len(nodes) == 1:
            return nodes
        
        parent_nodes = []
        
        # Process pairs of nodes
        for i in range(0, len(nodes), 2):
            left = nodes[i]
            
            # If odd number of nodes, duplicate the last one
            if i + 1 < len(nodes):
                right = nodes[i + 1]
            else:
                right = left
            
            # Create parent node
            parent_hash = self._hash_internal(left.hash, right.hash)
            parent = MerkleNode(parent_hash, left, right)
            parent_nodes.append(parent)
        
        return parent_nodes
    
    def build_from_files(self, file_hashes: Dict[str, bytes]) -> str:
        """
        Build Merkle tree from file canonical bytes.
        
        Args:
            file_hashes: Dict mapping file paths to canonical bytes
            
        Returns:
            Root hash (hex lowercase)
        """
        if not file_hashes:
            # Empty tree has a special root hash
            return hashlib.sha256(b'').hexdigest()
        
        # Sort files by canonical path (UTF-8 lexicographic)
        sorted_files = sorted(file_hashes.items(), key=lambda x: x[0])
        
        # Create leaf nodes
        self.leaves = []
        self.leaf_map = {}
        
        for idx, (file_path, canonical_bytes) in enumerate(sorted_files):
            leaf_hash = self._hash_leaf(canonical_bytes)
            leaf = MerkleNode(leaf_hash, file_path=file_path)
            self.leaves.append(leaf)
            self.leaf_map[file_path] = idx
        
        # Build tree bottom-up
        current_level = self.leaves[:]
        
        while len(current_level) > 1:
            current_level = self._build_tree_level(current_level)
        
        self.root = current_level[0] if current_level else None
        
        return self.root.hash if self.root else hashlib.sha256(b'').hexdigest()
    
    def get_inclusion_proof(self, file_path: str) -> Optional[List[Tuple[str, str]]]:
        """
        Get inclusion proof for a file.
        
        The proof is a list of (position, hash) tuples where position is 'left' or 'right'.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of proof elements [(position, hash), ...] or None if file not in tree
        """
        if file_path not in self.leaf_map:
            return None
        
        leaf_idx = self.leaf_map[file_path]
        proof = []
        
        # Reconstruct proof by traversing up from leaf to root
        current_level = self.leaves[:]
        current_idx = leaf_idx
        
        while len(current_level) > 1:
            # Determine sibling
            if current_idx % 2 == 0:
                # We are left child
                if current_idx + 1 < len(current_level):
                    sibling_hash = current_level[current_idx + 1].hash
                    proof.append(('right', sibling_hash))
                else:
                    # Odd number, duplicate ourselves
                    sibling_hash = current_level[current_idx].hash
                    proof.append(('right', sibling_hash))
            else:
                # We are right child
                sibling_hash = current_level[current_idx - 1].hash
                proof.append(('left', sibling_hash))
            
            # Move to parent level
            current_level = self._build_tree_level(current_level)
            current_idx = current_idx // 2
        
        return proof
    
    def verify_inclusion_proof(self, file_path: str, canonical_bytes: bytes, 
                               proof: List[Tuple[str, str]], root_hash: str) -> bool:
        """
        Verify an inclusion proof.
        
        Args:
            file_path: Path to file
            canonical_bytes: Canonical bytes of file
            proof: Inclusion proof [(position, hash), ...]
            root_hash: Expected root hash
            
        Returns:
            True if proof is valid, False otherwise
        """
        # Compute leaf hash
        current_hash = self._hash_leaf(canonical_bytes)
        
        # Apply proof elements
        for position, sibling_hash in proof:
            if position == 'left':
                current_hash = self._hash_internal(sibling_hash, current_hash)
            else:  # right
                current_hash = self._hash_internal(current_hash, sibling_hash)
        
        # Compare with root hash
        return current_hash == root_hash
    
    def export_proofs_jsonl(self, output_path: Union[str, Path]) -> None:
        """
        Export all inclusion proofs to JSONL file.
        
        Each line contains:
        {
            "file_path": "path/to/file",
            "leaf_hash": "...",
            "proof": [["left|right", "hash"], ...],
            "root_hash": "..."
        }
        
        Args:
            output_path: Path to output JSONL file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for file_path in sorted(self.leaf_map.keys()):
                leaf_idx = self.leaf_map[file_path]
                leaf_hash = self.leaves[leaf_idx].hash
                proof = self.get_inclusion_proof(file_path)
                
                record = {
                    "file_path": file_path,
                    "leaf_hash": leaf_hash,
                    "proof": proof if proof else [],
                    "root_hash": self.root.hash if self.root else ""
                }
                
                f.write(json.dumps(record, ensure_ascii=False) + '\n')


def build_merkle_tree(file_hashes: Dict[str, bytes]) -> Tuple[str, MerkleTree]:
    """
    Build a Merkle tree from file canonical bytes.
    
    Args:
        file_hashes: Dict mapping file paths to canonical bytes
        
    Returns:
        Tuple of (root_hash, MerkleTree instance)
    """
    tree = MerkleTree()
    root_hash = tree.build_from_files(file_hashes)
    return root_hash, tree
