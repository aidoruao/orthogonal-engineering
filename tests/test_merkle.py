"""
Unit tests for merkle module.
"""

import tempfile
from pathlib import Path
import pytest
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from toolkit.oe.merkle import (
    MerkleTree,
    build_merkle_tree_from_files,
    verify_inclusion_proof,
)


def test_empty_tree():
    """Test empty Merkle tree."""
    tree = MerkleTree()
    root = tree.build()
    # Empty tree should have a specific root
    assert len(root) == 64  # SHA-256 hex length


def test_single_leaf():
    """Test tree with single leaf."""
    tree = MerkleTree()
    tree.add_leaf('file1.txt', 'a' * 64)  # Dummy hash
    root = tree.build()
    
    assert len(root) == 64
    assert tree.root == root


def test_two_leaves():
    """Test tree with two leaves."""
    tree = MerkleTree()
    tree.add_leaf('file1.txt', 'a' * 64)
    tree.add_leaf('file2.txt', 'b' * 64)
    root = tree.build()
    
    assert len(root) == 64
    assert len(tree.tree_levels) == 2  # Leaf level + root level


def test_leaves_sorted_by_path():
    """Test that leaves are sorted lexicographically."""
    tree = MerkleTree()
    tree.add_leaf('z.txt', 'a' * 64)
    tree.add_leaf('a.txt', 'b' * 64)
    tree.add_leaf('m.txt', 'c' * 64)
    tree.build()
    
    # Check that leaves are sorted
    paths = [path for path, _ in tree.leaves]
    assert paths == ['a.txt', 'm.txt', 'z.txt']


def test_inclusion_proof():
    """Test inclusion proof generation."""
    tree = MerkleTree()
    tree.add_leaf('file1.txt', 'a' * 64)
    tree.add_leaf('file2.txt', 'b' * 64)
    tree.build()
    
    proof = tree.get_inclusion_proof('file1.txt')
    
    assert proof['path'] == 'file1.txt'
    assert proof['leaf_hash'] == 'a' * 64
    assert proof['root'] == tree.root
    assert 'proof' in proof


def test_inclusion_proof_not_found():
    """Test inclusion proof for non-existent file."""
    tree = MerkleTree()
    tree.add_leaf('file1.txt', 'a' * 64)
    tree.build()
    
    with pytest.raises(ValueError, match="Path not found"):
        tree.get_inclusion_proof('nonexistent.txt')


def test_verify_inclusion_proof_valid():
    """Test verification of valid inclusion proof."""
    tree = MerkleTree()
    tree.add_leaf('file1.txt', 'a' * 64)
    tree.add_leaf('file2.txt', 'b' * 64)
    tree.build()
    
    proof = tree.get_inclusion_proof('file1.txt')
    assert verify_inclusion_proof(proof) is True


def test_verify_inclusion_proof_invalid():
    """Test verification of invalid inclusion proof."""
    tree = MerkleTree()
    tree.add_leaf('file1.txt', 'a' * 64)
    tree.add_leaf('file2.txt', 'b' * 64)
    tree.build()
    
    proof = tree.get_inclusion_proof('file1.txt')
    # Tamper with the proof
    proof['leaf_hash'] = 'c' * 64
    
    assert verify_inclusion_proof(proof) is False


def test_export_proofs_jsonl():
    """Test exporting proofs to JSONL."""
    tree = MerkleTree()
    tree.add_leaf('file1.txt', 'a' * 64)
    tree.add_leaf('file2.txt', 'b' * 64)
    tree.build()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        temp_path = Path(f.name)
    
    try:
        tree.export_proofs_jsonl(temp_path)
        
        # Read and verify
        import json
        with open(temp_path, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 2  # Two proofs
        
        # Parse each line
        for line in lines:
            proof = json.loads(line)
            assert 'path' in proof
            assert 'leaf_hash' in proof
            assert 'proof' in proof
            assert 'root' in proof
    finally:
        temp_path.unlink()


def test_build_merkle_tree_from_files():
    """Test building tree from file list."""
    file_hashes = [
        ('dir/file1.txt', 'a' * 64),
        ('dir/file2.txt', 'b' * 64),
        ('file3.txt', 'c' * 64),
    ]
    
    tree = build_merkle_tree_from_files(file_hashes)
    
    assert tree.root
    assert len(tree.leaves) == 3


def test_deterministic_root():
    """Test that tree root is deterministic."""
    file_hashes = [
        ('file1.txt', 'a' * 64),
        ('file2.txt', 'b' * 64),
    ]
    
    tree1 = build_merkle_tree_from_files(file_hashes)
    tree2 = build_merkle_tree_from_files(file_hashes)
    
    assert tree1.root == tree2.root


def test_odd_number_of_nodes():
    """Test tree with odd number of leaves."""
    tree = MerkleTree()
    tree.add_leaf('file1.txt', 'a' * 64)
    tree.add_leaf('file2.txt', 'b' * 64)
    tree.add_leaf('file3.txt', 'c' * 64)
    root = tree.build()
    
    assert len(root) == 64
    # Should handle odd number correctly


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
