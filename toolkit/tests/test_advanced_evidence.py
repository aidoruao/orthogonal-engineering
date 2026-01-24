"""
Test module for advanced_evidence.py

Tests the AdvancedEvidenceStore class and its functionality for Phase 9
toolkit expansion.

Author: Orthogonal Engineering System
Date: 2026-01-22
Version: 1.0.0
"""

import json
import shutil
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from toolkit.oe.advanced_evidence import (
    AdvancedEvidenceStore,
    CausalEdge,
    CausalLinkType,
    CausalNode,
    EvidenceChain,
    EvidenceConfidence,
)


class TestAdvancedEvidenceStore(unittest.TestCase):
    """Test cases for AdvancedEvidenceStore class."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.evidence_store = AdvancedEvidenceStore(base_path=self.test_dir)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)

    def test_initialization(self):
        """Test AdvancedEvidenceStore initialization."""
        self.assertIsNotNone(self.evidence_store)
        self.assertEqual(self.evidence_store.base_path, Path(self.test_dir))

        # Check that subdirectories were created
        self.assertTrue((Path(self.test_dir) / "causal_chains").exists())
        self.assertTrue((Path(self.test_dir) / "cross_phase").exists())
        self.assertTrue((Path(self.test_dir) / "confidence_scores").exists())

    def test_add_causal_node(self):
        """Test adding causal nodes."""
        node_id = self.evidence_store.add_causal_node(
            evidence_id="TEST-EVIDENCE-001",
            phase=9,
            confidence=EvidenceConfidence.HIGH,
            metadata={"test": True},
        )

        self.assertIsNotNone(node_id)
        self.assertIn(node_id, self.evidence_store.causal_graph)

        node = self.evidence_store.causal_graph[node_id]
        self.assertEqual(node.evidence_id, "TEST-EVIDENCE-001")
        self.assertEqual(node.phase, 9)
        self.assertEqual(node.confidence, EvidenceConfidence.HIGH)
        self.assertEqual(node.metadata["test"], True)

    def test_add_causal_edge(self):
        """Test adding causal edges between nodes."""
        # Create two nodes first
        node1_id = self.evidence_store.add_causal_node(
            evidence_id="EVIDENCE-001", phase=8, confidence=EvidenceConfidence.MEDIUM
        )

        node2_id = self.evidence_store.add_causal_node(
            evidence_id="EVIDENCE-002", phase=9, confidence=EvidenceConfidence.HIGH
        )

        # Add edge between nodes
        edge_id = self.evidence_store.add_causal_edge(
            source_node_id=node1_id,
            target_node_id=node2_id,
            link_type=CausalLinkType.DIRECT,
            confidence_score=0.85,
            temporal_gap_seconds=3600.0,
            metadata={"test_edge": True},
        )

        self.assertIsNotNone(edge_id)
        self.assertIn(edge_id, self.evidence_store.causal_edges)

        edge = self.evidence_store.causal_edges[edge_id]
        self.assertEqual(edge.source_node_id, node1_id)
        self.assertEqual(edge.target_node_id, node2_id)
        self.assertEqual(edge.link_type, CausalLinkType.DIRECT)
        self.assertEqual(edge.confidence_score, 0.85)
        self.assertEqual(edge.temporal_gap_seconds, 3600.0)
        self.assertEqual(edge.metadata["test_edge"], True)

    def test_add_causal_edge_invalid_nodes(self):
        """Test adding causal edge with invalid nodes."""
        # Try to add edge with non-existent nodes
        with self.assertRaises(ValueError):
            self.evidence_store.add_causal_edge(
                source_node_id="NONEXISTENT-1",
                target_node_id="NONEXISTENT-2",
                link_type=CausalLinkType.DIRECT,
                confidence_score=0.5,
            )

    def test_add_causal_edge_invalid_confidence(self):
        """Test adding causal edge with invalid confidence score."""
        # Create nodes first
        node1_id = self.evidence_store.add_causal_node(
            evidence_id="EVIDENCE-001", phase=8
        )

        node2_id = self.evidence_store.add_causal_node(
            evidence_id="EVIDENCE-002", phase=9
        )

        # Try to add edge with invalid confidence
        with self.assertRaises(ValueError):
            self.evidence_store.add_causal_edge(
                source_node_id=node1_id,
                target_node_id=node2_id,
                link_type=CausalLinkType.DIRECT,
                confidence_score=1.5,  # Invalid: > 1.0
            )

        with self.assertRaises(ValueError):
            self.evidence_store.add_causal_edge(
                source_node_id=node1_id,
                target_node_id=node2_id,
                link_type=CausalLinkType.DIRECT,
                confidence_score=-0.1,  # Invalid: < 0.0
            )

    def test_create_evidence_chain(self):
        """Test creating evidence chains."""
        # Create nodes
        node_ids = []
        for i in range(3):
            node_id = self.evidence_store.add_causal_node(
                evidence_id=f"EVIDENCE-{i:03d}",
                phase=8 + i,
                confidence=EvidenceConfidence.HIGH,
            )
            node_ids.append(node_id)

        # Create edges
        edge_ids = []
        for i in range(2):
            edge_id = self.evidence_store.add_causal_edge(
                source_node_id=node_ids[i],
                target_node_id=node_ids[i + 1],
                link_type=CausalLinkType.DIRECT,
                confidence_score=0.8 + i * 0.1,
            )
            edge_ids.append(edge_id)

        # Create chain
        chain_id = self.evidence_store.create_evidence_chain(
            node_ids=node_ids, edge_ids=edge_ids, phases_covered=[8, 9, 10]
        )

        self.assertIsNotNone(chain_id)
        self.assertIn(chain_id, self.evidence_store.evidence_chains)

        chain = self.evidence_store.evidence_chains[chain_id]
        self.assertEqual(len(chain.nodes), 3)
        self.assertEqual(len(chain.edges), 2)
        self.assertEqual(chain.phases_covered, [8, 9, 10])
        self.assertTrue(0.0 <= chain.overall_confidence <= 1.0)

        # Check that chain file was created
        chain_file = Path(self.test_dir) / "causal_chains" / f"{chain_id}.json"
        self.assertTrue(chain_file.exists())

        # Verify chain file content
        with open(chain_file, "r") as f:
            chain_data = json.load(f)
            self.assertEqual(chain_data["chain_id"], chain_id)
            self.assertEqual(len(chain_data["nodes"]), 3)
            self.assertEqual(len(chain_data["edges"]), 2)

    def test_create_evidence_chain_invalid(self):
        """Test creating evidence chain with invalid data."""
        # Try to create chain with non-existent nodes
        with self.assertRaises(ValueError):
            self.evidence_store.create_evidence_chain(
                node_ids=["NONEXISTENT-1", "NONEXISTENT-2"],
                edge_ids=[],
                phases_covered=[8, 9],
            )

        # Try to create chain with non-existent edges
        node_id = self.evidence_store.add_causal_node(
            evidence_id="EVIDENCE-001", phase=8
        )

        with self.assertRaises(ValueError):
            self.evidence_store.create_evidence_chain(
                node_ids=[node_id], edge_ids=["NONEXISTENT-EDGE"], phases_covered=[8]
            )

    def test_link_evidence_across_phases(self):
        """Test linking evidence across phases."""
        result = self.evidence_store.link_evidence_across_phases(
            phase_a=8,
            phase_b=9,
            evidence_id_a="PHASE8-EVIDENCE-001",
            evidence_id_b="PHASE9-EVIDENCE-001",
            link_type=CausalLinkType.TEMPORAL,
            confidence_score=0.7,
        )

        self.assertEqual(len(result), 3)  # (node_id_a, node_id_b, edge_id)
        node_id_a, node_id_b, edge_id = result

        # Verify nodes were created
        self.assertIn(node_id_a, self.evidence_store.causal_graph)
        self.assertIn(node_id_b, self.evidence_store.causal_graph)

        # Verify edge was created
        self.assertIn(edge_id, self.evidence_store.causal_edges)

        # Verify metadata
        node_a = self.evidence_store.causal_graph[node_id_a]
        node_b = self.evidence_store.causal_graph[node_id_b]
        edge = self.evidence_store.causal_edges[edge_id]

        self.assertEqual(node_a.phase, 8)
        self.assertEqual(node_b.phase, 9)
        self.assertEqual(edge.link_type, CausalLinkType.TEMPORAL)
        self.assertEqual(edge.confidence_score, 0.7)

        # Check cross-phase metadata
        self.assertTrue(node_a.metadata.get("cross_phase_link", False))
        self.assertEqual(node_a.metadata.get("linked_phase"), 9)
        self.assertTrue(node_b.metadata.get("cross_phase_link", False))
        self.assertEqual(node_b.metadata.get("linked_phase"), 8)

    def test_validate_chain_completeness(self):
        """Test chain completeness validation."""
        # Create a complete chain (3 nodes, 2 edges connecting them)
        node_ids = []
        for i in range(3):
            node_id = self.evidence_store.add_causal_node(
                evidence_id=f"TEST-{i}", phase=9
            )
            node_ids.append(node_id)

        edge_ids = []
        for i in range(2):
            edge_id = self.evidence_store.add_causal_edge(
                source_node_id=node_ids[i],
                target_node_id=node_ids[i + 1],
                link_type=CausalLinkType.DIRECT,
                confidence_score=0.8,
            )
            edge_ids.append(edge_id)

        # Create chain and check completeness
        chain_id = self.evidence_store.create_evidence_chain(
            node_ids=node_ids, edge_ids=edge_ids
        )

        chain = self.evidence_store.evidence_chains[chain_id]
        self.assertTrue(chain.is_complete)

        # Create an incomplete chain (disconnected nodes)
        node_id4 = self.evidence_store.add_causal_node(evidence_id="TEST-4", phase=9)

        chain_id2 = self.evidence_store.create_evidence_chain(
            node_ids=[node_ids[0], node_id4],  # No edge between these
            edge_ids=[],
        )

        chain2 = self.evidence_store.evidence_chains[chain_id2]
        self.assertFalse(chain2.is_complete)

    def test_save_and_load_causal_data(self):
        """Test saving and loading causal data."""
        # Create some test data
        node_id = self.evidence_store.add_causal_node(
            evidence_id="SAVE-TEST", phase=9, confidence=EvidenceConfidence.HIGH
        )

        # Create new instance to load data
        new_store = AdvancedEvidenceStore(base_path=self.test_dir)

        # Verify data was loaded
        self.assertIn(node_id, new_store.causal_graph)
        node = new_store.causal_graph[node_id]
        self.assertEqual(node.evidence_id, "SAVE-TEST")
        self.assertEqual(node.phase, 9)
        self.assertEqual(node.confidence, EvidenceConfidence.HIGH)

    def test_log_causality_inheritance(self):
        """Test that AdvancedEvidenceStore inherits log_causality from EvidenceStore."""
        # This tests that the parent class method is available
        self.evidence_store.log_causality(
            action="test_action",
            cause="test_cause",
            effect="test_effect",
            confidence="high",
            metadata={"test": True},
        )

        # Check that causality log was created
        causality_dir = Path(self.test_dir) / "causality"
        self.assertTrue(causality_dir.exists())

        # There should be at least one causality log file
        log_files = list(causality_dir.glob("*.json"))
        self.assertGreater(len(log_files), 0)


class TestEnums(unittest.TestCase):
    """Test cases for enumeration classes."""

    def test_evidence_confidence_enum(self):
        """Test EvidenceConfidence enum values."""
        self.assertEqual(EvidenceConfidence.HIGH.value, "high")
        self.assertEqual(EvidenceConfidence.MEDIUM.value, "medium")
        self.assertEqual(EvidenceConfidence.LOW.value, "low")
        self.assertEqual(EvidenceConfidence.SPECULATIVE.value, "speculative")

    def test_causal_link_type_enum(self):
        """Test CausalLinkType enum values."""
        self.assertEqual(CausalLinkType.DIRECT.value, "direct")
        self.assertEqual(CausalLinkType.INDIRECT.value, "indirect")
        self.assertEqual(CausalLinkType.CORRELATION.value, "correlation")
        self.assertEqual(CausalLinkType.TEMPORAL.value, "temporal")
        self.assertEqual(CausalLinkType.NECESSARY.value, "necessary")
        self.assertEqual(CausalLinkType.SUFFICIENT.value, "sufficient")


class TestDataClasses(unittest.TestCase):
    """Test cases for data classes."""

    def test_causal_node_dataclass(self):
        """Test CausalNode data class."""
        node = CausalNode(
            node_id="TEST-NODE",
            evidence_id="TEST-EVIDENCE",
            phase=9,
            timestamp=datetime.now(),
            confidence=EvidenceConfidence.HIGH,
            metadata={"key": "value"},
        )

        self.assertEqual(node.node_id, "TEST-NODE")
        self.assertEqual(node.evidence_id, "TEST-EVIDENCE")
        self.assertEqual(node.phase, 9)
        self.assertEqual(node.confidence, EvidenceConfidence.HIGH)
        self.assertEqual(node.metadata["key"], "value")

    def test_causal_edge_dataclass(self):
        """Test CausalEdge data class."""
        edge = CausalEdge(
            edge_id="TEST-EDGE",
            source_node_id="NODE-1",
            target_node_id="NODE-2",
            link_type=CausalLinkType.DIRECT,
            confidence_score=0.85,
            temporal_gap_seconds=3600.0,
            metadata={"test": True},
        )

        self.assertEqual(edge.edge_id, "TEST-EDGE")
        self.assertEqual(edge.source_node_id, "NODE-1")
        self.assertEqual(edge.target_node_id, "NODE-2")
        self.assertEqual(edge.link_type, CausalLinkType.DIRECT)
        self.assertEqual(edge.confidence_score, 0.85)
        self.assertEqual(edge.temporal_gap_seconds, 3600.0)
        self.assertEqual(edge.metadata["test"], True)

    def test_evidence_chain_dataclass(self):
        """Test EvidenceChain data class."""
        # Create sample nodes and edges
        node = CausalNode(
            node_id="NODE-1",
            evidence_id="EVIDENCE-1",
            phase=9,
            timestamp=datetime.now(),
            confidence=EvidenceConfidence.HIGH,
        )

        edge = CausalEdge(
            edge_id="EDGE-1",
            source_node_id="NODE-1",
            target_node_id="NODE-2",
            link_type=CausalLinkType.DIRECT,
            confidence_score=0.8,
        )

        chain = EvidenceChain(
            chain_id="TEST-CHAIN",
            nodes=[node],
            edges=[edge],
            overall_confidence=0.9,
            phases_covered=[9],
            is_complete=True,
        )

        self.assertEqual(chain.chain_id, "TEST-CHAIN")
        self.assertEqual(len(chain.nodes), 1)
        self.assertEqual(len(chain.edges), 1)
        self.assertEqual(chain.overall_confidence, 0.9)
        self.assertEqual(chain.phases_covered, [9])
        self.assertTrue(chain.is_complete)


if __name__ == "__main__":
    unittest.main()
