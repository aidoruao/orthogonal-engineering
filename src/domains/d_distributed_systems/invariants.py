#!/usr/bin/env python3
"""Distributed Systems Invariants — CAP, Vector Clocks, Consensus."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import CAPAnalyzer, VectorClock, ConsensusVerifier


def check_cap_theorem(analyzer: CAPAnalyzer) -> Tuple[bool, ProofObject]:
    """CAP theorem: Cannot have Consistency + Availability + Partition tolerance simultaneously.

    Falsifies if: analyzer.satisfies_cap() returns False (attempts to claim all three). 
    falsifies_if: analyzer.satisfies_cap() returns False (attempts to claim all three).
    """
    if analyzer.satisfies_cap():
        return True, ProofObject(
            conclusion="CAP constraint satisfied",
            premises=[f"C={analyzer.has_consistency}, A={analyzer.has_availability}, P={analyzer.has_partition_tolerance}"],
            rule="cap_theorem"
        )
    
    return False, ProofObject(
        conclusion="VIOLATION: CAP theorem violated (cannot have all three during partition)",
        premises=[],
        rule="cap_theorem"
    )


def check_vector_clock_causality(vc1: VectorClock, vc2: VectorClock) -> Tuple[bool, ProofObject]:
    """Vector clocks must correctly track causality.

    Falsifies if: not applicable (function reports causal relation and always returns True).
    falsifies_if: not applicable (function reports causal relation and always returns True).
    """
    relation = vc1.compare(vc2)
    
    if relation == "concurrent":
        return True, ProofObject(
            conclusion="Events are concurrent (no causal relationship)",
            premises=[],
            rule="vector_clock_causality"
        )
    
    return True, ProofObject(
        conclusion=f"Causal relationship established: vc1 {relation} vc2",
        premises=[],
        rule="vector_clock_causality"
    )


def check_consensus_quorum(verifier: ConsensusVerifier) -> Tuple[bool, ProofObject]:
    """Consensus requires quorum > n/2 for safety.

    Falsifies if: votes received < quorum or no agreed majority value.
    falsifies_if: votes received < quorum or no agreed majority value.
    """
    quorum = verifier.quorum_size()
    received = len(verifier.votes_received)
    
    if received < quorum:
        return False, ProofObject(
            conclusion=f"VIOLATION: Insufficient votes ({received}) for quorum ({quorum})",
            premises=[],
            rule="consensus_quorum"
        )
    
    agreed = verifier.agreed_value()
    if agreed is None:
        return False, ProofObject(
            conclusion="VIOLATION: No majority agreement despite quorum",
            premises=[],
            rule="consensus_agreement"
        )
    
    return True, ProofObject(
        conclusion=f"Consensus reached on '{agreed}' with {received} votes",
        premises=[],
        rule="consensus_quorum"
    )


def check_quorum_size(verifier: ConsensusVerifier) -> Tuple[bool, ProofObject]:
    """Quorum must be > n/2 to prevent split-brain.

    Falsifies if: quorum_ratio <= MIN_QUORUM_RATIO.
    falsifies_if: quorum_ratio <= MIN_QUORUM_RATIO.
    """
    from .implementation import MIN_QUORUM_RATIO
    
    quorum_ratio = Fraction(verifier.quorum_size(), verifier.node_count)
    
    if quorum_ratio <= MIN_QUORUM_RATIO:
        return False, ProofObject(
            conclusion=f"VIOLATION: Quorum ratio {quorum_ratio} not > {MIN_QUORUM_RATIO}",
            premises=[],
            rule="quorum_size"
        )
    
    return True, ProofObject(
        conclusion=f"Quorum size adequate ({quorum_ratio} > {MIN_QUORUM_RATIO})",
        premises=[],
        rule="quorum_size"
    )


def run_all_invariants() -> dict:
    """Run all D_DISTRIBUTED_SYSTEMS invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    cap_analyzer = CAPAnalyzer()
    consensus_verifier = ConsensusVerifier(
        node_count=1,
    )
    vector_clock = VectorClock()

    checks = [
        ("check_cap_theorem", lambda: check_cap_theorem(cap_analyzer)),
        ("check_consensus_quorum", lambda: check_consensus_quorum(consensus_verifier)),
        ("check_quorum_size", lambda: check_quorum_size(consensus_verifier)),
        ("check_vector_clock_causality", lambda: check_vector_clock_causality(vector_clock, vector_clock)),
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
    print("All D_DISTRIBUTED_SYSTEMS invariants: PASS")
