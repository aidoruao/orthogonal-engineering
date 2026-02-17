"""
Unit tests for merkle module.
"""

import tempfile
import pytest
from pathlib import Path

from toolkit.oe.scaffold.merkle import MerkleTree, MerkleProof


def test_merkle_tree_empty():
    """Test empty Merkle tree."""
    tree = MerkleTree()
    root = tree.build()
    
    # Empty tree should have hash of empty bytes
    assert root is not None
    assert len(root) == 64


def test_merkle_tree_single_file():
    """Test Merkle tree with single file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        test_file = tmpdir / "test.txt"
        test_file.write_text("Test content")
        
        tree = MerkleTree()
        leaf_hash = tree.add_file(test_file, "test.txt")
        root = tree.build()
        
        # Leaf hash should be SHA-256(0x00 || content)
        assert len(leaf_hash) == 64
        assert root is not None


def test_merkle_tree_multiple_files():
    """Test Merkle tree with multiple files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create test files
        (tmpdir / "a.txt").write_text("File A")
        (tmpdir / "b.txt").write_text("File B")
        (tmpdir / "c.txt").write_text("File C")
        
        tree = MerkleTree()
        tree.add_file(tmpdir / "a.txt", "a.txt")
        tree.add_file(tmpdir / "b.txt", "b.txt")
        tree.add_file(tmpdir / "c.txt", "c.txt")
        
        root = tree.build()
        
        assert root is not None
        assert len(root) == 64
        
        # Tree should have leaves
        assert len(tree.leaves) == 3


def test_merkle_tree_deterministic_ordering():
    """Test that trees with same files but different add order produce same root."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create test files
        (tmpdir / "a.txt").write_text("File A")
        (tmpdir / "b.txt").write_text("File B")
        (tmpdir / "c.txt").write_text("File C")
        
        # Build tree 1: a, b, c
        tree1 = MerkleTree()
        tree1.add_file(tmpdir / "a.txt", "a.txt")
        tree1.add_file(tmpdir / "b.txt", "b.txt")
        tree1.add_file(tmpdir / "c.txt", "c.txt")
        root1 = tree1.build()
        
        # Build tree 2: c, a, b
        tree2 = MerkleTree()
        tree2.add_file(tmpdir / "c.txt", "c.txt")
        tree2.add_file(tmpdir / "a.txt", "a.txt")
        tree2.add_file(tmpdir / "b.txt", "b.txt")
        root2 = tree2.build()
        
        # Roots should be identical (deterministic ordering)
        assert root1 == root2


def test_merkle_proof_generation():
    """Test generating inclusion proof."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create test files
        (tmpdir / "a.txt").write_text("File A")
        (tmpdir / "b.txt").write_text("File B")
        (tmpdir / "c.txt").write_text("File C")
        
        tree = MerkleTree()
        tree.add_file(tmpdir / "a.txt", "a.txt")
        tree.add_file(tmpdir / "b.txt", "b.txt")
        tree.add_file(tmpdir / "c.txt", "c.txt")
        root = tree.build()
        
        # Get proof for middle file
        proof = tree.get_proof("b.txt")
        
        assert proof is not None
        assert proof.file_path == "b.txt"
        assert proof.root_hash == root
        assert len(proof.proof) > 0


def test_merkle_proof_verification():
    """Test verifying inclusion proof."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create test files
        (tmpdir / "a.txt").write_text("File A")
        (tmpdir / "b.txt").write_text("File B")
        (tmpdir / "c.txt").write_text("File C")
        
        tree = MerkleTree()
        tree.add_file(tmpdir / "a.txt", "a.txt")
        tree.add_file(tmpdir / "b.txt", "b.txt")
        tree.add_file(tmpdir / "c.txt", "c.txt")
        tree.build()
        
        # Get and verify proof
        proof = tree.get_proof("b.txt")
        assert tree.verify_proof(proof) is True


def test_merkle_proof_export():
    """Test exporting proofs to JSONL."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create test files
        (tmpdir / "a.txt").write_text("File A")
        (tmpdir / "b.txt").write_text("File B")
        
        tree = MerkleTree()
        tree.add_file(tmpdir / "a.txt", "a.txt")
        tree.add_file(tmpdir / "b.txt", "b.txt")
        tree.build()
        
        # Export proofs
        proofs_path = tmpdir / "proofs.jsonl"
        tree.export_proofs(proofs_path)
        
        assert proofs_path.exists()
        
        # Read and verify
        import json
        with open(proofs_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 2
            
            for line in lines:
                proof_data = json.loads(line)
                assert 'file_path' in proof_data
                assert 'leaf_hash' in proof_data
                assert 'root_hash' in proof_data
                assert 'proof' in proof_data


def test_merkle_get_proof_not_found():
    """Test getting proof for non-existent file."""
    tree = MerkleTree()
    tree.build()
    
    proof = tree.get_proof("nonexistent.txt")
    assert proof is None


def test_merkle_get_proof_before_build():
    """Test getting proof before building tree."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        test_file = tmpdir / "test.txt"
        test_file.write_text("Test")
        
        tree = MerkleTree()
        tree.add_file(test_file, "test.txt")
        
        # Should raise error if tree not built
        with pytest.raises(RuntimeError):
            tree.get_proof("test.txt")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
