"""
Structured logging module for CAS operations.

Provides consistent logging with causality tracking.
"""

import json
import logging
import sys
from datetime import datetime
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
