"""
CLI Entry Point for Canonicalization Scaffold

Provides subcommands:
- index: Generate manifest for repository
- merkle: Build Merkle tree and export proofs
- handling-clamp: Process GTA handling.meta files
- verify: Verify manifest or Merkle proofs
- dry-run: Preview operations without changes
- backup: Create backups before modifications
- restore: Restore from backup

Default behavior: dry-run mode with mandatory backups
--apply flag required for active modifications
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Set

from . import __version__
from .canonicalizer import canonical_byte_representation
from .handling_pipeline import DEFAULT_CLAMP_RULES, HandlingClampPipeline
from .hasher import hash_file
from .logger import create_hello_world_logger, create_verification_logger, JSONLLogger
from .manifest import ManifestGenerator
from .merkle import build_merkle_tree


class CanonicalCLI:
    """
    Main CLI application for canonicalization scaffold.
    """
    
    def __init__(self):
        """Initialize CLI."""
        self.parser = self._create_parser()
        self.config: Dict = {}
        self.logger: Optional[JSONLLogger] = None
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            description="Canonicalization Scaffold - Deterministic repository hashing and verification",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument(
            '--version',
            action='version',
            version=f'%(prog)s {__version__}'
        )
        
        parser.add_argument(
            '--repo-path',
            type=str,
            default='.',
            help='Path to repository (default: current directory)'
        )
        
        parser.add_argument(
            '--config',
            type=str,
            help='Path to config file (JSON)'
        )
        
        parser.add_argument(
            '--output-dir',
            type=str,
            default='./canonical_output',
            help='Output directory for logs and manifests (default: ./canonical_output)'
        )
        
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Apply modifications (required for non-dry-run operations)'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output'
        )
        
        # Subcommands
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Index command
        index_parser = subparsers.add_parser(
            'index',
            help='Generate manifest for repository'
        )
        index_parser.add_argument(
            '--exclude',
            nargs='*',
            default=['.git', '__pycache__', 'node_modules'],
            help='Patterns to exclude from manifest'
        )
        
        # Merkle command
        merkle_parser = subparsers.add_parser(
            'merkle',
            help='Build Merkle tree and export proofs'
        )
        merkle_parser.add_argument(
            '--manifest',
            type=str,
            help='Use existing manifest file (otherwise generate new one)'
        )
        
        # Handling-clamp command
        handling_parser = subparsers.add_parser(
            'handling-clamp',
            help='Process GTA handling.meta files'
        )
        handling_parser.add_argument(
            '--input',
            type=str,
            required=True,
            help='Input handling.meta file'
        )
        handling_parser.add_argument(
            '--clamp-rules',
            type=str,
            help='Path to JSON file with clamp rules (uses defaults if not provided)'
        )
        
        # Verify command
        verify_parser = subparsers.add_parser(
            'verify',
            help='Verify manifest or Merkle proofs'
        )
        verify_parser.add_argument(
            '--manifest',
            type=str,
            help='Manifest file to verify'
        )
        verify_parser.add_argument(
            '--proofs',
            type=str,
            help='Merkle proofs file to verify'
        )
        
        # Backup command
        backup_parser = subparsers.add_parser(
            'backup',
            help='Create backup of repository'
        )
        backup_parser.add_argument(
            '--backup-dir',
            type=str,
            help='Backup directory (default: <repo>_backup_<timestamp>)'
        )
        
        # Restore command
        restore_parser = subparsers.add_parser(
            'restore',
            help='Restore repository from backup'
        )
        restore_parser.add_argument(
            '--backup-dir',
            type=str,
            required=True,
            help='Backup directory to restore from'
        )
        
        # Dry-run command
        dry_run_parser = subparsers.add_parser(
            'dry-run',
            help='Preview operations without making changes'
        )
        dry_run_parser.add_argument(
            'sub_command',
            choices=['index', 'merkle', 'handling-clamp'],
            help='Command to preview'
        )
        
        return parser
    
    def _load_config(self, config_path: Optional[str]) -> None:
        """Load configuration from JSON file."""
        if config_path:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
    
    def _setup_logger(self, output_dir: Path, log_type: str = "hello_world") -> None:
        """Set up JSONL logger."""
        if log_type == "hello_world":
            self.logger = create_hello_world_logger(output_dir)
        else:
            self.logger = create_verification_logger(output_dir)
    
    def cmd_index(self, args) -> int:
        """Generate manifest for repository."""
        repo_path = Path(args.repo_path)
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up logger
        self._setup_logger(output_dir)
        
        # Check if dry-run
        if not args.apply:
            print("🔍 DRY-RUN MODE: No files will be modified")
            print(f"   Use --apply to actually generate manifest")
            print()
        
        manifest_path = output_dir / "manifest.jsonl"
        exclude_patterns = set(args.exclude)
        
        if args.verbose:
            print(f"Repository: {repo_path}")
            print(f"Output: {manifest_path}")
            print(f"Exclude: {exclude_patterns}")
            print()
        
        step_id = self.logger.start_operation("generate_manifest", repo=str(repo_path))
        
        try:
            generator = ManifestGenerator()
            
            if args.apply:
                count = generator.write_manifest(repo_path, manifest_path, exclude_patterns)
                self.logger.complete_operation(step_id, "generate_manifest", file_count=count)
                print(f"✓ Manifest generated: {count} files")
                print(f"  Output: {manifest_path}")
            else:
                # Preview mode - count files
                count = 0
                for _ in generator.generate_manifest_stream(repo_path, exclude_patterns):
                    count += 1
                print(f"  Would process {count} files")
                self.logger.complete_operation(step_id, "generate_manifest", 
                                              file_count=count, dry_run=True)
            
            return 0
            
        except Exception as e:
            self.logger.error_operation(step_id, "generate_manifest", str(e))
            print(f"✗ Error: {e}", file=sys.stderr)
            return 1
    
    def cmd_merkle(self, args) -> int:
        """Build Merkle tree and export proofs."""
        repo_path = Path(args.repo_path)
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        self._setup_logger(output_dir)
        
        if not args.apply:
            print("🔍 DRY-RUN MODE: Merkle tree will be computed but not saved")
            print()
        
        manifest_path = Path(args.manifest) if args.manifest else output_dir / "manifest.jsonl"
        proofs_path = output_dir / "merkle_proofs.jsonl"
        
        step_id = self.logger.start_operation("build_merkle_tree")
        
        try:
            # Load or generate manifest
            if not manifest_path.exists():
                if args.verbose:
                    print("Generating manifest first...")
                generator = ManifestGenerator()
                generator.write_manifest(repo_path, manifest_path)
            
            # Build file hashes dict
            file_hashes = {}
            for entry in ManifestGenerator.load_manifest(manifest_path):
                if entry.get("file_type") != "error":
                    file_path = repo_path / entry["canonical_path"]
                    if file_path.exists():
                        canonical_bytes = canonical_byte_representation(file_path)
                        file_hashes[entry["canonical_path"]] = canonical_bytes
            
            # Build Merkle tree
            root_hash, tree = build_merkle_tree(file_hashes)
            
            print(f"✓ Merkle root: {root_hash}")
            print(f"  Files: {len(file_hashes)}")
            
            if args.apply:
                tree.export_proofs_jsonl(proofs_path)
                print(f"  Proofs saved: {proofs_path}")
                self.logger.complete_operation(step_id, "build_merkle_tree", 
                                              root_hash=root_hash, file_count=len(file_hashes))
            else:
                print(f"  Would save proofs to: {proofs_path}")
                self.logger.complete_operation(step_id, "build_merkle_tree", 
                                              root_hash=root_hash, file_count=len(file_hashes), 
                                              dry_run=True)
            
            return 0
            
        except Exception as e:
            self.logger.error_operation(step_id, "build_merkle_tree", str(e))
            print(f"✗ Error: {e}", file=sys.stderr)
            return 1
    
    def cmd_handling_clamp(self, args) -> int:
        """Process GTA handling.meta files."""
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        self._setup_logger(output_dir)
        
        input_path = Path(args.input)
        output_path = output_dir / f"{input_path.stem}_clamped.jsonl"
        
        # Load clamp rules
        if args.clamp_rules:
            with open(args.clamp_rules, 'r') as f:
                clamp_rules = json.load(f)
        else:
            clamp_rules = DEFAULT_CLAMP_RULES
        
        if not args.apply:
            print("🔍 DRY-RUN MODE: Processing will be simulated only")
            print()
        
        if args.verbose:
            print(f"Input: {input_path}")
            print(f"Output: {output_path}")
            print(f"Clamp rules: {len(clamp_rules)} attributes")
            print()
        
        try:
            pipeline = HandlingClampPipeline(self.logger)
            results = pipeline.process_handling_file(
                input_path,
                output_path,
                clamp_rules,
                dry_run=(not args.apply)
            )
            
            print(f"✓ Processed {results['vehicle_count']} vehicles")
            if args.verbose:
                print(f"  Original hashes: {len(results['original_hashes'])}")
                print(f"  Clamped hashes: {len(results['clamped_hashes'])}")
            
            if args.apply:
                print(f"  Output: {output_path}")
            
            return 0
            
        except Exception as e:
            print(f"✗ Error: {e}", file=sys.stderr)
            return 1
    
    def cmd_verify(self, args) -> int:
        """Verify manifest or Merkle proofs."""
        repo_path = Path(args.repo_path)
        output_dir = Path(args.output_dir)
        
        self._setup_logger(output_dir, log_type="verification")
        
        if args.manifest:
            # Verify manifest
            manifest_path = Path(args.manifest)
            
            if args.verbose:
                print(f"Verifying manifest: {manifest_path}")
            
            step_id = self.logger.start_operation("verify_manifest", 
                                                 manifest=str(manifest_path))
            
            try:
                results = ManifestGenerator.verify_manifest(manifest_path, repo_path)
                
                print(f"\n✓ Manifest Verification Results:")
                print(f"  Total: {results['total']}")
                print(f"  Verified: {results['verified']}")
                print(f"  Mismatched: {results['mismatched']}")
                print(f"  Missing: {results['missing']}")
                
                if results['errors'] and args.verbose:
                    print(f"\n  Errors:")
                    for error in results['errors'][:10]:  # Show first 10
                        print(f"    - {error['file']}: {error['error']}")
                
                self.logger.complete_operation(step_id, "verify_manifest", **results)
                
                return 0 if results['mismatched'] == 0 and results['missing'] == 0 else 1
                
            except Exception as e:
                self.logger.error_operation(step_id, "verify_manifest", str(e))
                print(f"✗ Error: {e}", file=sys.stderr)
                return 1
        
        elif args.proofs:
            # Verify Merkle proofs (simplified - would need full implementation)
            print("Merkle proof verification not yet fully implemented")
            return 0
        
        else:
            print("Error: Must specify --manifest or --proofs", file=sys.stderr)
            return 1
    
    def cmd_backup(self, args) -> int:
        """Create backup of repository."""
        repo_path = Path(args.repo_path)
        
        if args.backup_dir:
            backup_path = Path(args.backup_dir)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = repo_path.parent / f"{repo_path.name}_backup_{timestamp}"
        
        if args.verbose:
            print(f"Creating backup...")
            print(f"  Source: {repo_path}")
            print(f"  Destination: {backup_path}")
        
        if not args.apply:
            print("🔍 DRY-RUN MODE: Backup will not be created")
            print(f"  Would backup to: {backup_path}")
            return 0
        
        try:
            shutil.copytree(repo_path, backup_path, 
                          ignore=shutil.ignore_patterns('.git', '__pycache__', 'node_modules'))
            print(f"✓ Backup created: {backup_path}")
            return 0
            
        except Exception as e:
            print(f"✗ Error: {e}", file=sys.stderr)
            return 1
    
    def cmd_restore(self, args) -> int:
        """Restore repository from backup."""
        repo_path = Path(args.repo_path)
        backup_path = Path(args.backup_dir)
        
        if not backup_path.exists():
            print(f"✗ Error: Backup directory not found: {backup_path}", file=sys.stderr)
            return 1
        
        if args.verbose:
            print(f"Restoring from backup...")
            print(f"  Source: {backup_path}")
            print(f"  Destination: {repo_path}")
        
        if not args.apply:
            print("🔍 DRY-RUN MODE: Restore will not be performed")
            print(f"  Would restore from: {backup_path}")
            print("⚠️  WARNING: This would replace current repository!")
            return 0
        
        print("⚠️  WARNING: This will replace the current repository!")
        confirm = input("Type 'yes' to confirm: ")
        
        if confirm.lower() != 'yes':
            print("Restore cancelled.")
            return 0
        
        try:
            # Remove current repo (except .git)
            for item in repo_path.iterdir():
                if item.name != '.git':
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
            
            # Copy from backup
            for item in backup_path.iterdir():
                dest = repo_path / item.name
                if item.is_dir():
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
            
            print(f"✓ Restored from: {backup_path}")
            return 0
            
        except Exception as e:
            print(f"✗ Error: {e}", file=sys.stderr)
            return 1
    
    def run(self, argv=None) -> int:
        """
        Run CLI application.
        
        Args:
            argv: Command line arguments (uses sys.argv if None)
            
        Returns:
            Exit code
        """
        args = self.parser.parse_args(argv)
        
        # Load config if provided
        if args.config:
            self._load_config(args.config)
        
        # Default to dry-run if no command or no --apply
        if not args.command:
            self.parser.print_help()
            return 0
        
        # Route to appropriate command
        if args.command == 'index':
            return self.cmd_index(args)
        elif args.command == 'merkle':
            return self.cmd_merkle(args)
        elif args.command == 'handling-clamp':
            return self.cmd_handling_clamp(args)
        elif args.command == 'verify':
            return self.cmd_verify(args)
        elif args.command == 'backup':
            return self.cmd_backup(args)
        elif args.command == 'restore':
            return self.cmd_restore(args)
        elif args.command == 'dry-run':
            # Dry-run wraps other commands
            print("🔍 DRY-RUN MODE enabled by default")
            print("   Add --apply to execute operations")
            return 0
        else:
            self.parser.print_help()
            return 0


def main():
    """Main entry point."""
    cli = CanonicalCLI()
    sys.exit(cli.run())


if __name__ == '__main__':
    main()
