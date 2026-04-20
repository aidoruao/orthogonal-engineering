"""Invariant checks for the secular projection domain."""
from __future__ import annotations

from typing import List, Tuple

from axioms.logic import ProofObject

from .implementation import SecularProjectionClaim, create_nominal_claim


def check_every_premise_has_witness(
    data: SecularProjectionClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: every theological premise has a secular witness.

    Standard: OE-102 secular projection completeness.
    Falsifies if: secular_witnesses < theological_premises.
    falsifies_if: secular_witnesses < theological_premises.
    """
    success = data.secular_witnesses >= data.theological_premises
    proof = ProofObject(
        rule="check_every_premise_has_witness",
        premises=[
            f"theological_premises={data.theological_premises}",
            f"secular_witnesses={data.secular_witnesses}",
        ],
        conclusion=(
            "PASS: every premise has a secular witness"
            if success else "FAIL: at least one premise lacks a secular witness"
        ),
    )
    return success, proof


def check_every_witness_has_falsifier(
    data: SecularProjectionClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: every secular witness has an associated falsification rule.

    Standard: YS-003 unfalsifiable = unaccountable.
    Falsifies if: falsification_rules < secular_witnesses.
    falsifies_if: falsification_rules < secular_witnesses.
    """
    success = data.falsification_rules >= data.secular_witnesses
    proof = ProofObject(
        rule="check_every_witness_has_falsifier",
        premises=[
            f"secular_witnesses={data.secular_witnesses}",
            f"falsification_rules={data.falsification_rules}",
        ],
        conclusion=(
            "PASS: every witness has a falsifier"
            if success else "FAIL: at least one witness is unfalsifiable"
        ),
    )
    return success, proof


def check_projection_non_expansive(
    data: SecularProjectionClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: projection does not shrink the falsifier set.

    A projection must be at least as constrained as the source claim — the
    projected falsifier cardinality must be >= the unprojected cardinality,
    otherwise the projection has hidden evidence.
    Standard: OE-103 projection preserves falsifiability.
    Falsifies if: projected_falsifier_cardinality < unprojected_falsifier_cardinality.
    falsifies_if: projected_falsifier_cardinality < unprojected_falsifier_cardinality.
    """
    success = (
        data.projected_falsifier_cardinality >= data.unprojected_falsifier_cardinality
    )
    proof = ProofObject(
        rule="check_projection_non_expansive",
        premises=[
            f"unprojected={data.unprojected_falsifier_cardinality}",
            f"projected={data.projected_falsifier_cardinality}",
        ],
        conclusion=(
            "PASS: projection preserved falsifier cardinality"
            if success else "FAIL: projection dropped falsifiers"
        ),
    )
    return success, proof


def check_no_appeal_to_authority(
    data: SecularProjectionClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: the projection contains zero appeals to authority.

    Standard: YS-004 no authority without proof + BC-007 steward role only.
    Falsifies if: appeal_to_authority_count > 0.
    falsifies_if: appeal_to_authority_count > 0.
    """
    success = data.appeal_to_authority_count == 0
    proof = ProofObject(
        rule="check_no_appeal_to_authority",
        premises=[
            f"appeal_to_authority_count={data.appeal_to_authority_count}",
        ],
        conclusion=(
            "PASS: zero appeals to authority"
            if success else (
                f"FAIL: {data.appeal_to_authority_count} appeals to authority"
            )
        ),
    )
    return success, proof


def check_popperian_audit_green(
    data: SecularProjectionClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: the Popperian audit pipeline signed off on the projection.

    Standard: audit/popperian_audit.py green exit.
    Falsifies if: not popperian_audit_green.
    falsifies_if: not popperian_audit_green.
    """
    success = data.popperian_audit_green
    proof = ProofObject(
        rule="check_popperian_audit_green",
        premises=[
            f"popperian_audit_green={data.popperian_audit_green}",
        ],
        conclusion=(
            "PASS: Popperian audit green"
            if success else "FAIL: Popperian audit not green"
        ),
    )
    return success, proof


def check_projection_signature_present(
    data: SecularProjectionClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: projection is sealed by a hex sha256 signature.

    Standard: CS-006 cryptographic projection seal.
    Falsifies if: signature is not a 64-character lowercase hex string.
    falsifies_if: signature is not a 64-character lowercase hex string.
    """
    sig = data.projection_signature_hash
    success = (
        isinstance(sig, str)
        and len(sig) == 64
        and all(c in "0123456789abcdef" for c in sig)
    )
    proof = ProofObject(
        rule="check_projection_signature_present",
        premises=[
            f"signature_length={len(sig) if isinstance(sig, str) else 'n/a'}",
        ],
        conclusion=(
            "PASS: projection signature well-formed"
            if success else "FAIL: projection signature missing or malformed"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain on the nominal claim.

    Standard: Secular projection nominal executable check set.
    Falsifies if: any invariant check returns False on the nominal claim.
    falsifies_if: any invariant check returns False on the nominal claim.
    """
    data = create_nominal_claim()
    checks = [
        ("check_every_premise_has_witness", check_every_premise_has_witness),
        ("check_every_witness_has_falsifier", check_every_witness_has_falsifier),
        ("check_projection_non_expansive", check_projection_non_expansive),
        ("check_no_appeal_to_authority", check_no_appeal_to_authority),
        ("check_popperian_audit_green", check_popperian_audit_green),
        ("check_projection_signature_present", check_projection_signature_present),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
