#!/usr/bin/env python3
"""
Log Analysis Example

Example script demonstrating how to analyze pipeline JSONL logs.

This script shows how to:
- Read JSONL pipeline logs
- Extract key metrics
- Identify errors and warnings
- Generate summaries

Usage: python log_analysis_example.py [log_file]
"""

import json
import sys
from collections import defaultdict
from pathlib import Path
from datetime import datetime


def parse_iso8601(timestamp_str):
    """Parse ISO8601 timestamp."""
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except:
        return None


def analyze_log(log_path):
    """Analyze a pipeline log file."""
    if not Path(log_path).exists():
        print(f"Error: Log file not found: {log_path}")
        return None
    
    stats = {
        'total_steps': 0,
        'by_status': defaultdict(int),
        'by_step_name': defaultdict(int),
        'errors': [],
        'start_time': None,
        'end_time': None,
        'duration_seconds': None
    }
    
    print(f"Analyzing log: {log_path}")
    print("=" * 60)
    
    with open(log_path, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line)
                
                stats['total_steps'] += 1
                stats['by_status'][entry['status']] += 1
                stats['by_step_name'][entry['step_name']] += 1
                
                # Track errors
                if entry['status'] == 'failed':
                    stats['errors'].append({
                        'step_id': entry['step_id'],
                        'step_name': entry['step_name'],
                        'error': entry.get('error', 'Unknown error'),
                        'timestamp': entry['timestamp']
                    })
                
                # Track timing
                timestamp = parse_iso8601(entry['timestamp'])
                if timestamp:
                    if stats['start_time'] is None or timestamp < stats['start_time']:
                        stats['start_time'] = timestamp
                    if stats['end_time'] is None or timestamp > stats['end_time']:
                        stats['end_time'] = timestamp
                
            except json.JSONDecodeError:
                print(f"Warning: Invalid JSON line: {line[:50]}...")
            except Exception as e:
                print(f"Warning: Error parsing line: {e}")
    
    # Calculate duration
    if stats['start_time'] and stats['end_time']:
        duration = stats['end_time'] - stats['start_time']
        stats['duration_seconds'] = duration.total_seconds()
    
    return stats


def print_summary(stats):
    """Print analysis summary."""
    print(f"\nTotal Steps: {stats['total_steps']}")
    
    print("\nBy Status:")
    for status, count in sorted(stats['by_status'].items()):
        print(f"  {status:12} {count:>5}")
    
    print("\nBy Step Name:")
    for step_name, count in sorted(stats['by_step_name'].items(), key=lambda x: -x[1]):
        print(f"  {step_name:30} {count:>5}")
    
    if stats['start_time']:
        print(f"\nStart Time: {stats['start_time'].isoformat()}")
    if stats['end_time']:
        print(f"End Time:   {stats['end_time'].isoformat()}")
    if stats['duration_seconds'] is not None:
        print(f"Duration:   {stats['duration_seconds']:.2f} seconds")
    
    if stats['errors']:
        print(f"\nErrors ({len(stats['errors'])}):")
        for error in stats['errors']:
            print(f"  Step {error['step_id']} ({error['step_name']}): {error['error']}")
    else:
        print("\n✓ No errors found")
    
    print("\n" + "=" * 60)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        # Default to example log
        log_file = "logs/indexing_pipeline.jsonl"
        print(f"No log file specified. Using default: {log_file}")
    else:
        log_file = sys.argv[1]
    
    stats = analyze_log(log_file)
    
    if stats:
        print_summary(stats)
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
