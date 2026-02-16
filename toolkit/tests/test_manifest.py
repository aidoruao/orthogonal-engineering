"""
Test module for manifest.py

Tests manifest generation and JSONL output.

Author: Orthogonal Engineering System
Date: 2026-02-16
Version: 1.0.0
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from toolkit.oe.manifest import ManifestEntry, ManifestGenerator


class TestManifestEntry(unittest.TestCase):
    """Test cases for ManifestEntry class."""
    
    def test_entry_creation(self):
        """Test creating a manifest entry."""
        entry = ManifestEntry(
            file_path='/path/to/file.txt',
            canonical_path='file.txt',
            file_type='text',
            canonical_hash='abc123',
            size=100
        )
        
        self.assertEqual(entry.file_path, '/path/to/file.txt')
        self.assertEqual(entry.canonical_path, 'file.txt')
        self.assertEqual(entry.file_type, 'text')
        self.assertEqual(entry.canonical_hash, 'abc123')
        self.assertEqual(entry.size, 100)
    
    def test_entry_to_dict(self):
        """Test converting entry to dictionary."""
        entry = ManifestEntry(
            file_path='/path/to/file.txt',
            canonical_path='file.txt',
            file_type='text',
            canonical_hash='abc123',
            size=100
        )
        
        data = entry.to_dict()
        
        self.assertIsInstance(data, dict)
        self.assertEqual(data['file_path'], '/path/to/file.txt')
        self.assertEqual(data['canonical_path'], 'file.txt')
        self.assertEqual(data['canonical_hash'], 'abc123')
    
    def test_entry_content_ref(self):
        """Test entry generates content-addressed reference."""
        entry = ManifestEntry(
            file_path='/path/to/file.txt',
            canonical_path='file.txt',
            file_type='text',
            canonical_hash='abc123',
            size=100
        )
        
        self.assertEqual(entry.content_ref, 'sha256:abc123')


class TestManifestGenerator(unittest.TestCase):
    """Test cases for ManifestGenerator class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create test files
        (self.test_path / 'file1.txt').write_text('content1')
        (self.test_path / 'file2.json').write_text('{"key": "value"}')
        
        subdir = self.test_path / 'subdir'
        subdir.mkdir()
        (subdir / 'file3.txt').write_text('content3')
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_generator_creation(self):
        """Test creating a manifest generator."""
        generator = ManifestGenerator(self.test_path)
        
        self.assertEqual(generator.base_path, self.test_path.resolve())
        self.assertEqual(len(generator.entries), 0)
    
    def test_add_file(self):
        """Test adding a file to manifest."""
        generator = ManifestGenerator(self.test_path)
        
        file_path = self.test_path / 'file1.txt'
        entry = generator.add_file(file_path)
        
        self.assertIsInstance(entry, ManifestEntry)
        self.assertEqual(entry.file_type, 'text')
        self.assertEqual(entry.size, 8)  # 'content1'
        self.assertEqual(len(generator.entries), 1)
    
    def test_add_file_not_found(self):
        """Test adding non-existent file raises error."""
        generator = ManifestGenerator(self.test_path)
        
        with self.assertRaises(FileNotFoundError):
            generator.add_file(self.test_path / 'nonexistent.txt')
    
    def test_scan_directory(self):
        """Test scanning directory for files."""
        generator = ManifestGenerator(self.test_path)
        
        entries = list(generator.scan_directory())
        
        # Should find all 3 test files
        self.assertEqual(len(entries), 3)
    
    def test_scan_directory_with_exclusions(self):
        """Test scanning with exclusion patterns."""
        generator = ManifestGenerator(self.test_path)
        
        # Create a file to exclude
        (self.test_path / 'test.pyc').write_text('bytecode')
        
        entries = list(generator.scan_directory(exclude_patterns=['*.pyc']))
        
        # Should not include .pyc file
        paths = [e.canonical_path for e in entries]
        self.assertNotIn('test.pyc', paths)
    
    def test_save_manifest(self):
        """Test saving manifest to JSONL file."""
        generator = ManifestGenerator(self.test_path)
        
        generator.add_file(self.test_path / 'file1.txt')
        generator.add_file(self.test_path / 'file2.json')
        
        output_path = self.test_path / 'manifest.jsonl'
        generator.save_manifest(output_path)
        
        # Verify file exists
        self.assertTrue(output_path.exists())
        
        # Verify JSONL format
        with open(output_path, 'r') as f:
            lines = f.readlines()
        
        self.assertEqual(len(lines), 2)
        
        for line in lines:
            data = json.loads(line)
            self.assertIn('file_path', data)
            self.assertIn('canonical_hash', data)
    
    def test_load_manifest(self):
        """Test loading manifest from JSONL file."""
        generator = ManifestGenerator(self.test_path)
        
        # Create and save manifest
        generator.add_file(self.test_path / 'file1.txt')
        output_path = self.test_path / 'manifest.jsonl'
        generator.save_manifest(output_path)
        
        # Load it back
        loaded_entries = generator.load_manifest(output_path)
        
        self.assertEqual(len(loaded_entries), 1)
        self.assertIsInstance(loaded_entries[0], ManifestEntry)
    
    def test_generate_streaming_manifest(self):
        """Test generating manifest with streaming."""
        generator = ManifestGenerator(self.test_path, checkpoint_interval=2)
        
        output_path = self.test_path / 'manifest.jsonl'
        generator.generate_streaming_manifest(output_path)
        
        # Verify manifest was created
        self.assertTrue(output_path.exists())
        
        # Load and verify
        with open(output_path, 'r') as f:
            lines = f.readlines()
        
        # Should have entries for all files
        self.assertGreaterEqual(len(lines), 3)
    
    def test_checkpoint_clears_entries(self):
        """Test that checkpointing clears entries."""
        generator = ManifestGenerator(self.test_path)
        
        generator.add_file(self.test_path / 'file1.txt')
        self.assertEqual(len(generator.entries), 1)
        
        output_path = self.test_path / 'manifest.jsonl'
        generator.save_manifest(output_path, checkpoint=True)
        
        # Entries should be cleared after checkpoint
        self.assertEqual(len(generator.entries), 0)


if __name__ == '__main__':
    unittest.main()
