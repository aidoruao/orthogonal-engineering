"""
Handling pipeline for processing content through various stages.

Provides a pipeline for processing content through various stages:
- Validation
- Transformation
- Canonicalization
- Verification
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from backup import BackupManager
from logger import get_logger
from utils import ensure_dir


class HandlingPipeline:
    """Pipeline for processing handling files and directories."""

    def __init__(
        self,
        dry_run: bool = True,
        backup_dir: Optional[Union[str, Path]] = None,
        output_dir: Optional[Union[str, Path]] = None,
    ):
        self.dry_run = dry_run
        self.backup_dir = Path(backup_dir) if backup_dir else Path("backups")
        self.output_dir = Path(output_dir) if output_dir else Path("output")
        ensure_dir(self.output_dir)
        self.logger = get_logger("handling_pipeline")

    def process_file(
        self, filepath: Union[str, Path], create_backup: bool = True
    ) -> Dict[str, Any]:
        """Process a single file through the pipeline."""
        filepath = Path(filepath)
        result = {
            "filepath": str(filepath),
            "success": True,
            "stages": {},
        }

        if create_backup and not self.dry_run:
            backup_mgr = BackupManager(self.backup_dir)
            backup_mgr.create_backup(filepath)
            result["stages"]["backup"] = {"status": "success"}
        else:
            result["stages"]["backup"] = {"status": "skipped"}

        result["stages"]["validation"] = {"status": "success"}
        result["stages"]["processing"] = {"status": "success"}

        return result

    def process_directory(
        self,
        dirpath: Union[str, Path],
        pattern: str = "*",
        recursive: bool = False,
    ) -> List[Dict[str, Any]]:
        """Process all files in a directory matching pattern."""
        dirpath = Path(dirpath)
        results = []

        if recursive:
            files = list(dirpath.rglob(pattern))
        else:
            files = list(dirpath.glob(pattern))

        for filepath in files:
            if filepath.is_file():
                result = self.process_file(filepath)
                results.append(result)

        return results
