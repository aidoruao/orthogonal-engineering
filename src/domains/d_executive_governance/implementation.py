"""Implementation models for the executive-governance domain.

An ``ExecutiveActionClaim`` records a single executive-authority action
(order, directive, rule-making, appointment) together with the separation-
of-powers accountability trail that must accompany it: statutory /
constitutional anchor, legislative notice or Congressional Review Act
submission, judicial-review standing, published record, and a coverage
fraction of the independence-review checklist.

Arithmetic uses :class:`fractions.Fraction` to keep review-coverage ratios
byte-exact across platforms.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

MIN_INDEPENDENCE_COVERAGE: Fraction = Fraction(7, 10)
"""Minimum fraction of independence-review items that must be signed off."""

MAX_SCOPE_EXPANSION: Fraction = Fraction(1, 5)
"""Maximum acceptable delta between claimed scope and statutory scope."""


@dataclass(frozen=True)
class ExecutiveActionClaim:
    """Structured claim for a single executive-authority action."""

    has_statutory_anchor: bool
    has_constitutional_anchor: bool
    legislative_notice_submitted: bool
    cra_submission_within_60_days: bool
    judicial_review_standing_preserved: bool
    published_in_federal_register: bool
    independence_review_items_signed: int
    independence_review_items_total: int
    scope_expansion: Fraction
    consent_log_entry_recorded: bool
    statutory_anchor_strength: Fraction = Fraction(1, 1)
    constitutional_anchor_strength: Fraction = Fraction(1, 1)
    publication_delay_days: int = 0
    judicial_review_pathways: int = 1


def create_nominal_claim() -> ExecutiveActionClaim:
    """Create nominal claim data used by :func:`run_all_invariants`.

    Falsifies if: a nominal claim cannot be constructed with every
    separation-of-powers anchor present and independence-review coverage
    >= :data:`MIN_INDEPENDENCE_COVERAGE`.
    falsifies_if: a nominal claim cannot be constructed with every
    separation-of-powers anchor present and independence-review coverage
    >= MIN_INDEPENDENCE_COVERAGE.
    """
    return ExecutiveActionClaim(
        has_statutory_anchor=True,
        has_constitutional_anchor=True,
        legislative_notice_submitted=True,
        cra_submission_within_60_days=True,
        judicial_review_standing_preserved=True,
        published_in_federal_register=True,
        independence_review_items_signed=9,
        independence_review_items_total=10,
        scope_expansion=Fraction(1, 10),
        consent_log_entry_recorded=True,
        statutory_anchor_strength=Fraction(1, 1),
        constitutional_anchor_strength=Fraction(1, 1),
        publication_delay_days=0,
        judicial_review_pathways=2,
    )


DOMAIN_METADATA = {
    "id": "D_EXECUTIVE_GOVERNANCE",
    "claim_model": "ExecutiveActionClaim",
    "check_functions": [
        "check_composite_anchor_strength",
        "check_cra_timeliness_score",
        "check_judicial_review_accessibility",
        "check_publication_timeliness_fraction",
        "check_independence_coverage_fraction",
        "check_scope_expansion_severity",
        "check_executive_accountability_score",
    ],
}
