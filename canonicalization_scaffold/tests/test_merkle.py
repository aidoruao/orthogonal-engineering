"""
Unit tests for merkle module
"""

import unittest
from canonicalization_scaffold.merkle import (
    MerkleNode,
    MerkleTree,
    build_merkle_tree,
)


class TestMerkleNode(unittest.TestCase):
    """Test cases for MerkleNode class."""
    
    def test_create_leaf_node(self):
        """Test creating a leaf node."""
        node = MerkleNode("abc123", file_path="test.txt")
        
        self.assertEqual(node.hash, "abc123")
        self.assertEqual(node.file_path, "test.txt")
        self.assertTrue(node.is_leaf)
        self.assertIsNone(node.left)
        self.assertIsNone(node.right)
    
    def test_create_internal_node(self):
        """Test creating an internal node."""
        left = MerkleNode("aaa", file_path="left.txt")
        right = MerkleNode("bbb", file_path="right.txt")
        parent = MerkleNode("ccc", left=left, right=right)
        
        self.assertEqual(parent.hash, "ccc")
        self.assertFalse(parent.is_leaf)
        self.assertEqual(parent.left, left)
        self.assertEqual(parent.right, right)
        self.assertIsNone(parent.file_path)


class TestMerkleTree(unittest.TestCase):
    """Test cases for MerkleTree class."""
    
    def test_hash_leaf(self):
        """Test leaf hash computation."""
        data = b"Hello, World!"
        result = MerkleTree._hash_leaf(data)
        
        # Should be SHA-256(0x00 || data)
        import hashlib
        expected = hashlib.sha256(b'\x00' + data).hexdigest()
        self.assertEqual(result, expected)
    
    def test_hash_internal(self):
        """Test internal node hash computation."""
        left_hash = "a" * 64
        right_hash = "b" * 64
        
        result = MerkleTree._hash_internal(left_hash, right_hash)
        
        # Should be SHA-256(0x01 || left_bytes || right_bytes)
        import hashlib
        left_bytes = bytes.fromhex(left_hash)
        right_bytes = bytes.fromhex(right_hash)
        expected = hashlib.sha256(b'\x01' + left_bytes + right_bytes).hexdigest()
        self.assertEqual(result, expected)
    
    def test_build_tree_single_file(self):
        """Test building tree with single file."""
        tree = MerkleTree()
        file_hashes = {"file1.txt": b"content1"}
        
        root_hash = tree.build_from_files(file_hashes)
        
        # Root should be the leaf hash
        expected = tree._hash_leaf(b"content1")
        self.assertEqual(root_hash, expected)
        self.assertEqual(len(tree.leaves), 1)
    
    def test_build_tree_two_files(self):
        """Test building tree with two files."""
        tree = MerkleTree()
        file_hashes = {
            "file1.txt": b"content1",
            "file2.txt": b"content2"
        }
        
        root_hash = tree.build_from_files(file_hashes)
        
        # Should combine two leaves
        self.assertEqual(len(tree.leaves), 2)
        self.assertIsNotNone(root_hash)
        self.assertEqual(len(root_hash), 64)  # SHA-256
    
    def test_build_tree_three_files(self):
        """Test building tree with three files (odd number)."""
        tree = MerkleTree()
        file_hashes = {
            "file1.txt": b"content1",
            "file2.txt": b"content2",
            "file3.txt": b"content3"
        }
        
        root_hash = tree.build_from_files(file_hashes)
        
        # Should handle odd number by duplicating last
        self.assertEqual(len(tree.leaves), 3)
        self.assertIsNotNone(root_hash)
    
    def test_build_tree_sorted_order(self):
        """Test that files are sorted by path."""
        tree = MerkleTree()
        file_hashes = {
            "zzz.txt": b"last",
            "aaa.txt": b"first",
            "mmm.txt": b"middle"
        }
        
        tree.build_from_files(file_hashes)
        
        # Leaves should be sorted by path
        self.assertEqual(tree.leaves[0].file_path, "aaa.txt")
        self.assertEqual(tree.leaves[1].file_path, "mmm.txt")
        self.assertEqual(tree.leaves[2].file_path, "zzz.txt")
    
    def test_build_tree_empty(self):
        """Test building tree with no files."""
        tree = MerkleTree()
        file_hashes = {}
        
        root_hash = tree.build_from_files(file_hashes)
        
        # Empty tree should have special hash
        import hashlib
        expected = hashlib.sha256(b'').hexdigest()
        self.assertEqual(root_hash, expected)
    
    def test_get_inclusion_proof(self):
        """Test getting inclusion proof for a file."""
        tree = MerkleTree()
        file_hashes = {
            "file1.txt": b"content1",
            "file2.txt": b"content2"
        }
        
        tree.build_from_files(file_hashes)
        proof = tree.get_inclusion_proof("file1.txt")
        
        # Should have proof elements
        self.assertIsNotNone(proof)
        self.assertIsInstance(proof, list)
        
        # For 2 files, should have 1 proof element (sibling)
        self.assertEqual(len(proof), 1)
    
    def test_get_inclusion_proof_nonexistent(self):
        """Test getting proof for non-existent file."""
        tree = MerkleTree()
        file_hashes = {"file1.txt": b"content1"}
        
        tree.build_from_files(file_hashes)
        proof = tree.get_inclusion_proof("nonexistent.txt")
        
        self.assertIsNone(proof)
    
    def test_verify_inclusion_proof(self):
        """Test verifying an inclusion proof."""
        tree = MerkleTree()
        file_hashes = {
            "file1.txt": b"content1",
            "file2.txt": b"content2"
        }
        
        root_hash = tree.build_from_files(file_hashes)
        proof = tree.get_inclusion_proof("file1.txt")
        
        # Verify proof
        is_valid = tree.verify_inclusion_proof(
            "file1.txt",
            b"content1",
            proof,
            root_hash
        )
        
        self.assertTrue(is_valid)
    
    def test_verify_inclusion_proof_invalid(self):
        """Test verifying an invalid proof."""
        tree = MerkleTree()
        file_hashes = {
            "file1.txt": b"content1",
            "file2.txt": b"content2"
        }
        
        root_hash = tree.build_from_files(file_hashes)
        proof = tree.get_inclusion_proof("file1.txt")
        
        # Verify with wrong content
        is_valid = tree.verify_inclusion_proof(
            "file1.txt",
            b"wrong_content",
            proof,
            root_hash
        )
        
        self.assertFalse(is_valid)
    
    def test_verify_inclusion_proof_wrong_root(self):
        """Test verifying proof with wrong root."""
        tree = MerkleTree()
        file_hashes = {
            "file1.txt": b"content1",
            "file2.txt": b"content2"
        }
        
        tree.build_from_files(file_hashes)
        proof = tree.get_inclusion_proof("file1.txt")
        
        # Verify with wrong root
        wrong_root = "0" * 64
        is_valid = tree.verify_inclusion_proof(
            "file1.txt",
            b"content1",
            proof,
            wrong_root
        )
        
        self.assertFalse(is_valid)
    
    def test_export_proofs_jsonl(self):
        """Test exporting proofs to JSONL."""
        import tempfile
        import json
        from pathlib import Path
        
        temp_dir = tempfile.mkdtemp()
        try:
            tree = MerkleTree()
            file_hashes = {
                "file1.txt": b"content1",
                "file2.txt": b"content2"
            }
            
            tree.build_from_files(file_hashes)
            
            output_path = Path(temp_dir) / "proofs.jsonl"
            tree.export_proofs_jsonl(output_path)
            
            # Read and verify
            self.assertTrue(output_path.exists())
            
            with open(output_path, 'r') as f:
                lines = f.readlines()
            
            # Should have 2 lines (one per file)
            self.assertEqual(len(lines), 2)
            
            # Parse first line
            record = json.loads(lines[0])
            self.assertIn("file_path", record)
            self.assertIn("leaf_hash", record)
            self.assertIn("proof", record)
            self.assertIn("root_hash", record)
            
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_build_merkle_tree_convenience(self):
        """Test convenience function for building tree."""
        file_hashes = {
            "file1.txt": b"content1",
            "file2.txt": b"content2"
        }
        
        root_hash, tree = build_merkle_tree(file_hashes)
        
        self.assertIsNotNone(root_hash)
        self.assertIsInstance(tree, MerkleTree)
        self.assertEqual(len(tree.leaves), 2)


class TestMerkleTreeLarge(unittest.TestCase):
    """Test Merkle tree with larger datasets."""
    
    def test_build_tree_many_files(self):
        """Test building tree with many files."""
        tree = MerkleTree()
        
        # Create 100 files
        file_hashes = {
            f"file_{i:03d}.txt": f"content_{i}".encode()
            for i in range(100)
        }
        
        root_hash = tree.build_from_files(file_hashes)
        
        self.assertEqual(len(tree.leaves), 100)
        self.assertIsNotNone(root_hash)
        
        # Verify a proof
        proof = tree.get_inclusion_proof("file_050.txt")
        is_valid = tree.verify_inclusion_proof(
            "file_050.txt",
            b"content_50",
            proof,
            root_hash
        )
        self.assertTrue(is_valid)


if __name__ == '__main__':
    unittest.main()
