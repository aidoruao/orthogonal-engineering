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


def check_composite_anchor_strength(
    data: ExecutiveActionClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: weighted average of statutory and constitutional anchor strength.

    Standard: U.S. Const. art. II 3 take-care clause + Youngstown Sheet and
    Tube Co. v. Sawyer, 343 U.S. 579 (1952).
    Falsifies if: (statutory_anchor_strength + constitutional_anchor_strength) / 2 < Fraction(3, 4).
    falsifies_if: (statutory_anchor_strength + constitutional_anchor_strength) / 2 < Fraction(3, 4).
    """
    avg = (data.statutory_anchor_strength + data.constitutional_anchor_strength) / 2
    threshold = Fraction(3, 4)
    success = avg >= threshold
    proof = ProofObject(
        rule="check_composite_anchor_strength",
        premises=[
            f"statutory_anchor_strength={data.statutory_anchor_strength}",
            f"constitutional_anchor_strength={data.constitutional_anchor_strength}",
            f"average={avg}",
            f"threshold={threshold}",
        ],
        conclusion=(
            f"PASS: average strength {avg} >= {threshold}"
            if success
            else f"FAIL: average strength {avg} < {threshold}"
        ),
    )
    return success, proof


def check_cra_timeliness_score(
    data: ExecutiveActionClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: Congressional Review Act notice submitted AND within 60-day deadline.

    Standard: Congressional Review Act, 5 U.S.C. 801-808.
    Falsifies if: legislative_notice_submitted is False OR cra_submission_within_60_days is False.
    falsifies_if: legislative_notice_submitted is False OR cra_submission_within_60_days is False.
    """
    if not data.legislative_notice_submitted:
        score = Fraction(0)
        success = False
    elif not data.cra_submission_within_60_days:
        score = Fraction(1, 3)
        success = False
    else:
        score = Fraction(1)
        success = True
    proof = ProofObject(
        rule="check_cra_timeliness_score",
        premises=[
            f"legislative_notice_submitted={data.legislative_notice_submitted}",
            f"cra_within_60_days={data.cra_submission_within_60_days}",
            f"timeliness_score={score}",
        ],
        conclusion=(
            f"PASS: CRA timeliness score {score} sufficient"
            if success
            else f"FAIL: CRA timeliness score {score} insufficient"
        ),
    )
    return success, proof


def check_judicial_review_accessibility(
    data: ExecutiveActionClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: judicial review pathways available and standing preserved.

    Standard: Administrative Procedure Act, 5 U.S.C. 702; Motor Vehicle
    Mfrs. Assn v. State Farm, 463 U.S. 29 (1983).
    Falsifies if: judicial_review_pathways < 1 OR judicial_review_standing_preserved is False.
    falsifies_if: judicial_review_pathways < 1 OR judicial_review_standing_preserved is False.
    """
    if data.judicial_review_pathways < 1:
        score = Fraction(0)
        success = False
    elif not data.judicial_review_standing_preserved:
        score = Fraction(0)
        success = False
    else:
        score = Fraction(min(data.judicial_review_pathways, 3), 3)
        success = True
    proof = ProofObject(
        rule="check_judicial_review_accessibility",
        premises=[
            f"judicial_review_pathways={data.judicial_review_pathways}",
            f"judicial_review_standing_preserved={data.judicial_review_standing_preserved}",
            f"accessibility_score={score}",
        ],
        conclusion=(
            f"PASS: judicial review accessible (score {score})"
            if success
            else f"FAIL: judicial review inaccessible (score {score})"
        ),
    )
    return success, proof


def check_publication_timeliness_fraction(
    data: ExecutiveActionClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: published in Federal Register AND publication delay within statutory maximum.

    Standard: Federal Register Act, 44 U.S.C. 1505-1507.
    Falsifies if: published_in_federal_register is False OR publication_delay_days > 60.
    falsifies_if: published_in_federal_register is False OR publication_delay_days > 60.
    """
    max_days = 60
    delay = max(data.publication_delay_days, 0)
    fraction = Fraction(delay, max_days) if max_days > 0 else Fraction(0)
    if not data.published_in_federal_register:
        success = False
        reason = "not published in Federal Register"
    elif delay > max_days:
        success = False
        reason = f"delay fraction {fraction} exceeds limit"
    else:
        success = True
        reason = f"delay fraction {fraction} within limit"
    proof = ProofObject(
        rule="check_publication_timeliness_fraction",
        premises=[
            f"published_in_federal_register={data.published_in_federal_register}",
            f"publication_delay_days={delay}",
            f"delay_fraction={fraction}",
            f"max_days={max_days}",
        ],
        conclusion=("PASS: " if success else "FAIL: ") + reason,
    )
    return success, proof


def check_independence_coverage_fraction(
    data: ExecutiveActionClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: independence review sign-off rate as exact Fraction.

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
        rule="check_independence_coverage_fraction",
        premises=[
            f"signed={signed}",
            f"total={total}",
            f"ratio={ratio}",
            f"floor={MIN_INDEPENDENCE_COVERAGE}",
        ],
        conclusion=(
            f"PASS: independence coverage {ratio} >= floor {MIN_INDEPENDENCE_COVERAGE}"
            if success
            else f"FAIL: independence coverage {ratio} < floor {MIN_INDEPENDENCE_COVERAGE}"
        ),
    )
    return success, proof


def check_scope_expansion_severity(
    data: ExecutiveActionClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: scope expansion as severity fraction of statutory limit.

    Standard: West Virginia v. EPA, 597 U.S. 697 (2022) major-questions doctrine.
    Falsifies if: scope_expansion > MAX_SCOPE_EXPANSION.
    falsifies_if: scope_expansion > MAX_SCOPE_EXPANSION.
    """
    if MAX_SCOPE_EXPANSION > Fraction(0):
        severity = data.scope_expansion / MAX_SCOPE_EXPANSION
    else:
        severity = Fraction(0)
    success = data.scope_expansion <= MAX_SCOPE_EXPANSION
    proof = ProofObject(
        rule="check_scope_expansion_severity",
        premises=[
            f"scope_expansion={data.scope_expansion}",
            f"max={MAX_SCOPE_EXPANSION}",
            f"severity_fraction={severity}",
        ],
        conclusion=(
            f"PASS: severity {severity} within limit"
            if success
            else f"FAIL: severity {severity} exceeds limit"
        ),
    )
    return success, proof


def check_executive_accountability_score(
    data: ExecutiveActionClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: composite accountability score across consent, anchors, and coverage.

    Standard: BC-001 append-only consent log + separation-of-powers doctrine.
    Falsifies if: composite_score < Fraction(1, 2).
    falsifies_if: composite_score < Fraction(1, 2).
    """
    consent_factor = Fraction(1) if data.consent_log_entry_recorded else Fraction(0)
    anchor_factor = (data.statutory_anchor_strength + data.constitutional_anchor_strength) / 2
    total = max(data.independence_review_items_total, 0)
    signed = max(data.independence_review_items_signed, 0)
    coverage = Fraction(signed, total) if total > 0 else Fraction(0)
    composite = (consent_factor + anchor_factor + coverage) / 3
    threshold = Fraction(1, 2)
    success = composite >= threshold
    proof = ProofObject(
        rule="check_executive_accountability_score",
        premises=[
            f"consent_factor={consent_factor}",
            f"anchor_factor={anchor_factor}",
            f"coverage={coverage}",
            f"composite={composite}",
            f"threshold={threshold}",
        ],
        conclusion=(
            f"PASS: composite {composite} >= {threshold}"
            if success
            else f"FAIL: composite {composite} < {threshold}"
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
        ("check_composite_anchor_strength", check_composite_anchor_strength),
        ("check_cra_timeliness_score", check_cra_timeliness_score),
        ("check_judicial_review_accessibility", check_judicial_review_accessibility),
        ("check_publication_timeliness_fraction", check_publication_timeliness_fraction),
        ("check_independence_coverage_fraction", check_independence_coverage_fraction),
        ("check_scope_expansion_severity", check_scope_expansion_severity),
        ("check_executive_accountability_score", check_executive_accountability_score),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
