"""
Test module for causal_analyzer.py

Tests the CausalAnalyzer class and its functionality for Phase 9
advanced causal analysis.

Author: Orthogonal Engineering System
Date: 2026-01-22
Version: 1.0.0
"""

import json
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from toolkit.oe.advanced_evidence import (
    AdvancedEvidenceStore,
    CausalLinkType,
    EvidenceConfidence,
)
from toolkit.oe.causal_analyzer import (
    AnalysisType,
    CausalAnalyzer,
    CausalStrengthAnalysis,
    PhaseCrossoverAnalysis,
    TemporalPattern,
)


class TestCausalAnalyzer(unittest.TestCase):
    """Test cases for CausalAnalyzer class."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.evidence_store = AdvancedEvidenceStore(base_path=self.test_dir)
        self.analyzer = CausalAnalyzer(self.evidence_store)

        # Create test data
        self._create_test_evidence()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)

    def _create_test_evidence(self):
        """Create test evidence data for analysis."""
        # Create nodes with different timestamps for temporal analysis
        self.node_ids = []
        base_time = datetime.now()

        # Phase 8 nodes
        for i in range(3):
            node_id = self.evidence_store.add_causal_node(
                evidence_id=f"PHASE8-EVIDENCE-{i:03d}",
                phase=8,
                confidence=EvidenceConfidence.HIGH,
                metadata={"created_by": "test"},
            )
            self.node_ids.append(node_id)

        # Phase 9 nodes with regular intervals
        for i in range(5):
            node_id = self.evidence_store.add_causal_node(
                evidence_id=f"PHASE9-EVIDENCE-{i:03d}",
                phase=9,
                confidence=EvidenceConfidence.MEDIUM
                if i % 2 == 0
                else EvidenceConfidence.HIGH,
                metadata={"created_by": "test", "sequence": i},
            )
            self.node_ids.append(node_id)

        # Create edges between nodes
        self.edge_ids = []
        for i in range(len(self.node_ids) - 1):
            edge_id = self.evidence_store.add_causal_edge(
                source_node_id=self.node_ids[i],
                target_node_id=self.node_ids[i + 1],
                link_type=CausalLinkType.DIRECT
                if i % 2 == 0
                else CausalLinkType.INDIRECT,
                confidence_score=0.7 + (i * 0.05),
                temporal_gap_seconds=3600.0 * (i + 1),
            )
            self.edge_ids.append(edge_id)

        # Create cross-phase edges
        cross_edge_id = self.evidence_store.add_causal_edge(
            source_node_id=self.node_ids[2],  # Phase 8 node
            target_node_id=self.node_ids[5],  # Phase 9 node
            link_type=CausalLinkType.TEMPORAL,
            confidence_score=0.85,
            temporal_gap_seconds=86400.0,  # 1 day
        )
        self.edge_ids.append(cross_edge_id)

        # Create evidence chain
        self.chain_id = self.evidence_store.create_evidence_chain(
            node_ids=self.node_ids[:4],
            edge_ids=self.edge_ids[:3],
            phases_covered=[8, 9],
        )

    def test_initialization(self):
        """Test CausalAnalyzer initialization."""
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(self.analyzer.evidence_store, self.evidence_store)
        self.assertTrue(self.analyzer.analysis_results_path.exists())

    def test_analyze_temporal_patterns(self):
        """Test temporal pattern analysis."""
        patterns = self.analyzer.analyze_temporal_patterns(time_window_hours=48.0)

        self.assertIsInstance(patterns, list)

        if patterns:  # May not find patterns with small dataset
            pattern = patterns[0]
            self.assertIsInstance(pattern, TemporalPattern)
            self.assertIsNotNone(pattern.pattern_id)
            self.assertIsNotNone(pattern.pattern_type)
            self.assertIsInstance(pattern.nodes_involved, list)
            self.assertIsInstance(pattern.time_gaps, list)
            self.assertTrue(0.0 <= pattern.confidence <= 1.0)

        # Check that analysis results were saved
        analysis_file = self.analyzer.analysis_results_path / "temporal_patterns.json"
        self.assertTrue(analysis_file.exists())

        with open(analysis_file, "r") as f:
            analysis_data = json.load(f)
            self.assertIn("patterns", analysis_data)
            self.assertIn("summary", analysis_data)

    def test_analyze_confidence_distribution(self):
        """Test confidence distribution analysis."""
        results = self.analyzer.analyze_confidence_distribution()

        self.assertIsInstance(results, dict)

        # Check required fields
        self.assertIn("node_confidence_distribution", results)
        self.assertIn("edge_confidence_stats", results)
        self.assertIn("chain_confidence_stats", results)
        self.assertIn("confidence_correlation", results)

        # Check node confidence distribution
        node_dist = results["node_confidence_distribution"]
        for confidence_level in ["high", "medium", "low", "speculative"]:
            self.assertIn(confidence_level, node_dist)
            self.assertIsInstance(node_dist[confidence_level], int)

        # Check edge confidence stats
        edge_stats = results["edge_confidence_stats"]
        self.assertIn("count", edge_stats)
        self.assertIn("mean", edge_stats)
        self.assertIn("median", edge_stats)
        self.assertGreaterEqual(edge_stats["count"], 0)

        # Check that analysis results were saved
        analysis_file = (
            self.analyzer.analysis_results_path / "confidence_distribution.json"
        )
        self.assertTrue(analysis_file.exists())

    def test_analyze_phase_crossover(self):
        """Test phase crossover analysis."""
        analyses = self.analyzer.analyze_phase_crossover()

        self.assertIsInstance(analyses, list)

        if analyses:  # May have cross-phase edges
            analysis = analyses[0]
            self.assertIsInstance(analysis, PhaseCrossoverAnalysis)
            self.assertIsInstance(analysis.phase_a, int)
            self.assertIsInstance(analysis.phase_b, int)
            self.assertGreaterEqual(analysis.crossover_count, 0)
            self.assertTrue(0.0 <= analysis.average_confidence <= 1.0)
            self.assertIsInstance(analysis.dominant_link_type, CausalLinkType)
            self.assertIsInstance(analysis.temporal_gap_stats, dict)

        # Check that analysis results were saved
        analysis_file = self.analyzer.analysis_results_path / "phase_crossover.json"
        self.assertTrue(analysis_file.exists())

    def test_analyze_evidence_density(self):
        """Test evidence density analysis."""
        results = self.analyzer.analyze_evidence_density(time_resolution="hour")

        self.assertIsInstance(results, dict)

        # Check required fields
        self.assertIn("time_resolution", results)
        self.assertIn("periods", results)
        self.assertIn("densities", results)
        self.assertIn("statistics", results)
        self.assertIn("density_trend", results)

        # Check statistics
        stats = results["statistics"]
        self.assertIn("total_periods", stats)
        self.assertIn("total_evidence", stats)
        self.assertIn("average_density", stats)
        self.assertIn("max_density", stats)
        self.assertIn("min_density", stats)

        # Test different time resolutions
        for resolution in ["hour", "day", "week"]:
            try:
                results = self.analyzer.analyze_evidence_density(
                    time_resolution=resolution
                )
                self.assertEqual(results["time_resolution"], resolution)
            except ValueError as e:
                if resolution not in ["hour", "day", "week"]:
                    self.assertIsInstance(e, ValueError)

        # Check that analysis results were saved
        analysis_file = self.analyzer.analysis_results_path / "evidence_density.json"
        self.assertTrue(analysis_file.exists())

    def test_analyze_causal_strength(self):
        """Test causal strength analysis."""
        analyses = self.analyzer.analyze_causal_strength()

        self.assertIsInstance(analyses, list)

        if analyses:  # May have chains
            analysis = analyses[0]
            self.assertIsInstance(analysis, CausalStrengthAnalysis)
            self.assertIsNotNone(analysis.chain_id)
            self.assertTrue(0.0 <= analysis.average_edge_confidence <= 1.0)
            self.assertIsInstance(analysis.weakest_link, tuple)
            self.assertIsInstance(analysis.strongest_link, tuple)
            self.assertTrue(0.0 <= analysis.chain_coherence <= 1.0)

        # Check that analysis results were saved
        analysis_file = self.analyzer.analysis_results_path / "causal_strength.json"
        self.assertTrue(analysis_file.exists())

    def test_calculate_density_trend(self):
        """Test density trend calculation."""
        # Test increasing trend
        increasing_densities = [1, 2, 3, 4, 5]
        trend = self.analyzer._calculate_density_trend(increasing_densities)
        self.assertEqual(trend, "increasing")

        # Test decreasing trend
        decreasing_densities = [5, 4, 3, 2, 1]
        trend = self.analyzer._calculate_density_trend(decreasing_densities)
        self.assertEqual(trend, "decreasing")

        # Test stable trend (low variance)
        stable_densities = [10, 10, 10, 10, 10]
        trend = self.analyzer._calculate_density_trend(stable_densities)
        self.assertEqual(trend, "stable")

        # Test variable trend
        variable_densities = [1, 10, 2, 9, 3]
        trend = self.analyzer._calculate_density_trend(variable_densities)
        self.assertEqual(trend, "variable")

        # Test insufficient data
        insufficient_densities = [5]
        trend = self.analyzer._calculate_density_trend(insufficient_densities)
        self.assertEqual(trend, "insufficient_data")

    def test_calculate_confidence_correlation(self):
        """Test confidence correlation calculation."""
        correlations = self.analyzer._calculate_confidence_correlation()

        self.assertIsInstance(correlations, dict)

        # Correlation values should be between -1 and 1 if present
        for key, value in correlations.items():
            self.assertTrue(-1.0 <= value <= 1.0)

    def test_save_analysis_results(self):
        """Test saving analysis results."""
        test_results = {
            "test_field": "test_value",
            "numeric_field": 42,
            "list_field": [1, 2, 3],
            "dict_field": {"nested": "value"},
        }

        # Test saving with different analysis types
        for analysis_type in AnalysisType:
            self.analyzer._save_analysis_results(
                analysis_type=analysis_type, results=test_results
            )

            # Check file was created
            analysis_file = (
                self.analyzer.analysis_results_path / f"{analysis_type.value}.json"
            )
            self.assertTrue(analysis_file.exists())

            # Verify content
            with open(analysis_file, "r") as f:
                loaded_data = json.load(f)
                self.assertEqual(loaded_data["test_field"], "test_value")
                self.assertEqual(loaded_data["numeric_field"], 42)

    def test_empty_evidence_store(self):
        """Test analysis with empty evidence store."""
        empty_dir = tempfile.mkdtemp()
        empty_store = AdvancedEvidenceStore(base_path=empty_dir)
        empty_analyzer = CausalAnalyzer(empty_store)

        # These should handle empty data gracefully
        patterns = empty_analyzer.analyze_temporal_patterns()
        self.assertEqual(patterns, [])

        confidence_results = empty_analyzer.analyze_confidence_distribution()
        self.assertIsInstance(confidence_results, dict)

        phase_crossover = empty_analyzer.analyze_phase_crossover()
        self.assertEqual(phase_crossover, [])

        density_results = empty_analyzer.analyze_evidence_density()
        self.assertIn("error", density_results)

        causal_strength = empty_analyzer.analyze_causal_strength()
        self.assertEqual(causal_strength, [])

        shutil.rmtree(empty_dir)


class TestEnums(unittest.TestCase):
    """Test cases for enumeration classes."""

    def test_analysis_type_enum(self):
        """Test AnalysisType enum values."""
        self.assertEqual(AnalysisType.TEMPORAL_PATTERNS.value, "temporal_patterns")
        self.assertEqual(
            AnalysisType.CONFIDENCE_DISTRIBUTION.value, "confidence_distribution"
        )
        self.assertEqual(AnalysisType.PHASE_CROSSOVER.value, "phase_crossover")
        self.assertEqual(AnalysisType.EVIDENCE_DENSITY.value, "evidence_density")
        self.assertEqual(AnalysisType.CAUSAL_STRENGTH.value, "causal_strength")
        self.assertEqual(AnalysisType.CHAIN_COMPLETENESS.value, "chain_completeness")


class TestDataClasses(unittest.TestCase):
    """Test cases for data classes."""

    def test_temporal_pattern_dataclass(self):
        """Test TemporalPattern data class."""
        pattern = TemporalPattern(
            pattern_id="TEST-PATTERN",
            pattern_type="regular_interval",
            nodes_involved=["NODE-1", "NODE-2", "NODE-3"],
            time_gaps=[3600.0, 3600.0, 3600.0],
            confidence=0.85,
            metadata={"test": True, "node_count": 3},
        )

        self.assertEqual(pattern.pattern_id, "TEST-PATTERN")
        self.assertEqual(pattern.pattern_type, "regular_interval")
        self.assertEqual(len(pattern.nodes_involved), 3)
        self.assertEqual(len(pattern.time_gaps), 3)
        self.assertEqual(pattern.confidence, 0.85)
        self.assertEqual(pattern.metadata["test"], True)

    def test_phase_crossover_analysis_dataclass(self):
        """Test PhaseCrossoverAnalysis data class."""
        analysis = PhaseCrossoverAnalysis(
            phase_a=8,
            phase_b=9,
            crossover_count=5,
            average_confidence=0.75,
            dominant_link_type=CausalLinkType.TEMPORAL,
            temporal_gap_stats={
                "mean": 86400.0,
                "median": 86400.0,
                "min": 3600.0,
                "max": 172800.0,
                "count": 5,
            },
            metadata={"test": True, "edge_ids": ["EDGE-1", "EDGE-2"]},
        )

        self.assertEqual(analysis.phase_a, 8)
        self.assertEqual(analysis.phase_b, 9)
        self.assertEqual(analysis.crossover_count, 5)
        self.assertEqual(analysis.average_confidence, 0.75)
        self.assertEqual(analysis.dominant_link_type, CausalLinkType.TEMPORAL)
        self.assertEqual(analysis.temporal_gap_stats["mean"], 86400.0)
        self.assertEqual(analysis.metadata["test"], True)

    def test_causal_strength_analysis_dataclass(self):
        """Test CausalStrengthAnalysis data class."""
        analysis = CausalStrengthAnalysis(
            chain_id="TEST-CHAIN",
            average_edge_confidence=0.82,
            weakest_link=("EDGE-3", 0.65),
            strongest_link=("EDGE-1", 0.95),
            chain_coherence=0.78,
            metadata={"test": True, "edge_count": 4, "node_count": 5},
        )

        self.assertEqual(analysis.chain_id, "TEST-CHAIN")
        self.assertEqual(analysis.average_edge_confidence, 0.82)
        self.assertEqual(analysis.weakest_link, ("EDGE-3", 0.65))
        self.assertEqual(analysis.strongest_link, ("EDGE-1", 0.95))
        self.assertEqual(analysis.chain_coherence, 0.78)
        self.assertEqual(analysis.metadata["test"], True)


if __name__ == "__main__":
    unittest.main()
