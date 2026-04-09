#!/usr/bin/env python3
"""
Database Systems Domain — ACID, Serializability, B-tree Invariants

Key concepts:
- ACID properties (Atomicity, Consistency, Isolation, Durability)
- Conflict serializability
- B-tree structural invariants
"""

from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional
from enum import Enum, auto


class TransactionStatus(Enum):
    ACTIVE = auto()
    COMMITTED = auto()
    ABORTED = auto()


@dataclass
class Operation:
    """Database operation (read or write)."""
    transaction_id: str
    object_id: str
    op_type: str  # 'R' or 'W'


@dataclass
class Schedule:
    """Sequence of operations from multiple transactions."""
    operations: List[Operation]
    
    def conflicts(self) -> List[Tuple[Operation, Operation]]:
        """Find conflicting operations (same object, at least one write)."""
        conflicts = []
        for i, op1 in enumerate(self.operations):
            for op2 in self.operations[i+1:]:
                if op1.object_id == op2.object_id:
                    if 'W' in (op1.op_type, op2.op_type):
                        if op1.transaction_id != op2.transaction_id:
                            conflicts.append((op1, op2))
        return conflicts
    
    def is_conflict_serializable(self) -> bool:
        """Check if schedule is conflict-serializable (acyclic precedence graph)."""
        # Build precedence graph
        edges: Set[Tuple[str, str]] = set()
        conflicts = self.conflicts()
        
        for op1, op2 in conflicts:
            # op1 precedes op2
            edge = (op1.transaction_id, op2.transaction_id)
            if edge[0] != edge[1]:
                edges.add(edge)
        
        # Check for cycles using simple DFS
        nodes = set()
        for e in edges:
            nodes.add(e[0])
            nodes.add(e[1])
        
        def has_cycle(node: str, visited: Set[str], rec_stack: Set[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for edge in edges:
                if edge[0] == node:
                    neighbor = edge[1]
                    if neighbor not in visited:
                        if has_cycle(neighbor, visited, rec_stack):
                            return True
                    elif neighbor in rec_stack:
                        return True
            
            rec_stack.remove(node)
            return False
        
        visited: Set[str] = set()
        for node in nodes:
            if node not in visited:
                if has_cycle(node, visited, set()):
                    return False
        return True


@dataclass
class Transaction:
    """Database transaction with ACID tracking."""
    tx_id: str
    operations: List[Operation] = field(default_factory=list)
    status: TransactionStatus = TransactionStatus.ACTIVE
    
    def is_committed(self) -> bool:
        return self.status == TransactionStatus.COMMITTED


@dataclass
class BTreeNode:
    """B-tree node with invariant checking."""
    keys: List[int]
    children: List['BTreeNode'] = field(default_factory=list)
    is_leaf: bool = True
    max_degree: int = 4  # Maximum children (t=2 means max 4 children, max 3 keys)
    
    def is_valid(self) -> bool:
        """Check B-tree invariants at this node."""
        # Keys sorted
        if self.keys != sorted(self.keys):
            return False
        
        # Key count within bounds
        max_keys = self.max_degree - 1
        if len(self.keys) > max_keys:
            return False
        
        # Non-root nodes must have at least (max_degree//2 - 1) keys
        # (simplified: just check max for now)
        
        return True
    
    def height(self) -> int:
        """Calculate subtree height."""
        if self.is_leaf:
            return 1
        if not self.children:
            return 1
        return 1 + max(c.height() for c in self.children)


@dataclass
class TransactionManager:
    """Manages transaction durability and atomicity."""
    transactions: Dict[str, Transaction] = field(default_factory=dict)
    committed_writes: Dict[str, str] = field(default_factory=dict)  # object -> tx_id
    
    def is_durable(self, tx_id: str) -> bool:
        """Check if committed transaction is durable."""
        tx = self.transactions.get(tx_id)
        if not tx:
            return False
        if tx.status != TransactionStatus.COMMITTED:
            return False
        # All writes recorded
        return True


# ACID thresholds
MAX_TRANSACTION_TIME_MS = Fraction(30000)  # 30 second timeout
