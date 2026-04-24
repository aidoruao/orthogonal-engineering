"""D_DAG_THEORY implementation -- Directed Acyclic Graph structures.

Part 3E of Forensic Offensive Campaign.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, List, Set, Tuple


@dataclass(frozen=True)
class DAGNode:
    """A single node in a DAG with content-addressed identity.

    falsifies_if: node_id is empty or content_hash is empty.
    """
    node_id: str
    content_hash: str
    payload: str
    children: Tuple[str, ...]


@dataclass(frozen=True)
class DAGState:
    """State of a directed acyclic graph.

    falsifies_if: nodes is empty while claiming a valid DAG.
    """
    dag_id: str
    nodes: Dict[str, DAGNode]
    root_id: str
    max_depth: int


@dataclass(frozen=True)
class DAGExpansion:
    """Deterministic expansion of a DAG to a target depth.

    falsifies_if: target_depth < 0 or expansion_factor < 1.
    """
    dag_id: str
    target_depth: int
    expansion_factor: int
    resulting_nodes: int
    resulting_edges: int


DOMAIN_METADATA = {
    "name": "d_dag_theory",
    "version": "1.0.0",
    "part": "3E",
    "campaign": "CAMPAIGN-FORENSIC-OFFENSIVE-001",
}
