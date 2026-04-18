"""
Tests for SAL state classification module.

Validates Fraction-based threshold boundaries, ProofObject structure,
YeshuaClaim wrapping, and falsifiability predicates.
"""

from fractions import Fraction

import pytest

from axioms.logic import ProofObject
from axioms.yeshua_axioms import YeshuaClaim
from src.sal.state_classification import StateLabel, classify_artifact, wrap_claim


DEFAULT_THRESHOLDS = {
    "certain": Fraction(247, 1),
    "high_confidence": Fraction(200, 1),
    "probable": Fraction(150, 1),
    "unknown": Fraction(100, 1),
    "suspicious": Fraction(50, 1),
}


class TestClassifyArtifact:
    def test_classify_certain(self):
        state, (success, proof) = classify_artifact(
            path="/tmp/test.txt",
            checksum="abc123",
            metrics={"score": Fraction(300, 1)},
            thresholds=DEFAULT_THRESHOLDS,
        )
        assert state == StateLabel.CERTAIN.value
        assert success is True
        assert isinstance(proof, ProofObject)
        assert proof.falsifies_if is not None and len(proof.falsifies_if) > 0

    def test_classify_high_confidence(self):
        state, (success, proof) = classify_artifact(
            path="/tmp/test.txt",
            checksum="abc123",
            metrics={"score": Fraction(220, 1)},
            thresholds=DEFAULT_THRESHOLDS,
        )
        assert state == StateLabel.HIGH_CONFIDENCE.value
        assert success is True

    def test_classify_probable(self):
        state, (success, proof) = classify_artifact(
            path="/tmp/test.txt",
            checksum="abc123",
            metrics={"score": Fraction(160, 1)},
            thresholds=DEFAULT_THRESHOLDS,
        )
        assert state == StateLabel.PROBABLE.value
        assert success is True

    def test_classify_unknown(self):
        state, (success, proof) = classify_artifact(
            path="/tmp/test.txt",
            checksum="abc123",
            metrics={"score": Fraction(100, 1)},
            thresholds=DEFAULT_THRESHOLDS,
        )
        assert state == StateLabel.UNKNOWN.value
        assert success is True

    def test_classify_suspicious(self):
        state, (success, proof) = classify_artifact(
            path="/tmp/test.txt",
            checksum="abc123",
            metrics={"score": Fraction(50, 1)},
            thresholds=DEFAULT_THRESHOLDS,
        )
        assert state == StateLabel.SUSPICIOUS.value
        assert success is False

    def test_classify_invalid(self):
        state, (success, proof) = classify_artifact(
            path="/tmp/test.txt",
            checksum="abc123",
            metrics={"score": Fraction(10, 1)},
            thresholds=DEFAULT_THRESHOLDS,
        )
        assert state == StateLabel.INVALID.value
        assert success is False

    def test_classify_boundary_certain_exact(self):
        # Exact boundary for CERTAIN
        state, (success, _) = classify_artifact(
            path="/tmp/test.txt",
            checksum="abc123",
            metrics={"score": Fraction(247, 1)},
            thresholds=DEFAULT_THRESHOLDS,
        )
        assert state == StateLabel.CERTAIN.value
        assert success is True

    def test_classify_boundary_high_confidence_exact(self):
        # Exact boundary for HIGH_CONFIDENCE
        state, (success, _) = classify_artifact(
            path="/tmp/test.txt",
            checksum="abc123",
            metrics={"score": Fraction(200, 1)},
            thresholds=DEFAULT_THRESHOLDS,
        )
        assert state == StateLabel.HIGH_CONFIDENCE.value
        assert success is True

    def test_classify_fraction_arithmetic(self):
        # Use non-integer Fraction to verify no float conversion
        state, (success, proof) = classify_artifact(
            path="/tmp/test.txt",
            checksum="abc123",
            metrics={"score": Fraction(495, 2)},  # 247.5
            thresholds={
                "certain": Fraction(247, 1),
                "high_confidence": Fraction(200, 1),
                "probable": Fraction(150, 1),
                "unknown": Fraction(100, 1),
                "suspicious": Fraction(50, 1),
            },
        )
        assert state == StateLabel.CERTAIN.value
        assert success is True
        # Verify premises contain serialized Fractions
        premises_str = " ".join(str(p) for p in proof.premises)
        assert "495/2" in premises_str or "247" in premises_str

    def test_proof_object_fields(self):
        state, (success, proof) = classify_artifact(
            path="/tmp/test.txt",
            checksum="abc123",
            metrics={"score": Fraction(150, 1)},
            thresholds=DEFAULT_THRESHOLDS,
        )
        assert proof.rule == "StateClassification"
        assert len(proof.premises) > 0
        assert "path=/tmp/test.txt" in proof.premises
        assert "checksum=abc123" in proof.premises
        assert proof.conclusion.startswith("state=")
        assert proof.falsifies_if is not None
        assert len(proof.falsifies_if) > 0

    def test_falsifies_if_non_empty(self):
        _, (success, proof) = classify_artifact(
            path="/tmp/test.txt",
            checksum="abc123",
            metrics={"score": Fraction(10, 1)},
            thresholds=DEFAULT_THRESHOLDS,
        )
        assert proof.falsifies_if is not None
        assert isinstance(proof.falsifies_if, str)
        assert len(proof.falsifies_if) > 0


class TestWrapClaim:
    def test_wrap_claim_returns_yeshua(self):
        state, (success, claim) = wrap_claim(
            path="/tmp/test.txt",
            checksum="abc123",
            metrics={"score": Fraction(300, 1)},
            thresholds=DEFAULT_THRESHOLDS,
        )
        assert state == StateLabel.CERTAIN.value
        assert success is True
        assert isinstance(claim, YeshuaClaim)
        assert claim.source == "src.sal.state_classification"
        assert claim.hash_commitment is not None
        assert len(claim.hash_commitment) == 64
        assert claim.is_hash_anchored()
        assert claim.is_reproducible()

    def test_yeshua_claim_derivation_valid(self):
        _, (_, claim) = wrap_claim(
            path="/tmp/test.txt",
            checksum="abc123",
            metrics={"score": Fraction(300, 1)},
            thresholds=DEFAULT_THRESHOLDS,
        )
        assert claim.derivation.is_valid()
        assert claim.derivation.falsifies_if is not None
