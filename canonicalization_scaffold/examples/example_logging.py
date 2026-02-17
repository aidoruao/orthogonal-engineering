#!/usr/bin/env python3
"""
Example: JSONL Logging

This example demonstrates how to:
1. Create a structured logger
2. Log operations with step IDs
3. Track operation lifecycle (start/complete/error)
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from canonicalization_scaffold.logger import JSONLLogger, create_hello_world_logger
import json
import time

def main():
    output_dir = Path("./canonical_output/logs")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("JSONL Logging Example")
    print("=" * 60)
    print()
    
    # Example 1: Basic logger
    print("Example 1: Basic logging")
    print("-" * 60)
    
    logger = JSONLLogger(output_dir, "example_log")
    
    # Log a simple event
    logger.log("info", {"message": "Application started", "version": "1.0.0"})
    print("  ✓ Logged application start")
    
    # Log with custom step ID
    logger.log("debug", {"message": "Debug information"}, step_id="custom-step-1")
    print("  ✓ Logged debug info with custom step ID")
    
    print()
    
    # Example 2: Operation tracking
    print("Example 2: Operation lifecycle tracking")
    print("-" * 60)
    
    # Start an operation
    step_id = logger.start_operation(
        "data_processing",
        input_file="data.csv",
        config={"batch_size": 100}
    )
    print(f"  ✓ Started operation (step_id: {step_id[:8]}...)")
    
    # Simulate work
    time.sleep(0.1)
    
    # Complete the operation
    logger.complete_operation(
        step_id,
        "data_processing",
        records_processed=1000,
        duration_ms=100
    )
    print("  ✓ Completed operation")
    
    print()
    
    # Example 3: Error handling
    print("Example 3: Error logging")
    print("-" * 60)
    
    step_id = logger.start_operation("risky_operation")
    print("  ✓ Started risky operation")
    
    # Simulate an error
    logger.error_operation(
        step_id,
        "risky_operation",
        "Connection timeout",
        error_code=500
    )
    print("  ✓ Logged error")
    
    print()
    
    # Example 4: Hello World logger
    print("Example 4: Hello World handling logger")
    print("-" * 60)
    
    hw_logger = create_hello_world_logger(output_dir)
    
    step_id = hw_logger.start_operation(
        "canonicalize_file",
        file="example.txt",
        file_type="text"
    )
    print("  ✓ Started canonicalization")
    
    hw_logger.complete_operation(
        step_id,
        "canonicalize_file",
        hash="abc123def456",
        size_bytes=1024
    )
    print("  ✓ Completed canonicalization")
    
    print()
    
    # Display log contents
    print("=" * 60)
    print("Log File Contents")
    print("=" * 60)
    print()
    
    log_file = output_dir / "example_log.jsonl"
    print(f"Reading: {log_file}")
    print()
    
    with open(log_file, 'r') as f:
        for i, line in enumerate(f, 1):
            record = json.loads(line)
            
            # Format timestamp
            timestamp = record['timestamp'][:19]  # Truncate for display
            
            # Format event
            event_type = record['event_type']
            
            # Get operation or message
            operation = record.get('operation', record.get('message', ''))
            
            print(f"  {i}. [{timestamp}] {event_type:8} - {operation}")
    
    print()
    
    # Display Hello World log
    hw_log_file = output_dir / "hello_world_handling_pipeline.jsonl"
    print(f"Reading: {hw_log_file}")
    print()
    
    with open(hw_log_file, 'r') as f:
        for i, line in enumerate(f, 1):
            record = json.loads(line)
            timestamp = record['timestamp'][:19]
            event_type = record['event_type']
            operation = record.get('operation', record.get('message', ''))
            print(f"  {i}. [{timestamp}] {event_type:8} - {operation}")
    
    print()
    print("=" * 60)
    print("Example completed!")
    print("=" * 60)
    print()
    print(f"Log files saved to: {output_dir}")


if __name__ == '__main__':
    main()
