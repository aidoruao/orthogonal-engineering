"""
Backup management with mandatory backup policy.

Ensures all operations create backups before modifications.
Safety-first approach: backups are mandatory, not optional.
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union

from logger import get_logger
from utils import ensure_dir


class BackupManager:
    """Manages backups with mandatory backup policy."""

    def __init__(self, backup_dir: Optional[Union[str, Path]] = None):
        self.backup_dir = Path(backup_dir) if backup_dir else Path("backups")
        ensure_dir(self.backup_dir)
        self.logger = get_logger("backup")

    def create_backup(self, filepath: Union[str, Path], prefix: str = "") -> Path:
        """Create backup of file (MANDATORY before any modification)."""
        filepath = Path(filepath)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{prefix}{filepath.name}_{timestamp}.bak"
        backup_path = self.backup_dir / backup_name
        shutil.copy2(filepath, backup_path)
        self.logger.info(f"Backup created: {backup_path}")
        return backup_path

    def list_backups(self, pattern: str = "*") -> List[Path]:
        """List backups matching pattern."""
        return sorted(self.backup_dir.glob(pattern))

    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """Remove old backups, keeping the most recent ones."""
        backups = self.list_backups("*.bak")
        if len(backups) <= keep_count:
            return 0
        to_remove = backups[:-keep_count]
        for backup in to_remove:
            backup.unlink()
        return len(to_remove)
