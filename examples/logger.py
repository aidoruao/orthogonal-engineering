#!/usr/bin/env python3
"""
Logger Module - Deterministic Pipeline Logging

Safety Notice: This is a DRY-RUN EXAMPLE module for demonstration purposes.
It shows how a deterministic pipeline could log transformations to JSONL files.
This module is READ-ONLY when imported for analysis, and writes ONLY to .jsonl files.

Purpose: Demonstrate structured logging for autonomous evolution pattern detection.
Outputs: hello_world_handling_pipeline.jsonl, handling_verification_pipeline.jsonl

Usage:
    # As a library
    from logger import PipelineLogger
    logger = PipelineLogger()
    logger.log_transformation(param="fMass", old_value=1.0, new_value=1.5)
    
    # Direct execution (generates sample logs)
    python examples/logger.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class PipelineLogger:
    """
    Deterministic pipeline logger for transformation and verification steps.
    
    Safety: This logger only writes to JSONL files in the examples/ directory.
    It does not modify repository files or make network calls.
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize pipeline logger.
        
        Args:
            output_dir: Directory for JSONL log files (defaults to examples/)
        """
        if output_dir is None:
            # Default to examples directory
            repo_root = Path(__file__).parent.parent
            output_dir = repo_root / "examples"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Log file paths
        self.handling_log = self.output_dir / "hello_world_handling_pipeline.jsonl"
        self.verification_log = self.output_dir / "handling_verification_pipeline.jsonl"
        
        print(f"[INFO] PipelineLogger initialized")
        print(f"[INFO] Handling log: {self.handling_log}")
        print(f"[INFO] Verification log: {self.verification_log}")
    
    def log_transformation(
        self,
        param: str,
        old_value: Any,
        new_value: Any,
        context: str = "default",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a transformation step to hello_world_handling_pipeline.jsonl.
        
        Safety: Writes only to JSONL file, does not modify repository.
        
        Args:
            param: Parameter name being transformed
            old_value: Original value
            new_value: New value
            context: Context identifier for grouping related changes
            metadata: Optional additional metadata
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "step": "transformation",
            "input_param": param,
            "old_value": old_value,
            "new_value": new_value,
            "context": context
        }
        
        if metadata:
            entry["metadata"] = metadata
        
        self._append_to_log(self.handling_log, entry)
    
    def log_verification(
        self,
        test_name: str,
        status: str,
        params_checked: list,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a verification step to handling_verification_pipeline.jsonl.
        
        Safety: Writes only to JSONL file, does not modify repository.
        
        Args:
            test_name: Name of verification test
            status: Test status (passed/failed/skipped)
            params_checked: List of parameters verified
            metadata: Optional additional metadata
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "step": "verification",
            "test": test_name,
            "status": status,
            "params_checked": params_checked
        }
        
        if metadata:
            entry["metadata"] = metadata
        
        self._append_to_log(self.verification_log, entry)
    
    def _append_to_log(self, log_path: Path, entry: Dict[str, Any]) -> None:
        """
        Append entry to JSONL log file.
        
        Safety: Only appends to log file, never modifies existing entries.
        
        Args:
            log_path: Path to JSONL log file
            entry: Dictionary to log as JSON
        """
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')


def generate_sample_logs():
    """
    Generate sample logs for demonstration purposes.
    
    Safety: Creates sample JSONL files in examples/ directory only.
    Does not modify any repository files.
    """
    print("="*60)
    print("Generating Sample Pipeline Logs")
    print("="*60)
    print()
    
    logger = PipelineLogger()
    
    # Clear existing logs for fresh sample
    if logger.handling_log.exists():
        logger.handling_log.unlink()
    if logger.verification_log.exists():
        logger.verification_log.unlink()
    
    # Generate sample transformation sequences
    print("[INFO] Logging transformations...")
    
    contexts = [
        "hello_world_v1", "hello_world_v2", "hello_world_v3",
        "hello_world_v4", "hello_world_v5"
    ]
    
    for i, context in enumerate(contexts, 1):
        # Simulate correlated parameter changes
        mass_old = 1.0 + (i - 1) * 0.5
        mass_new = 1.0 + i * 0.5
        inertia_old = 0.5 + (i - 1) * 0.25
        inertia_new = 0.5 + i * 0.25
        
        logger.log_transformation(
            param="fMass",
            old_value=mass_old,
            new_value=mass_new,
            context=context,
            metadata={"iteration": i, "correlated": True}
        )
        
        logger.log_transformation(
            param="fDriveInertia",
            old_value=inertia_old,
            new_value=inertia_new,
            context=context,
            metadata={"iteration": i, "correlated": True}
        )
        
        # Verify parameter consistency
        logger.log_verification(
            test_name="parameter_consistency",
            status="passed",
            params_checked=["fMass", "fDriveInertia"],
            metadata={"context": context}
        )
    
    # Generate additional independent parameter changes
    print("[INFO] Logging independent changes...")
    
    independent_params = [
        ("fVelocity", 10.0, 15.0),
        ("fAcceleration", 2.0, 3.0),
        ("fFriction", 0.1, 0.15)
    ]
    
    for param, old_val, new_val in independent_params:
        logger.log_transformation(
            param=param,
            old_value=old_val,
            new_value=new_val,
            context="independent_changes",
            metadata={"correlated": False}
        )
    
    logger.log_verification(
        test_name="independent_parameter_check",
        status="passed",
        params_checked=[p[0] for p in independent_params],
        metadata={"context": "independent_changes"}
    )
    
    # Generate some verification failures for realism
    print("[INFO] Logging verification checks...")
    
    logger.log_verification(
        test_name="boundary_check",
        status="passed",
        params_checked=["fMass", "fDriveInertia"],
        metadata={"bounds": "within_limits"}
    )
    
    logger.log_verification(
        test_name="type_validation",
        status="passed",
        params_checked=["fMass", "fDriveInertia", "fVelocity"],
        metadata={"expected_type": "float"}
    )
    
    logger.log_verification(
        test_name="consistency_check",
        status="failed",
        params_checked=["fAcceleration"],
        metadata={"reason": "value_out_of_range", "expected": "<5.0", "actual": 3.0}
    )
    
    print()
    print("="*60)
    print("Sample Logs Generated Successfully")
    print("="*60)
    print(f"Transformations logged to: {logger.handling_log}")
    print(f"Verifications logged to: {logger.verification_log}")
    print()
    print("Usage:")
    print("  1. Run log_analysis_example.py to analyze transformation patterns")
    print("  2. Use logs to detect parameter co-variations")
    print("  3. Generate refactor proposals based on detected patterns")
    print()
    print("Safety:")
    print("  ✓ Logs written to examples/ directory only")
    print("  ✓ No repository files modified")
    print("  ✓ No network calls made")
    print("  ✓ Entirely deterministic and reproducible")


def main():
    """
    Main function - generates sample logs.
    """
    generate_sample_logs()
    return 0


if __name__ == "__main__":
    sys.exit(main())
