"""
tests/test_global_merkle.py — Tests for global Merkle root generation

Author: Orthogonal Engineering
PR: #34
Version: 1.0.0
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from merkle.global_merkle import build_global_merkle

REPO_ROOT = Path(__file__).parent.parent


def test_build_global_merkle_returns_tuple():
    root, count = build_global_merkle()
    assert isinstance(root, str)
    assert isinstance(count, int)


def test_global_merkle_root_is_64_hex():
    root, _ = build_global_merkle()
    assert len(root) == 64
    assert all(c in "0123456789abcdef" for c in root)


def test_global_merkle_file_count_positive():
    _, count = build_global_merkle()
    assert count > 0


def test_global_merkle_deterministic():
    r1, c1 = build_global_merkle()
    r2, c2 = build_global_merkle()
    assert r1 == r2
    assert c1 == c2


def test_global_root_json_exists():
    global_root = REPO_ROOT / "merkle" / "global_root.json"
    assert global_root.exists(), "merkle/global_root.json must exist"


def test_global_root_json_has_required_fields():
    global_root = REPO_ROOT / "merkle" / "global_root.json"
    if not global_root.exists():
        pytest.skip("global_root.json not yet generated")
    data = json.loads(global_root.read_text(encoding="utf-8"))
    assert "root_hash" in data
    assert "file_count" in data
    assert "hash_algorithm" in data
    assert data["hash_algorithm"] == "SHA-256"
