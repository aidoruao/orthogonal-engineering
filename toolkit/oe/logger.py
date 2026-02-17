"""
Logger module for deterministic JSONL logging.

Provides monotonic step_id and ISO8601 UTC timestamps.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class PipelineLogger:
    """JSONL logger with monotonic step IDs and ISO8601 timestamps."""
    
    def __init__(self, log_file: Path):
        """
        Initialize logger.
        
        Args:
            log_file: Path to JSONL log file
        """
        self.log_file = log_file
        self.step_id = 0
        
        # Ensure parent directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize log file
        if not self.log_file.exists():
            self.log_file.touch()
    
    def _get_timestamp(self) -> str:
        """
        Get current timestamp in ISO8601 UTC format.
        
        Returns:
            ISO8601 timestamp string
        """
        return datetime.now(timezone.utc).isoformat()
    
    def log(self, event_type: str, data: Dict[str, Any], 
            extra_fields: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an event to the JSONL file.
        
        Args:
            event_type: Type of event (e.g., 'start', 'complete', 'error')
            data: Event data
            extra_fields: Optional extra fields to include
        """
        self.step_id += 1
        
        log_entry = {
            'step_id': self.step_id,
            'timestamp': self._get_timestamp(),
            'event_type': event_type,
            **data
        }
        
        if extra_fields:
            log_entry.update(extra_fields)
        
        # Write to log file
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry, separators=(',', ':')) + '\n')
    
    def log_start(self, operation: str, **kwargs) -> None:
        """
        Log the start of an operation.
        
        Args:
            operation: Operation name
            **kwargs: Additional data
        """
        data = {'operation': operation, 'status': 'start'}
        data.update(kwargs)
        self.log('start', data)
    
    def log_complete(self, operation: str, **kwargs) -> None:
        """
        Log the completion of an operation.
        
        Args:
            operation: Operation name
            **kwargs: Additional data
        """
        data = {'operation': operation, 'status': 'complete'}
        data.update(kwargs)
        self.log('complete', data)
    
    def log_error(self, operation: str, error: str, **kwargs) -> None:
        """
        Log an error.
        
        Args:
            operation: Operation name
            error: Error message
            **kwargs: Additional data
        """
        data = {'operation': operation, 'status': 'error', 'error': error}
        data.update(kwargs)
        self.log('error', data)
    
    def log_progress(self, operation: str, progress: float, total: int, **kwargs) -> None:
        """
        Log progress update.
        
        Args:
            operation: Operation name
            progress: Progress percentage (0.0 to 1.0)
            total: Total items
            **kwargs: Additional data
        """
        data = {
            'operation': operation,
            'status': 'progress',
            'progress': progress,
            'total': total
        }
        data.update(kwargs)
        self.log('progress', data)


def create_hello_world_logger() -> PipelineLogger:
    """
    Create logger for hello_world_handling_pipeline.jsonl.
    
    Returns:
        PipelineLogger instance
    """
    log_path = Path('logs/hello_world_handling_pipeline.jsonl')
    return PipelineLogger(log_path)


def create_verification_logger() -> PipelineLogger:
    """
    Create logger for handling_verification_pipeline.jsonl.
    
    Returns:
        PipelineLogger instance
    """
    log_path = Path('logs/handling_verification_pipeline.jsonl')
    return PipelineLogger(log_path)
