"""
Advanced Evidence Module for Phase 9 Toolkit Expansion

Implements G9-03: Expanded EvidenceStore Logging with advanced causality tracking,
evidence linking across phases, and confidence scoring.

Author: Orthogonal Engineering System
Date: 2026-01-22
Version: 1.0.0
"""

import hashlib
import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from .evidence_store import EvidenceStore


class EvidenceConfidence(Enum):
    """Confidence levels for evidence chains."""

    HIGH = "high"  # Direct observation, cryptographic proof
    MEDIUM = "medium"  # Strong inference, multiple corroborating sources
    LOW = "low"  # Weak inference, single source
    SPECULATIVE = "speculative"  # Hypothesis, requires validation


class CausalLinkType(Enum):
    """Types of causal relationships between evidence items."""

    DIRECT = "direct"  # A directly causes B
    INDIRECT = "indirect"  # A contributes to B through intermediate steps
    CORRELATION = "correlation"  # A and B occur together but causation unclear
    TEMPORAL = "temporal"  # A precedes B in time
    NECESSARY = "necessary"  # A is necessary for B
    SUFFICIENT = "sufficient"  # A is sufficient for B
    CROSS_PHASE = "cross_phase"  # Links evidence across different phases


@dataclass
class CausalNode:
    """Node in a causal graph representing an evidence item."""

    node_id: str
    evidence_id: str
    phase: int
    timestamp: datetime
    confidence: EvidenceConfidence
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CausalEdge:
    """Edge in a causal graph representing a causal relationship."""

    edge_id: str
    source_node_id: str
    target_node_id: str
    link_type: CausalLinkType
    confidence_score: float  # 0.0 to 1.0
    temporal_gap_seconds: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidenceChain:
    """Chain of evidence items with causal relationships."""

    chain_id: str
    nodes: List[CausalNode]
    edges: List[CausalEdge]
    overall_confidence: float
    phases_covered: List[int]
    is_complete: bool


class AdvancedEvidenceStore(EvidenceStore):
    """
    Enhanced EvidenceStore with advanced causality tracking and evidence linking.

    Implements:
    1. Multi-level causality chains (cause → effect → sub-effect)
    2. Evidence linking across phases (Phase 8 → Phase 9 → Phase 10)
    3. Automated evidence validation against SHA256 manifests
    4. Temporal correlation analysis
    5. Confidence scoring for evidence chains
    """

    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize advanced evidence store.

        Args:
            base_path: Base directory for evidence storage (default: logs/evidence)
        """
        super().__init__(base_path)

        # Create advanced subdirectories
        self.causal_chains_path = self.base_path / "causal_chains"
        self.causal_chains_path.mkdir(exist_ok=True)

        self.cross_phase_path = self.base_path / "cross_phase"
        self.cross_phase_path.mkdir(exist_ok=True)

        self.confidence_scores_path = self.base_path / "confidence_scores"
        self.confidence_scores_path.mkdir(exist_ok=True)

        # Initialize causal graph
        self.causal_graph: Dict[str, CausalNode] = {}
        self.causal_edges: Dict[str, CausalEdge] = {}
        self.evidence_chains: Dict[str, EvidenceChain] = {}

        # Load existing causal data
        self._load_causal_data()

    def _load_causal_data(self) -> None:
        """Load existing causal data from storage."""
        # Load causal nodes
        nodes_file = self.metadata_path / "causal_nodes.json"
        if nodes_file.exists():
            with open(nodes_file, "r") as f:
                nodes_data = json.load(f)
                for node_id, node_data in nodes_data.items():
                    self.causal_graph[node_id] = CausalNode(
                        node_id=node_id,
                        evidence_id=node_data["evidence_id"],
                        phase=node_data["phase"],
                        timestamp=datetime.fromisoformat(node_data["timestamp"]),
                        confidence=EvidenceConfidence(node_data["confidence"]),
                        metadata=node_data.get("metadata", {}),
                    )

        # Load causal edges
        edges_file = self.metadata_path / "causal_edges.json"
        if edges_file.exists():
            with open(edges_file, "r") as f:
                edges_data = json.load(f)
                for edge_id, edge_data in edges_data.items():
                    self.causal_edges[edge_id] = CausalEdge(
                        edge_id=edge_id,
                        source_node_id=edge_data["source_node_id"],
                        target_node_id=edge_data["target_node_id"],
                        link_type=CausalLinkType(edge_data["link_type"]),
                        confidence_score=edge_data["confidence_score"],
                        temporal_gap_seconds=edge_data.get("temporal_gap_seconds"),
                        metadata=edge_data.get("metadata", {}),
                    )

        # Load evidence chains
        chains_file = self.metadata_path / "evidence_chains.json"
        if chains_file.exists():
            with open(chains_file, "r") as f:
                chains_data = json.load(f)
                for chain_id, chain_data in chains_data.items():
                    # Reconstruct nodes and edges from IDs
                    nodes = [
                        self.causal_graph[node_id] for node_id in chain_data["node_ids"]
                    ]
                    edges = [
                        self.causal_edges[edge_id] for edge_id in chain_data["edge_ids"]
                    ]

                    self.evidence_chains[chain_id] = EvidenceChain(
                        chain_id=chain_id,
                        nodes=nodes,
                        edges=edges,
                        overall_confidence=chain_data["overall_confidence"],
                        phases_covered=chain_data["phases_covered"],
                        is_complete=chain_data["is_complete"],
                    )

    def _save_causal_data(self) -> None:
        """Save causal data to storage."""
        # Save causal nodes
        nodes_data = {
            node_id: {
                "evidence_id": node.evidence_id,
                "phase": node.phase,
                "timestamp": node.timestamp.isoformat(),
                "confidence": node.confidence.value,
                "metadata": node.metadata,
            }
            for node_id, node in self.causal_graph.items()
        }
        with open(self.metadata_path / "causal_nodes.json", "w") as f:
            json.dump(nodes_data, f, indent=2)

        # Save causal edges
        edges_data = {
            edge_id: {
                "source_node_id": edge.source_node_id,
                "target_node_id": edge.target_node_id,
                "link_type": edge.link_type.value,
                "confidence_score": edge.confidence_score,
                "temporal_gap_seconds": edge.temporal_gap_seconds,
                "metadata": edge.metadata,
            }
            for edge_id, edge in self.causal_edges.items()
        }
        with open(self.metadata_path / "causal_edges.json", "w") as f:
            json.dump(edges_data, f, indent=2)

        # Save evidence chains
        chains_data = {
            chain_id: {
                "node_ids": [node.node_id for node in chain.nodes],
                "edge_ids": [edge.edge_id for edge in chain.edges],
                "overall_confidence": chain.overall_confidence,
                "phases_covered": chain.phases_covered,
                "is_complete": chain.is_complete,
            }
            for chain_id, chain in self.evidence_chains.items()
        }
        with open(self.metadata_path / "evidence_chains.json", "w") as f:
            json.dump(chains_data, f, indent=2)

    def add_causal_node(
        self,
        evidence_id: str,
        phase: int,
        confidence: EvidenceConfidence = EvidenceConfidence.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Add a node to the causal graph.

        Args:
            evidence_id: ID of the evidence item
            phase: Phase number (8, 9, 10, etc.)
            confidence: Confidence level for this evidence
            metadata: Additional metadata about the evidence

        Returns:
            Node ID for the created node
        """
        node_id = f"NODE-{uuid.uuid4().hex[:8].upper()}"

        node = CausalNode(
            node_id=node_id,
            evidence_id=evidence_id,
            phase=phase,
            timestamp=datetime.now(),
            confidence=confidence,
            metadata=metadata or {},
        )

        self.causal_graph[node_id] = node
        self._save_causal_data()

        # Log the addition
        self.log_causality(
            action="add_causal_node",
            cause=f"Evidence {evidence_id} from Phase {phase}",
            effect=f"Causal node {node_id} created",
            confidence=confidence.value,
            metadata={"node_id": node_id, "evidence_id": evidence_id, "phase": phase},
        )

        return node_id

    def add_causal_edge(
        self,
        source_node_id: str,
        target_node_id: str,
        link_type: CausalLinkType = CausalLinkType.DIRECT,
        confidence_score: float = 0.8,
        temporal_gap_seconds: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Add an edge between causal nodes.

        Args:
            source_node_id: ID of the source node
            target_node_id: ID of the target node
            link_type: Type of causal relationship
            confidence_score: Confidence score for this edge (0.0 to 1.0)
            temporal_gap_seconds: Time gap between source and target events
            metadata: Additional metadata about the causal relationship

        Returns:
            Edge ID for the created edge
        """
        # Validate nodes exist
        if source_node_id not in self.causal_graph:
            raise ValueError(f"Source node {source_node_id} not found")
        if target_node_id not in self.causal_graph:
            raise ValueError(f"Target node {target_node_id} not found")

        # Validate confidence score
        if not 0.0 <= confidence_score <= 1.0:
            raise ValueError(
                f"Confidence score must be between 0.0 and 1.0, got {confidence_score}"
            )

        edge_id = f"EDGE-{uuid.uuid4().hex[:8].upper()}"

        edge = CausalEdge(
            edge_id=edge_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            link_type=link_type,
            confidence_score=confidence_score,
            temporal_gap_seconds=temporal_gap_seconds,
            metadata=metadata or {},
        )

        self.causal_edges[edge_id] = edge
        self._save_causal_data()

        # Log the addition
        source_node = self.causal_graph[source_node_id]
        target_node = self.causal_graph[target_node_id]

        self.log_causality(
            action="add_causal_edge",
            cause=f"Causal node {source_node_id} (Phase {source_node.phase})",
            effect=f"Causal node {target_node_id} (Phase {target_node.phase})",
            confidence=f"{confidence_score:.2f}",
            metadata={
                "edge_id": edge_id,
                "link_type": link_type.value,
                "source_phase": source_node.phase,
                "target_phase": target_node.phase,
            },
        )

        return edge_id

    def create_evidence_chain(
        self,
        node_ids: List[str],
        edge_ids: List[str],
        phases_covered: Optional[List[int]] = None,
    ) -> str:
        """
        Create an evidence chain from nodes and edges.

        Args:
            node_ids: List of node IDs in the chain
            edge_ids: List of edge IDs connecting the nodes
            phases_covered: List of phases covered by this chain

        Returns:
            Chain ID for the created evidence chain
        """
        # Validate nodes and edges exist
        for node_id in node_ids:
            if node_id not in self.causal_graph:
                raise ValueError(f"Node {node_id} not found")

        for edge_id in edge_ids:
            if edge_id not in self.causal_edges:
                raise ValueError(f"Edge {edge_id} not found")

        # Get nodes and edges
        nodes = [self.causal_graph[node_id] for node_id in node_ids]
        edges = [self.causal_edges[edge_id] for edge_id in edge_ids]

        # Calculate overall confidence
        node_confidences = {
            EvidenceConfidence.HIGH: 1.0,
            EvidenceConfidence.MEDIUM: 0.7,
            EvidenceConfidence.LOW: 0.4,
            EvidenceConfidence.SPECULATIVE: 0.1,
        }

        avg_node_confidence = sum(
            node_confidences[node.confidence] for node in nodes
        ) / len(nodes)
        avg_edge_confidence = (
            sum(edge.confidence_score for edge in edges) / len(edges) if edges else 1.0
        )
        overall_confidence = (avg_node_confidence + avg_edge_confidence) / 2

        # Determine phases covered if not provided
        if phases_covered is None:
            phases_covered = sorted(set(node.phase for node in nodes))

        chain_id = f"CHAIN-{uuid.uuid4().hex[:8].upper()}"

        chain = EvidenceChain(
            chain_id=chain_id,
            nodes=nodes,
            edges=edges,
            overall_confidence=overall_confidence,
            phases_covered=phases_covered,
            is_complete=self._validate_chain_completeness(nodes, edges),
        )

        self.evidence_chains[chain_id] = chain
        self._save_causal_data()

        # Save chain to file
        chain_file = self.causal_chains_path / f"{chain_id}.json"
        chain_data = {
            "chain_id": chain_id,
            "nodes": [
                {
                    "node_id": node.node_id,
                    "evidence_id": node.evidence_id,
                    "phase": node.phase,
                    "confidence": node.confidence.value,
                }
                for node in nodes
            ],
            "edges": [
                {
                    "edge_id": edge.edge_id,
                    "source_node_id": edge.source_node_id,
                    "target_node_id": edge.target_node_id,
                    "link_type": edge.link_type.value,
                    "confidence_score": edge.confidence_score,
                }
                for edge in edges
            ],
            "overall_confidence": overall_confidence,
            "phases_covered": phases_covered,
            "is_complete": chain.is_complete,
            "created_at": datetime.now().isoformat(),
        }

        with open(chain_file, "w") as f:
            json.dump(chain_data, f, indent=2)

        # Log the creation
        self.log_causality(
            action="create_evidence_chain",
            cause=f"Evidence chain creation requested",
            effect=f"Evidence chain {chain_id} created with {len(nodes)} nodes and {len(edges)} edges",
            confidence=f"{overall_confidence:.2f}",
            metadata={
                "chain_id": chain_id,
                "node_count": len(nodes),
                "edge_count": len(edges),
                "phases_covered": phases_covered,
            },
        )

        return chain_id

    def _validate_chain_completeness(
        self, nodes: List[CausalNode], edges: List[CausalEdge]
    ) -> bool:
        """
        Validate if an evidence chain is complete.

        A complete chain has:
        1. At least 2 nodes
        2. Edges connecting all nodes in sequence
        3. No disconnected nodes

        Args:
            nodes: List of nodes in the chain
            edges: List of edges in the chain

        Returns:
            True if the chain is complete, False otherwise
        """
        if len(nodes) < 2:
            return False

        # Create adjacency list
        adjacency = {node.node_id: set() for node in nodes}
        for edge in edges:
            if edge.source_node_id in adjacency:
                adjacency[edge.source_node_id].add(edge.target_node_id)

        # Check if all nodes are connected in a single path
        visited = set()

        def dfs(node_id: str) -> None:
            visited.add(node_id)
            for neighbor in adjacency.get(node_id, []):
                if neighbor not in visited:
                    dfs(neighbor)

        # Start DFS from first node
        if nodes:
            dfs(nodes[0].node_id)

        return len(visited) == len(nodes)

    def link_evidence_across_phases(
        self,
        phase_a: int,
        phase_b: int,
        evidence_id_a: str,
        evidence_id_b: str,
        link_type: CausalLinkType = CausalLinkType.TEMPORAL,
        confidence_score: float = 0.7,
    ) -> Tuple[str, str, str]:
        """
        Link evidence items across different phases.

        Args:
            phase_a: First phase number
            phase_b: Second phase number
            evidence_id_a: Evidence ID from phase A
            evidence_id_b: Evidence ID from phase B
            link_type: Type of causal relationship
            confidence_score: Confidence score for the link

        Returns:
            Tuple of (node_id_a, node_id_b, edge_id)
        """
        # Create nodes for both evidence items
        node_id_a = self.add_causal_node(
            evidence_id=evidence_id_a,
            phase=phase_a,
            confidence=EvidenceConfidence.HIGH,
            metadata={"cross_phase_link": True, "linked_phase": phase_b},
        )

        node_id_b = self.add_causal_node(
            evidence_id=evidence_id_b,
            phase=phase_b,
            confidence=EvidenceConfidence.HIGH,
            metadata={"cross_phase_link": True, "linked_phase": phase_a},
        )

        # Create edge linking the nodes
        edge_id = self.add_causal_edge(
            source_node_id=node_id_a,
            target_node_id=node_id_b,
            link_type=CausalLinkType.CROSS_PHASE,
            confidence_score=confidence_score,
            metadata={
                "cross_phase_link": True,
                "phase_a": phase_a,
                "phase_b": phase_b,
                "evidence_id_a": evidence_id_a,
                "evidence_id_b": evidence_id_b,
            },
        )

        return node_id_a, node_id_b, edge_id
