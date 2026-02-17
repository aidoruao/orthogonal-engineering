"""
Unit tests for manifest module.
"""

import tempfile
import json
import pytest
from pathlib import Path

from toolkit.oe.scaffold.manifest import ManifestBuilder, ManifestEntry


def test_manifest_entry_to_dict():
    """Test ManifestEntry conversion to dict."""
    entry = ManifestEntry(
        canonical_path="test.txt",
        file_type="text/plain",
        canonical_hash="abc123",
        size=1024,
        content_address="sha256:abc123"
    )
    
    result = entry.to_dict()
    
    assert result['canonical_path'] == "test.txt"
    assert result['file_type'] == "text/plain"
    assert result['canonical_hash'] == "abc123"
    assert result['size'] == 1024
    assert result['content_address'] == "sha256:abc123"


def test_manifest_builder_add_file():
    """Test adding single file to manifest."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create test file
        test_file = tmpdir / "test.txt"
        test_file.write_text("Test content")
        
        # Build manifest
        manifest_path = tmpdir / "manifest.jsonl"
        builder = ManifestBuilder(output_path=manifest_path)
        
        entry = builder.add_file(test_file, "test.txt")
        
        assert entry is not None
        assert entry.canonical_path == "test.txt"
        assert entry.size == len("Test content")
        assert len(entry.canonical_hash) == 64
        assert entry.content_address.startswith("sha256:")
        
        # Verify file written
        assert manifest_path.exists()


def test_manifest_builder_add_directory():
    """Test adding directory to manifest."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create test files
        (tmpdir / "a.txt").write_text("File A")
        (tmpdir / "b.txt").write_text("File B")
        (tmpdir / "subdir").mkdir()
        (tmpdir / "subdir" / "c.txt").write_text("File C")
        
        # Build manifest
        manifest_path = tmpdir / "manifest.jsonl"
        builder = ManifestBuilder(output_path=manifest_path)
        
        entries = list(builder.add_directory(tmpdir, pattern="**/*.txt"))
        
        assert len(entries) == 3
        
        # Verify manifest file
        with open(manifest_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 3


def test_manifest_builder_skip_duplicates():
    """Test that duplicate files are skipped."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        test_file = tmpdir / "test.txt"
        test_file.write_text("Test")
        
        manifest_path = tmpdir / "manifest.jsonl"
        builder = ManifestBuilder(output_path=manifest_path)
        
        # Add same file twice
        entry1 = builder.add_file(test_file, "test.txt")
        entry2 = builder.add_file(test_file, "test.txt")
        
        assert entry1 is not None
        assert entry2 is None  # Should be skipped


def test_manifest_builder_checkpointing():
    """Test checkpointing functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create many files to trigger checkpoint
        for i in range(150):
            (tmpdir / f"file_{i}.txt").write_text(f"Content {i}")
        
        manifest_path = tmpdir / "manifest.jsonl"
        checkpoint_path = tmpdir / "checkpoint.json"
        
        builder = ManifestBuilder(
            output_path=manifest_path,
            checkpoint_path=checkpoint_path
        )
        
        list(builder.add_directory(tmpdir, pattern="*.txt"))
        builder.finalize()
        
        # Verify checkpoint created
        assert checkpoint_path.exists()
        
        with open(checkpoint_path, 'r') as f:
            checkpoint = json.load(f)
            assert 'processed_files' in checkpoint
            assert checkpoint['total_processed'] == 150


def test_manifest_builder_resume_from_checkpoint():
    """Test resuming from checkpoint."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create files
        (tmpdir / "a.txt").write_text("File A")
        (tmpdir / "b.txt").write_text("File B")
        
        manifest_path = tmpdir / "manifest.jsonl"
        checkpoint_path = tmpdir / "checkpoint.json"
        
        # First run - process first file
        builder1 = ManifestBuilder(
            output_path=manifest_path,
            checkpoint_path=checkpoint_path
        )
        builder1.add_file(tmpdir / "a.txt", "a.txt")
        builder1.finalize()
        
        # Second run - should skip first file
        builder2 = ManifestBuilder(
            output_path=manifest_path,
            checkpoint_path=checkpoint_path
        )
        
        # Try to add both files
        entry_a = builder2.add_file(tmpdir / "a.txt", "a.txt")
        entry_b = builder2.add_file(tmpdir / "b.txt", "b.txt")
        
        # First should be skipped
        assert entry_a is None
        assert entry_b is not None


def test_manifest_builder_file_type_detection():
    """Test file type detection."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create files with different types
        (tmpdir / "test.txt").write_text("Text")
        (tmpdir / "test.json").write_text('{"key": "value"}')
        (tmpdir / "test.py").write_text("print('hello')")
        
        manifest_path = tmpdir / "manifest.jsonl"
        builder = ManifestBuilder(output_path=manifest_path)
        
        entries = list(builder.add_directory(tmpdir))
        
        # Check detected types
        types = {e.canonical_path: e.file_type for e in entries}
        
        assert 'text/plain' in types.get('test.txt', '')
        assert 'json' in types.get('test.json', '').lower()
        assert 'python' in types.get('test.py', '').lower()


def test_manifest_builder_deterministic_ordering():
    """Test that manifest entries are ordered deterministically."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create files in non-alphabetical order
        (tmpdir / "z.txt").write_text("Z")
        (tmpdir / "a.txt").write_text("A")
        (tmpdir / "m.txt").write_text("M")
        
        manifest_path = tmpdir / "manifest.jsonl"
        builder = ManifestBuilder(output_path=manifest_path)
        
        list(builder.add_directory(tmpdir, pattern="*.txt"))
        
        # Read manifest and check order
        with open(manifest_path, 'r') as f:
            paths = [json.loads(line)['canonical_path'] for line in f]
        
        # Should be sorted
        assert paths == sorted(paths)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
