#!/usr/bin/env python3
"""
INELASTICITY CHECKER - PHASE 2 TRUTH INELASTICITY VALIDATION

Purpose: Validate truth inelasticity claims for grounding models G₁-G₅.
Truth inelasticity measures how resistant a truth claim is to reinterpretation
or evasion when confronted with contradictory evidence.

Methodological Principle: Steel without coercion. Test claims rigorously
without forcing acceptance or rejection.

Author: Orthogonal Engineering System
Date: 2026-01-20
Version: 1.0.0
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


class InelasticityChecker:
    """Check truth inelasticity for grounding models."""

    def __init__(self):
        self.grounding_models = {
            "G1": "Brute Fact",
            "G2": "Infinite Regress",
            "G3": "Coherentism",
            "G4": "Platonism",
            "G5": "Logos",
        }

        self.inelasticity_criteria = {
            "specificity": "Specificity of claims (0-3)",
            "falsifiability": "Clear falsification conditions (0-3)",
            "predictive_power": "Testable predictions (0-2)",
            "operational_consequences": "Real-world implications (0-2)",
            "methodological_risk": "Risk of being wrong (0-2)",
            "explanatory_scope": "Scope of explanation (0-2)",
            "historical_engagement": "Engagement with historical data (0-2)",
            "internal_consistency": "Internal logical consistency (0-2)",
            "evasion_resistance": "Resistance to reinterpretation (0-2)",
        }

        self.max_score = 20  # Sum of all criteria max values

    def load_grounding_model(self, model_id: str) -> Dict[str, Any]:
        """Load grounding model data from file."""
        model_file = f"../grounding_models/test_{model_id.lower().replace(' ', '_')}.md"

        try:
            with open(model_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse model data (simplified parsing)
            model_data = {
                "id": model_id,
                "name": self.grounding_models[model_id],
                "content": content,
                "file_path": model_file,
            }

            return model_data

        except FileNotFoundError:
            print(f"Warning: Model file not found: {model_file}")
            return {
                "id": model_id,
                "name": self.grounding_models[model_id],
                "content": "",
                "file_path": model_file,
            }

    def evaluate_inelasticity(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate truth inelasticity for a grounding model."""
        model_id = model_data["id"]
        model_name = model_data["name"]
        content = model_data["content"].lower()

        scores = {}

        # 1. Specificity of claims (0-3)
        specificity_keywords = ["specific", "precise", "exact", "defined", "clear"]
        specificity_count = sum(1 for word in specificity_keywords if word in content)
        scores["specificity"] = min(3, specificity_count)

        # 2. Falsifiability (0-3)
        falsifiability_keywords = [
            "falsif",
            "testable",
            "refutable",
            "disprovable",
            "verifiable",
        ]
        falsifiability_count = sum(
            1 for word in falsifiability_keywords if word in content
        )
        scores["falsifiability"] = min(3, falsifiability_count)

        # 3. Predictive power (0-2)
        predictive_keywords = [
            "predict",
            "expect",
            "forecast",
            "anticipate",
            "projection",
        ]
        predictive_count = sum(1 for word in predictive_keywords if word in content)
        scores["predictive_power"] = min(2, predictive_count)

        # 4. Operational consequences (0-2)
        operational_keywords = [
            "consequence",
            "implication",
            "effect",
            "result",
            "outcome",
            "impact",
        ]
        operational_count = sum(1 for word in operational_keywords if word in content)
        scores["operational_consequences"] = min(2, operational_count)

        # 5. Methodological risk (0-2)
        # Higher risk = more inelastic (willing to be wrong)
        risk_keywords = ["risk", "could be wrong", "falsifiable", "test", "challenge"]
        risk_count = sum(1 for word in risk_keywords if word in content)
        scores["methodological_risk"] = min(2, risk_count)

        # 6. Explanatory scope (0-2)
        scope_keywords = [
            "explain",
            "account for",
            "comprehensive",
            "complete",
            "total",
        ]
        scope_count = sum(1 for word in scope_keywords if word in content)
        scores["explanatory_scope"] = min(2, scope_count)

        # 7. Historical engagement (0-2)
        historical_keywords = ["historical", "evidence", "data", "record", "document"]
        historical_count = sum(1 for word in historical_keywords if word in content)
        scores["historical_engagement"] = min(2, historical_count)

        # 8. Internal consistency (0-2)
        consistency_keywords = [
            "consistent",
            "coherent",
            "logical",
            "non-contradictory",
        ]
        inconsistency_keywords = ["contradict", "paradox", "inconsistent", "illogical"]
        consistency_count = sum(1 for word in consistency_keywords if word in content)
        inconsistency_count = sum(
            1 for word in inconsistency_keywords if word in content
        )
        scores["internal_consistency"] = min(
            2, max(0, consistency_count - inconsistency_count)
        )

        # 9. Evasion resistance (0-2)
        # Resistance to reinterpretation when faced with counter-evidence
        evasion_keywords = [
            "resistant",
            "firm",
            "fixed",
            "stable",
            "unchanging",
            "invariant",
        ]
        evasion_count = sum(1 for word in evasion_keywords if word in content)
        scores["evasion_resistance"] = min(2, evasion_count)

        # Calculate total score
        total_score = sum(scores.values())
        normalized_score = (total_score / self.max_score) * 10  # Scale to 0-10

        return {
            "model_id": model_id,
            "model_name": model_name,
            "scores": scores,
            "total_raw": total_score,
            "total_normalized": round(normalized_score, 2),
            "max_possible": self.max_score,
        }

    def check_all_models(self) -> Dict[str, Any]:
        """Check inelasticity for all grounding models."""
        results = {}

        print("=" * 70)
        print("TRUTH INELASTICITY CHECK - GROUNDING MODELS G₁-G₅")
        print("=" * 70)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Criteria: {len(self.inelasticity_criteria)} categories")
        print(f"Maximum score: {self.max_score} (normalized to 0-10 scale)")
        print()

        for model_id in self.grounding_models.keys():
            print(f"Checking {model_id}: {self.grounding_models[model_id]}...")

            model_data = self.load_grounding_model(model_id)
            evaluation = self.evaluate_inelasticity(model_data)
            results[model_id] = evaluation

            # Print results
            print(f"  Total score: {evaluation['total_raw']}/{self.max_score}")
            print(f"  Normalized: {evaluation['total_normalized']}/10")

            # Show top 3 strengths
            sorted_scores = sorted(
                evaluation["scores"].items(), key=lambda x: x[1], reverse=True
            )
            print(
                f"  Top strengths: {', '.join([f'{k}:{v}' for k, v in sorted_scores[:3]])}"
            )
            print()

        # Calculate rankings
        ranked_models = sorted(
            results.items(), key=lambda x: x[1]["total_normalized"], reverse=True
        )

        print("-" * 70)
        print("TRUTH INELASTICITY RANKINGS")
        print("-" * 70)

        for rank, (model_id, data) in enumerate(ranked_models, 1):
            print(f"{rank}. {model_id}: {data['model_name']}")
            print(
                f"   Score: {data['total_normalized']}/10 "
                f"({data['total_raw']}/{self.max_score})"
            )

        print()

        # Save results
        self.save_results(results, ranked_models)

        return {
            "results": results,
            "rankings": ranked_models,
            "check_date": datetime.now().isoformat(),
            "criteria": self.inelasticity_criteria,
        }

    def save_results(self, results: Dict[str, Any], rankings: List[Tuple]) -> None:
        """Save inelasticity check results to file."""
        output_dir = Path("inelasticity_results")
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"inelasticity_check_{timestamp}.json"

        output_data = {
            "metadata": {
                "check_date": datetime.now().isoformat(),
                "system": "Orthogonal Engineering Phase 2",
                "version": "1.0.0",
                "criteria": self.inelasticity_criteria,
                "max_score": self.max_score,
            },
            "results": results,
            "rankings": [
                {
                    "rank": rank,
                    "model_id": model_id,
                    "model_name": results[model_id]["model_name"],
                    "score": results[model_id]["total_normalized"],
                    "raw_score": results[model_id]["total_raw"],
                }
                for rank, (model_id, _) in enumerate(rankings, 1)
            ],
            "summary": {
                "highest_score": rankings[0][1]["total_normalized"] if rankings else 0,
                "lowest_score": rankings[-1][1]["total_normalized"] if rankings else 0,
                "average_score": sum(r[1]["total_normalized"] for r in rankings)
                / len(rankings)
                if rankings
                else 0,
                "model_count": len(results),
            },
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"Results saved to: {output_file}")

        # Also create a markdown summary
        md_file = output_dir / f"inelasticity_summary_{timestamp}.md"
        self.create_markdown_summary(output_data, md_file)

    def create_markdown_summary(self, data: Dict[str, Any], output_path: Path) -> None:
        """Create markdown summary of inelasticity check."""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# TRUTH INELASTICITY CHECK - PHASE 2 RESULTS\n\n")
            f.write(f"**Date:** {data['metadata']['check_date']}\n")
            f.write(f"**System:** {data['metadata']['system']}\n")
            f.write(f"**Version:** {data['metadata']['version']}\n\n")

            f.write("## SUMMARY\n\n")
            f.write(f"- **Models checked:** {data['summary']['model_count']}\n")
            f.write(f"- **Highest score:** {data['summary']['highest_score']}/10\n")
            f.write(f"- **Lowest score:** {data['summary']['lowest_score']}/10\n")
            f.write(
                f"- **Average score:** {data['summary']['average_score']:.2f}/10\n\n"
            )

            f.write("## RANKINGS\n\n")
            f.write("| Rank | Model | Score (0-10) | Raw Score |\n")
            f.write("|------|-------|-------------|-----------|\n")

            for ranking in data["rankings"]:
                f.write(
                    f"| {ranking['rank']} | {ranking['model_id']}: {ranking['model_name']} | "
                    f"{ranking['score']} | {ranking['raw_score']}/{data['metadata']['max_score']} |\n"
                )

            f.write("\n## CRITERIA\n\n")
            f.write("| Criterion | Description | Max Score |\n")
            f.write("|-----------|-------------|-----------|\n")

            for criterion, description in data["metadata"]["criteria"].items():
                # Extract max score from description
                import re

                match = re.search(r"\((\d+)-(\d+)\)", description)
                if match:
                    max_score = match.group(2)
                else:
                    max_score = "?"

                f.write(f"| {criterion} | {description} | {max_score} |\n")

            f.write("\n## DETAILED RESULTS\n\n")

            for model_id, result in data["results"].items():
                f.write(f"### {model_id}: {result['model_name']}\n\n")
                f.write(
                    f"- **Total score:** {result['total_normalized']}/10 "
                    f"({result['total_raw']}/{data['metadata']['max_score']})\n\n"
                )

                f.write("| Criterion | Score |\n")
                f.write("|-----------|-------|\n")

                for criterion, score in result["scores"].items():
                    f.write(f"| {criterion} | {score} |\n")

                f.write("\n")

            f.write("\n## METHODOLOGICAL NOTES\n\n")
            f.write(
                "1. **Truth inelasticity** measures resistance to reinterpretation when faced with contradictory evidence.\n"
            )
            f.write(
                "2. **Higher scores** indicate more specific, falsifiable, and operationally consequential claims.\n"
            )
            f.write(
                "3. **Methodological risk** is valued: willingness to be wrong increases inelasticity.\n"
            )
            f.write(
                "4. **Normalization:** Raw scores (0-20) normalized to 0-10 scale for comparison.\n"
            )
            f.write(
                "5. **Automated analysis** based on keyword detection; manual review recommended for precision.\n"
            )

        print(f"Markdown summary saved to: {output_path}")


def main():
    """Main function for command-line execution."""
    checker = InelasticityChecker()

    try:
        results = checker.check_all_models()

        print("=" * 70)
        print("INELASTICITY CHECK COMPLETE")
        print("=" * 70)

        # Print final summary
        highest = results["rankings"][0][1] if results["rankings"] else None
        if highest:
            print(
                f"Highest inelasticity: {highest['model_id']} ({highest['model_name']})"
            )
            print(f"Score: {highest['total_normalized']}/10")

        print("\nNext steps:")
        print("1. Review detailed results in inelasticity_results/ directory")
        print("2. Compare with Phase 4 historical correspondence results")
        print("3. Integrate into full audit workflow")

        return 0

    except Exception as e:
        print(f"Error during inelasticity check: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
