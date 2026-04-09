#!/usr/bin/env python3
"""
Distributed Systems Domain — CAP Theorem, Vector Clocks, Consensus

Key concepts:
- CAP theorem (Consistency, Availability, Partition tolerance)
- Vector clock causality tracking
- Quorum consensus
"""

from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional
from enum import Enum, auto


class SystemProperty(Enum):
    CONSISTENCY = auto()
    AVAILABILITY = auto()
    PARTITION_TOLERANCE = auto()


@dataclass
class CAPAnalyzer:
    """Analyze CAP theorem constraints."""
    has_consistency: bool = False
    has_availability: bool = False
    has_partition_tolerance: bool = False
    
    def satisfies_cap(self) -> bool:
        """CAP theorem: can have at most 2 of 3 properties during partition."""
        # During network partition, must choose between C and A
        if self.has_partition_tolerance:
            # Can have C+P or A+P but not C+A+P during partition
            return not (self.has_consistency and self.has_availability)
        return True  # No partition = can have C+A


@dataclass
class VectorClock:
    """Vector clock for causality tracking."""
    timestamps: Dict[str, int] = field(default_factory=dict)
    
    def increment(self, node_id: str) -> None:
        """Increment own clock."""
        self.timestamps[node_id] = self.timestamps.get(node_id, 0) + 1
    
    def update(self, other: 'VectorClock') -> None:
        """Merge another vector clock (receive message)."""
        for node, ts in other.timestamps.items():
            self.timestamps[node] = max(self.timestamps.get(node, 0), ts)
    
    def compare(self, other: 'VectorClock') -> Optional[str]:
        """
        Compare vector clocks.
        Returns: 'before', 'after', 'concurrent', or 'equal'
        """
        all_nodes = set(self.timestamps.keys()) | set(other.timestamps.keys())
        
        less = False
        greater = False
        
        for node in all_nodes:
            t1 = self.timestamps.get(node, 0)
            t2 = other.timestamps.get(node, 0)
            
            if t1 < t2:
                less = True
            elif t1 > t2:
                greater = True
        
        if less and not greater:
            return "before"
        if greater and not less:
            return "after"
        if not less and not greater:
            return "equal"
        return "concurrent"
    
    def happens_before(self, other: 'VectorClock') -> bool:
        """Check if this event happens before other."""
        return self.compare(other) == "before"


@dataclass
class ConsensusVerifier:
    """Verify consensus protocol properties."""
    node_count: int
    votes_received: Dict[str, str] = field(default_factory=dict)  # node -> value
    
    def quorum_size(self) -> int:
        """Majority quorum: > n/2."""
        return (self.node_count // 2) + 1
    
    def has_quorum(self) -> bool:
        """Check if quorum achieved."""
        return len(self.votes_received) >= self.quorum_size()
    
    def agreed_value(self) -> Optional[str]:
        """Check if quorum agrees on value."""
        if not self.has_quorum():
            return None
        
        # Count votes
        vote_counts: Dict[str, int] = {}
        for vote in self.votes_received.values():
            vote_counts[vote] = vote_counts.get(vote, 0) + 1
        
        # Find majority
        for value, count in vote_counts.items():
            if count >= self.quorum_size():
                return value
        
        return None


@dataclass
class DistributedTransaction:
    """Two-phase commit transaction."""
    tx_id: str
    participants: List[str]
    prepare_votes: Dict[str, bool] = field(default_factory=dict)
    
    def all_prepared(self) -> bool:
        """All participants voted YES in prepare phase."""
        return (
            len(self.prepare_votes) == len(self.participants) and
            all(self.prepare_votes.values())
        )


# Distributed systems thresholds
MAX_CLOCK_SKEW_MS = Fraction(100)
MIN_QUORUM_RATIO = Fraction(1, 2)  # Majority
