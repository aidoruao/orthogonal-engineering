"""
Unit tests for merkle module.

Tests binary Merkle tree construction and inclusion proofs.
"""

import tempfile
import unittest
from pathlib import Path

from scaffold.merkle import InclusionProof, MerkleTree


class TestMerkleTree(unittest.TestCase):
    """Test cases for Merkle tree module."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create test files
        self.file1 = self.test_path / "file1.txt"
        self.file1.write_text("Content of file 1")
        
        self.file2 = self.test_path / "file2.txt"
        self.file2.write_text("Content of file 2")
        
        self.file3 = self.test_path / "file3.txt"
        self.file3.write_text("Content of file 3")
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_add_file(self):
        """Test adding files to tree."""
        tree = MerkleTree()
        tree.add_file(self.file1)
        
        self.assertEqual(len(tree.leaves), 1)
        self.assertIn(str(self.file1), tree.file_to_leaf)
    
    def test_build_tree_single_file(self):
        """Test building tree with single file."""
        tree = MerkleTree()
        tree.add_file(self.file1)
        tree.build()
        
        root_hash = tree.get_root_hash()
        self.assertIsNotNone(root_hash)
        self.assertEqual(len(root_hash), 64)  # SHA-256 hex length
    
    def test_build_tree_multiple_files(self):
        """Test building tree with multiple files."""
        tree = MerkleTree()
        tree.add_file(self.file1)
        tree.add_file(self.file2)
        tree.add_file(self.file3)
        tree.build()
        
        root_hash = tree.get_root_hash()
        self.assertIsNotNone(root_hash)
        
        # Verify all leaves are in tree
        self.assertEqual(len(tree.leaves), 3)
    
    def test_leaf_ordering(self):
        """Test that leaves are ordered by canonical path."""
        tree = MerkleTree()
        
        # Add files in non-alphabetical order
        tree.add_file(self.file3)
        tree.add_file(self.file1)
        tree.add_file(self.file2)
        tree.build()
        
        # Check that leaves are sorted
        paths = [leaf.file_path for leaf in tree.leaves]
        sorted_paths = sorted(paths, key=lambda p: p.encode('utf-8'))
        self.assertEqual(paths, sorted_paths)
    
    def test_inclusion_proof(self):
        """Test generating inclusion proofs."""
        tree = MerkleTree()
        tree.add_file(self.file1)
        tree.add_file(self.file2)
        tree.build()
        
        proof = tree.get_inclusion_proof(self.file1)
        
        self.assertIsNotNone(proof)
        self.assertEqual(proof.leaf_path, str(self.file1))
        self.assertEqual(proof.root_hash, tree.get_root_hash())
    
    def test_proof_verification(self):
        """Test verifying inclusion proofs."""
        tree = MerkleTree()
        tree.add_file(self.file1)
        tree.add_file(self.file2)
        tree.add_file(self.file3)
        tree.build()
        
        # Get proof for each file
        for file in [self.file1, self.file2, self.file3]:
            proof = tree.get_inclusion_proof(file)
            self.assertIsNotNone(proof)
            
            # Verify proof
            self.assertTrue(proof.verify(), f"Proof verification failed for {file}")
    
    def test_verify_tree(self):
        """Test verifying entire tree."""
        tree = MerkleTree()
        tree.add_file(self.file1)
        tree.add_file(self.file2)
        tree.build()
        
        self.assertTrue(tree.verify_tree())
    
    def test_export_proofs_jsonl(self):
        """Test exporting proofs to JSONL."""
        tree = MerkleTree()
        tree.add_file(self.file1)
        tree.add_file(self.file2)
        tree.build()
        
        output_file = self.test_path / "proofs.jsonl"
        tree.export_proofs_jsonl(output_file)
        
        self.assertTrue(output_file.exists())
        
        # Read and verify JSONL
        import json
        with open(output_file, 'r') as f:
            lines = f.readlines()
        
        self.assertEqual(len(lines), 2)
        
        # Each line should be valid JSON with proof data
        for line in lines:
            proof_data = json.loads(line)
            self.assertIn('leaf_path', proof_data)
            self.assertIn('leaf_hash', proof_data)
            self.assertIn('root_hash', proof_data)
            self.assertIn('proof_path', proof_data)
    
    def test_deterministic_root(self):
        """Test that tree root is deterministic."""
        # Build first tree
        tree1 = MerkleTree()
        tree1.add_file(self.file1)
        tree1.add_file(self.file2)
        tree1.build()
        root1 = tree1.get_root_hash()
        
        # Build second tree with same files
        tree2 = MerkleTree()
        tree2.add_file(self.file1)
        tree2.add_file(self.file2)
        tree2.build()
        root2 = tree2.get_root_hash()
        
        # Roots should match
        self.assertEqual(root1, root2)
    
    def test_file_not_found(self):
        """Test handling non-existent files."""
        tree = MerkleTree()
        
        with self.assertRaises(FileNotFoundError):
            tree.add_file(self.test_path / "nonexistent.txt")
    
    def test_proof_for_nonexistent_file(self):
        """Test getting proof for file not in tree."""
        tree = MerkleTree()
        tree.add_file(self.file1)
        tree.build()
        
        proof = tree.get_inclusion_proof(self.file2)
        self.assertIsNone(proof)


if __name__ == '__main__':
    unittest.main()
