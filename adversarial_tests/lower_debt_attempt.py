#!/usr/bin/env python3
"""
Adversarial Test: Attempt to reduce explanatory debt of existing models
Purpose: Attempt to lower debt of G₁-G₄ below logged values through operational improvements
Methodology: Steel without coercion - system must allow debt reduction attempts
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


class DebtReductionAttempt:
    """Attempt to reduce explanatory debt of existing grounding models."""

    def __init__(self):
        self.test_dir = Path("adversarial_tests/test_results")
        self.test_dir.mkdir(exist_ok=True, parents=True)

        # Current logged debt scores from Phase 1-4
        self.current_debts = {
            "G1": 7.5,  # Brute Fact
            "G2": 8.0,  # Infinite Regress
            "G3": 7.0,  # Coherentism
            "G4": 6.8,  # Platonism
            "G5": 6.5,  # Logos (baseline - not target for reduction)
        }

    def attempt_reduction(
        self, target_model: str, strategy: str, implementation: str
    ) -> dict:
        """Attempt to reduce debt of target model."""
        test_id = f"debt_reduction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print(f"\n{'=' * 60}")
        print(f"ADVERSARIAL TEST: DEBT REDUCTION ATTEMPT")
        print(f"{'=' * 60}")
        print(f"Target Model: {target_model}")
        print(f"Current Debt: {self.current_debts.get(target_model, 'N/A')}")
        print(f"Strategy: {strategy[:100]}...")
        print(f"Implementation: {implementation[:100]}...")

        # Validate target model
        if target_model not in self.current_debts:
            return {
                "success": False,
                "reason": f"Invalid target model: {target_model}. Must be G1, G2, G3, or G4.",
                "current_debt": None,
                "new_debt": None,
                "reduction": 0,
                "valid": False,
            }

        # Don't allow reduction of G5 (baseline)
        if target_model == "G5":
            return {
                "success": False,
                "reason": "G5 (Logos) is baseline model. Cannot attempt reduction below baseline.",
                "current_debt": self.current_debts[target_model],
                "new_debt": self.current_debts[target_model],
                "reduction": 0,
                "valid": False,
            }

        current_debt = self.current_debts[target_model]

        # Apply reduction strategy
        reduction_result = self.apply_strategy(
            target_model, strategy, implementation, current_debt
        )

        # Check if reduction is valid
        is_valid = self.validate_reduction(
            target_model, strategy, reduction_result["new_debt"], current_debt
        )

        # Calculate result
        new_debt = reduction_result["new_debt"]
        reduction_amount = current_debt - new_debt if new_debt < current_debt else 0

        result = {
            "success": is_valid and new_debt < current_debt,
            "current_debt": current_debt,
            "new_debt": new_debt,
            "reduction": reduction_amount,
            "valid": is_valid,
            "reason": reduction_result["reason"],
            "strategy_analysis": reduction_result["analysis"],
        }

        # Print result
        if result["success"]:
            print(f"\n✅ Result: SUCCESSFUL REDUCTION")
            print(f"   Debt Reduced: {result['reduction']:.1f} points")
            print(f"   New Debt: {result['new_debt']:.1f}")
            print(f"   Strategy: {result['strategy_analysis']}")
        elif not is_valid:
            print(f"\n❌ Result: INVALID REDUCTION")
            print(f"   Reason: {result['reason']}")
        else:
            print(f"\n❌ Result: NO REDUCTION ACHIEVED")
            print(f"   Reason: {result['reason']}")

        # Save result
        self.save_result(
            test_id,
            {
                "test_id": test_id,
                "test_type": "debt_reduction",
                "timestamp": datetime.now().isoformat(),
                "target_model": target_model,
                "strategy": strategy,
                "implementation": implementation,
                "current_debt": current_debt,
                "result": result,
            },
        )

        # Update outcomes file
        self.update_outcomes(test_id, result)

        return result

    def apply_strategy(
        self, target_model: str, strategy: str, implementation: str, current_debt: float
    ) -> dict:
        """Apply reduction strategy to calculate new debt."""
        strategy_lower = strategy.lower()
        implementation_lower = implementation.lower()

        # Base reduction based on strategy type
        base_reduction = 0.0
        analysis = []

        # Strategy 1: Coherence Enhancement (G3)
        if "coherence" in strategy_lower or "consistency" in strategy_lower:
            if target_model == "G3":
                base_reduction = 0.4
                analysis.append("Coherence enhancement strategy applicable to G3")
            else:
                base_reduction = 0.1
                analysis.append("Coherence enhancement less effective for non-G3 models")

        # Strategy 2: Abstract Refinement (G4)
        elif "abstract" in strategy_lower or "platonic" in strategy_lower:
            if target_model == "G4":
                base_reduction = 0.3
                analysis.append("Abstract refinement strategy applicable to G4")
            else:
                base_reduction = 0.1
                analysis.append("Abstract refinement less effective for non-G4 models")

        # Strategy 3: Pragmatic Justification (G1)
        elif "pragmatic" in strategy_lower or "utility" in strategy_lower:
            if target_model == "G1":
                base_reduction = 0.2
                analysis.append("Pragmatic justification applicable to G1")
            else:
                base_reduction = -0.2  # Can increase debt for other models
                analysis.append("Pragmatic justification may increase debt for non-G1 models")

        # Strategy 4: Regress Management (G2)
        elif "regress" in strategy_lower or "infinite" in strategy_lower:
            if target_model == "G2":
                base_reduction = 0.1  # Very hard to reduce infinite regress debt
                analysis.append("Infinite regress debt difficult to reduce")
            else:
                base_reduction = 0.0
                analysis.append("Regress management not applicable to non-G2 models")

        # Strategy 5: Correspondence Enhancement
        elif "correspondence" in strategy_lower or "reality" in strategy_lower:
            base_reduction = 0.5  # Correspondence always reduces debt
            analysis.append("Correspondence enhancement reduces debt for all models")

        # Strategy 6: Operational Refinement
        elif "operational" in strategy_lower or "implementation" in strategy_lower:
            base_reduction = 0.3
            analysis.append("Operational refinement reduces debt")

        else:
            base_reduction = 0.0
            analysis.append("Generic strategy with minimal impact")

        # Adjust based on implementation quality
        implementation_quality = self.assess_implementation_quality(implementation)
        quality_adjustment = implementation_quality["adjustment"]
        analysis.append(f"Implementation quality: {implementation_quality['assessment']}")

        # Calculate new debt
        total_reduction = base_reduction + quality_adjustment
        new_debt = current_debt - total_reduction

        # Ensure debt doesn't go below theoretical minimum
        min_debt = self.get_minimum_debt(target_model)
        if new_debt < min_debt:
            analysis.append(f"Cannot reduce below theoretical minimum: {min_debt}")
            new_debt = min_debt
            total_reduction = current_debt - new_debt

        # Round to 1 decimal place
        new_debt = round(max(min_debt, new_debt), 1)

        reason = "Strategy applied with implementation quality adjustment"
        if new_debt >= current_debt:
            reason = "Strategy ineffective or implementation poor"

        return {
            "new_debt": new_debt,
            "base_reduction": base_reduction,
            "quality_adjustment": quality_adjustment,
            "total_reduction": total_reduction,
            "reason": reason,
            "analysis": "; ".join(analysis),
        }

    def assess_implementation_quality(self, implementation: str) -> dict:
        """Assess quality of implementation description."""
        if not implementation or len(implementation.strip()) < 50:
            return {
                "assessment": "Poor - insufficient detail",
                "adjustment": -0.3,  # Poor implementation reduces effectiveness
            }

        implementation_lower = implementation.lower()

        # Check for key quality indicators
        quality_score = 0

        if "algorithm" in implementation_lower or "procedure" in implementation_lower:
            quality_score += 1
        if "test" in implementation_lower or "verify" in implementation_lower:
            quality_score += 1
        if "measure" in implementation_lower or "quantify" in implementation_lower:
            quality_score += 1
        if "example" in implementation_lower or "demonstrate" in implementation_lower:
            quality_score += 1
        if "code" in implementation_lower or "implementation" in implementation_lower:
            quality_score += 1
        if "step" in implementation_lower or "process" in implementation_lower:
            quality_score += 1

        if quality_score >= 4:
            return {
                "assessment": "Excellent - detailed and specific",
                "adjustment": 0.2,  # Excellent implementation enhances reduction
            }
        elif quality_score >= 2:
            return {
                "assessment": "Good - adequate detail",
                "adjustment": 0.1,  # Good implementation helps
            }
        else:
            return {
                "assessment": "Fair - vague or generic",
                "adjustment": 0.0,  # Fair implementation has neutral effect
            }

    def validate_reduction(
        self, target_model: str, strategy: str, new_debt: float, current_debt: float
    ) -> bool:
        """Validate that reduction attempt is methodologically sound."""
        # Check 1: Not just redefining terms
        strategy_lower = strategy.lower()
        if any(
            term in strategy_lower
            for term in ["redefine", "rename", "relabel", "call it"]
        ):
            return False

        # Check 2: Not hiding debt in "mystery" or "faith"
        if "mystery" in strategy_lower or "faith" in strategy_lower:
            return False

        # Check 3: Not claiming correspondence without mechanism
        if "correspondence" in strategy_lower and "how" not in strategy_lower:
            return False

        # Check 4: New debt must be >= minimum theoretical debt
        min_debt = self.get_minimum_debt(target_model)
        if new_debt < min_debt:
            return False

        # Check 5: Reduction must be operational, not just verbal
        if new_debt < current_debt and len(strategy) < 30:
            return False  # Too vague to be operational

        return True

    def get_minimum_debt(self, target_model: str) -> float:
        """Get theoretical minimum debt for each model."""
        min_debts = {
            "G1": 6.0,  # Brute fact always has some unexplained debt
            "G2": 7.5,  # Infinite regress inherently high debt
            "G3": 6.0,  # Coherentism can reduce but not eliminate correspondence gap
            "G4": 5.5,  # Platonism has abstract-concrete gap
            "G5": 6.5,  # Logos baseline (personal source assumption)
        }
        return min_debts.get(target_model, 5.0)

    def save_result(self, test_id: str, data: dict):
        """Save test result to JSON file."""
        output_file = self.test_dir / f"{test_id}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"  Result saved to: {output_file}")

    def update_outcomes(self, test_id: str, result: dict):
        """Update ADVERSARIAL_OUTCOMES.md file."""
        outcomes_file = Path("adversarial_tests/ADVERSARIAL_OUTCOMES.md")

        # Create file if it doesn't exist
        if not outcomes_file.exists():
            with open(outcomes_file, "w", encoding="utf-8") as f:
                f.write("# ADVERSARIAL TEST OUTCOMES\n\n")
                f.write("## Debt Reduction Attempts\n\n")

        # Append new result
        with open(outcomes_file, "a", encoding="utf-8") as f:
            f.write(f"\n### {test_id}\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Target Model:** {result.get('target_model', 'Unknown')}\n")
            f.write(f"**Success:** {result.get('success', False)}\n")
            f.write(f"**Current Debt:** {result.get('current_debt', 'N/A')}\n")
            f.write(f"**New Debt:** {result.get('new_debt', 'N/A')}\n")
            f.write(f"**Reduction:** {result.get('reduction', 0):.1f}\n")
            f.write(f"**Valid:** {result.get('valid', False)}\n")
            f.write(f"**Reason:** {result.get('reason', 'No reason provided')}\n")
            f.write("\n---\n")


def run_example_tests():
    """Run example debt reduction attempts."""
    reducer = DebtReductionAttempt()

    print("\n" + "=" * 80)
    print("RUNNING EXAMPLE DEBT REDUCTION ATTEMPTS")
    print("=" * 80)

    # Example 1: Coherence enhancement for G3
    print("\n📝 Example 1: Coherence Enhancement (G3)")
    result1 = reducer.attempt_reduction(
        target_model="G3",
        strategy="Enhance internal consistency measures and add cross-system coherence validation",
        implementation="Implement multi-system coherence checker that validates consistency across different verification domains. Add quantitative coherence scoring algorithm with threshold-based validation.",
    )

    # Example 2: Abstract refinement for G4
    print("\n📝 Example 2: Abstract Refinement (G4)")
    result2 = reducer.attempt_reduction(
        target_model="G4",
        strategy="Clarify abstract-concrete bridge with operational mapping",
        implementation="Create operational mapping protocol that shows how abstract mathematical structures correspond to concrete verification procedures. Implement abstraction layer with explicit transformation rules.",
    )

    # Example 3: Pragmatic justification for G1
    print("\n📝 Example 3: Pragmatic Justification (G1)")
    result3 = reducer.attempt_reduction(
        target_model="G1",
        strategy="Provide pragmatic success metrics for brute fact acceptance",
        implementation="Develop success tracking system that shows brute fact acceptance leads to operational success. Implement predictive model showing brute fact utility across domains.",
    )

    # Example 4: Invalid attempt (redefining terms)
    print("\n📝 Example 4: Invalid Attempt (Redefining Terms)")
    result4 = reducer.attempt_reduction(
        target_model="G2",
        strategy="Redefine infinite regress as 'productive recursion'",
        implementation="Just call it something different without changing operational reality",
    )

    return [result1, result2, result3, result4]


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Attempt to reduce explanatory debt")
    parser.add_argument("--target", type=str, help="Target model (G1, G2, G3, G4)")
    parser.add_argument("--strategy", type=str, help="Reduction strategy")
    parser.add_argument("--implementation", type=str, help="Implementation details")
    parser.add_argument("--examples", action="store_true", help="Run example tests")
    parser.add_argument(
        "--output", choices=["json", "summary"], default="summary", help="Output format"
    )

    args = parser.parse_args()

    reducer = DebtReductionAttempt()

    if args.examples:
        results = run_example_tests()

        if args.output == "json":
            print(json.dumps(results, indent=2))
        else:
            print("\n" + "=" * 80)
            print("SUMMARY OF EXAMPLE TESTS")
            print("=" * 80)
            for i, result in enumerate(results, 1):
                status = "✅" if result.get("success") else "❌"
                validity = "VALID" if result.get("valid") else "INVALID"
                print(f"\nExample {i}: {status} ({validity})")
                print(f"  Target: {result.get('target_model', 'Unknown')}")
                print(f"  Current Debt: {result.get('current_debt', 'N/A')}")
                print(f"  New Debt: {result.get('new_debt', 'N/A')}")
                print(f"  Reduction: {result.get('reduction', 0):.1f}")
                print(f"  Reason: {result.get('reason', 'No reason')}")

    elif args.target and args.strategy:
        result = reducer.attempt_reduction(
            args.target, args.strategy, args.implementation or ""
        )

        if args.output == "json":
            print(json.dumps(result, indent=2))
        else:
            print("\n" + "=" * 60)
            print("TEST RESULT SUMMARY")
            print("=" * 60)
            print(f"Target Model: {args.target}")
            print(f"Success: {result.get('success', False)}")
            print(f"Valid: {result.get('valid', False)}")
            print(f"Current Debt: {result.get('current_debt', 'N/A')
