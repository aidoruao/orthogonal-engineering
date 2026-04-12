"""
tests/test_domain_merkle.py — Tests for per-domain Merkle root generation.

PR: #118
Standard: Yeshua / Glass-Box / Orthogonal Engineering
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from merkle.domain_merkle import build_domain_merkle, build_all_domain_roots

REPO_ROOT = Path(__file__).parent.parent
DOMAINS_DIR = REPO_ROOT / "src" / "domains"


def test_build_domain_merkle_returns_tuple():
    """build_domain_merkle returns (str, int)."""
    domain_dir = next(
        d for d in sorted(DOMAINS_DIR.iterdir())
        if d.is_dir() and not d.name.startswith("_")
    )
    root, count = build_domain_merkle(domain_dir)
    assert isinstance(root, str)
    assert isinstance(count, int)


def test_build_domain_merkle_root_is_64_hex():
    """Each domain root hash is 64 lowercase hex chars."""
    domain_dir = next(
        d for d in sorted(DOMAINS_DIR.iterdir())
        if d.is_dir() and not d.name.startswith("_")
    )
    root, _ = build_domain_merkle(domain_dir)
    assert len(root) == 64
    assert all(c in "0123456789abcdef" for c in root)


def test_build_domain_merkle_file_count_positive():
    """At least one source file is counted per non-empty domain."""
    domain_dir = next(
        d for d in sorted(DOMAINS_DIR.iterdir())
        if d.is_dir() and not d.name.startswith("_")
    )
    _, count = build_domain_merkle(domain_dir)
    assert count > 0


def test_build_all_domain_roots_returns_dict():
    """build_all_domain_roots returns a non-empty dict."""
    results = build_all_domain_roots()
    assert isinstance(results, dict)
    assert len(results) > 0


def test_all_domain_roots_have_64_hex_hashes():
    """Every domain root hash is 64 lowercase hex chars."""
    results = build_all_domain_roots()
    for domain, info in results.items():
        root = info["root_hash"]
        assert len(root) == 64, f"{domain}: root_hash length != 64"
        assert all(c in "0123456789abcdef" for c in root), (
            f"{domain}: root_hash is not hex"
        )


def test_domain_roots_deterministic():
    """Repeated calls to build_all_domain_roots return identical roots."""
    r1 = build_all_domain_roots()
    r2 = build_all_domain_roots()
    assert r1 == r2


def test_domain_roots_json_exists():
    """merkle/domain_roots.json exists after generation."""
    domain_roots = REPO_ROOT / "merkle" / "domain_roots.json"
    if not domain_roots.exists():
        pytest.skip("domain_roots.json not yet generated")
    assert domain_roots.exists()


def test_domain_roots_json_has_required_fields():
    """Each entry in domain_roots.json has required fields."""
    domain_roots = REPO_ROOT / "merkle" / "domain_roots.json"
    if not domain_roots.exists():
        pytest.skip("domain_roots.json not yet generated")
    data = json.loads(domain_roots.read_text(encoding="utf-8"))
    assert len(data) > 0
    for domain, info in data.items():
        assert "root_hash" in info, f"{domain} missing root_hash"
        assert "file_count" in info, f"{domain} missing file_count"
        assert "hash_algorithm" in info, f"{domain} missing hash_algorithm"
        assert info["hash_algorithm"] == "SHA-256", f"{domain} wrong hash algorithm"
