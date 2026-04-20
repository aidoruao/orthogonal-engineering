"""Implementation models for the secular projection domain.

The "secular projection" domain captures the discipline of projecting a
Yeshua-indexed claim onto a secular (Popperian / falsification-only) coordinate
system without losing its falsifier set. A projection is well-formed iff every
theological premise has a secular witness, every secular witness has a
falsification rule, and the projected claim is at least as constrained as the
unprojected claim.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SecularProjectionClaim:
    """Record for a secular projection of a Yeshua-indexed claim."""

    theological_premises: int
    secular_witnesses: int
    falsification_rules: int
    unprojected_falsifier_cardinality: int
    projected_falsifier_cardinality: int
    popperian_audit_green: bool
    appeal_to_authority_count: int
    projection_signature_hash: str


def create_nominal_claim() -> SecularProjectionClaim:
    """Create nominal claim data used by :func:`run_all_invariants`.

    Falsifies if: the nominal claim cannot be constructed such that every
    theological premise has a secular witness and a falsification rule.
    falsifies_if: the nominal claim cannot be constructed such that every
    theological premise has a secular witness and a falsification rule.
    """
    return SecularProjectionClaim(
        theological_premises=12,
        secular_witnesses=12,
        falsification_rules=12,
        unprojected_falsifier_cardinality=24,
        projected_falsifier_cardinality=24,
        popperian_audit_green=True,
        appeal_to_authority_count=0,
        projection_signature_hash=(
            "0" * 64  # deterministic fixture hash, replaced by real sha256 in prod
        ),
    )


DOMAIN_METADATA = {
    "id": "D_SECULAR_PROJECTION",
    "claim_model": "SecularProjectionClaim",
    "check_functions": [
        "check_every_premise_has_witness",
        "check_every_witness_has_falsifier",
        "check_projection_non_expansive",
        "check_no_appeal_to_authority",
        "check_popperian_audit_green",
        "check_projection_signature_present",
    ],
}
