"""
Unit tests for manifest module
"""

import json
import tempfile
import unittest
from pathlib import Path

from canonicalization_scaffold.manifest import (
    ManifestGenerator,
    generate_manifest,
)


class TestManifestGenerator(unittest.TestCase):
    """Test cases for ManifestGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create test repository structure
        self.repo_path = self.temp_path / "test_repo"
        self.repo_path.mkdir()
        
        # Create test files
        (self.repo_path / "file1.txt").write_text("Hello")
        (self.repo_path / "file2.json").write_text('{"key": "value"}')
        
        # Create subdirectory
        subdir = self.repo_path / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("World")
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_get_canonical_path(self):
        """Test canonical path generation."""
        file_path = self.repo_path / "subdir" / "file.txt"
        
        result = ManifestGenerator._get_canonical_path(file_path, self.repo_path)
        
        # Should be relative with forward slashes
        self.assertEqual(result, "subdir/file.txt")
    
    def test_get_content_addressed_ref(self):
        """Test content-addressed reference generation."""
        hash_value = "abc123def456"
        
        result = ManifestGenerator._get_content_addressed_ref(hash_value)
        
        self.assertEqual(result, "sha256:abc123def456")
    
    def test_generate_manifest_entry(self):
        """Test generating a single manifest entry."""
        generator = ManifestGenerator()
        file_path = self.repo_path / "file1.txt"
        
        entry = generator.generate_manifest_entry(file_path, self.repo_path)
        
        # Check required fields
        self.assertIn("canonical_path", entry)
        self.assertIn("file_type", entry)
        self.assertIn("canonical_hash", entry)
        self.assertIn("size", entry)
        self.assertIn("content_addressed_ref", entry)
        
        # Check values
        self.assertEqual(entry["canonical_path"], "file1.txt")
        self.assertEqual(entry["file_type"], "text")
        self.assertEqual(entry["size"], 5)  # "Hello" is 5 bytes
        self.assertTrue(entry["content_addressed_ref"].startswith("sha256:"))
    
    def test_generate_manifest_stream(self):
        """Test streaming manifest generation."""
        generator = ManifestGenerator()
        
        entries = list(generator.generate_manifest_stream(self.repo_path))
        
        # Should have 3 files
        self.assertEqual(len(entries), 3)
        
        # Check that all have required fields
        for entry in entries:
            self.assertIn("canonical_path", entry)
            self.assertIn("file_type", entry)
    
    def test_generate_manifest_stream_exclusions(self):
        """Test manifest generation with exclusions."""
        # Create files that should be excluded
        (self.repo_path / ".git").mkdir()
        (self.repo_path / ".git" / "config").write_text("git config")
        (self.repo_path / "test.pyc").write_text("compiled")
        
        generator = ManifestGenerator()
        exclude = {'.git', '*.pyc'}
        
        entries = list(generator.generate_manifest_stream(self.repo_path, exclude))
        
        # Should not include .git or .pyc files
        paths = [e["canonical_path"] for e in entries]
        self.assertNotIn(".git/config", paths)
        # Original 3 files should still be there
        self.assertIn("file1.txt", paths)
    
    def test_write_manifest(self):
        """Test writing manifest to file."""
        generator = ManifestGenerator()
        output_path = self.temp_path / "manifest.jsonl"
        
        count = generator.write_manifest(self.repo_path, output_path)
        
        # Should process 3 files
        self.assertEqual(count, 3)
        
        # Check output file
        self.assertTrue(output_path.exists())
        
        with open(output_path, 'r') as f:
            lines = f.readlines()
        
        # Should have 3 lines
        self.assertEqual(len(lines), 3)
        
        # Each line should be valid JSON
        for line in lines:
            entry = json.loads(line)
            self.assertIn("canonical_path", entry)
    
    def test_write_manifest_with_checkpointing(self):
        """Test manifest writing with checkpointing enabled."""
        generator = ManifestGenerator(checkpoint_interval=2)
        output_path = self.temp_path / "manifest.jsonl"
        
        count = generator.write_manifest(
            self.repo_path,
            output_path,
            enable_checkpoints=True
        )
        
        # Should process all files
        self.assertEqual(count, 3)
        
        # Checkpoint file should be cleaned up after completion
        checkpoint_path = output_path.parent / f"{output_path.stem}_checkpoint.jsonl"
        self.assertFalse(checkpoint_path.exists())
    
    def test_load_manifest(self):
        """Test loading manifest from file."""
        # Create manifest first
        generator = ManifestGenerator()
        output_path = self.temp_path / "manifest.jsonl"
        generator.write_manifest(self.repo_path, output_path)
        
        # Load it
        entries = list(ManifestGenerator.load_manifest(output_path))
        
        # Should load all entries
        self.assertEqual(len(entries), 3)
        
        for entry in entries:
            self.assertIn("canonical_path", entry)
    
    def test_verify_manifest_valid(self):
        """Test verifying a valid manifest."""
        # Create manifest
        generator = ManifestGenerator()
        output_path = self.temp_path / "manifest.jsonl"
        generator.write_manifest(self.repo_path, output_path)
        
        # Verify it
        results = ManifestGenerator.verify_manifest(output_path, self.repo_path)
        
        # All should verify
        self.assertEqual(results["total"], 3)
        self.assertEqual(results["verified"], 3)
        self.assertEqual(results["mismatched"], 0)
        self.assertEqual(results["missing"], 0)
    
    def test_verify_manifest_modified_file(self):
        """Test verifying manifest with modified file."""
        # Create manifest
        generator = ManifestGenerator()
        output_path = self.temp_path / "manifest.jsonl"
        generator.write_manifest(self.repo_path, output_path)
        
        # Modify a file
        (self.repo_path / "file1.txt").write_text("Modified")
        
        # Verify
        results = ManifestGenerator.verify_manifest(output_path, self.repo_path)
        
        # Should detect mismatch
        self.assertEqual(results["total"], 3)
        self.assertEqual(results["verified"], 2)
        self.assertEqual(results["mismatched"], 1)
    
    def test_verify_manifest_missing_file(self):
        """Test verifying manifest with missing file."""
        # Create manifest
        generator = ManifestGenerator()
        output_path = self.temp_path / "manifest.jsonl"
        generator.write_manifest(self.repo_path, output_path)
        
        # Delete a file
        (self.repo_path / "file1.txt").unlink()
        
        # Verify
        results = ManifestGenerator.verify_manifest(output_path, self.repo_path)
        
        # Should detect missing
        self.assertEqual(results["total"], 3)
        self.assertEqual(results["verified"], 2)
        self.assertEqual(results["missing"], 1)
    
    def test_generate_manifest_convenience(self):
        """Test convenience function."""
        output_path = self.temp_path / "manifest.jsonl"
        
        count = generate_manifest(self.repo_path, output_path)
        
        self.assertEqual(count, 3)
        self.assertTrue(output_path.exists())
    
    def test_manifest_deterministic(self):
        """Test that manifest generation is deterministic."""
        generator1 = ManifestGenerator()
        output_path1 = self.temp_path / "manifest1.jsonl"
        generator1.write_manifest(self.repo_path, output_path1)
        
        generator2 = ManifestGenerator()
        output_path2 = self.temp_path / "manifest2.jsonl"
        generator2.write_manifest(self.repo_path, output_path2)
        
        # Both manifests should be identical
        with open(output_path1, 'r') as f1, open(output_path2, 'r') as f2:
            content1 = f1.read()
            content2 = f2.read()
        
        self.assertEqual(content1, content2)
    
    def test_manifest_sorted_paths(self):
        """Test that manifest paths are sorted."""
        # Create files with various names
        (self.repo_path / "zzz.txt").write_text("last")
        (self.repo_path / "aaa.txt").write_text("first")
        
        generator = ManifestGenerator()
        entries = list(generator.generate_manifest_stream(self.repo_path))
        
        # Extract paths
        paths = [e["canonical_path"] for e in entries]
        
        # Should be sorted
        self.assertEqual(paths, sorted(paths))


if __name__ == '__main__':
    unittest.main()
