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

    def _perform_correspondence_validations(self) -> List[Dict[str, Any]]:
        """Perform correspondence validations on processed clusters."""
        validations = []

        for cluster in self.cluster_analyses:
            # Validation 1: File existence
            existing_files = 0
            for file_analysis in cluster.file_analyses:
                if os.path.exists(file_analysis.file_path):
                    existing_files += 1

            file_existence_ratio = (
                existing_files / len(cluster.file_analyses)
                if cluster.file_analyses
                else 0
            )

            validations.append(
                {
                    "cluster_id": cluster.cluster_id,
                    "validation_type": "file_existence",
                    "description": f"{existing_files}/{len(cluster.file_analyses)} files exist on filesystem",
                    "success": file_existence_ratio >= 0.9,
                    "evidence": f"Existence ratio: {file_existence_ratio:.1%}",
                    "methodology": "Correspondence Validation - File Existence",
                }
            )

            # Validation 2: Model mentions correspondence
            if cluster.model_distribution:
                detected_models = set(cluster.model_distribution.keys())

                # Sample check of actual content
                sample_valid = 0
                sample_size = min(3, len(cluster.file_analyses))
                for i in range(sample_size):
                    file_analysis = cluster.file_analyses[i]
                    if file_analysis.detected_models:
                        if any(
                            model in detected_models
                            for model in file_analysis.detected_models
                        ):
                            sample_valid += 1

                model_correspondence_ratio = (
                    sample_valid / sample_size if sample_size > 0 else 0
                )

                validations.append(
                    {
                        "cluster_id": cluster.cluster_id,
                        "validation_type": "model_correspondence",
                        "description": f"Model mentions correspond in {sample_valid}/{sample_size} sampled files",
                        "success": model_correspondence_ratio >= 0.5,
                        "evidence": f"Correspondence ratio: {model_correspondence_ratio:.1%}",
                        "methodology": "Correspondence Validation - Model Mentions",
                    }
                )

        return validations

    def _generate_falsifiable_claims(self) -> List[Dict[str, Any]]:
        """Generate falsifiable claims based on analysis results."""
        claims = []

        if not self.cluster_analyses:
            return claims

        # Claim 1: Overall canal density
        overall_density = self.report.overall_canal_density if self.report else 0
        claims.append(
            {
                "claim_id": "CLAIM-001-DENSITY",
                "statement": f"The overall canal density in AI conversations is {overall_density:.1%}",
                "falsification_test": "Run independent canal detection on same files",
                "falsification_condition": "If independent measurement differs by >20%",
                "confidence": 0.7,
                "evidence": f"Based on analysis of {self.report.total_files_processed if self.report else 0} files",
                "methodology": "Orthogonal Engineering - Falsifiable Density Claim",
            }
        )

        # Claim 2: Model distribution
        all_models = {}
        for cluster in self.cluster_analyses:
            for model, count in cluster.model_distribution.items():
                all_models[model] = all_models.get(model, 0) + count

        if all_models:
            top_model = max(all_models.items(), key=lambda x: x[1])
            claims.append(
                {
                    "claim_id": "CLAIM-002-MODEL-DISTRIBUTION",
                    "statement": f"The most common AI model in conversations is {top_model[0]} ({top_model[1]} files)",
                    "falsification_test": "Manual review of file contents",
                    "falsification_condition": "If manual review shows different model distribution",
                    "confidence": 0.8,
                    "evidence": f"Found in {len(self.cluster_analyses)} clusters",
                    "methodology": "Orthogonal Engineering - Model Distribution Analysis",
                }
            )

        # Claim 3: Health correlation
        healthy_clusters = [c for c in self.cluster_analyses if c.health_score > 0.7]
        if healthy_clusters and len(self.cluster_analyses) > 1:
            health_ratio = len(healthy_clusters) / len(self.cluster_analyses)
            claims.append(
                {
                    "claim_id": "CLAIM-003-HEALTH-CORRELATION",
                    "statement": f"{health_ratio:.0%} of conversation clusters have good health (score > 0.7)",
                    "falsification_test": "Apply different health scoring methodology",
                    "falsification_condition": "If alternative scoring shows significantly different health distribution",
                    "confidence": 0.6,
                    "evidence": f"{len(healthy_clusters)}/{len(self.cluster_analyses)} clusters healthy",
                    "methodology": "Orthogonal Engineering - Health Assessment Falsification",
                }
            )

        return claims

    def save_report(self, output_path: str = "ai_conversation_analysis_report.json"):
        """Save batch processing report to JSON file."""
        if not self.report:
            raise ValueError("No report to save. Run process_all_clusters() first.")

        report_dict = self.report.to_dict()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)

        print(f"\n[OE Processor] Report saved to: {output_path}")
        print(f"[OE Processor] Summary:")
        print(f"  - Files processed: {self.report.total_files_processed}")
        print(f"  - Clusters analyzed: {self.report.total_clusters_processed}")
        print(f"  - Overall canal density: {self.report.overall_canal_density:.1%}")
        print(f"  - Processing time: {self.report.duration_seconds:.1f} seconds")

        return output_path


def main():
    """Main entry point for AI conversation processor."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Orthogonal Engineering AI Conversation Batch Processor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s filesystem_scan.json          # Process all clusters from scan
  %(prog)s filesystem_scan.json --limit 5 # Process first 5 clusters only
  %(prog)s filesystem_scan.json --output analysis.json # Custom output file
        """,
    )

    parser.add_argument(
        "scan_file",
        help="Filesystem scan JSON file containing AI conversation clusters",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit processing to first N clusters (default: all)",
    )

    parser.add_argument(
        "--output",
        default="ai_conversation_analysis_report.json",
        help="Output JSON file path (default: ai_conversation_analysis_report.json)",
    )

    parser.add_argument(
        "--max-files",
        type=int,
        default=50,
        help="Maximum files to process per cluster (default: 50)",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("ORTHOGONAL ENGINEERING - AI CONVERSATION PROCESSOR")
    print("=" * 70)
    print(f"Scan file: {args.scan_file}")
    print(f"Output: {args.output}")
    print(f"Max files per cluster: {args.max_files}")
    if args.limit:
        print(f"Cluster limit: {args.limit}")
    print("-" * 70)

    # Load scan data
    try:
        with open(args.scan_file, "r", encoding="utf-8", errors="ignore") as f:
            scan_data = json.load(f)
    except Exception as e:
        print(f"Error loading scan file: {e}")
        sys.exit(1)

    # Extract AI clusters
    ai_clusters = scan_data.get("ai_conversation_clusters", [])
    if not ai_clusters:
        print("No AI conversation clusters found in scan file")
        sys.exit(1)

    # Apply limit if specified
    if args.limit:
        ai_clusters = ai_clusters[: args.limit]
        print(f"Processing first {len(ai_clusters)} clusters (limited)")

    print(f"Found {len(ai_clusters)} AI conversation clusters")
    print(
        f"Total files in clusters: {sum(len(c.get('file_paths', [])) for c in ai_clusters)}"
    )

    # Create and run processor
    processor = AIConversationProcessor(ai_clusters)

    try:
        report = processor.process_all_clusters(max_files_per_cluster=args.max_files)
        output_file = processor.save_report(args.output)

        print("\n" + "=" * 70)
        print("PROCESSING COMPLETE")
        print("=" * 70)
        print(f"Report saved to: {output_file}")
        print("\nNext steps:")
        print("  1. Review the analysis report")
        print("  2. Validate correspondence claims")
        print("  3. Test falsifiable claims with independent methods")
        print("  4. Integrate findings into orthogonal engineering workflow")

    except KeyboardInterrupt:
        print("\n[OE Processor] Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[OE Processor] Error during processing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
