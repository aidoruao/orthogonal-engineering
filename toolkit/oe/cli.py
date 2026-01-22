"""
Orthogonal Engineering CLI - Unified command-line interface

Implements G11-01: Unified CLI exists (/toolkit/oe/cli.py)
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .evidence_store import EvidenceStore


def log_causality_metadata(
    cause: str, trigger: str, invariant_id: str, actor: str = "cli"
) -> Dict[str, Any]:
    """
    Log causality metadata as required by G11-06.

    Args:
        cause: Reason for change
        trigger: Invariant or event ID
        invariant_id: G11-XX invariant identifier
        actor: human, cli, zed_ai, etc.

    Returns:
        Dictionary with causality metadata
    """
    metadata = {
        "cause": cause,
        "trigger": trigger,
        "invariant_id": invariant_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "actor": actor,
    }

    # Log to evidence store
    evidence_store = EvidenceStore()
    evidence_store.log_causality(metadata)

    # Also write to file for immediate access
    logs_dir = Path("logs/causality")
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_file = (
        logs_dir / f"causality_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(log_file, "w") as f:
        json.dump(metadata, f, indent=2)

    return metadata


def verify_blueprint_compliance() -> int:
    """
    Verify repository compliance with ORTHOGONAL_TOOLKIT_BLUEPRINT_v1.0.html

    Returns:
        Exit code: 0 for compliance, 2 for violations
    """
    import sys
    from pathlib import Path

    # Add project root to path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

    from automation.run_full_audit_with_trace import run_full_audit_with_trace

    try:
        # Check if blueprint exists
        blueprint_path = Path("glass-box/ORTHOGONAL_TOOLKIT_BLUEPRINT_v1.0.html")
        if not blueprint_path.exists():
            print(
                "[X] Blueprint not found: glass-box/ORTHOGONAL_TOOLKIT_BLUEPRINT_v1.0.html"
            )
            return 2

        # Check required artifacts
        required_artifacts = [
            "toolkit/oe/__init__.py",
            "toolkit/oe/cli.py",
            "toolkit/oe/evidence_store.py",
            "workflows/",
            "ontology/failure_ontology.yaml",
            "ontology/failure_ontology.owl",
            "examples/",
            "glass-box/index.html",
        ]

        violations = []
        for artifact in required_artifacts:
            if artifact.endswith("/"):
                # Directory
                if not Path(artifact).exists():
                    violations.append(f"Missing directory: {artifact}")
            else:
                # File
                if not Path(artifact).exists():
                    violations.append(f"Missing file: {artifact}")

        if violations:
            print("[X] Blueprint violations detected:")
            for violation in violations:
                print(f"  - {violation}")

            # Log causality metadata for violation
            log_causality_metadata(
                cause="Blueprint verification failed",
                trigger="G11-10 verification",
                invariant_id="G11-10",
                actor="cli",
            )
            return 2

        print("[OK] Blueprint compliance verified")

        # Also run full audit
        print("\nRunning full audit with trace...")
        return run_full_audit_with_trace()

    except Exception as e:
        print(f"[!] Verification error: {e}")
        return 2


def generate_missing_artifacts() -> int:
    """
    Generate missing artifacts as per blueprint requirements.

    Returns:
        Exit code: 0 for success, 2 for failure
    """
    try:
        # Log causality
        log_causality_metadata(
            cause="Generate missing artifacts",
            trigger="Blueprint Section B",
            invariant_id="G11-04",
            actor="cli",
        )

        # Create example files if directory is empty
        examples_dir = Path("examples")
        if examples_dir.exists() and not any(examples_dir.iterdir()):
            # Create basic example
            example_file = examples_dir / "basic_usage.py"
            example_file.write_text("""
# Orthogonal Engineering Basic Usage Example

from toolkit.oe import EvidenceStore

# Create evidence store
store = EvidenceStore()

# Log some evidence
store.log_evidence(
    evidence_type="test_result",
    content={"test": "passed", "score": 100},
    source="example_test"
)

print("Example completed successfully")
""")
            print(f"[OK] Created example: {example_file}")

        # Create workflows if empty
        workflows_dir = Path("workflows")
        if workflows_dir.exists() and not any(workflows_dir.iterdir()):
            # Create basic workflow
            workflow_file = workflows_dir / "basic_validation.yaml"
            workflow_file.write_text("""
# Basic Validation Workflow
name: basic_validation
version: 1.0
description: Basic validation workflow for Orthogonal Engineering

steps:
  - name: verify_structure
    action: verify_blueprint_compliance
    timeout: 30

  - name: generate_trace
    action: generate_trace
    requires: verify_structure

  - name: verify_hashes
    action: verify_sha256_manifest
    requires: generate_trace
""")
            print(f"[OK] Created workflow: {workflow_file}")

        # Create ontology files if missing
        ontology_dir = Path("ontology")
        ontology_dir.mkdir(exist_ok=True)

        # Create YAML ontology if missing
        yaml_ontology = ontology_dir / "failure_ontology.yaml"
        if not yaml_ontology.exists():
            yaml_ontology.write_text("""
# Failure Ontology - YAML version
failure_types:
  - name: boundary_violation
    description: Violation of glass-box boundary
    severity: critical

  - name: missing_artifact
    description: Required artifact not found
    severity: high

  - name: causality_metadata_missing
    description: Missing causality logging
    severity: high

  - name: invariant_failure
    description: Atomic invariant not satisfied
    severity: critical
""")
            print(f"[OK] Created ontology: {yaml_ontology}")

        # Create OWL ontology if missing
        owl_ontology = ontology_dir / "failure_ontology.owl"
        if not owl_ontology.exists():
            owl_ontology.write_text("""<?xml version="1.0"?>
<rdf:RDF xmlns="http://www.orthogonal-engineering.org/ontology/failure#"
     xml:base="http://www.orthogonal-engineering.org/ontology/failure"
     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
     xmlns:owl="http://www.w3.org/2002/07/owl#"
     xmlns:xml="http://www.w3.org/XML/1998/namespace"
     xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
     xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
    <owl:Ontology rdf:about="http://www.orthogonal-engineering.org/ontology/failure"/>

    <owl:Class rdf:about="http://www.orthogonal-engineering.org/ontology/failure#BoundaryViolation">
        <rdfs:label>Boundary Violation</rdfs:label>
        <rdfs:comment>Violation of glass-box boundary</rdfs:comment>
    </owl:Class>

    <owl:Class rdf:about="http://www.orthogonal-engineering.org/ontology/failure#MissingArtifact">
        <rdfs:label>Missing Artifact</rdfs:label>
        <rdfs:comment>Required artifact not found</rdfs:comment>
    </owl:Class>
</rdf:RDF>""")
            print(f"[OK] Created ontology: {owl_ontology}")

        # Create glass-box index if missing
        glassbox_index = Path("glass-box/index.html")
        if not glassbox_index.exists():
            glassbox_index.write_text("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Glass-Box Boundary Dashboard</title>
    <style>
        body { font-family: monospace; margin: 2rem; }
        .ok { color: green; }
        .fail { color: red; }
        .warning { color: orange; }
    </style>
</head>
<body>
    <h1>Glass-Box Boundary Dashboard</h1>
    <p>This directory contains authoritative blueprints and boundary definitions.</p>

    <h2>Available Blueprints</h2>
    <ul>
        <li><a href="ORTHOGONAL_TOOLKIT_BLUEPRINT_v1.0.html">ORTHOGONAL_TOOLKIT_BLUEPRINT_v1.0.html</a> - Phase 11 Toolkit Blueprint</li>
    </ul>

    <h2>Verification Status</h2>
    <div id="status">Run verification to check status...</div>

    <script>
        // Simple status checker
        fetch('/api/verify')
            .then(response => response.json())
            .then(data => {
                const statusDiv = document.getElementById('status');
                if (data.compliant) {
                    statusDiv.innerHTML = '<span class="ok">✅ All blueprints compliant</span>';
                } else {
                    statusDiv.innerHTML = '<span class="fail">❌ Violations detected</span>';
                }
            })
            .catch(error => {
                document.getElementById('status').innerHTML =
                    '<span class="warning">⚠️ Status check failed: ' + error + '</span>';
            });
    </script>
</body>
</html>""")
            print(f"[OK] Created glass-box index: {glassbox_index}")

        return 0

    except Exception as e:
        print(f"[X] Failed to generate artifacts: {e}")
        return 2


def main() -> None:
    """
    Main CLI entry point.
    """
    parser = argparse.ArgumentParser(
        description="Orthogonal Engineering Toolkit CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  oe verify           Verify blueprint compliance
  oe generate         Generate missing artifacts
  oe audit            Run full audit with trace
  oe --help           Show this help message
        """,
    )

    parser.add_argument(
        "command",
        nargs="?",
        default="verify",
        choices=["verify", "generate", "audit", "help"],
        help="Command to execute",
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Set up logging
    import logging

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(message)s")

    # Execute command
    exit_code = 0

    if args.command == "verify":
        exit_code = verify_blueprint_compliance()
    elif args.command == "generate":
        exit_code = generate_missing_artifacts()
    elif args.command == "audit":
        from pathlib import Path

        # Add project root to path
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))

        from automation.run_full_audit_with_trace import run_full_audit_with_trace

        exit_code = run_full_audit_with_trace()
    elif args.command == "help":
        parser.print_help()
        exit_code = 0

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
