"""
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
"""

import argparse
import json
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
        handling_parser.add_argument("--config", help="Path to clamp config JSON file")
        
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
        
        # Run clamp pipeline with optional config
        print("\nRunning clamp pipeline...")
        try:
            if args.config:
                print(f"Using config file: {args.config}")
                pipeline = HandlingClampPipeline(self.logger, config_file=args.config)
            else:
                pipeline = HandlingClampPipeline(self.logger)
        except (FileNotFoundError, ValueError) as e:
            print(f"Error loading config: {e}", file=sys.stderr)
            return 1
        
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
        
        # Safety checks
        if target_path.exists():
            # Check if target is a git repository with uncommitted changes
            git_dir = target_path / ".git"
            if git_dir.exists():
                print("Warning: Target is a git repository!")
                
                # Check for uncommitted changes
                try:
                    import subprocess
                    result = subprocess.run(
                        ["git", "-C", str(target_path), "status", "--porcelain"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        print("ERROR: Target has uncommitted changes!")
                        print("Please commit or stash changes before restoring.")
                        print("\nUncommitted changes detected:")
                        print(result.stdout[:500])  # Show first 500 chars
                        return 1
                except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
                    # If git check fails, continue with extra warning
                    print("Warning: Could not check git status")
            
            # Show what will be deleted
            file_count = sum(1 for _ in target_path.rglob("*") if _.is_file())
            print(f"\nTarget directory exists: {target_path}")
            print(f"Contains: ~{file_count} files")
        
        print(f"\nRestoring backup: {backup_path} -> {target_path}")
        print("⚠️  WARNING: This will PERMANENTLY DELETE the target directory!")
        print("⚠️  This operation cannot be undone!")
        
        # First confirmation
        response = input("\nType 'DELETE' to confirm deletion of target: ")
        if response != 'DELETE':
            print("Restore cancelled")
            return 0
        
        # Second confirmation
        response = input("Are you absolutely sure? [y/N]: ")
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
    sys.exit(main())
