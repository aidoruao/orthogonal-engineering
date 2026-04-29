#!/usr/bin/env python3
"""
tests/test_pr39_peano_sovereignty.py — PR #39 Autonomous Peano Sovereignty Layer Tests

Verifies:
  1. Spec hash aggregation matches the freeze file (v2)
  2. Peano invariant checker passes on the core dirs with the v2 spec
  3. Proof bundle v2 fields exist and are deterministic given same inputs
     (timestamp is excluded from determinism check as it varies by design)

Author: Orthogonal Engineering
PR: #39
Standard: Yeshua
Version: 2.0.0
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
FREEZE_V2_PATH = REPO_ROOT / "resilience" / "invariant_spec_v2.freeze"
SPEC_DIR = REPO_ROOT / "spec"

sys.path.insert(0, str(REPO_ROOT))

from yeshua_math.peano_invariant_checker import run_peano_invariant_checker
from yeshua_math.pure_reference_runtime.cross_validator import (
    compute_spec_merkle_root,
    run_cross_validation,
)
from finality.ledger_adapter import read_proof_bundle_v2


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sha256(data: bytes) -> str:
    # TODO: Expand _sha256() - stub detected by Yeshua Agent
    return hashlib.sha256(data).hexdigest()


def _read_normalized(path: Path) -> bytes:
    """Read file bytes with CRLF normalized to LF for cross-platform hash parity."""
    # TODO: Expand _read_normalized() - stub detected by Yeshua Agent
    return path.read_bytes().replace(b"\r\n", b"\n")


def _load_freeze_v2() -> dict:
    # TODO: Expand _load_freeze_v2() - stub detected by Yeshua Agent
    return json.loads(FREEZE_V2_PATH.read_text(encoding="utf-8"))


def _build_proof_bundle_v2(node_id: str = "test-node") -> dict:
    """Build a proof_bundle_v2.json dict deterministically (excluding timestamp)."""
    freeze = _load_freeze_v2()
    leaf_hashes = sorted(
        _sha256(_read_normalized(REPO_ROOT / e["path"]))
        for e in freeze["spec_files"]
    )
    merkle_root = _sha256("|".join(leaf_hashes).encode("utf-8"))
    output_hash = _sha256(f"peano_sovereignty_v2|{merkle_root}".encode("utf-8"))
    env_str = "os=linux|py=3.11|seed=39"
    environment_hash = _sha256(env_str.encode("utf-8"))
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "environment_hash": environment_hash,
        "invariant_spec_version": "v2",
        "merkle_root": merkle_root,
        "node_id": node_id,
        "output_hash": output_hash,
        "timestamp": timestamp,
    }


# ---------------------------------------------------------------------------
# 1. Spec hash aggregation
# ---------------------------------------------------------------------------

class TestSpecHashAggregation:
    """Verify that spec file SHA-256 hashes match the freeze file values."""

    def test_freeze_v2_file_exists(self):
        assert FREEZE_V2_PATH.exists(), f"freeze file missing: {FREEZE_V2_PATH}"

    def test_freeze_v2_has_expected_fields(self):
        freeze = _load_freeze_v2()
        assert freeze["freeze_version"] == "v2"
        assert freeze["invariant_spec_version"] == "v2"
        assert "merkle_root" in freeze
        assert "spec_files" in freeze
        assert len(freeze["spec_files"]) >= 1

    def test_peano_axioms_json_exists(self):
        assert (SPEC_DIR / "peano_axioms.json").exists()

    def test_spec_file_hashes_match_freeze(self):
        """Each spec file's SHA-256 must match the value recorded in the freeze file."""
        freeze = _load_freeze_v2()
        for entry in freeze["spec_files"]:
            sf = REPO_ROOT / entry["path"]
            assert sf.exists(), f"spec file missing: {sf}"
            actual = _sha256(_read_normalized(sf))
            assert actual == entry["sha256"], (
                f"hash mismatch for {entry['path']}: "
                f"expected={entry['sha256']} actual={actual}"
            )

    def test_merkle_root_matches_freeze(self):
        """The computed Merkle root of all spec files must match the freeze file."""
        freeze = _load_freeze_v2()
        leaf_hashes = []
        for entry in freeze["spec_files"]:
            sf = REPO_ROOT / entry["path"]
            assert sf.exists(), f"spec file missing: {sf}"
            leaf_hashes.append(_sha256(_read_normalized(sf)))
        computed = _sha256("|".join(sorted(leaf_hashes)).encode("utf-8"))
        assert computed == freeze["merkle_root"], (
            f"Merkle root mismatch: computed={computed} freeze={freeze['merkle_root']}"
        )

    def test_compute_spec_merkle_root_helper(self):
        """compute_spec_merkle_root() returns expected value from freeze file."""
        freeze = _load_freeze_v2()
        merkle_root, error = compute_spec_merkle_root(freeze)
        assert error == "", f"compute_spec_merkle_root error: {error}"
        assert merkle_root == freeze["merkle_root"]


# ---------------------------------------------------------------------------
# 2. Peano invariant checker with v2 spec
# ---------------------------------------------------------------------------

class TestPeanoInvariantChecker:
    """Verify the Peano invariant checker passes on core directories."""

    def test_invariant_checker_passes_core_dirs(self):
        """run_peano_invariant_checker must find no violations in core dirs."""
        report = run_peano_invariant_checker()
        assert report.all_passed, (
            f"Peano invariant violations found:\n"
            + "\n".join(
                f"  {v.file}:{v.line}: {v.kind}: {v.detail}"
                for v in report.violations
            )
        )

    def test_invariant_checker_returns_report(self):
        report = run_peano_invariant_checker(dirs=["yeshua_math"])
        assert hasattr(report, "all_passed")
        assert hasattr(report, "violations")
        assert hasattr(report, "passed")

    def test_invariant_checker_to_json(self):
        report = run_peano_invariant_checker(dirs=["yeshua_math"])
        js = report.to_json()
        parsed = json.loads(js)
        assert "all_passed" in parsed
        assert "violations" in parsed

    def test_invariant_checker_with_spec_v2(self, tmp_path):
        """Peano checker with --spec validates spec hashes before running."""
        # This exercises the spec validation path used by the workflow.
        import subprocess
        result = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "yeshua_math" / "peano_invariant_checker.py"),
                "--spec", str(FREEZE_V2_PATH),
                "--dirs", "yeshua_math",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"peano_invariant_checker.py failed:\nstdout={result.stdout}\nstderr={result.stderr}"
        )
        parsed = json.loads(result.stdout)
        assert parsed["all_passed"] is True


# ---------------------------------------------------------------------------
# 3. Cross-validator spec Merkle check
# ---------------------------------------------------------------------------

class TestCrossValidatorSpecMerkle:
    """Verify the cross-validator correctly checks the spec Merkle root."""

    def test_cross_validation_passes(self):
        result = run_cross_validation()
        # Only check spec_merkle_root_v2 — other checks may need C runtime
        spec_check = next(
            (c for c in result.checks if c["name"] == "spec_merkle_root_v2"),
            None,
        )
        assert spec_check is not None, "spec_merkle_root_v2 check missing from cross-validator"
        assert spec_check["passed"], (
            f"spec_merkle_root_v2 failed: {spec_check['detail']}"
        )

    def test_cross_validator_arithmetic_checks_pass(self):
        result = run_cross_validation()
        arith_failures = [
            c for c in result.failures
            if c["name"].startswith("peano_") or c["name"].startswith("demorgan_")
        ]
        assert arith_failures == [], (
            f"Arithmetic/logic cross-validation failures: {arith_failures}"
        )


# ---------------------------------------------------------------------------
# 4. Proof bundle v2 fields and determinism
# ---------------------------------------------------------------------------

class TestProofBundleV2:
    """Verify proof_bundle_v2 fields and determinism."""

    REQUIRED_FIELDS = {
        "merkle_root", "output_hash", "environment_hash",
        "timestamp", "invariant_spec_version", "node_id",
    }

    def test_bundle_has_required_fields(self):
        bundle = _build_proof_bundle_v2()
        missing = self.REQUIRED_FIELDS - set(bundle.keys())
        assert missing == set(), f"Missing fields: {missing}"

    def test_bundle_invariant_spec_version_is_v2(self):
        bundle = _build_proof_bundle_v2()
        assert bundle["invariant_spec_version"] == "v2"

    def test_bundle_merkle_root_matches_freeze(self):
        freeze = _load_freeze_v2()
        bundle = _build_proof_bundle_v2()
        assert bundle["merkle_root"] == freeze["merkle_root"]

    def test_bundle_deterministic_excluding_timestamp(self):
        """Identical inputs produce identical fields except timestamp."""
        b1 = _build_proof_bundle_v2(node_id="node-A")
        b2 = _build_proof_bundle_v2(node_id="node-A")
        for field in ("merkle_root", "output_hash", "environment_hash",
                      "invariant_spec_version", "node_id"):
            assert b1[field] == b2[field], (
                f"Field {field!r} is not deterministic: {b1[field]!r} != {b2[field]!r}"
            )

    def test_bundle_timestamp_is_utc_iso8601(self):
        bundle = _build_proof_bundle_v2()
        ts = bundle["timestamp"]
        # Should parse as UTC ISO 8601
        parsed = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
        assert parsed is not None

    def test_read_proof_bundle_v2_validates_fields(self, tmp_path):
        bundle = _build_proof_bundle_v2()
        p = tmp_path / "proof_bundle_v2.json"
        p.write_text(json.dumps(bundle))
        loaded = read_proof_bundle_v2(p)
        assert loaded["invariant_spec_version"] == "v2"

    def test_read_proof_bundle_v2_rejects_missing_fields(self, tmp_path):
        bundle = _build_proof_bundle_v2()
        del bundle["merkle_root"]
        p = tmp_path / "bad_bundle.json"
        p.write_text(json.dumps(bundle))
        with pytest.raises(ValueError, match="missing required fields"):
            read_proof_bundle_v2(p)

    def test_read_proof_bundle_v2_rejects_unknown_spec_version(self, tmp_path):
        bundle = _build_proof_bundle_v2()
        bundle["invariant_spec_version"] = "v99"
        p = tmp_path / "bad_bundle.json"
        p.write_text(json.dumps(bundle))
        with pytest.raises(ValueError, match="unsupported invariant_spec_version"):
            read_proof_bundle_v2(p)

    def test_read_proof_bundle_v2_accepts_v1(self, tmp_path):
        bundle = _build_proof_bundle_v2()
        bundle["invariant_spec_version"] = "v1"
        p = tmp_path / "v1_bundle.json"
        p.write_text(json.dumps(bundle))
        loaded = read_proof_bundle_v2(p)
        assert loaded["invariant_spec_version"] == "v1"
