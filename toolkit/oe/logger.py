"""
Logger module for orthogonal-engineering.

Provides JSONL structured logging with ISO8601 UTC timestamps for the
canonicalization and handling pipeline operations.

Author: Orthogonal Engineering System
Date: 2026-02-16
Version: 1.0.0
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Union


class StructuredLogger:
    """JSONL structured logger for pipeline operations."""
    
    def __init__(self, output_path: Union[str, Path], auto_flush: bool = True):
        """
        Initialize structured logger.
        
        Args:
            output_path: Path to JSONL log file
            auto_flush: If True, flush after each write
        """
        self.output_path = Path(output_path)
        self.auto_flush = auto_flush
        self.file_handle = None
        self._open_log()
    
    def _open_log(self):
        """Open log file for writing."""
        # Create parent directory if needed
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Open in append mode
        self.file_handle = open(self.output_path, 'a', encoding='utf-8')
    
    def _get_timestamp(self) -> str:
        """Get current ISO8601 UTC timestamp."""
        return datetime.now(timezone.utc).isoformat()
    
    def log(self, step_id: str, event_type: str, data: Dict[str, Any] = None, **kwargs):
        """
        Log a structured event.
        
        Args:
            step_id: Identifier for the pipeline step
            event_type: Type of event (e.g., 'start', 'complete', 'error')
            data: Optional dictionary of event data
            **kwargs: Additional fields to include in log record
        """
        record = {
            'timestamp': self._get_timestamp(),
            'step_id': step_id,
            'event_type': event_type
        }
        
        if data:
            record['data'] = data
        
        # Add any additional fields
        record.update(kwargs)
        
        # Write to file
        self.file_handle.write(json.dumps(record, sort_keys=True) + '\n')
        
        if self.auto_flush:
            self.file_handle.flush()
    
    def log_hello_world(self, pipeline_name: str = "handling_pipeline"):
        """
        Log a Hello World event for the pipeline.
        
        Args:
            pipeline_name: Name of the pipeline
        """
        self.log(
            step_id='hello_world',
            event_type='greeting',
            message='Hello World from canonicalization pipeline',
            pipeline=pipeline_name
        )
    
    def close(self):
        """Close the log file."""
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class HandlingPipelineLogger(StructuredLogger):
    """Specialized logger for handling.meta pipeline operations."""
    
    def __init__(self, output_dir: Union[str, Path] = '.'):
        """
        Initialize handling pipeline logger.
        
        Args:
            output_dir: Directory for log files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Use specific filename for handling pipeline
        log_path = output_dir / 'hello_world_handling_pipeline.jsonl'
        super().__init__(log_path)
    
    def log_vehicle_clamp(self, vehicle_name: str, field: str, old_value: Any, 
                         new_value: Any, dry_run: bool = False):
        """
        Log a vehicle field clamp operation.
        
        Args:
            vehicle_name: Name of the vehicle
            field: Field being clamped
            old_value: Original value
            new_value: New (clamped) value
            dry_run: If True, this is a dry-run operation
        """
        self.log(
            step_id='vehicle_clamp',
            event_type='clamp_applied' if not dry_run else 'clamp_dry_run',
            data={
                'vehicle_name': vehicle_name,
                'field': field,
                'old_value': old_value,
                'new_value': new_value
            },
            dry_run=dry_run
        )
    
    def log_parsing_start(self, file_path: str):
        """
        Log start of handling.meta parsing.
        
        Args:
            file_path: Path to handling.meta file
        """
        self.log(
            step_id='parse_handling',
            event_type='start',
            file_path=file_path
        )
    
    def log_parsing_complete(self, file_path: str, vehicle_count: int):
        """
        Log completion of handling.meta parsing.
        
        Args:
            file_path: Path to handling.meta file
            vehicle_count: Number of vehicles parsed
        """
        self.log(
            step_id='parse_handling',
            event_type='complete',
            file_path=file_path,
            vehicle_count=vehicle_count
        )


class VerificationPipelineLogger(StructuredLogger):
    """Specialized logger for verification operations."""
    
    def __init__(self, output_dir: Union[str, Path] = '.'):
        """
        Initialize verification pipeline logger.
        
        Args:
            output_dir: Directory for log files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Use specific filename for verification
        log_path = output_dir / 'handling_verification_pipeline.jsonl'
        super().__init__(log_path)
    
    def log_hash_verification(self, file_path: str, expected_hash: str, 
                            actual_hash: str, verified: bool):
        """
        Log hash verification result.
        
        Args:
            file_path: Path to file
            expected_hash: Expected hash value
            actual_hash: Actual computed hash
            verified: Whether verification passed
        """
        self.log(
            step_id='verify_hash',
            event_type='verification_result',
            data={
                'file_path': file_path,
                'expected_hash': expected_hash,
                'actual_hash': actual_hash,
                'verified': verified
            }
        )
    
    def log_merkle_verification(self, file_path: str, root_hash: str, verified: bool):
        """
        Log Merkle proof verification result.
        
        Args:
            file_path: Path to file
            root_hash: Merkle root hash
            verified: Whether verification passed
        """
        self.log(
            step_id='verify_merkle',
            event_type='verification_result',
            data={
                'file_path': file_path,
                'root_hash': root_hash,
                'verified': verified
            }
        )
