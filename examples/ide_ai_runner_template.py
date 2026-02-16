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
        default=r'C:\Users\Aidor\Downloads\ai_exports',
        help='Vault directory containing AI exports (default: C:\\Users\\Aidor\\Downloads\\ai_exports)'
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
