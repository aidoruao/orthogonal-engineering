#!/usr/bin/env python3
"""
Complete PR #18 Workflow Demonstration
======================================

Demonstrates the full autonomous workflow from exploration to execution.
"""

import json
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and display output."""
    print(f"\n{'='*70}")
    print(f"{description}")
    print(f"{'='*70}")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print output
    if result.stdout:
        for line in result.stdout.split('\n')[:30]:  # First 30 lines
            print(line)
        if len(result.stdout.split('\n')) > 30:
            print(f"... ({len(result.stdout.split('\n')) - 30} more lines)")
    
    if result.returncode != 0:
        print(f"\nError (exit code {result.returncode}):")
        print(result.stderr)
        return False
    
    return True


def analyze_report(report_path):
    """Analyze and display report summary."""
    print(f"\n{'='*70}")
    print("REPORT ANALYSIS")
    print(f"{'='*70}\n")
    
    with open(report_path, 'r') as f:
        report = json.load(f)
    
    repo_data = report['repos']['orthogonal-engineering']
    
    print(f"Repository: orthogonal-engineering")
    print(f"Total Files: {repo_data['exact_file_counts']['total']:,}")
    print(f"Total LOC: {repo_data['total_LOC']:,}")
    print(f"Total Shards: {len(repo_data['shard_map']):,}")
    print(f"Dependencies: {sum(len(d) for d in repo_data.get('dependencies', {}).values())}")
    
    print(f"\nScaffolding Plan:")
    plan = report['scaffolding_plan']
    print(f"  Current LOC: {plan['current_LOC']:,}")
    print(f"  Target LOC: {plan['target_LOC']:,}")
    print(f"  Gap: {plan['lines_needed']:,}")
    print(f"  Strategy: {plan['expansion_strategy']}")
    
    print(f"\nTop 5 Shards by LOC:")
    shard_map = repo_data['shard_map']
    sorted_shards = sorted(
        shard_map.items(),
        key=lambda x: x[1]['total_loc'],
        reverse=True
    )
    for shard_name, shard_data in sorted_shards[:5]:
        print(f"  {shard_name:20} {shard_data['total_loc']:8,} LOC")


def main():
    """Run the complete demonstration."""
    print("="*70)
    print("PR #18 COMPLETE WORKFLOW DEMONSTRATION")
    print("="*70)
    print("\nThis demonstration shows the full autonomous workflow:")
    print("1. Autonomous exploration")
    print("2. Report analysis")
    print("3. Task-agent dry-run")
    print("4. Task-agent execution (simulated)")
    print()
    
    repo_root = Path(__file__).parent.parent  # Go up to repo root
    output_dir = Path("/tmp/pr18_demo")
    output_dir.mkdir(exist_ok=True)
    
    report_path = output_dir / "exploration_report.json"
    
    # Step 1: Run autonomous explorer
    if not run_command(
        ["python", str(repo_root / "autonomous_pr18_explorer.py"), 
         "--output", str(report_path)],
        "STEP 1: Running Autonomous Explorer"
    ):
        print("Failed to run autonomous explorer")
        return 1
    
    # Step 2: Analyze report
    analyze_report(report_path)
    
    # Step 3: Run task-agent in dry-run mode
    if not run_command(
        ["python", str(repo_root / "pr18_task_agent.py"),
         str(report_path), "--dry-run"],
        "STEP 2: Running Task-Agent (Dry-Run)"
    ):
        print("Failed to run task-agent dry-run")
        return 1
    
    # Step 4: Run task-agent with limited cycles (simulation)
    print(f"\n{'='*70}")
    print("STEP 3: Running Task-Agent (Simulation - 1 Cycle)")
    print(f"{'='*70}")
    print("\nNote: This is a simulation. In production, this would:")
    print("  - Generate actual code files")
    print("  - Perform real refactoring")
    print("  - Update all SHA-256 hashes")
    print("  - Create comprehensive tests")
    print()
    
    if not run_command(
        ["python", str(repo_root / "pr18_task_agent.py"),
         str(report_path), "--max-cycles", "1"],
        "Task-Agent Execution (Simulated)"
    ):
        print("Failed to run task-agent execution")
        return 1
    
    # Show generated files
    print(f"\n{'='*70}")
    print("GENERATED FILES")
    print(f"{'='*70}\n")
    
    for file in output_dir.glob("*.json"):
        size = file.stat().st_size
        print(f"  {file.name:40} {size:10,} bytes")
    
    # Final summary
    print(f"\n{'='*70}")
    print("DEMONSTRATION COMPLETE")
    print(f"{'='*70}\n")
    
    print("The PR #18 autonomous workflow successfully:")
    print("  ✓ Explored the repository")
    print("  ✓ Analyzed shard requirements")
    print("  ✓ Determined actions for each shard")
    print("  ✓ Simulated execution")
    print("  ✓ Generated execution reports")
    print("  ✓ Prepared for final indexing")
    print()
    print(f"All output files saved to: {output_dir}")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
