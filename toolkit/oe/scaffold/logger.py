"""
Logger Module

JSONL logger with:
- Monotonic step_id for ordered events
- ISO8601 UTC timestamps
- Separate logs for different pipelines
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Union, Optional, Any


class ScaffoldLogger:
    """JSONL logger for scaffold operations."""
    
    def __init__(self, log_path: Union[str, Path]):
        """
        Initialize logger.
        
        Args:
            log_path: Path to JSONL log file
        """
        self.log_path = Path(log_path)
        self.step_id = 0
        
        # Create directory if needed
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, event_type: str, message: str, **kwargs: Any) -> None:
        """
        Log an event.
        
        Args:
            event_type: Type of event (e.g., "start", "complete", "error")
            message: Human-readable message
            **kwargs: Additional fields to include in log entry
        """
        self.step_id += 1
        
        entry = {
            "step_id": self.step_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "message": message,
            **kwargs
        }
        
        # Append to JSONL file
        with open(self.log_path, "a", encoding="utf-8") as f:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")
    
    def log_start(self, operation: str, **kwargs: Any) -> None:
        """Log operation start."""
        self.log("start", f"Starting {operation}", operation=operation, **kwargs)
    
    def log_complete(self, operation: str, **kwargs: Any) -> None:
        """Log operation completion."""
        self.log("complete", f"Completed {operation}", operation=operation, **kwargs)
    
    def log_error(self, operation: str, error: str, **kwargs: Any) -> None:
        """Log error."""
        self.log("error", f"Error in {operation}: {error}", 
                operation=operation, error=error, **kwargs)
    
    def log_info(self, message: str, **kwargs: Any) -> None:
        """Log informational message."""
        self.log("info", message, **kwargs)


def create_hello_world_logger(output_dir: Union[str, Path] = ".") -> ScaffoldLogger:
    """
    Create logger for hello_world_handling_pipeline.jsonl.
    
    Args:
        output_dir: Directory for log file
        
    Returns:
        ScaffoldLogger instance
    """
    output_dir = Path(output_dir)
    log_path = output_dir / "hello_world_handling_pipeline.jsonl"
    return ScaffoldLogger(log_path)


def create_verification_logger(output_dir: Union[str, Path] = ".") -> ScaffoldLogger:
    """
    Create logger for handling_verification_pipeline.jsonl.
    
    Args:
        output_dir: Directory for log file
        
    Returns:
        ScaffoldLogger instance
    """
    output_dir = Path(output_dir)
    log_path = output_dir / "handling_verification_pipeline.jsonl"
    return ScaffoldLogger(log_path)


class LogReader:
    """Reader for JSONL log files."""
    
    @staticmethod
    def read_log(log_path: Union[str, Path]) -> list:
        """
        Read all entries from a log file.
        
        Args:
            log_path: Path to JSONL log file
            
        Returns:
            List of log entry dictionaries
        """
        log_path = Path(log_path)
        
        if not log_path.exists():
            return []
        
        entries = []
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
        
        return entries
    
    @staticmethod
    def filter_by_event_type(entries: list, event_type: str) -> list:
        """Filter log entries by event type."""
        return [e for e in entries if e.get("event_type") == event_type]
    
    @staticmethod
    def filter_by_operation(entries: list, operation: str) -> list:
        """Filter log entries by operation."""
        return [e for e in entries if e.get("operation") == operation]
