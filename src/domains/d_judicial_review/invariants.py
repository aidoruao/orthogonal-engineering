"""D_JUDICIAL_REVIEW invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: Marbury v. Madison (1803)
"""

from fractions import Fraction
from src.domains.d_judicial_review.implementation import (
    JudicialReview,
    SitusIndependence,
    ChallengeGround,
    ReviewOutcome,
    check_judicial_review_available,
)


def check_any_statute_can_be_challenged() -> bool:
    """
    Invariant: Any statute can be challenged for constitutional compliance.
    Falsification: If challenge against valid statute is rejected.
    """
    review = JudicialReview()
    
    # Can challenge legislative statute
    challenge = review.file_challenge(
        challenge_id="TEST-001",
        statute_name="Test Legislative Act",
        enacting_branch="legislative",
        grounds=[ChallengeGround.DUE_PROCESS],
    )
    assert challenge.can_be_reviewed()
    
    # Can challenge executive action
    challenge = review.file_challenge(
        challenge_id="TEST-002",
        statute_name="Executive Order 12345",
        enacting_branch="executive",
        grounds=[ChallengeGround.SEPARATION_OF_POWERS],
    )
    assert challenge.can_be_reviewed()
    
    return True


def check_review_requires_independent_situs() -> bool:
    """
    Invariant: Review must be by independent situs (not enacting branch).
    Falsification: If review by non-independent situs is allowed.
    """
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
    )
    review.challenges["INDEPENDENCE-TEST"].situs = situs
    
    # Should not be valid situs
    assert not review.challenges["INDEPENDENCE-TEST"].is_valid_situs(), (
        "Situs with enacting branch involvement should be invalid"
    )
    
    # Conduct review should dismiss
    outcome = review.conduct_review(
        challenge_id="INDEPENDENCE-TEST",
        statute_unconstitutional=True,
        reasoning="Test reasoning",
    )
    assert outcome == ReviewOutcome.DISMISSED, (
        "Review with invalid situs should be dismissed"
    )
    
    return True


def check_independent_situs_accepts_review() -> bool:
    """
    Invariant: Independent situs can conduct review.
    Falsification: If review by independent court is rejected.
    """
    review = JudicialReview()
    
    review.file_challenge(
        challenge_id="VALID-TEST",
        statute_name="Test Act",
        enacting_branch="legislative",
        grounds=[ChallengeGround.FOURTH_AMENDMENT],
    )
    
    # Assign independent situs
    result = review.assign_independent_situs("VALID-TEST", "Federal District Court")
    assert result is True
    assert review.challenges["VALID-TEST"].is_valid_situs()
    
    # Conduct review should proceed
    outcome = review.conduct_review(
        challenge_id="VALID-TEST",
        statute_unconstitutional=False,
        reasoning="Statute is constitutional",
    )
    assert outcome == ReviewOutcome.UPHELD
    
    return True


def check_unconstitutional_statute_invalidated() -> bool:
    """
    Invariant: Unconstitutional statutes are invalidated by review.
    Falsification: If unconstitutional statute is upheld.
    """
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
    
    assert outcome == ReviewOutcome.FULLY_INVALIDATED
    assert review.is_statute_valid("Unconstitutional Act") is False
    
    return True


def check_judicial_review_available_function() -> bool:
    """
    Invariant: Judicial review is available for all statutes.
    Falsification: If review availability check returns False.
    """
    assert check_judicial_review_available("Any Act", "legislative") is True
    assert check_judicial_review_available("Any Order", "executive") is True
    
    return True


def check_situs_independence_score() -> bool:
    """
    Invariant: Situs independence score determines validity.
    Falsification: If low independence score is accepted.
    """
    # Fully independent situs
    situs1 = SitusIndependence(
        court_name="Independent Court",
        enacting_branch_involved=False,
        judicial_independence_score=Fraction(1, 1),
    )
    assert situs1.is_independent()
    
    # Non-independent situs (branch involved)
    situs2 = SitusIndependence(
        court_name="Biased Panel",
        enacting_branch_involved=True,
        judicial_independence_score=Fraction(0, 1),
    )
    assert not situs2.is_independent()
    
    return True


def run_all_invariants() -> dict:
    """Run all D_JUDICIAL_REVIEW invariants."""
    checks = [
        check_any_statute_can_be_challenged,
        check_review_requires_independent_situs,
        check_independent_situs_accepts_review,
        check_unconstitutional_statute_invalidated,
        check_judicial_review_available_function,
        check_situs_independence_score,
    ]
    results = {}
    for check in checks:
        try:
            check()
            results[check.__name__] = "PASS"
        except AssertionError as e:
            results[check.__name__] = f"FAIL: {e}"
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if v != "PASS"]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_JUDICIAL_REVIEW invariants: PASS")
