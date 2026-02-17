"""
JSONL Logger Module

Provides JSONL logging with monotonic step_id and ISO8601 UTC timestamps.
Writes to hello_world_handling_pipeline.jsonl and handling_verification_pipeline.jsonl.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class ScaffoldLogger:
    """
    JSONL logger with monotonic step IDs and ISO8601 UTC timestamps.
    """
    
    def __init__(self, log_dir: Optional[Path] = None):
        """
        Initialize scaffold logger.
        
        Args:
            log_dir: Directory for log files (default: ./logs)
        """
        self.log_dir = Path(log_dir) if log_dir else Path("logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Log file paths
        self.handling_pipeline_log = self.log_dir / "hello_world_handling_pipeline.jsonl"
        self.verification_pipeline_log = self.log_dir / "handling_verification_pipeline.jsonl"
        
        # Monotonic step counters
        self._handling_step_id = 0
        self._verification_step_id = 0
    
    def _get_timestamp(self) -> str:
        """
        Get current UTC timestamp in ISO8601 format.
        
        Returns:
            ISO8601 timestamp string
        """
        return datetime.now(timezone.utc).isoformat()
    
    def log_handling_step(self, 
                         action: str, 
                         details: Dict[str, Any], 
                         status: str = "success") -> int:
        """
        Log a step in the handling pipeline.
        
        Args:
            action: Action description
            details: Additional details dictionary
            status: Step status (success, warning, error)
            
        Returns:
            Step ID
        """
        self._handling_step_id += 1
        
        log_entry = {
            "step_id": self._handling_step_id,
            "timestamp": self._get_timestamp(),
            "pipeline": "handling",
            "action": action,
            "status": status,
            "details": details
        }
        
        with open(self.handling_pipeline_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        return self._handling_step_id
    
    def log_verification_step(self,
                             action: str,
                             details: Dict[str, Any],
                             status: str = "success") -> int:
        """
        Log a step in the verification pipeline.
        
        Args:
            action: Action description
            details: Additional details dictionary
            status: Step status (success, warning, error)
            
        Returns:
            Step ID
        """
        self._verification_step_id += 1
        
        log_entry = {
            "step_id": self._verification_step_id,
            "timestamp": self._get_timestamp(),
            "pipeline": "verification",
            "action": action,
            "status": status,
            "details": details
        }
        
        with open(self.verification_pipeline_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        return self._verification_step_id
    
    def log_error(self, pipeline: str, error: str, details: Optional[Dict[str, Any]] = None):
        """
        Log an error in either pipeline.
        
        Args:
            pipeline: Pipeline name ('handling' or 'verification')
            error: Error message
            details: Optional additional details
        """
        error_details = {"error": error}
        if details:
            error_details.update(details)
        
        if pipeline == "handling":
            self.log_handling_step("error", error_details, status="error")
        elif pipeline == "verification":
            self.log_verification_step("error", error_details, status="error")
    
    def get_handling_steps(self) -> int:
        """Get current handling step count."""
        return self._handling_step_id
    
    def get_verification_steps(self) -> int:
        """Get current verification step count."""
        return self._verification_step_id
    
    def reset_counters(self):
        """Reset step counters (useful for testing)."""
        self._handling_step_id = 0
        self._verification_step_id = 0
    
    def read_handling_log(self) -> list:
        """
        Read all entries from handling pipeline log.
        
        Returns:
            List of log entry dictionaries
        """
        if not self.handling_pipeline_log.exists():
            return []
        
        entries = []
        with open(self.handling_pipeline_log, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
        return entries
    
    def read_verification_log(self) -> list:
        """
        Read all entries from verification pipeline log.
        
        Returns:
            List of log entry dictionaries
        """
        if not self.verification_pipeline_log.exists():
            return []
        
        entries = []
        with open(self.verification_pipeline_log, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
        return entries
