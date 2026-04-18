"""
SAL State Classification Module

Deterministic classifier that maps artifacts to enumerated state labels
and wraps the result in a (bool, ProofObject) pair within a YeshuaClaim.

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

from enum import Enum
from fractions import Fraction
from typing import Any, Dict, Tuple

from axioms.logic import ProofObject
from axioms.yeshua_axioms import YeshuaClaim


class StateLabel(Enum):
    """Explicit state classification labels ordered from highest to lowest confidence."""

    CERTAIN = "CERTAIN"
    HIGH_CONFIDENCE = "HIGH_CONFIDENCE"
    PROBABLE = "PROBABLE"
    UNKNOWN = "UNKNOWN"
    SUSPICIOUS = "SUSPICIOUS"
    INVALID = "INVALID"

    def __str__(self) -> str:
        return self.value


# Ordered thresholds from highest confidence to lowest
_STATE_ORDER = [
    StateLabel.CERTAIN,
    StateLabel.HIGH_CONFIDENCE,
    StateLabel.PROBABLE,
    StateLabel.UNKNOWN,
    StateLabel.SUSPICIOUS,
    StateLabel.INVALID,
]


def classify_artifact(
    path: str,
    checksum: str,
    metrics: Dict[str, Fraction],
    thresholds: Dict[str, Fraction],
) -> Tuple[str, Tuple[bool, ProofObject]]:
    """
    Return (state_label, (success, ProofObject)).

    ProofObject must include 'falsifies_if'.

    Args:
        path: Artifact file path.
        checksum: Artifact checksum.
        metrics: Numeric scores as Fractions (e.g., {"score": Fraction(247, 1)}).
        thresholds: Configured threshold Fractions. Expected keys:
            - "certain"
            - "high_confidence"
            - "probable"
            - "unknown"
            - "suspicious"

    Returns:
        A tuple of (state_label_str, (success_bool, proof_object)).
    """
    score = metrics.get("score", Fraction(0, 1))

    # Deterministic classification using Fraction comparisons
    if score >= thresholds.get("certain", Fraction(247, 1)):
        state = StateLabel.CERTAIN
        success = True
    elif score >= thresholds.get("high_confidence", Fraction(200, 1)):
        state = StateLabel.HIGH_CONFIDENCE
        success = True
    elif score >= thresholds.get("probable", Fraction(150, 1)):
        state = StateLabel.PROBABLE
        success = True
    elif score >= thresholds.get("unknown", Fraction(100, 1)):
        state = StateLabel.UNKNOWN
        success = True
    elif score >= thresholds.get("suspicious", Fraction(50, 1)):
        state = StateLabel.SUSPICIOUS
        success = False
    else:
        state = StateLabel.INVALID
        success = False

    falsifies_if = (
        f"Artifact {path} has score {score} which does not meet the "
        f"'{state.value}' threshold ({thresholds.get(state.value.lower(), 'N/A')})"
    )

    proof = ProofObject(
        rule="StateClassification",
        premises=[
            f"path={path}",
            f"checksum={checksum}",
            f"score={score}",
            f"thresholds={_serialize_thresholds(thresholds)}",
        ],
        conclusion=f"state={state.value}, success={success}",
        falsifies_if=falsifies_if,
    )

    return state.value, (success, proof)


def wrap_claim(
    path: str,
    checksum: str,
    metrics: Dict[str, Fraction],
    thresholds: Dict[str, Fraction],
) -> Tuple[str, Tuple[bool, YeshuaClaim]]:
    """
    Classify an artifact and wrap the ProofObject in a YeshuaClaim.

    Returns:
        (state_label, (success, YeshuaClaim)).
    """
    state_label, (success, proof) = classify_artifact(
        path, checksum, metrics, thresholds
    )

    claim = YeshuaClaim(
        source="src.sal.state_classification",
        statement=f"Artifact {path} classified as {state_label}",
        derivation=proof,
    )

    return state_label, (success, claim)


def _serialize_thresholds(thresholds: Dict[str, Fraction]) -> Dict[str, str]:
    """Serialize Fraction thresholds to strings for premises."""
    return {k: str(v) for k, v in thresholds.items()}
