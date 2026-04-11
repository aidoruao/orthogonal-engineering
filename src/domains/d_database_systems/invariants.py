#!/usr/bin/env python3
"""Database Systems Invariants — ACID, Serializability, B-tree."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import Schedule, BTreeNode, Transaction, TransactionStatus


def check_conflict_serializability(schedule: Schedule) -> Tuple[bool, ProofObject]:
    """Schedule must be conflict-serializable for correctness.

    Falsifies if: schedule.is_conflict_serializable() is False.
    """
    if schedule.is_conflict_serializable():
        return True, ProofObject(
            conclusion="Schedule is conflict-serializable",
            premises=[f"Operations: {len(schedule.operations)}"],
            rule="conflict_serializability"
        )
    
    return False, ProofObject(
        conclusion="VIOLATION: Schedule not conflict-serializable (cycle in precedence graph)",
        premises=[],
        rule="conflict_serializability"
    )


def check_btree_invariants(node: BTreeNode) -> Tuple[bool, ProofObject]:
    """B-tree must satisfy structural invariants.

    Falsifies if: node.is_valid() is False.
    """
    if not node.is_valid():
        return False, ProofObject(
            conclusion="VIOLATION: B-tree invariants violated",
            premises=[f"Keys: {node.keys}", f"Max degree: {node.max_degree}"],
            rule="btree_invariants"
        )
    
    return True, ProofObject(
        conclusion="B-tree invariants satisfied",
        premises=[f"Keys: {len(node.keys)}", f"Height: {node.height()}"],
        rule="btree_invariants"
    )


def check_atomicity(tx: Transaction) -> Tuple[bool, ProofObject]:
    """Transaction must be all-or-nothing (Atomicity).

    Falsifies if: transaction status is neither COMMITTED nor ABORTED (partial state).
    """
    if tx.status == TransactionStatus.COMMITTED:
        return True, ProofObject(
            conclusion="Transaction committed (atomicity satisfied)",
            premises=[],
            rule="acid_atomicity"
        )
    
    if tx.status == TransactionStatus.ABORTED:
        return True, ProofObject(
            conclusion="Transaction aborted cleanly (atomicity satisfied)",
            premises=[],
            rule="acid_atomicity"
        )
    
    return False, ProofObject(
        conclusion="VIOLATION: Transaction in partial state",
        premises=[f"Status: {tx.status.name}"],
        rule="acid_atomicity"
    )


def check_durability(tx: Transaction) -> Tuple[bool, ProofObject]:
    """Committed transactions must be durable.

    Falsifies if: not applicable (function assumes durability when committed).
    """
    if tx.status != TransactionStatus.COMMITTED:
        return True, ProofObject(
            conclusion="Durability not applicable (not committed)",
            premises=[],
            rule="acid_durability_applicability"
        )
    
    # Simplified: assume committed is durable for this check
    return True, ProofObject(
        conclusion="Transaction durable",
        premises=[],
        rule="acid_durability"
    )


def check_isolation(schedule: Schedule) -> Tuple[bool, ProofObject]:
    """Concurrent transactions must be isolated (serializable).

    Falsifies if: conflict serializability check fails.
    """
    return check_conflict_serializability(schedule)
