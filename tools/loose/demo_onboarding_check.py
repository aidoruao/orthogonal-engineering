"""
Demo script for Onboarding Check - IDE-AI Integration

Demonstrates the atomic instruction blueprint implementation for
"Check-Onboarding Status" in the Orthogonal Engineering framework.

Author: Orthogonal Engineering System
Date: 2026-01-24
Version: 1.0.0
"""

import sys
from pathlib import Path

# Add toolkit to path
sys.path.insert(0, str(Path(__file__).parent / "toolkit"))

from toolkit.oe.onboarding_check import (
    CheckOnboardingPipeline,
    OnboardingChecker,
    OnboardingStatus,
)


def demo_basic_check():
    """Demonstrate basic onboarding check."""
    print("=" * 60)
    print("DEMO 1: BASIC ONBOARDING CHECK")
    print("=" * 60)

    checker = OnboardingChecker()
    report = checker.run_full_check()

    print("\n📊 Report Summary:")
    print(f"  Status: {report.status.value.upper()}")
    print(f"  Repository: {report.repository_root}")
    print(f"  Artifacts found: {len(report.candidate_artifacts)}")

    if report.artifact_path:
        print(f"  Primary artifact: {report.artifact_path}")

    if report.missing_fields:
        print(f"  Missing fields: {', '.join(report.missing_fields)}")

    # Save report
    output_path = checker.save_report()
    print(f"\n💾 Report saved to: {output_path}")

    return report


def demo_pipeline_form():
    """Demonstrate pipeline form with stage outputs."""
    print("\n" + "=" * 60)
    print("DEMO 2: PIPELINE FORM")
    print("=" * 60)

    pipeline = CheckOnboardingPipeline()

    print("Running pipeline stages...")

    # Stage 1: Identify candidate artifacts
    print("\n🔍 Stage 1: Identifying candidate artifacts")
    artifacts = pipeline.stage_1_identify_candidate_artifacts()
    print(f"  Found {len(artifacts)} artifacts")

    if artifacts:
        print("  Sample artifacts:")
        for artifact in artifacts[:3]:  # Show first 3
            print(f"    - {artifact.path} ({artifact.artifact_type.value})")
        if len(artifacts) > 3:
            print(f"    ... and {len(artifacts) - 3} more")

    # Stage 2: Validate structure
    print("\n✅ Stage 2: Validating artifact structure")
    if artifacts:
        validation_results = pipeline.stage_2_validate_structure(artifacts)

        valid_count = sum(1 for r in validation_results if r.status == "valid")
        partial_count = sum(1 for r in validation_results if r.status == "partial")
        invalid_count = sum(1 for r in validation_results if r.status == "invalid")

        print(
            f"  Valid: {valid_count}, Partial: {partial_count}, Invalid: {invalid_count}"
        )

        # Show validation details for first artifact
        if validation_results:
            first_result = validation_results[0]
            print(f"\n  Sample validation for '{first_result.artifact_path}':")
            print(f"    Status: {first_result.status}")
            if first_result.missing_fields:
                print(
                    f"    Missing fields: {', '.join(first_result.missing_fields[:3])}"
                )
                if len(first_result.missing_fields) > 3:
                    print(f"    ... and {len(first_result.missing_fields) - 3} more")

    # Stage 3: Cross-check with repository
    print("\n🔗 Stage 3: Cross-checking with repository")
    if artifacts:
        # Find artifact with commit hash
        artifact_with_hash = next((a for a in artifacts if a.commit_hash), None)
        cross_check = pipeline.stage_3_cross_check_repo(
            artifact_with_hash.commit_hash if artifact_with_hash else None
        )

        print(f"  Commit match: {cross_check.commit_match}")
        print(f"  Directories exist: {len(cross_check.directories_exist)}")
        print(f"  Directories missing: {len(cross_check.directories_missing)}")
        print(f"  Critical files found: {len(cross_check.files_exist)}")
        print(f"  Critical files missing: {len(cross_check.files_missing)}")

    # Stage 4: Generate report
    print("\n📋 Stage 4: Generating report")
    report = pipeline.stage_4_generate_report(
        artifacts if artifacts else [],
        validation_results if "validation_results" in locals() else [],
        cross_check if "cross_check" in locals() else None,
    )

    print(f"  Final status: {report.status.value.upper()}")

    # Save stage outputs
    saved_files = pipeline.save_stage_outputs()
    print(f"\n💾 Stage outputs saved:")
    for stage, path in saved_files.items():
        print(f"  {stage}: {path}")

    return report


def demo_atomic_instruction_blueprint():
    """Demonstrate the atomic instruction blueprint principles."""
    print("\n" + "=" * 60)
    print("DEMO 3: ATOMIC INSTRUCTION BLUEPRINT")
    print("=" * 60)

    print("""
🎯 Atomic Instruction Blueprint: "Check-Onboarding Status"

1️⃣ Define the Goal
   Determine if an onboarding acknowledgment exists fully or partially.

2️⃣ Atomic Steps (Teach the AI How to Fish)
   Step 1 — Identify Candidate Artifacts
   Step 2 — Validate Structure
   Step 3 — Cross-Check with Repository
   Step 4 — Produce Report

3️⃣ Teaching Principles
   • Each step is idempotent (repeatable without side effects)
   • The AI does not modify files — read-only for verification
   • Partial results are logged atomically for later reasoning
   • The AI is self-verifying: checks its own observation

4️⃣ Pipeline Form
   pipeline: CheckOnboarding
     stage_1: IdentifyCandidateArtifacts
     stage_2: ValidateStructure
     stage_3: CrossCheckRepo
     stage_4: GenerateReport

5️⃣ Outcome
   You teach the AI how to fish in any repo
   AI can adapt to repo changes, partial commits, new threads
   You never trust a thread blindly; all verification is concrete
""")

    # Show how the blueprint maps to code
    print("\n🔧 Blueprint to Code Mapping:")
    print("  Step 1 → identify_candidate_artifacts()")
    print("  Step 2 → validate_artifact_structure()")
    print("  Step 3 → cross_check_with_repository()")
    print("  Step 4 → generate_report()")
    print("\n  Pipeline → CheckOnboardingPipeline class")
    print("  Stage outputs → save_stage_outputs()")


def demo_integration_with_existing_system():
    """Demonstrate integration with existing Glass-Box Boundary system."""
    print("\n" + "=" * 60)
    print("DEMO 4: INTEGRATION WITH GLASS-BOX BOUNDARY")
    print("=" * 60)

    print("""
🔄 Integration Points:

1. With AGENT.md Framework:
   • Uses @glass_box_boundary decorators
   • Follows GB-ORIGIN-1.11 schema
   • Produces trace-compatible reports

2. With Existing Onboarding System:
   • Checks ONBOARD_FIRST.md, LEVEL1.md, LEVEL2.md
   • Validates critical files exist
   • Cross-checks with repository state

3. With IDE-AI Integration:
   • Read-only verification (no modifications)
   • Atomic, idempotent operations
   • Self-verifying design
   • Pipeline form for debugging

4. With CI/CD Pipeline:
   • Exit codes: 0=Full, 1=Partial, 2=Absent, 3=Error
   • JSON report output
   • Stage outputs for debugging
   • Integration with run_full_audit_with_trace.py
""")

    # Show exit code mapping
    print("\n🚦 Exit Code Mapping:")
    print("  0: Onboarding status FULL - All artifacts verified")
    print("  1: Onboarding status PARTIAL - Some artifacts missing/incomplete")
    print("  2: Onboarding status ABSENT - No valid onboarding artifacts")
    print("  3: Error during check execution")


def demo_usage_examples():
    """Show practical usage examples."""
    print("\n" + "=" * 60)
    print("DEMO 5: PRACTICAL USAGE EXAMPLES")
    print("=" * 60)

    print("""
📝 Command Line Usage:

1. Basic check with auto-generated report:
   $ python -m toolkit.oe.onboarding_check

2. Specify repository path:
   $ python -m toolkit.oe.onboarding_check --repository /path/to/repo

3. Save report to specific location:
   $ python -m toolkit.oe.onboarding_check --output /path/to/report.json

4. Use pipeline form with stage outputs:
   $ python -m toolkit.oe.onboarding_check --pipeline --save-stages

5. Verbose output:
   $ python -m toolkit.oe.onboarding_check --verbose

📝 Python API Usage:

```python
from toolkit.oe.onboarding_check import OnboardingChecker

# Basic check
checker = OnboardingChecker("/path/to/repo")
report = checker.run_full_check()
print(f"Status: {report.status.value}")

# Pipeline form
from toolkit.oe.onboarding_check import CheckOnboardingPipeline
pipeline = CheckOnboardingPipeline()
report = pipeline.run_pipeline()

# Access stage outputs
artifacts = pipeline.stage_1_identify_candidate_artifacts()
validation = pipeline.stage_2_validate_structure(artifacts)
```

📝 Integration with Existing Scripts:

```python
# In run_full_audit_with_trace.py
from toolkit.oe.onboarding_check import OnboardingChecker

def check_onboarding_status():
    checker = OnboardingChecker()
    report = checker.run_full_check()

    if report.status == OnboardingStatus.ABSENT:
        print("❌ No onboarding artifacts found")
        return False
    elif report.status == OnboardingStatus.PARTIAL:
        print("⚠️  Partial onboarding - some artifacts missing")
        return True  # Allow with warning
    else:
        print("✅ Onboarding verified")
        return True
```
""")


def main():
    """Main demonstration function."""
    print("🚀 ONBOARDING CHECK DEMONSTRATION")
    print("=" * 60)
    print("Orthogonal Engineering - IDE-AI Integration")
    print("Atomic Instruction Blueprint: 'Check-Onboarding Status'")
    print("=" * 60)

    try:
        # Run demos
        report1 = demo_basic_check()
        report2 = demo_pipeline_form()
        demo_atomic_instruction_blueprint()
        demo_integration_with_existing_system()
        demo_usage_examples()

        # Summary
        print("\n" + "=" * 60)
        print("🎉 DEMONSTRATION COMPLETE")
        print("=" * 60)
        print(f"\nFinal onboarding status: {report2.status.value.upper()}")

        if report2.status == OnboardingStatus.FULL:
            print("✅ Repository is fully onboarded and ready for AI work")
        elif report2.status == OnboardingStatus.PARTIAL:
            print("⚠️  Repository has partial onboarding - review missing artifacts")
        else:
            print("❌ Repository lacks onboarding artifacts - run onboarding protocol")

        print("\n📚 Next steps:")
        print("  1. Review the generated reports in logs/onboarding_checks/")
        print("  2. Integrate with your CI/CD pipeline")
        print("  3. Add to pre-commit hooks")
        print("  4. Use in AI agent initialization")

    except Exception as e:
        print(f"\n❌ Demonstration error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
