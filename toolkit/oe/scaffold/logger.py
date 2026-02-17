"""
<<<<<<< HEAD
JSONL logger with monotonic step IDs and ISO8601 UTC timestamps.

Provides structured logging for the auditable scaffold pipeline.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class ScaffoldLogger:
    """
    JSONL logger with monotonic step_id and ISO8601 UTC timestamps.
    
    Creates two log files based on the prefix parameter:
    - {prefix}_pipeline.jsonl: For pipeline events
    - {prefix}_verification_pipeline.jsonl: For verification events
    
    Example: prefix="handling" creates handling_pipeline.jsonl and handling_verification_pipeline.jsonl
    """
    
    def __init__(self, output_dir: str = ".", prefix: str = "handling"):
        """
        Initialize the logger.
        
        Args:
            output_dir: Directory to write log files
            prefix: Prefix for log file names (handling, hello_world_handling, etc.)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.step_id = 0
        self.prefix = prefix
        
        # Create log files
        self.pipeline_log = self.output_dir / f"{prefix}_pipeline.jsonl"
        self.verification_log = self.output_dir / f"{prefix}_verification_pipeline.jsonl"
        
    def _get_timestamp(self) -> str:
        """Get ISO8601 UTC timestamp."""
        return datetime.now(timezone.utc).isoformat()
    
    def _increment_step(self) -> int:
        """Get next monotonic step ID."""
        self.step_id += 1
        return self.step_id
    
    def log_pipeline(self, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an event to the pipeline log.
        
        Args:
            event: Event name/description
            data: Optional additional data to log
        """
        entry = {
            "step_id": self._increment_step(),
            "timestamp": self._get_timestamp(),
            "event": event,
            "data": data or {}
        }
        
        with open(self.pipeline_log, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def log_verification(self, event: str, result: bool, 
                        details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a verification event.
        
        Args:
            event: Verification event description
            result: True if verification passed, False otherwise
            details: Optional verification details
        """
        entry = {
            "step_id": self._increment_step(),
            "timestamp": self._get_timestamp(),
            "event": event,
            "result": result,
            "details": details or {}
        }
        
        with open(self.verification_log, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def log(self, event: str, **kwargs: Any) -> None:
        """
        General purpose log method.
        
        Args:
            event: Event description
            **kwargs: Additional key-value pairs to log
        """
        self.log_pipeline(event, kwargs)


# Example usage for hello_world_handling_pipeline.jsonl
def create_hello_world_logger(output_dir: str = ".") -> ScaffoldLogger:
    """Create a logger for hello world handling pipeline."""
    return ScaffoldLogger(output_dir=output_dir, prefix="hello_world_handling")
=======
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
>>>>>>> copilot/add-deterministic-auditable-scaffold
