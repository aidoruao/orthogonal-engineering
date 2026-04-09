"""Memory Models — Sequential consistency, TSO, release-acquire.

Formalizes memory ordering guarantees for concurrent systems.
All operations return (result, ProofObject) pairs.

Mathematical foundation: Lamport, "How to Make a Multiprocessor
Computer That Correctly Executes Multiprocess Programs"
Biblical: Psalm 139:16 — "All the days ordained for me were
written in your book before one of them came to be."
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Optional, Dict, Set
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject


class OpType(Enum):
    """Type of memory operation."""
    READ = auto()
    WRITE = auto()
    FENCE = auto()
    ACQUIRE = auto()  # Lock/mutex acquire
    RELEASE = auto()  # Lock/mutex release


@dataclass(frozen=True)
class MemoryOperation:
    """A single memory operation.
    
    Tracks the thread, operation type, address, value, and timestamp.
    """
    thread_id: str
    op_type: OpType
    address: str
    value: Optional[Fraction]
    timestamp: Fraction
    
    def __str__(self) -> str:
        val_str = f"={self.value}" if self.value is not None else ""
        return f"{self.thread_id}:{self.op_type.name}({self.address}{val_str})@{self.timestamp}"


@dataclass
class MemoryOrder:
    """A sequence of memory operations forming an execution trace."""
    operations: List[MemoryOperation] = field(default_factory=list)
    
    def add_operation(self, op: MemoryOperation) -> None:
        """Add an operation to the order."""
        self.operations.append(op)
    
    def get_operations_to_address(self, address: str) -> List[MemoryOperation]:
        """Get all operations targeting a specific address."""
        return [op for op in self.operations if op.address == address]
    
    def get_operations_by_thread(self, thread_id: str) -> List[MemoryOperation]:
        """Get all operations from a specific thread."""
        return [op for op in self.operations if op.thread_id == thread_id]


def check_sequential_consistency(order: MemoryOrder) -> Tuple[bool, ProofObject]:
    """Check if execution is sequentially consistent.
    
    Sequential consistency requires:
    1. All threads observe the same total order of operations
    2. For each read, the value equals the most recent write to that address
    
    Args:
        order: The memory order to check
    
    Returns:
        (is_sc, proof)
    """
    if not order.operations:
        return True, ProofObject(
            rule="SequentialConsistency",
            premises=["no operations"],
            conclusion="trivially consistent"
        )
    
    # Track last write to each address
    last_write: Dict[str, Fraction] = {}
    violations = []
    
    for op in order.operations:
        if op.op_type == OpType.WRITE:
            if op.value is not None:
                last_write[op.address] = op.value
        
        elif op.op_type == OpType.READ:
            if op.address in last_write:
                expected = last_write[op.address]
                if op.value != expected:
                    violations.append(
                        f"Read at {op.address}: expected {expected}, got {op.value}"
                    )
            # If no prior write, read is uninitialized (allowed in some models)
    
    is_sc = len(violations) == 0
    
    proof = ProofObject(
        rule="SequentialConsistency",
        premises=[
            f"operations={len(order.operations)}",
            f"addresses={len(last_write)}",
            f"violations={len(violations)}"
        ],
        conclusion=f"is_sc={is_sc}"
    )
    
    return is_sc, proof


def check_happens_before(op_a: MemoryOperation,
                         op_b: MemoryOperation,
                         program_order: Dict[str, List[MemoryOperation]]) -> Tuple[bool, ProofObject]:
    """Check if operation a happens-before operation b.
    
    Happens-before relations:
    1. Program order: a and b in same thread, a precedes b
    2. Synchronization: a is release, b is acquire, same location
    3. Transitivity: a hb b and b hb c implies a hb c
    
    Args:
        op_a: First operation
        op_b: Second operation
        program_order: Dict mapping thread_id to list of operations in program order
    
    Returns:
        (happens_before, proof)
    """
    # Check program order (same thread)
    if op_a.thread_id == op_b.thread_id:
        thread_ops = program_order.get(op_a.thread_id, [])
        try:
            idx_a = thread_ops.index(op_a)
            idx_b = thread_ops.index(op_b)
            if idx_a < idx_b:
                return True, ProofObject(
                    rule="HappensBefore",
                    premises=["same thread", f"idx_a={idx_a} < idx_b={idx_b}"],
                    conclusion="happens_before via program order"
                )
        except ValueError:
            pass
    
    # Check synchronization (release-acquire)
    if (op_a.op_type == OpType.RELEASE and 
        op_b.op_type == OpType.ACQUIRE and
        op_a.address == op_b.address):
        return True, ProofObject(
            rule="HappensBefore",
            premises=["release-acquire pair", f"address={op_a.address}"],
            conclusion="happens_before via synchronization"
        )
    
    # Check if op_a timestamp is before op_b
    if op_a.timestamp < op_b.timestamp:
        return True, ProofObject(
            rule="HappensBefore",
            premises=[f"timestamp_a={op_a.timestamp} < timestamp_b={op_b.timestamp}"],
            conclusion="happens_before via timestamp"
        )
    
    return False, ProofObject(
        rule="HappensBefore",
        premises=["no ordering relation found"],
        conclusion="no happens_before relation"
    )


def check_data_race_free(order: MemoryOrder,
                         program_order: Dict[str, List[MemoryOperation]]) -> Tuple[bool, ProofObject]:
    """Check if execution is data-race free.
    
    A data race occurs when:
    1. Two accesses to the same address from different threads
    2. At least one is a write
    3. They are not ordered by happens-before
    
    Args:
        order: The memory order to check
        program_order: Program order for each thread
    
    Returns:
        (is_drf, proof)
    """
    if not order.operations:
        return True, ProofObject(
            rule="DataRaceFree",
            premises=["no operations"],
            conclusion="trivially data-race free"
        )
    
    # Group operations by address
    ops_by_address: Dict[str, List[MemoryOperation]] = {}
    for op in order.operations:
        if op.address not in ops_by_address:
            ops_by_address[op.address] = []
        ops_by_address[op.address].append(op)
    
    races = []
    
    for address, ops in ops_by_address.items():
        # Check all pairs of operations to this address
        for i, op_a in enumerate(ops):
            for op_b in ops[i+1:]:
                # Skip if same thread
                if op_a.thread_id == op_b.thread_id:
                    continue
                
                # Skip if neither is a write
                if op_a.op_type not in [OpType.WRITE, OpType.RELEASE] and \
                   op_b.op_type not in [OpType.WRITE, OpType.RELEASE]:
                    continue
                
                # Check if ordered by happens-before
                a_hb_b, _ = check_happens_before(op_a, op_b, program_order)
                b_hb_a, _ = check_happens_before(op_b, op_a, program_order)
                
                if not a_hb_b and not b_hb_a:
                    races.append(
                        f"Data race on {address}: {op_a} || {op_b}"
                    )
    
    is_drf = len(races) == 0
    
    proof = ProofObject(
        rule="DataRaceFree",
        premises=[
            f"addresses={len(ops_by_address)}",
            f"operations={len(order.operations)}",
            f"races={len(races)}"
        ],
        conclusion=f"is_drf={is_drf}"
    )
    
    return is_drf, proof


@dataclass
class ReleaseAcquirePair:
    """A matching release-acquire pair for synchronization."""
    release_op: MemoryOperation
    acquire_op: MemoryOperation
    address: str


def check_release_acquire_consistency(
    releases: List[MemoryOperation],
    acquires: List[MemoryOperation]
) -> Tuple[bool, ProofObject]:
    """Check if every acquire sees the effects of a matching release.
    
    In release-acquire semantics:
    - Release operations make prior writes visible
    - Acquire operations see all writes before the matching release
    - This creates a happens-before edge between release and acquire
    
    Args:
        releases: List of release operations
        acquires: List of acquire operations
    
    Returns:
        (consistent, proof)
    """
    # Group by address
    releases_by_addr: Dict[str, List[MemoryOperation]] = {}
    for rel in releases:
        if rel.address not in releases_by_addr:
            releases_by_addr[rel.address] = []
        releases_by_addr[rel.address].append(rel)
    
    acquires_by_addr: Dict[str, List[MemoryOperation]] = {}
    for acq in acquires:
        if acq.address not in acquires_by_addr:
            acquires_by_addr[acq.address] = []
        acquires_by_addr[acq.address].append(acq)
    
    # Check that every acquire has a matching release
    unmatched = []
    for addr, acq_list in acquires_by_addr.items():
        if addr not in releases_by_addr:
            for acq in acq_list:
                unmatched.append(f"Acquire at {addr}@{acq.timestamp} has no matching release")
    
    # Check ordering: each acquire should see the latest release before it
    ordering_violations = []
    for addr in set(releases_by_addr.keys()) & set(acquires_by_addr.keys()):
        rels = sorted(releases_by_addr[addr], key=lambda x: x.timestamp)
        acqs = sorted(acquires_by_addr[addr], key=lambda x: x.timestamp)
        
        for acq in acqs:
            # Find the latest release before this acquire
            matching_rels = [r for r in rels if r.timestamp < acq.timestamp]
            if not matching_rels:
                ordering_violations.append(
                    f"Acquire at {addr}@{acq.timestamp} has no prior release"
                )
    
    consistent = len(unmatched) == 0 and len(ordering_violations) == 0
    
    proof = ProofObject(
        rule="ReleaseAcquireConsistency",
        premises=[
            f"releases={len(releases)}",
            f"acquires={len(acquires)}",
            f"unmatched={len(unmatched)}",
            f"ordering_violations={len(ordering_violations)}"
        ],
        conclusion=f"consistent={consistent}"
    )
    
    return consistent, proof


def check_total_store_order(
    order: MemoryOrder,
    thread_ids: List[str]
) -> Tuple[bool, ProofObject]:
    """Check if execution respects Total Store Order (TSO).
    
    TSO (x86 memory model):
    - Reads can be reordered after writes
    - Writes are totally ordered (store buffer flushed in order)
    - Each thread sees its own writes immediately
    
    Args:
        order: The memory order
        thread_ids: List of thread IDs in the system
    
    Returns:
        (is_tso, proof)
    """
    # Simplified TSO check: verify no write-write reordering
    # In TSO, writes from the same thread must appear in program order
    
    violations = []
    
    for tid in thread_ids:
        thread_writes = [
            op for op in order.operations 
            if op.thread_id == tid and op.op_type == OpType.WRITE
        ]
        
        # Check writes appear in timestamp order
        sorted_writes = sorted(thread_writes, key=lambda x: x.timestamp)
        
        # Verify program order is respected
        for i, w in enumerate(thread_writes):
            if i > 0:
                prev_w = thread_writes[i-1]
                if w.timestamp < prev_w.timestamp:
                    violations.append(
                        f"Thread {tid}: write reordering detected"
                    )
    
    is_tso = len(violations) == 0
    
    proof = ProofObject(
        rule="TotalStoreOrder",
        premises=[
            f"threads={len(thread_ids)}",
            f"operations={len(order.operations)}",
            f"violations={len(violations)}"
        ],
        conclusion=f"is_tso={is_tso}"
    )
    
    return is_tso, proof
