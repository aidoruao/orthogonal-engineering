#!/usr/bin/env python3
"""
AI Conversation Batch Processor for Orthogonal Engineering
==========================================================

Batch processes AI conversation files using orthogonal engineering methodology.
Applies canal detection, invariant extraction, and correspondence validation
to your collection of AI conversation files.

Key Features:
1. Batch processing of AI conversation clusters
2. Canal detection with statistical analysis
3. Invariant extraction and classification
4. Correspondence validation against filesystem
5. Falsifiable claims about conversation quality

Based on Orthogonal Engineering Principles:
- Invariant detection in AI outputs
- Correspondence validation with reality
- Falsifiable density measurements
- Mimicry vs grounding distinction

Author: Orthogonal Engineering System
Date: 2026-01-20
Version: 1.0.0
"""

import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Import existing orthogonal engineering tools
try:
    from canal_detector import analyze_conversation_file
except ImportError:
    # Fallback implementation
    def analyze_conversation_file(file_path: str) -> Dict:
        """Basic canal detection for conversation files."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Simple canal detection patterns
            patterns = {
                "explicit_invariant_tags": r"\[INVARIANT\].*?\[/INVARIANT\]",
                "code_blocks": r"```(?:python|javascript|bash|html|css|json)",
                "structured_answers": r"(?:Answer:|Solution:|Code:|Implementation:)",
                "constraint_language": r"\b(must|should|shall|required|verified|correct)\b",
                "model_mentions": r"\b(ChatGPT|Claude|DeepSeek|GPT-|Gemini|LLaMA)\b",
            }

            results = {}
            for pattern_name, pattern in patterns.items():
                matches = re.findall(pattern, content, re.IGNORECASE)
                results[pattern_name] = len(matches)
                results[f"{pattern_name}_examples"] = matches[:3]

            # Calculate basic metrics
            lines = content.split("\n")
            turns = len(
                [
                    l
                    for l in lines
                    if re.match(
                        r"^(?:User|Human|Assistant|AI|System):", l, re.IGNORECASE
                    )
                ]
            )

            results.update(
                {
                    "file_path": file_path,
                    "file_size": len(content),
                    "line_count": len(lines),
                    "turn_count": turns,
                    "canal_candidates": results.get("explicit_invariant_tags", 0)
                    + results.get("code_blocks", 0),
                    "scan_timestamp": datetime.now().isoformat(),
                }
            )

            return results

        except Exception as e:
            return {
                "file_path": file_path,
                "error": str(e),
                "scan_timestamp": datetime.now().isoformat(),
            }


@dataclass
class ConversationAnalysis:
    """Analysis results for a single conversation file."""

    file_path: str
    file_size: int
    line_count: int
    turn_count: int
    canal_candidates: int
    invariant_tags: int
    code_blocks: int
    constraint_statements: int
    detected_models: List[str]
    canal_density: float  # canal_candidates / turn_count
    scan_timestamp: str
    errors: List[str]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict:
        result = asdict(self)
        result["canal_density_pct"] = self.canal_density * 100
        return result


@dataclass
class ClusterAnalysis:
    """Analysis results for a cluster of conversation files."""

    cluster_id: str
    file_count: int
    total_size: int
    total_turns: int
    total_canal_candidates: int
    average_canal_density: float
    density_stddev: float
    model_distribution: Dict[str, int]
    date_range: Tuple[str, str]
    file_analyses: List[ConversationAnalysis]
    health_score: float  # 0.0 to 1.0
    recommendations: List[str]

    def to_dict(self) -> Dict:
        result = asdict(self)
        result["date_range"] = list(self.date_range)
        result["file_analyses"] = [fa.to_dict() for fa in self.file_analyses]
        result["average_canal_density_pct"] = self.average_canal_density * 100
        result["health_score_pct"] = self.health_score * 100
        return result


@dataclass
class BatchProcessingReport:
    """Complete batch processing report."""

    processing_id: str
    start_time: str
    end_time: str
    duration_seconds: float
    total_files_processed: int
    total_clusters_processed: int
    overall_canal_density: float
    cluster_analyses: List[ClusterAnalysis]
    key_findings: List[Dict[str, Any]]
    methodology_applied: List[str]
    correspondence_validations: List[Dict[str, Any]]
    falsifiable_claims: List[Dict[str, Any]]

    def to_dict(self) -> Dict:
        result = asdict(self)
        result["cluster_analyses"] = [ca.to_dict() for ca in self.cluster_analyses]
        result["overall_canal_density_pct"] = self.overall_canal_density * 100
        return result


class AIConversationProcessor:
    """
    Main processor class for batch analysis of AI conversations.

    Applies orthogonal engineering methodology to:
    1. Detect canals (invariant-bearing structures)
    2. Calculate invariant density
    3. Validate correspondence with filesystem
    4. Generate falsifiable claims
    5. Identify mimicry vs grounding patterns
    """

    def __init__(self, clusters_data: List[Dict]):
        """
        Initialize processor with conversation clusters.

        Args:
            clusters_data: List of cluster data from filesystem scanner
        """
        self.clusters_data = clusters_data
        self.cluster_analyses: List[ClusterAnalysis] = []
        self.report: Optional[BatchProcessingReport] = None

    def process_all_clusters(
        self, max_files_per_cluster: int = 50
    ) -> BatchProcessingReport:
        """
        Process all conversation clusters using orthogonal engineering.

        Args:
            max_files_per_cluster: Maximum files to process per cluster

        Returns:
            Complete batch processing report
        """
        processing_id = f"batch-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()

        print("=" * 70)
        print("ORTHOGONAL ENGINEERING - AI CONVERSATION BATCH PROCESSOR")
        print("=" * 70)
        print(f"Processing ID: {processing_id}")
        print(f"Clusters to process: {len(self.clusters_data)}")
        print(f"Methodology: Canal detection + Invariant extraction")
        print(f"Validation: Correspondence + Falsifiability")
        print("-" * 70)

        total_files = 0
        total_turns = 0
        total_canal_candidates = 0

        # Process each cluster
        for i, cluster_data in enumerate(self.clusters_data, 1):
            print(
                f"\n[Cluster {i}/{len(self.clusters_data)}] {cluster_data.get('cluster_id', f'cluster-{i}')}"
            )

            cluster_analysis = self._process_cluster(
                cluster_data, max_files_per_cluster
            )
            if cluster_analysis:
                self.cluster_analyses.append(cluster_analysis)
                total_files += cluster_analysis.file_count
                total_turns += cluster_analysis.total_turns
                total_canal_candidates += cluster_analysis.total_canal_candidates

                print(
                    f"  Files: {cluster_analysis.file_count}, Turns: {cluster_analysis.total_turns}"
                )
                print(f"  Canal density: {cluster_analysis.average_canal_density:.1%}")
                print(
                    f"  Models: {', '.join(cluster_analysis.model_distribution.keys())}"
                )

        # Calculate overall statistics
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        overall_canal_density = (
            total_canal_candidates / total_turns if total_turns > 0 else 0
        )

        # Generate report
        self.report = BatchProcessingReport(
            processing_id=processing_id,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            duration_seconds=duration,
            total_files_processed=total_files,
            total_clusters_processed=len(self.cluster_analyses),
            overall_canal_density=overall_canal_density,
            cluster_analyses=self.cluster_analyses,
            key_findings=self._generate_key_findings(),
            methodology_applied=[
                "Orthogonal Engineering Canal Detection",
                "Invariant Density Calculation",
                "Correspondence Validation",
                "Falsifiable Claim Generation",
                "Mimicry vs Grounding Analysis",
            ],
            correspondence_validations=self._perform_correspondence_validations(),
            falsifiable_claims=self._generate_falsifiable_claims(),
        )

        print("\n" + "=" * 70)
        print("BATCH PROCESSING COMPLETE")
        print("=" * 70)
        print(f"Total files processed: {total_files}")
        print(f"Total turns analyzed: {total_turns}")
        print(f"Overall canal density: {overall_canal_density:.1%}")
        print(f"Processing time: {duration:.1f} seconds")
        print(f"Clusters analyzed: {len(self.cluster_analyses)}")
        print("-" * 70)

        return self.report

    def _process_cluster(
        self, cluster_data: Dict, max_files: int
    ) -> Optional[ClusterAnalysis]:
        """Process a single cluster of conversation files."""
        file_paths = cluster_data.get("file_paths", [])
        if not file_paths:
            return None

        # Limit files for processing
        files_to_process = file_paths[:max_files]
        file_analyses = []

        print(f"  Processing {len(files_to_process)} files...")

        for file_path in files_to_process:
            analysis = self._analyze_single_file(file_path)
            if analysis:
                file_analyses.append(analysis)

        if not file_analyses:
            return None

        # Calculate cluster statistics
        file_count = len(file_analyses)
        total_size = sum(fa.file_size for fa in file_analyses)
        total_turns = sum(fa.turn_count for fa in file_analyses)
        total_canal_candidates = sum(fa.canal_candidates for fa in file_analyses)

        # Calculate canal densities
        densities = [fa.canal_density for fa in file_analyses if fa.turn_count > 0]
        avg_density = sum(densities) / len(densities) if densities else 0

        # Calculate standard deviation
        if len(densities) > 1:
            mean = avg_density
            variance = sum((d - mean) ** 2 for d in densities) / len(densities)
            stddev = variance**0.5
        else:
            stddev = 0

        # Model distribution
        model_counter = Counter()
        for fa in file_analyses:
            for model in fa.detected_models:
                model_counter[model] += 1

        # Date range
        dates = []
        for fa in file_analyses:
            if "scan_timestamp" in fa.metadata:
                dates.append(fa.metadata["scan_timestamp"])
        date_range = (min(dates), max(dates)) if dates else ("unknown", "unknown")

        # Health score (based on orthogonal engineering principles)
        health_score = self._calculate_cluster_health(file_analyses)

        # Recommendations
        recommendations = self._generate_cluster_recommendations(
            file_analyses, avg_density, health_score
        )

        return ClusterAnalysis(
            cluster_id=cluster_data.get("cluster_id", "unknown"),
            file_count=file_count,
            total_size=total_size,
            total_turns=total_turns,
            total_canal_candidates=total_canal_candidates,
            average_canal_density=avg_density,
            density_stddev=stddev,
            model_distribution=dict(model_counter),
            date_range=date_range,
            file_analyses=file_analyses,
            health_score=health_score,
            recommendations=recommendations,
        )

    def _analyze_single_file(self, file_path: str) -> Optional[ConversationAnalysis]:
        """Analyze a single conversation file."""
        try:
            # Use existing canal detector or fallback
            analysis_result = analyze_conversation_file(file_path)

            if "error" in analysis_result:
                return ConversationAnalysis(
                    file_path=file_path,
                    file_size=0,
                    line_count=0,
                    turn_count=0,
                    canal_candidates=0,
                    invariant_tags=0,
                    code_blocks=0,
                    constraint_statements=0,
                    detected_models=[],
                    canal_density=0,
                    scan_timestamp=datetime.now().isoformat(),
                    errors=[analysis_result["error"]],
                    metadata=analysis_result,
                )

            # Extract metrics
            file_size = analysis_result.get("file_size", 0)
            line_count = analysis_result.get("line_count", 0)
            turn_count = analysis_result.get("turn_count", 0)
            canal_candidates = analysis_result.get("canal_candidates", 0)

            # Count specific patterns
            invariant_tags = len(
                analysis_result.get("explicit_invariant_tags_examples", [])
            )
            code_blocks = len(analysis_result.get("code_blocks_examples", []))
            constraint_statements = len(
                analysis_result.get("constraint_language_examples", [])
            )

            # Detect models from content
            detected_models = []
            model_matches = analysis_result.get("model_mentions_examples", [])
            for match in model_matches:
                if "chatgpt" in match.lower() or "gpt-" in match.lower():
                    detected_models.append("ChatGPT")
                elif "claude" in match.lower():
                    detected_models.append("Claude")
                elif "deepseek" in match.lower():
                    detected_models.append("DeepSeek")
                elif "gemini" in match.lower():
                    detected_models.append("Gemini")

            # Remove duplicates
            detected_models = list(set(detected_models))

            # Calculate canal density
            canal_density = canal_candidates / turn_count if turn_count > 0 else 0

            return ConversationAnalysis(
                file_path=file_path,
                file_size=file_size,
                line_count=line_count,
                turn_count=turn_count,
                canal_candidates=canal_candidates,
                invariant_tags=invariant_tags,
                code_blocks=code_blocks,
                constraint_statements=constraint_statements,
                detected_models=detected_models,
                canal_density=canal_density,
                scan_timestamp=analysis_result.get(
                    "scan_timestamp", datetime.now().isoformat()
                ),
                errors=[],
                metadata=analysis_result,
            )

        except Exception as e:
            return ConversationAnalysis(
                file_path=file_path,
                file_size=0,
                line_count=0,
                turn_count=0,
                canal_candidates=0,
                invariant_tags=0,
                code_blocks=0,
                constraint_statements=0,
                detected_models=[],
                canal_density=0,
                scan_timestamp=datetime.now().isoformat(),
                errors=[str(e)],
                metadata={},
            )

    def _calculate_cluster_health(
        self, file_analyses: List[ConversationAnalysis]
    ) -> float:
        """Calculate health score for a cluster based on orthogonal engineering principles."""
        if not file_analyses:
            return 0.0

        scores = []

        for fa in file_analyses:
            file_score = 0.0

            # Score based on canal density (higher is better)
            if fa.canal_density > 0:
                file_score += min(fa.canal_density * 2, 0.4)  # Up to 40%

            # Score based on explicit invariant tags
            if fa.invariant_tags > 0:
                file_score += 0.2

            # Score based on code blocks (grounding evidence)
            if fa.code_blocks > 0:
                file_score += 0.2

            # Score based on constraint language
            if fa.constraint_statements > 0:
                file_score += 0.1

            # Penalty for errors
            if fa.errors:
                file_score -= 0.1

            scores.append(max(0.0, min(1.0, file_score)))

        return sum(scores) / len(scores) if scores else 0.0

    def _generate_cluster_recommendations(
        self,
        file_analyses: List[ConversationAnalysis],
        avg_density: float,
        health_score: float,
    ) -> List[str]:
        """Generate recommendations for a cluster."""
        recommendations = []

        # Based on orthogonal engineering methodology
        if avg_density < 0.05:
            recommendations.append(
                "Low canal density - consider manual review for invariant extraction"
            )
        elif avg_density > 0.20:
            recommendations.append(
                "High canal density - good candidate for automated invariant extraction"
            )

        if health_score < 0.5:
            recommendations.append(
                "Low health score - apply correspondence validation to key claims"
            )

        # Check for specific patterns
        total_invariant_tags = sum(fa.invariant_tags for fa in file_analyses)
        if total_invariant_tags == 0:
            recommendations.append(
                "No explicit [INVARIANT] tags found - consider adding invariant tagging"
            )

        total_code_blocks = sum(fa.code_blocks for fa in file_analyses)
        if total_code_blocks > 10:
            recommendations.append(
                "Multiple code blocks present - good for correspondence validation"
            )

        return recommendations

    def _generate_key_findings(self) -> List[Dict[str, Any]]:
        """Generate key findings from batch processing."""
        findings = []

        if not self.cluster_analyses:
            return findings

        # Overall statistics
        total_files = sum(ca.file_count for ca in self.cluster_analyses)
        total_turns = sum(ca.total_turns for ca in self.cluster_analyses)
        total_canal_candidates = sum(
            ca.total_canal_candidates for ca in self.cluster_analyses
        )

        overall_density = total_canal_candidates / total_turns if total_turns > 0 else 0

        findings.append(
            {
                "type": "overall_statistics",
                "description": f"Processed {total_files} files with {total_turns} turns",
                "confidence": 0.95,
                "evidence": [f"Overall canal density: {overall_density:.1%}"],
                "methodology": "Orthogonal Engineering Canal Detection",
            }
        )

        # Density findings
        densities = [ca.average_canal_density for ca in self.cluster_analyses]
        if densities:
            avg_density = sum(densities) / len(densities)
            max_density = max(densities)
            min_density = min(densities)

            findings.append(
                {
                    "type": "density_analysis",
                    "description": f"Canal density ranges from {min_density:.1%} to {max_density:.1%}",
                    "confidence": 0.85,
                    "evidence": [f"Average density: {avg_density:.1%}"],
                    "methodology": "Invariant Density Calculation",
                }
            )

        # Model distribution findings
        all_models = {}
        for ca in self.cluster_analyses:
            for model, count in ca.model_distribution.items():
                all_models[model] = all_models.get(model, 0) + count

        if all_models:
            top_models = sorted(all_models.items(), key=lambda x: x[1], reverse=True)[
                :3
            ]
            findings.append(
                {
                    "type": "model_distribution",
                    "description": f"Top AI models: {', '.join([f'{m} ({c} files)' for m, c in top_models])}",
                    "confidence": 0.9,
                    "evidence": [f"Total unique models: {len(all_models)}"],
                    "methodology": "Correspondence Validation",
                }
            )

        # Health findings
        health_scores = [ca.health_score for ca in self.cluster_analyses]
        if health_scores:
            avg_health = sum(health_scores) / len(health_scores)
            healthy_clusters = len([h for h in health_scores if h > 0.7])

            findings.append(
                {
                    "type": "cluster_health",
                    "description": f"{healthy_clusters}/{len(health_scores)} clusters have good health (score > 0.7)",
                    "confidence": 0.8,
                    "evidence": [f"Average health score: {avg_health:.1%}"],
                    "methodology": "Orthogonal Engineering Health Assessment",
                }
            )

        # Specific pattern findings
        total_invariant_tags = 0
        total_code_blocks = 0
        for ca in self.cluster_analyses:
            for fa in ca.file_analyses:
                total_invariant_tags += fa.invariant_tags
                total_code_blocks += fa.code_blocks

        if total_invariant_tags > 0:
            findings.append(
                {
                    "type": "invariant_tagging",
                    "description": f"Found {total_invariant_tags} explicit [INVARIANT] tags",
                    "confidence": 0.95,
                    "evidence": [
                        "Explicit invariant tagging indicates structured output"
                    ],
                    "methodology": "Invariant Pattern Detection",
                }
            )

        if total_code_blocks > 0:
            findings.append(
                {
                    "type": "code_grounding",
                    "description": f"Found {total_code_blocks} code blocks for correspondence validation",
                    "confidence": 0.9,
                    "evidence": ["Code blocks provide grounding for truth claims"],
                    "methodology": "Correspondence Validation",
                }
            )

        return findings
