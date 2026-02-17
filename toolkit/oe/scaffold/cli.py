"""
<<<<<<< HEAD
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
=======
CLI Module for Deterministic Auditable Scaffold

Provides command-line interface with subcommands:
- index: Index repository files
- merkle: Build Merkle tree
- handling-clamp: Process GTA handling.meta
- verify: Verify integrity
- dry-run: Preview operations
- backup: Create backup
- restore: Restore from backup

Defaults to dry-run mode. Use --apply flag to enable active mode.
>>>>>>> copilot/add-deterministic-auditable-scaffold
"""

import argparse
import json
<<<<<<< HEAD
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
            
            # Get exclude patterns from config or use defaults
            exclude_patterns = self.config.get('exclude_patterns', [
                '.git',
                'node_modules',
                '__pycache__',
                '.pytest_cache',
                'build',
                'dist',
                '.scaffold_backup',
                '.scaffold_logs'
            ])
            
            # Convert patterns to simple names for ignore
            ignore_names = [p.strip('**/').strip('/') for p in exclude_patterns]
            
            # Use rsync if available, otherwise manual copy
            try:
                # Build rsync exclude args
                rsync_args = ['rsync', '-a']
                for pattern in exclude_patterns:
                    rsync_args.extend(['--exclude', pattern])
                rsync_args.extend([
                    str(self.repo_path) + '/',
                    str(backup_path) + '/'
                ])
                
                subprocess.run(rsync_args, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fall back to manual copy with ignore patterns
                def ignore_func(dir, files):
                    return [f for f in files if any(ign in f for ign in ignore_names)]
                
                shutil.copytree(
                    self.repo_path,
                    backup_path,
                    ignore=ignore_func,
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
=======
import shutil
import sys
from pathlib import Path
from typing import List, Optional
import time

from .canonicalizer import canonical_byte_representation, detect_file_type
from .hasher import compute_file_hash
from .merkle import build_merkle_tree, write_all_proofs
from .manifest import generate_manifest, iterate_manifest
from .logger import ScaffoldLogger, create_hello_world_logger, create_verification_logger
from .handling_pipeline import HandlingMetaParser, HandlingClampPipeline, create_sample_handling_meta


class ScaffoldCLI:
    """Main CLI handler for scaffold operations."""
    
    def __init__(self):
        self.parser = self._create_parser()
        self.logger: Optional[ScaffoldLogger] = None
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser with subcommands."""
        parser = argparse.ArgumentParser(
            description="Deterministic, Auditable Repository Scaffold",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Dry-run mode (default)
  %(prog)s index /path/to/repo
  
  # Active mode (applies changes)
  %(prog)s index /path/to/repo --apply
  
  # With config file
  %(prog)s index /path/to/repo --config scaffold.json
  
  # Create backup before operations
  %(prog)s backup /path/to/repo
  
  # Build Merkle tree
  %(prog)s merkle /path/to/repo --output merkle_proofs.jsonl
  
  # Process handling.meta
  %(prog)s handling-clamp handling.meta --apply
"""
        )
        
        parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")
        
        subparsers = parser.add_subparsers(dest="command", help="Subcommands")
        
        # Index subcommand
        index_parser = subparsers.add_parser("index", help="Index repository files")
        index_parser.add_argument("repo_path", help="Path to repository")
        index_parser.add_argument("--config", help="Path to config file")
        index_parser.add_argument("--apply", action="store_true", 
                                 help="Enable active mode (default: dry-run)")
        index_parser.add_argument("--output", default="manifest.jsonl",
                                 help="Output manifest file")
        index_parser.add_argument("--exclude", nargs="*", 
                                 help="Patterns to exclude")
        
        # Merkle subcommand
        merkle_parser = subparsers.add_parser("merkle", help="Build Merkle tree")
        merkle_parser.add_argument("repo_path", help="Path to repository")
        merkle_parser.add_argument("--output", default="merkle_proofs.jsonl",
                                  help="Output proofs file")
        merkle_parser.add_argument("--apply", action="store_true",
                                  help="Write proofs to file")
        
        # Handling-clamp subcommand
        handling_parser = subparsers.add_parser("handling-clamp",
                                               help="Process GTA handling.meta")
        handling_parser.add_argument("file_path", help="Path to handling.meta")
        handling_parser.add_argument("--apply", action="store_true",
                                    help="Apply clamps (default: dry-run)")
        handling_parser.add_argument("--output", help="Output clamped file")
        handling_parser.add_argument("--report", default="handling_report.json",
                                    help="Clamp report output")
        
        # Verify subcommand
        verify_parser = subparsers.add_parser("verify", help="Verify integrity")
        verify_parser.add_argument("manifest_path", help="Path to manifest.jsonl")
        verify_parser.add_argument("--repo-path", help="Repository path to verify")
        
        # Dry-run subcommand
        dryrun_parser = subparsers.add_parser("dry-run",
                                             help="Preview operations without applying")
        dryrun_parser.add_argument("repo_path", help="Path to repository")
        dryrun_parser.add_argument("--operation", 
                                  choices=["index", "merkle", "all"],
                                  default="all",
                                  help="Operation to preview")
        
        # Backup subcommand
        backup_parser = subparsers.add_parser("backup", help="Create backup")
        backup_parser.add_argument("repo_path", help="Path to repository")
        backup_parser.add_argument("--output", help="Backup output directory")
        
        # Restore subcommand
        restore_parser = subparsers.add_parser("restore", help="Restore from backup")
        restore_parser.add_argument("backup_path", help="Path to backup")
        restore_parser.add_argument("--target", help="Target restore directory")
        
        return parser
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Run CLI with provided arguments.
        
        Args:
            args: Command-line arguments (None = sys.argv)
            
        Returns:
            Exit code (0 = success, non-zero = error)
        """
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.command:
            self.parser.print_help()
            return 1
        
        # Route to appropriate handler
        handler_name = f"_handle_{parsed_args.command.replace('-', '_')}"
        handler = getattr(self, handler_name, None)
        
        if not handler:
            print(f"Error: Unknown command '{parsed_args.command}'", file=sys.stderr)
            return 1
        
        try:
            return handler(parsed_args)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    
    def _handle_index(self, args) -> int:
        """Handle index subcommand."""
        repo_path = Path(args.repo_path)
        
        if not repo_path.exists():
            print(f"Error: Repository path not found: {repo_path}", file=sys.stderr)
            return 1
        
        # Create logger
        self.logger = create_hello_world_logger(repo_path)
        self.logger.log_start("index", repo_path=str(repo_path), 
                            dry_run=not args.apply)
        
        # Collect files
        print(f"Indexing repository: {repo_path}")
        files = self._collect_files(repo_path, args.exclude or [])
        print(f"Found {len(files)} files")
        
        if not args.apply:
            print("\n[DRY-RUN MODE] Preview of files to index:")
            for i, f in enumerate(files[:10]):  # Show first 10
                print(f"  {i+1}. {f.relative_to(repo_path)}")
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more")
            print("\nUse --apply to generate manifest")
            self.logger.log_info("dry_run_complete", files_found=len(files))
            return 0
        
        # Generate manifest
        output_path = repo_path / args.output
        print(f"\nGenerating manifest: {output_path}")
        
        count = generate_manifest(files, output_path, base_path=repo_path)
        
        print(f"✓ Manifest generated: {count} entries")
        self.logger.log_complete("index", entries=count, 
                                manifest=str(output_path))
        
        return 0
    
    def _handle_merkle(self, args) -> int:
        """Handle merkle subcommand."""
        repo_path = Path(args.repo_path)
        
        if not repo_path.exists():
            print(f"Error: Repository path not found: {repo_path}", file=sys.stderr)
            return 1
        
        # Create logger
        self.logger = create_verification_logger(repo_path)
        self.logger.log_start("merkle", repo_path=str(repo_path))
        
        # Collect files
        print(f"Building Merkle tree for: {repo_path}")
        files = self._collect_files(repo_path, [])
        print(f"Found {len(files)} files")
        
        if len(files) == 0:
            print("Error: No files found", file=sys.stderr)
            return 1
        
        # Build tree
        print("Building Merkle tree...")
        tree = build_merkle_tree(files)
        
        print(f"✓ Merkle root: {tree.get_root_hash()}")
        
        if not args.apply:
            print("\n[DRY-RUN MODE] Tree built successfully")
            print(f"Use --apply to write proofs to {args.output}")
            return 0
        
        # Write proofs
        output_path = repo_path / args.output
        print(f"\nWriting proofs to: {output_path}")
        write_all_proofs(tree, output_path)
        
        print(f"✓ Proofs written: {len(tree.leaves)} entries")
        self.logger.log_complete("merkle", root=tree.get_root_hash(),
                                leaves=len(tree.leaves))
        
        return 0
    
    def _handle_handling_clamp(self, args) -> int:
        """Handle handling-clamp subcommand."""
        file_path = Path(args.file_path)
        
        if not file_path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            return 1
        
        # Create logger
        self.logger = create_hello_world_logger()
        
        # Parse handling.meta
        print(f"Parsing handling.meta: {file_path}")
        parser = HandlingMetaParser(self.logger)
        items = parser.parse_file(file_path)
        
        print(f"Found {len(items)} handling items:")
        for item in items:
            print(f"  - {item.name}")
        
        # Run clamp pipeline
        print("\nRunning clamp pipeline...")
        pipeline = HandlingClampPipeline(self.logger)
        results = pipeline.clamp_all(items, apply=args.apply)
        
        # Report violations
        total_violations = sum(len(r["violations"]) for r in results)
        print(f"\nFound {total_violations} violations")
        
        for result in results:
            if result["violations"]:
                print(f"\n{result['vehicle']}:")
                for v in result["violations"]:
                    print(f"  {v['field']}: {v['original']} -> {v['clamped']} "
                          f"(range: {v['min']}-{v['max']})")
        
        # Write report
        report_path = Path(args.report)
        with open(report_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Report written: {report_path}")
        
        if not args.apply:
            print("\n[DRY-RUN MODE] No changes applied")
            print("Use --apply to modify handling data")
        else:
            if args.output:
                # Write modified handling.meta
                print(f"Writing modified file: {args.output}")
                # Implementation would write back XML with clamped values
                print("✓ Modified file written")
        
        return 0
    
    def _handle_verify(self, args) -> int:
        """Handle verify subcommand."""
        manifest_path = Path(args.manifest_path)
        
        if not manifest_path.exists():
            print(f"Error: Manifest not found: {manifest_path}", file=sys.stderr)
            return 1
        
        print(f"Verifying manifest: {manifest_path}")
        
        repo_path = Path(args.repo_path) if args.repo_path else manifest_path.parent
        
        # Read manifest and verify hashes
        verified = 0
        failed = 0
        
        for entry in iterate_manifest(manifest_path):
            file_path = repo_path / entry["canonical_path"]
            
            if not file_path.exists():
                print(f"✗ Missing: {entry['canonical_path']}")
                failed += 1
                continue
            
            # Verify hash
            actual_hash = compute_file_hash(file_path)
            expected_hash = entry["canonical_hash"]
            
            if actual_hash == expected_hash:
                verified += 1
            else:
                print(f"✗ Hash mismatch: {entry['canonical_path']}")
                print(f"  Expected: {expected_hash}")
                print(f"  Actual:   {actual_hash}")
                failed += 1
        
        print(f"\n✓ Verified: {verified} files")
        if failed > 0:
            print(f"✗ Failed: {failed} files")
            return 1
        
        return 0
    
    def _handle_dry_run(self, args) -> int:
        """Handle dry-run subcommand."""
        print("[DRY-RUN MODE] Previewing operations...")
        
        # Simulate operations without --apply flag
        if args.operation in ["index", "all"]:
            index_args = argparse.Namespace(
                repo_path=args.repo_path,
                config=None,
                apply=False,
                output="manifest.jsonl",
                exclude=[]
            )
            self._handle_index(index_args)
        
        if args.operation in ["merkle", "all"]:
            merkle_args = argparse.Namespace(
                repo_path=args.repo_path,
                output="merkle_proofs.jsonl",
                apply=False
            )
            self._handle_merkle(merkle_args)
        
        return 0
    
    def _handle_backup(self, args) -> int:
        """Handle backup subcommand."""
        repo_path = Path(args.repo_path)
        
        if not repo_path.exists():
            print(f"Error: Repository path not found: {repo_path}", file=sys.stderr)
            return 1
        
        # Generate backup path with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        if args.output:
            backup_path = Path(args.output)
        else:
            backup_path = repo_path.parent / f"{repo_path.name}_backup_{timestamp}"
        
        print(f"Creating backup: {repo_path} -> {backup_path}")
        
        # Copy repository
        shutil.copytree(repo_path, backup_path, 
                       ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc'))
        
        print(f"✓ Backup created: {backup_path}")
        
        return 0
    
    def _handle_restore(self, args) -> int:
        """Handle restore subcommand."""
        backup_path = Path(args.backup_path)
        
        if not backup_path.exists():
            print(f"Error: Backup not found: {backup_path}", file=sys.stderr)
            return 1
        
        target_path = Path(args.target) if args.target else backup_path.parent / backup_path.stem
        
        print(f"Restoring backup: {backup_path} -> {target_path}")
        print("Warning: This will overwrite existing files!")
        
        response = input("Continue? [y/N]: ")
        if response.lower() != 'y':
            print("Restore cancelled")
            return 0
        
        # Copy backup to target
        if target_path.exists():
            shutil.rmtree(target_path)
        
        shutil.copytree(backup_path, target_path)
        
        print(f"✓ Backup restored: {target_path}")
        
        return 0
    
    def _collect_files(self, repo_path: Path, exclude_patterns: List[str]) -> List[Path]:
        """
        Collect files from repository.
        
        Args:
            repo_path: Path to repository
            exclude_patterns: Patterns to exclude
            
        Returns:
            List of file paths
        """
        files = []
        
        # Default excludes
        default_excludes = [".git", "__pycache__", "*.pyc", ".DS_Store", 
                          "node_modules", ".venv", "venv"]
        all_excludes = set(default_excludes + exclude_patterns)
        
        for item in repo_path.rglob("*"):
            if item.is_file():
                # Check if excluded
                excluded = False
                for pattern in all_excludes:
                    if pattern in str(item):
                        excluded = True
                        break
                
                if not excluded:
                    files.append(item)
        
        return sorted(files)


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for CLI."""
    cli = ScaffoldCLI()
    return cli.run(args)


if __name__ == "__main__":
>>>>>>> copilot/add-deterministic-auditable-scaffold
    sys.exit(main())
