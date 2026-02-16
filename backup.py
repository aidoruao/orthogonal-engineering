"""
Backup module for creating timestamped backups with immutable manifest.

This module provides backup functionality required before any destructive writes.

Author: Orthogonal Engineering
Date: 2026-02-16
Version: 1.0.0
"""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from hasher import sha256_hex


class BackupManager:
    """Manage timestamped backups with immutable backup manifest."""
    
    def __init__(self, backup_dir: Path = None):
        """
        Initialize backup manager.
        
        Args:
            backup_dir: Directory for backups (defaults to ./backups)
        """
        if backup_dir is None:
            backup_dir = Path('./backups')
        
        self.backup_dir = backup_dir
        self.manifest_path = backup_dir / 'backup_manifest.jsonl'
        
        # Ensure backup directory exists
        backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_utc_timestamp(self) -> str:
        """Get current UTC timestamp in ISO8601 format."""
        return datetime.now(timezone.utc).isoformat()
    
    def _get_backup_id(self) -> str:
        """Generate unique backup ID based on timestamp."""
        now = datetime.now(timezone.utc)
        return now.strftime('%Y%m%d_%H%M%S_%f')
    
    def create_backup(
        self,
        file_path: Path,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Create a timestamped backup of a file.
        
        Args:
            file_path: Path to file to backup
            metadata: Optional metadata to store with backup
            
        Returns:
            Backup record dictionary
            
        Raises:
            FileNotFoundError: If source file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Cannot backup non-existent file: {file_path}")
        
        # Generate backup ID and paths
        backup_id = self._get_backup_id()
        backup_name = f"{file_path.name}.{backup_id}.backup"
        backup_path = self.backup_dir / backup_name
        
        # Read original file and compute hash
        with open(file_path, 'rb') as f:
            original_content = f.read()
        original_hash = sha256_hex(original_content)
        
        # Copy file to backup location
        shutil.copy2(file_path, backup_path)
        
        # Create backup record
        backup_record = {
            'backup_id': backup_id,
            'timestamp': self._get_utc_timestamp(),
            'original_path': str(file_path.absolute()),
            'backup_path': str(backup_path.absolute()),
            'original_hash': original_hash,
            'size_bytes': len(original_content),
            'metadata': metadata or {}
        }
        
        # Append to manifest
        with open(self.manifest_path, 'a') as f:
            f.write(json.dumps(backup_record) + '\n')
        
        return backup_record
    
    def restore_backup(self, backup_id: str) -> bool:
        """
        Restore a file from backup.
        
        Args:
            backup_id: ID of backup to restore
            
        Returns:
            True if successful, False otherwise
        """
        # Find backup record in manifest
        backup_record = None
        if self.manifest_path.exists():
            with open(self.manifest_path, 'r') as f:
                for line in f:
                    record = json.loads(line)
                    if record['backup_id'] == backup_id:
                        backup_record = record
                        break
        
        if not backup_record:
            return False
        
        # Restore file
        backup_path = Path(backup_record['backup_path'])
        original_path = Path(backup_record['original_path'])
        
        if not backup_path.exists():
            return False
        
        try:
            original_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_path, original_path)
            return True
        except Exception:
            return False
    
    def list_backups(self, original_path: Optional[Path] = None) -> List[Dict]:
        """
        List all backups, optionally filtered by original path.
        
        Args:
            original_path: Optional path to filter backups
            
        Returns:
            List of backup records
        """
        backups = []
        
        if not self.manifest_path.exists():
            return backups
        
        with open(self.manifest_path, 'r') as f:
            for line in f:
                record = json.loads(line)
                if original_path is None or record['original_path'] == str(original_path.absolute()):
                    backups.append(record)
        
        return backups
    
    def verify_backup(self, backup_id: str) -> bool:
        """
        Verify backup integrity by comparing hash.
        
        Args:
            backup_id: ID of backup to verify
            
        Returns:
            True if backup is valid, False otherwise
        """
        # Find backup record
        backup_record = None
        if self.manifest_path.exists():
            with open(self.manifest_path, 'r') as f:
                for line in f:
                    record = json.loads(line)
                    if record['backup_id'] == backup_id:
                        backup_record = record
                        break
        
        if not backup_record:
            return False
        
        backup_path = Path(backup_record['backup_path'])
        if not backup_path.exists():
            return False
        
        # Compute hash of backup file
        with open(backup_path, 'rb') as f:
            backup_content = f.read()
        backup_hash = sha256_hex(backup_content)
        
        return backup_hash == backup_record['original_hash']


def backup_before_write(file_path: Path, backup_dir: Path = None) -> Dict:
    """
    Convenience function to create backup before writing to a file.
    
    Args:
        file_path: Path to file that will be modified
        backup_dir: Optional backup directory
        
    Returns:
        Backup record
    """
    manager = BackupManager(backup_dir)
    return manager.create_backup(file_path)
