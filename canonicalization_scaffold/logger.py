"""
JSONL Logger for Canonicalization Scaffold

Provides structured logging with ISO8601 UTC timestamps, step IDs,
and JSONL output format.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4


class JSONLLogger:
    """
    JSONL logger with structured step IDs and ISO8601 UTC timestamps.
    
    Writes records in JSONL (JSON Lines) format for easy streaming and processing.
    """
    
    def __init__(self, output_dir: Path, log_name: str = "pipeline"):
        """
        Initialize JSONL logger.
        
        Args:
            output_dir: Directory where log files will be written
            log_name: Base name for log files (default: "pipeline")
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log_name = log_name
        self.session_id = str(uuid4())
        
    def _get_timestamp(self) -> str:
        """Get current UTC timestamp in ISO8601 format."""
        return datetime.now(timezone.utc).isoformat()
    
    def log(self, event_type: str, data: Dict[str, Any], step_id: Optional[str] = None) -> None:
        """
        Log an event to JSONL file.
        
        Args:
            event_type: Type of event (e.g., "start", "complete", "error")
            data: Event data dictionary
            step_id: Optional step identifier (auto-generated if not provided)
        """
        if step_id is None:
            step_id = str(uuid4())
            
        record = {
            "timestamp": self._get_timestamp(),
            "session_id": self.session_id,
            "step_id": step_id,
            "event_type": event_type,
            **data
        }
        
        log_file = self.output_dir / f"{self.log_name}.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    
    def start_operation(self, operation: str, **kwargs) -> str:
        """
        Log the start of an operation.
        
        Args:
            operation: Name of the operation
            **kwargs: Additional data to log
            
        Returns:
            Step ID for this operation
        """
        step_id = str(uuid4())
        self.log("start", {"operation": operation, **kwargs}, step_id)
        return step_id
    
    def complete_operation(self, step_id: str, operation: str, **kwargs) -> None:
        """
        Log the completion of an operation.
        
        Args:
            step_id: Step ID from start_operation
            operation: Name of the operation
            **kwargs: Additional data to log
        """
        self.log("complete", {"operation": operation, **kwargs}, step_id)
    
    def error_operation(self, step_id: str, operation: str, error: str, **kwargs) -> None:
        """
        Log an error during an operation.
        
        Args:
            step_id: Step ID from start_operation
            operation: Name of the operation
            error: Error message
            **kwargs: Additional data to log
        """
        self.log("error", {"operation": operation, "error": error, **kwargs}, step_id)


def create_hello_world_logger(output_dir: Path) -> JSONLLogger:
    """
    Create a Hello World handling pipeline logger.
    
    Args:
        output_dir: Directory where log files will be written
        
    Returns:
        JSONLLogger instance configured for hello world handling
    """
    logger = JSONLLogger(output_dir, "hello_world_handling_pipeline")
    logger.log("init", {
        "message": "Hello World Handling Pipeline initialized",
        "version": "0.1.0"
    })
    return logger


def create_verification_logger(output_dir: Path) -> JSONLLogger:
    """
    Create a handling verification pipeline logger.
    
    Args:
        output_dir: Directory where log files will be written
        
    Returns:
        JSONLLogger instance configured for verification
    """
    logger = JSONLLogger(output_dir, "handling_verification_pipeline")
    logger.log("init", {
        "message": "Handling Verification Pipeline initialized",
        "version": "0.1.0"
    })
    return logger


# Example usage demonstrating the logger
if __name__ == "__main__":
    # Create example logs
    output_dir = Path("./logs")
    
    # Hello World logger
    hw_logger = create_hello_world_logger(output_dir)
    step = hw_logger.start_operation("example_canonicalization", file="test.txt")
    hw_logger.complete_operation(step, "example_canonicalization", status="success")
    
    # Verification logger
    verify_logger = create_verification_logger(output_dir)
    step = verify_logger.start_operation("verify_manifest", manifest="test_manifest.jsonl")
    verify_logger.complete_operation(step, "verify_manifest", status="verified")
    
    print("✓ Example logs written to ./logs/")
