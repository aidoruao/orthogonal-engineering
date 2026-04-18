"""
Tests for forensic commit generator.

Validates JSON schema, SHA-256 commitments, Merkle root computation,
and commit trailer generation.
"""

import json
from fractions import Fraction
from pathlib import Path

import pytest

from audit.forensic_commit import (
    build_forensic_commit,
    generate_commit_trailer,
    write_forensic_commit,
)
from axioms.yeshua_axioms import YeshuaClaim


DEFAULT_THRESHOLDS = {
    "certain": Fraction(247, 1),
    "high_confidence": Fraction(200, 1),
    "probable": Fraction(150, 1),
    "unknown": Fraction(100, 1),
    "suspicious": Fraction(50, 1),
    "invalid": Fraction(0, 1),
}


class TestBuildForensicCommit:
    def test_build_returns_dict(self):
        metadata = {
            "commit_sha": "abc123",
            "timestamp": "2026-01-01T00:00:00Z",
            "authors": ["Test Author"],
            "co_authors": [],
        }
        artifacts = [
            {"path": "/tmp/f1.txt", "size": 100, "sha256": "a" * 64},
        ]
        result = build_forensic_commit(metadata, artifacts, DEFAULT_THRESHOLDS)
        assert isinstance(result, dict)
        assert result["commit_sha"] == "abc123"

    def test_commitment_present(self):
        metadata = {
            "commit_sha": "abc123",
            "timestamp": "2026-01-01T00:00:00Z",
            "authors": ["Test Author"],
            "co_authors": [],
        }
        artifacts = [
            {"path": "/tmp/f1.txt", "size": 100, "sha256": "a" * 64},
        ]
        result = build_forensic_commit(metadata, artifacts, DEFAULT_THRESHOLDS)
        assert "commitment" in result
        assert len(result["commitment"]) == 64

    def test_merkle_root_present(self):
        metadata = {
            "commit_sha": "abc123",
            "timestamp": "2026-01-01T00:00:00Z",
            "authors": ["Test Author"],
            "co_authors": [],
        }
        artifacts = [
            {"path": "/tmp/f1.txt", "size": 100, "sha256": "a" * 64},
        ]
        result = build_forensic_commit(metadata, artifacts, DEFAULT_THRESHOLDS)
        assert "merkle_root" in result
        assert len(result["merkle_root"]) == 64

    def test_artifacts_classified(self):
        metadata = {
            "commit_sha": "abc123",
            "timestamp": "2026-01-01T00:00:00Z",
            "authors": ["Test Author"],
            "co_authors": [],
        }
        artifacts = [
            {"path": "/tmp/f1.txt", "size": 100, "sha256": "a" * 64},
        ]
        result = build_forensic_commit(metadata, artifacts, DEFAULT_THRESHOLDS)
        assert len(result["artifacts"]) == 1
        assert "state_label" in result["artifacts"][0]
        assert "classifier_proof" in result["artifacts"][0]

    def test_top_level_claim_present(self):
        metadata = {
            "commit_sha": "abc123",
            "timestamp": "2026-01-01T00:00:00Z",
            "authors": ["Test Author"],
            "co_authors": [],
        }
        artifacts = [
            {"path": "/tmp/f1.txt", "size": 100, "sha256": "a" * 64},
        ]
        result = build_forensic_commit(metadata, artifacts, DEFAULT_THRESHOLDS)
        assert "top_level_claim" in result
        claim = result["top_level_claim"]
        assert "hash_commitment" in claim
        assert len(claim["hash_commitment"]) == 64

    def test_falsifies_if_present(self):
        metadata = {
            "commit_sha": "abc123",
            "timestamp": "2026-01-01T00:00:00Z",
            "authors": ["Test Author"],
            "co_authors": [],
        }
        artifacts = [
            {"path": "/tmp/f1.txt", "size": 100, "sha256": "a" * 64},
        ]
        result = build_forensic_commit(metadata, artifacts, DEFAULT_THRESHOLDS)
        assert "falsifies_if" in result
        assert isinstance(result["falsifies_if"], str)
        assert len(result["falsifies_if"]) > 0

    def test_thresholds_used(self):
        metadata = {
            "commit_sha": "abc123",
            "timestamp": "2026-01-01T00:00:00Z",
            "authors": ["Test Author"],
            "co_authors": [],
        }
        artifacts = [
            {"path": "/tmp/f1.txt", "size": 100, "sha256": "a" * 64},
        ]
        result = build_forensic_commit(metadata, artifacts, DEFAULT_THRESHOLDS)
        assert "thresholds_used" in result
        assert result["thresholds_used"]["certain"] == "247"

    def test_commitment_matches_payload(self):
        metadata = {
            "commit_sha": "abc123",
            "timestamp": "2026-01-01T00:00:00Z",
            "authors": ["Test Author"],
            "co_authors": [],
        }
        artifacts = [
            {"path": "/tmp/f1.txt", "size": 100, "sha256": "a" * 64},
        ]
        result = build_forensic_commit(metadata, artifacts, DEFAULT_THRESHOLDS)
        # Recompute commitment without the commitment field itself
        from audit.forensic_commit import _compute_commitment
        payload = {k: v for k, v in result.items() if k != "commitment"}
        recomputed = _compute_commitment(payload)
        assert result["commitment"] == recomputed


class TestWriteForensicCommit:
    def test_writes_file(self, tmp_path):
        metadata = {
            "commit_sha": "def456",
            "timestamp": "2026-01-01T00:00:00Z",
            "authors": ["Test Author"],
            "co_authors": [],
        }
        artifacts = [
            {"path": "/tmp/f1.txt", "size": 100, "sha256": "a" * 64},
        ]
        forensic_obj = build_forensic_commit(metadata, artifacts, DEFAULT_THRESHOLDS)
        dest = tmp_path / "forensic"
        filepath = write_forensic_commit(forensic_obj, str(dest))
        assert Path(filepath).exists()
        with open(filepath) as f:
            loaded = json.load(f)
        assert loaded["commit_sha"] == "def456"


class TestGenerateCommitTrailer:
    def test_trailer_contains_key_fields(self):
        metadata = {
            "commit_sha": "ghi789",
            "timestamp": "2026-01-01T00:00:00Z",
            "authors": ["Test Author"],
            "co_authors": [],
        }
        artifacts = [
            {"path": "/tmp/f1.txt", "size": 100, "sha256": "a" * 64},
        ]
        forensic_obj = build_forensic_commit(metadata, artifacts, DEFAULT_THRESHOLDS)
        trailer = generate_commit_trailer(forensic_obj)
        assert "Forensic-Commit:" in trailer
        assert "Forensic-Merkle-Root:" in trailer
        assert "Forensic-Commitment:" in trailer
