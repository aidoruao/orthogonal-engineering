#!/usr/bin/env python3
"""
IDE AI Runner Template for AlphaOmegaFinalizer

This template demonstrates a complete dry-run workflow for IDE AI systems.
It runs the finalizer, executes tests, computes manifest hashes, and generates
an AI run report.

SAFETY: Default mode is DRY-RUN. Use --apply flag to switch to apply mode.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return the result."""
    print(f"\n{'=' * 70}")
    print(f"{description}")
    print(f"{'=' * 70}")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result


def compute_file_hash(file_path):
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def main():
    parser = argparse.ArgumentParser(
        description='IDE AI Runner Template for AlphaOmegaFinalizer'
    )
    parser.add_argument(
        '--vault-dir',
        type=str,
        default=None,
        help='Vault directory containing AI exports (override this default with your actual path)'
    )
    parser.add_argument(
        '--out-dir',
        type=str,
        default='./outputs',
        help='Output directory (default: ./outputs)'
    )
    parser.add_argument(
        '--apply',
        action='store_true',
        help='Apply mode - actually write outputs (default: dry-run)'
    )
    
    args = parser.parse_args()
    
    # Initialize report
    report = {
        'run_timestamp': datetime.now(timezone.utc).isoformat(),
        'mode': 'apply' if args.apply else 'dry-run',
        'vault_path': args.vault_dir,
        'output_path': args.out_dir,
        'results': {},
        'warnings': [],
        'errors': [],
        'next_steps': []
    }
    
    print("=" * 70)
    print("IDE AI RUNNER - AlphaOmegaFinalizer")
    print("=" * 70)
    print(f"Timestamp: {report['run_timestamp']}")
    print(f"Mode: {report['mode'].upper()}")
    print(f"Vault: {args.vault_dir}")
    print(f"Output: {args.out_dir}")
    print("=" * 70)
    
    # Step 1: Run unit tests
    test_result = run_command(
        [sys.executable, '-m', 'pytest', 'core/tests/test_alpha_omega_finalizer.py', '-v'],
        "Step 1: Running Unit Tests"
    )
    
    report['results']['tests_passed'] = (test_result.returncode == 0)
    if test_result.returncode != 0:
        report['errors'].append('Unit tests failed')
        report['next_steps'].append('Fix failing unit tests before proceeding')
    
    # Step 2: Run finalizer
    finalizer_cmd = [
        sys.executable,
        'core/alpha_omega_finalizer.py',
        '--vault-dir', args.vault_dir,
        '--out-dir', args.out_dir
    ]
    
    if args.apply:
        finalizer_cmd.append('--apply')
        report['warnings'].append('Running in APPLY mode - files will be written')
    else:
        report['warnings'].append('Running in DRY-RUN mode - no files will be written')
    
    finalizer_result = run_command(
        finalizer_cmd,
        "Step 2: Running AlphaOmegaFinalizer"
    )
    
    report['results']['finalization_success'] = (finalizer_result.returncode == 0)
    if finalizer_result.returncode != 0:
        report['errors'].append('Finalization failed')
        report['next_steps'].append('Review finalization errors above')
    
    # Extract Merkle root from output (if successful)
    if finalizer_result.returncode == 0:
        for line in finalizer_result.stdout.split('\n'):
            if 'Merkle Root:' in line:
                merkle_root = line.split('Merkle Root:')[1].strip()
                report['results']['merkle_root'] = merkle_root
                break
    
    # Step 3: Compute manifest hash (if apply mode and files exist)
    if args.apply:
        ledger_path = Path(args.out_dir) / 'finalization_ledger.json'
        master_root_path = Path(args.out_dir) / 'master_root.txt'
        
        if ledger_path.exists():
            manifest_hash = compute_file_hash(ledger_path)
            report['results']['manifest_hash'] = manifest_hash
            print(f"\nManifest Hash (SHA-256): {manifest_hash}")
        else:
            report['errors'].append('Ledger file not found after finalization')
        
        if master_root_path.exists():
            with open(master_root_path, 'r') as f:
                master_root = f.read().strip()
            report['results']['master_root_file'] = master_root
            
            # Verify consistency
            if 'merkle_root' in report['results']:
                if master_root == report['results']['merkle_root']:
                    print(f"✓ Master root file matches Merkle root")
                    report['results']['root_consistency'] = True
                else:
                    print(f"✗ Master root file does NOT match Merkle root")
                    report['errors'].append('Root consistency check failed')
                    report['results']['root_consistency'] = False
    
    # Step 4: Verify integrity (if apply mode)
    if args.apply:
        ledger_path = Path(args.out_dir) / 'finalization_ledger.json'
        if ledger_path.exists():
            verify_result = run_command(
                [
                    sys.executable,
                    'core/alpha_omega_finalizer.py',
                    '--vault-dir', args.vault_dir,
                    '--verify', str(ledger_path)
                ],
                "Step 4: Verifying Integrity"
            )
            
            report['results']['integrity_verified'] = (verify_result.returncode == 0)
            if verify_result.returncode != 0:
                report['errors'].append('Integrity verification failed')
                report['next_steps'].append('Investigate integrity verification failure')
    
    # Generate summary
    print("\n" + "=" * 70)
    print("RUN SUMMARY")
    print("=" * 70)
    
    all_success = (
        report['results'].get('tests_passed', False) and
        report['results'].get('finalization_success', False)
    )
    
    if args.apply:
        all_success = all_success and report['results'].get('integrity_verified', False)
    
    if all_success:
        print("✓ ALL CHECKS PASSED")
    else:
        print("✗ SOME CHECKS FAILED")
    
    print(f"\nTests Passed: {'✓' if report['results'].get('tests_passed') else '✗'}")
    print(f"Finalization: {'✓' if report['results'].get('finalization_success') else '✗'}")
    
    if args.apply:
        print(f"Integrity: {'✓' if report['results'].get('integrity_verified') else '✗'}")
    
    if 'merkle_root' in report['results']:
        print(f"\nMerkle Root: {report['results']['merkle_root']}")
    
    # Add next steps
    if report['mode'] == 'dry-run' and all_success:
        report['next_steps'].extend([
            'Review Merkle root and file counts',
            'Verify reproducibility (run again and compare)',
            'Consider running with --apply if satisfied'
        ])
    
    if report['mode'] == 'apply' and all_success:
        report['next_steps'].extend([
            'Review ledger and master root files',
            'Commit outputs to repository (NOT vault files)',
            'Update documentation with Merkle root'
        ])
    
    # Write report
    report_path = Path(args.out_dir) / 'ide_ai_run_report.json'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Report written to: {report_path}")
    
    # Print warnings and next steps
    if report['warnings']:
        print("\n⚠ WARNINGS:")
        for warning in report['warnings']:
            print(f"  - {warning}")
    
    if report['errors']:
        print("\n✗ ERRORS:")
        for error in report['errors']:
            print(f"  - {error}")
    
    if report['next_steps']:
        print("\n→ NEXT STEPS:")
        for step in report['next_steps']:
            print(f"  - {step}")
    
    print("\n" + "=" * 70)
    
    # Exit with appropriate code
    sys.exit(0 if all_success else 1)


if __name__ == '__main__':
    main()
IDE AI Runner Template

This template demonstrates how to use the CAS system for IDE AI workflows.
Follows safety-first principles: dry-run default, mandatory backups, no auto-push.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backup import BackupManager
from core.alpha_omega_finalizer import AlphaOmegaFinalizer
from handling_pipeline import HandlingPipeline
from logger import get_logger
from manifest import Manifest


def main():
    """Main runner function."""
    
    # Initialize logger
    logger = get_logger("ide_ai_runner")
    logger.info("Starting IDE AI runner")
    
    # Configuration
    DRY_RUN = True  # ALWAYS start with dry-run
    # NOTE: Update this vault path to match your local environment
    VAULT_PATH = Path("C:/Users/Aidor/Downloads/ai_exports")  # Example local-only vault
    
    # Example files to process (adjust as needed)
    source_files = [
        "example_file1.txt",
        "example_file2.py",
    ]
    
    # Step 1: Initialize components
    logger.info("Initializing components")
    pipeline = HandlingPipeline(dry_run=DRY_RUN)
    backup_manager = BackupManager()
    finalizer = AlphaOmegaFinalizer(name="ide_ai_session")
    
    # Step 2: Alpha phase - Capture initial state
    logger.info("Alpha phase: Capturing initial state")
    existing_files = [f for f in source_files if Path(f).exists()]
    
    if not existing_files:
        logger.warning("No existing files found to process")
        return
    
    finalizer.alpha(
        existing_files,
        metadata={
            "session": "ide_ai_runner",
            "dry_run": DRY_RUN,
            "vault_path": str(VAULT_PATH)
        }
    )
    
    # Step 3: Create manifest before processing
    logger.info("Creating manifest")
    manifest = Manifest(name="ide_ai_session")
    for filepath in existing_files:
        manifest.add_entry(filepath)
    
    manifest_path = Path("manifests/ide_ai_session_manifest.json")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest.save(manifest_path)
    logger.info(f"Manifest saved to {manifest_path}")
    
    # Step 4: Process files through pipeline
    logger.info(f"Processing {len(existing_files)} files (dry_run={DRY_RUN})")
    results = []
    
    for filepath in existing_files:
        try:
            result = pipeline.process_file(filepath, create_backup=True)
            results.append(result)
            
            # Log result
            status = "✓" if all(
                s.get("status") in ["success", "skipped"]
                for s in result.get("stages", {}).values()
            ) else "✗"
            
            logger.info(f"{status} Processed: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to process {filepath}: {e}")
            results.append({"filepath": str(filepath), "error": str(e)})
    
    # Step 5: Omega phase - Verify final state
    logger.info("Omega phase: Verifying final state")
    omega_result = finalizer.omega(verify=True)
    
    if omega_result["verification"]["verified"]:
        logger.info("✓ Verification PASSED - Files unchanged (as expected in dry-run)")
    else:
        logger.error("✗ Verification FAILED")
        logger.error(f"Issues: {omega_result['verification']['issues']}")
    
    # Step 6: Save finalization report
    report_path = Path("reports/ide_ai_session_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    finalizer.save_report(report_path)
    logger.info(f"Finalization report saved to {report_path}")
    
    # Step 7: Summary
    logger.info("=" * 60)
    logger.info("Session Summary:")
    logger.info(f"  Mode: {'DRY-RUN' if DRY_RUN else 'LIVE'}")
    logger.info(f"  Files processed: {len(results)}")
    logger.info(f"  Verification: {'PASSED' if omega_result['verification']['verified'] else 'FAILED'}")
    logger.info(f"  Manifest: {manifest_path}")
    logger.info(f"  Report: {report_path}")
    
    if DRY_RUN:
        logger.info("")
        logger.info("To run in LIVE mode:")
        logger.info("  1. Review dry-run results")
        logger.info("  2. Set DRY_RUN = False")
        logger.info("  3. Re-run this script")
        logger.info("  WARNING: Live mode creates backups and modifies files")
    
    logger.info("=" * 60)


def example_usage_patterns():
    """
    Example usage patterns for common scenarios.
    
    This function is not executed - it's here for documentation.
    """
    
    # Pattern 1: Simple file hashing
    from hasher import hash_file
    file_hash = hash_file("myfile.txt")
    print(f"Hash: {file_hash}")
    
    # Pattern 2: Create backup before modification
    from backup import BackupManager
    bm = BackupManager()
    backup_path = bm.create_backup("important.txt")
    # Now safe to modify important.txt
    
    # Pattern 3: Verify file integrity
    from manifest import Manifest
    manifest = Manifest.load("manifest.json")
    verification = manifest.verify()
    if verification["verified"]:
        print("All files verified!")
    
    # Pattern 4: Alpha-Omega verification for critical operations
    from core.alpha_omega_finalizer import AlphaOmegaFinalizer
    finalizer = AlphaOmegaFinalizer(name="critical")
    finalizer.alpha(["file1.txt", "file2.txt"])
    # ... perform operations ...
    result = finalizer.omega(verify=True)
    if not result["verification"]["verified"]:
        print("ERROR: Verification failed!")
IDE AI Runner Template (Python)

Example script for running deterministic pipeline operations.

IMPORTANT: This is a TEMPLATE. Customize paths and parameters for your use.

Usage: python ide_ai_runner_template.py
"""

import subprocess
import sys
from pathlib import Path


# Configuration - CUSTOMIZE THESE
REPO_PATH = Path("/path/to/your/repository")
VAULT_PATH = Path("/home/yourname/your_vault")  # NOT the example path!
OUTPUT_DIR = Path("./pipeline_output")


def run_command(cmd, description, check=True):
    """Run a command and display output."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(map(str, cmd))}\n")
    
    result = subprocess.run(cmd, check=check)
    return result.returncode == 0


def main():
    """Main pipeline execution."""
    print("Deterministic Pipeline Runner")
    print("=" * 60)
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Index Repository (Dry-Run)
    success = run_command(
        ["python", "cli.py", "index", 
         "--repo", str(REPO_PATH),
         "--out", str(OUTPUT_DIR / "manifest.jsonl")],
        "[1/5] Indexing repository (dry-run)"
    )
    
    if not success:
        print("Dry-run failed. Aborting.")
        return 1
    
    # Pause for review
    input("\nReview the output above. Press Enter to continue with actual indexing, or Ctrl+C to abort: ")
    
    # Step 2: Index Repository (Apply)
    success = run_command(
        ["python", "cli.py", "index",
         "--repo", str(REPO_PATH),
         "--out", str(OUTPUT_DIR / "manifest.jsonl"),
         "--apply"],
        "[2/5] Indexing repository (apply)"
    )
    
    if not success:
        print("Indexing failed. Aborting.")
        return 1
    
    # Step 3: Build Merkle Tree
    success = run_command(
        ["python", "cli.py", "merkle",
         "--manifest", str(OUTPUT_DIR / "manifest.jsonl"),
         "--apply"],
        "[3/5] Building Merkle tree"
    )
    
    if not success:
        print("Merkle tree building failed. Continuing anyway...")
    
    # Step 4: Verify Proofs
    proofs_file = OUTPUT_DIR / "merkle_proofs.jsonl"
    if proofs_file.exists():
        run_command(
            ["python", "cli.py", "verify",
             "--manifest", str(proofs_file)],
            "[4/5] Verifying Merkle proofs",
            check=False
        )
    
    # Step 5: Finalize Vault (if exists)
    if VAULT_PATH.exists():
        run_command(
            ["python", "core/alpha_omega_finalizer.py",
             "--vault-dir", str(VAULT_PATH),
             "--apply"],
            "[5/5] Finalizing vault",
            check=False
        )
    else:
        print(f"\n[5/5] Vault path does not exist, skipping finalization")
        print(f"      Vault path: {VAULT_PATH}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Pipeline execution complete!")
    print("=" * 60)
    print(f"Outputs in: {OUTPUT_DIR}")
    print(f"Logs in: ./logs/")
    
    # Display file counts
    manifest_file = OUTPUT_DIR / "manifest.jsonl"
    if manifest_file.exists():
        with open(manifest_file, 'r') as f:
            line_count = sum(1 for _ in f)
        print(f"\nManifest entries: {line_count}")
    
    if proofs_file.exists():
        with open(proofs_file, 'r') as f:
            proof_count = sum(1 for _ in f)
        print(f"Merkle proofs: {proof_count}")
    
    print("\nReview logs in ./logs/ for detailed operation history")
    
    return 0


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger = get_logger("ide_ai_runner")
        logger.error(f"Unexpected error: {e}")
        raise
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)
