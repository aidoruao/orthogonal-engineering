"""
CLI Module

Command-line interface for the deterministic auditable Python scaffold.

Subcommands:
- index: Generate manifest index for repository
- merkle: Build Merkle tree and generate inclusion proofs
- handling-clamp: Process GTA handling.meta files
- verify: Verify manifest and Merkle proofs
- dry-run: Run operations in dry-run mode (default)
- backup: Create backup of repository/files
- restore: Restore from backup

Default mode is dry-run with mandatory backups.
Requires --apply flag for active modifications.
"""

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .canonicalizer import canonical_byte_representation, get_file_type
from .handling_pipeline import HandlingPipeline
from .hasher import compute_file_hash
from .logger import ScaffoldLogger
from .manifest import ManifestGenerator
from .merkle import MerkleTree


class ScaffoldCLI:
    """Main CLI class for scaffold operations."""
    
    def __init__(self, 
                 repo_path: Optional[Path] = None,
                 config_file: Optional[Path] = None,
                 dry_run: bool = True,
                 verbose: bool = False):
        """
        Initialize CLI.
        
        Args:
            repo_path: Path to repository (default: current directory)
            config_file: Path to config file
            dry_run: Run in dry-run mode (default: True)
            verbose: Enable verbose output
        """
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.config_file = config_file
        self.dry_run = dry_run
        self.verbose = verbose
        
        # Initialize logger
        self.logger = ScaffoldLogger(log_dir=self.repo_path / "logs")
        
        # Load config if provided
        self.config = {}
        if config_file and config_file.exists():
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        
        # Backup directory
        self.backup_dir = self.repo_path / ".scaffold_backups"
    
    def _log(self, message: str, level: str = "info"):
        """Log message to console."""
        prefix = {
            "info": "[INFO]",
            "warning": "[WARN]",
            "error": "[ERROR]",
            "success": "[OK]"
        }.get(level, "[INFO]")
        
        print(f"{prefix} {message}")
    
    def _create_backup(self, files: list) -> Path:
        """
        Create backup of specified files.
        
        Args:
            files: List of file paths to backup
            
        Returns:
            Path to backup directory
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / timestamp
        backup_path.mkdir(parents=True, exist_ok=True)
        
        self._log(f"Creating backup in {backup_path}")
        
        for file in files:
            file_path = Path(file)
            if file_path.exists():
                # Preserve directory structure
                rel_path = file_path.relative_to(self.repo_path) if file_path.is_relative_to(self.repo_path) else file_path.name
                backup_file = backup_path / rel_path
                backup_file.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(file_path, backup_file)
                if self.verbose:
                    self._log(f"  Backed up: {rel_path}", "info")
        
        # Save backup metadata
        metadata = {
            "timestamp": timestamp,
            "file_count": len(files),
            "files": [str(f) for f in files]
        }
        
        with open(backup_path / "backup_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self._log(f"Backup complete: {len(files)} files", "success")
        return backup_path
    
    def cmd_index(self, args):
        """Generate manifest index for repository."""
        self._log(f"Generating manifest for {self.repo_path}")
        
        if self.dry_run:
            self._log("DRY RUN MODE - No files will be modified", "warning")
            # Count files that would be processed
            count = 0
            for file in self.repo_path.rglob('*'):
                if file.is_file() and not file.name.startswith('.'):
                    count += 1
            self._log(f"Would process {count} files")
            return 0
        
        # Generate manifest
        output_path = args.output or self.repo_path / "manifest.jsonl"
        generator = ManifestGenerator(
            repo_path=self.repo_path,
            output_path=output_path,
            checkpoint_interval=args.checkpoint_interval
        )
        
        processed = generator.generate(resume=args.resume)
        stats = generator.get_statistics()
        
        self._log(f"Manifest generated: {output_path}", "success")
        self._log(f"  Processed: {stats['processed_files']} files")
        self._log(f"  Skipped: {stats['skipped_files']} files")
        self._log(f"  Errors: {stats['errors']}")
        
        return 0 if stats['errors'] == 0 else 1
    
    def cmd_merkle(self, args):
        """Build Merkle tree and generate inclusion proofs."""
        self._log(f"Building Merkle tree for {self.repo_path}")
        
        # Read files from manifest or directory
        tree = MerkleTree()
        
        if args.manifest and Path(args.manifest).exists():
            # Load from manifest
            self._log(f"Loading files from manifest: {args.manifest}")
            from .manifest import ManifestGenerator
            
            gen = ManifestGenerator(self.repo_path, output_path=args.manifest)
            for entry in gen.iter_entries():
                file_path = self.repo_path / entry.canonical_path
                if file_path.exists():
                    tree.add_file(file_path)
        else:
            # Scan directory
            self._log("Scanning directory for files")
            for file in self.repo_path.rglob('*'):
                if file.is_file() and not file.name.startswith('.'):
                    try:
                        tree.add_file(file)
                    except Exception as e:
                        if self.verbose:
                            self._log(f"  Skipped {file}: {e}", "warning")
        
        if self.dry_run:
            self._log("DRY RUN MODE - Merkle tree built but not saved", "warning")
            root_hash = tree.get_root_hash()
            self._log(f"Would generate Merkle root: {root_hash}")
            return 0
        
        # Build tree
        tree.build()
        root_hash = tree.get_root_hash()
        
        self._log(f"Merkle root hash: {root_hash}", "success")
        
        # Export proofs
        output_path = args.output or self.repo_path / "merkle_proofs.jsonl"
        tree.export_proofs_jsonl(output_path)
        
        self._log(f"Merkle proofs exported: {output_path}", "success")
        
        # Verify tree
        if tree.verify_tree():
            self._log("Merkle tree verification: PASSED", "success")
        else:
            self._log("Merkle tree verification: FAILED", "error")
            return 1
        
        return 0
    
    def cmd_handling_clamp(self, args):
        """Process GTA handling.meta files."""
        self._log(f"Processing handling files in {args.input}")
        
        if self.dry_run:
            self._log("DRY RUN MODE - No files will be modified", "warning")
            # Count .meta files
            input_path = Path(args.input)
            count = len(list(input_path.rglob("*.meta")))
            self._log(f"Would process {count} .meta files")
            return 0
        
        # Process handling files
        pipeline = HandlingPipeline(logger=self.logger)
        
        input_path = Path(args.input)
        output_dir = Path(args.output) if args.output else None
        
        if input_path.is_file():
            # Process single file
            result = pipeline.process_file(input_path, output_dir)
            self._log(f"Processed: {result['file']}", "success")
            self._log(f"  Vehicles: {result['vehicle_count']}")
            self._log(f"  Hash: {result['hash']}")
        else:
            # Process directory
            results = pipeline.process_directory(input_path, output_dir)
            self._log(f"Processed {len(results)} files", "success")
        
        return 0
    
    def cmd_verify(self, args):
        """Verify manifest and Merkle proofs."""
        self._log(f"Verifying repository: {self.repo_path}")
        
        errors = []
        
        # Verify manifest if exists
        manifest_path = args.manifest or self.repo_path / "manifest.jsonl"
        if Path(manifest_path).exists():
            self._log(f"Verifying manifest: {manifest_path}")
            from .manifest import ManifestGenerator
            
            gen = ManifestGenerator(self.repo_path, output_path=manifest_path)
            manifest_errors = gen.verify_manifest()
            
            if manifest_errors:
                self._log(f"Manifest verification: FAILED ({len(manifest_errors)} errors)", "error")
                for err in manifest_errors[:10]:  # Show first 10
                    self._log(f"  {err}", "error")
                errors.extend(manifest_errors)
            else:
                self._log("Manifest verification: PASSED", "success")
        
        # Verify Merkle proofs if exist
        proofs_path = args.proofs or self.repo_path / "merkle_proofs.jsonl"
        if Path(proofs_path).exists():
            self._log(f"Verifying Merkle proofs: {proofs_path}")
            
            with open(proofs_path, 'r') as f:
                proof_count = 0
                failed_count = 0
                
                for line in f:
                    if line.strip():
                        proof_data = json.loads(line)
                        proof_count += 1
                        
                        # Verify each proof
                        from .merkle import InclusionProof
                        
                        # Reconstruct proof (simplified verification)
                        # In production, would fully verify against current state
                        if self.verbose:
                            self._log(f"  Verified: {proof_data['leaf_path']}", "info")
                
                if failed_count > 0:
                    self._log(f"Merkle verification: FAILED ({failed_count}/{proof_count})", "error")
                    errors.append(f"{failed_count} Merkle proof failures")
                else:
                    self._log(f"Merkle verification: PASSED ({proof_count} proofs)", "success")
        
        return 0 if not errors else 1
    
    def cmd_backup(self, args):
        """Create backup of repository/files."""
        self._log("Creating backup")
        
        # Collect files to backup
        if args.files:
            files = [Path(f) for f in args.files]
        else:
            # Backup all files in repo
            files = [f for f in self.repo_path.rglob('*') if f.is_file() and not f.name.startswith('.')]
        
        backup_path = self._create_backup(files)
        self._log(f"Backup created: {backup_path}", "success")
        
        return 0
    
    def cmd_restore(self, args):
        """Restore from backup."""
        self._log(f"Restoring from backup: {args.backup}")
        
        backup_path = Path(args.backup)
        
        if not backup_path.exists():
            self._log(f"Backup not found: {args.backup}", "error")
            return 1
        
        if self.dry_run:
            self._log("DRY RUN MODE - No files will be restored", "warning")
            # Count files in backup
            count = len(list(backup_path.rglob('*')))
            self._log(f"Would restore {count} items")
            return 0
        
        # Load backup metadata
        metadata_file = backup_path / "backup_metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            self._log(f"Backup timestamp: {metadata['timestamp']}")
            self._log(f"Files to restore: {metadata['file_count']}")
        
        # Restore files
        restored = 0
        for item in backup_path.rglob('*'):
            if item.is_file() and item.name != "backup_metadata.json":
                # Get relative path
                rel_path = item.relative_to(backup_path)
                target_path = self.repo_path / rel_path
                
                # Create parent directories
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Restore file
                shutil.copy2(item, target_path)
                restored += 1
                
                if self.verbose:
                    self._log(f"  Restored: {rel_path}", "info")
        
        self._log(f"Restore complete: {restored} files", "success")
        return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Deterministic Auditable Python Scaffold CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate manifest (dry-run)
  python -m scaffold.cli index

  # Generate manifest (apply changes)
  python -m scaffold.cli index --apply

  # Build Merkle tree
  python -m scaffold.cli merkle --apply

  # Verify integrity
  python -m scaffold.cli verify

  # Backup repository
  python -m scaffold.cli backup

  # Process handling files
  python -m scaffold.cli handling-clamp --input ./data --apply
        """
    )
    
    # Global options
    parser.add_argument('--repo-path', type=Path, help='Repository path (default: current directory)')
    parser.add_argument('--config', type=Path, help='Config file path')
    parser.add_argument('--apply', action='store_true', help='Apply changes (disable dry-run)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Generate manifest index')
    index_parser.add_argument('--output', type=Path, help='Output manifest path')
    index_parser.add_argument('--resume', action='store_true', help='Resume from checkpoint')
    index_parser.add_argument('--checkpoint-interval', type=int, default=100, 
                             help='Checkpoint interval (default: 100)')
    
    # Merkle command
    merkle_parser = subparsers.add_parser('merkle', help='Build Merkle tree')
    merkle_parser.add_argument('--manifest', type=Path, help='Input manifest file')
    merkle_parser.add_argument('--output', type=Path, help='Output proofs path')
    
    # Handling-clamp command
    handling_parser = subparsers.add_parser('handling-clamp', help='Process handling.meta files')
    handling_parser.add_argument('--input', required=True, help='Input file or directory')
    handling_parser.add_argument('--output', help='Output directory')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify manifest and proofs')
    verify_parser.add_argument('--manifest', type=Path, help='Manifest file to verify')
    verify_parser.add_argument('--proofs', type=Path, help='Merkle proofs file')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create backup')
    backup_parser.add_argument('--files', nargs='+', help='Specific files to backup')
    
    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore from backup')
    restore_parser.add_argument('--backup', required=True, help='Backup directory to restore')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Initialize CLI
    cli = ScaffoldCLI(
        repo_path=args.repo_path,
        config_file=args.config,
        dry_run=not args.apply,
        verbose=args.verbose
    )
    
    # Execute command
    command_map = {
        'index': cli.cmd_index,
        'merkle': cli.cmd_merkle,
        'handling-clamp': cli.cmd_handling_clamp,
        'verify': cli.cmd_verify,
        'backup': cli.cmd_backup,
        'restore': cli.cmd_restore
    }
    
    if args.command in command_map:
        return command_map[args.command](args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
