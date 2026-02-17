"""
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
