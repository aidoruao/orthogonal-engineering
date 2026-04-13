#!/usr/bin/env python3
"""Election Law Invariants — Eligibility, custody, recounts."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    BallotCustodyRecord,
    BallotCustodyTracker,
    ElectionResult,
    EligibilityVerifier,
    RecountAnalyzer,
    Voter,
)


def check_one_person_one_vote(verifier: EligibilityVerifier) -> Tuple[bool, ProofObject]:
    """One person, one vote: eligible voters must not have voted yet.

    Falsifies if: voter has already voted or is not registered.
    falsifies_if: voter has already voted or is not registered.
    """
    if verifier.voter.voted:
        return False, ProofObject(
            conclusion="VIOLATION: Voter already voted",
            premises=[],
            rule="one_person_one_vote"
        )
    
    if not verifier.voter.registered:
        return False, ProofObject(
            conclusion="VIOLATION: Voter not registered",
            premises=[],
            rule="voter_registration"
        )
    
    return True, ProofObject(
        conclusion="Voter eligible (registered, not yet voted)",
        premises=[],
        rule="one_person_one_vote"
    )


def check_custody_chain_unbroken(tracker: BallotCustodyTracker) -> Tuple[bool, ProofObject]:
    """Ballot chain of custody must be unbroken.

    Falsifies if: chain_unbroken() is False or ballot_count_consistent() is False.
    falsifies_if: chain_unbroken() is False or ballot_count_consistent() is False.
    """
    if not tracker.chain_unbroken():
        return False, ProofObject(
            conclusion="VIOLATION: Chain of custody broken",
            premises=[],
            rule="custody_chain"
        )
    
    if not tracker.ballot_count_consistent():
        return False, ProofObject(
            conclusion="VIOLATION: Ballot count inconsistency in custody chain",
            premises=[],
            rule="custody_count"
        )
    
    return True, ProofObject(
        conclusion="Chain of custody intact",
        premises=[f"Links: {len(tracker.custody_chain)}"],
        rule="custody_chain"
    )


def check_recount_threshold(analyzer: RecountAnalyzer) -> Tuple[bool, ProofObject]:
    """Recount triggered when margin < 0.5%.

    Falsifies if: analyzer.recount_required() is True.
    falsifies_if: analyzer.recount_required() is True.
    """
    margin = analyzer.winning_margin()
    threshold = analyzer.RECOUNT_THRESHOLD_PCT
    
    if analyzer.recount_required():
        return False, ProofObject(
            conclusion=f"RECOUNT REQUIRED: Margin {margin*100}% < {threshold}% threshold",
            premises=[],
            rule="recount_threshold"
        )
    
    return True, ProofObject(
        conclusion=f"Recount not required (margin {margin*100}% >= {threshold}%)",
        premises=[],
        rule="recount_threshold"
    )


def check_eligibility_before_voting(verifier: EligibilityVerifier) -> Tuple[bool, ProofObject]:
    """Eligibility must be verified before voting.

    Falsifies if: verifier.is_eligible() is False.
    falsifies_if: verifier.is_eligible() is False.
    """
    if not verifier.is_eligible():
        return False, ProofObject(
            conclusion="VIOLATION: Ineligible voter attempting to vote",
            premises=[f"Registered: {verifier.voter.registered}", f"Already voted: {verifier.voter.voted}"],
            rule="eligibility_verification"
        )
    
    return True, ProofObject(
        conclusion="Eligibility verified",
        premises=[],
        rule="eligibility_verification"
    )


def run_all_invariants() -> dict:
    """Run all D_ELECTION_LAW invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    ballot_custody_tracker = BallotCustodyTracker(
        ballot_batch_id="ELECTION-001",
        custody_chain=[BallotCustodyRecord(
        timestamp=None,
        location="Sample Location",
        custodian="SAMPLE",
        ballot_count=1,
        seal_number="SAMPLE",
    )],
    )
    eligibility_verifier = EligibilityVerifier(
        voter=Voter(
        voter_id="ELECTION-001",
    ),
    )
    recount_analyzer = RecountAnalyzer(
        results=[ElectionResult(
        candidate="ELECTION-001",
        votes=1,
    )],
        total_votes_cast=1,
    )

    checks = [
        ("check_custody_chain_unbroken", lambda: check_custody_chain_unbroken(ballot_custody_tracker)),
        ("check_eligibility_before_voting", lambda: check_eligibility_before_voting(eligibility_verifier)),
        ("check_one_person_one_vote", lambda: check_one_person_one_vote(eligibility_verifier)),
        ("check_recount_threshold", lambda: check_recount_threshold(recount_analyzer)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            result = func()
            if isinstance(result, tuple) and len(result) == 2:
                success, proof = result
                results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
            else:
                passed = getattr(result, "passed", True)
                results[name] = "PASS" if passed else "FAIL: " + str(getattr(result, "evidence", result))
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_ELECTION_LAW invariants: PASS")
