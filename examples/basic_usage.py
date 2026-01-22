"""
Orthogonal Engineering Toolkit - Basic Usage Example

This example demonstrates the basic usage of the Orthogonal Engineering Toolkit
including the EvidenceStore, causality logging, and CLI interface.

Implements G11-04: Examples directory contains usage examples.
"""

import json
import sys
from pathlib import Path

# Add toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from toolkit.oe import EvidenceStore
from toolkit.oe import main as cli_main
from toolkit.oe.evidence_store import log_causality_quick


def demonstrate_evidence_store():
    """Demonstrate EvidenceStore functionality."""
    print("=== Demonstrating EvidenceStore ===")

    # Create evidence store
    store = EvidenceStore()
    print(f"Evidence store created at: {store.base_path}")

    # Log some evidence
    evidence_id = store.log_evidence(
        evidence_type="test_result",
        content={"test": "basic_usage", "status": "passed", "score": 100},
        source="basic_usage.py",
        metadata={"example": True, "phase": 11},
    )
    print(f"Logged evidence with ID: {evidence_id}")

    # Retrieve evidence
    evidence = store.get_evidence(evidence_id)
    if evidence:
        print(f"Retrieved evidence: {evidence['type']} from {evidence['source']}")
        print(f"Content: {json.dumps(evidence['content'], indent=2)}")

    # Get statistics
    stats = store.get_stats()
    print(f"\nEvidence store statistics:")
    print(f"  Total evidence entries: {stats['total_evidence']}")
    print(f"  Total causality entries: {stats['total_causality']}")
    print(f"  Evidence by type: {stats['evidence_by_type']}")

    return store


def demonstrate_causality_logging():
    """Demonstrate causality logging functionality."""
    print("\n=== Demonstrating Causality Logging ===")

    # Quick causality logging
    causality_id = log_causality_quick(
        cause="Demonstrating causality logging in example",
        trigger="example_execution",
        invariant_id="G11-06",
        actor="example_script",
    )
    print(f"Logged causality with ID: {causality_id}")

    # Create store for more advanced logging
    store = EvidenceStore()

    # Detailed causality logging
    detailed_id = store.log_causality(
        {
            "cause": "Detailed causality example",
            "trigger": "manual_invocation",
            "invariant_id": "G11-06",
            "timestamp": "2026-01-21T12:00:00Z",
            "actor": "example_script",
            "additional_info": "This is a detailed example",
        }
    )
    print(f"Logged detailed causality with ID: {detailed_id}")

    # Search causality logs
    logs = store.search_causality(invariant_id="G11-06")
    print(f"Found {len(logs)} causality logs for invariant G11-06")

    return store


def demonstrate_cli_interface():
    """Demonstrate CLI interface functionality."""
    print("\n=== Demonstrating CLI Interface ===")

    print("Available CLI commands:")
    print("  python -m toolkit.oe verify     - Verify blueprint compliance")
    print("  python -m toolkit.oe generate   - Generate missing artifacts")
    print("  python -m toolkit.oe audit      - Run full audit with trace")
    print("  python -m toolkit.oe help       - Show help message")

    # Note: In a real script, we would call the CLI functions directly
    # For this example, we'll just show how to import and use them
    from toolkit.oe.cli import generate_missing_artifacts, verify_blueprint_compliance

    print("\nCLI functions available for import:")
    print("  from toolkit.oe.cli import verify_blueprint_compliance")
    print("  from toolkit.oe.cli import generate_missing_artifacts")
    print("  from toolkit.oe.cli import log_causality_metadata")


def demonstrate_integrity_verification():
    """Demonstrate integrity verification."""
    print("\n=== Demonstrating Integrity Verification ===")

    store = EvidenceStore()

    # Verify integrity
    print("Verifying evidence store integrity...")
    report = store.verify_integrity()

    if report.get("all_valid", False):
        print("✅ All evidence and causality logs are valid")
    else:
        print("❌ Integrity issues found:")
        for issue in report.get("issues", []):
            print(f"  - {issue}")

    print(f"\nIntegrity report summary:")
    print(f"  Total evidence entries: {report['total_evidence']}")
    print(f"  Total causality entries: {report['total_causality']}")
    print(f"  Evidence integrity checks: {len(report['evidence_integrity'])}")
    print(f"  Causality integrity checks: {len(report['causality_integrity'])}")


def demonstrate_workflow_integration():
    """Demonstrate workflow integration."""
    print("\n=== Demonstrating Workflow Integration ===")

    # Check if workflow YAML exists
    workflow_path = Path("workflows/basic_validation.yaml")
    if workflow_path.exists():
        print(f"✅ Workflow YAML found: {workflow_path}")

        # Read and display basic info
        try:
            import yaml

            with open(workflow_path, "r") as f:
                workflow = yaml.safe_load(f)

            print(f"Workflow: {workflow.get('name', 'Unknown')}")
            print(f"Version: {workflow.get('version', 'Unknown')}")
            print(f"Description: {workflow.get('description', 'No description')}")
            print(f"Steps: {len(workflow.get('steps', []))}")

        except ImportError:
            print("Note: PyYAML not installed, skipping workflow parsing")
        except Exception as e:
            print(f"Note: Could not parse workflow: {e}")
    else:
        print(f"⚠️ Workflow YAML not found: {workflow_path}")


def demonstrate_ontology_usage():
    """Demonstrate ontology usage."""
    print("\n=== Demonstrating Ontology Usage ===")

    # Check ontology files
    yaml_ontology = Path("ontology/failure_ontology.yaml")
    owl_ontology = Path("ontology/failure_ontology.owl")

    if yaml_ontology.exists():
        print(f"✅ YAML ontology found: {yaml_ontology}")
    else:
        print(f"❌ YAML ontology missing: {yaml_ontology}")

    if owl_ontology.exists():
        print(f"✅ OWL ontology found: {owl_ontology}")
    else:
        print(f"❌ OWL ontology missing: {owl_ontology}")

    # Demonstrate failure classification
    print("\nFailure classification example:")
    failures = [
        {
            "type": "boundary_violation",
            "description": "Missing @glass_box_boundary decorator",
        },
        {"type": "missing_artifact", "description": "toolkit/oe/cli.py not found"},
        {
            "type": "causality_metadata_missing",
            "description": "File created without causality log",
        },
    ]

    for failure in failures:
        print(f"  - {failure['type']}: {failure['description']}")


def main():
    """Main example function."""
    print("Orthogonal Engineering Toolkit - Basic Usage Example")
    print("=" * 60)

    try:
        # Demonstrate all features
        demonstrate_evidence_store()
        demonstrate_causality_logging()
        demonstrate_cli_interface()
        demonstrate_integrity_verification()
        demonstrate_workflow_integration()
        demonstrate_ontology_usage()

        print("\n" + "=" * 60)
        print("✅ Example completed successfully")
        print("\nNext steps:")
        print("1. Run blueprint verification: python -m toolkit.oe verify")
        print("2. Generate missing artifacts: python -m toolkit.oe generate")
        print("3. Run full audit: python -m toolkit.oe audit")

        # Log completion
        log_causality_quick(
            cause="Basic usage example completed",
            trigger="script_execution",
            invariant_id="G11-04",
            actor="example_script",
        )

    except Exception as e:
        print(f"\n❌ Example failed with error: {e}")
        import traceback

        traceback.print_exc()

        # Log failure
        log_causality_quick(
            cause=f"Basic usage example failed: {e}",
            trigger="script_failure",
            invariant_id="G11-07",
            actor="example_script",
        )

        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
