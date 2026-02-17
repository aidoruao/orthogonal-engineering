#!/usr/bin/env python3
"""
Log Analysis Example

Demonstrates how to analyze CAS operation logs for insights and debugging.
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
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List


def load_jsonl_logs(log_file: Path) -> List[Dict]:
    """Load JSONL log file."""
    logs = []
    
    if not log_file.exists():
        print(f"Log file not found: {log_file}")
        return logs
    
    with open(log_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Warning: Failed to parse log line: {e}")
    
    return logs


def analyze_operations(logs: List[Dict]) -> Dict:
    """Analyze operation types and frequencies."""
    operation_counts = Counter()
    operation_errors = Counter()
    
    for log in logs:
        level = log.get("level", "INFO")
        message = log.get("message", "")
        
        # Count operations
        if "operation" in log:
            operation_counts[log["operation"]] += 1
        
        # Count errors
        if level == "ERROR":
            operation_errors[message] += 1
    
    return {
        "operation_counts": dict(operation_counts),
        "error_counts": dict(operation_errors),
        "total_logs": len(logs)
    }


def analyze_timing(logs: List[Dict]) -> Dict:
    """Analyze operation timing patterns."""
    if not logs:
        return {}
    
    timestamps = []
    for log in logs:
        if "timestamp" in log:
            try:
                ts = datetime.fromisoformat(log["timestamp"].replace('Z', '+00:00'))
                timestamps.append(ts)
            except ValueError:
                pass
    
    if not timestamps:
        return {}
    
    timestamps.sort()
    
    # Calculate time between operations
    intervals = []
    for i in range(1, len(timestamps)):
        interval = (timestamps[i] - timestamps[i-1]).total_seconds()
        intervals.append(interval)
    
    return {
        "first_operation": timestamps[0].isoformat(),
        "last_operation": timestamps[-1].isoformat(),
        "total_duration_seconds": (timestamps[-1] - timestamps[0]).total_seconds(),
        "average_interval_seconds": sum(intervals) / len(intervals) if intervals else 0,
        "operation_count": len(timestamps)
    }


def analyze_file_operations(logs: List[Dict]) -> Dict:
    """Analyze file-related operations."""
    files_processed = set()
    files_with_errors = set()
    operations_by_file = defaultdict(list)
    
    for log in logs:
        # Extract file references
        filepath = log.get("filepath") or log.get("file") or log.get("path")
        
        if filepath:
            files_processed.add(filepath)
            
            operation = log.get("operation", "unknown")
            operations_by_file[filepath].append(operation)
            
            if log.get("level") == "ERROR":
                files_with_errors.add(filepath)
    
    return {
        "total_files_processed": len(files_processed),
        "files_with_errors": len(files_with_errors),
        "operations_per_file": {
            f: len(ops) for f, ops in operations_by_file.items()
        }
    }


def generate_report(log_file: Path, output_file: Path = None):
    """Generate comprehensive log analysis report."""
    print(f"Analyzing log file: {log_file}")
    
    logs = load_jsonl_logs(log_file)
    
    if not logs:
        print("No logs found to analyze")
        return
    
    print(f"Loaded {len(logs)} log entries")
    
    # Perform analyses
    operation_analysis = analyze_operations(logs)
    timing_analysis = analyze_timing(logs)
    file_analysis = analyze_file_operations(logs)
    
    # Compile report
    report = {
        "log_file": str(log_file),
        "analyzed_at": datetime.utcnow().isoformat() + "Z",
        "summary": {
            "total_logs": len(logs),
            "operations": operation_analysis,
            "timing": timing_analysis,
            "files": file_analysis
        }
    }
    
    # Print summary
    print("\n" + "=" * 60)
    print("LOG ANALYSIS REPORT")
    print("=" * 60)
    print(f"\nTotal logs: {len(logs)}")
    
    print("\nOperation counts:")
    for op, count in operation_analysis["operation_counts"].items():
        print(f"  {op}: {count}")
    
    if operation_analysis["error_counts"]:
        print("\nErrors:")
        for error, count in operation_analysis["error_counts"].items():
            print(f"  {error}: {count}")
    
    if timing_analysis:
        print("\nTiming:")
        print(f"  Duration: {timing_analysis.get('total_duration_seconds', 0):.2f}s")
        print(f"  Operations: {timing_analysis.get('operation_count', 0)}")
        print(f"  Avg interval: {timing_analysis.get('average_interval_seconds', 0):.3f}s")
    
    print("\nFile operations:")
    print(f"  Files processed: {file_analysis['total_files_processed']}")
    print(f"  Files with errors: {file_analysis['files_with_errors']}")
    
    # Save report if output file specified
    if output_file:
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nReport saved to: {output_file}")
    
    print("=" * 60)
    
    return report


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python log_analysis_example.py <log_file> [output_file]")
        print("\nExample:")
        print("  python log_analysis_example.py logs/pipeline_20260216.jsonl")
        print("  python log_analysis_example.py logs/pipeline_20260216.jsonl analysis_report.json")
        sys.exit(1)
    
    log_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    try:
        generate_report(log_file, output_file)
    except Exception as e:
        print(f"Error during analysis: {e}")
        raise


if __name__ == "__main__":
    main()
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
