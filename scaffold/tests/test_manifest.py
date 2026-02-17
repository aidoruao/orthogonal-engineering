"""
Unit tests for manifest module.

Tests manifest generation and verification.
"""

import json
import tempfile
import unittest
from pathlib import Path

from scaffold.manifest import (
    ManifestCheckpoint,
    ManifestEntry,
    ManifestGenerator,
)


class TestManifestEntry(unittest.TestCase):
    """Test cases for ManifestEntry class."""
    
    def test_creation(self):
        """Test creating manifest entry."""
        entry = ManifestEntry(
            canonical_path="test/file.txt",
            file_type="text",
            canonical_hash="abc123",
            size=100
        )
        
        self.assertEqual(entry.canonical_path, "test/file.txt")
        self.assertEqual(entry.file_type, "text")
        self.assertEqual(entry.canonical_hash, "abc123")
        self.assertEqual(entry.size, 100)
        self.assertTrue(entry.content_address.startswith("sha256:"))
    
    def test_to_dict(self):
        """Test converting entry to dictionary."""
        entry = ManifestEntry(
            canonical_path="test.txt",
            file_type="text",
            canonical_hash="abc123",
            size=50
        )
        
        data = entry.to_dict()
        
        self.assertIn('canonical_path', data)
        self.assertIn('file_type', data)
        self.assertIn('canonical_hash', data)
        self.assertIn('size', data)
        self.assertIn('content_address', data)
    
    def test_from_dict(self):
        """Test creating entry from dictionary."""
        data = {
            "canonical_path": "test.txt",
            "file_type": "text",
            "canonical_hash": "abc123",
            "size": 50,
            "content_address": "sha256:abc123"
        }
        
        entry = ManifestEntry.from_dict(data)
        
        self.assertEqual(entry.canonical_path, "test.txt")
        self.assertEqual(entry.canonical_hash, "abc123")


class TestManifestCheckpoint(unittest.TestCase):
    """Test cases for ManifestCheckpoint class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        self.checkpoint_file = self.test_path / "checkpoint.json"
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test checkpoint initialization."""
        checkpoint = ManifestCheckpoint(self.checkpoint_file)
        self.assertEqual(len(checkpoint.processed_files), 0)
    
    def test_save_and_load(self):
        """Test saving and loading checkpoint."""
        checkpoint = ManifestCheckpoint(self.checkpoint_file)
        
        processed = {"file1.txt", "file2.txt", "file3.txt"}
        checkpoint.save(processed)
        
        self.assertTrue(self.checkpoint_file.exists())
        
        # Load checkpoint
        checkpoint2 = ManifestCheckpoint(self.checkpoint_file)
        self.assertEqual(checkpoint2.processed_files, processed)
    
    def test_mark_processed(self):
        """Test marking files as processed."""
        checkpoint = ManifestCheckpoint(self.checkpoint_file)
        
        checkpoint.mark_processed("file1.txt")
        checkpoint.mark_processed("file2.txt")
        
        self.assertTrue(checkpoint.is_processed("file1.txt"))
        self.assertTrue(checkpoint.is_processed("file2.txt"))
        self.assertFalse(checkpoint.is_processed("file3.txt"))
    
    def test_clear(self):
        """Test clearing checkpoint."""
        checkpoint = ManifestCheckpoint(self.checkpoint_file)
        checkpoint.mark_processed("file.txt")
        checkpoint.save(checkpoint.processed_files)
        
        checkpoint.clear()
        
        self.assertEqual(len(checkpoint.processed_files), 0)
        self.assertFalse(self.checkpoint_file.exists())


class TestManifestGenerator(unittest.TestCase):
    """Test cases for ManifestGenerator class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create test files
        (self.test_path / "file1.txt").write_text("Content 1")
        (self.test_path / "file2.txt").write_text("Content 2")
        
        # Create subdirectory
        subdir = self.test_path / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("Content 3")
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test generator initialization."""
        gen = ManifestGenerator(self.test_path)
        
        self.assertEqual(gen.repo_path, self.test_path)
        self.assertEqual(gen.output_path, self.test_path / "manifest.jsonl")
    
    def test_generate_manifest(self):
        """Test generating manifest."""
        gen = ManifestGenerator(self.test_path)
        processed = gen.generate(resume=False)
        
        self.assertGreater(processed, 0)
        self.assertTrue(gen.output_path.exists())
    
    def test_iter_entries(self):
        """Test iterating manifest entries."""
        gen = ManifestGenerator(self.test_path)
        gen.generate(resume=False)
        
        entries = list(gen.iter_entries())
        
        self.assertGreater(len(entries), 0)
        
        # Check entry structure
        for entry in entries:
            self.assertIsNotNone(entry.canonical_path)
            self.assertIsNotNone(entry.file_type)
            self.assertIsNotNone(entry.canonical_hash)
            self.assertGreater(entry.size, 0)
    
    def test_get_statistics(self):
        """Test getting generation statistics."""
        gen = ManifestGenerator(self.test_path)
        gen.generate(resume=False)
        
        stats = gen.get_statistics()
        
        self.assertIn('total_files', stats)
        self.assertIn('processed_files', stats)
        self.assertIn('errors', stats)
        self.assertGreater(stats['processed_files'], 0)
    
    def test_verify_manifest(self):
        """Test manifest verification."""
        gen = ManifestGenerator(self.test_path)
        gen.generate(resume=False)
        
        errors = gen.verify_manifest()
        
        # Should have no errors for freshly generated manifest
        self.assertEqual(len(errors), 0)
    
    def test_verify_manifest_with_changes(self):
        """Test verification detects changes."""
        gen = ManifestGenerator(self.test_path)
        gen.generate(resume=False)
        
        # Modify a file
        (self.test_path / "file1.txt").write_text("Modified content")
        
        errors = gen.verify_manifest()
        
        # Should detect hash mismatch
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("Hash mismatch" in err for err in errors))
    
    def test_checkpoint_resume(self):
        """Test resuming from checkpoint."""
        gen = ManifestGenerator(self.test_path, checkpoint_interval=1)
        
        # Generate partial manifest
        gen.generate(resume=False)
        
        # Add new file
        (self.test_path / "file4.txt").write_text("New content")
        
        # Resume generation
        gen2 = ManifestGenerator(self.test_path, checkpoint_interval=1)
        processed = gen2.generate(resume=True)
        
        # Should process new file
        self.assertGreater(processed, 0)
    
    def test_should_include_filters(self):
        """Test file filtering."""
        # Create hidden file
        (self.test_path / ".hidden").write_text("Hidden")
        
        # Create __pycache__
        pycache = self.test_path / "__pycache__"
        pycache.mkdir()
        (pycache / "test.pyc").write_text("Bytecode")
        
        gen = ManifestGenerator(self.test_path)
        gen.generate(resume=False)
        
        entries = list(gen.iter_entries())
        
        # Hidden files and __pycache__ should be excluded
        paths = [e.canonical_path for e in entries]
        self.assertNotIn('.hidden', paths)
        self.assertFalse(any('__pycache__' in p for p in paths))


if __name__ == '__main__':
    unittest.main()
