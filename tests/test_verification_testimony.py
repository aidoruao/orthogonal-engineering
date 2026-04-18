"""
Tests for verification-as-testimony runner.

Validates evidence directory creation, attestations.json structure,
YeshuaClaim wrapping, and commitment computation.
"""

import json
from fractions import Fraction
from pathlib import Path

import pytest

from audit.verification_testimony import run_verifications
from axioms.logic import ProofObject
from axioms.yeshua_axioms import YeshuaClaim


class TestRunVerifications:
    def test_runs_tasks_and_returns_success(self, tmp_path):
        def task_pass():
            return True, ProofObject(
                rule="Pass",
                premises=["p"],
                conclusion="c",
                falsifies_if="false",
            )

        success, claim = run_verifications(
            verification_tasks=[task_pass],
            thresholds={},
            out_dir=str(tmp_path / "evidence"),
        )
        assert success is True
        assert isinstance(claim, YeshuaClaim)
        assert claim.is_hash_anchored()
        assert claim.is_reproducible()

    def test_runs_tasks_and_returns_failure(self, tmp_path):
        def task_fail():
            return False, ProofObject(
                rule="Fail",
                premises=["p"],
                conclusion="c",
                falsifies_if="true",
            )

        success, claim = run_verifications(
            verification_tasks=[task_fail],
            thresholds={},
            out_dir=str(tmp_path / "evidence"),
        )
        assert success is False

    def test_writes_attestations_json(self, tmp_path):
        def task_pass():
            return True, ProofObject(
                rule="Pass",
                premises=["p"],
                conclusion="c",
                falsifies_if="false",
            )

        out_dir = tmp_path / "evidence"
        run_verifications(
            verification_tasks=[task_pass],
            thresholds={},
            out_dir=str(out_dir),
        )
        attestations_path = out_dir / "attestations.json"
        assert attestations_path.exists()
        with open(attestations_path) as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]["task"] == "task_pass"
        assert data[0]["success"] is True
        assert "falsifies_if" in data[0]
        assert "claim" in data[0]

    def test_writes_commitment_file(self, tmp_path):
        def task_pass():
            return True, ProofObject(
                rule="Pass",
                premises=["p"],
                conclusion="c",
                falsifies_if="false",
            )

        out_dir = tmp_path / "evidence"
        run_verifications(
            verification_tasks=[task_pass],
            thresholds={},
            out_dir=str(out_dir),
        )
        commitment_path = out_dir / "commitment.txt"
        assert commitment_path.exists()
        commitment = commitment_path.read_text().strip()
        assert len(commitment) == 64

    def test_writes_summary_json(self, tmp_path):
        def task_pass():
            return True, ProofObject(
                rule="Pass",
                premises=["p"],
                conclusion="c",
                falsifies_if="false",
            )

        out_dir = tmp_path / "evidence"
        run_verifications(
            verification_tasks=[task_pass],
            thresholds={},
            out_dir=str(out_dir),
        )
        summary_path = out_dir / "summary.json"
        assert summary_path.exists()
        with open(summary_path) as f:
            data = json.load(f)
        assert data["overall_success"] is True
        assert data["task_count"] == 1
        assert "merkle_root" in data
        assert "commitment" in data
        assert "falsifies_if" in data

    def test_multiple_tasks(self, tmp_path):
        def task_a():
            return True, ProofObject(
                rule="A", premises=["p"], conclusion="c", falsifies_if="false"
            )

        def task_b():
            return False, ProofObject(
                rule="B", premises=["p"], conclusion="c", falsifies_if="true"
            )

        success, claim = run_verifications(
            verification_tasks=[task_a, task_b],
            thresholds={},
            out_dir=str(tmp_path / "evidence"),
        )
        assert success is False
        attestations_path = tmp_path / "evidence" / "attestations.json"
        with open(attestations_path) as f:
            data = json.load(f)
        assert len(data) == 2

    def test_top_level_claim_derivation_valid(self, tmp_path):
        def task_pass():
            return True, ProofObject(
                rule="Pass",
                premises=["p"],
                conclusion="c",
                falsifies_if="false",
            )

        success, claim = run_verifications(
            verification_tasks=[task_pass],
            thresholds={},
            out_dir=str(tmp_path / "evidence"),
        )
        assert claim.derivation.is_valid()
        assert claim.derivation.falsifies_if is not None
