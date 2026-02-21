"""
Tests for EvidenceManager — tests/test_evidence_manager.py

Validates that EvidenceManager produces a deterministic Merkle root
("Omega invariant hash") for a set of files, and that the root changes
when any file changes.

Author: Orthogonal Engineering
PR: #32
Version: 1.0.0
"""

import hashlib
import json
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from toolkit.oe.evidence_manager import EvidenceManager


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_repo(tmp_path: Path, files: dict) -> Path:
    """Create a temporary repo directory with the given files."""
    for rel, content in files.items():
        dest = tmp_path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, str):
            dest.write_text(content, encoding="utf-8")
        else:
            dest.write_bytes(content)
    return tmp_path


# ---------------------------------------------------------------------------
# Basic tests
# ---------------------------------------------------------------------------


def test_omega_root_is_64_char_hex(tmp_path):
    """compute_omega_root() returns a 64-character lowercase hex string."""
    make_repo(tmp_path, {"README.md": "Hello"})
    em = EvidenceManager(repo_root=tmp_path)
    root = em.compute_omega_root()
    assert isinstance(root, str)
    assert len(root) == 64
    assert root == root.lower()
    assert all(c in "0123456789abcdef" for c in root)


def test_omega_root_deterministic(tmp_path):
    """compute_omega_root() returns the same value on repeated calls."""
    make_repo(tmp_path, {"a.txt": "alpha", "b.txt": "beta"})
    em = EvidenceManager(repo_root=tmp_path)
    root1 = em.compute_omega_root()
    em2 = EvidenceManager(repo_root=tmp_path)
    root2 = em2.compute_omega_root()
    assert root1 == root2


def test_omega_root_changes_when_file_changes(tmp_path):
    """Omega root changes when a file's content changes."""
    make_repo(tmp_path, {"file.txt": "original content"})
    em1 = EvidenceManager(repo_root=tmp_path)
    root1 = em1.compute_omega_root()

    # Modify the file
    (tmp_path / "file.txt").write_text("modified content", encoding="utf-8")
    em2 = EvidenceManager(repo_root=tmp_path)
    root2 = em2.compute_omega_root()

    assert root1 != root2


def test_omega_root_changes_when_file_added(tmp_path):
    """Omega root changes when a new file is added."""
    make_repo(tmp_path, {"existing.txt": "data"})
    em1 = EvidenceManager(repo_root=tmp_path)
    root1 = em1.compute_omega_root()

    (tmp_path / "new_file.txt").write_text("new", encoding="utf-8")
    em2 = EvidenceManager(repo_root=tmp_path)
    root2 = em2.compute_omega_root()

    assert root1 != root2


def test_empty_repo_produces_root(tmp_path):
    """EvidenceManager handles an empty directory without crashing."""
    em = EvidenceManager(repo_root=tmp_path)
    root = em.compute_omega_root()
    assert isinstance(root, str)
    assert len(root) == 64


def test_single_file_root(tmp_path):
    """Single-file repo produces a valid root."""
    make_repo(tmp_path, {"only.txt": "hello world"})
    em = EvidenceManager(repo_root=tmp_path)
    root = em.compute_omega_root()
    assert len(root) == 64


def test_multiple_files_root(tmp_path):
    """Multi-file repo produces a valid root."""
    make_repo(tmp_path, {
        "a.txt": "alpha",
        "b.txt": "beta",
        "c.txt": "gamma",
        "sub/d.txt": "delta",
    })
    em = EvidenceManager(repo_root=tmp_path)
    root = em.compute_omega_root()
    assert len(root) == 64


# ---------------------------------------------------------------------------
# Canonicality — order independence
# ---------------------------------------------------------------------------


def test_root_independent_of_insertion_order(tmp_path):
    """Root is the same regardless of the order files are discovered."""
    make_repo(tmp_path, {
        "z.txt": "zeta",
        "a.txt": "alpha",
        "m.txt": "mu",
    })
    em = EvidenceManager(repo_root=tmp_path)
    root = em.compute_omega_root()

    # The tree sorts leaves by canonical path, so order of file creation
    # must not matter.  We check determinism: same root on second call.
    em2 = EvidenceManager(repo_root=tmp_path)
    assert em2.compute_omega_root() == root


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


def test_generate_report_structure(tmp_path):
    """generate_report() returns a dict with expected keys."""
    make_repo(tmp_path, {"README.md": "# Test"})
    em = EvidenceManager(repo_root=tmp_path)
    report = em.generate_report()

    assert "timestamp" in report
    assert "repo_root" in report
    assert "omega_root" in report
    assert "file_count" in report
    assert "files" in report
    assert report["file_count"] == 1
    assert len(report["files"]) == 1


def test_generate_report_file_entries(tmp_path):
    """File entries in the report have 'path' and 'hash' keys."""
    make_repo(tmp_path, {"doc.txt": "content"})
    em = EvidenceManager(repo_root=tmp_path)
    report = em.generate_report()

    for entry in report["files"]:
        assert "path" in entry
        assert "hash" in entry
        assert len(entry["hash"]) == 64


def test_generate_report_json_serialisable(tmp_path):
    """generate_report() returns a JSON-serialisable dict."""
    make_repo(tmp_path, {"data.json": '{"key": "value"}'})
    em = EvidenceManager(repo_root=tmp_path)
    report = em.generate_report()
    # Should not raise
    json.dumps(report)


# ---------------------------------------------------------------------------
# Inclusion proof
# ---------------------------------------------------------------------------


def test_get_inclusion_proof(tmp_path):
    """get_inclusion_proof returns a valid proof for a file in the tree."""
    make_repo(tmp_path, {"file.txt": "data", "other.txt": "more"})
    em = EvidenceManager(repo_root=tmp_path)
    em.compute_omega_root()

    proof = em.get_inclusion_proof("file.txt")
    assert "path" in proof
    assert "leaf_hash" in proof
    assert "proof" in proof
    assert "root" in proof


def test_get_inclusion_proof_invalid_path(tmp_path):
    """get_inclusion_proof raises ValueError for a file not in tree."""
    make_repo(tmp_path, {"exists.txt": "data"})
    em = EvidenceManager(repo_root=tmp_path)
    em.compute_omega_root()

    with pytest.raises(ValueError):
        em.get_inclusion_proof("nonexistent.txt")


# ---------------------------------------------------------------------------
# Exclusion patterns
# ---------------------------------------------------------------------------


def test_excludes_pyc_files(tmp_path):
    """EvidenceManager excludes .pyc files by default."""
    make_repo(tmp_path, {
        "module.py": "x = 1",
        "module.pyc": b"\x00\x01\x02",
    })
    em = EvidenceManager(repo_root=tmp_path)
    em.compute_omega_root()

    # .pyc should not appear in the leaves
    canon_paths = [p for p, _ in em._tree.leaves]
    assert not any(p.endswith(".pyc") for p in canon_paths)


def test_excludes_custom_dirs(tmp_path):
    """EvidenceManager respects custom exclude_dirs."""
    make_repo(tmp_path, {
        "src/code.py": "x = 1",
        "excluded_dir/secret.txt": "secret",
    })
    em = EvidenceManager(
        repo_root=tmp_path,
        exclude_dirs=frozenset({"excluded_dir"}),
    )
    em.compute_omega_root()

    canon_paths = [p for p, _ in em._tree.leaves]
    assert not any("excluded_dir" in p for p in canon_paths)
    assert any("src" in p for p in canon_paths)
