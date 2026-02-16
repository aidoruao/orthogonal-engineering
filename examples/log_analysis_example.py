#!/usr/bin/env python3
"""
Log Analysis Example: Pattern Discovery from Pipeline Audit Logs

This script demonstrates how to analyze JSONL audit logs produced by PIPELINE_LOGGER.py
to discover common parameter change patterns and relationships.

This is a simple analytics demo, not an autonomous refactor tool.
It operates in read-only mode and produces a summary of discovered patterns.

Usage:
    python examples/log_analysis_example.py

Output:
    examples/log_analysis_summary.txt - Summary of discovered patterns
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Non-destructive operation: read-only analysis
DRY_RUN_MODE = True


def read_jsonl_logs(log_file_path):
    """
    Read JSONL log file and return list of parsed entries.
    
    Args:
        log_file_path: Path to JSONL log file
    
    Returns:
        List of dictionaries, one per log entry
    """
    entries = []
    
    if not Path(log_file_path).exists():
        print(f"⚠️  Log file not found: {log_file_path}")
        print(f"ℹ️  Creating sample log file for demonstration...")
        create_sample_log(log_file_path)
    
    try:
        with open(log_file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    entries.append(entry)
                except json.JSONDecodeError as e:
                    print(f"⚠️  Skipping invalid JSON at line {line_num}: {e}")
                    continue
    except Exception as e:
        print(f"❌ Error reading log file: {e}")
        return []
    
    return entries


def create_sample_log(log_file_path):
    """Create a sample log file for demonstration purposes."""
    sample_entries = [
        {
            "timestamp": "2026-01-15T10:30:00Z",
            "action": "parameter_change",
            "file": "src/physics/vehicle.py",
            "function": "update_vehicle_properties",
            "parameters": {
                "fMass": {"old": 1500.0, "new": 1800.0},
                "fDriveInertia": {"old": 2.5, "new": 3.0}
            },
            "actor": "manual_update",
            "commit": "abc123"
        },
        {
            "timestamp": "2026-01-16T14:20:00Z",
            "action": "parameter_change",
            "file": "src/physics/vehicle.py",
            "function": "update_vehicle_properties",
            "parameters": {
                "fMass": {"old": 1800.0, "new": 2000.0},
                "fDriveInertia": {"old": 3.0, "new": 3.5}
            },
            "actor": "automated_script",
            "commit": "def456"
        },
        {
            "timestamp": "2026-01-18T09:15:00Z",
            "action": "parameter_change",
            "file": "src/physics/truck.py",
            "function": "configure_truck",
            "parameters": {
                "fMass": {"old": 3000.0, "new": 3600.0},
                "fDriveInertia": {"old": 5.0, "new": 6.0}
            },
            "actor": "manual_update",
            "commit": "ghi789"
        },
        {
            "timestamp": "2026-01-20T16:45:00Z",
            "action": "parameter_change",
            "file": "src/physics/vehicle.py",
            "function": "update_vehicle_properties",
            "parameters": {
                "fMass": {"old": 2000.0, "new": 1600.0},
                "fDriveInertia": {"old": 3.5, "new": 2.8}
            },
            "actor": "manual_update",
            "commit": "jkl012"
        },
        {
            "timestamp": "2026-02-01T11:00:00Z",
            "action": "parameter_change",
            "file": "src/physics/car.py",
            "function": "adjust_car_physics",
            "parameters": {
                "fMass": {"old": 1200.0, "new": 1440.0},
                "fDriveInertia": {"old": 2.0, "new": 2.4}
            },
            "actor": "automated_script",
            "commit": "mno345"
        }
    ]
    
    with open(log_file_path, 'w') as f:
        for entry in sample_entries:
            f.write(json.dumps(entry) + '\n')
    
    print(f"✅ Created sample log file: {log_file_path}")


def analyze_parameter_changes(entries):
    """
    Analyze parameter change patterns from log entries.
    
    Args:
        entries: List of log entry dictionaries
    
    Returns:
        Dictionary of discovered patterns and statistics
    """
    # Track parameter changes
    parameter_changes = defaultdict(list)
    co_occurring_changes = defaultdict(lambda: defaultdict(int))
    
    for entry in entries:
        if entry.get('action') != 'parameter_change':
            continue
        
        params = entry.get('parameters', {})
        if not params:
            continue
        
        # Track individual parameter changes
        for param_name, change in params.items():
            if isinstance(change, dict) and 'old' in change and 'new' in change:
                old_val = change['old']
                new_val = change['new']
                if old_val != new_val:
                    parameter_changes[param_name].append({
                        'old': old_val,
                        'new': new_val,
                        'timestamp': entry.get('timestamp'),
                        'file': entry.get('file')
                    })
        
        # Track co-occurring parameter changes
        changed_params = [p for p, c in params.items() 
                         if isinstance(c, dict) and c.get('old') != c.get('new')]
        
        for i, param1 in enumerate(changed_params):
            for param2 in changed_params[i+1:]:
                # Store both directions for correlation analysis
                pair_key = tuple(sorted([param1, param2]))
                co_occurring_changes[pair_key][entry.get('file', 'unknown')] += 1
    
    return {
        'parameter_changes': parameter_changes,
        'co_occurring_changes': co_occurring_changes
    }


def calculate_correlation(param_changes, param1, param2):
    """
    Calculate simple correlation between two parameters.
    
    This is a simplified correlation - in production, use proper statistical methods.
    
    Args:
        param_changes: Dictionary of parameter changes
        param1: First parameter name
        param2: Second parameter name
    
    Returns:
        Dictionary with correlation statistics
    """
    changes1 = param_changes.get(param1, [])
    changes2 = param_changes.get(param2, [])
    
    if not changes1 or not changes2:
        return None
    
    # Find co-occurring changes by timestamp
    co_changes = []
    for c1 in changes1:
        for c2 in changes2:
            if c1['timestamp'] == c2['timestamp']:
                try:
                    ratio1 = c1['new'] / c1['old'] if c1['old'] != 0 else 0
                    ratio2 = c2['new'] / c2['old'] if c2['old'] != 0 else 0
                    co_changes.append({
                        'ratio1': ratio1,
                        'ratio2': ratio2,
                        'timestamp': c1['timestamp']
                    })
                except (TypeError, ZeroDivisionError):
                    continue
    
    if not co_changes:
        return None
    
    # Calculate average ratio relationship
    avg_ratio = sum(c['ratio2'] / c['ratio1'] if c['ratio1'] != 0 else 0 
                    for c in co_changes) / len(co_changes)
    
    return {
        'instances': len(co_changes),
        'average_ratio': avg_ratio,
        'confidence': 'high' if len(co_changes) >= 5 else 'medium' if len(co_changes) >= 3 else 'low'
    }


def generate_summary_report(analysis_results):
    """
    Generate a human-readable summary report of discovered patterns.
    
    Args:
        analysis_results: Dictionary from analyze_parameter_changes()
    
    Returns:
        String containing formatted summary report
    """
    report = []
    report.append("=" * 80)
    report.append("Log Analysis Summary: Parameter Change Pattern Discovery")
    report.append("=" * 80)
    report.append(f"Generated: {datetime.utcnow().isoformat()}Z")
    report.append(f"Mode: DRY-RUN (Read-only analysis)")
    report.append("")
    
    # Parameter change statistics
    param_changes = analysis_results['parameter_changes']
    report.append("## Parameter Change Frequency")
    report.append("")
    
    if param_changes:
        for param, changes in sorted(param_changes.items(), 
                                     key=lambda x: len(x[1]), 
                                     reverse=True):
            report.append(f"  - {param}: {len(changes)} changes detected")
    else:
        report.append("  (No parameter changes detected)")
    
    report.append("")
    
    # Co-occurring parameter changes
    co_changes = analysis_results['co_occurring_changes']
    report.append("## Co-occurring Parameter Changes")
    report.append("")
    
    if co_changes:
        report.append("Parameters that frequently change together:")
        report.append("")
        for param_pair, file_counts in sorted(co_changes.items(), 
                                              key=lambda x: sum(x[1].values()), 
                                              reverse=True):
            total_instances = sum(file_counts.values())
            param1, param2 = param_pair
            report.append(f"  - {param1} ↔ {param2}")
            report.append(f"    Total instances: {total_instances}")
            report.append(f"    Files affected: {len(file_counts)}")
            
            # Calculate correlation if both parameters have changes
            correlation = calculate_correlation(param_changes, param1, param2)
            if correlation:
                report.append(f"    Co-occurring changes: {correlation['instances']}")
                report.append(f"    Average ratio: {correlation['average_ratio']:.2f}")
                report.append(f"    Confidence: {correlation['confidence']}")
            report.append("")
    else:
        report.append("  (No co-occurring parameter changes detected)")
    
    report.append("")
    
    # Suggested transformations (for demonstration only)
    report.append("## Suggested Pattern-Based Transformations")
    report.append("")
    report.append("Based on discovered patterns, the following transformations")
    report.append("could be considered (requires human review):")
    report.append("")
    
    suggestions_made = False
    for param_pair, file_counts in co_changes.items():
        param1, param2 = param_pair
        correlation = calculate_correlation(param_changes, param1, param2)
        
        if correlation and correlation['confidence'] in ['high', 'medium']:
            suggestions_made = True
            report.append(f"  📊 Pattern: {param1} → {param2}")
            report.append(f"     When {param1} changes, consider adjusting {param2}")
            report.append(f"     Typical ratio: {correlation['average_ratio']:.2f}")
            report.append(f"     Evidence: {correlation['instances']} instances")
            report.append(f"     Confidence: {correlation['confidence']}")
            report.append("")
    
    if not suggestions_made:
        report.append("  (Insufficient data for high-confidence suggestions)")
        report.append("  (Minimum 3 co-occurring instances required)")
    
    report.append("")
    report.append("=" * 80)
    report.append("⚠️  IMPORTANT: This is a read-only analysis.")
    report.append("⚠️  No files have been modified.")
    report.append("⚠️  All transformations require human review and approval.")
    report.append("=" * 80)
    
    return "\n".join(report)


def main():
    """Main entry point for log analysis."""
    print("🔍 Log Analysis Example: Pattern Discovery")
    print("=" * 60)
    print()
    
    # Read log file
    log_file = Path(__file__).parent / "hello_world_handling_pipeline.jsonl"
    print(f"📖 Reading log file: {log_file}")
    
    entries = read_jsonl_logs(log_file)
    print(f"✅ Loaded {len(entries)} log entries")
    print()
    
    # Analyze patterns
    print("🔬 Analyzing parameter change patterns...")
    analysis_results = analyze_parameter_changes(entries)
    
    # Generate summary report
    print("📝 Generating summary report...")
    report = generate_summary_report(analysis_results)
    
    # Write summary to file
    output_file = Path(__file__).parent / "log_analysis_summary.txt"
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"✅ Summary report written to: {output_file}")
    print()
    
    # Display report
    print(report)
    print()
    
    # Final status
    print("=" * 60)
    print("✅ Analysis complete!")
    print(f"📄 Results saved to: {output_file}")
    print("⚠️  No files were modified (dry-run mode)")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
