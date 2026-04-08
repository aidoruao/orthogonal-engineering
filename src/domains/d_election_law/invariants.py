"""D_ELECTION_LAW invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: Voting Rights Act, Help America Vote Act (HAVA)
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import List, Set
from datetime import datetime


@dataclass
class Voter:
    """Registered voter."""
    voter_id: str
    name: str
    age: int
    citizenship: str
    registered: bool
    registration_date: datetime
    felon_status: bool  # True = ineligible in some states


@dataclass
class Ballot:
    """Election ballot."""
    ballot_id: str
    election_id: str
    voter_id: str
    timestamp: datetime
    selections: List[str]


@dataclass
class ElectionResult:
    """Election results for recount check."""
    election_id: str
    total_votes: int
    margin_votes: int
    margin_percent: Fraction
    recount_threshold: Fraction


def check_voter_eligibility() -> bool:
    """
    Invariant: Voter must be 18+, citizen, registered to vote.
    Falsification: If underage or non-citizen allowed to vote.
    """
    # Eligible voter
    eligible = Voter(
        voter_id="V001",
        name="Eligible Citizen",
        age=35,
        citizenship="US",
        registered=True,
        registration_date=datetime(2020, 1, 1),
        felon_status=False,
    )
    
    assert eligible.age >= 18, "Voter must be at least 18"
    assert eligible.citizenship == "US", "Voter must be US citizen"
    assert eligible.registered is True, "Voter must be registered"
    
    # Ineligible - underage
    underage = Voter(
        voter_id="V002",
        name="Young Person",
        age=16,
        citizenship="US",
        registered=True,
        registration_date=datetime(2024, 1, 1),
        felon_status=False,
    )
    
    assert underage.age >= 18, (
        f"Voter {underage.name} underage: {underage.age} < 18"
    )
    
    return True


def check_ballot_uniqueness() -> bool:
    """
    Invariant: Each ballot has unique ID, no duplicates in count.
    Falsification: If duplicate ballot IDs found in election.
    """
    ballots = [
        Ballot("B001", "E2024", "V001", datetime.now(), ["Candidate A"]),
        Ballot("B002", "E2024", "V002", datetime.now(), ["Candidate B"]),
        Ballot("B003", "E2024", "V003", datetime.now(), ["Candidate A"]),
        Ballot("B001", "E2024", "V004", datetime.now(), ["Candidate B"]),  # Duplicate ID!
    ]
    
    ballot_ids = [b.ballot_id for b in ballots]
    unique_ids = set(ballot_ids)
    
    assert len(ballot_ids) == len(unique_ids), (
        f"Duplicate ballot IDs found: {len(ballot_ids)} ballots, "
        f"only {len(unique_ids)} unique IDs"
    )
    
    return True


def check_recount_threshold() -> bool:
    """
    Invariant: Margin < 0.5% triggers automatic recount.
    Falsification: If 0.4% margin doesn't trigger recount.
    """
    # Close election requiring recount
    close_election = ElectionResult(
        election_id="E2024",
        total_votes=100000,
        margin_votes=400,
        margin_percent=Fraction(4, 10),  # 0.4%
        recount_threshold=Fraction(5, 10),  # 0.5%
    )
    
    assert close_election.margin_percent < close_election.recount_threshold, (
        f"Margin {float(close_election.margin_percent)*100}% below "
        f"threshold {float(close_election.recount_threshold)*100}%, recount required"
    )
    
    # Clear win - no recount needed
    clear_win = ElectionResult(
        election_id="E2024_2",
        total_votes=100000,
        margin_votes=10000,
        margin_percent=Fraction(10),  # 10%
        recount_threshold=Fraction(5, 10),  # 0.5%
    )
    
    assert clear_win.margin_percent >= clear_win.recount_threshold, (
        f"Margin {float(clear_win.margin_percent)*100}% above threshold, no recount"
    )
    
    return True


def check_no_felon_voting() -> bool:
    """
    Invariant: Convicted felons (in disenfranchising states) cannot vote.
    Falsification: If felon allowed to vote where prohibited.
    """
    # Note: This varies by state - some allow post-sentence voting
    # Checking for state where felons are disenfranchised
    felon = Voter(
        voter_id="V003",
        name="Convicted Felon",
        age=40,
        citizenship="US",
        registered=False,  # Should not be registered
        registration_date=datetime(2020, 1, 1),
        felon_status=True,
    )
    
    # In states with disenfranchisement
    state_felon_disenfranchisement = True
    
    if state_felon_disenfranchisement and felon.felon_status:
        assert felon.registered is False, (
            f"Felon {felon.name} should not be registered in "
            f"disenfranchising jurisdiction"
        )
    
    return True


def check_voter_registration_deadline() -> bool:
    """
    Invariant: Voter registration must occur before deadline.
    Falsification: If same-day registration not allowed but voter registered.
    """
    election_date = datetime(2024, 11, 5)
    registration_deadline = election_date - timedelta(days=30)  # 30 days before
    
    voter = Voter(
        voter_id="V004",
        name="Late Registrant",
        age=30,
        citizenship="US",
        registered=True,
        registration_date=datetime(2024, 10, 20),  # 16 days before - after deadline
        felon_status=False,
    )
    
    assert voter.registration_date <= registration_deadline, (
        f"Voter {voter.name} registered {voter.registration_date}, "
        f"after deadline {registration_deadline}"
    )
    
    return True


def check_one_person_one_vote() -> bool:
    """
    Invariant: Each voter casts exactly one ballot.
    Falsification: If voter has multiple ballots in same election.
    """
    ballots = [
        Ballot("B001", "E2024", "V001", datetime.now(), ["Candidate A"]),
        Ballot("B002", "E2024", "V005", datetime.now(), ["Candidate B"]),
        Ballot("B003", "E2024", "V001", datetime.now(), ["Candidate C"]),  # V001 votes twice!
    ]
    
    voter_counts = {}
    for ballot in ballots:
        voter_counts[ballot.voter_id] = voter_counts.get(ballot.voter_id, 0) + 1
    
    for voter_id, count in voter_counts.items():
        assert count <= 1, (
            f"Voter {voter_id} cast {count} ballots, violates one-person-one-vote"
        )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("voter_eligibility", check_voter_eligibility),
        ("ballot_uniqueness", check_ballot_uniqueness),
        ("recount_threshold", check_recount_threshold),
        ("felon_voting", check_no_felon_voting),
        ("registration_deadline", check_voter_registration_deadline),
        ("one_person_one_vote", check_one_person_one_vote),
    ]
    
    for name, check_func in checks:
        try:
            check_func()
            results[name] = "PASS"
        except AssertionError as e:
            results[name] = f"FAIL: {e}"
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
    print("All D_ELECTION_LAW invariants: PASS")
