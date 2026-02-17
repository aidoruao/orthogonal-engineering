#!/usr/bin/env python3
"""
Example: Using Autonomous PR #18 Explorer Output
================================================

This example demonstrates how to use the JSON output from the
autonomous explorer to make decisions about repository expansion.
"""

import json
from pathlib import Path


def analyze_exploration_report(report_path: str):
    """
    Analyze the exploration report and provide insights.
    
    Args:
        report_path: Path to the JSON report file
    """
    # Load the report
    with open(report_path, 'r') as f:
        report = json.load(f)
    
    print("="*70)
    print("AUTONOMOUS PR #18 EXPLORATION REPORT ANALYSIS")
    print("="*70)
    print()
    
    # Extract key metrics
    repo_name = list(report['repos'].keys())[0]
    repo_data = report['repos'][repo_name]
    
    total_files = repo_data['exact_file_counts']['total']
    total_loc = repo_data['total_LOC']
    total_size = repo_data['total_size_bytes']
    
    print(f"Repository: {repo_name}")
    print(f"Total Files: {total_files:,}")
    print(f"Total LOC: {total_loc:,}")
    print(f"Total Size: {total_size / 1024 / 1024:.2f} MB")
    print()
    
    # Language breakdown
    print("Language Distribution:")
    print("-" * 70)
    loc_by_lang = repo_data.get('LOC_by_language', {})
    # Sort by LOC descending
    sorted_langs = sorted(loc_by_lang.items(), key=lambda x: x[1], reverse=True)
    for lang, loc in sorted_langs[:10]:  # Top 10 languages
        percentage = (loc / total_loc) * 100
        bar_length = int(percentage / 2)  # Scale to 50 chars max
        bar = '█' * bar_length
        print(f"  {lang:15} {loc:8,} LOC {percentage:5.1f}% {bar}")
    print()
    
    # Scaffolding plan
    print("Scaffolding Plan:")
    print("-" * 70)
    plan = report['scaffolding_plan']
    print(f"  Current LOC: {plan['current_LOC']:,}")
    print(f"  Target LOC:  {plan['target_LOC']:,}")
    print(f"  Gap:         {plan['lines_needed']:,}")
    print(f"  Strategy:    {plan['expansion_strategy']}")
    print()
    
    # Next actions
    print("Next Actions:")
    print("-" * 70)
    print(f"  {report['next_actions']}")
    print()
    
    # Top shards by LOC
    print("Top 10 Shards by LOC:")
    print("-" * 70)
    shard_map = repo_data['shard_map']
    sorted_shards = sorted(
        shard_map.items(), 
        key=lambda x: x[1]['total_loc'], 
        reverse=True
    )
    for shard_name, shard_data in sorted_shards[:10]:
        loc = shard_data['total_loc']
        file_count = shard_data['file_count']
        avg_loc = loc / file_count if file_count > 0 else 0
        print(f"  {shard_name:25} {loc:8,} LOC  {file_count:4} files  avg: {avg_loc:6.0f} LOC/file")
    print()
    
    # Dependencies summary
    print("Dependencies Summary:")
    print("-" * 70)
    deps = repo_data.get('dependencies', {})
    total_deps = sum(len(dep_list) for dep_list in deps.values())
    print(f"  Total unique dependencies: {total_deps}")
    if deps:
        print(f"  Dependency sources:")
        for source, dep_list in deps.items():
            print(f"    {source}: {len(dep_list)} dependencies")
    print()
    
    # Recommendations
    print("Recommendations:")
    print("-" * 70)
    
    if plan['lines_needed'] > 0:
        print(f"  • Expand codebase by {plan['lines_needed']:,} LOC")
        if 'files_to_add' in plan:
            print(f"  • Suggested file additions:")
            for path, lines in plan['files_to_add'].items():
                print(f"    - {path}: ~{lines:,} LOC")
    elif total_loc > plan['target_LOC'] * 1.1:
        print(f"  • Consider refactoring or splitting large modules")
        print(f"  • Current LOC ({total_loc:,}) exceeds target by {total_loc - plan['target_LOC']:,}")
    else:
        print(f"  • LOC target achieved! Repository is ready for PR generation")
    
    print()
    print("="*70)
    
    # Verification status
    print(f"\nVerification Compatible: {report.get('verification_compatible', False)}")
    print(f"Shard Parallelizable: {report.get('shard_parallelizable', False)}")
    print(f"Deterministic: {report.get('deterministic', False)}")
    print(f"Timestamp: {report.get('timestamp', 'N/A')}")


def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python example_usage.py <report.json>")
        print("\nExample:")
        print("  python autonomous_pr18_explorer.py --output report.json")
        print("  python example_usage.py report.json")
        sys.exit(1)
    
    report_path = sys.argv[1]
    
    if not Path(report_path).exists():
        print(f"Error: Report file not found: {report_path}")
        sys.exit(1)
    
    analyze_exploration_report(report_path)


if __name__ == '__main__':
    main()
