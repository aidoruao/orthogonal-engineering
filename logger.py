"""
Structured logging module for CAS operations.

Provides consistent logging with causality tracking.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class CASLogger:
    """Structured logger for content-addressable storage operations."""

    def __init__(self, name: str = "cas", log_dir: Optional[Path] = None):
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
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"{name}_{timestamp}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(console_formatter)
        self.logger.addHandler(file_handler)

    def log_start(self, operation: str, details: Optional[Dict[str, Any]] = None) -> None:
        self.logger.info(f"START {operation}: {json.dumps(details or {})}")

    def log_complete(self, operation: str, details: Optional[Dict[str, Any]] = None) -> None:
        self.logger.info(f"COMPLETE {operation}: {json.dumps(details or {})}")

    def log_info(self, operation: str, message: str) -> None:
        self.logger.info(f"INFO {operation}: {message}")

    def log_error(self, operation: str, message: str) -> None:
        self.logger.error(f"ERROR {operation}: {message}")

    def info(self, message: str) -> None:
        self.logger.info(message)

    def error(self, message: str) -> None:
        self.logger.error(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)


class PipelineLogger(CASLogger):
    """Alias for CASLogger used by pipeline operations."""

    pass


def get_logger(name: str = "cas") -> CASLogger:
    """Get or create a CASLogger instance."""
    return CASLogger(name=name)


def create_logger(log_name: str, log_dir: Optional[Path] = None) -> PipelineLogger:
    """Create a pipeline logger."""
    return PipelineLogger(name=log_name, log_dir=log_dir)
