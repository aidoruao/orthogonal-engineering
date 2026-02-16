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
