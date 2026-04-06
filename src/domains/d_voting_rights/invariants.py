"""D_VOTING_RIGHTS invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: 15th, 19th, 24th, 26th Amendments
"""

from src.domains.d_voting_rights.implementation import (
    VotingRightsChecker,
    Voter,
    VotingRightViolation,
    check_voting_rights,
)


def check_15th_amendment_no_racial_discrimination() -> bool:
    """
    Invariant: 15th Amendment prohibits racial discrimination in voting.
    Falsification: If procedure denying vote based on race is not flagged.
    """
    checker = VotingRightsChecker()
    
    result = checker.check_15th_amendment_compliance(
        "Voting denied based on race or color"
    )
    
    assert result is False, (
        "Racial discrimination should violate 15th Amendment"
    )
    assert VotingRightViolation.RACIAL_DISCRIMINATION in checker.violations
    
    return True


def check_19th_amendment_no_sex_discrimination() -> bool:
    """
    Invariant: 19th Amendment prohibits sex discrimination in voting.
    Falsification: If procedure denying vote based on sex is not flagged.
    """
    checker = VotingRightsChecker()
    
    result = checker.check_19th_amendment_compliance(
        "Voting denied on account of sex"
    )
    
    assert result is False, (
        "Sex discrimination should violate 19th Amendment"
    )
    assert VotingRightViolation.SEX_DISCRIMINATION in checker.violations
    
    return True


def check_26th_amendment_age_18() -> bool:
    """
    Invariant: 26th Amendment guarantees vote for 18+ citizens.
    Falsification: If 18-year-old citizen is denied right to vote.
    """
    checker = VotingRightsChecker()
    
    voter = checker.register_voter(
        voter_id="TEST-18YO",
        age=18,
        is_citizen=True,
    )
    
    assert voter.has_right_to_vote() is True, (
        "18-year-old citizen should have right to vote"
    )
    
    # Check eligibility
    result = checker.check_voting_eligibility("TEST-18YO")
    assert result["eligible"] is True
    
    return True


def check_under_18_cannot_vote() -> bool:
    """
    Invariant: Under 18 cannot vote (26th Amendment).
    Falsification: If 17-year-old is allowed to vote.
    """
    checker = VotingRightsChecker()
    
    voter = checker.register_voter(
        voter_id="TEST-17YO",
        age=17,
        is_citizen=True,
    )
    
    assert voter.has_right_to_vote() is False, (
        "17-year-old should not have right to vote"
    )
    
    return True


def check_non_citizen_cannot_vote() -> bool:
    """
    Invariant: Non-citizens cannot vote in federal elections.
    Falsification: If non-citizen is allowed to vote.
    """
    checker = VotingRightsChecker()
    
    voter = checker.register_voter(
        voter_id="TEST-NON-CITIZEN",
        age=25,
        is_citizen=False,
    )
    
    assert voter.has_right_to_vote() is False, (
        "Non-citizen should not have right to vote"
    )
    
    return True


def check_vote_verification() -> bool:
    """
    Invariant: Vote is recorded as cast and verifiable.
    Falsification: If vote cannot be verified against tampering.
    """
    checker = VotingRightsChecker()
    
    # Register and cast ballot
    checker.register_voter("VOTER-001", age=25, is_citizen=True)
    ballot = checker.cast_ballot(
        voter_id="VOTER-001",
        selections={"President": "Candidate A", "Senator": "Candidate B"},
    )
    
    # Verify ballot integrity
    assert ballot.verify_integrity() is True, (
        "Ballot should verify immediately after casting"
    )
    
    # Verify vote matches intent
    verification = checker.verify_vote(
        ballot_id=ballot.ballot_id,
        expected_selections={"President": "Candidate A", "Senator": "Candidate B"},
    )
    
    assert verification.matches_voter_intent(
        {"President": "Candidate A", "Senator": "Candidate B"}
    ), "Vote should match voter intent"
    
    return True


def check_poll_tax_prohibited() -> bool:
    """
    Invariant: 24th Amendment prohibits poll taxes.
    Falsification: If poll tax is not flagged as violation.
    """
    checker = VotingRightsChecker()
    
    # Register voter who hasn't paid poll tax
    voter = checker.register_voter(
        voter_id="TEST-POLL-TAX",
        age=25,
        is_citizen=True,
    )
    voter.has_paid_poll_tax = False
    
    # Check eligibility - should flag poll tax
    result = checker.check_voting_eligibility("TEST-POLL-TAX")
    
    # Poll tax requirement violates 24th Amendment
    has_poll_tax_violation = any(
        v == VotingRightViolation.POLL_TAX for v in result["violations"]
    )
    assert has_poll_tax_violation, (
        "Poll tax should be flagged as 24th Amendment violation"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all D_VOTING_RIGHTS invariants."""
    checks = [
        check_15th_amendment_no_racial_discrimination,
        check_19th_amendment_no_sex_discrimination,
        check_26th_amendment_age_18,
        check_under_18_cannot_vote,
        check_non_citizen_cannot_vote,
        check_vote_verification,
        check_poll_tax_prohibited,
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
    print("All D_VOTING_RIGHTS invariants: PASS")
