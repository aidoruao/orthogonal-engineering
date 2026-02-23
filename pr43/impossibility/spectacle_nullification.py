# pr43/impossibility/spectacle_nullification.py
# PR #43 — Orthogonal Parallel
# Standard: Yeshua
#
# Theorem: Spectacle Nullification
#
# If correctness is verifiable via proof,
# no rhetorical amplification alters the truth value.
# Truth independent of audience.
# Spectacle produces zero delta in validity.

from __future__ import annotations

from typing import Dict


def truth_value(proof: Dict) -> bool:
    """
    Truth = structural validity, determined by logic alone.
    Not by market reception, hype, or rhetorical amplification.
    """
    return bool(proof.get("valid", False))


def spectacle_delta(proof: Dict, rhetorical_amplitude: int = 0) -> int:
    """
    The change in truth value produced by rhetorical amplification.
    Always zero. Theorem: spectacle produces zero delta in validity.
    """
    return 0


def nullification_proof(proof: Dict) -> Dict:
    """
    Construct a proof record demonstrating spectacle nullification.
    """
    tv = truth_value(proof)
    delta = spectacle_delta(proof)
    return {
        "theorem": "SpectacleNullification",
        "input_truth_value": tv,
        "rhetorical_amplitude_applied": 0,
        "delta_in_validity": delta,
        "output_truth_value": tv,
        "invariant": "truth_value_unchanged_by_spectacle",
        "proof_method": "constructive",
    }
