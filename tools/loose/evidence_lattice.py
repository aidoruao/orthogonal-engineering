"""
A-23: Evidence Lattice
========================
Implements the partially-ordered evidence set from the Kimi bi-layer spec:

    E = {e1 ≤ e2 ≤ e3}

Partial order (≤) is defined by source authority + confidence + recency:
    human > external > internal   (source rank)
    higher confidence > lower     (when source ranks equal)
    newer > older                 (recency bias for dynamic systems)

The lattice provides:
- ``EvidenceNode``: an atomic evidence claim with source, confidence, timestamp
- ``EvidenceLattice``: ordered set with insert, join (merge), conflict detection

Merge rules:
  - If e1 < e2 (e2 is stronger): the join is e2.
  - If e1 and e2 are incomparable (different sources, similar confidence):
    a synthetic merge node is created with a slight confidence penalty (×0.95).

Conflict detection:
  - Two nodes conflict when they come from different sources AND have
    contradictory ``verdict`` fields (e.g., "healthy" vs "critical").
"""
from __future__ import annotations

import hashlib
import math
import time
from dataclasses import dataclass, field
from functools import total_ordering
from typing import Any, Dict, List, Optional, Set, Tuple

# Source authority ranks (higher = more authoritative)
_SOURCE_RANK: Dict[str, int] = {
    "human": 3,
    "external": 2,
    "internal": 1,
    "bridged_from_internal": 0,
    "merged": 0,
}


@total_ordering
@dataclass
class EvidenceNode:
    """An atomic evidence claim in the lattice.

    Attributes:
        source:       ``"internal"``, ``"external"``, ``"human"``, or ``"merged(...)"``
        confidence:   float in [0, 1]
        timestamp:    UNIX timestamp (float)
        verdict:      Optional verdict string (e.g., ``"healthy"``, ``"warning"``)
        payload:      Arbitrary evidence payload
        dependencies: IDs of parent nodes that were merged to produce this node
    """

    source: str
    confidence: float
    timestamp: float
    verdict: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    id: str = field(init=False)

    def __post_init__(self) -> None:
        key = f"{self.source}:{self.confidence:.6f}:{self.timestamp:.6f}"
        self.id = hashlib.sha256(key.encode()).hexdigest()[:12]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EvidenceNode):
            return NotImplemented
        return (
            abs(self.confidence - other.confidence) < 1e-9
            and self.source == other.source
        )

    def __lt__(self, other: "EvidenceNode") -> bool:
        """self < other means *other* is the stronger evidence."""
        sr_self = _SOURCE_RANK.get(self.source, 0)
        sr_other = _SOURCE_RANK.get(other.source, 0)

        if sr_self != sr_other:
            return sr_self < sr_other

        if abs(self.confidence - other.confidence) > 0.01:
            return self.confidence < other.confidence

        return self.timestamp < other.timestamp

    def __hash__(self) -> int:
        return hash(self.id)

    def merge(self, other: "EvidenceNode") -> "EvidenceNode":
        """Lattice join: return the stronger node, or a synthetic merge if incomparable."""
        if self < other:
            return other
        if other < self:
            return self
        # Incomparable: synthetic merge with slight confidence penalty
        merged_source = f"merged({self.source},{other.source})"
        return EvidenceNode(
            source=merged_source,
            confidence=max(self.confidence, other.confidence) * 0.95,
            timestamp=max(self.timestamp, other.timestamp),
            verdict=self.verdict if self.verdict == other.verdict else None,
            payload={**self.payload, **other.payload},
            dependencies=[self.id, other.id],
        )


class EvidenceLattice:
    """Partially ordered set of evidence nodes with merge and conflict detection.

    The lattice maintains at most one node per ``(source, verdict)`` pair.
    When a new node arrives for the same key, the stronger one (by ≤ order)
    replaces the weaker one.
    """

    def __init__(self) -> None:
        self._nodes: Dict[str, EvidenceNode] = {}  # key → node
        self._conflicts: List[Tuple[EvidenceNode, EvidenceNode]] = []

    # ---------------------------------------------------------------- #
    # Public API                                                         #
    # ---------------------------------------------------------------- #

    def insert(self, node: EvidenceNode) -> None:
        """Insert a node into the lattice.

        If an existing node with the same key exists, keep the stronger one.
        Additionally, scan for inter-key verdict contradictions from the same source.
        """
        key = f"{node.source}:{node.verdict or '_'}"
        existing = self._nodes.get(key)

        if existing is not None:
            # Same (source, verdict) key: keep stronger
            self._nodes[key] = existing.merge(node)
            return

        # Check for contradiction: same source with a different verdict already present
        for existing_key, existing_node in self._nodes.items():
            if (
                existing_node.source == node.source
                and existing_node.verdict is not None
                and node.verdict is not None
                and existing_node.verdict != node.verdict
            ):
                self._conflicts.append((existing_node, node))

        self._nodes[key] = node

    def merge_conflict_resolution(self) -> "EvidenceNode":
        """Return a single merged node representing the strongest available evidence."""
        if not self._nodes:
            return EvidenceNode(
                source="empty_lattice",
                confidence=0.0,
                timestamp=time.time(),
            )
        nodes = sorted(self._nodes.values(), reverse=True)
        result = nodes[0]
        for n in nodes[1:]:
            result = result.merge(n)
        return result

    def conflicts(self) -> List[Dict[str, Any]]:
        """Return all detected contradiction pairs as serialisable dicts."""
        return [
            {
                "node_a": {"id": a.id, "source": a.source, "verdict": a.verdict, "confidence": a.confidence},
                "node_b": {"id": b.id, "source": b.source, "verdict": b.verdict, "confidence": b.confidence},
                "type": "verdict_contradiction",
            }
            for a, b in self._conflicts
        ]

    def strongest(self) -> Optional[EvidenceNode]:
        """Return the single strongest node currently in the lattice."""
        if not self._nodes:
            return None
        return max(self._nodes.values())

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the lattice state for persistence / debugging."""
        return {
            "node_count": len(self._nodes),
            "conflict_count": len(self._conflicts),
            "nodes": [
                {
                    "id": n.id,
                    "source": n.source,
                    "confidence": round(n.confidence, 4),
                    "timestamp": n.timestamp,
                    "verdict": n.verdict,
                    "dependencies": n.dependencies,
                }
                for n in self._nodes.values()
            ],
            "conflicts": self.conflicts(),
        }
