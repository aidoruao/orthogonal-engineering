"""
CLI entrypoint for the deterministic auditable scaffold.

Provides subcommands:
- index: Build file index and manifest
- merkle: Build Merkle tree and generate proofs
- handling-clamp: Parse and validate GTA handling.meta
- verify: Verify file integrity against manifest
- dry-run: Preview operations without modification
- backup: Create backup before operations
- restore: Restore from backup

Defaults to dry-run mode. --apply required for active modifications.
Creates a local branch for review when --apply is used.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional
import subprocess
import shutil
from datetime import datetime

from .logger import ScaffoldLogger
from .manifest import ManifestBuilder
from .merkle import MerkleTree
from .handling_pipeline import HandlingMetaParser
from .hasher import hash_file


class ScaffoldCLI:
    """Main CLI controller for the scaffold."""
    
    def __init__(self, repo_path: str = ".", config_file: Optional[str] = None, 
                 apply: bool = False, verbose: bool = False):
        """
        Initialize CLI.
        
        Args:
            repo_path: Path to repository
            config_file: Optional configuration file
            apply: If True, apply modifications (default: dry-run)
            verbose: Enable verbose output
        """
        self.repo_path = Path(repo_path).resolve()
        self.config_file = config_file
        self.apply = apply
        self.verbose = verbose
        self.logger = ScaffoldLogger(output_dir=self.repo_path / ".scaffold_logs")
        
        # Load config if provided
        self.config = {}
        if config_file:
            self._load_config(config_file)
    
    def _load_config(self, config_file: str) -> None:
        """Load configuration from file."""
        try:
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load config: {e}")
    
    def _create_branch(self, branch_name: str) -> bool:
        """
        Create a local git branch for review.
        
        Args:
            branch_name: Name of branch to create
            
        Returns:
            True if successful
        """
        try:
            result = subprocess.run(
                ['git', 'checkout', '-b', branch_name],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Warning: Failed to create branch: {e}")
            return False
    
    def _log(self, message: str) -> None:
        """Log message if verbose mode enabled."""
        if self.verbose:
            print(message)
        self.logger.log_pipeline("CLI", {"message": message})
    
    def index(self, pattern: str = "**/*", output: str = "manifest.jsonl") -> int:
        """
        Build file index and manifest.
        
        Args:
            pattern: Glob pattern for files to index
            output: Output manifest file path
            
        Returns:
            Exit code (0 = success)
        """
        self._log(f"Building index with pattern: {pattern}")
        
        if not self.apply:
            print("🔍 DRY-RUN MODE: No files will be modified")
            print(f"   Would build index for: {self.repo_path}")
            print(f"   Pattern: {pattern}")
            print(f"   Output: {output}")
            print("\n   Run with --apply to execute")
            return 0
        
        # Create branch for review
        branch_name = f"scaffold-index-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        if self._create_branch(branch_name):
            print(f"✓ Created branch: {branch_name}")
        
        # Build manifest
        manifest_path = self.repo_path / output
        checkpoint_path = self.repo_path / ".scaffold_checkpoint.json"
        
        builder = ManifestBuilder(
            output_path=manifest_path,
            checkpoint_path=checkpoint_path
        )
        
        count = 0
        for entry in builder.add_directory(self.repo_path, pattern=pattern):
            count += 1
            if count % 100 == 0:
                self._log(f"Processed {count} files...")
        
        builder.finalize()
        
        print(f"✓ Indexed {count} files")
        print(f"✓ Manifest written to: {manifest_path}")
        
        return 0
    
    def merkle(self, manifest_path: str = "manifest.jsonl", 
               output: str = "merkle_proofs.jsonl") -> int:
        """
        Build Merkle tree and generate proofs.
        
        Args:
            manifest_path: Path to manifest file
            output: Output proofs file
            
        Returns:
            Exit code (0 = success)
        """
        self._log("Building Merkle tree")
        
        manifest_file = self.repo_path / manifest_path
        
        if not manifest_file.exists():
            print(f"❌ Manifest not found: {manifest_file}")
            print("   Run 'index' command first")
            return 1
        
        if not self.apply:
            print("🔍 DRY-RUN MODE: No files will be modified")
            print(f"   Would build Merkle tree from: {manifest_path}")
            print(f"   Output: {output}")
            print("\n   Run with --apply to execute")
            return 0
        
        # Create branch
        branch_name = f"scaffold-merkle-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        if self._create_branch(branch_name):
            print(f"✓ Created branch: {branch_name}")
        
        # Build tree
        tree = MerkleTree()
        
        with open(manifest_file, 'r') as f:
            for line in f:
                entry = json.loads(line)
                file_path = self.repo_path / entry['canonical_path']
                if file_path.exists():
                    tree.add_file(file_path, entry['canonical_path'])
        
        root = tree.build()
        print(f"✓ Merkle root: {root}")
        
        # Export proofs
        proofs_path = self.repo_path / output
        tree.export_proofs(proofs_path)
        print(f"✓ Proofs written to: {proofs_path}")
        
        return 0
    
    def handling_clamp(self, meta_file: str) -> int:
        """
        Parse and validate GTA handling.meta file.
        
        Args:
            meta_file: Path to handling.meta file
            
        Returns:
            Exit code (0 = success)
        """
        self._log(f"Parsing handling.meta: {meta_file}")
        
        meta_path = self.repo_path / meta_file
        
        if not meta_path.exists():
            print(f"❌ File not found: {meta_path}")
            return 1
        
        # Parse
        parser = HandlingMetaParser()
        try:
            entries = parser.parse_file(meta_path)
            print(f"✓ Parsed {len(entries)} vehicle handling entries")
            
            # Validate
            errors = parser.validate()
            if errors:
                print("\n⚠️  Validation errors:")
                for error in errors:
                    print(f"   - {error}")
                return 1
            else:
                print("✓ Validation passed")
            
            # Show summary
            if self.verbose:
                print("\nVehicles:")
                for entry in entries:
                    print(f"  - {entry.name}: mass={entry.mass}, drag={entry.drag_multiplier}")
            
            return 0
            
        except Exception as e:
            print(f"❌ Failed to parse: {e}")
            return 1
    
    def verify(self, manifest_path: str = "manifest.jsonl") -> int:
        """
        Verify file integrity against manifest.
        
        Args:
            manifest_path: Path to manifest file
            
        Returns:
            Exit code (0 = success)
        """
        self._log("Verifying file integrity")
        
        manifest_file = self.repo_path / manifest_path
        
        if not manifest_file.exists():
            print(f"❌ Manifest not found: {manifest_file}")
            return 1
        
        errors = 0
        verified = 0
        
        with open(manifest_file, 'r') as f:
            for line in f:
                entry = json.loads(line)
                file_path = self.repo_path / entry['canonical_path']
                
                if not file_path.exists():
                    print(f"❌ Missing: {entry['canonical_path']}")
                    errors += 1
                    continue
                
                # Verify hash
                current_hash = hash_file(file_path, canonical=True)
                if current_hash != entry['canonical_hash']:
                    print(f"❌ Modified: {entry['canonical_path']}")
                    errors += 1
                else:
                    verified += 1
                    if self.verbose:
                        print(f"✓ {entry['canonical_path']}")
        
        print(f"\n✓ Verified: {verified} files")
        if errors > 0:
            print(f"❌ Errors: {errors} files")
            return 1
        
        return 0
    
    def backup(self, output_dir: str = ".scaffold_backup") -> int:
        """
        Create backup of repository.
        
        Args:
            output_dir: Output directory for backup
            
        Returns:
            Exit code (0 = success)
        """
        self._log("Creating backup")
        
        backup_path = self.repo_path / output_dir
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_path / timestamp
        
        if not self.apply:
            print("🔍 DRY-RUN MODE: No backup will be created")
            print(f"   Would backup to: {backup_path}")
            print("\n   Run with --apply to execute")
            return 0
        
        try:
            # Copy repository (excluding .git and large dirs)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Use rsync if available, otherwise manual copy
            try:
                subprocess.run([
                    'rsync', '-av',
                    '--exclude', '.git',
                    '--exclude', 'node_modules',
                    '--exclude', '__pycache__',
                    str(self.repo_path) + '/',
                    str(backup_path) + '/'
                ], check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fall back to manual copy
                shutil.copytree(
                    self.repo_path,
                    backup_path,
                    ignore=shutil.ignore_patterns('.git', 'node_modules', '__pycache__'),
                    dirs_exist_ok=True
                )
            
            print(f"✓ Backup created: {backup_path}")
            return 0
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return 1
    
    def restore(self, backup_path: str) -> int:
        """
        Restore from backup.
        
        Args:
            backup_path: Path to backup directory
            
        Returns:
            Exit code (0 = success)
        """
        self._log("Restoring from backup")
        
        backup = Path(backup_path)
        
        if not backup.exists():
            print(f"❌ Backup not found: {backup}")
            return 1
        
        if not self.apply:
            print("🔍 DRY-RUN MODE: No files will be restored")
            print(f"   Would restore from: {backup}")
            print("\n   Run with --apply to execute")
            return 0
        
        try:
            # Restore files
            for item in backup.iterdir():
                dest = self.repo_path / item.name
                if item.is_file():
                    shutil.copy2(item, dest)
                elif item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
            
            print(f"✓ Restored from: {backup}")
            return 0
            
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return 1


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Deterministic, auditable Python scaffold for repository operations",
        epilog="""
Examples:

  # Dry-run (default - preview only):
  %(prog)s index --pattern "**/*.py"
  %(prog)s merkle
  
  # Apply changes (requires --apply flag):
  %(prog)s --apply index --pattern "**/*.py"
  %(prog)s --apply merkle --output my_proofs.jsonl
  
  # Verify integrity:
  %(prog)s verify
  
  # Backup and restore:
  %(prog)s --apply backup
  %(prog)s --apply restore .scaffold_backup/20260216_123456
  
  # Parse handling.meta:
  %(prog)s handling-clamp path/to/handling.meta

All modifications create a local git branch for review.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Global options
    parser.add_argument('--repo-path', default='.', help='Path to repository (default: current dir)')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--apply', action='store_true', help='Apply modifications (default: dry-run)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # index command
    index_parser = subparsers.add_parser('index', help='Build file index and manifest')
    index_parser.add_argument('--pattern', default='**/*', help='Glob pattern for files')
    index_parser.add_argument('--output', default='manifest.jsonl', help='Output manifest file')
    
    # merkle command
    merkle_parser = subparsers.add_parser('merkle', help='Build Merkle tree and proofs')
    merkle_parser.add_argument('--manifest', default='manifest.jsonl', help='Input manifest file')
    merkle_parser.add_argument('--output', default='merkle_proofs.jsonl', help='Output proofs file')
    
    # handling-clamp command
    handling_parser = subparsers.add_parser('handling-clamp', help='Parse GTA handling.meta')
    handling_parser.add_argument('meta_file', help='Path to handling.meta file')
    
    # verify command
    verify_parser = subparsers.add_parser('verify', help='Verify file integrity')
    verify_parser.add_argument('--manifest', default='manifest.jsonl', help='Manifest file to verify against')
    
    # backup command
    backup_parser = subparsers.add_parser('backup', help='Create repository backup')
    backup_parser.add_argument('--output', default='.scaffold_backup', help='Backup directory')
    
    # restore command
    restore_parser = subparsers.add_parser('restore', help='Restore from backup')
    restore_parser.add_argument('backup_path', help='Path to backup directory')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Create CLI instance
    cli = ScaffoldCLI(
        repo_path=args.repo_path,
        config_file=args.config,
        apply=args.apply,
        verbose=args.verbose
    )
    
    # Execute command
    if args.command == 'index':
        return cli.index(pattern=args.pattern, output=args.output)
    elif args.command == 'merkle':
        return cli.merkle(manifest_path=args.manifest, output=args.output)
    elif args.command == 'handling-clamp':
        return cli.handling_clamp(meta_file=args.meta_file)
    elif args.command == 'verify':
        return cli.verify(manifest_path=args.manifest)
    elif args.command == 'backup':
        return cli.backup(output_dir=args.output)
    elif args.command == 'restore':
        return cli.restore(backup_path=args.backup_path)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
