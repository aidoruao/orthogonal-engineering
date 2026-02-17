"""
Binary Merkle tree implementation for deterministic verification.

Tree structure:
- Leaf nodes: SHA-256(0x00 || canonical_bytes)
- Internal nodes: SHA-256(0x01 || left_hash || right_hash)
- Leaves ordered by canonical path (UTF-8 lexicographic)

Produces:
- Root hash
- Inclusion proofs exported as JSONL
"""

import hashlib
import json
from pathlib import Path
from typing import List, Tuple, Optional, Union
from dataclasses import dataclass

from .canonicalizer import canonical_byte_representation
from .hasher import hash_bytes


@dataclass
class MerkleProof:
    """
    Inclusion proof for a file in the Merkle tree.
    """
    file_path: str
    leaf_hash: str
    root_hash: str
    proof: List[Tuple[str, str]]  # List of (position, hash) where position is 'left' or 'right'
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'file_path': self.file_path,
            'leaf_hash': self.leaf_hash,
            'root_hash': self.root_hash,
            'proof': [{'position': pos, 'hash': h} for pos, h in self.proof]
        }


class MerkleTree:
    """
    Binary Merkle tree for file verification.
    
    Features:
    - Deterministic ordering by canonical path
    - SHA-256 based hashing
    - Inclusion proof generation
    - JSONL export
    """
    
    LEAF_PREFIX = b'\x00'
    INTERNAL_PREFIX = b'\x01'
    
    def __init__(self):
        """Initialize empty Merkle tree."""
        self.leaves = []  # List of (path, leaf_hash)
        self.root = None
        self.tree_levels = []  # List of levels for proof generation
    
    def add_file(self, file_path: Union[str, Path], canonical_path: Optional[str] = None) -> str:
        """
        Add a file to the tree.
        
        Args:
            file_path: Path to file
            canonical_path: Optional canonical path for sorting (defaults to str(file_path))
            
        Returns:
            Leaf hash
        """
        path = Path(file_path)
        if canonical_path is None:
            canonical_path = str(path)
        
        # Get canonical bytes
        canonical_bytes = canonical_byte_representation(path)
        
        # Compute leaf hash: SHA-256(0x00 || canonical_bytes)
        leaf_hash = hashlib.sha256(self.LEAF_PREFIX + canonical_bytes).hexdigest()
        
        self.leaves.append((canonical_path, leaf_hash))
        return leaf_hash
    
    def build(self) -> str:
        """
        Build the Merkle tree and return root hash.
        
        Returns:
            Root hash
        """
        if not self.leaves:
            # Empty tree - hash of empty bytes
            self.root = hash_bytes(b'')
            return self.root
        
        # Sort leaves by canonical path (UTF-8 lexicographic)
        self.leaves.sort(key=lambda x: x[0])
        
        # Initialize bottom level with leaf hashes
        current_level = [leaf_hash for _, leaf_hash in self.leaves]
        self.tree_levels = [current_level[:]]
        
        # Build tree bottom-up
        while len(current_level) > 1:
            next_level = []
            
            # Process pairs
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                
                if i + 1 < len(current_level):
                    right = current_level[i + 1]
                else:
                    # Odd number of nodes - duplicate last one
                    right = left
                
                # Internal node: SHA-256(0x01 || left || right)
                combined = self.INTERNAL_PREFIX + bytes.fromhex(left) + bytes.fromhex(right)
                parent_hash = hashlib.sha256(combined).hexdigest()
                next_level.append(parent_hash)
            
            current_level = next_level
            self.tree_levels.append(current_level[:])
        
        self.root = current_level[0]
        return self.root
    
    def get_proof(self, file_path: str) -> Optional[MerkleProof]:
        """
        Get inclusion proof for a file.
        
        Args:
            file_path: Canonical path of file
            
        Returns:
            MerkleProof or None if file not in tree
        """
        if self.root is None:
            raise RuntimeError("Tree not built yet - call build() first")
        
        # Find leaf index
        leaf_index = None
        leaf_hash = None
        for i, (path, lh) in enumerate(self.leaves):
            if path == file_path:
                leaf_index = i
                leaf_hash = lh
                break
        
        if leaf_index is None:
            return None
        
        # Build proof by traversing up the tree
        proof = []
        current_index = leaf_index
        
        for level in self.tree_levels[:-1]:  # Exclude root level
            # Determine sibling
            if current_index % 2 == 0:
                # Current is left child
                sibling_index = current_index + 1
                position = 'right'
            else:
                # Current is right child
                sibling_index = current_index - 1
                position = 'left'
            
            # Get sibling hash (or duplicate if odd)
            if sibling_index < len(level):
                sibling_hash = level[sibling_index]
            else:
                sibling_hash = level[current_index]
            
            proof.append((position, sibling_hash))
            
            # Move to parent level
            current_index = current_index // 2
        
        return MerkleProof(
            file_path=file_path,
            leaf_hash=leaf_hash,
            root_hash=self.root,
            proof=proof
        )
    
    def export_proofs(self, output_path: Union[str, Path]) -> None:
        """
        Export all inclusion proofs as JSONL.
        
        Args:
            output_path: Path to output JSONL file
        """
        output_path = Path(output_path)
        
        with open(output_path, 'w') as f:
            for file_path, _ in self.leaves:
                proof = self.get_proof(file_path)
                if proof:
                    f.write(json.dumps(proof.to_dict()) + '\n')
    
    def verify_proof(self, proof: MerkleProof) -> bool:
        """
        Verify an inclusion proof.
        
        Args:
            proof: MerkleProof to verify
            
        Returns:
            True if proof is valid
        """
        current_hash = proof.leaf_hash
        
        for position, sibling_hash in proof.proof:
            if position == 'left':
                combined = self.INTERNAL_PREFIX + bytes.fromhex(sibling_hash) + bytes.fromhex(current_hash)
            else:
                combined = self.INTERNAL_PREFIX + bytes.fromhex(current_hash) + bytes.fromhex(sibling_hash)
            
            current_hash = hashlib.sha256(combined).hexdigest()
        
        return current_hash == proof.root_hash


# Unit tests and examples
def _test_merkle_tree():
    """Test Merkle tree construction."""
    import tempfile
    
    # Create temporary files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create test files
        (tmpdir / "a.txt").write_text("File A")
        (tmpdir / "b.txt").write_text("File B")
        (tmpdir / "c.txt").write_text("File C")
        
        # Build tree
        tree = MerkleTree()
        tree.add_file(tmpdir / "a.txt", "a.txt")
        tree.add_file(tmpdir / "b.txt", "b.txt")
        tree.add_file(tmpdir / "c.txt", "c.txt")
        
        root = tree.build()
        assert root is not None
        assert len(root) == 64  # SHA-256 hex length
        
        # Get and verify proof
        proof = tree.get_proof("b.txt")
        assert proof is not None
        assert tree.verify_proof(proof)
        
        print("✓ Merkle tree tests passed")


if __name__ == "__main__":
    _test_merkle_tree()
    print("\n✓ All merkle tests passed")
