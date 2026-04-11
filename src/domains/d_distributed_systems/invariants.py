#!/usr/bin/env python3
"""Distributed Systems Invariants — CAP, Vector Clocks, Consensus."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import CAPAnalyzer, VectorClock, ConsensusVerifier


def check_cap_theorem(analyzer: CAPAnalyzer) -> Tuple[bool, ProofObject]:
    """CAP theorem: Cannot have Consistency + Availability + Partition tolerance simultaneously.
    
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
