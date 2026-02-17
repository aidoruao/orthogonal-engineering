"""
Backup management with mandatory backup policy.

Ensures all operations create backups before modifications.
Safety-first approach: backups are mandatory, not optional.
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from logger import get_logger
from utils import ensure_dir, format_size


class BackupManager:
    """Manages backups with mandatory backup policy."""
    
    def __init__(self, backup_dir: Optional[Union[str, Path]] = None):
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
            backup_dir: Directory for backups (default: ./backups)
        """
        self.backup_dir = Path(backup_dir) if backup_dir else Path("backups")
        ensure_dir(self.backup_dir)
        self.logger = get_logger("backup")
    
    def create_backup(self, filepath: Union[str, Path], prefix: str = "") -> Path:
        """
        Create backup of file (MANDATORY before any modification).
        
        Args:
            filepath: File to backup
            prefix: Optional prefix for backup name
            
        Returns:
            Path to backup file
            
        Raises:
            FileNotFoundError: If source file doesn't exist
            RuntimeError: If backup creation fails
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"Cannot backup non-existent file: {filepath}")
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{prefix}{filepath.stem}_{timestamp}{filepath.suffix}"
        backup_path = self.backup_dir / backup_name
        
        # Ensure backup doesn't already exist (avoid collisions)
        counter = 1
        while backup_path.exists():
            backup_name = f"{prefix}{filepath.stem}_{timestamp}_{counter}{filepath.suffix}"
            backup_path = self.backup_dir / backup_name
            counter += 1
        
        try:
            # Copy with metadata preservation
            shutil.copy2(filepath, backup_path)
            
            file_size = backup_path.stat().st_size
            self.logger.info(
                f"Backup created: {backup_path.name}",
                original=str(filepath),
                backup=str(backup_path),
                size=format_size(file_size)
            )
            
            return backup_path
            
        except Exception as e:
            error_msg = f"Failed to create backup: {e}"
            self.logger.error(error_msg, filepath=str(filepath))
            raise RuntimeError(error_msg) from e
    
    def restore_backup(self, backup_path: Union[str, Path], target_path: Union[str, Path]) -> Path:
        """
        Restore file from backup.
        
        Args:
            backup_path: Path to backup file
            target_path: Where to restore the file
            
        Returns:
            Path to restored file
            
        Raises:
            FileNotFoundError: If backup doesn't exist
        """
        backup_path = Path(backup_path)
        target_path = Path(target_path)
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")
        
        # Ensure target directory exists
        ensure_dir(target_path.parent)
        
        # Copy backup to target
        shutil.copy2(backup_path, target_path)
        
        self.logger.info(
            f"Restored from backup: {backup_path.name}",
            backup=str(backup_path),
            restored_to=str(target_path)
        )
        
        return target_path
    
    def list_backups(self, pattern: str = "*") -> list[Path]:
        """
        List available backups.
        
        Args:
            pattern: Glob pattern for filtering backups
            
        Returns:
            List of backup file paths
        """
        return sorted(self.backup_dir.glob(pattern), reverse=True)
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """
        Clean up old backups, keeping most recent ones.
        
        Args:
            keep_count: Number of recent backups to keep
            
        Returns:
            Number of backups removed
        """
        backups = self.list_backups()
        
        if len(backups) <= keep_count:
            return 0
        
        to_remove = backups[keep_count:]
        removed_count = 0
        
        for backup in to_remove:
            try:
                backup.unlink()
                removed_count += 1
                self.logger.debug(f"Removed old backup: {backup.name}")
            except Exception as e:
                self.logger.warning(f"Failed to remove backup {backup.name}: {e}")
        
        if removed_count > 0:
            self.logger.info(f"Cleaned up {removed_count} old backups (kept {keep_count} most recent)")
        
        return removed_count


# Decorator for functions that modify files
def require_backup(backup_manager: Optional[BackupManager] = None):
    """
    Decorator to enforce backup before file modification.
    
    Args:
        backup_manager: BackupManager instance (creates one if None)
    """
    def decorator(func):
        def wrapper(filepath: Union[str, Path], *args, **kwargs):
            manager = backup_manager or BackupManager()
            
            # Create backup before modification
            filepath = Path(filepath)
            if filepath.exists():
                manager.create_backup(filepath)
            
            # Perform modification
            return func(filepath, *args, **kwargs)
        
        return wrapper
    return decorator
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
