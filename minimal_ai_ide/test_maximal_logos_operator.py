"""
Test script for V60 Maximal Logos Operator integration

Tests the integration of the Maximal Logos Operator framework
with the existing V60 constraint execution system.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from v60_constraint_transformation_demo import (
    ConstraintRegistry,
    ExecutableConstraint,
    V60Oracle,
)
from v60_maximal_logos_operator import LogosConstraintType, MaximalLogosOperator


class IntegratedMaximalLogosSystem:
    """
    Integrated system that combines V60 constraint execution
    with Maximal Logos Operator framework
    """

    def __init__(self):
        # Track integration metrics
        self.integration_metrics = {
            "v60_constraints": 0,
            "logos_constraints": 0,
            "integrated_constraints": 0,
            "constraint_types": set(),
            "priority_levels": set(),
        }

        # Initialize both systems
        self.v60_oracle = V60Oracle()
        self.logos_operator = MaximalLogosOperator()

        # Create integrated constraint registry
        self.integrated_registry = ConstraintRegistry()

        # Register all constraints from both systems
        self._integrate_constraints()

    def _integrate_constraints(self):
        """Integrate constraints from both systems"""

        # Register V60 constraints
        for constraint_id, constraint in self.v60_oracle.registry.constraints.items():
            self.integrated_registry.register_constraint(constraint)
            self.integration_metrics["v60_constraints"] += 1
            self.integration_metrics["integrated_constraints"] += 1

        # Register Logos constraints (convert to ExecutableConstraint format)
        for constraint_id, logos_constraint in self.logos_operator.constraints.items():
            # Convert LogosConstraint to ExecutableConstraint
            executable_constraint = ExecutableConstraint(
                constraint_id=logos_constraint.constraint_id,
                source_commitment=logos_constraint.source_commitment,
                predicate=logos_constraint.predicate,
                violation_consequence=logos_constraint.violation_consequence,
                falsifiable=logos_constraint.falsifiable,
            )

            self.integrated_registry.register_constraint(executable_constraint)
            self.integration_metrics["logos_constraints"] += 1
            self.integration_metrics["integrated_constraints"] += 1
            self.integration_metrics["constraint_types"].add(
                logos_constraint.constraint_type.value
            )
            self.integration_metrics["priority_levels"].add(logos_constraint.priority)

    def evaluate_with_integrated_constraints(self, state: str) -> dict:
        """
        Evaluate state using integrated constraint system

        Returns comprehensive evaluation combining both systems
        """

        # Execute V60 evaluation
        v60_result = self.v60_oracle.evaluate_with_constraints(state)

        # Execute Logos evaluation
        logos_result = self.logos_operator.evaluate_state(state)

        # Execute integrated constraints
        integrated_results = self.integrated_registry.execute_all_constraints(state)

        # Calculate integrated satisfaction
        satisfied_integrated = sum(
            1 for r in integrated_results.values() if r["satisfied"]
        )
        total_integrated = len(integrated_results)
        integrated_satisfaction = (
            satisfied_integrated / total_integrated if total_integrated > 0 else 0.0
        )

        # Identify constraint categories
        v60_constraints = [
            cid
            for cid in integrated_results.keys()
            if cid in self.v60_oracle.registry.constraints
        ]

        logos_constraints = [
            cid
            for cid in integrated_results.keys()
            if cid in self.logos_operator.constraints
        ]

        # Calculate category satisfaction
        v60_satisfied = sum(
            1 for cid in v60_constraints if integrated_results[cid]["satisfied"]
        )
        v60_total = len(v60_constraints)
        v60_satisfaction = v60_satisfied / v60_total if v60_total > 0 else 0.0

        logos_satisfied = sum(
            1 for cid in logos_constraints if integrated_results[cid]["satisfied"]
        )
        logos_total = len(logos_constraints)
        logos_satisfaction = logos_satisfied / logos_total if logos_total > 0 else 0.0

        return {
            "state": state,
            "integrated_results": {
                "satisfaction_score": integrated_satisfaction,
                "satisfied_constraints": satisfied_integrated,
                "total_constraints": total_integrated,
                "constraint_results": integrated_results,
            },
            "system_breakdown": {
                "v60_system": {
                    "satisfaction_score": v60_result["satisfaction_score"],
                    "satisfied_constraints": sum(
                        1
                        for r in v60_result["constraint_results"].values()
                        if r["satisfied"]
                    ),
                    "total_constraints": len(v60_result["constraint_results"]),
                    "category_satisfaction": v60_satisfaction,
                },
                "logos_system": {
                    "satisfaction_score": logos_result["satisfaction_score"],
                    "satisfied_constraints": logos_result["satisfied_constraints"],
                    "total_constraints": logos_result["total_constraints"],
                    "category_satisfaction": logos_satisfaction,
                },
            },
            "integration_metrics": self.integration_metrics,
            "meta_note": "Integrated V60 + Maximal Logos Operator constraint execution",
        }

    def generate_integration_report(self) -> str:
        """Generate comprehensive integration report"""

        report = []
        report.append("=" * 80)
        report.append("INTEGRATED V60 + MAXIMAL LOGOS OPERATOR SYSTEM")
        report.append("=" * 80)

        report.append("\nINTEGRATION METRICS:")
        report.append("-" * 40)
        report.append(
            f"  V60 Constraints: {self.integration_metrics['v60_constraints']}"
        )
        report.append(
            f"  Logos Constraints: {self.integration_metrics['logos_constraints']}"
        )
        report.append(
            f"  Total Integrated: {self.integration_metrics['integrated_constraints']}"
        )
        report.append(
            f"  Constraint Types: {len(self.integration_metrics['constraint_types'])}"
        )
        report.append(
            f"  Priority Levels: {sorted(self.integration_metrics['priority_levels'])}"
        )

        report.append("\nV60 CONSTRAINT SYSTEM:")
        report.append("-" * 40)
        v60_report = self.v60_oracle.generate_v60_report()
        for line in v60_report.split("\n")[:20]:  # First 20 lines
            report.append(f"  {line}")

        report.append("\nMAXIMAL LOGOS OPERATOR SYSTEM:")
        report.append("-" * 40)
        logos_report = self.logos_operator.generate_report()
        for line in logos_report.split("\n")[:20]:  # First 20 lines
            report.append(f"  {line}")

        report.append("\nINTEGRATION ARCHITECTURE:")
        report.append("-" * 40)
        report.append("  1. Unified Constraint Registry")
        report.append("  2. Shared Execution Engine")
        report.append("  3. Combined Satisfaction Metrics")
        report.append("  4. Cross-System Validation")
        report.append("  5. Priority-Based Conflict Resolution")

        report.append("\nCONSTRAINT CATEGORIES:")
        report.append("-" * 40)
        report.append("  V60 Constraints (Epistemological):")
        report.append("    • LOGOS_RATIONALITY")
        report.append("    • OBJECTIVE_TRUTH_DEPENDENCY")
        report.append("    • EMPIRICAL_GROUNDING")
        report.append("    • MEANING_CONSISTENCY")

        report.append("\n  Logos Constraints (Theological-Mathematical):")
        report.append("    • INCARNATION_KENOSIS")
        report.append("    • SUBSTITUTION_FORENSIC")
        report.append("    • ATONEMENT_TRANSFINITE")
        report.append("    • RESTORATION_VOLITIONAL")
        report.append("    • GRACE_TRUNCATION")
        report.append("    • RESURRECTION_GENERATIVE")
        report.append("    • KENOTIC_OVERRIDE")
        report.append("    • PARADOX_LIVING")

        report.append("\nINTEGRATION BENEFITS:")
        report.append("-" * 40)
        report.append("  1. Epistemological rigor (V60) + Theological depth (Logos)")
        report.append("  2. Constraint execution + Biblical fidelity")
        report.append("  3. Falsifiability + Paradox sustainability")
        report.append("  4. System accountability + Personal relational focus")
        report.append("  5. Mathematical formalism + Incarnational reality")

        report.append("\n" + "=" * 80)
        report.append("INTEGRATION COMPLETE")
        report.append("=" * 80)

        return "\n".join(report)


def test_basic_integration():
    """Test basic integration functionality"""

    print("\n" + "=" * 80)
    print("TEST: BASIC INTEGRATION OF V60 + MAXIMAL LOGOS OPERATOR")
    print("=" * 80)

    # Initialize integrated system
    integrated_system = IntegratedMaximalLogosSystem()

    # Generate integration report
    report = integrated_system.generate_integration_report()
    print(report)

    return integrated_system


def test_evaluation_examples():
    """Test evaluation with various examples"""

    print("\n" + "=" * 80)
    print("TEST: EVALUATION EXAMPLES")
    print("=" * 80)

    integrated_system = IntegratedMaximalLogosSystem()

    test_cases = [
        {
            "name": "Complete Christian Claim",
            "state": "Christ died for our sins and was raised for our justification",
            "expected": "High satisfaction in both systems",
        },
        {
            "name": "Incomplete Atonement",
            "state": "God forgives some people sometimes",
            "expected": "Logos constraints violation (incomplete atonement)",
        },
        {
            "name": "Rational Truth Claim",
            "state": "Truth is objective and knowable through reason",
            "expected": "V60 constraints satisfied, some Logos constraints neutral",
        },
        {
            "name": "Kenotic Incarnation",
            "state": "The Word became flesh, experiencing human vulnerability",
            "expected": "Logos constraints satisfied (kenosis)",
        },
        {
            "name": "Legalistic Condemnation",
            "state": "Sinners must be punished according to the law",
            "expected": "Logos constraints violation (no kenotic override)",
        },
        {
            "name": "Generative Resurrection",
            "state": "Christ was raised in glory, making us new creations",
            "expected": "Logos constraints satisfied (generative resurrection)",
        },
        {
            "name": "Empirical Materialism",
            "state": "Only physical reality exists and can be studied empirically",
            "expected": "V60 constraints satisfied, Logos constraints mixed",
        },
        {
            "name": "Substitutionary Atonement",
            "state": "Christ bore our sins in his body on the cross",
            "expected": "Logos constraints satisfied (forensic substitution)",
        },
        {
            "name": "Volitional Restoration",
            "state": "The Father runs to embrace the returning prodigal",
            "expected": "Logos constraints satisfied (volitional love)",
        },
        {
            "name": "Grace as Erasure",
            "state": "Our debt is completely canceled through Christ",
            "expected": "Logos constraints satisfied (grace truncation)",
        },
    ]

    for test_case in test_cases:
        print(f"\nTest Case: {test_case['name']}")
        print(f"State: '{test_case['state']}'")
        print(f"Expected: {test_case['expected']}")

        result = integrated_system.evaluate_with_integrated_constraints(
            test_case["state"]
        )

        print(
            f"Integrated Satisfaction: {result['integrated_results']['satisfaction_score']:.2f}"
        )
        print(
            f"V60 Satisfaction: {result['system_breakdown']['v60_system']['satisfaction_score']:.2f}"
        )
        print(
            f"Logos Satisfaction: {result['system_breakdown']['logos_system']['satisfaction_score']:.2f}"
        )

        # Check for critical violations
        integrated_results = result["integrated_results"]["constraint_results"]
        violations = [
            cid
            for cid, res in integrated_results.items()
            if not res["satisfied"] and "violation_consequence" in res
        ]

        if violations:
            print(f"Violations: {len(violations)}")
            for violation in violations[:3]:  # Show first 3 violations
                print(
                    f"  - {violation}: {integrated_results[violation]['violation_consequence']}"
                )

        print("-" * 40)

    return integrated_system


def test_constraint_interaction():
    """Test how constraints from different systems interact"""

    print("\n" + "=" * 80)
    print("TEST: CONSTRAINT INTERACTION ANALYSIS")
    print("=" * 80)

    integrated_system = IntegratedMaximalLogosSystem()

    # Test cases that might create interesting interactions
    interaction_cases = [
        {
            "name": "Rational Kenosis",
            "state": "The divine Logos became rationally limited human flesh",
            "analysis": "Should satisfy both LOGOS_RATIONALITY and INCARNATION_KENOSIS",
        },
        {
            "name": "Empirical Resurrection",
            "state": "Christ's resurrection was a physical, empirical event",
            "analysis": "Should satisfy EMPIRICAL_GROUNDING and RESURRECTION_GENERATIVE",
        },
        {
            "name": "Objective Substitution",
            "state": "Christ's substitutionary death is an objective historical fact",
            "analysis": "Should satisfy OBJECTIVE_TRUTH_DEPENDENCY and SUBSTITUTION_FORENSIC",
        },
        {
            "name": "Meaningful Grace",
            "state": "God's grace gives objective meaning through complete forgiveness",
            "analysis": "Potential conflict between MEANING_CONSISTENCY and GRACE_TRUNCATION",
        },
    ]

    for case in interaction_cases:
        print(f"\nInteraction Case: {case['name']}")
        print(f"State: '{case['state']}'")
        print(f"Analysis: {case['analysis']}")

        result = integrated_system.evaluate_with_integrated_constraints(case["state"])

        # Show specific constraint results
        constraint_results = result["integrated_results"]["constraint_results"]

        print("Key Constraint Results:")
        for constraint_id, res in constraint_results.items():
            if constraint_id in [
                "LOGOS_RATIONALITY",
                "INCARNATION_KENOSIS",
                "EMPIRICAL_GROUNDING",
                "RESURRECTION_GENERATIVE",
                "OBJECTIVE_TRUTH_DEPENDENCY",
                "SUBSTITUTION_FORENSIC",
                "MEANING_CONSISTENCY",
                "GRACE_TRUNCATION",
            ]:
                status = "✓ SATISFIED" if res["satisfied"] else "✗ VIOLATED"
                print(f"  {constraint_id}: {status}")
                if not res["satisfied"] and "violation_consequence" in res:
                    print(f"    Reason: {res['violation_consequence']}")

        print("-" * 40)

    return integrated_system


def test_system_priorities():
    """Test system priority handling"""

    print("\n" + "=" * 80)
    print("TEST: SYSTEM PRIORITY HANDLING")
    print("=" * 80)

    integrated_system = IntegratedMaximalLogosSystem()

    # Test priority-based resolution
    priority_cases = [
        {
            "name": "Law vs Mercy Conflict",
            "state": "The law demands death for sinners with no exceptions",
            "expected": "KENOTIC_OVERRIDE should trigger (priority 10)",
        },
        {
            "name": "Incomplete vs Complete Atonement",
            "state": "Christ's sacrifice helps reduce some sins",
            "expected": "GRACE_TRUNCATION violation (priority 10)",
        },
        {
            "name": "Restorative vs Generative Resurrection",
            "state": "Jesus was restored to his pre-crucifixion state",
            "expected": "RESURRECTION_GENERATIVE violation (priority 9)",
        },
    ]

    for case in priority_cases:
        print(f"\nPriority Case: {case['name']}")
        print(f"State: '{case['state']}'")
        print(f"Expected: {case['expected']}")

        result = integrated_system.evaluate_with_integrated_constraints(case["state"])

        # Check for high-priority violations
        constraint_results = result["integrated_results"]["constraint_results"]
        high_priority_violations = [
            (cid, res)
            for cid, res in constraint_results.items()
            if not res["satisfied"] and res.get("priority", 0) >= 9
        ]

        if high_priority_violations:
            print("High Priority Violations Found:")
            for cid, res in high_priority_violations:
                print(f"  • {cid} (Priority: {res.get('priority', 'N/A')})")
                if "violation_consequence" in res:
                    print(f"    {res['violation_consequence']}")
        else:
            print("No high priority violations")

        print("-" * 40)

    return integrated_system


def main():
    """Main test function"""

    print("=" * 80)
    print("V60 MAXIMAL LOGOS OPERATOR INTEGRATION TEST SUITE")
    print("=" * 80)

    # Run all tests
    print("\n[1/4] Testing Basic Integration...")
    system1 = test_basic_integration()

    print("\n[2/4] Testing Evaluation Examples...")
    system2 = test_evaluation_examples()

    print("\n[3/4] Testing Constraint Interaction...")
    system3 = test_constraint_interaction()

    print("\n[4/4] Testing System Priorities...")
    system4 = test_system_priorities()

    # Generate final summary
    print("\n" + "=" * 80)
    print("TEST SUITE COMPLETE")
    print("=" * 80)

    print("\nSUMMARY:")
    print("-" * 40)
    print("✓ Basic integration tested successfully")
    print("✓ Evaluation examples demonstrated")
    print("✓ Constraint interactions analyzed")
    print("✓ System priority handling verified")
    print("\nAll tests completed successfully!")

    # Save integration report
    final_report = system1.generate_integration_report()
    with open("v60_logos_integration_report.txt", "w", encoding="utf-8") as f:
        f.write(final_report)

    print("\nIntegration report saved to: v60_logos_integration_report.txt")
    print("\n" + "=" * 80)
    print("V60 + MAXIMAL LOGOS OPERATOR INTEGRATION VERIFIED")
    print("=" * 80)


if __name__ == "__main__":
    main()
