"""
Unit tests for the Deterministic Auditable Scaffold

Tests all modules: canonicalizer, hasher, merkle, manifest, logger, handling_pipeline, CLI
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from toolkit.oe.scaffold.canonicalizer import (
    canonical_byte_representation,
    detect_file_type,
    normalize_text,
    canonicalize_json,
    FileType,
)
from toolkit.oe.scaffold.hasher import compute_hash, compute_file_hash
from toolkit.oe.scaffold.merkle import (
    build_merkle_tree,
    compute_leaf_hash,
    compute_internal_hash,
    MerkleTree,
)
from toolkit.oe.scaffold.manifest import (
    generate_manifest,
    create_manifest_entry,
    iterate_manifest,
)
from toolkit.oe.scaffold.logger import ScaffoldLogger, LogReader
from toolkit.oe.scaffold.handling_pipeline import (
    HandlingMetaParser,
    HandlingClampPipeline,
    create_sample_handling_meta,
)


class TestCanonicalizer(unittest.TestCase):
    """Test canonicalizer module."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_detect_file_type(self):
        """Test file type detection."""
        self.assertEqual(detect_file_type("test.json"), FileType.JSON)
        self.assertEqual(detect_file_type("test.xml"), FileType.XML)
        self.assertEqual(detect_file_type("test.txt"), FileType.TEXT)
        self.assertEqual(detect_file_type("test.py"), FileType.TEXT)
        self.assertEqual(detect_file_type("test.bin"), FileType.BINARY)
    
    def test_normalize_text(self):
        """Test text normalization."""
        # Test line ending normalization
        text = "line1\r\nline2\rline3\n"
        normalized = normalize_text(text)
        self.assertIn("\n", normalized)
        self.assertNotIn("\r", normalized)
        
        # Test trailing whitespace
        text = "line1  \nline2\t\n"
        normalized = normalize_text(text)
        self.assertEqual(normalized, "line1\nline2\n")
    
    def test_canonicalize_json(self):
        """Test JSON canonicalization."""
        json_str = '{"b": 2, "a": 1}'
        canonical = canonicalize_json(json_str)
        self.assertEqual(canonical, '{"a":1,"b":2}')
    
    def test_canonical_byte_representation_text(self):
        """Test canonical representation for text files."""
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("Hello\r\nWorld\r\n", encoding="utf-8")
        
        canonical = canonical_byte_representation(test_file)
        self.assertEqual(canonical, b"Hello\nWorld\n")
    
    def test_canonical_byte_representation_json(self):
        """Test canonical representation for JSON files."""
        test_file = Path(self.temp_dir) / "test.json"
        test_file.write_text('{"b": 2, "a": 1}', encoding="utf-8")
        
        canonical = canonical_byte_representation(test_file)
        self.assertEqual(canonical, b'{"a":1,"b":2}')
    
    def test_canonical_byte_representation_binary(self):
        """Test canonical representation for binary files."""
        test_file = Path(self.temp_dir) / "test.bin"
        test_file.write_bytes(b"\x00\x01\x02\x03")
        
        canonical = canonical_byte_representation(test_file)
        self.assertEqual(canonical, b"\x00\x01\x02\x03")


class TestHasher(unittest.TestCase):
    """Test hasher module."""
    
    def test_compute_hash(self):
        """Test SHA-256 hash computation."""
        data = b"Hello, World!"
        hash_value = compute_hash(data)
        
        # Verify it's a valid SHA-256 hex string
        self.assertEqual(len(hash_value), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in hash_value))
    
    def test_compute_hash_deterministic(self):
        """Test hash is deterministic."""
        data = b"Test data"
        hash1 = compute_hash(data)
        hash2 = compute_hash(data)
        self.assertEqual(hash1, hash2)
    
    def test_compute_file_hash(self):
        """Test file hash computation."""
        temp_dir = tempfile.mkdtemp()
        try:
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("Hello\n", encoding="utf-8")
            
            hash_value = compute_file_hash(test_file)
            self.assertEqual(len(hash_value), 64)
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestMerkle(unittest.TestCase):
    """Test Merkle tree module."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_compute_leaf_hash(self):
        """Test leaf hash computation."""
        data = b"test data"
        leaf_hash = compute_leaf_hash(data)
        
        # Verify format
        self.assertEqual(len(leaf_hash), 64)
        
        # Verify it uses 0x00 prefix
        import hashlib
        expected = hashlib.sha256(b'\x00' + data).hexdigest()
        self.assertEqual(leaf_hash, expected)
    
    def test_compute_internal_hash(self):
        """Test internal node hash computation."""
        left = "a" * 64
        right = "b" * 64
        
        internal = compute_internal_hash(left, right)
        self.assertEqual(len(internal), 64)
    
    def test_build_merkle_tree_single_file(self):
        """Test Merkle tree with single file."""
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("Hello\n", encoding="utf-8")
        
        tree = build_merkle_tree([test_file])
        
        self.assertIsNotNone(tree.root)
        self.assertEqual(len(tree.leaves), 1)
        self.assertIsInstance(tree.get_root_hash(), str)
    
    def test_build_merkle_tree_multiple_files(self):
        """Test Merkle tree with multiple files."""
        files = []
        for i in range(3):
            f = Path(self.temp_dir) / f"test{i}.txt"
            f.write_text(f"Content {i}\n", encoding="utf-8")
            files.append(f)
        
        tree = build_merkle_tree(files)
        
        self.assertEqual(len(tree.leaves), 3)
        self.assertIsInstance(tree.get_root_hash(), str)
    
    def test_merkle_proof(self):
        """Test Merkle proof generation."""
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("Hello\n", encoding="utf-8")
        
        tree = build_merkle_tree([test_file])
        proof = tree.get_proof(str(test_file))
        
        self.assertIsNotNone(proof)
        self.assertEqual(proof["file_path"], str(test_file))
        self.assertIn("leaf_hash", proof)
        self.assertIn("root_hash", proof)


class TestManifest(unittest.TestCase):
    """Test manifest module."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_manifest_entry(self):
        """Test manifest entry creation."""
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("Hello\n", encoding="utf-8")
        
        entry = create_manifest_entry(test_file, base_path=self.temp_dir)
        
        self.assertEqual(entry.canonical_path, "test.txt")
        self.assertEqual(entry.file_type, FileType.TEXT)
        self.assertIsInstance(entry.canonical_hash, str)
        self.assertEqual(entry.size, 6)
    
    def test_generate_manifest(self):
        """Test manifest generation."""
        # Create test files
        files = []
        for i in range(3):
            f = Path(self.temp_dir) / f"test{i}.txt"
            f.write_text(f"Content {i}\n", encoding="utf-8")
            files.append(f)
        
        output_path = Path(self.temp_dir) / "manifest.jsonl"
        count = generate_manifest(files, output_path, base_path=self.temp_dir)
        
        self.assertEqual(count, 3)
        self.assertTrue(output_path.exists())
    
    def test_iterate_manifest(self):
        """Test manifest iteration."""
        # Create test file and manifest
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("Hello\n", encoding="utf-8")
        
        output_path = Path(self.temp_dir) / "manifest.jsonl"
        generate_manifest([test_file], output_path, base_path=self.temp_dir)
        
        # Iterate and verify
        entries = list(iterate_manifest(output_path))
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["canonical_path"], "test.txt")


class TestLogger(unittest.TestCase):
    """Test logger module."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_logger_basic(self):
        """Test basic logging."""
        log_path = Path(self.temp_dir) / "test.jsonl"
        logger = ScaffoldLogger(log_path)
        
        logger.log("test_event", "Test message", extra_field="value")
        
        # Verify log file
        self.assertTrue(log_path.exists())
        
        # Read and verify
        entries = LogReader.read_log(log_path)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["event_type"], "test_event")
        self.assertEqual(entries[0]["message"], "Test message")
        self.assertEqual(entries[0]["extra_field"], "value")
    
    def test_logger_step_id(self):
        """Test monotonic step_id."""
        log_path = Path(self.temp_dir) / "test.jsonl"
        logger = ScaffoldLogger(log_path)
        
        logger.log("event1", "Message 1")
        logger.log("event2", "Message 2")
        logger.log("event3", "Message 3")
        
        entries = LogReader.read_log(log_path)
        
        self.assertEqual(entries[0]["step_id"], 1)
        self.assertEqual(entries[1]["step_id"], 2)
        self.assertEqual(entries[2]["step_id"], 3)
    
    def test_logger_timestamps(self):
        """Test ISO8601 timestamps."""
        log_path = Path(self.temp_dir) / "test.jsonl"
        logger = ScaffoldLogger(log_path)
        
        logger.log("test", "Message")
        
        entries = LogReader.read_log(log_path)
        timestamp = entries[0]["timestamp"]
        
        # Verify ISO8601 format (contains 'T' and ends with timezone)
        self.assertIn("T", timestamp)
        self.assertTrue(timestamp.endswith("+00:00") or timestamp.endswith("Z"))


class TestHandlingPipeline(unittest.TestCase):
    """Test handling pipeline module."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_sample_handling_meta(self):
        """Test sample handling.meta creation."""
        output_path = Path(self.temp_dir) / "handling.meta"
        create_sample_handling_meta(output_path)
        
        self.assertTrue(output_path.exists())
        content = output_path.read_text()
        self.assertIn("CHandlingData", content)
        self.assertIn("ADDER", content)
    
    def test_parse_handling_meta(self):
        """Test handling.meta parsing."""
        output_path = Path(self.temp_dir) / "handling.meta"
        create_sample_handling_meta(output_path)
        
        parser = HandlingMetaParser()
        items = parser.parse_file(output_path)
        
        self.assertGreater(len(items), 0)
        self.assertIn("ADDER", parser.get_vehicle_names())
    
    def test_handling_clamp_pipeline(self):
        """Test handling clamp pipeline."""
        output_path = Path(self.temp_dir) / "handling.meta"
        create_sample_handling_meta(output_path)
        
        parser = HandlingMetaParser()
        items = parser.parse_file(output_path)
        
        pipeline = HandlingClampPipeline()
        results = pipeline.clamp_all(items, apply=False)
        
        self.assertEqual(len(results), len(items))
        
        # Results should have vehicle name
        for result in results:
            self.assertIn("vehicle", result)
            self.assertIn("violations", result)


def run_all_tests():
    """Run all scaffold tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCanonicalizer))
    suite.addTests(loader.loadTestsFromTestCase(TestHasher))
    suite.addTests(loader.loadTestsFromTestCase(TestMerkle))
    suite.addTests(loader.loadTestsFromTestCase(TestManifest))
    suite.addTests(loader.loadTestsFromTestCase(TestLogger))
    suite.addTests(loader.loadTestsFromTestCase(TestHandlingPipeline))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
