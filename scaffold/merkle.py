"""
Merkle Tree Module

Builds binary Merkle tree with the following specification:
- Leaf node: SHA-256(0x00 || canonical_bytes)
- Internal node: SHA-256(0x01 || left_hash || right_hash)
- Leaves ordered by canonical path (UTF-8 lexicographic)
- Produces root hash and per-leaf inclusion proofs exported as JSONL
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from .canonicalizer import canonical_byte_representation
from .hasher import compute_hash


class MerkleNode:
    """Represents a node in the Merkle tree."""
    
    def __init__(self, hash_value: str, is_leaf: bool = False, 
                 file_path: Optional[str] = None):
        """
        Initialize Merkle node.
        
        Args:
            hash_value: Hash value of the node
            is_leaf: Whether this is a leaf node
            file_path: File path (for leaf nodes only)
        """
        self.hash = hash_value
        self.is_leaf = is_leaf
        self.file_path = file_path
        self.left: Optional[MerkleNode] = None
        self.right: Optional[MerkleNode] = None


class InclusionProof:
    """Represents a Merkle inclusion proof for a leaf."""
    
    def __init__(self, leaf_path: str, leaf_hash: str, root_hash: str):
        """
        Initialize inclusion proof.
        
        Args:
            leaf_path: Path to the leaf file
            leaf_hash: Hash of the leaf
            root_hash: Root hash of the tree
        """
        self.leaf_path = leaf_path
        self.leaf_hash = leaf_hash
        self.root_hash = root_hash
        self.siblings: List[Tuple[str, str]] = []  # (hash, position: 'left' or 'right')
    
    def add_sibling(self, sibling_hash: str, position: str):
        """
        Add a sibling node to the proof path.
        
        Args:
            sibling_hash: Hash of the sibling node
            position: Position of sibling ('left' or 'right')
        """
        self.siblings.append((sibling_hash, position))
    
    def to_dict(self) -> dict:
        """Convert proof to dictionary format."""
        return {
            "leaf_path": self.leaf_path,
            "leaf_hash": self.leaf_hash,
            "root_hash": self.root_hash,
            "proof_path": [
                {"sibling_hash": h, "position": p} 
                for h, p in self.siblings
            ]
        }
    
    def verify(self) -> bool:
        """
        Verify the inclusion proof.
        
        Returns:
            True if proof is valid, False otherwise
        """
        current_hash = self.leaf_hash
        
        for sibling_hash, position in self.siblings:
            if position == 'left':
                # Sibling is on the left
                combined = bytes.fromhex(sibling_hash) + bytes.fromhex(current_hash)
            else:
                # Sibling is on the right
                combined = bytes.fromhex(current_hash) + bytes.fromhex(sibling_hash)
            
            # Internal node: SHA-256(0x01 || left || right)
            current_hash = hashlib.sha256(b'\x01' + combined).hexdigest()
        
        return current_hash == self.root_hash


class MerkleTree:
    """
    Binary Merkle tree implementation.
    
    Spec:
    - Leaf: SHA-256(0x00 || canonical_bytes)
    - Internal: SHA-256(0x01 || left || right)
    - Leaves ordered by canonical path (UTF-8 lexicographic)
    """
    
    def __init__(self):
        """Initialize Merkle tree."""
        self.root: Optional[MerkleNode] = None
        self.leaves: List[MerkleNode] = []
        self.file_to_leaf: Dict[str, MerkleNode] = {}
    
    def _compute_leaf_hash(self, canonical_bytes: bytes) -> str:
        """
        Compute hash for a leaf node.
        
        Args:
            canonical_bytes: Canonical byte representation
            
        Returns:
            Leaf hash (hex lowercase)
        """
        # Leaf: SHA-256(0x00 || canonical_bytes)
        return hashlib.sha256(b'\x00' + canonical_bytes).hexdigest()
    
    def _compute_internal_hash(self, left_hash: str, right_hash: str) -> str:
        """
        Compute hash for an internal node.
        
        Args:
            left_hash: Hash of left child
            right_hash: Hash of right child
            
        Returns:
            Internal node hash (hex lowercase)
        """
        # Internal: SHA-256(0x01 || left || right)
        left_bytes = bytes.fromhex(left_hash)
        right_bytes = bytes.fromhex(right_hash)
        return hashlib.sha256(b'\x01' + left_bytes + right_bytes).hexdigest()
    
    def add_file(self, file_path: Union[str, Path]):
        """
        Add a file to the tree.
        
        Args:
            file_path: Path to the file
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get canonical bytes
        canonical_bytes = canonical_byte_representation(path)
        
        # Compute leaf hash
        leaf_hash = self._compute_leaf_hash(canonical_bytes)
        
        # Create leaf node
        leaf = MerkleNode(leaf_hash, is_leaf=True, file_path=str(path))
        self.leaves.append(leaf)
        self.file_to_leaf[str(path)] = leaf
    
    def build(self):
        """
        Build the Merkle tree from added files.
        
        Leaves are ordered by canonical path (UTF-8 lexicographic).
        """
        if not self.leaves:
            raise ValueError("No files added to tree")
        
        # Sort leaves by file path (UTF-8 lexicographic)
        self.leaves.sort(key=lambda leaf: leaf.file_path.encode('utf-8'))
        
        # Build tree bottom-up
        current_level = self.leaves.copy()
        
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
                
                # Create internal node
                internal_hash = self._compute_internal_hash(left.hash, right.hash)
                internal = MerkleNode(internal_hash, is_leaf=False)
                internal.left = left
                internal.right = right
                
                next_level.append(internal)
            
            current_level = next_level
        
        # Root is the last remaining node
        self.root = current_level[0]
    
    def get_root_hash(self) -> Optional[str]:
        """
        Get the root hash of the tree.
        
        Returns:
            Root hash or None if tree not built
        """
        return self.root.hash if self.root else None
    
    def get_inclusion_proof(self, file_path: Union[str, Path]) -> Optional[InclusionProof]:
        """
        Get inclusion proof for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            InclusionProof or None if file not in tree
        """
        path_str = str(Path(file_path))
        
        if path_str not in self.file_to_leaf:
            return None
        
        if not self.root:
            raise ValueError("Tree not built. Call build() first.")
        
        leaf = self.file_to_leaf[path_str]
        proof = InclusionProof(path_str, leaf.hash, self.root.hash)
        
        # Traverse tree to build proof path
        self._build_proof_path(self.root, leaf, proof)
        
        return proof
    
    def _build_proof_path(self, node: MerkleNode, target_leaf: MerkleNode, 
                         proof: InclusionProof, current_path: Optional[List] = None):
        """
        Recursively build proof path.
        
        Args:
            node: Current node
            target_leaf: Target leaf node
            proof: Proof object to populate
            current_path: Current path in tree
        """
        if current_path is None:
            current_path = []
        
        if node.is_leaf:
            # Found the leaf
            return node == target_leaf
        
        # Check left subtree
        if node.left and self._build_proof_path(node.left, target_leaf, proof, current_path):
            # Target is in left subtree, add right sibling
            if node.right:
                proof.add_sibling(node.right.hash, 'right')
            return True
        
        # Check right subtree
        if node.right and self._build_proof_path(node.right, target_leaf, proof, current_path):
            # Target is in right subtree, add left sibling
            if node.left:
                proof.add_sibling(node.left.hash, 'left')
            return True
        
        return False
    
    def export_proofs_jsonl(self, output_path: Union[str, Path]):
        """
        Export inclusion proofs for all leaves as JSONL.
        
        Args:
            output_path: Path to output JSONL file
        """
        if not self.root:
            raise ValueError("Tree not built. Call build() first.")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for leaf in self.leaves:
                proof = self.get_inclusion_proof(leaf.file_path)
                if proof:
                    f.write(json.dumps(proof.to_dict(), ensure_ascii=False) + '\n')
    
    def verify_tree(self) -> bool:
        """
        Verify all inclusion proofs in the tree.
        
        Returns:
            True if all proofs are valid
        """
        if not self.root:
            return False
        
        for leaf in self.leaves:
            proof = self.get_inclusion_proof(leaf.file_path)
            if not proof or not proof.verify():
                return False
        
        return True
