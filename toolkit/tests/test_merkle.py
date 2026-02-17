"""
Test module for merkle.py

Tests binary Merkle tree construction, proof generation, and verification.

Author: Orthogonal Engineering System
Date: 2026-02-16
Version: 1.0.0
"""

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from toolkit.oe.merkle import MerkleNode, MerkleTree


class TestMerkleNode(unittest.TestCase):
    """Test cases for MerkleNode class."""
    
    def test_leaf_node_creation(self):
        """Test creating a leaf node."""
        node = MerkleNode('abc123', file_path='test.txt')
        
        self.assertEqual(node.hash, 'abc123')
        self.assertEqual(node.file_path, 'test.txt')
        self.assertTrue(node.is_leaf())
    
    def test_internal_node_creation(self):
        """Test creating an internal node."""
        left = MerkleNode('left_hash')
        right = MerkleNode('right_hash')
        parent = MerkleNode('parent_hash', left=left, right=right)
        
        self.assertEqual(parent.hash, 'parent_hash')
        self.assertFalse(parent.is_leaf())


class TestMerkleTree(unittest.TestCase):
    """Test cases for MerkleTree class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create test files
        self.files = []
        for i in range(4):
            file_path = self.test_path / f'file{i}.txt'
            with open(file_path, 'w') as f:
                f.write(f'content{i}')
            self.files.append(str(file_path))
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_tree_creation(self):
        """Test basic Merkle tree creation."""
        tree = MerkleTree(self.files, base_path=self.test_path)
        
        self.assertIsNotNone(tree.root)
        self.assertEqual(len(tree.leaves), 4)
    
    def test_leaf_hash_format(self):
        """Test leaf hash uses 0x00 prefix."""
        tree = MerkleTree(self.files[:1], base_path=self.test_path)
        
        # Manually compute expected leaf hash
        with open(self.files[0], 'r') as f:
            content = f.read().encode('utf-8')
        expected = hashlib.sha256(b'\x00' + content).hexdigest()
        
        self.assertEqual(tree.leaves[0].hash, expected)
    
    def test_root_hash_deterministic(self):
        """Test root hash is deterministic."""
        tree1 = MerkleTree(self.files, base_path=self.test_path)
        tree2 = MerkleTree(self.files, base_path=self.test_path)
        
        self.assertEqual(tree1.get_root_hash(), tree2.get_root_hash())
    
    def test_root_hash_order_independent_after_sorting(self):
        """Test root hash is same regardless of input order (due to sorting)."""
        # Create tree with files in different order
        tree1 = MerkleTree(self.files, base_path=self.test_path)
        tree2 = MerkleTree(list(reversed(self.files)), base_path=self.test_path)
        
        # Should be same due to canonical sorting
        self.assertEqual(tree1.get_root_hash(), tree2.get_root_hash())
    
    def test_single_file_tree(self):
        """Test Merkle tree with single file."""
        tree = MerkleTree(self.files[:1], base_path=self.test_path)
        
        self.assertEqual(len(tree.leaves), 1)
        self.assertIsNotNone(tree.get_root_hash())
    
    def test_odd_number_files(self):
        """Test Merkle tree with odd number of files."""
        # Use 3 files
        tree = MerkleTree(self.files[:3], base_path=self.test_path)
        
        self.assertEqual(len(tree.leaves), 3)
        self.assertIsNotNone(tree.get_root_hash())
    
    def test_get_proof(self):
        """Test getting inclusion proof for a file."""
        tree = MerkleTree(self.files, base_path=self.test_path)
        
        proof = tree.get_proof(self.files[0])
        
        # Proof should exist
        self.assertIsInstance(proof, list)
        self.assertGreater(len(proof), 0)
        
        # Each proof step should have position and hash
        for position, hash_val in proof:
            self.assertIn(position, ['left', 'right'])
            self.assertEqual(len(hash_val), 64)  # SHA-256 hex
    
    def test_verify_proof(self):
        """Test verifying inclusion proof."""
        tree = MerkleTree(self.files, base_path=self.test_path)
        
        for file_path in self.files:
            proof = tree.get_proof(file_path)
            verified = tree.verify_proof(file_path, proof)
            self.assertTrue(verified)
    
    def test_verify_proof_invalid_file(self):
        """Test get_proof raises error for file not in tree."""
        tree = MerkleTree(self.files[:2], base_path=self.test_path)
        
        with self.assertRaises(ValueError):
            tree.get_proof(self.files[3])
    
    def test_export_proofs_jsonl(self):
        """Test exporting proofs to JSONL."""
        tree = MerkleTree(self.files, base_path=self.test_path)
        
        output_path = self.test_path / 'proofs.jsonl'
        tree.export_proofs_jsonl(output_path)
        
        # Verify file exists
        self.assertTrue(output_path.exists())
        
        # Verify JSONL format
        with open(output_path, 'r') as f:
            lines = f.readlines()
        
        self.assertEqual(len(lines), 4)  # One per file
        
        for line in lines:
            record = json.loads(line)
            self.assertIn('file_path', record)
            self.assertIn('leaf_hash', record)
            self.assertIn('proof', record)
            self.assertIn('root_hash', record)
            self.assertEqual(record['root_hash'], tree.get_root_hash())
    
    def test_empty_file_list_error(self):
        """Test that empty file list raises error."""
        with self.assertRaises(ValueError):
            MerkleTree([], base_path=self.test_path)
    
    def test_internal_hash_format(self):
        """Test internal hash uses 0x01 prefix."""
        tree = MerkleTree(self.files[:2], base_path=self.test_path)
        
        # Get leaf hashes
        left_hash = tree.leaves[0].hash
        right_hash = tree.leaves[1].hash
        
        # Manually compute expected internal hash
        left_bytes = bytes.fromhex(left_hash)
        right_bytes = bytes.fromhex(right_hash)
        expected = hashlib.sha256(b'\x01' + left_bytes + right_bytes).hexdigest()
        
        # Root should be the internal node
        self.assertEqual(tree.get_root_hash(), expected)
    
    def test_modified_file_changes_root(self):
        """Test that modifying a file changes the root hash."""
        tree1 = MerkleTree(self.files, base_path=self.test_path)
        root1 = tree1.get_root_hash()
        
        # Modify a file
        with open(self.files[0], 'w') as f:
            f.write('modified content')
        
        tree2 = MerkleTree(self.files, base_path=self.test_path)
        root2 = tree2.get_root_hash()
        
        # Root should change
        self.assertNotEqual(root1, root2)


if __name__ == '__main__':
    unittest.main()
