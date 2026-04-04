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
"""
CLI module - Main entrypoint for the deterministic pipeline scaffold.

This module provides command-line interface with subcommands:
- index: Generate file manifest
- merkle: Build Merkle tree with inclusion proofs
- handling-clamp: Process GTA handling.meta files
- verify: Verify manifest integrity

Default behavior is DRY-RUN. --apply flag required for writes.

Author: Orthogonal Engineering
Date: 2026-02-16
Version: 1.0.0
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
from canonicalizer import canonicalize
from hasher import sha256_hex
from manifest import generate_manifest, ManifestGenerator
from merkle import MerkleTreeBuilder, verify_inclusion_proof
from handling_pipeline import process_handling_file
from logger import create_logger
from tools.repo_diagnoser.diagnoser import RepoDiagnoser


VERSION = "1.0.0"


def cmd_index(args):
    """Index command - generate file manifest."""
    print(f"{'DRY RUN - ' if not args.apply else ''}Indexing repository: {args.repo}")
    
    # Create logger
    logger = create_logger('indexing_pipeline')
    logger.log_start('index', {'repo': str(args.repo), 'dry_run': not args.apply})
    
    # Prepare output path
    if args.out:
        output_path = Path(args.out)
    else:
        output_path = Path(args.manifest) if args.manifest else Path('manifest.jsonl')
    
    # Prepare exclude patterns
    exclude_patterns = None
    if args.subset:
        # Subset mode - only index specific patterns
        patterns = args.subset.split(',')
    else:
        patterns = None
        # Default excludes
        exclude_patterns = [
            '.git/**',
            '**/__pycache__/**',
            '**/*.pyc',
            '**/node_modules/**',
            '**/.env'
        ]
    
    if not args.apply:
        # Dry run - just show what would be done
        logger.log_info('index', f'Would create manifest at: {output_path}')
        print(f"Would create manifest at: {output_path}")
        print(f"Repository: {args.repo}")
        if patterns:
            print(f"Patterns: {patterns}")
        if exclude_patterns:
            print(f"Exclude: {exclude_patterns}")
        logger.log_complete('index', {'dry_run': True})
        return 0
    
    # Actually generate manifest
    try:
        summary = generate_manifest(
            repo_path=Path(args.repo),
            output_path=output_path,
            patterns=patterns,
            exclude_patterns=exclude_patterns
        )
        
        print(json.dumps(summary, indent=2))
        logger.log_complete('index', summary)
        return 0
    except Exception as e:
        logger.log_error('index', str(e))
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_merkle(args):
    """Merkle command - build Merkle tree from manifest."""
    print(f"{'DRY RUN - ' if not args.apply else ''}Building Merkle tree from: {args.manifest}")
    
    # Create logger
    logger = create_logger('merkle_pipeline')
    logger.log_start('merkle', {'manifest': str(args.manifest), 'dry_run': not args.apply})
    
    # Read manifest
    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"Error: Manifest not found: {manifest_path}", file=sys.stderr)
        logger.log_error('merkle', f'Manifest not found: {manifest_path}')
        return 1
    
    # Build Merkle tree
    builder = MerkleTreeBuilder()
    
    with open(manifest_path, 'r') as f:
        for line in f:
            entry = json.loads(line)
            # Use canonical hash as the content
            canonical_bytes = bytes.fromhex(entry['canonical_hash'])
            builder.add_leaf(entry['canonical_path'], canonical_bytes)
    
    root_hash = builder.build_tree()
    
    summary = {
        'root_hash': root_hash,
        'total_leaves': len(builder.leaves)
    }
    
    print(f"Merkle Root: {root_hash}")
    print(f"Total Leaves: {len(builder.leaves)}")
    
    if not args.apply:
        logger.log_info('merkle', 'Dry run - would write proofs')
        print("Dry run - proofs not written")
        logger.log_complete('merkle', {**summary, 'dry_run': True})
        return 0
    
    # Write proofs
    if args.out:
        proofs_path = Path(args.out)
    else:
        proofs_path = manifest_path.parent / 'merkle_proofs.jsonl'
    
    builder.write_proofs(proofs_path)
    summary['proofs_path'] = str(proofs_path)
    
    print(f"Proofs written to: {proofs_path}")
    logger.log_complete('merkle', summary)
    
    return 0


def cmd_handling_clamp(args):
    """Handling-clamp command - process GTA handling.meta files."""
    print(f"{'DRY RUN - ' if not args.apply else ''}Processing handling file: {args.handling_path}")
    
    # Create logger
    logger = create_logger('hello_world_handling_pipeline')
    
    # Process file
    result = process_handling_file(
        input_path=Path(args.handling_path),
        output_dir=Path(args.out) if args.out else Path('./output'),
        dry_run=not args.apply,
        phase1=True,
        phase2=False,  # Can be made configurable
        logger=logger
    )
    
    if result['success']:
        print(json.dumps(result, indent=2))
        return 0
    else:
        print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
        return 1


def cmd_verify(args):
    """Verify command - verify manifest or Merkle proofs."""
    print(f"Verifying: {args.manifest}")
    
    # Create logger
    logger = create_logger('handling_verification_pipeline')
    logger.log_start('verify', {'manifest': str(args.manifest)})
    
    manifest_path = Path(args.manifest)
    
    if not manifest_path.exists():
        print(f"Error: File not found: {manifest_path}", file=sys.stderr)
        logger.log_error('verify', f'File not found: {manifest_path}')
        return 1
    
    # Check if it's a proof file
    if 'proof' in manifest_path.name:
        # Verify Merkle proofs
        valid_count = 0
        invalid_count = 0
        
        with open(manifest_path, 'r') as f:
            for line in f:
                proof = json.loads(line)
                if verify_inclusion_proof(proof):
                    valid_count += 1
                else:
                    invalid_count += 1
                    print(f"Invalid proof for: {proof['path']}")
        
        print(f"Valid proofs: {valid_count}")
        print(f"Invalid proofs: {invalid_count}")
        
        summary = {'valid': valid_count, 'invalid': invalid_count}
        logger.log_complete('verify', summary)
        
        return 0 if invalid_count == 0 else 1
    else:
        # Verify manifest integrity
        print("Manifest verification not yet implemented")
        logger.log_info('verify', 'Manifest verification placeholder')
        return 0


def cmd_diagnose(args) -> int:
    """Diagnose command — clone and analyse a public Git repository."""
    diagnoser = RepoDiagnoser(clone_dir=args.clone_dir)

    if args.url:
        prefix = "DRY RUN — " if not args.apply else ""
        print(f"{prefix}Cloning {args.url} …")
        if not args.apply:
            print("  (pass --apply to perform the clone and analysis)")
            return 0
        try:
            result = diagnoser.diagnose(args.url, depth=args.depth, ref=args.ref)
        except RuntimeError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
    else:
        local_path = Path(args.local)
        if not local_path.is_dir():
            print(f"Error: local path not found: {local_path}", file=sys.stderr)
            return 1
        print(f"Analysing local repository: {local_path}")
        result = diagnoser.analyze(local_path)
        result["repo_path"] = str(local_path)

    if args.out_proofs:
        if not args.apply:
            print(f"DRY RUN — would write proofs to: {args.out_proofs}")
        else:
            result["tree"].export_proofs_jsonl(Path(args.out_proofs))
            print(f"Inclusion proofs written to: {args.out_proofs}")

    print("\nDiagnosis complete.")
    summary = {
        "repo_path": result.get("repo_path", ""),
        "merkle_root": result["merkle_root"],
        "file_count": len(result["file_hashes"]),
        "scan_timestamp": result["scan"].get("scan_timestamp", ""),
    }
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"  Repo path  : {summary['repo_path']}")
        print(f"  Files      : {summary['file_count']}")
        print(f"  Merkle root: {summary['merkle_root']}")
        print(f"  Scanned at : {summary['scan_timestamp']}")
    return 0


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

    parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Generate file manifest')
    index_parser.add_argument('--repo', type=str, default='.', help='Repository path')
    index_parser.add_argument('--manifest', type=str, help='Output manifest path (deprecated, use --out)')
    index_parser.add_argument('--out', type=str, help='Output manifest path')
    index_parser.add_argument('--subset', type=str, help='Comma-separated file patterns to include')
    index_parser.add_argument('--apply', action='store_true', help='Apply changes (default is dry-run)')
    
    # Merkle command
    merkle_parser = subparsers.add_parser('merkle', help='Build Merkle tree')
    merkle_parser.add_argument('--manifest', type=str, required=True, help='Input manifest.jsonl')
    merkle_parser.add_argument('--out', type=str, help='Output proofs path')
    merkle_parser.add_argument('--apply', action='store_true', help='Apply changes (default is dry-run)')
    
    # Handling-clamp command
    handling_parser = subparsers.add_parser('handling-clamp', help='Process GTA handling.meta')
    handling_parser.add_argument('--handling-path', type=str, required=True, help='Path to handling.meta')
    handling_parser.add_argument('--out', type=str, help='Output directory')
    handling_parser.add_argument('--apply', action='store_true', help='Apply changes (default is dry-run)')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify manifest or proofs')
    verify_parser.add_argument('--manifest', type=str, required=True, help='Manifest or proof file to verify')

    # Diagnose command
    diagnose_parser = subparsers.add_parser(
        'diagnose', help='Clone and analyse a public Git repository'
    )
    diagnose_source = diagnose_parser.add_mutually_exclusive_group(required=True)
    diagnose_source.add_argument('--url', metavar='URL', help='Public Git repository URL to clone')
    diagnose_source.add_argument(
        '--local', metavar='PATH', help='Path to an already-cloned local repository'
    )
    diagnose_parser.add_argument(
        '--depth', type=int, default=1, metavar='N',
        help='Shallow-clone depth (default: 1).  Use 0 for a full clone.'
    )
    diagnose_parser.add_argument(
        '--ref', metavar='REF', default=None,
        help='Branch or tag to check out (default: repository default branch)'
    )
    diagnose_parser.add_argument(
        '--clone-dir', metavar='DIR', default='/tmp/repo_analysis',
        help='Base directory for clones (default: /tmp/repo_analysis)'
    )
    diagnose_parser.add_argument(
        '--out-proofs', metavar='FILE', default=None,
        help='Write Merkle inclusion proofs to this JSONL file (requires --apply)'
    )
    diagnose_parser.add_argument(
        '--apply', action='store_true', help='Apply changes (default is dry-run)'
    )
    diagnose_parser.add_argument(
        '--json', action='store_true', help='Print summary as JSON'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        if args.command == "hash":
            return cmd_hash(args)
        elif args.command == "process":
            return cmd_process(args)
        elif args.command == "backup":
            return cmd_backup(args)
        elif args.command == "manifest":
            return cmd_manifest(args)
        elif args.command == 'index':
            return cmd_index(args)
        elif args.command == 'merkle':
            return cmd_merkle(args)
        elif args.command == 'handling-clamp':
            return cmd_handling_clamp(args)
        elif args.command == 'verify':
            return cmd_verify(args)
        elif args.command == 'diagnose':
            return cmd_diagnose(args)
        else:
            parser.print_help()
            return 1

    except Exception as e:
        logger = get_logger("cli")
        logger.error(f"Command failed: {e}")
        if "--verbose" in sys.argv:
            raise
        return 1


if __name__ == '__main__':
    sys.exit(main())
