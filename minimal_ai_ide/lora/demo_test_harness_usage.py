"""
Demonstration Script: Using the Unified Test Harness System

This script demonstrates how to properly use the new test harness system
to prevent test script explosion while maintaining comprehensive validation.

Key Concepts Demonstrated:
1. Stage-aware test generation
2. Using the unified test harness
3. Respecting output limits
4. Implementing feedback loops
5. Constraint preservation
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from lora.test_harness import LoRATestHarness, TestCase

    HARNESS_AVAILABLE = True
except ImportError:
    HARNESS_AVAILABLE = False
    print("Warning: Test harness not available, running in demo mode")


def demonstrate_stage_awareness():
    """Demonstrate stage-aware test generation"""
    print("\n" + "=" * 70)
    print("DEMONSTRATION 1: Stage-Aware Test Generation")
    print("=" * 70)

    if not HARNESS_AVAILABLE:
        print("Skipping - harness not available")
        return

    # Create harness instance
    harness = LoRATestHarness()

    # Check current stage and test generation permission
    allowed, message = harness.can_generate_tests()

    print(f"Current Stage: {harness.system_status.get('lora_training_stage', 0)}")
    print(
        f"Stage Description: {harness.system_status.get('current_stage_description', 'unknown')}"
    )
    print(f"Test Generation Allowed: {'YES' if allowed else 'NO'}")
    print(f"Message: {message}")

    # Show stage definitions
    print("\nStage Definitions:")
    stage_defs = harness.system_status.get("stage_definitions", {})
    for stage_num, stage_info in sorted(stage_defs.items()):
        print(f"  Stage {stage_num}: {stage_info.get('name', 'unknown')}")
        print(f"    Description: {stage_info.get('description', '')}")
        print(
            f"    Test Generation: {'ALLOWED' if stage_info.get('allowed_test_generation') else 'NOT ALLOWED'}"
        )
        print(f"    Max Scripts: {stage_info.get('max_test_scripts', 0)}")
        print(f"    Max Lines: {stage_info.get('max_test_lines', 0)}")

    return harness


def demonstrate_harness_usage(harness):
    """Demonstrate using the unified test harness"""
    print("\n" + "=" * 70)
    print("DEMONSTRATION 2: Unified Test Harness Usage")
    print("=" * 70)

    if not HARNESS_AVAILABLE:
        print("Skipping - harness not available")
        return

    # List current test cases
    print("\nCurrent Test Cases in Registry:")
    harness.list_test_cases()

    # Get test summary
    summary = harness.get_test_summary()
    print(f"\nTest Summary:")
    print(f"Total test cases: {summary['total_test_cases']}")
    print("Test cases by stage:")
    for stage, count in summary["by_stage"].items():
        print(f"  Stage {stage}: {count} test(s)")

    # Demonstrate adding a new test case (if allowed)
    allowed, message = harness.can_generate_tests()
    if allowed:
        print("\nDemonstrating test case addition...")

        # Create a new test case
        new_test = TestCase(
            id="demo_test_1",
            name="Demo Validation Test",
            description="Demonstration test for harness usage",
            stage=harness.system_status.get("lora_training_stage", 0),
            function_name="test_demo_validation",
            constraints=["LOGOS", "DEMO_INTEGRITY"],
            timeout_seconds=15,
            required=False,
        )

        # Add to harness
        harness.add_test_case(new_test)
        print(f"Added demo test case: {new_test.name}")

        # Note: In real usage, you would also implement the test function
        # in the harness or in a separate module

        # Remove demo test to keep registry clean
        harness.remove_test_case("demo_test_1")
        print("Removed demo test case to keep registry clean")
    else:
        print(f"\nCannot add test case: {message}")


def demonstrate_stage_transition():
    """Demonstrate stage transitions"""
    print("\n" + "=" * 70)
    print("DEMONSTRATION 3: Stage Transitions")
    print("=" * 70)

    if not HARNESS_AVAILABLE:
        print("Skipping - harness not available")
        return

    harness = LoRATestHarness()
    current_stage = harness.system_status.get("lora_training_stage", 0)

    print(f"Current Stage: {current_stage}")

    # Demonstrate what happens at each stage transition
    stages_to_demo = [1, 2, 3]  # Skip stage 0 (setup)

    for new_stage in stages_to_demo:
        if new_stage <= current_stage:
            continue

        print(f"\nTransitioning to Stage {new_stage}:")

        # Get stage info
        stage_defs = harness.system_status.get("stage_definitions", {})
        stage_info = stage_defs.get(str(new_stage), {})

        print(f"  Stage Name: {stage_info.get('name', 'unknown')}")
        print(f"  Description: {stage_info.get('description', '')}")
        print(
            f"  Test Generation: {'ALLOWED' if stage_info.get('allowed_test_generation') else 'NOT ALLOWED'}"
        )

        # Show what tests would run at this stage
        test_cases = [tc for tc in harness.test_cases if tc.stage == new_stage]
        print(f"  Tests at this stage: {len(test_cases)}")

        for tc in test_cases:
            print(f"    - {tc.name}: {tc.description}")

    print("\nNote: Actual stage transitions would use:")
    print("  python lora/test_harness.py update-stage --stage X --desc 'Description'")


def demonstrate_feedback_loop():
    """Demonstrate feedback loop implementation"""
    print("\n" + "=" * 70)
    print("DEMONSTRATION 4: Feedback Loop Implementation")
    print("=" * 70)

    # Load system status
    status_file = "lora/system_status.json"
    try:
        with open(status_file, "r") as f:
            status = json.load(f)
    except FileNotFoundError:
        print(f"Status file not found: {status_file}")
        return

    print("Current System Status:")
    print(f"  Training Stage: {status.get('lora_training_stage', 0)}")
    print(f"  Test Generation Count: {status.get('test_generation_count', 0)}")

    last_results = status.get("last_test_results")
    if last_results:
        print(f"  Last Test Results:")
        print(f"    Stage: {last_results.get('stage', 'unknown')}")
        print(f"    Timestamp: {last_results.get('timestamp', 'unknown')}")
        print(
            f"    Passed: {last_results.get('passed', 0)}/{last_results.get('total_tests', 0)}"
        )
    else:
        print("  No previous test results")

    # Demonstrate checking before generating tests
    print("\nFeedback Loop Check (Before Generating Tests):")

    current_stage = status.get("lora_training_stage", 0)
    stage_defs = status.get("stage_definitions", {})
    stage_info = stage_defs.get(str(current_stage), {})

    if not stage_info.get("allowed_test_generation", False):
        print("  ❌ Test generation not allowed at current stage")
        print(f"  Action: Wait for stage transition or use existing test results")
    else:
        gen_count = status.get("test_generation_count", 0)
        max_scripts = stage_info.get("max_test_scripts", 0)

        if gen_count >= max_scripts:
            print(f"  ❌ Test generation limit reached ({gen_count}/{max_scripts})")
            print(f"  Action: Use existing test results or request limit increase")
        else:
            print(f"  ✅ Test generation allowed ({gen_count}/{max_scripts} used)")
            print(f"  Action: Can generate new tests")

    # Demonstrate updating after test completion
    print("\nFeedback Loop Update (After Test Completion):")
    print("  After running tests, system status would be updated with:")
    print("    - Last test generation timestamp")
    print("    - Test results (pass/fail counts)")
    print("    - Updated generation count")
    print("    - Any new test cases added to registry")


def demonstrate_constraint_preservation():
    """Demonstrate constraint preservation in tests"""
    print("\n" + "=" * 70)
    print("DEMONSTRATION 5: Constraint Preservation")
    print("=" * 70)

    print("Theological Constraints for Tests:")
    constraints = {
        "LOGOS": "Structural integrity and coherence",
        "CHALCEDON": "Duality preservation (human/divine, train/eval)",
        "GRACE": "Error tolerance and recovery",
        "SETUP_INTEGRITY": "Environment validation",
        "DATA_INTEGRITY": "Dataset validation",
        "MODEL_INTEGRITY": "Model validation",
        "GOVERNANCE": "Compliance checking",
        "CONSTRAINT_PRESERVATION": "Constraint verification",
        "DEMO_INTEGRITY": "Demonstration system integrity",
    }

    for constraint, description in constraints.items():
        print(f"  {constraint}: {description}")

    print("\nExample Test Case with Constraints:")
    example_test = {
        "id": "example_constraint_test",
        "name": "Multi-Constraint Validation",
        "constraints": ["LOGOS", "DATA_INTEGRITY", "GRACE"],
        "description": "Validates data while preserving structural integrity and allowing graceful error handling",
    }

    for key, value in example_test.items():
        print(f"  {key}: {value}")

    print("\nConstraint Preservation Rules:")
    print("  1. All tests must declare their constraints")
    print("  2. Tests must not violate declared constraints")
    print("  3. Test results must be checked against constraint requirements")
    print("  4. Constraint violations must be logged and addressed")


def demonstrate_cli_usage():
    """Demonstrate command-line interface usage"""
    print("\n" + "=" * 70)
    print("DEMONSTRATION 6: Command-Line Interface Usage")
    print("=" * 70)

    print("Available Commands:")

    commands = {
        "run": "Run tests for current stage",
        "update-stage": "Update to a new stage (requires --stage and --desc)",
        "list": "List all test cases in registry",
        "check-generation": "Check if test generation is allowed",
        "summary": "Get test summary statistics",
    }

    for cmd, description in commands.items():
        print(f"  python lora/test_harness.py {cmd}")
        print(f"    {description}")

    print("\nExamples:")
    print("  # Run tests for current stage")
    print("  python lora/test_harness.py run")
    print("")
    print("  # Update to stage 1 (small validation)")
    print(
        "  python lora/test_harness.py update-stage --stage 1 --desc 'Setup complete'"
    )
    print("")
    print("  # List all test cases")
    print("  python lora/test_harness.py list")
    print("")
    print("  # Check if test generation is allowed")
    print("  python lora/test_harness.py check-generation")
    print("")
    print("  # Get test summary")
    print("  python lora/test_harness.py summary")

    print("\nExpected Output Format:")
    print("""
  ======================================================================
  Running tests for LoRA Training Stage 1
  Number of tests: 2
  ======================================================================

  ============================================================
  Running test: Dataset Validation
  Description: Validate training dataset format and structure
  Stage: 1
  Constraints: LOGOS, DATA_INTEGRITY
  ============================================================
  ✓ Dataset validation passed
  ✓ Test PASSED in 0.45s
  """)


def demonstrate_emergency_override():
    """Demonstrate emergency override (use sparingly)"""
    print("\n" + "=" * 70)
    print("DEMONSTRATION 7: Emergency Override (Use Sparingly)")
    print("=" * 70)

    print("Emergency override should ONLY be used when:")
    print("  1. System is in a broken state")
    print("  2. Standard validation is failing")
    print("  3. Manual intervention is required")
    print("  4. You have explicit approval")

    print("\nEmergency Diagnostic Template:")
    emergency_template = '''"""
EMERGENCY DIAGNOSTIC - MANUAL OVERRIDE
Reason: [Explain why override is needed]
Approval: [Reference approval if any]
Timestamp: {timestamp}
"""

import os
import sys
from datetime import datetime

def emergency_diagnostic():
    """Emergency diagnostic function"""
    print("EMERGENCY DIAGNOSTIC ACTIVE")
    print(f"Time: {datetime.now().isoformat()}")

    # Emergency logic here
    # This bypasses normal limits and constraints
    # Use extreme caution

    print("Emergency diagnostic complete")

if __name__ == "__main__":
    emergency_diagnostic()'''

    print(emergency_template.format(timestamp=datetime.datetime.now().isoformat()))

    print("\n⚠ WARNING: Emergency overrides:")
    print("  - Bypass all normal limits and constraints")
    print("  - Can cause system instability if misused")
    print("  - Must be thoroughly documented")
    print("  - Should be removed after use")


def main():
    """Main demonstration function"""
    print("=" * 70)
    print("UNIFIED TEST HARNESS SYSTEM DEMONSTRATION")
    print("=" * 70)
    print("This script demonstrates the new structured approach to")
    print("test generation that prevents script explosion while")
    print("maintaining comprehensive LoRA training validation.")
    print("=" * 70)

    # Check if harness is available
    if not HARNESS_AVAILABLE:
        print("\n⚠ WARNING: Test harness module not available!")
        print("Running in demonstration-only mode.")
        print("To use the full system, ensure:")
        print("  1. lora/test_harness.py exists")
        print("  2. Python path includes project root")
        print("  3. All dependencies are installed")

    # Run demonstrations
    harness = demonstrate_stage_awareness()

    if HARNESS_AVAILABLE:
        demonstrate_harness_usage(harness)

    demonstrate_stage_transition()
    demonstrate_feedback_loop()
    demonstrate_constraint_preservation()
    demonstrate_cli_usage()
    demonstrate_emergency_override()

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY: Key Benefits of New System")
    print("=" * 70)

    benefits = [
        "Prevents test script explosion through structured approach",
        "Enforces stage-aware test generation",
        "Provides unified test harness for all validation",
        "Implements feedback loops to avoid redundant tests",
        "Respects output limits (script count, line count)",
        "Preserves theological and governance constraints",
        "Provides clear CLI for all operations",
        "Includes emergency override for critical situations",
        "Maintains comprehensive validation without clutter",
    ]

    for i, benefit in enumerate(benefits, 1):
        print(f"{i}. {benefit}")

    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Review AI_TEST_GENERATION_INSTRUCTIONS.md for detailed guidance")
    print("2. Use 'python lora/test_harness.py list' to see available tests")
    print("3. Check current stage with 'python lora/test_harness.py check-generation'")
    print("4. Run tests for current stage with 'python lora/test_harness.py run'")
    print("5. Add new test cases to harness instead of creating separate scripts")
    print("\nRemember: The goal is comprehensive validation without script explosion!")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Demonstrate unified test harness system usage"
    )
    parser.add_argument(
        "--section",
        type=str,
        choices=[
            "all",
            "stage",
            "harness",
            "feedback",
            "constraints",
            "cli",
            "emergency",
        ],
        default="all",
        help="Specific section to demonstrate",
    )

    args = parser.parse_args()

    if args.section == "all":
        main()
    else:
        print("=" * 70)
        print(f"DEMONSTRATION: {args.section.upper()} SECTION")
        print("=" * 70)

        if args.section == "stage":
            demonstrate_stage_awareness()
        elif args.section == "harness" and HARNESS_AVAILABLE:
            harness = LoRATestHarness()
            demonstrate_harness_usage(harness)
        elif args.section == "feedback":
            demonstrate_feedback_loop()
        elif args.section == "constraints":
            demonstrate_constraint_preservation()
        elif args.section == "cli":
            demonstrate_cli_usage()
        elif args.section == "emergency":
            demonstrate_emergency_override()
        else:
            print(f"Cannot demonstrate '{args.section}' - harness not available")
