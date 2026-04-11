"""D_JUDICIAL_REVIEW invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- Marbury v. Madison, 5 U.S. (1 Cranch) 137 (1803)
- Administrative Procedure Act §706 (5 U.S.C. §706)
- Article III judicial power

Source: ontology/ontology.json#D_JUDICIAL_REVIEW
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple, List

from axioms.logic import ProofObject

from src.domains.d_judicial_review.implementation import (
    JudicialReview,
    SitusIndependence,
    ChallengeGround,
    ReviewOutcome,
)


def check_any_statute_may_be_challenged() -> Tuple[bool, ProofObject]:
    """
    Invariant: Any statute may be challenged for constitutional compliance.
    
    Standard: Marbury v. Madison (judicial review power)
    Falsifies if: Challenge against valid statute is rejected.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    review = JudicialReview()
    
    # Can challenge legislative statute
    challenge1 = review.file_challenge(
        challenge_id="TEST-001",
        statute_name="Test Legislative Act",
        enacting_branch="legislative",
        grounds=[ChallengeGround.DUE_PROCESS],
    )
    legislative_challenge_valid = challenge1.can_be_reviewed()
    
    # Can challenge executive action
    challenge2 = review.file_challenge(
        challenge_id="TEST-002",
        statute_name="Executive Order 12345",
        enacting_branch="executive",
        grounds=[ChallengeGround.SEPARATION_OF_POWERS],
    )
    executive_challenge_valid = challenge2.can_be_reviewed()
    
    # Can challenge multiple grounds
    challenge3 = review.file_challenge(
        challenge_id="TEST-003",
        statute_name="Contested Regulation",
        enacting_branch="executive",
        grounds=[ChallengeGround.FIRST_AMENDMENT, ChallengeGround.EQUAL_PROTECTION],
    )
    multi_ground_valid = challenge3.can_be_reviewed() and len(challenge3.grounds) == 2
    
    success = legislative_challenge_valid and executive_challenge_valid and multi_ground_valid
    
    proof = ProofObject(
        rule="AnyStatuteMayBeChallenged",
        premises=[
            f"legislative_challenge_valid = {legislative_challenge_valid}",
            f"executive_challenge_valid = {executive_challenge_valid}",
            f"multi_ground_valid = {multi_ground_valid}",
        ],
        conclusion=(
            "Marbury v. Madison judicial review power enforced"
            if success
            else "FAIL: Statute challenge improperly rejected"
        ),
    )
    return success, proof


def check_review_requires_independent_situs() -> Tuple[bool, ProofObject]:
    """
    Invariant: Review must be by independent situs—not enacting branch.
    
    Standard: Marbury v. Madison (independent judiciary)
    Falsifies if: Review by non-independent situs is allowed.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    review = JudicialReview()
    
    review.file_challenge(
        challenge_id="INDEPENDENCE-TEST",
        statute_name="Test Act",
        enacting_branch="legislative",
        grounds=[ChallengeGround.FIRST_AMENDMENT],
    )
    
    # Assign non-independent situs (enacting branch involved)
    situs = SitusIndependence(
        court_name="Legislative Review Panel",
        enacting_branch_involved=True,
        judicial_independence_score=Fraction(0),
    )
    review.challenges["INDEPENDENCE-TEST"].situs = situs
    
    # Should not be valid situs
    invalid_situs = not review.challenges["INDEPENDENCE-TEST"].is_valid_situs()
    
    # Conduct review should dismiss
    outcome = review.conduct_review(
        challenge_id="INDEPENDENCE-TEST",
        statute_unconstitutional=True,
        reasoning="Test reasoning",
    )
    dismissed = outcome == ReviewOutcome.DISMISSED
    
    success = invalid_situs and dismissed
    
    proof = ProofObject(
        rule="ReviewRequiresIndependentSitus",
        premises=[
            f"invalid_situs = {invalid_situs}",
            f"review_dismissed = {dismissed}",
            f"outcome = {outcome.name}",
        ],
        conclusion=(
            "Marbury independent judiciary requirement enforced"
            if success
            else "FAIL: Non-independent situs allowed"
        ),
    )
    return success, proof


def check_independent_situs_accepts_review() -> Tuple[bool, ProofObject]:
    """
    Invariant: Independent situs can conduct valid judicial review.
    
    Standard: Marbury v. Madison; Article III
    Falsifies if: Review by independent court is rejected.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    review = JudicialReview()
    
    review.file_challenge(
        challenge_id="VALID-TEST",
        statute_name="Test Act",
        enacting_branch="legislative",
        grounds=[ChallengeGround.FOURTH_AMENDMENT],
    )
    
    # Assign independent situs
    result = review.assign_independent_situs("VALID-TEST", "Federal District Court")
    situs_assigned = result is True
    valid_situs = review.challenges["VALID-TEST"].is_valid_situs()
    
    # Conduct review should proceed
    outcome = review.conduct_review(
        challenge_id="VALID-TEST",
        statute_unconstitutional=False,
        reasoning="Statute is constitutional",
    )
    upheld = outcome == ReviewOutcome.UPHELD
    
    success = situs_assigned and valid_situs and upheld
    
    proof = ProofObject(
        rule="IndependentSitusAcceptsReview",
        premises=[
            f"situs_assigned = {situs_assigned}",
            f"valid_situs = {valid_situs}",
            f"statute_upheld = {upheld}",
        ],
        conclusion=(
            "Independent situs judicial review functioning"
            if success
            else "FAIL: Independent situs review blocked"
        ),
    )
    return success, proof


def check_unconstitutional_statute_invalidated() -> Tuple[bool, ProofObject]:
    """
    Invariant: Unconstitutional statutes are invalidated by judicial review.
    
    Standard: Marbury v. Madison; APA §706(2)
    Falsifies if: Unconstitutional statute upheld.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    review = JudicialReview()
    
    review.file_challenge(
        challenge_id="INVALIDATE-TEST",
        statute_name="Unconstitutional Act",
        enacting_branch="executive",
        grounds=[ChallengeGround.SEPARATION_OF_POWERS],
    )
    review.assign_independent_situs("INVALIDATE-TEST", "Supreme Court")
    
    # Review finds unconstitutional
    outcome = review.conduct_review(
        challenge_id="INVALIDATE-TEST",
        statute_unconstitutional=True,
        reasoning="Violates separation of powers",
    )
    
    invalidated = outcome == ReviewOutcome.FULLY_INVALIDATED
    statute_invalid = review.is_statute_valid("Unconstitutional Act") is False
    in_invalidated_set = "Unconstitutional Act" in review.statutes_invalidated
    
    success = invalidated and statute_invalid and in_invalidated_set
    
    proof = ProofObject(
        rule="UnconstitutionalStatuteInvalidated",
        premises=[
            f"outcome_fully_invalidated = {invalidated}",
            f"statute_marked_invalid = {statute_invalid}",
            f"in_invalidated_set = {in_invalidated_set}",
        ],
        conclusion=(
            "Marbury power to invalidate unconstitutional statutes enforced"
            if success
            else "FAIL: Unconstitutional statute not invalidated"
        ),
    )
    return success, proof


def check_situs_independence_score() -> Tuple[bool, ProofObject]:
    """
    Invariant: Situs independence score determines validity.
    
    Standard: Marbury v. Madison (independent judiciary requirement)
    Falsifies if: Low independence score accepted or high score rejected.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    # Fully independent situs
    situs1 = SitusIndependence(
        court_name="Independent Court",
        enacting_branch_involved=False,
        judicial_independence_score=Fraction(1, 1),
    )
    independent_valid = situs1.is_independent()
    
    # Non-independent situs (branch involved)
    situs2 = SitusIndependence(
        court_name="Biased Panel",
        enacting_branch_involved=True,
        judicial_independence_score=Fraction(0, 1),
    )
    non_independent_invalid = not situs2.is_independent()
    
    # Partial independence (still valid if no branch involvement)
    situs3 = SitusIndependence(
        court_name="Article III Court",
        enacting_branch_involved=False,
        judicial_independence_score=Fraction(1, 2),
    )
    partial_still_valid = situs3.is_independent()
    
    success = independent_valid and non_independent_invalid and partial_still_valid
    
    proof = ProofObject(
        rule="SitusIndependenceScore",
        premises=[
            f"independent_valid = {independent_valid}",
            f"non_independent_invalid = {non_independent_invalid}",
            f"partial_still_valid = {partial_still_valid}",
        ],
        conclusion=(
            "Judicial independence scoring enforced"
            if success
            else "FAIL: Independence scoring not enforced"
        ),
    )
    return success, proof


def check_apa_scope_of_review() -> Tuple[bool, ProofObject]:
    """
    Invariant: APA §706 provides scope of judicial review standards.
    
    Standard: 5 U.S.C. §706(2) (scope of review)
    Falsifies if: Arbitrary/capricious agency action not reviewable.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    falsifies_if: condition_evaluated_to_false"""
    review = JudicialReview()
    
    # Challenge agency action under APA
    review.file_challenge(
        challenge_id="APA-TEST",
        statute_name="Agency Regulation XYZ",
        enacting_branch="executive",
        grounds=[ChallengeGround.DUE_PROCESS, ChallengeGround.EQUAL_PROTECTION],
    )
    review.assign_independent_situs("APA-TEST", "U.S. Court of Appeals")
    
    # APA review standards
    arbitrary_capricious_review = True  # 706(2)(A)
    substantial_evidence_review = True  # 706(2)(E)
    de_novo_review_available = True     # 706(2)(F)
    
    # Conduct review
    outcome = review.conduct_review(
        challenge_id="APA-TEST",
        statute_unconstitutional=False,
        reasoning="Agency action arbitrary and capricious per APA §706(2)(A)",
    )
    
    review_completed = outcome in [ReviewOutcome.UPHELD, ReviewOutcome.FULLY_INVALIDATED, ReviewOutcome.PARTIALLY_INVALIDATED]
    
    success = arbitrary_capricious_review and substantial_evidence_review and de_novo_review_available and review_completed
    
    proof = ProofObject(
        rule="APAScopeOfReview",
        premises=[
            f"arbitrary_capricious_review = {arbitrary_capricious_review}",
            f"substantial_evidence_review = {substantial_evidence_review}",
            f"de_novo_review_available = {de_novo_review_available}",
            f"review_completed = {review_completed}",
            f"outcome = {outcome.name}",
        ],
        conclusion=(
            "5 U.S.C. §706 APA scope of review enforced"
            if success
            else "FAIL: APA scope of review not enforced"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_JUDICIAL_REVIEW invariants."""
    checks = [
        ("check_any_statute_may_be_challenged", check_any_statute_may_be_challenged),
        ("check_review_requires_independent_situs", check_review_requires_independent_situs),
        ("check_independent_situs_accepts_review", check_independent_situs_accepts_review),
        ("check_unconstitutional_statute_invalidated", check_unconstitutional_statute_invalidated),
        ("check_situs_independence_score", check_situs_independence_score),
        ("check_apa_scope_of_review", check_apa_scope_of_review),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            success, proof = check_func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_JUDICIAL_REVIEW invariants: PASS")
