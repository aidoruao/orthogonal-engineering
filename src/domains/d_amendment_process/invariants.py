"""D_AMENDMENT_PROCESS invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: US Constitution Article V
"""

from fractions import Fraction
from src.domains.d_amendment_process.implementation import (
    AmendmentProcess,
    IndelibleClause,
    RatificationStatus,
    check_amendment_threshold,
)


def check_amendment_requires_congressional_supermajority() -> bool:
    """
    Invariant: Amendment requires 2/3 congressional approval.
    Falsification: If amendment with < 2/3 support is accepted.
    """
    process = AmendmentProcess()
    
    # Should succeed with 2/3 support
    two_thirds = Fraction(2, 3)
    proposal = process.propose_amendment(
        proposal_id="TEST-001",
        text="Test amendment",
        congressional_support=two_thirds,
    )
    assert proposal.status == RatificationStatus.CONGRESSIONALLY_APPROVED
    
    # Should fail with < 2/3 support
    try:
        process.propose_amendment(
            proposal_id="TEST-002",
            text="Test amendment 2",
            congressional_support=Fraction(1, 2),  # Simple majority only
        )
        assert False, "Should have rejected simple majority"
    except ValueError:
        pass  # Expected
    
    return True


def check_amendment_requires_three_fourths_states() -> bool:
    """
    Invariant: Amendment requires 3/4 of states (38/50).
    Falsification: If ratification with < 38 states succeeds.
    """
    process = AmendmentProcess()
    
    # Propose amendment
    process.propose_amendment(
        proposal_id="STATE-TEST",
        text="State ratification test",
        congressional_support=Fraction(2, 3),
    )
    
    # Ratify with 37 states (not enough)
    for i in range(37):
        ratified = process.ratify_by_state("STATE-TEST", f"State-{i}")
        assert not ratified, "Should not ratify with only 37 states"
    
    # 38th state triggers ratification
    ratified = process.ratify_by_state("STATE-TEST", "State-38")
    assert ratified, "Should ratify with 38th state"
    
    # Verify status
    proposal = process.proposals["STATE-TEST"]
    assert proposal.status == RatificationStatus.RATIFIED
    
    return True


def check_indelible_equal_state_suffrage() -> bool:
    """
    Invariant: Equal state suffrage in Senate cannot be amended without consent.
    Falsification: If amendment removing equal state suffrage is allowed.
    """
    process = AmendmentProcess()
    
    # Attempt to amend away equal state suffrage
    indelible = process.check_indelible_clause(
        "Amendment to remove equal suffrage in Senate for all states"
    )
    
    assert indelible == IndelibleClause.EQUAL_STATE_SUFFRAGE_IN_SENATE, (
        "Should detect indelible clause violation"
    )
    
    # Amendment with consent might be allowed (not implemented in this simplified version)
    # This would require per-state consent tracking
    
    return True


def check_indelible_amendment_process() -> bool:
    """
    Invariant: Amendment process itself cannot be abolished.
    Falsification: If amendment abolishing Article V is allowed.
    """
    process = AmendmentProcess()
    
    # Attempt to abolish amendment process
    indelible = process.check_indelible_clause(
        "Amendment to abolish the amendment process and end Article V"
    )
    
    assert indelible == IndelibleClause.AMENDMENT_PROCESS_ITSELF, (
        "Should detect attempt to abolish amendment process"
    )
    
    return True


def check_amendment_validity_report() -> bool:
    """
    Invariant: Valid amendment reports correct status.
    Falsification: If validity check returns wrong information.
    """
    process = AmendmentProcess()
    
    process.propose_amendment(
        proposal_id="VALID-TEST",
        text="Valid amendment text",
        congressional_support=Fraction(2, 3),
    )
    
    # Ratify with 38 states
    for i in range(38):
        process.ratify_by_state("VALID-TEST", f"State-{i}")
    
    result = process.is_amendment_valid("VALID-TEST")
    
    assert result["valid"] is True
    assert result["threshold_met"] is True
    assert result["status"] == "RATIFIED"
    
    return True


def check_threshold_calculation() -> bool:
    """
    Invariant: Threshold calculation is correct (3/4 = 38/50).
    Falsification: If threshold calculation is incorrect.
    """
    # 37 states is not enough
    assert not check_amendment_threshold(37)
    
    # 38 states is the threshold
    assert check_amendment_threshold(38)
    
    # 50 states is obviously enough
    assert check_amendment_threshold(50)
    
    # 0 states is not enough
    assert not check_amendment_threshold(0)
    
    return True


def run_all_invariants() -> dict:
    """Run all D_AMENDMENT_PROCESS invariants."""
    checks = [
        check_amendment_requires_congressional_supermajority,
        check_amendment_requires_three_fourths_states,
        check_indelible_equal_state_suffrage,
        check_indelible_amendment_process,
        check_amendment_validity_report,
        check_threshold_calculation,
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
    print("All D_AMENDMENT_PROCESS invariants: PASS")
