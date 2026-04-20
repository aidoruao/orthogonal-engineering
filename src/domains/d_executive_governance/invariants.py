"""Invariant checks for the executive-governance domain."""
from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject

from .implementation import (
    MAX_SCOPE_EXPANSION,
    MIN_INDEPENDENCE_COVERAGE,
    ExecutiveActionClaim,
    create_nominal_claim,
)


def check_separation_of_powers_anchors(
    data: ExecutiveActionClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: action has both a statutory and a constitutional anchor.

    Standard: U.S. Const. art. II §3 take-care clause + Youngstown Sheet &
    Tube Co. v. Sawyer, 343 U.S. 579 (1952).
    Falsifies if: either anchor is missing.
    falsifies_if: either anchor is missing.
    """
    success = data.has_statutory_anchor and data.has_constitutional_anchor
    proof = ProofObject(
        rule="check_separation_of_powers_anchors",
        premises=[
            f"statutory_anchor={data.has_statutory_anchor}",
            f"constitutional_anchor={data.has_constitutional_anchor}",
        ],
        conclusion=(
            "PASS: both anchors present"
            if success else "FAIL: missing statutory or constitutional anchor"
        ),
    )
    return success, proof


def check_congressional_review_act_compliance(
    data: ExecutiveActionClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: legislative notice and CRA submission both complete.

    Standard: Congressional Review Act, 5 U.S.C. §§801–808.
    Falsifies if: legislative_notice_submitted False or CRA deadline missed.
    falsifies_if: legislative_notice_submitted False or CRA deadline missed.
    """
    success = (
        data.legislative_notice_submitted and data.cra_submission_within_60_days
    )
    proof = ProofObject(
        rule="check_congressional_review_act_compliance",
        premises=[
            f"legislative_notice={data.legislative_notice_submitted}",
            f"cra_within_60_days={data.cra_submission_within_60_days}",
        ],
        conclusion=(
            "PASS: CRA pathway satisfied"
            if success else "FAIL: CRA pathway incomplete"
        ),
    )
    return success, proof


def check_judicial_review_preserved(
    data: ExecutiveActionClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: judicial review standing is not foreclosed.

    Standard: Administrative Procedure Act, 5 U.S.C. §702; Motor Vehicle
    Mfrs. Ass'n v. State Farm, 463 U.S. 29 (1983).
    Falsifies if: judicial_review_standing_preserved False.
    falsifies_if: judicial_review_standing_preserved False.
    """
    success = data.judicial_review_standing_preserved
    proof = ProofObject(
        rule="check_judicial_review_preserved",
        premises=[
            f"judicial_review_standing_preserved={data.judicial_review_standing_preserved}",
        ],
        conclusion=(
            "PASS: judicial review preserved"
            if success else "FAIL: judicial review foreclosed"
        ),
    )
    return success, proof


def check_publication_requirement(
    data: ExecutiveActionClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: action is published in the Federal Register.

    Standard: Federal Register Act, 44 U.S.C. §§1505–1507.
    Falsifies if: published_in_federal_register False.
    falsifies_if: published_in_federal_register False.
    """
    success = data.published_in_federal_register
    proof = ProofObject(
        rule="check_publication_requirement",
        premises=[
            f"published_in_federal_register={data.published_in_federal_register}",
        ],
        conclusion=(
            "PASS: Federal Register publication complete"
            if success else "FAIL: not published in Federal Register"
        ),
    )
    return success, proof


def check_independence_review_coverage(
    data: ExecutiveActionClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: independence review sign-off rate >= floor.

    Standard: Inspector General Act of 1978 as amended +
    AF-008 independence-review requirement.
    Falsifies if: signed / total < MIN_INDEPENDENCE_COVERAGE.
    falsifies_if: signed / total < MIN_INDEPENDENCE_COVERAGE.
    """
    total = max(data.independence_review_items_total, 0)
    signed = max(data.independence_review_items_signed, 0)
    if total == 0:
        success = False
        ratio = Fraction(0)
    else:
        ratio = Fraction(signed, total)
        success = ratio >= MIN_INDEPENDENCE_COVERAGE
    proof = ProofObject(
        rule="check_independence_review_coverage",
        premises=[
            f"signed={signed}",
            f"total={total}",
            f"ratio={ratio}",
            f"floor={MIN_INDEPENDENCE_COVERAGE}",
        ],
        conclusion=(
            "PASS: independence review coverage >= floor"
            if success else f"FAIL: ratio {ratio} < floor {MIN_INDEPENDENCE_COVERAGE}"
        ),
    )
    return success, proof


def check_scope_expansion_bounded(
    data: ExecutiveActionClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: claimed scope does not exceed statutory scope by more than 20%.

    Standard: West Virginia v. EPA, 597 U.S. 697 (2022) major-questions doctrine.
    Falsifies if: scope_expansion > MAX_SCOPE_EXPANSION.
    falsifies_if: scope_expansion > MAX_SCOPE_EXPANSION.
    """
    success = data.scope_expansion <= MAX_SCOPE_EXPANSION
    proof = ProofObject(
        rule="check_scope_expansion_bounded",
        premises=[
            f"scope_expansion={data.scope_expansion}",
            f"limit={MAX_SCOPE_EXPANSION}",
        ],
        conclusion=(
            "PASS: scope expansion within limit"
            if success
            else f"FAIL: scope_expansion {data.scope_expansion} > {MAX_SCOPE_EXPANSION}"
        ),
    )
    return success, proof


def check_consent_log_recorded(
    data: ExecutiveActionClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: consent-log entry exists for this action.

    Standard: BC-001 append-only consent log.
    Falsifies if: consent_log_entry_recorded False.
    falsifies_if: consent_log_entry_recorded False.
    """
    success = data.consent_log_entry_recorded
    proof = ProofObject(
        rule="check_consent_log_recorded",
        premises=[
            f"consent_log_entry_recorded={data.consent_log_entry_recorded}",
        ],
        conclusion=(
            "PASS: consent log entry present"
            if success else "FAIL: consent log entry missing"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain on the nominal claim.

    Standard: Executive governance nominal executable check set.
    Falsifies if: any invariant check returns False on the nominal claim.
    falsifies_if: any invariant check returns False on the nominal claim.
    """
    data = create_nominal_claim()
    checks = [
        ("check_separation_of_powers_anchors", check_separation_of_powers_anchors),
        (
            "check_congressional_review_act_compliance",
            check_congressional_review_act_compliance,
        ),
        ("check_judicial_review_preserved", check_judicial_review_preserved),
        ("check_publication_requirement", check_publication_requirement),
        ("check_independence_review_coverage", check_independence_review_coverage),
        ("check_scope_expansion_bounded", check_scope_expansion_bounded),
        ("check_consent_log_recorded", check_consent_log_recorded),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
