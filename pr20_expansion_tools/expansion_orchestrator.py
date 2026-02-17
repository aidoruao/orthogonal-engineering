#!/usr/bin/env python3
"""
PR #20 Expansion Orchestrator

Main entry point for the PR #20 deterministic expansion to 1B LOC.
Coordinates all tools and manages the complete expansion workflow.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from shard_generator.shard_generator import ShardGenerator
from dag_manager.dag_manager import DAGManager
from verification.verification_checker import VerificationChecker
from audit_trail.audit_trail_generator import AuditTrailGenerator
from replication_controller.replication_controller import ReplicationController


def verify_tools() -> bool:
    """Verify all tools are functional before starting expansion."""
    print("Verifying expansion tools...")
    print("="*60)
    
    tools_ok = True
    
    # Test shard generator
    try:
        generator = ShardGenerator(seed=42, output_dir='/tmp/test_pr20')
        print("✓ Shard Generator: OK")
    except Exception as e:
        print(f"✗ Shard Generator: FAILED - {str(e)}")
        tools_ok = False
    
    # Test DAG manager
    try:
        dag = DAGManager(dag_file='/tmp/test_dag.json')
        print("✓ DAG Manager: OK")
    except Exception as e:
        print(f"✗ DAG Manager: FAILED - {str(e)}")
        tools_ok = False
    
    # Test verification checker
    try:
        verifier = VerificationChecker(verification_log='/tmp/test_verification.json')
        print("✓ Verification Checker: OK")
    except Exception as e:
        print(f"✗ Verification Checker: FAILED - {str(e)}")
        tools_ok = False
    
    # Test audit trail generator
    try:
        audit = AuditTrailGenerator(audit_file='/tmp/test_audit.jsonl')
        print("✓ Audit Trail Generator: OK")
    except Exception as e:
        print(f"✗ Audit Trail Generator: FAILED - {str(e)}")
        tools_ok = False
    
    # Test replication controller
    try:
        controller = ReplicationController(target_loc=10000, seed=42, output_dir='/tmp/test_replication')
        print("✓ Replication Controller: OK")
    except Exception as e:
        print(f"✗ Replication Controller: FAILED - {str(e)}")
        tools_ok = False
    
    print("="*60)
    
    if tools_ok:
        print("✓ All tools verified and ready!")
    else:
        print("✗ Some tools failed verification. Please fix errors before proceeding.")
    
    return tools_ok


def print_banner():
    """Print PR #20 banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║               PR #20 - DETERMINISTIC EXPANSION               ║
║                    1.86M → 1B LOC Target                    ║
║                                                              ║
║   Yeshua Standards: Truth-aligned, Fully Deterministic,     ║
║   Fully Auditable, Cross-domain, Popperian, Glass-box       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def main():
    """Main orchestrator function."""
    parser = argparse.ArgumentParser(
        description='PR #20 Expansion Orchestrator - Deterministic expansion to 1B LOC',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--verify-tools', action='store_true', 
                       help='Verify all tools are functional')
    parser.add_argument('--target-loc', type=int, default=1000000000,
                       help='Target lines of code (default: 1B)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for deterministic generation (default: 42)')
    parser.add_argument('--output-dir', type=str, default='./pr20_generated',
                       help='Output directory for generated code')
    parser.add_argument('--domains', type=str, 
                       default='python,javascript,typescript,java,c,cpp,go',
                       help='Comma-separated list of domains to generate')
    parser.add_argument('--dry-run', action='store_true',
                       help='Perform dry run without creating files')
    parser.add_argument('--apply', action='store_true',
                       help='Apply changes (create files). WARNING: This will generate up to 1B LOC!')
    
    args = parser.parse_args()
    
    print_banner()
    
    # Verify tools if requested
    if args.verify_tools:
        if not verify_tools():
            sys.exit(1)
        return
    
    # Show warning for actual expansion
    if not args.dry_run and not args.apply:
        print("\n⚠️  WARNING: Default is DRY RUN mode")
        print("Use --dry-run to see what would be generated")
        print("Use --apply to actually generate files (NOT RECOMMENDED for 1B LOC!)")
        print("\nRun with --dry-run to see the expansion plan.")
        return
    
    if args.apply and not args.dry_run:
        print("\n⚠️  CRITICAL WARNING ⚠️")
        print("="*60)
        print("You are about to generate files targeting 1 BILLION LOC!")
        print(f"Target: {args.target_loc:,} lines of code")
        print(f"Output: {args.output_dir}")
        print("="*60)
        
        response = input("\nType 'YES I UNDERSTAND' to proceed: ")
        if response != "YES I UNDERSTAND":
            print("Expansion cancelled.")
            return
    
    # Parse domains
    domains = [d.strip() for d in args.domains.split(',')]
    
    # Create replication controller
    controller = ReplicationController(
        target_loc=args.target_loc,
        seed=args.seed,
        output_dir=args.output_dir
    )
    
    # Run expansion
    result = controller.expand_to_target(
        domains=domains,
        dry_run=args.dry_run
    )
    
    # Print results
    print("\n" + "="*60)
    print("EXPANSION SUMMARY")
    print("="*60)
    print(json.dumps(result, indent=2))
    print("="*60)


if __name__ == '__main__':
    main()
