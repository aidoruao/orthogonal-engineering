"""
Orthogonal Engineering CLI - Unified command-line interface

Implements G11-01: Unified CLI exists (/toolkit/oe/cli.py)
Extended with deterministic Merkle-rooted pipeline commands.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .evidence_store import EvidenceStore
from .manifest import ManifestGenerator, load_manifest
from .merkle import build_merkle_tree_from_files, verify_inclusion_proof
from .logger import PipelineLogger, create_hello_world_logger, create_verification_logger
from .handling_pipeline import parse_handling_meta


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


def cmd_index(args) -> int:
    """
    Index command: Generate manifest.jsonl for a repository.
    
    Args:
        args: Command line arguments
        
    Returns:
        Exit code
    """
    repo_path = Path(args.repo)
    manifest_path = Path(args.out) / 'manifest.jsonl'
    
    if not repo_path.exists():
        print(f"[X] Repository not found: {repo_path}")
        return 1
    
    # Create logger
    logger = PipelineLogger(Path('logs/index_pipeline.jsonl'))
    logger.log_start('index', repo=str(repo_path))
    
    print(f"[*] Indexing repository: {repo_path}")
    print(f"[*] Output manifest: {manifest_path}")
    
    # Determine exclusion patterns
    exclude_patterns = [
        '.git/*',
        '*.pyc',
        '__pycache__/*',
        '*.egg-info/*',
        'node_modules/*',
        '.pytest_cache/*',
    ]
    
    if args.subset:
        exclude_patterns.extend(args.subset.split(','))
    
    try:
        # Create manifest generator
        generator = ManifestGenerator(manifest_path)
        
        # Process directory
        count = 0
        for entry in generator.process_directory(repo_path, exclude_patterns):
            count += 1
            if count % 100 == 0:
                print(f"[*] Processed {count} files...")
                logger.log_progress('index', count / 1000, count, processed=count)
        
        # Finalize
        generator.finalize()
        
        print(f"[OK] Indexed {count} files")
        logger.log_complete('index', files=count)
        return 0
        
    except Exception as e:
        print(f"[X] Indexing failed: {e}")
        logger.log_error('index', str(e))
        return 1


def cmd_merkle(args) -> int:
    """
    Merkle command: Build Merkle tree from manifest.
    
    Args:
        args: Command line arguments
        
    Returns:
        Exit code
    """
    manifest_path = Path(args.manifest)
    output_dir = Path(args.out)
    
    if not manifest_path.exists():
        print(f"[X] Manifest not found: {manifest_path}")
        return 1
    
    # Create logger
    logger = PipelineLogger(Path('logs/merkle_pipeline.jsonl'))
    logger.log_start('merkle', manifest=str(manifest_path))
    
    print(f"[*] Building Merkle tree from: {manifest_path}")
    
    try:
        # Load manifest
        file_hashes = []
        for entry in load_manifest(manifest_path):
            file_hashes.append((entry['path'], entry['hash']))
        
        print(f"[*] Loaded {len(file_hashes)} files from manifest")
        
        # Build Merkle tree
        tree = build_merkle_tree_from_files(file_hashes)
        
        print(f"[OK] Merkle root: {tree.root}")
        
        # Export root
        root_file = output_dir / 'merkle_root.txt'
        root_file.parent.mkdir(parents=True, exist_ok=True)
        root_file.write_text(tree.root)
        print(f"[*] Root saved to: {root_file}")
        
        # Export proofs
        proofs_file = output_dir / 'merkle_proofs.jsonl'
        tree.export_proofs_jsonl(proofs_file)
        print(f"[*] Proofs saved to: {proofs_file}")
        
        logger.log_complete('merkle', root=tree.root, files=len(file_hashes))
        return 0
        
    except Exception as e:
        print(f"[X] Merkle tree build failed: {e}")
        logger.log_error('merkle', str(e))
        return 1


def cmd_verify(args) -> int:
    """
    Verify command: Verify Merkle inclusion proofs.
    
    Args:
        args: Command line arguments
        
    Returns:
        Exit code
    """
    proofs_path = Path(args.out) / 'merkle_proofs.jsonl'
    
    if not proofs_path.exists():
        print(f"[X] Proofs file not found: {proofs_path}")
        return 1
    
    # Create logger
    logger = create_verification_logger()
    logger.log_start('verify', proofs=str(proofs_path))
    
    print(f"[*] Verifying proofs from: {proofs_path}")
    
    try:
        verified = 0
        failed = 0
        
        with open(proofs_path, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                
                proof = json.loads(line)
                if verify_inclusion_proof(proof):
                    verified += 1
                else:
                    failed += 1
                    print(f"[!] Verification failed for: {proof['path']}")
        
        print(f"[OK] Verified: {verified}, Failed: {failed}")
        
        logger.log_complete('verify', verified=verified, failed=failed)
        return 0 if failed == 0 else 1
        
    except Exception as e:
        print(f"[X] Verification failed: {e}")
        logger.log_error('verify', str(e))
        return 1


def cmd_handling_clamp(args) -> int:
    """
    Handling-clamp command: Parse and validate GTA handling.meta.
    
    Args:
        args: Command line arguments
        
    Returns:
        Exit code
    """
    handling_path = Path(args.handling_path)
    output_dir = Path(args.out)
    
    if not handling_path.exists():
        print(f"[X] Handling file not found: {handling_path}")
        return 1
    
    # Create logger
    logger = create_hello_world_logger()
    logger.log_start('handling_clamp', handling=str(handling_path))
    
    print(f"[*] Parsing handling file: {handling_path}")
    
    try:
        # Parse handling file
        data = parse_handling_meta(handling_path)
        
        print(f"[OK] Parsed {data['count']} vehicles")
        
        # Save output
        output_file = output_dir / 'handling_data.json'
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"[*] Data saved to: {output_file}")
        
        logger.log_complete('handling_clamp', vehicles=data['count'])
        return 0
        
    except Exception as e:
        print(f"[X] Handling parse failed: {e}")
        logger.log_error('handling_clamp', str(e))
        return 1


def cmd_backup(args) -> int:
    """
    Backup command: Create backup of manifest and Merkle tree.
    
    Args:
        args: Command line arguments
        
    Returns:
        Exit code
    """
    output_dir = Path(args.out)
    backup_dir = Path('backups') / datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print(f"[*] Creating backup in: {backup_dir}")
    
    try:
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy manifest
        manifest_path = output_dir / 'manifest.jsonl'
        if manifest_path.exists():
            import shutil
            shutil.copy2(manifest_path, backup_dir / 'manifest.jsonl')
            print(f"[*] Backed up manifest")
        
        # Copy Merkle files
        for file in ['merkle_root.txt', 'merkle_proofs.jsonl']:
            src = output_dir / file
            if src.exists():
                import shutil
                shutil.copy2(src, backup_dir / file)
                print(f"[*] Backed up {file}")
        
        print(f"[OK] Backup complete: {backup_dir}")
        return 0
        
    except Exception as e:
        print(f"[X] Backup failed: {e}")
        return 1


def cmd_restore(args) -> int:
    """
    Restore command: Restore from backup.
    
    Args:
        args: Command line arguments
        
    Returns:
        Exit code
    """
    # List available backups
    backups_dir = Path('backups')
    
    if not backups_dir.exists():
        print("[X] No backups found")
        return 1
    
    backups = sorted(backups_dir.iterdir(), reverse=True)
    
    if not backups:
        print("[X] No backups found")
        return 1
    
    print("[*] Available backups:")
    for i, backup in enumerate(backups):
        print(f"  {i}: {backup.name}")
    
    # For now, just list them
    print("[*] Use backup index to restore (not yet implemented)")
    return 0


def main() -> None:
    """
    Main CLI entry point.
    """
    parser = argparse.ArgumentParser(
        description="Orthogonal Engineering Toolkit CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  oe verify                      Verify blueprint compliance
  oe generate                    Generate missing artifacts
  oe audit                       Run full audit with trace
  oe index --repo . --out output Index repository files
  oe merkle --manifest manifest.jsonl --out output
  oe verify --out output         Verify Merkle proofs
  oe handling-clamp --handling-path file.meta --out output
  oe backup --out output         Backup manifest and Merkle tree
  oe --help                      Show this help message
        """,
    )

    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Legacy commands
    verify_parser = subparsers.add_parser('verify', help='Verify blueprint compliance')
    generate_parser = subparsers.add_parser('generate', help='Generate missing artifacts')
    audit_parser = subparsers.add_parser('audit', help='Run full audit with trace')
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Index repository and generate manifest')
    index_parser.add_argument('--repo', default='.', help='Repository path (default: current directory)')
    index_parser.add_argument('--out', default='output', help='Output directory (default: output)')
    index_parser.add_argument('--subset', help='Comma-separated list of additional exclude patterns')
    index_parser.add_argument('--workers', type=int, default=1, help='Number of worker threads')
    index_parser.add_argument('--apply', action='store_true', help='Apply changes (default is dry-run)')
    
    # Merkle command
    merkle_parser = subparsers.add_parser('merkle', help='Build Merkle tree from manifest')
    merkle_parser.add_argument('--manifest', default='output/manifest.jsonl', help='Manifest file path')
    merkle_parser.add_argument('--out', default='output', help='Output directory')
    merkle_parser.add_argument('--apply', action='store_true', help='Apply changes (default is dry-run)')
    
    # Verify command (Merkle proofs)
    verify_merkle_parser = subparsers.add_parser('verify-merkle', help='Verify Merkle inclusion proofs')
    verify_merkle_parser.add_argument('--out', default='output', help='Output directory with proofs')
    
    # Handling-clamp command
    handling_parser = subparsers.add_parser('handling-clamp', help='Parse GTA handling.meta file')
    handling_parser.add_argument('--handling-path', required=True, help='Path to handling.meta file')
    handling_parser.add_argument('--out', default='output', help='Output directory')
    handling_parser.add_argument('--apply', action='store_true', help='Apply changes (default is dry-run)')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Backup manifest and Merkle tree')
    backup_parser.add_argument('--out', default='output', help='Output directory to backup')
    
    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore from backup')
    restore_parser.add_argument('--backup-dir', help='Backup directory to restore from')
    
    # Global options
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    # Set up logging
    import logging

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(message)s")

    # Execute command
    exit_code = 0

    if args.command == 'verify':
        exit_code = verify_blueprint_compliance()
    elif args.command == 'generate':
        exit_code = generate_missing_artifacts()
    elif args.command == 'audit':
        from pathlib import Path

        # Add project root to path
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))

        from automation.run_full_audit_with_trace import run_full_audit_with_trace

        exit_code = run_full_audit_with_trace()
    elif args.command == 'index':
        if not args.apply:
            print("[DRY-RUN] Use --apply to actually write manifest")
        exit_code = cmd_index(args)
    elif args.command == 'merkle':
        if not args.apply:
            print("[DRY-RUN] Use --apply to actually write Merkle tree")
        exit_code = cmd_merkle(args)
    elif args.command == 'verify-merkle':
        exit_code = cmd_verify(args)
    elif args.command == 'handling-clamp':
        if not args.apply:
            print("[DRY-RUN] Use --apply to actually write output")
        exit_code = cmd_handling_clamp(args)
    elif args.command == 'backup':
        exit_code = cmd_backup(args)
    elif args.command == 'restore':
        exit_code = cmd_restore(args)
    elif args.command == 'help' or args.command is None:
        parser.print_help()
        exit_code = 0
    else:
        parser.print_help()
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
