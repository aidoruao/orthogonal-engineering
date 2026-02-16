#!/usr/bin/env python3
"""
CAS CLI - Command-line interface for content-addressable storage operations.

Safety-first design:
- Dry-run mode by default
- Mandatory backups for modifications
- No automatic git push
- Local-only operations

Example usage:
    python cli.py hash file.txt
    python cli.py process file.txt --dry-run
    python cli.py manifest create files/*.txt
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from backup import BackupManager
from handling_pipeline import HandlingPipeline
from hasher import hash_file
from logger import get_logger
from manifest import Manifest
from utils import format_size


def cmd_hash(args):
    """Hash a file or files."""
    logger = get_logger("cli")
    
    for filepath in args.files:
        filepath = Path(filepath)
        
        if not filepath.exists():
            logger.error(f"File not found: {filepath}")
            continue
        
        try:
            file_hash = hash_file(filepath)
            size = format_size(filepath.stat().st_size)
            print(f"{file_hash}  {filepath} ({size})")
        except Exception as e:
            logger.error(f"Failed to hash {filepath}: {e}")


def cmd_process(args):
    """Process files through pipeline."""
    logger = get_logger("cli")
    
    pipeline = HandlingPipeline(
        dry_run=args.dry_run,
        backup_dir=args.backup_dir,
        output_dir=args.output_dir
    )
    
    results = []
    
    for filepath in args.files:
        filepath = Path(filepath)
        
        if not filepath.exists():
            logger.error(f"File not found: {filepath}")
            continue
        
        if filepath.is_dir():
            # Process directory
            dir_results = pipeline.process_directory(
                filepath,
                pattern=args.pattern or "*",
                recursive=args.recursive
            )
            results.extend(dir_results)
        else:
            # Process single file
            result = pipeline.process_file(filepath, create_backup=not args.no_backup)
            results.append(result)
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for result in results:
            status = "✓" if all(
                s.get("status") in ["success", "skipped"] 
                for s in result.get("stages", {}).values()
            ) else "✗"
            print(f"{status} {result['filepath']}")
            
            if args.verbose:
                for stage, details in result.get("stages", {}).items():
                    print(f"  {stage}: {details.get('status')}")


def cmd_backup(args):
    """Manage backups."""
    backup_manager = BackupManager(args.backup_dir)
    logger = get_logger("cli")
    
    if args.action == "create":
        for filepath in args.files:
            filepath = Path(filepath)
            if filepath.exists():
                backup_path = backup_manager.create_backup(filepath)
                print(f"Backup created: {backup_path}")
            else:
                logger.error(f"File not found: {filepath}")
    
    elif args.action == "list":
        backups = backup_manager.list_backups(args.pattern or "*")
        print(f"Found {len(backups)} backups:")
        for backup in backups:
            size = format_size(backup.stat().st_size)
            print(f"  {backup.name} ({size})")
    
    elif args.action == "cleanup":
        count = backup_manager.cleanup_old_backups(keep_count=args.keep)
        print(f"Removed {count} old backups (kept {args.keep} most recent)")


def cmd_manifest(args):
    """Manage manifests."""
    logger = get_logger("cli")
    
    if args.action == "create":
        manifest = Manifest(name=args.name or "manifest")
        
        for filepath in args.files:
            filepath = Path(filepath)
            if filepath.exists():
                manifest.add_entry(filepath)
            else:
                logger.warning(f"Skipping missing file: {filepath}")
        
        output_path = Path(args.output or "manifest.json")
        manifest.save(output_path)
        print(f"Manifest created: {output_path}")
        print(f"  Entries: {len(manifest.entries)}")
        print(f"  Merkle root: {manifest.get_merkle_root()}")
    
    elif args.action == "verify":
        manifest_path = Path(args.manifest)
        manifest = Manifest.load(manifest_path)
        
        results = manifest.verify()
        
        print(f"Verification results for {manifest_path}:")
        print(f"  Total: {results['total']}")
        print(f"  Valid: {results['valid']}")
        print(f"  Invalid: {results['invalid']}")
        print(f"  Missing: {results['missing']}")
        print(f"  Status: {'✓ VERIFIED' if results['verified'] else '✗ FAILED'}")
        
        if args.verbose:
            for detail in results['details']:
                status_symbol = "✓" if detail['status'] == "valid" else "✗"
                print(f"  {status_symbol} {detail['path']} ({detail['status']})")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CAS CLI - Content-Addressable Storage Operations",
        epilog="Safety-first: Dry-run mode by default, backups mandatory, no auto-push"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Hash command
    hash_parser = subparsers.add_parser("hash", help="Compute SHA-256 hash of files")
    hash_parser.add_argument("files", nargs="+", help="Files to hash")
    
    # Process command
    process_parser = subparsers.add_parser("process", help="Process files through pipeline")
    process_parser.add_argument("files", nargs="+", help="Files or directories to process")
    process_parser.add_argument("--dry-run", action="store_true", default=True,
                               help="Dry-run mode (default: True)")
    process_parser.add_argument("--live", dest="dry_run", action="store_false",
                               help="Live mode (disables dry-run)")
    process_parser.add_argument("--no-backup", action="store_true",
                               help="Skip backup creation (NOT RECOMMENDED)")
    process_parser.add_argument("--backup-dir", type=str,
                               help="Backup directory (default: ./backups)")
    process_parser.add_argument("--output-dir", type=str,
                               help="Output directory (default: ./output)")
    process_parser.add_argument("--pattern", type=str,
                               help="File pattern for directories (default: *)")
    process_parser.add_argument("--recursive", action="store_true",
                               help="Process directories recursively")
    process_parser.add_argument("--json", action="store_true",
                               help="Output results as JSON")
    process_parser.add_argument("--verbose", action="store_true",
                               help="Verbose output")
    
    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Manage backups")
    backup_parser.add_argument("action", choices=["create", "list", "cleanup"],
                              help="Backup action")
    backup_parser.add_argument("files", nargs="*", help="Files to backup")
    backup_parser.add_argument("--backup-dir", type=str,
                              help="Backup directory (default: ./backups)")
    backup_parser.add_argument("--pattern", type=str,
                              help="Pattern for listing backups")
    backup_parser.add_argument("--keep", type=int, default=10,
                              help="Number of backups to keep when cleaning up")
    
    # Manifest command
    manifest_parser = subparsers.add_parser("manifest", help="Manage manifests")
    manifest_parser.add_argument("action", choices=["create", "verify"],
                                help="Manifest action")
    manifest_parser.add_argument("files", nargs="*", help="Files for manifest")
    manifest_parser.add_argument("--manifest", type=str,
                                help="Manifest file path (for verify)")
    manifest_parser.add_argument("--name", type=str,
                                help="Manifest name (for create)")
    manifest_parser.add_argument("--output", type=str,
                                help="Output path (for create)")
    manifest_parser.add_argument("--verbose", action="store_true",
                                help="Verbose output")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        if args.command == "hash":
            cmd_hash(args)
        elif args.command == "process":
            cmd_process(args)
        elif args.command == "backup":
            cmd_backup(args)
        elif args.command == "manifest":
            cmd_manifest(args)
        else:
            parser.print_help()
            return 1
        
        return 0
        
    except Exception as e:
        logger = get_logger("cli")
        logger.error(f"Command failed: {e}")
        if "--verbose" in sys.argv:
            raise
        return 1


if __name__ == "__main__":
    sys.exit(main())
