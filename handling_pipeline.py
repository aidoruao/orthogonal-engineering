"""
Content handling pipeline for CAS operations.

Provides a pipeline for processing content through various stages:
canonicalization, hashing, backup, and storage.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from backup import BackupManager
from canonicalizer import canonicalize_file
from hasher import hash_data, hash_file
from logger import get_logger
from manifest import Manifest
from utils import ensure_dir


class HandlingPipeline:
    """Pipeline for processing content through CAS stages."""
    
    def __init__(self, 
                 dry_run: bool = True,
                 backup_dir: Optional[Path] = None,
                 output_dir: Optional[Path] = None):
        """
        Initialize handling pipeline.
        
        Args:
            dry_run: If True, no files are modified (default: True for safety)
            backup_dir: Directory for backups
            output_dir: Directory for processed output
        """
        self.dry_run = dry_run
        self.backup_manager = BackupManager(backup_dir)
        self.output_dir = Path(output_dir) if output_dir else Path("output")
        self.logger = get_logger("pipeline")
        
        if dry_run:
            self.logger.info("Pipeline initialized in DRY-RUN mode (no modifications)")
        else:
            self.logger.warning("Pipeline initialized in LIVE mode (modifications enabled)")
    
    def process_file(self, filepath: Union[str, Path], create_backup: bool = True) -> Dict[str, Any]:
        """
        Process file through pipeline.
        
        Args:
            filepath: Path to file to process
            create_backup: Whether to create backup (default: True)
            
        Returns:
            Processing result dictionary
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        result = {
            "filepath": str(filepath),
            "dry_run": self.dry_run,
            "stages": {}
        }
        
        # Stage 1: Backup (if requested and not dry-run)
        if create_backup and not self.dry_run:
            backup_path = self.backup_manager.create_backup(filepath)
            result["stages"]["backup"] = {
                "status": "success",
                "path": str(backup_path)
            }
        elif create_backup and self.dry_run:
            result["stages"]["backup"] = {
                "status": "skipped",
                "reason": "dry_run"
            }
        
        # Stage 2: Canonicalize
        try:
            canonical_content = canonicalize_file(filepath)
            result["stages"]["canonicalize"] = {
                "status": "success",
                "size": len(canonical_content)
            }
        except Exception as e:
            result["stages"]["canonicalize"] = {
                "status": "error",
                "error": str(e)
            }
            return result
        
        # Stage 3: Hash
        try:
            content_hash = hash_data(canonical_content)
            result["stages"]["hash"] = {
                "status": "success",
                "hash": content_hash
            }
        except Exception as e:
            result["stages"]["hash"] = {
                "status": "error",
                "error": str(e)
            }
            return result
        
        # Stage 4: Store (if not dry-run)
        if not self.dry_run:
            try:
                ensure_dir(self.output_dir)
                output_path = self.output_dir / f"{content_hash}{filepath.suffix}"
                
                with open(output_path, 'wb') as f:
                    f.write(canonical_content)
                
                result["stages"]["store"] = {
                    "status": "success",
                    "path": str(output_path)
                }
            except Exception as e:
                result["stages"]["store"] = {
                    "status": "error",
                    "error": str(e)
                }
        else:
            result["stages"]["store"] = {
                "status": "skipped",
                "reason": "dry_run",
                "would_store_as": f"{content_hash}{filepath.suffix}"
            }
        
        return result
    
    def process_directory(self, 
                          directory: Union[str, Path], 
                          pattern: str = "*",
                          recursive: bool = False) -> List[Dict[str, Any]]:
        """
        Process all files in directory.
        
        Args:
            directory: Directory to process
            pattern: File pattern to match
            recursive: Whether to process recursively
            
        Returns:
            List of processing results
        """
        directory = Path(directory)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        # Find matching files
        if recursive:
            files = list(directory.rglob(pattern))
        else:
            files = list(directory.glob(pattern))
        
        files = [f for f in files if f.is_file()]
        
        self.logger.info(f"Processing {len(files)} files from {directory}")
        
        results = []
        for filepath in files:
            try:
                result = self.process_file(filepath)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to process {filepath}: {e}")
                results.append({
                    "filepath": str(filepath),
                    "error": str(e)
                })
        
        return results
    
    def create_manifest(self, 
                       files: List[Union[str, Path]], 
                       name: str = "pipeline_manifest") -> Manifest:
        """
        Create manifest for processed files.
        
        Args:
            files: List of files to include in manifest
            name: Manifest name
            
        Returns:
            Manifest object
        """
        manifest = Manifest(name=name, metadata={
            "dry_run": self.dry_run,
            "created_by": "HandlingPipeline"
        })
        
        for filepath in files:
            filepath = Path(filepath)
            if filepath.exists():
                try:
                    manifest.add_entry(filepath)
                except Exception as e:
                    self.logger.error(f"Failed to add {filepath} to manifest: {e}")
        
        return manifest
