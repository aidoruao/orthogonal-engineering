"""
Causal Analyzer Module for Phase 9 Toolkit Expansion

Implements advanced causal analysis capabilities for Orthogonal Engineering methodology.
Provides tools for analyzing causal relationships, temporal patterns, and evidence chains.

Author: Orthogonal Engineering System
Date: 2026-01-22
Version: 1.0.0
"""

import json
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import matplotlib.pyplot as plt
import networkx as nx

from .advanced_evidence import (
    AdvancedEvidenceStore,
    CausalEdge,
    CausalLinkType,
    CausalNode,
    EvidenceChain,
    EvidenceConfidence,
)


class AnalysisType(Enum):
    """Types of causal analysis."""

    TEMPORAL_PATTERNS = "temporal_patterns"
    CONFIDENCE_DISTRIBUTION = "confidence_distribution"
    PHASE_CROSSOVER = "phase_crossover"
    EVIDENCE_DENSITY = "evidence_density"
    CAUSAL_STRENGTH = "causal_strength"
    CHAIN_COMPLETENESS = "chain_completeness"


@dataclass
class TemporalPattern:
    """Pattern detected in temporal sequence of evidence."""

    pattern_id: str
    pattern_type: str
    nodes_involved: List[str]
    time_gaps: List[float]
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PhaseCrossoverAnalysis:
    """Analysis of evidence crossover between phases."""

    phase_a: int
    phase_b: int
    crossover_count: int
    average_confidence: float
    dominant_link_type: CausalLinkType
    temporal_gap_stats: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CausalStrengthAnalysis:
    """Analysis of causal strength in evidence chains."""

    chain_id: str
    average_edge_confidence: float
    weakest_link: Tuple[str, float]  # (edge_id, confidence)
    strongest_link: Tuple[str, float]  # (edge_id, confidence)
    chain_coherence: float  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class CausalAnalyzer:
    """
    Advanced causal analyzer for Orthogonal Engineering evidence.

    Provides:
    1. Temporal pattern analysis
    2. Confidence distribution analysis
    3. Phase crossover analysis
    4. Evidence density analysis
    5. Causal strength analysis
    6. Chain completeness analysis
    """

    def __init__(self, evidence_store: AdvancedEvidenceStore):
        """
        Initialize causal analyzer.

        Args:
            evidence_store: AdvancedEvidenceStore instance to analyze
        """
        self.evidence_store = evidence_store
        self.analysis_results_path = Path("logs/analysis/causal")
        self.analysis_results_path.mkdir(parents=True, exist_ok=True)

    def analyze_temporal_patterns(
        self, time_window_hours: float = 24.0
    ) -> List[TemporalPattern]:
        """
        Analyze temporal patterns in evidence.

        Args:
            time_window_hours: Time window for pattern detection in hours

        Returns:
            List of detected temporal patterns
        """
        patterns = []
        time_window = timedelta(hours=time_window_hours)

        # Group nodes by timestamp
        nodes_by_time = sorted(
            self.evidence_store.causal_graph.values(), key=lambda n: n.timestamp
        )

        if len(nodes_by_time) < 2:
            return patterns

        # Detect temporal clusters
        current_cluster = [nodes_by_time[0]]
        clusters = []

        for i in range(1, len(nodes_by_time)):
            time_gap = nodes_by_time[i].timestamp - nodes_by_time[i - 1].timestamp
            if time_gap <= time_window:
                current_cluster.append(nodes_by_time[i])
            else:
                if len(current_cluster) >= 2:
                    clusters.append(current_cluster)
                current_cluster = [nodes_by_time[i]]

        if len(current_cluster) >= 2:
            clusters.append(current_cluster)

        # Analyze each cluster
        for cluster_idx, cluster in enumerate(clusters):
            # Calculate time gaps
            timestamps = [node.timestamp for node in cluster]
            time_gaps = []
            for i in range(1, len(timestamps)):
                gap = (timestamps[i] - timestamps[i - 1]).total_seconds()
                time_gaps.append(gap)

            # Calculate pattern confidence
            if time_gaps:
                gap_variance = (
                    statistics.variance(time_gaps) if len(time_gaps) > 1 else 0
                )
                # Lower variance = more regular pattern
                confidence = 1.0 / (1.0 + gap_variance)
            else:
                confidence = 0.5

            # Determine pattern type
            if len(cluster) >= 3:
                if all(0.8 <= gap / time_gaps[0] <= 1.2 for gap in time_gaps[1:]):
                    pattern_type = "regular_interval"
                elif all(
                    time_gaps[i] < time_gaps[i + 1] for i in range(len(time_gaps) - 1)
                ):
                    pattern_type = "increasing_interval"
                elif all(
                    time_gaps[i] > time_gaps[i + 1] for i in range(len(time_gaps) - 1)
                ):
                    pattern_type = "decreasing_interval"
                else:
                    pattern_type = "irregular_cluster"
            else:
                pattern_type = "pair"

            pattern = TemporalPattern(
                pattern_id=f"PATTERN-{cluster_idx:04d}",
                pattern_type=pattern_type,
                nodes_involved=[node.node_id for node in cluster],
                time_gaps=time_gaps,
                confidence=min(confidence, 1.0),
                metadata={
                    "cluster_size": len(cluster),
                    "time_window_hours": time_window_hours,
                    "phases": list(set(node.phase for node in cluster)),
                },
            )
            patterns.append(pattern)

        # Save analysis results
        self._save_analysis_results(
            analysis_type=AnalysisType.TEMPORAL_PATTERNS,
            results={
                "patterns": [
                    {
                        "pattern_id": p.pattern_id,
                        "pattern_type": p.pattern_type,
                        "nodes_involved": p.nodes_involved,
                        "time_gaps": p.time_gaps,
                        "confidence": p.confidence,
                        "metadata": p.metadata,
                    }
                    for p in patterns
                ],
                "summary": {
                    "total_patterns": len(patterns),
                    "average_confidence": statistics.mean(
                        [p.confidence for p in patterns]
                    )
                    if patterns
                    else 0,
                    "pattern_types": Counter([p.pattern_type for p in patterns]),
                },
            },
        )

        return patterns

    def analyze_confidence_distribution(self) -> Dict[str, Any]:
        """
        Analyze confidence distribution across evidence.

        Returns:
            Dictionary with confidence distribution statistics
        """
        # Node confidence distribution
        node_confidences = {"high": 0, "medium": 0, "low": 0, "speculative": 0}

        for node in self.evidence_store.causal_graph.values():
            node_confidences[node.confidence.value] += 1

        # Edge confidence distribution
        edge_confidences = [
            edge.confidence_score for edge in self.evidence_store.causal_edges.values()
        ]

        # Chain confidence distribution
        chain_confidences = [
            chain.overall_confidence
            for chain in self.evidence_store.evidence_chains.values()
        ]

        analysis_results = {
            "node_confidence_distribution": node_confidences,
            "edge_confidence_stats": {
                "count": len(edge_confidences),
                "mean": statistics.mean(edge_confidences) if edge_confidences else 0,
                "median": statistics.median(edge_confidences)
                if edge_confidences
                else 0,
                "std_dev": statistics.stdev(edge_confidences)
                if len(edge_confidences) > 1
                else 0,
                "min": min(edge_confidences) if edge_confidences else 0,
                "max": max(edge_confidences) if edge_confidences else 0,
            },
            "chain_confidence_stats": {
                "count": len(chain_confidences),
                "mean": statistics.mean(chain_confidences) if chain_confidences else 0,
                "median": statistics.median(chain_confidences)
                if chain_confidences
                else 0,
                "std_dev": statistics.stdev(chain_confidences)
                if len(chain_confidences) > 1
                else 0,
                "min": min(chain_confidences) if chain_confidences else 0,
                "max": max(chain_confidences) if chain_confidences else 0,
            },
            "confidence_correlation": self._calculate_confidence_correlation(),
        }

        # Save analysis results
        self._save_analysis_results(
            analysis_type=AnalysisType.CONFIDENCE_DISTRIBUTION, results=analysis_results
        )

        return analysis_results

    def _calculate_confidence_correlation(self) -> Dict[str, float]:
        """
        Calculate correlation between different confidence measures.

        Returns:
            Dictionary with correlation metrics
        """
        correlations = {}

        if len(self.evidence_store.evidence_chains) >= 2:
            # Calculate correlation between chain confidence and average edge confidence
            chain_data = []
            for chain in self.evidence_store.evidence_chains.values():
                if chain.edges:
                    avg_edge_confidence = sum(
                        edge.confidence_score for edge in chain.edges
                    ) / len(chain.edges)
                    chain_data.append((chain.overall_confidence, avg_edge_confidence))

            if len(chain_data) >= 2:
                chain_confs, edge_confs = zip(*chain_data)
                try:
                    correlations["chain_vs_edge"] = statistics.correlation(
                        chain_confs, edge_confs
                    )
                except statistics.StatisticsError:
                    correlations["chain_vs_edge"] = 0.0

        return correlations

    def analyze_phase_crossover(self) -> List[PhaseCrossoverAnalysis]:
        """
        Analyze evidence crossover between phases.

        Returns:
            List of phase crossover analyses
        """
        analyses = []

        # Get all phases present in evidence
        phases = sorted(
            set(node.phase for node in self.evidence_store.causal_graph.values())
        )

        if len(phases) < 2:
            return analyses

        # Analyze each phase pair
        for i in range(len(phases)):
            for j in range(i + 1, len(phases)):
                phase_a = phases[i]
                phase_b = phases[j]

                # Find edges connecting phases
                crossover_edges = []
                for edge in self.evidence_store.causal_edges.values():
                    source_node = self.evidence_store.causal_graph[edge.source_node_id]
                    target_node = self.evidence_store.causal_graph[edge.target_node_id]

                    if (
                        source_node.phase == phase_a and target_node.phase == phase_b
                    ) or (
                        source_node.phase == phase_b and target_node.phase == phase_a
                    ):
                        crossover_edges.append(edge)

                if not crossover_edges:
                    continue

                # Calculate statistics
                confidence_scores = [edge.confidence_score for edge in crossover_edges]
                link_types = [edge.link_type for edge in crossover_edges]
                temporal_gaps = [
                    edge.temporal_gap_seconds
                    for edge in crossover_edges
                    if edge.temporal_gap_seconds is not None
                ]

                # Find dominant link type
                link_type_counts = Counter(link_types)
                dominant_link_type = link_type_counts.most_common(1)[0][0]

                # Calculate temporal gap statistics
                temporal_stats = {}
                if temporal_gaps:
                    temporal_stats = {
                        "mean": statistics.mean(temporal_gaps),
                        "median": statistics.median(temporal_gaps)
                        if len(temporal_gaps) > 1
                        else temporal_gaps[0],
                        "min": min(temporal_gaps),
                        "max": max(temporal_gaps),
                        "count": len(temporal_gaps),
                    }

                analysis = PhaseCrossoverAnalysis(
                    phase_a=phase_a,
                    phase_b=phase_b,
                    crossover_count=len(crossover_edges),
                    average_confidence=statistics.mean(confidence_scores),
                    dominant_link_type=dominant_link_type,
                    temporal_gap_stats=temporal_stats,
                    metadata={
                        "edge_ids": [edge.edge_id for edge in crossover_edges],
                        "confidence_distribution": {
                            "mean": statistics.mean(confidence_scores),
                            "std_dev": statistics.stdev(confidence_scores)
                            if len(confidence_scores) > 1
                            else 0,
                        },
                    },
                )
                analyses.append(analysis)

        # Save analysis results
        self._save_analysis_results(
            analysis_type=AnalysisType.PHASE_CROSSOVER,
            results={
                "analyses": [
                    {
                        "phase_a": a.phase_a,
                        "phase_b": a.phase_b,
                        "crossover_count": a.crossover_count,
                        "average_confidence": a.average_confidence,
                        "dominant_link_type": a.dominant_link_type.value,
                        "temporal_gap_stats": a.temporal_gap_stats,
                        "metadata": a.metadata,
                    }
                    for a in analyses
                ],
                "summary": {
                    "total_crossovers": sum(a.crossover_count for a in analyses),
                    "phase_pairs_analyzed": len(analyses),
                    "average_crossover_confidence": statistics.mean(
                        [a.average_confidence for a in analyses]
                    )
                    if analyses
                    else 0,
                },
            },
        )

        return analyses

    def analyze_evidence_density(self, time_resolution: str = "hour") -> Dict[str, Any]:
        """
        Analyze evidence density over time.

        Args:
            time_resolution: Time resolution for density analysis ("hour", "day", "week")

        Returns:
            Dictionary with evidence density statistics
        """
        if not self.evidence_store.causal_graph:
            return {"error": "No evidence available for density analysis"}

        # Group evidence by time period
        nodes_by_time = sorted(
            self.evidence_store.causal_graph.values(), key=lambda n: n.timestamp
        )

        # Determine time resolution
        if time_resolution == "hour":
            time_format = "%Y-%m-%d %H:00"
            delta = timedelta(hours=1)
        elif time_resolution == "day":
            time_format = "%Y-%m-%d"
            delta = timedelta(days=1)
        elif time_resolution == "week":
            time_format = "%Y-W%W"
            delta = timedelta(weeks=1)
        else:
            raise ValueError(f"Unsupported time resolution: {time_resolution}")

        # Group nodes by time period
        time_periods = defaultdict(list)
        for node in nodes_by_time:
            if time_resolution == "week":
                period = node.timestamp.strftime(time_format)
            else:
                period = node.timestamp.strftime(time_format)
            time_periods[period].append(node)

        # Calculate density statistics
        periods = sorted(time_periods.keys())
        densities = [len(time_periods[period]) for period in periods]

        analysis_results = {
            "time_resolution": time_resolution,
            "periods": periods,
            "densities": densities,
            "statistics": {
                "total_periods": len(periods),
                "total_evidence": sum(densities),
                "average_density": statistics.mean(densities) if densities else 0,
                "max_density": max(densities) if densities else 0,
                "min_density": min(densities) if densities else 0,
                "density_variance": statistics.variance(densities)
                if len(densities) > 1
                else 0,
            },
            "density_trend": self._calculate_density_trend(densities),
        }

        # Save analysis results
        self._save_analysis_results(
            analysis_type=AnalysisType.EVIDENCE_DENSITY, results=analysis_results
        )

        return analysis_results

    def _calculate_density_trend(self, densities: List[int]) -> str:
        """
        Calculate trend in evidence density.

        Args:
            densities: List of density values over time

        Returns:
            Trend description ("increasing", "decreasing", "stable", "variable")
        """
        if len(densities) < 2:
            return "insufficient_data"

        # Simple trend detection
        increasing = all(
            densities[i] <= densities[i + 1] for i in range(len(densities) - 1)
        )
        decreasing = all(
            densities[i] >= densities[i + 1] for i in range(len(densities) - 1)
        )

        if increasing:
            return "increasing"
        elif decreasing:
            return "decreasing"
        else:
            # Check if mostly stable
            mean_density = statistics.mean(densities)
            variance = statistics.variance(densities) if len(densities) > 1 else 0
            if variance < mean_density * 0.1:  # Less than 10% variation
                return "stable"
            else:
                return "variable"

    def analyze_causal_strength(self) -> List[CausalStrengthAnalysis]:
        """
        Analyze causal strength in evidence chains.

        Returns:
            List of causal strength analyses
        """
        analyses = []

        for chain_id, chain in self.evidence_store.evidence_chains.items():
            if not chain.edges:
                continue

            # Calculate edge confidence statistics
            edge_confidences = [edge.confidence_score for edge in chain.edges]
            avg_edge_confidence = statistics.mean(edge_confidences)

            # Find weakest and strongest links
            weakest_edge = min(chain.edges, key=lambda e: e.confidence_score)
            strongest_edge = max(chain.edges, key=lambda e: e.confidence_score)

            # Calculate chain coherence (how consistent are confidence scores)
            if len(edge_confidences) > 1:
                coherence = 1.0 - (
                    statistics.stdev(edge_confidences) / avg_edge_confidence
                )
                coherence = max(0.0, min(1.0, coherence))
            else:
                coherence = 1.0

            analysis = CausalStrengthAnalysis(
                chain_id=chain_id,
                average_edge_confidence=avg_edge_confidence,
                weakest_link=(weakest_edge.edge_id, weakest_edge.confidence_score),
                strongest_link=(
                    strongest_edge.edge_id,
                    strongest_edge.confidence_score,
                ),
                chain_coherence=coherence,
                metadata={
                    "node_count": len(chain.nodes),
                    "edge_count": len(chain.edges),
                    "phases_covered": chain.phases_covered,
                    "is_complete": chain.is_complete,
                    "analysis_timestamp": datetime.now().isoformat(),
                },
            )

            analyses[chain_id] = analysis

            # Log the analysis
            self.evidence_store.log_causality(
                action="analyze_causal_strength",
                cause=f"Evidence chain {chain_id}",
                effect="Causal strength analysis completed",
                confidence=f"{avg_edge_confidence:.2f}",
                metadata={
                    "chain_id": chain_id,
                    "average_confidence": avg_edge_confidence,
                    "weakest_link_confidence": weakest_edge.confidence_score,
                    "strongest_link_confidence": strongest_edge.confidence_score,
                    "coherence": coherence,
                },
            )

        return analyses
