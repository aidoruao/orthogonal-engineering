"""
Structured logging module for CAS operations.

Provides consistent logging with causality tracking.
"""

import json
import logging
import sys
from datetime import datetime
Logger module providing JSONL logging for pipeline steps.

This module provides structured JSONL logging with monotonic step IDs
and ISO8601 UTC timestamps for pipeline operations.

Author: Orthogonal Engineering
Date: 2026-02-16
Version: 1.0.0
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class CASLogger:
    """Structured logger for content-addressable storage operations."""
    
    def __init__(self, name: str = "cas", log_dir: Optional[Path] = None):
        """
        Initialize CAS logger.
        
        Args:
            name: Logger name
            log_dir: Directory for log files (default: ./logs)
        """
        self.name = name
        self.log_dir = Path(log_dir) if log_dir else Path("logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup Python logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler for structured logs
        log_file = self.log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.jsonl"
        self.log_file = log_file
    
    def log(self, level: str, message: str, **kwargs):
        """
        Log structured message.
        
        Args:
            level: Log level (info, warning, error, debug)
            message: Log message
            **kwargs: Additional metadata
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level.upper(),
            "logger": self.name,
            "message": message,
            **kwargs
        }
        
        # Write to structured log file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        # Also log via Python logger
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(message)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.log("info", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.log("warning", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.log("error", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.log("debug", message, **kwargs)
    
    def causality(self, cause: str, trigger: str, actor: str = "system", **kwargs):
        """
        Log causality metadata.
        
        Args:
            cause: Reason for action
            trigger: What triggered the action
            actor: Who/what performed the action
            **kwargs: Additional context
        """
        self.log(
            "info",
            f"Causality: {cause}",
            cause=cause,
            trigger=trigger,
            actor=actor,
            **kwargs
        )


# Global logger instance
_global_logger: Optional[CASLogger] = None


def get_logger(name: str = "cas") -> CASLogger:
    """Get or create global logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = CASLogger(name)
    return _global_logger
class PipelineLogger:
    """JSONL logger for pipeline steps with monotonic IDs and UTC timestamps."""
    
    def __init__(self, log_path: Path):
        """
        Initialize pipeline logger.
        
        Args:
            log_path: Path to JSONL log file
        """
        self.log_path = log_path
        self.step_counter = 0
        
        # Ensure parent directory exists
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _get_utc_timestamp(self) -> str:
        """Get current UTC timestamp in ISO8601 format."""
        return datetime.now(timezone.utc).isoformat()
    
    def log_step(
        self,
        step_name: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> None:
        """
        Log a pipeline step.
        
        Args:
            step_name: Name of the pipeline step
            status: Status (e.g., 'started', 'completed', 'failed')
            details: Optional additional details
            error: Optional error message
        """
        self.step_counter += 1
        
        log_entry = {
            'step_id': self.step_counter,
            'timestamp': self._get_utc_timestamp(),
            'step_name': step_name,
            'status': status
        }
        
        if details:
            log_entry['details'] = details
        
        if error:
            log_entry['error'] = error
        
        # Append to JSONL file
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def log_start(self, step_name: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log the start of a step."""
        self.log_step(step_name, 'started', details)
    
    def log_complete(self, step_name: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log the completion of a step."""
        self.log_step(step_name, 'completed', details)
    
    def log_error(self, step_name: str, error: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log an error in a step."""
        self.log_step(step_name, 'failed', details, error)
    
    def log_info(self, step_name: str, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log informational message."""
        info_details = details or {}
        info_details['message'] = message
        self.log_step(step_name, 'info', info_details)


def create_logger(log_name: str, log_dir: Path = None) -> PipelineLogger:
    """
    Create a pipeline logger with standard naming.
    
    Args:
        log_name: Base name for the log (e.g., 'hello_world_handling_pipeline')
        log_dir: Directory for logs (defaults to ./logs)
        
    Returns:
        PipelineLogger instance
    """
    if log_dir is None:
        log_dir = Path('./logs')
    
    log_path = log_dir / f"{log_name}.jsonl"
    return PipelineLogger(log_path)
