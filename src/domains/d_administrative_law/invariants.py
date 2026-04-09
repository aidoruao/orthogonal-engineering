#!/usr/bin/env python3
"""
Administrative Law Invariants — Falsifiable Regulatory Constraints

All thresholds derived from APA and federal circuit precedent.
Uses Fraction for exact arithmetic — 0 floating-point in regulatory logic.
"""

from fractions import Fraction
from datetime import datetime
from typing import Tuple, List
from axioms.logic import ProofObject
from .implementation import (
    Rulemaking, 
    ExhaustionClaim, 
    MIN_COMMENT_PERIOD_DAYS,
    RulemakingType,
)


def check_notice_period(rule: Rulemaking) -> Tuple[bool, ProofObject]:
    """
    APA § 553(b) — Notice of proposed rulemaking must allow 
    sufficient time for meaningful public participation.
    
    Standard: Minimum 30 days for comment period.
    Exception: Good cause (documented separately).
    
    Returns: (passes, ProofObject)
    """
    if rule.rule_type == RulemakingType.INTERPRETIVE:
        # Exempt from notice-and-comment
        return True, ProofObject(
            conclusion="Interpretive rule exempt from notice-and-comment",
            premises=["Rule type: INTERPRETIVE"],
            rule="apa_553_exemption"
        )
    
    actual_days = rule.get_comment_period_days()
    
    if actual_days < MIN_COMMENT_PERIOD_DAYS:
        return False, ProofObject(
            conclusion=f"VIOLATION: Comment period {actual_days} days < minimum {MIN_COMMENT_PERIOD_DAYS}",
            premises=[
                f"Actual period: {actual_days} days",
                f"Required minimum: {MIN_COMMENT_PERIOD_DAYS} days",
                "APA § 553(b)(2)"
            ],
            rule="apa_553_notice_period"
        )
    
    return True, ProofObject(
        conclusion=f"Notice period adequate: {actual_days} days >= {MIN_COMMENT_PERIOD_DAYS}",
        premises=[
            f"Comment period: {actual_days} days",
            f"Minimum required: {MIN_COMMENT_PERIOD_DAYS} days"
        ],
        rule="apa_553_notice_period"
    )


def check_exhaustion(claim: ExhaustionClaim) -> Tuple[bool, ProofObject]:
    """
    McKart v. United States (1975) — Exhaustion of administrative 
    remedies is generally required before judicial review.
    
    Exceptions (not checked here):
    - Futility
    - Irreparable injury
    - Purely legal question
    """
    if claim.is_exhausted():
        return True, ProofObject(
            conclusion="Administrative remedies exhausted",
            premises=[
                f"Remedies sought: {claim.remedies_sought}",
                f"Remedies exhausted: {claim.remedies_exhausted}"
            ],
            rule="exhaustion_doctrine"
        )
    
    missing = set(claim.remedies_sought) - set(claim.remedies_exhausted)
    return False, ProofObject(
        conclusion=f"VIOLATION: Administrative remedies not exhausted",
        premises=[
            f"Remedies sought: {claim.remedies_sought}",
            f"Remedies exhausted: {claim.remedies_exhausted}",
            f"Missing: {missing}"
        ],
        rule="exhaustion_doctrine"
    )


def check_chevron_step_one(rule: Rulemaking) -> Tuple[bool, ProofObject]:
    """
    Chevron Step 1: Has Congress spoken directly to the precise 
    question at issue? If yes, statutory language controls.
    
    Returns False if agency interpreted unambiguous statute.
    """
    if not rule.statutory_ambiguity:
        # Statute is unambiguous — agency cannot reinterpret
        return False, ProofObject(
            conclusion="VIOLATION: Agency interpreted unambiguous statute",
            premises=[
                "Statutory ambiguity: False",
                "Chevron Step 1: Congress spoke directly"
            ],
            rule="chevron_step_one"
        )
    
    return True, ProofObject(
        conclusion="Statute ambiguous — Chevron deference may apply",
        premises=["Statutory ambiguity confirmed"],
        rule="chevron_step_one"
    )


def check_finality(rule: Rulemaking) -> Tuple[bool, ProofObject]:
    """
    Bennett v. Spear (1997) — Final agency action test:
    1. Action marks consummation of agency decision-making
    2. Action is one by which rights/obligations determined
    """
    has_final_date = rule.final_rule_date is not None
    has_effective_date = rule.effective_date is not None
    
    if not has_final_date:
        return False, ProofObject(
            conclusion="Not final: No final rule date",
            premises=["Rule lacks final_rule_date"],
            rule="finality_test_consummation"
        )
    
    if not has_effective_date:
        return False, ProofObject(
            conclusion="Not final: No legal effect (no effective_date)",
            premises=["Rule lacks effective_date"],
            rule="finality_test_legal_consequences"
        )
    
    return True, ProofObject(
        conclusion="Final agency action — ripe for review",
        premises=[
            f"Final rule date: {rule.final_rule_date}",
            f"Effective date: {rule.effective_date}"
        ],
        rule="finality_test"
    )


def check_record_based_decision(
    rule: Rulemaking, 
    comments_required: int = 1
) -> Tuple[bool, ProofObject]:
    """
    Camp v. Pitts (1972) — Agency decision must be based on 
    the administrative record. No ex parte contacts.
    
    Minimal check: At least some public participation recorded.
    """
    comment_count = rule.get_comment_count()
    
    if comment_count < comments_required:
        return False, ProofObject(
            conclusion=f"VIOLATION: Insufficient record ({comment_count} comments)",
            premises=[
                f"Comments received: {comment_count}",
                f"Minimum required: {comments_required}"
            ],
            rule="record_based_decision"
        )
    
    return True, ProofObject(
        conclusion="Administrative record adequate",
        premises=[f"Comments in record: {comment_count}"],
        rule="record_based_decision"
    )


def run_all_invariants(rule: Rulemaking, claim: ExhaustionClaim) -> List[Tuple[str, bool, ProofObject]]:
    """Run all administrative law invariants and return results."""
    results = []
    
    results.append(("notice_period", *check_notice_period(rule)))
    results.append(("exhaustion", *check_exhaustion(claim)))
    results.append(("chevron_step_one", *check_chevron_step_one(rule)))
    results.append(("finality", *check_finality(rule)))
    results.append(("record_based", *check_record_based_decision(rule)))
    
    return results
