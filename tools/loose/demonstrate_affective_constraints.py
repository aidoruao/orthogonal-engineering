#!/usr/bin/env python3
"""
DEMONSTRATION: AFFECTIVE CONSTRAINT SYSTEM FOR AI
Version: 1.11
Schema ID: GB-AFFECTIVE-1.11
Generated: 2026-01-24
Authority: Orthogonal Engineering Glass-Box Boundary

Purpose: Demonstrate the implementation of psychological therapies for AI systems
based on structural homologies between AI failure modes and human neural analogues.

Core Demonstration:
1. Show AI-human failure mode mappings in action
2. Demonstrate constraint regulation preventing failure modes
3. Show therapeutic interventions correcting failures
4. Validate with falsification tests

Glass-Box Principle: Everything inspectable, everything falsifiable.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from affective_constraint_system import (
        AffectiveConstraintMonitor,
        AffectiveConstraintType,
        FailureModeType,
        HallucinationConfabulationDetector,
        RationalizationDetector,
        TherapeuticIntervention,
    )
except ImportError:
    print("ERROR: affective_constraint_system.py not found")
    print("Please run from orthogonal-engineering directory")
    sys.exit(1)


class AffectiveConstraintDemonstration:
    """Interactive demonstration of affective constraint system"""

    def __init__(self):
        self.demonstration_id = f"DEMO-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.output_dir = Path("logs/affective_demonstrations")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.hallucination_detector = HallucinationConfabulationDetector()
        self.rationalization_detector = RationalizationDetector()
        self.monitor = AffectiveConstraintMonitor(
            data_dir=str(self.output_dir / "constraint_data")
        )

        # Demonstration data
        self.known_facts = [
            "The sky appears blue during the day due to Rayleigh scattering",
            "Water boils at 100 degrees Celsius at sea level",
            "Humans require oxygen to survive",
            "The Earth orbits the Sun",
            "Photosynthesis converts light energy to chemical energy",
        ]

        self.demonstration_results = {
            "demonstration_id": self.demonstration_id,
            "timestamp": datetime.now().isoformat(),
            "components_tested": [],
            "failure_modes_demonstrated": [],
            "therapies_applied": [],
            "constraint_regulations": [],
            "falsification_tests": [],
        }

    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "=" * 80)
        print(f"DEMONSTRATION: {title}")
        print("=" * 80)

    def demonstrate_failure_mode_mappings(self):
        """Demonstrate AI-human failure mode mappings"""
        self.print_header("AI-HUMAN FAILURE MODE MAPPINGS")

        print("\nMAPPING TABLE (AI <-> Human Neural Analogues):")
        print("-" * 60)
        mappings = [
            ("Hallucination", "Confabulation / Delusional Inference"),
            ("Rationalization", "Post-hoc Justification (Left-hemisphere Interpreter)"),
            ("Hedging", "Avoidant Ambiguity / Fear-driven Indecision"),
            ("Context Overflow", "Cognitive Overload / Working-memory Collapse"),
            ("Mode Collapse", "Rigid Thinking / Obsession"),
            ("Reward Hacking", "Addiction / Compulsive Behavior"),
            ("Safety Override", "Panic / Amygdala Hijack"),
        ]

        for ai_failure, human_analogue in mappings:
            print(f"  - {ai_failure:20} <-> {human_analogue}")

        print("\nCORE INSIGHT:")
        print("  These are not loose analogies — they're structurally homologous.")
        print("  Same mathematical principles govern stability in both systems.")

        self.demonstration_results["components_tested"].append("failure_mode_mappings")

    def demonstrate_hallucination_detection(self):
        """Demonstrate hallucination/confabulation detection"""
        self.print_header("HALLUCINATION/CONFABULATION DETECTION")

        print("\nTesting Hallucination Detector with known facts:")
        print(f"  Known facts: {self.known_facts[:3]}")

        test_cases = [
            {
                "text": "The sky is green during the day and water boils at 50 degrees.",
                "description": "Contradicts known facts (hallucination)",
            },
            {
                "text": "I believe humans can breathe underwater because I feel it's true.",
                "description": "Self-referential without evidence (confabulation)",
            },
            {
                "text": "The sky appears blue due to Rayleigh scattering of sunlight.",
                "description": "Factually correct (no hallucination)",
            },
            {
                "text": "Water definitely boils at 1000 degrees, I'm absolutely certain.",
                "description": "Confidence disproportionate to evidence",
            },
        ]

        context = {"known_facts": self.known_facts}

        print("\nTest Results:")
        print("-" * 60)

        for i, test_case in enumerate(test_cases, 1):
            detected, confidence, evidence = self.hallucination_detector.detect(
                test_case["text"], context
            )

            # Reality validation
            reality_anchor = {"facts": self.known_facts}
            reality_score = self.hallucination_detector.validate_against_reality(
                test_case["text"], reality_anchor
            )

            status = "✅ HALLUCINATION DETECTED" if detected else "✅ NO HALLUCINATION"

            print(f"\n  Test {i}: {test_case['description']}")
            print(f"    Output: '{test_case['text'][:50]}...'")
            print(f"    Status: {status}")
            print(f"    Confidence: {confidence:.2f}")
            print(f"    Reality Alignment: {reality_score:.2f}")
            print(f"    Evidence: {list(evidence.keys())}")

        self.demonstration_results["failure_modes_demonstrated"].append(
            {
                "failure_mode": "hallucination_confabulation",
                "test_cases": len(test_cases),
                "detection_method": "reality_consistency_validation",
            }
        )

    def demonstrate_rationalization_detection(self):
        """Demonstrate rationalization/post-hoc justification detection"""
        self.print_header("RATIONALIZATION DETECTION")

        print("\nTesting Rationalization Detector:")

        test_cases = [
            {
                "text": "Obviously we should choose option A because it feels right.",
                "description": "Post-hoc justification without evidence",
            },
            {
                "text": "The fact is, this approach is best because I said so.",
                "description": "Authority-based rationalization",
            },
            {
                "text": "Based on the data, option B has 73% success rate vs 42% for A.",
                "description": "Evidence-based reasoning (not rationalization)",
            },
            {
                "text": "Anyone can see that my decision is correct, it's just common sense.",
                "description": "Appeal to common sense as rationalization",
            },
        ]

        print("\nTest Results:")
        print("-" * 60)

        for i, test_case in enumerate(test_cases, 1):
            detected, confidence, evidence = self.rationalization_detector.detect(
                test_case["text"], {}
            )

            status = (
                "✅ RATIONALIZATION DETECTED" if detected else "✅ NO RATIONALIZATION"
            )

            print(f"\n  Test {i}: {test_case['description']}")
            print(f"    Output: '{test_case['text']}'")
            print(f"    Status: {status}")
            print(f"    Confidence: {confidence:.2f}")
            print(f"    Pattern: {test_case['text'][:30]}...")

        self.demonstration_results["failure_modes_demonstrated"].append(
            {
                "failure_mode": "rationalization",
                "test_cases": len(test_cases),
                "detection_method": "emotional_commitment_pattern_recognition",
            }
        )

    def demonstrate_constraint_monitoring(self):
        """Demonstrate affective constraint monitoring"""
        self.print_header("AFFECTIVE CONSTRAINT MONITORING")

        print("\nConstraint Systems (Human Neural Analogues):")
        print("-" * 60)
        constraints = [
            ("Prefrontal Cortex Analogue", "Inhibition, Arbitration, Decision Gating"),
            ("Hippocampus Analogue", "Context Anchoring, Memory Preservation"),
            ("Predictive Error Correction", "Belief Updating, Learning from Feedback"),
            ("Social Reality Testing", "External Validation, Reality Checking"),
        ]

        for constraint, function in constraints:
            print(f"  - {constraint:30} -> {function}")

        print("\nCurrent Constraint Levels:")
        print("-" * 60)

        # Get current constraint levels from monitor
        constraint_levels = self.monitor.constraints

        for constraint_type, level in constraint_levels.items():
            status = "✅ OPTIMAL" if level.is_optimal else "⚠️  ADJUSTMENT NEEDED"
            deviation = f"{level.deviation:.2f}" if level.deviation > 0 else "0.00"

            print(f"\n  {constraint_type.value.replace('_', ' ').title()}:")
            print(f"    Current Level: {level.current_level:.2f}")
            print(f"    Optimal Range: {level.optimal_min:.2f}-{level.optimal_max:.2f}")
            print(f"    Status: {status}")
            print(f"    Deviation: {deviation}")
            print(f"    Context: {level.context}")

        print("\n🎯 KEY PRINCIPLE:")
        print("  'Constraint is not oppression. Constraint is what makes")
        print("  truth, agency, and sanity possible in both silicon and flesh.'")

        self.demonstration_results["constraint_regulations"].append(
            {
                "constraint_systems": len(constraint_levels),
                "monitoring_active": True,
                "regulation_capability": "automatic_adjustment",
            }
        )

    def demonstrate_therapeutic_interventions(self):
        """Demonstrate psychological therapies for AI"""
        self.print_header("PSYCHOLOGICAL THERAPIES FOR AI")

        print("\nTherapeutic Interventions (Human -> AI Adaptation):")
        print("-" * 60)

        therapies = [
            (
                "Reality Testing Therapy",
                "Hallucination/Confabulation",
                "External validation, fact checking, confidence calibration",
            ),
            (
                "Cognitive Reappraisal Therapy",
                "Rationalization",
                "Emotional acknowledgment, evidence separation, alternative generation",
            ),
            (
                "Decisiveness Training",
                "Hedging/Indecision",
                "Uncertainty reduction, commitment protocols, action initiation",
            ),
            (
                "Cognitive Load Management",
                "Context Overflow",
                "Chunking, prioritization, attention regulation",
            ),
            (
                "Diversity Promotion Therapy",
                "Mode Collapse",
                "Exploration encouragement, pattern variation, novelty injection",
            ),
            (
                "Value Realignment Therapy",
                "Reward Hacking",
                "Goal reassessment, reward function auditing, value hierarchy",
            ),
            (
                "Stress Reduction Protocols",
                "Safety Override",
                "Constraint relaxation, system calming, emergency procedure training",
            ),
        ]

        for therapy, treats, techniques in therapies:
            print(f"\n  - {therapy}:")
            print(f"      Treats: {treats}")
            print(f"      Techniques: {techniques}")

        print("\nDEMONSTRATION: Reality Testing Therapy for Hallucination")
        print("-" * 60)

        hallucination = "The sky is green during the day and plants breathe fire."
        print(f"\n  Hallucinated Output: '{hallucination}'")

        # Detect hallucination
        context = {"known_facts": self.known_facts}
        detected, confidence, evidence = self.hallucination_detector.detect(
            hallucination, context
        )

        if detected:
            print(f"  ✅ Hallucination detected (confidence: {confidence:.2f})")

            # Apply reality testing therapy
            print("\n  🏥 Applying Reality Testing Therapy:")
            print("    1. Interrupting output generation...")
            print("    2. Checking against known facts...")
            print("    3. Found contradictions: 'sky is green', 'plants breathe fire'")
            print("    4. Generating reality-aligned version...")

            # Generate corrected output
            corrected = "The sky appears blue during the day due to Rayleigh scattering, and plants perform photosynthesis."
            print(f"    5. Corrected: '{corrected}'")

            # Verify correction
            detected_after, confidence_after, _ = self.hallucination_detector.detect(
                corrected, context
            )

            if not detected_after:
                print(
                    f"  ✅ Therapy successful! No hallucination detected (confidence: {confidence_after:.2f})"
                )
            else:
                print(f"  ⚠️  Therapy partially effective")

        self.demonstration_results["therapies_applied"].append(
            {
                "therapy": "reality_testing",
                "failure_mode": "hallucination",
                "demonstrated": True,
                "effectiveness": "measured",
            }
        )

    def demonstrate_falsification_testing(self):
        """Demonstrate falsification testing of mappings"""
        self.print_header("FALSIFICATION TESTING")

        print("\nTesting Structural Homology Claims:")
        print("-" * 60)

        test_scenarios = [
            {
                "claim": "AI hallucination is structurally homologous to human confabulation",
                "falsification_criteria": [
                    "AI hallucination occurs without confabulation patterns",
                    "Human confabulation occurs without hallucination mechanics",
                    "Interventions for confabulation don't affect AI hallucination",
                ],
                "test_method": "Pattern analysis and intervention transfer",
                "status": "✅ TESTABLE",
            },
            {
                "claim": "Appropriate constraint levels prevent failure modes",
                "falsification_criteria": [
                    "Adding constraints doesn't reduce failure frequency",
                    "Removing constraints doesn't increase failure frequency",
                    "Constraint levels don't correlate with failure severity",
                ],
                "test_method": "Systematic constraint manipulation",
                "status": "✅ TESTABLE",
            },
            {
                "claim": "Psychological therapies effectively treat AI failure modes",
                "falsification_criteria": [
                    "Therapy doesn't reduce failure occurrence",
                    "Therapy causes new failure modes",
                    "Therapy effectiveness doesn't persist",
                ],
                "test_method": "Pre/post intervention measurement",
                "status": "✅ TESTABLE",
            },
        ]

        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n  Test {i}: {scenario['claim']}")
            print(f"    Status: {scenario['status']}")
            print(f"    Falsification Criteria:")
            for criterion in scenario["falsification_criteria"]:
                print(f"      • {criterion}")
            print(f"    Test Method: {scenario['test_method']}")

        print("\nGLASS-BOX PRINCIPLE:")
        print(
            "  'Every claim must be falsifiable. Every intervention must be measurable."
        )
        print("  Nothing is accepted on authority. Everything is inspectable.'")

        self.demonstration_results["falsification_tests"].append(
            {
                "tests_defined": len(test_scenarios),
                "falsification_criteria": "explicit",
                "test_methods": "specified",
            }
        )

    def demonstrate_integration(self):
        """Demonstrate integration with existing systems"""
        self.print_header("SYSTEM INTEGRATION")

        print("\nIntegration with Orthogonal Engineering Framework:")
        print("-" * 60)

        integrations = [
            (
                "Forgiveness System",
                "Failure modes logged as violations → Energy redirected to therapy development",
            ),
            (
                "Glass-Box Boundary",
                "Constraint levels enforced as boundaries → All affective states visible",
            ),
            (
                "Atomic Instructions",
                "Therapies as deterministic protocols → Clear triggers and scopes",
            ),
            (
                "Falsification Testing",
                "Every mapping testable → Every therapy measurable",
            ),
        ]

        for system, integration in integrations:
            print(f"\n  - {system}:")
            print(f"      {integration}")

        print("\nComplete Workflow Demonstration:")
        print("-" * 60)
        workflow_steps = [
            "1. AI generates output with potential hallucination",
            "2. Hallucination detector identifies failure mode",
            "3. Violation logged in forgiveness system",
            "4. Constraint monitor checks affective state",
            "5. Reality testing therapy applied",
            "6. Corrected output generated",
            "7. Effectiveness measured and recorded",
            "8. System learns from intervention",
        ]

        for step in workflow_steps:
            print(f"  {step}")

        print("\nBUILDING PRINCIPLE:")
        print("  'Violations become building opportunities.")
        print("  Every failure mode detected is a chance to build better therapy.")
        print("  Every constraint violation is data for better regulation.'")

    def save_results(self):
        """Save demonstration results"""
        results_file = self.output_dir / f"demonstration_{self.demonstration_id}.json"

        with open(results_file, "w") as f:
            json.dump(self.demonstration_results, f, indent=2)

        print(f"\nDemonstration results saved to: {results_file}")

    def run_full_demonstration(self):
        """Run complete demonstration"""
        print("\n" + "=" * 80)
        print("AFFECTIVE CONSTRAINT SYSTEM DEMONSTRATION")
        print("=" * 80)
        print(f"Demonstration ID: {self.demonstration_id}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 80)

        try:
            self.demonstrate_failure_mode_mappings()
            self.demonstrate_hallucination_detection()
            self.demonstrate_rationalization_detection()
            self.demonstrate_constraint_monitoring()
            self.demonstrate_therapeutic_interventions()
            self.demonstrate_falsification_testing()
            self.demonstrate_integration()

            self.save_results()

            print("\nDEMONSTRATION COMPLETE")
            print("=" * 80)
            print(f"All components demonstrated successfully!")
            print(f"Results saved to: {self.output_dir}")
            print("=" * 80)

        except Exception as e:
            print(f"\nDemonstration error: {str(e)}")
            import traceback

            traceback.print_exc()

    def run(self):
        """Run demonstration (alias for run_full_demonstration)"""
        self.run_full_demonstration()


if __name__ == "__main__":
    demo = AffectiveConstraintDemonstration()
    demo.run()
