#!/usr/bin/env python3
"""
Unit tests for AlphaOmegaFinalizer

Tests cover:
- Time normalization
- Canonical bytes generation
- Redaction hooks
- Fingerprinting
- Merkle root generation
- Finalization workflow (dry-run)
- Integrity verification

Uses synthetic test data only - no real user exports.
"""

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from core.alpha_omega_finalizer import (
    AlphaOmegaFinalizer,
    canonical_bytes,
    fingerprint_sha256,
    fingerprint_hmac_sha256,
    generate_merkle_root,
    normalize_time,
    simple_redact_hook,
)


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def temp_vault(tmp_path):
    """Create a temporary vault directory with synthetic test data."""
    vault = tmp_path / "vault"
    vault.mkdir()
    
    # Create synthetic test files
    test_data_1 = {
        "id": "test_001",
        "timestamp": 1704067200,  # 2024-01-01 00:00:00 UTC
        "content": "This is a test message",
        "user": "test_user@example.com"
    }
    
    test_data_2 = {
        "id": "test_002",
        "timestamp": "2024-01-02T00:00:00Z",
        "content": "Another test message",
        "password": "secret123"
    }
    
    test_data_list = [
        {"id": "item_001", "value": 100},
        {"id": "item_002", "value": 200},
    ]
    
    # Write test files
    (vault / "test_export_1.json").write_text(json.dumps(test_data_1, indent=2))
    (vault / "test_export_2.json").write_text(json.dumps(test_data_2, indent=2))
    (vault / "test_export_list.json").write_text(json.dumps(test_data_list, indent=2))
    
    return vault


@pytest.fixture
def temp_output(tmp_path):
    """Create a temporary output directory."""
    output = tmp_path / "outputs"
    output.mkdir()
    return output


# ============================================================================
# TIME NORMALIZATION TESTS
# ============================================================================

def test_normalize_time_unix_epoch():
    """Test normalization of Unix epoch timestamp."""
    timestamp = 1704067200  # 2024-01-01 00:00:00 UTC
    result = normalize_time(timestamp)
    assert result.startswith('2024-01-01')
    assert '+00:00' in result or 'Z' in result.replace('+00:00', 'Z')


def test_normalize_time_iso_string():
    """Test normalization of ISO 8601 string."""
    timestamp = "2024-01-01T00:00:00Z"
    result = normalize_time(timestamp)
    assert result.startswith('2024-01-01')
    assert '+00:00' in result


def test_normalize_time_datetime_object():
    """Test normalization of datetime object."""
    timestamp = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    result = normalize_time(timestamp)
    assert result.startswith('2024-01-01')
    assert '+00:00' in result


def test_normalize_time_with_fallback():
    """Test fallback for unparseable timestamp."""
    fallback = "2024-01-01T00:00:00+00:00"
    result = normalize_time("invalid_timestamp", fallback_epoch=fallback)
    assert result == fallback


def test_normalize_time_none_with_fallback():
    """Test None timestamp with fallback."""
    fallback = "2024-01-01T00:00:00+00:00"
    result = normalize_time(None, fallback_epoch=fallback)
    assert result == fallback


# ============================================================================
# CANONICAL BYTES TESTS
# ============================================================================

def test_canonical_bytes_deterministic():
    """Test that canonical bytes are deterministic for same data."""
    data = {"b": 2, "a": 1, "c": 3}
    
    result1 = canonical_bytes(data)
    result2 = canonical_bytes(data)
    
    assert result1 == result2


def test_canonical_bytes_sorted_keys():
    """Test that canonical bytes use sorted keys."""
    data = {"z": 1, "a": 2}
    result = canonical_bytes(data)
    
    # Should be ordered as {"a": 2, "z": 1}
    assert result == b'{"a":2,"z":1}'


def test_canonical_bytes_nested():
    """Test canonical bytes with nested structures."""
    data = {
        "outer": {
            "z": 1,
            "a": 2
        },
        "list": [3, 2, 1]
    }
    
    result1 = canonical_bytes(data)
    result2 = canonical_bytes(data)
    
    assert result1 == result2
    # Keys should be sorted
    assert b'"outer"' in result1
    assert b'"list"' in result1


# ============================================================================
# REDACTION HOOK TESTS
# ============================================================================

def test_simple_redact_hook_password():
    """Test that password fields are redacted."""
    data = {
        "username": "test_user",
        "password": "secret123",
        "api_password": "another_secret"
    }
    
    redacted = simple_redact_hook(data)
    
    assert redacted["username"] == "test_user"
    assert redacted["password"] == "[REDACTED]"
    assert redacted["api_password"] == "[REDACTED]"


def test_simple_redact_hook_email():
    """Test that email addresses are redacted."""
    data = {
        "message": "Contact me at user@example.com for details"
    }
    
    redacted = simple_redact_hook(data)
    
    assert "user@example.com" not in redacted["message"]
    assert "[EMAIL_REDACTED]" in redacted["message"]


def test_simple_redact_hook_deterministic():
    """Test that redaction is deterministic."""
    data = {
        "password": "secret",
        "email": "test@example.com"
    }
    
    result1 = simple_redact_hook(data)
    result2 = simple_redact_hook(data)
    
    assert result1 == result2


# ============================================================================
# FINGERPRINTING TESTS
# ============================================================================

def test_fingerprint_sha256_deterministic():
    """Test SHA-256 fingerprinting is deterministic."""
    data = b"test data"
    
    fp1 = fingerprint_sha256(data)
    fp2 = fingerprint_sha256(data)
    
    assert fp1 == fp2
    assert len(fp1) == 64  # SHA-256 produces 64 hex characters


def test_fingerprint_sha256_different_data():
    """Test that different data produces different fingerprints."""
    data1 = b"test data 1"
    data2 = b"test data 2"
    
    fp1 = fingerprint_sha256(data1)
    fp2 = fingerprint_sha256(data2)
    
    assert fp1 != fp2


def test_fingerprint_hmac_sha256_with_key():
    """Test HMAC-SHA256 fingerprinting."""
    data = b"test data"
    key = b"secret_key"
    
    fp1 = fingerprint_hmac_sha256(data, key)
    fp2 = fingerprint_hmac_sha256(data, key)
    
    assert fp1 == fp2
    assert len(fp1) == 64


def test_fingerprint_hmac_sha256_different_keys():
    """Test that different keys produce different fingerprints."""
    data = b"test data"
    key1 = b"key1"
    key2 = b"key2"
    
    fp1 = fingerprint_hmac_sha256(data, key1)
    fp2 = fingerprint_hmac_sha256(data, key2)
    
    assert fp1 != fp2


# ============================================================================
# MERKLE ROOT TESTS
# ============================================================================

def test_generate_merkle_root_empty():
    """Test Merkle root generation with empty list."""
    result = generate_merkle_root([])
    
    # Should return hash of empty string
    assert len(result) == 64


def test_generate_merkle_root_single():
    """Test Merkle root generation with single fingerprint."""
    fingerprints = ["abc123"]
    result = generate_merkle_root(fingerprints)
    
    # Single fingerprint is returned as-is
    assert result == "abc123"


def test_generate_merkle_root_pair():
    """Test Merkle root generation with pair of fingerprints."""
    fingerprints = ["abc", "def"]
    result = generate_merkle_root(fingerprints)
    
    assert len(result) == 64
    # Should be deterministic
    assert result == generate_merkle_root(fingerprints)


def test_generate_merkle_root_deterministic():
    """Test Merkle root is deterministic."""
    fingerprints = ["fp1", "fp2", "fp3", "fp4"]
    
    result1 = generate_merkle_root(fingerprints)
    result2 = generate_merkle_root(fingerprints)
    
    assert result1 == result2


def test_generate_merkle_root_order_matters():
    """Test that fingerprint order affects Merkle root."""
    fp1 = generate_merkle_root(["a", "b", "c"])
    fp2 = generate_merkle_root(["c", "b", "a"])
    
    # Order matters - different order should give different root
    assert fp1 != fp2


# ============================================================================
# FINALIZER INITIALIZATION TESTS
# ============================================================================

def test_finalizer_init_default_dry_run(temp_vault, temp_output):
    """Test that finalizer defaults to dry-run mode."""
    finalizer = AlphaOmegaFinalizer(
        vault_dir=temp_vault,
        out_dir=temp_output
    )
    
    assert finalizer.dry_run is True
    assert finalizer.vault_dir == temp_vault
    assert finalizer.out_dir == temp_output


def test_finalizer_init_vault_not_exists(temp_output):
    """Test that finalizer raises error if vault doesn't exist."""
    with pytest.raises(ValueError, match="Vault directory does not exist"):
        AlphaOmegaFinalizer(
            vault_dir="/nonexistent/path",
            out_dir=temp_output
        )


def test_finalizer_init_with_redaction(temp_vault, temp_output):
    """Test finalizer initialization with redaction hook."""
    finalizer = AlphaOmegaFinalizer(
        vault_dir=temp_vault,
        out_dir=temp_output,
        redact_hook=simple_redact_hook
    )
    
    assert finalizer.redact_hook is not None


def test_finalizer_init_with_hmac_key(temp_vault, temp_output):
    """Test finalizer initialization with HMAC key."""
    finalizer = AlphaOmegaFinalizer(
        vault_dir=temp_vault,
        out_dir=temp_output,
        hmac_key=b"test_key"
    )
    
    assert finalizer.hmac_key == b"test_key"


# ============================================================================
# FILE PROCESSING TESTS
# ============================================================================

def test_process_file_basic(temp_vault, temp_output):
    """Test basic file processing."""
    finalizer = AlphaOmegaFinalizer(
        vault_dir=temp_vault,
        out_dir=temp_output
    )
    
    file_path = temp_vault / "test_export_1.json"
    result = finalizer.process_file(file_path)
    
    assert result['file'] == 'test_export_1.json'
    assert 'fingerprint' in result
    assert len(result['fingerprint']) == 64
    assert result['size_bytes'] > 0
    assert result['redacted'] is False


def test_process_file_with_redaction(temp_vault, temp_output):
    """Test file processing with redaction."""
    finalizer = AlphaOmegaFinalizer(
        vault_dir=temp_vault,
        out_dir=temp_output,
        redact_hook=simple_redact_hook
    )
    
    file_path = temp_vault / "test_export_2.json"
    result = finalizer.process_file(file_path)
    
    assert result['redacted'] is True
    assert 'fingerprint' in result


def test_process_file_deterministic(temp_vault, temp_output):
    """Test that processing same file produces same fingerprint."""
    finalizer = AlphaOmegaFinalizer(
        vault_dir=temp_vault,
        out_dir=temp_output
    )
    
    file_path = temp_vault / "test_export_1.json"
    
    result1 = finalizer.process_file(file_path)
    result2 = finalizer.process_file(file_path)
    
    assert result1['fingerprint'] == result2['fingerprint']


# ============================================================================
# FINALIZATION TESTS
# ============================================================================

def test_finalize_eternity_dry_run(temp_vault, temp_output):
    """Test finalization in dry-run mode."""
    finalizer = AlphaOmegaFinalizer(
        vault_dir=temp_vault,
        out_dir=temp_output,
        dry_run=True
    )
    
    result = finalizer.finalize_eternity()
    
    assert result['success'] is True
    assert result['dry_run'] is True
    assert 'merkle_root' in result
    assert 'anchors' in result
    assert result['anchors']['total_files'] == 3  # 3 test files
    
    # Verify no files written in dry-run
    assert not (temp_output / 'finalization_ledger.json').exists()
    assert not (temp_output / 'master_root.txt').exists()


def test_finalize_eternity_apply_mode(temp_vault, temp_output):
    """Test finalization in apply mode."""
    finalizer = AlphaOmegaFinalizer(
        vault_dir=temp_vault,
        out_dir=temp_output,
        dry_run=False
    )
    
    result = finalizer.finalize_eternity()
    
    assert result['success'] is True
    assert result['dry_run'] is False
    assert 'merkle_root' in result
    
    # Verify files written in apply mode
    assert (temp_output / 'finalization_ledger.json').exists()
    assert (temp_output / 'master_root.txt').exists()
    
    # Verify ledger content
    with open(temp_output / 'finalization_ledger.json', 'r') as f:
        ledger = json.load(f)
    
    assert ledger['merkle_root'] == result['merkle_root']
    assert ledger['total_files'] == 3
    
    # Verify master root content
    with open(temp_output / 'master_root.txt', 'r') as f:
        master_root = f.read().strip()
    
    assert master_root == result['merkle_root']


def test_finalize_eternity_specific_files(temp_vault, temp_output):
    """Test finalization with specific files."""
    finalizer = AlphaOmegaFinalizer(
        vault_dir=temp_vault,
        out_dir=temp_output,
        dry_run=True
    )
    
    result = finalizer.finalize_eternity(files=['test_export_1.json'])
    
    assert result['success'] is True
    assert result['anchors']['total_files'] == 1


def test_finalize_eternity_reproducible(temp_vault, temp_output):
    """Test that finalization produces reproducible results."""
    finalizer = AlphaOmegaFinalizer(
        vault_dir=temp_vault,
        out_dir=temp_output,
        dry_run=True
    )
    
    result1 = finalizer.finalize_eternity()
    result2 = finalizer.finalize_eternity()
    
    # Merkle roots should match (deterministic)
    assert result1['merkle_root'] == result2['merkle_root']


# ============================================================================
# INTEGRITY VERIFICATION TESTS
# ============================================================================

def test_verify_integrity_success(temp_vault, temp_output):
    """Test successful integrity verification."""
    # First, finalize in apply mode
    finalizer = AlphaOmegaFinalizer(
        vault_dir=temp_vault,
        out_dir=temp_output,
        dry_run=False
    )
    
    finalizer.finalize_eternity()
    
    # Now verify
    ledger_path = temp_output / 'finalization_ledger.json'
    success = finalizer.verify_integrity(ledger_path)
    
    assert success is True


def test_verify_integrity_tampered_file(temp_vault, temp_output):
    """Test integrity verification with tampered file."""
    # First, finalize in apply mode
    finalizer = AlphaOmegaFinalizer(
        vault_dir=temp_vault,
        out_dir=temp_output,
        dry_run=False
    )
    
    finalizer.finalize_eternity()
    
    # Tamper with a file
    tampered_file = temp_vault / 'test_export_1.json'
    tampered_file.write_text(json.dumps({"tampered": "data"}))
    
    # Verify should fail
    ledger_path = temp_output / 'finalization_ledger.json'
    success = finalizer.verify_integrity(ledger_path)
    
    assert success is False


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

def test_finalize_no_files(temp_output):
    """Test finalization with no files in vault."""
    empty_vault = temp_output / "empty_vault"
    empty_vault.mkdir()
    
    finalizer = AlphaOmegaFinalizer(
        vault_dir=empty_vault,
        out_dir=temp_output,
        dry_run=True
    )
    
    result = finalizer.finalize_eternity()
    
    assert result['success'] is False
    assert 'error' in result


def test_canonical_bytes_with_unicode():
    """Test canonical bytes with Unicode characters."""
    data = {"text": "Hello 世界 🌍"}
    
    result = canonical_bytes(data)
    
    assert isinstance(result, bytes)
    # Should be deterministic
    assert result == canonical_bytes(data)


def test_normalize_time_float_epoch():
    """Test normalize_time with float epoch."""
    timestamp = 1704067200.5
    result = normalize_time(timestamp)
    
    assert result.startswith('2024-01-01')


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_full_workflow_dry_run(temp_vault, temp_output):
    """Test complete workflow in dry-run mode."""
    finalizer = AlphaOmegaFinalizer(
        vault_dir=temp_vault,
        out_dir=temp_output,
        redact_hook=simple_redact_hook,
        fallback_epoch="2024-01-01T00:00:00+00:00",
        dry_run=True
    )
    
    result = finalizer.finalize_eternity()
    
    assert result['success'] is True
    assert result['dry_run'] is True
    assert len(result['merkle_root']) == 64
    assert result['ledger']['redaction_enabled'] is True
    assert result['ledger']['total_files'] == 3


def test_full_workflow_with_hmac(temp_vault, temp_output):
    """Test complete workflow with HMAC fingerprinting."""
    finalizer = AlphaOmegaFinalizer(
        vault_dir=temp_vault,
        out_dir=temp_output,
        hmac_key=b"test_hmac_key",
        dry_run=False
    )
    
    result = finalizer.finalize_eternity()
    
    assert result['success'] is True
    assert result['ledger']['hmac_enabled'] is True
    
    # Verify integrity
    ledger_path = temp_output / 'finalization_ledger.json'
    success = finalizer.verify_integrity(ledger_path)
    assert success is True
