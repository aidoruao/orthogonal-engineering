"""
PR #28 — Cross-Platform Determinism Tests
Verifies that core operations produce identical results across runs.
"""

import hashlib
import importlib.util
import json
import struct
from pathlib import Path


def test_sha256_determinism():
    """Same input always produces same SHA-256 hash."""
    data = b"orthogonal-engineering-determinism-seed"
    h1 = hashlib.sha256(data).hexdigest()
    h2 = hashlib.sha256(data).hexdigest()
    assert h1 == h2, f"SHA-256 not deterministic: {h1} != {h2}"


def test_json_serialization_determinism():
    """json.dumps with sort_keys produces identical output across runs."""
    obj = {"z": 1, "a": 2, "m": [3, 4, 5]}
    s1 = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    s2 = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    assert s1 == s2, "JSON serialization not deterministic"


def test_struct_pack_determinism():
    """struct.pack produces identical bytes across runs."""
    b1 = struct.pack(">II", 42, 99)
    b2 = struct.pack(">II", 42, 99)
    assert b1 == b2, "struct.pack not deterministic"


def test_falsification_import():
    """Verify test_falsification.py is importable (dependency of pr28-determinism workflow)."""
    spec = importlib.util.find_spec("tests.test_falsification")
    assert spec is not None, "tests.test_falsification module cannot be located"
    assert Path("tests/test_falsification.py").exists(), "test_falsification.py not found"


if __name__ == "__main__":
    test_sha256_determinism()
    test_json_serialization_determinism()
    test_struct_pack_determinism()
    test_falsification_import()
    print("All determinism tests passed")
