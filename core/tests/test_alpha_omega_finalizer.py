#!/usr/bin/env python3
"""
Unit tests for AlphaOmegaFinalizer.

Tests cover:
- Timestamp normalization
- Canonical byte serialization
- SHA-256 hashing
- Merkle tree construction
- Ledger writing and verification
- Redaction hooks
- Streaming file processing
"""

import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.alpha_omega_finalizer import AlphaOmegaFinalizer


class TestAlphaOmegaFinalizer:
    """Test suite for AlphaOmegaFinalizer."""
    
    def setup_method(self):
        """Set up test fixtures before each test."""
        # Create temporary directories
        self.temp_dir = tempfile.mkdtemp()
        self.vault_dir = Path(self.temp_dir) / "vault"
        self.outputs_dir = Path(self.temp_dir) / "outputs"
        
        self.vault_dir.mkdir()
        self.outputs_dir.mkdir()
        
        print(f"Test setup: vault={self.vault_dir}, outputs={self.outputs_dir}")
    
    def teardown_method(self):
        """Clean up test fixtures after each test."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
        print("Test cleanup complete")
    
    def test_timestamp_normalization_iso8601(self):
        """Test timestamp normalization with ISO8601 input."""
        finalizer = AlphaOmegaFinalizer(
            vault_dir=str(self.vault_dir),
            outputs_dir=str(self.outputs_dir)
        )
        
        # Test various ISO8601 formats
        test_cases = [
            ("2024-01-15T10:30:00Z", "2024-01-15T10:30:00Z"),
            ("2024-01-15T10:30:00+00:00", "2024-01-15T10:30:00Z"),
            ("2024-01-15T10:30:00", "2024-01-15T10:30:00Z"),  # Assumes UTC
        ]
        
        for input_ts, expected_output in test_cases:
            result = finalizer.normalize_timestamp(input_ts)
            assert result == expected_output, f"Failed for {input_ts}: got {result}"
        
        print("✅ Timestamp normalization test passed")
    
    def test_timestamp_normalization_fallback(self):
        """Test fallback epoch for missing timestamps."""
        fallback = "2000-01-01T00:00:00Z"
        finalizer = AlphaOmegaFinalizer(
            vault_dir=str(self.vault_dir),
            outputs_dir=str(self.outputs_dir),
            fallback_epoch=fallback
        )
        
        # Test None and invalid timestamps
        assert finalizer.normalize_timestamp(None) == fallback
        assert finalizer.normalize_timestamp("") == fallback
        assert finalizer.normalize_timestamp("invalid") == fallback
        
        print("✅ Timestamp fallback test passed")
    
    def test_canonical_serialization(self):
        """Test deterministic canonical serialization."""
        finalizer = AlphaOmegaFinalizer(
            vault_dir=str(self.vault_dir),
            outputs_dir=str(self.outputs_dir)
        )
        
        # Test that order doesn't matter
        data1 = {"b": 2, "a": 1, "c": 3}
        data2 = {"a": 1, "c": 3, "b": 2}
        
        bytes1 = finalizer.canonical_serialize(data1)
        bytes2 = finalizer.canonical_serialize(data2)
        
        assert bytes1 == bytes2, "Canonical serialization should be order-independent"
        
        # Verify format
        expected = b'{"a":1,"b":2,"c":3}'
        assert bytes1 == expected, f"Expected {expected}, got {bytes1}"
        
        print("✅ Canonical serialization test passed")
    
    def test_sha256_computation(self):
        """Test SHA-256 hash computation."""
        finalizer = AlphaOmegaFinalizer(
            vault_dir=str(self.vault_dir),
            outputs_dir=str(self.outputs_dir)
        )
        
        # Known test vector
        test_data = b"hello world"
        expected_hash = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
        
        result = finalizer.compute_sha256(test_data)
        assert result == expected_hash, f"SHA-256 mismatch: {result}"
        
        print("✅ SHA-256 computation test passed")
    
    def test_merkle_tree_single_entry(self):
        """Test Merkle tree with single entry."""
        finalizer = AlphaOmegaFinalizer(
            vault_dir=str(self.vault_dir),
            outputs_dir=str(self.outputs_dir)
        )
        
        # Single hash
        test_hash = "a" * 64
        finalizer.entry_hashes = [test_hash]
        
        root, levels = finalizer.build_merkle_tree()
        
        # Root should be the hash itself
        assert root == test_hash
        assert len(levels) == 1
        assert levels[0] == [test_hash]
        
        print("✅ Merkle tree (single entry) test passed")
    
    def test_merkle_tree_multiple_entries(self):
        """Test Merkle tree with multiple entries."""
        finalizer = AlphaOmegaFinalizer(
            vault_dir=str(self.vault_dir),
            outputs_dir=str(self.outputs_dir)
        )
        
        # Create test hashes
        hash1 = "a" * 64
        hash2 = "b" * 64
        hash3 = "c" * 64
        hash4 = "d" * 64
        
        finalizer.entry_hashes = [hash1, hash2, hash3, hash4]
        
        root, levels = finalizer.build_merkle_tree()
        
        # Should have 3 levels: [4 leaves, 2 parents, 1 root]
        assert len(levels) == 3
        assert len(levels[0]) == 4  # Leaves
        assert len(levels[1]) == 2  # Parents
        assert len(levels[2]) == 1  # Root
        
        # Manually verify structure
        # Level 1: hash(hash1 + hash2), hash(hash3 + hash4)
        expected_parent1 = finalizer.compute_sha256((hash1 + hash2).encode())
        expected_parent2 = finalizer.compute_sha256((hash3 + hash4).encode())
        
        assert levels[1][0] == expected_parent1
        assert levels[1][1] == expected_parent2
        
        # Level 2: hash(parent1 + parent2)
        expected_root = finalizer.compute_sha256((expected_parent1 + expected_parent2).encode())
        assert root == expected_root
        
        print("✅ Merkle tree (multiple entries) test passed")
    
    def test_merkle_tree_odd_entries(self):
        """Test Merkle tree with odd number of entries."""
        finalizer = AlphaOmegaFinalizer(
            vault_dir=str(self.vault_dir),
            outputs_dir=str(self.outputs_dir)
        )
        
        # 3 hashes (odd number)
        hash1 = "a" * 64
        hash2 = "b" * 64
        hash3 = "c" * 64
        
        finalizer.entry_hashes = [hash1, hash2, hash3]
        
        root, levels = finalizer.build_merkle_tree()
        
        # Should handle odd number by duplicating last
        assert len(levels) == 3
        assert len(levels[0]) == 3  # Leaves
        assert len(levels[1]) == 2  # Parents (hash3 duplicated)
        
        print("✅ Merkle tree (odd entries) test passed")
    
    def test_process_json_file(self):
        """Test processing a JSON file."""
        # Create a test JSON file
        test_data = [
            {"id": 1, "content": "Message 1", "timestamp": "2024-01-01T10:00:00Z"},
            {"id": 2, "content": "Message 2", "timestamp": "2024-01-01T11:00:00Z"}
        ]
        
        json_file = self.vault_dir / "test.json"
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        finalizer = AlphaOmegaFinalizer(
            vault_dir=str(self.vault_dir),
            outputs_dir=str(self.outputs_dir)
        )
        
        entries = finalizer.process_json_file(json_file)
        
        assert len(entries) == 2
        assert entries[0]["id"] == 1
        assert entries[1]["id"] == 2
        
        print("✅ JSON file processing test passed")
    
    def test_process_jsonl_file(self):
        """Test processing a JSONL file."""
        # Create a test JSONL file
        test_data = [
            {"id": 1, "content": "Message 1", "timestamp": "2024-01-01T10:00:00Z"},
            {"id": 2, "content": "Message 2", "timestamp": "2024-01-01T11:00:00Z"},
            {"id": 3, "content": "Message 3", "timestamp": "2024-01-01T12:00:00Z"}
        ]
        
        jsonl_file = self.vault_dir / "test.jsonl"
        with open(jsonl_file, 'w') as f:
            for entry in test_data:
                f.write(json.dumps(entry) + '\n')
        
        finalizer = AlphaOmegaFinalizer(
            vault_dir=str(self.vault_dir),
            outputs_dir=str(self.outputs_dir)
        )
        
        entries = finalizer.process_jsonl_file_streaming(jsonl_file)
        
        assert len(entries) == 3
        assert entries[0]["id"] == 1
        assert entries[2]["id"] == 3
        
        print("✅ JSONL file processing test passed")
    
    def test_redaction_disabled(self):
        """Test that redaction is disabled by default."""
        finalizer = AlphaOmegaFinalizer(
            vault_dir=str(self.vault_dir),
            outputs_dir=str(self.outputs_dir),
            redact=False
        )
        
        entry = {"user_id": "user123", "content": "sensitive data"}
        redacted = finalizer.apply_redaction(entry)
        
        # Should be unchanged
        assert redacted == entry
        
        print("✅ Redaction disabled test passed")
    
    def test_redaction_enabled(self):
        """Test basic redaction rules."""
        finalizer = AlphaOmegaFinalizer(
            vault_dir=str(self.vault_dir),
            outputs_dir=str(self.outputs_dir),
            redact=True
        )
        
        # Test sensitive content redaction
        entry = {"content": "This is explicit content"}
        redacted = finalizer.apply_redaction(entry)
        
        assert redacted["content"] == "[REDACTED: Sensitive content]"
        assert redacted.get("redacted") == True
        
        # Test user ID hashing
        entry = {"user_id": "user123", "content": "normal content"}
        redacted = finalizer.apply_redaction(entry)
        
        assert "user_id" not in redacted
        assert "user_id_hash" in redacted
        assert len(redacted["user_id_hash"]) == 16
        
        print("✅ Redaction enabled test passed")
    
    def test_full_pipeline_dry_run(self):
        """Test complete finalization pipeline in dry-run mode."""
        # Create test data
        test_data = [
            {"id": 1, "content": "First message", "timestamp": "2024-01-01T10:00:00Z"},
            {"id": 2, "content": "Second message", "timestamp": "2024-01-01T11:00:00Z"}
        ]
        
        json_file = self.vault_dir / "chat_export.json"
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        # Run finalization in dry-run mode
        finalizer = AlphaOmegaFinalizer(
            vault_dir=str(self.vault_dir),
            outputs_dir=str(self.outputs_dir),
            dry_run=True
        )
        
        merkle_root, ledger_path, root_path = finalizer.finalize()
        
        # Should compute root but not write files
        assert merkle_root is not None
        assert len(merkle_root) == 64  # SHA-256 hex length
        assert ledger_path is None  # Dry run doesn't write
        assert root_path is None
        
        # Verify no files were created
        assert not (self.outputs_dir / "SOVEREIGN_CONSTITUTION.jsonl").exists()
        assert not (self.outputs_dir / "MASTER_ROOT.txt").exists()
        
        print("✅ Full pipeline (dry-run) test passed")
    
    def test_full_pipeline_with_write(self):
        """Test complete finalization pipeline with actual file writing."""
        # Create test data
        test_data = [
            {"id": 1, "content": "First message", "timestamp": "2024-01-01T10:00:00Z"},
            {"id": 2, "content": "Second message", "timestamp": "2024-01-01T11:00:00Z"},
            {"id": 3, "content": "Third message", "timestamp": "2024-01-01T12:00:00Z"}
        ]
        
        jsonl_file = self.vault_dir / "chat_export.jsonl"
        with open(jsonl_file, 'w') as f:
            for entry in test_data:
                f.write(json.dumps(entry) + '\n')
        
        # Run finalization with write enabled
        finalizer = AlphaOmegaFinalizer(
            vault_dir=str(self.vault_dir),
            outputs_dir=str(self.outputs_dir),
            dry_run=False
        )
        
        merkle_root, ledger_path, root_path = finalizer.finalize()
        
        # Verify results
        assert merkle_root is not None
        assert ledger_path is not None
        assert root_path is not None
        
        # Verify files exist
        assert ledger_path.exists()
        assert root_path.exists()
        
        # Verify ledger content
        with open(ledger_path, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 3  # 3 entries
        
        # Verify each line is valid JSON
        for line in lines:
            entry = json.loads(line.strip())
            assert 'hash' in entry
            assert 'timestamp' in entry
            assert 'data' in entry
        
        # Verify master root content
        with open(root_path, 'r') as f:
            root_content = f.read()
        
        assert merkle_root in root_content
        
        print("✅ Full pipeline (with write) test passed")
    
    def test_verification_success(self):
        """Test successful integrity verification."""
        # Create and finalize test data
        test_data = [
            {"id": 1, "content": "Message 1", "timestamp": "2024-01-01T10:00:00Z"},
            {"id": 2, "content": "Message 2", "timestamp": "2024-01-01T11:00:00Z"}
        ]
        
        json_file = self.vault_dir / "test.json"
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        # Finalize
        finalizer = AlphaOmegaFinalizer(
            vault_dir=str(self.vault_dir),
            outputs_dir=str(self.outputs_dir),
            dry_run=False
        )
        finalizer.finalize()
        
        # Verify
        result = finalizer.verify_integrity()
        
        assert result == True, "Verification should succeed for unmodified ledger"
        
        print("✅ Verification success test passed")
    
    def test_verification_failure_tampered_ledger(self):
        """Test verification failure when ledger is tampered."""
        # Create and finalize test data
        test_data = [
            {"id": 1, "content": "Message 1", "timestamp": "2024-01-01T10:00:00Z"},
            {"id": 2, "content": "Message 2", "timestamp": "2024-01-01T11:00:00Z"}
        ]
        
        json_file = self.vault_dir / "test.json"
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        # Finalize
        finalizer = AlphaOmegaFinalizer(
            vault_dir=str(self.vault_dir),
            outputs_dir=str(self.outputs_dir),
            dry_run=False
        )
        finalizer.finalize()
        
        # Tamper with ledger
        ledger_path = self.outputs_dir / "SOVEREIGN_CONSTITUTION.jsonl"
        with open(ledger_path, 'a') as f:
            tampered_entry = {"id": 999, "content": "Tampered"}
            f.write(json.dumps(tampered_entry) + '\n')
        
        # Verify - should fail
        result = finalizer.verify_integrity()
        
        assert result == False, "Verification should fail for tampered ledger"
        
        print("✅ Verification failure (tampered) test passed")
    
    def test_empty_vault_directory(self):
        """Test handling of empty vault directory."""
        finalizer = AlphaOmegaFinalizer(
            vault_dir=str(self.vault_dir),
            outputs_dir=str(self.outputs_dir),
            dry_run=True
        )
        
        merkle_root, ledger_path, root_path = finalizer.finalize()
        
        # Should handle gracefully
        assert merkle_root is None
        assert ledger_path is None
        assert root_path is None
        
        print("✅ Empty vault test passed")
    
    def test_multiple_files_in_vault(self):
        """Test processing multiple files in vault."""
        # Create multiple test files
        data1 = [{"id": 1, "content": "File 1", "timestamp": "2024-01-01T10:00:00Z"}]
        data2 = [{"id": 2, "content": "File 2", "timestamp": "2024-01-01T11:00:00Z"}]
        data3 = [
            {"id": 3, "content": "File 3 Entry 1", "timestamp": "2024-01-01T12:00:00Z"},
            {"id": 4, "content": "File 3 Entry 2", "timestamp": "2024-01-01T13:00:00Z"}
        ]
        
        with open(self.vault_dir / "file1.json", 'w') as f:
            json.dump(data1, f)
        
        with open(self.vault_dir / "file2.json", 'w') as f:
            json.dump(data2, f)
        
        with open(self.vault_dir / "file3.jsonl", 'w') as f:
            for entry in data3:
                f.write(json.dumps(entry) + '\n')
        
        finalizer = AlphaOmegaFinalizer(
            vault_dir=str(self.vault_dir),
            outputs_dir=str(self.outputs_dir),
            dry_run=True
        )
        
        finalizer.process_vault_directory()
        
        # Should have 4 total entries (1 + 1 + 2)
        assert len(finalizer.ledger_entries) == 4
        
        # Verify source file tracking
        sources = set(entry['source_file'] for entry in finalizer.ledger_entries)
        assert 'file1.json' in sources
        assert 'file2.json' in sources
        assert 'file3.jsonl' in sources
        
        print("✅ Multiple files test passed")


def run_tests():
    """Run all tests."""
    test_suite = TestAlphaOmegaFinalizer()
    
    test_methods = [
        method for method in dir(test_suite)
        if method.startswith('test_') and callable(getattr(test_suite, method))
    ]
    
    print("="*70)
    print("AlphaOmegaFinalizer Test Suite")
    print("="*70)
    print(f"Running {len(test_methods)} tests...\n")
    
    passed = 0
    failed = 0
    errors = []
    
    for test_name in test_methods:
        try:
            test_suite.setup_method()
            try:
                test_method = getattr(test_suite, test_name)
                test_method()
                passed += 1
            except AssertionError as e:
                failed += 1
                errors.append((test_name, str(e)))
                print(f"❌ FAILED: {test_name}")
                print(f"   {e}\n")
            except Exception as e:
                failed += 1
                errors.append((test_name, str(e)))
                print(f"❌ ERROR: {test_name}")
                print(f"   {e}\n")
            finally:
                # Always clean up, even on failure
                test_suite.teardown_method()
        except Exception as e:
            # Setup failed
            failed += 1
            errors.append((test_name, f"Setup failed: {str(e)}"))
            print(f"❌ SETUP ERROR: {test_name}")
            print(f"   {e}\n")
    
    print("="*70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*70)
    
    if errors:
        print("\nFailed tests:")
        for test_name, error in errors:
            print(f"  - {test_name}: {error}")
        return 1
    else:
        print("\n✅ All tests passed!")
        return 0


if __name__ == '__main__':
    sys.exit(run_tests())
