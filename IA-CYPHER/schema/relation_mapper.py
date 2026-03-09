"""
relation_mapper.py — IA-CYPHER Entity Relation Graph Builder

Builds a directed entity relation graph from classified traces.
Nodes = corporate entities.  Edges = relations (OWNS, CONTROLS, FUNDS, etc.)

Graph is stored as an adjacency dict for portability (no external libs required).
Can export to JSON for downstream tools.
"""

from __future__ import annotations

import json
from typing import Dict, List, Optional, Set, Tuple

from .corporate_audit_schema import RELATION_IDS


# ---------------------------------------------------------------------------
# Graph node and edge types
# ---------------------------------------------------------------------------

class EntityNode:
    """A corporate entity in the relation graph."""

    __slots__ = ("entity_id", "name", "ontology_category", "trace_ids", "properties")

    def __init__(
        self,
        entity_id: str,
        name: str,
        ontology_category: str = "UNKNOWN",
        trace_ids: Optional[List[str]] = None,
        properties: Optional[Dict] = None,
    ) -> None:
        self.entity_id = entity_id
        self.name = name
        self.ontology_category = ontology_category
        self.trace_ids: List[str] = trace_ids or []
        self.properties: Dict = properties or {}

    def to_dict(self) -> Dict:
        return {
            "entity_id":         self.entity_id,
            "name":              self.name,
            "ontology_category": self.ontology_category,
            "trace_ids":         self.trace_ids,
            "properties":        self.properties,
        }


class RelationEdge:
    """A directed relation between two entities."""

    __slots__ = ("from_id", "relation_id", "to_id", "trace_ids", "confidence", "notes")

    def __init__(
        self,
        from_id: str,
        relation_id: str,
        to_id: str,
        trace_ids: Optional[List[str]] = None,
        confidence: float = 1.0,
        notes: str = "",
    ) -> None:
        if relation_id not in RELATION_IDS and relation_id != "UNKNOWN":
            raise ValueError(f"Unknown relation_id '{relation_id}'. Valid: {RELATION_IDS}")
        self.from_id = from_id
        self.relation_id = relation_id
        self.to_id = to_id
        self.trace_ids: List[str] = trace_ids or []
        self.confidence = confidence
        self.notes = notes

    def edge_key(self) -> Tuple[str, str, str]:
        return (self.from_id, self.relation_id, self.to_id)

    def to_dict(self) -> Dict:
        return {
            "from_id":     self.from_id,
            "relation_id": self.relation_id,
            "to_id":       self.to_id,
            "trace_ids":   self.trace_ids,
            "confidence":  self.confidence,
            "notes":       self.notes,
        }


# ---------------------------------------------------------------------------
# RelationGraph — the main data structure
# ---------------------------------------------------------------------------

class RelationGraph:
    """
    Directed graph of corporate entities and their relations.

    Usage
    -----
    g = RelationGraph()
    g.add_entity(EntityNode("google", "Google LLC", "INFORMATION_PROCESSOR"))
    g.add_entity(EntityNode("deepmind", "DeepMind", "INFORMATION_PROCESSOR"))
    g.add_edge(RelationEdge("google", "OWNS", "deepmind", trace_ids=["trace_001"]))
    report = g.summary()
    """

    def __init__(self) -> None:
        self._nodes: Dict[str, EntityNode] = {}
        self._edges: Dict[Tuple, RelationEdge] = {}

    # -- Node operations --

    def add_entity(self, node: EntityNode) -> None:
        self._nodes[node.entity_id] = node

    def get_entity(self, entity_id: str) -> Optional[EntityNode]:
        return self._nodes.get(entity_id)

    def has_entity(self, entity_id: str) -> bool:
        return entity_id in self._nodes

    def all_entities(self) -> List[EntityNode]:
        return list(self._nodes.values())

    # -- Edge operations --

    def add_edge(self, edge: RelationEdge) -> None:
        # Auto-add missing endpoint nodes as UNKNOWN
        for eid in (edge.from_id, edge.to_id):
            if eid not in self._nodes:
                self._nodes[eid] = EntityNode(eid, eid, "UNKNOWN")
        self._edges[edge.edge_key()] = edge

    def has_edge(self, from_id: str, relation_id: str, to_id: str) -> bool:
        return (from_id, relation_id, to_id) in self._edges

    def get_edge(self, from_id: str, relation_id: str, to_id: str) -> Optional[RelationEdge]:
        return self._edges.get((from_id, relation_id, to_id))

    def all_edges(self) -> List[RelationEdge]:
        return list(self._edges.values())

    def edges_from(self, entity_id: str) -> List[RelationEdge]:
        return [e for e in self._edges.values() if e.from_id == entity_id]

    def edges_to(self, entity_id: str) -> List[RelationEdge]:
        return [e for e in self._edges.values() if e.to_id == entity_id]

    # -- Pattern queries --

    def entities_by_relation(self, relation_id: str) -> List[Tuple[str, str]]:
        """Return (from_id, to_id) pairs for all edges of a given relation type."""
        return [
            (e.from_id, e.to_id)
            for e in self._edges.values()
            if e.relation_id == relation_id
        ]

    def relation_distribution(self) -> Dict[str, int]:
        """Count edges by relation type."""
        counts: Dict[str, int] = {r: 0 for r in RELATION_IDS}
        for edge in self._edges.values():
            if edge.relation_id in counts:
                counts[edge.relation_id] += 1
        return counts

    def find_high_control_entities(self, min_out_edges: int = 2) -> List[str]:
        """Return entity IDs with >= min_out_edges outgoing CONTROLS/SUPPRESSES/FUNDS edges."""
        from collections import Counter
        control_relations = {"CONTROLS", "SUPPRESSES", "FUNDS", "COORDINATES"}
        counter: Dict[str, int] = {}
        for e in self._edges.values():
            if e.relation_id in control_relations:
                counter[e.from_id] = counter.get(e.from_id, 0) + 1
        return [eid for eid, cnt in counter.items() if cnt >= min_out_edges]

    # -- Summary --

    def summary(self) -> Dict:
        return {
            "node_count":           len(self._nodes),
            "edge_count":           len(self._edges),
            "relation_distribution": self.relation_distribution(),
            "high_control_entities": self.find_high_control_entities(),
            "nodes":                [n.to_dict() for n in self._nodes.values()],
            "edges":                [e.to_dict() for e in self._edges.values()],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.summary(), indent=indent)

    # -- Build from classified corpus --

    @classmethod
    def from_corpus(cls, classified_corpus: Dict) -> "RelationGraph":
        """
        Build a RelationGraph by scanning a classified corpus for entity mentions
        and pattern-implied relations.

        For each classified trace, if it has a known entity field, add the entity.
        If pattern P1 (Capture) is detected, add a CONTROLS edge from entity to
        'regulatory_body'. If P9 (Discourse Capture), add FUNDS edge to 'media'.
        etc.

        This is a heuristic inference layer — traces must have 'entity' field
        to produce nodes; relations are inferred from detected patterns.
        """
        g = cls()

        # Map patterns to implied relations
        pattern_to_relation = {
            "P1":  "CONTROLS",
            "P2":  "EXTRACTS",
            "P3":  "EXTERNALIZES",
            "P4":  "CONCEALS",
            "P5":  "DEFLECTS",
            "P6":  "SUPPRESSES",
            "P7":  "COORDINATES",
            "P8":  "BECOMES",
            "P9":  "FUNDS",
            "P10": "SUPPRESSES",
        }

        # Map patterns to default target node id (used when no explicit target in trace)
        pattern_to_default_target = {
            "P1":  "regulatory_body",
            "P2":  "population",
            "P3":  "public",
            "P4":  "evidence",
            "P5":  "blame_target",
            "P6":  "information",
            "P7":  "coordinated_entity",
            "P8":  "successor_entity",
            "P9":  "media_or_research",
            "P10": "discourse",
        }

        for item in classified_corpus.get("classified", []):
            entity_id = item.get("entity")
            entity_name = item.get("entity_name", entity_id)
            trace_id = item.get("id", item.get("sha256", "unknown")[:12])

            if not entity_id:
                continue

            # Ensure entity node exists
            if not g.has_entity(entity_id):
                g.add_entity(EntityNode(
                    entity_id=entity_id,
                    name=entity_name or entity_id,
                    ontology_category=item.get("ontology_category", "UNKNOWN"),
                    trace_ids=[trace_id],
                ))
            else:
                node = g.get_entity(entity_id)
                if trace_id not in node.trace_ids:
                    node.trace_ids.append(trace_id)

            # Infer edges from detected patterns
            for pat_id in item.get("patterns", []):
                rel_id = pattern_to_relation.get(pat_id)
                target_id = item.get("target_entity") or pattern_to_default_target.get(pat_id, "unknown_target")
                if rel_id:
                    if g.has_edge(entity_id, rel_id, target_id):
                        # Append trace to existing edge
                        existing = g.get_edge(entity_id, rel_id, target_id)
                        if trace_id not in existing.trace_ids:
                            existing.trace_ids.append(trace_id)
                    else:
                        g.add_edge(RelationEdge(
                            from_id=entity_id,
                            relation_id=rel_id,
                            to_id=target_id,
                            trace_ids=[trace_id],
                            confidence=0.8,
                            notes=f"Inferred from pattern {pat_id}",
                        ))

        return g
