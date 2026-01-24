"""
Phase 9 Causal Analysis Script

Performs advanced causal analysis on Phase 9 evidence, generates analysis reports,
and integrates with the EvidenceStore for comprehensive methodological analysis.

Author: Orthogonal Engineering System
Date: 2026-01-22
Version: 1.0.0
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent / "toolkit"))

from toolkit.oe.advanced_evidence import AdvancedEvidenceStore
from toolkit.oe.causal_analyzer import CausalAnalyzer, AnalysisType


class Phase9CausalAnalysis:
    """
    Advanced causal analysis for Phase 9 evidence and methodology.

    Features:
    1. Comprehensive causal analysis across all evidence types
    2. Temporal pattern detection and analysis
    3. Confidence distribution analysis
    4. Phase crossover analysis
    5. Evidence density analysis
    6. Causal strength analysis
    7. Integration with EvidenceStore for causality logging
    8. Exit code 2 on analysis failures
    """

    def __init__(self, evidence_store_path: Optional[str] = None):
        """
        Initialize causal analysis.

        Args:
            evidence_store_path: Path to evidence store (default: logs/evidence)
        """
        self.evidence_store_path = evidence_store_path or "logs/evidence"
        self.evidence_store = AdvancedEvidenceStore(base_path=self.evidence_store_path)
        self.causal_analyzer = CausalAnalyzer(self.evidence_store)

        # Create analysis output directory
        self.analysis_output_path = Path("logs/analysis/phase9")
        self.analysis_output_path.mkdir(parents=True, exist_ok=True)

    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """
        Run comprehensive causal analysis.

        Returns:
            Comprehensive analysis results dictionary
        """
        print("=" * 70)
        print("PHASE 9 COMPREHENSIVE CAUSAL ANALYSIS")
        print("=" * 70)

        analysis_start = datetime.now()

        # Run all analysis types
        analysis_results = {}

        # 1. Temporal Pattern Analysis
        print("\n[1/6] Analyzing temporal patterns...")
        try:
            temporal_patterns = self.causal_analyzer.analyze_temporal_patterns(
                time_window_hours=24.0
            )
            analysis_results["temporal_patterns"] = {
                "patterns_found": len(temporal_patterns),
                "patterns": [
                    {
                        "pattern_id": p.pattern_id,
                        "pattern_type": p.pattern_type,
                        "nodes_involved": p.nodes_involved,
                        "confidence": p.confidence,
                    }
                    for p in temporal_patterns
                ]
                if temporal_patterns
                else [],
                "status": "completed",
            }
            print(f"  ✓ Found {len(temporal_patterns)} temporal patterns")
        except Exception as e:
            analysis_results["temporal_patterns"] = {
                "error": str(e),
                "status": "failed",
            }
            print(f"  ✗ Temporal pattern analysis failed: {str(e)}")

        # 2. Confidence Distribution Analysis
        print("\n[2/6] Analyzing confidence distribution...")
        try:
            confidence_distribution = (
                self.causal_analyzer.analyze_confidence_distribution()
            )
            analysis_results["confidence_distribution"] = {
                "node_distribution": confidence_distribution.get(
                    "node_confidence_distribution", {}
                ),
                "edge_stats": confidence_distribution.get("edge_confidence_stats", {}),
                "chain_stats": confidence_distribution.get("chain_confidence_stats", {}),
                "status": "completed",
            }
            print("  ✓ Confidence distribution analysis completed")
        except Exception as e:
            analysis_results["confidence_distribution"] = {
                "error": str(e),
                "status": "failed",
            }
            print(f"  ✗ Confidence distribution analysis failed: {str(e)}")

        # 3. Phase Crossover Analysis
        print("\n[3/6] Analyzing phase crossover...")
        try:
            phase_crossover = self.causal_analyzer.analyze_phase_crossover()
            analysis_results["phase_crossover"] = {
                "analyses_found": len(phase_crossover),
                "analyses": [
                    {
                        "phase_a": a.phase_a,
                        "phase_b": a.phase_b,
                        "crossover_count": a.crossover_count,
                        "average_confidence": a.average_confidence,
                        "dominant_link_type": a.dominant_link_type.value,
                    }
                    for a in phase_crossover
                ]
                if phase_crossover
                else [],
                "status": "completed",
            }
            print(f"  ✓ Found {len(phase_crossover)} phase crossover analyses")
        except Exception as e:
            analysis_results["phase_crossover"] = {
                "error": str(e),
                "status": "failed",
            }
            print(f"  ✗ Phase crossover analysis failed: {str(e)}")

        # 4. Evidence Density Analysis
        print("\n[4/6] Analyzing evidence density...")
        try:
            evidence_density = self.causal_analyzer.analyze_evidence_density(
                time_resolution="day"
            )
            analysis_results["evidence_density"] = {
                "time_resolution": evidence_density.get("time_resolution", "day"),
                "periods_analyzed": len(evidence_density.get("periods", [])),
                "total_evidence": evidence_density.get("statistics", {}).get(
                    "total_evidence", 0
                ),
                "density_trend": evidence_density.get("density_trend", "unknown"),
                "status": "completed",
            }
            print("  ✓ Evidence density analysis completed")
        except Exception as e:
            analysis_results["evidence_density"] = {
                "error": str(e),
                "status": "failed",
            }
            print(f"  ✗ Evidence density analysis failed: {str(e)}")

        # 5. Causal Strength Analysis
        print("\n[5/6] Analyzing causal strength...")
        try:
            causal_strength = self.causal_analyzer.analyze_causal_strength()
            analysis_results["causal_strength"] = {
                "chains_analyzed": len(causal_strength),
                "analyses": [
                    {
                        "chain_id": a.chain_id,
                        "average_edge_confidence": a.average_edge_confidence,
                        "chain_coherence": a.chain_coherence,
                    }
                    for a in causal_strength
                ]
                if causal_strength
                else [],
                "status": "completed",
            }
            print(f"  ✓ Analyzed causal strength for {len(causal_strength)} chains")
        except Exception as e:
            analysis_results["causal_strength"] = {
                "error": str(e),
                "status": "failed",
            }
            print(f"  ✗ Causal strength analysis failed: {str(e)}")

        # 6. Chain Completeness Analysis
        print("\n[6/6] Analyzing chain completeness...")
        try:
            chain_completeness = self._analyze_chain_completeness()
            analysis_results["chain_completeness"] = chain_completeness
            print("  ✓ Chain completeness analysis completed")
        except Exception as e:
            analysis_results["chain_completeness"] = {
                "error": str(e),
                "status": "failed",
            }
            print(f"  ✗ Chain completeness analysis failed: {str(e)}")

        # Calculate overall analysis statistics
        analysis_end = datetime.now()
        analysis_duration = (analysis_end - analysis_start).total_seconds()

        successful_analyses = sum(
            1
            for result in analysis_results.values()
            if isinstance(result, dict) and result.get("status") == "completed"
        )
        total_analyses = len(analysis_results)

        overall_results = {
            "analysis_timestamp": analysis_start.isoformat(),
            "analysis_duration_seconds": analysis_duration,
            "total_analyses": total_analyses,
            "successful_analyses": successful_analyses,
            "failed_analyses": total_analyses - successful_analyses,
            "evidence_store_stats": {
                "causal_nodes": len(self.evidence_store.causal_graph),
                "causal_edges": len(self.evidence_store.causal_edges),
                "evidence_chains": len(self.evidence_store.evidence_chains),
            },
            "detailed_results": analysis_results,
        }

        # Save analysis results
        self._save_analysis_results(overall_results)

        # Log analysis completion
        self.evidence_store.log_causality(
            action="phase9_causal_analysis",
            cause="Comprehensive causal analysis requested",
            effect=f"Causal analysis completed with {successful_analyses}/{total_analyses} successful analyses",
            confidence="high",
            metadata={
                "analysis_duration_seconds": analysis_duration,
                "successful_analyses": successful_analyses,
                "total_analyses": total_analyses,
                "evidence_nodes": len(self.evidence_store.causal_graph),
                "evidence_edges": len(self.evidence_store.causal_edges),
            },
        )

        # Print summary
        self._print_analysis_summary(overall_results)

        return overall_results

    def _analyze_chain_completeness(self) -> Dict[str, Any]:
        """
        Analyze completeness of evidence chains.

        Returns:
            Chain completeness analysis results
        """
        chains = list(self.evidence_store.evidence_chains.values())

        if not chains:
            return {
                "total_chains": 0,
                "complete_chains": 0,
                "incomplete_chains": 0,
                "completion_rate": 0.0,
                "status": "completed",
            }

        complete_chains = sum(1 for chain in chains if chain.is_complete)
        incomplete_chains = len(chains) - complete_chains
        completion_rate = complete_chains / len(chains) if chains else 0.0

        # Analyze chain lengths
        chain_lengths = [len(chain.nodes) for chain in chains]
        avg_chain_length = sum(chain_lengths) / len(chain_lengths) if chain_lengths else 0

        return {
            "total_chains": len(chains),
            "complete_chains": complete_chains,
            "incomplete_chains": incomplete_chains,
            "completion_rate": completion_rate,
            "average_chain_length": avg_chain_length,
            "min_chain_length": min(chain_lengths) if chain_lengths else 0,
            "max_chain_length": max(chain_lengths) if chain_lengths else 0,
            "status": "completed",
        }

    def _save_analysis_results(self, results: Dict[str, Any]) -> None:
        """
        Save analysis results to file.

        Args:
            results: Analysis results dictionary
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.analysis_output_path / f"causal_analysis_{timestamp}.json"

        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\nAnalysis results saved to: {output_file}")

        # Also save a latest copy
        latest_file = self.analysis_output_path / "latest_causal_analysis.json"
        with open(latest_file, "w") as f:
            json.dump(results, f, indent=2)

    def _print_analysis_summary(self, results: Dict[str, Any]) -> None:
        """
        Print analysis summary to console.

        Args:
            results: Analysis results dictionary
        """
        print("\n" + "=" * 70)
        print("CAUSAL ANALYSIS SUMMARY")
        print("=" * 70)
        print(f"Analysis Timestamp: {results['analysis_timestamp']}")
        print(f"Analysis Duration: {results['analysis_duration_seconds']:.2f} seconds")
        print(f"Total Analyses: {results['total_analyses']}")
        print(f"Successful Analyses: {results['successful_analyses']}")
        print(f"Failed Analyses: {results['failed_analyses']}")
        print(f"Success Rate: {(results['successful_analyses']/results['total_analyses']*100):.1f}%")

        print("\nEvidence Store Statistics:")
        stats = results["evidence_store_stats"]
        print(f"  Causal Nodes: {stats['causal_nodes']}")
        print(f"  Causal Edges: {stats['causal_edges']}")
        print(f"  Evidence Chains: {stats['evidence_chains']}")

        print("\nDetailed Results:")
        for analysis_name, analysis_result in results["detailed_results"].items():
            status = analysis_result.get("status", "unknown")
            status_symbol = "✓" if status == "completed" else "✗"
            print(f"  {status_symbol} {analysis_name.replace('_', ' ').title()}: {status}")

        print("=" * 70)

    def analyze_specific_type(self, analysis_type: str, **kwargs) -> Dict[str, Any]:
        """
        Run specific type of analysis.

        Args:
            analysis_type: Type of analysis to run
            **kwargs: Additional arguments for the analysis

        Returns:
            Analysis results
        """
        analysis_type_enum = AnalysisType(analysis_type)

        try:
            if analysis_type_enum == AnalysisType.TEMPORAL_PATTERNS:
                time_window = kwargs.get("time_window_hours", 24.0)
                results = self.causal_analyzer.analyze_temporal_patterns(time_window)
                return {"analysis_type": "temporal_patterns", "results": results}

            elif analysis_type_enum == AnalysisType.CONFIDENCE_DISTRIBUTION:
                results = self.causal_analyzer.analyze_confidence_distribution()
                return {"analysis_type": "confidence_distribution", "results": results}

            elif analysis_type_enum == AnalysisType.PHASE_CROSSOVER:
                results = self.causal_analyzer.analyze_phase_crossover()
                return {"analysis_type": "phase_crossover", "results": results}

            elif analysis_type_enum == AnalysisType.EVIDENCE_DENSITY:
                time_resolution = kwargs.get("time_resolution", "day")
                results = self.causal_analyzer.analyze_evidence_density(time_resolution)
                return {"analysis_type": "evidence_density", "results": results}

            elif analysis_type_enum == AnalysisType.CAUSAL_STRENGTH:
                results = self.causal_analyzer.analyze_causal_strength()
                return {"analysis_type": "causal_strength", "results": results}

            elif analysis_type_enum == AnalysisType.CHAIN_COMPLETENESS:
                results = self._analyze_chain_completeness()
                return {"analysis_type": "chain_completeness", "results": results}

            else:
                raise ValueError(f"Unsupported analysis type: {analysis_type}")

        except Exception as e:
            return {
                "analysis_type": analysis_type,
                "error": str(e),
                "status": "failed",
            }


def main():
    """Main entry point for Phase 9 Causal Analysis."""
    parser = argparse.ArgumentParser(
        description="Phase 9 Causal Analysis - Advanced causal analysis for Phase 9 evidence"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Comprehensive analysis command
    comprehensive_parser = subparsers.add_parser(
        "comprehensive", help="Run comprehensive causal analysis"
    )
    comprehensive_parser.add_argument(
        "--evidence-store",
        default="logs/evidence",
        help="Path to evidence store",
    )
    comprehensive_parser.add_argument(
        "--output",
        help="Output file path (default: logs/analysis/phase9/causal_analysis_<timestamp>.json)",
    )

    # Specific analysis command
    specific_parser = subparsers.add_parser(
        "specific", help="Run specific type of analysis"
    )
    specific_parser.add_argument(
        "analysis_type",
        choices=[at.value for at in AnalysisType],
        help="Type of analysis to run",
    )
    specific_parser.add_argument(
        "--evidence-store",
        default="logs/evidence",
        help="Path to evidence store",
    )
    specific_parser.add_argument(
        "--time-window-hours",
        type=float,
        default=24.0,
        help="Time window for temporal pattern analysis (hours)",
    )
    specific_parser.add_argument(
        "--time-resolution",
        choices=["hour", "day", "week"],
        default="day",
        help="Time resolution for evidence density analysis",
    )
    specific_parser.add_argument(
        "--output",
        help="Output file path",
    )

    # Report command
    report_parser = subparsers.add_parser("report", help="Generate analysis report")
    report_parser.add_argument(
        "input_file",
        help="Input analysis results file",
    )
    report_parser.add_argument(
        "--format",
        choices=["json", "text", "summary"],
        default="summary",
        help="Report format",
    )
    report_parser.add_argument(
        "--output",
        help="Output file path (default: print to console)",
    )

    args = parser.parse_args()

    try:
        if args.command == "comprehensive":
            analyzer = Phase9CausalAnalysis(
                evidence_store_path=args.evidence_store
            )
            results = analyzer.run_comprehensive_analysis()

            if args.output:
                output_path = Path(args.output)
                with open(output_path, "w") as f:
                    json.dump(results, f, indent=2)
                print(f"\nResults also saved to: {output_path}")

            # Exit with code 0 if all analyses successful
            successful = results["successful_analyses"]
            total = results["total_analyses"]
            sys.exit(0 if successful == total else 1)

        elif args.command == "specific":
            analyzer = Phase9CausalAnalysis(
                evidence_store_path=args.evidence_store
            )

            kwargs = {}
            if args.analysis_type == "temporal_patterns":
                kwargs["time_window_hours"] = args.time_window_hours
            elif args.analysis_type == "evidence_density":
                kwargs["time_resolution"] = args.time_resolution

            results = analyzer.analyze_specific_type(args.analysis_type,
