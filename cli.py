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

from canonicalizer import canonicalize
from hasher import sha256_hex
from manifest import generate_manifest, ManifestGenerator
from merkle import MerkleTreeBuilder, verify_inclusion_proof
from handling_pipeline import process_handling_file
from logger import create_logger


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


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Deterministic Pipeline Scaffold - Default behavior is DRY-RUN',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Index repository (dry-run)
  python cli.py index --repo /path/to/repo
  
  # Index and create manifest (apply)
  python cli.py index --repo /path/to/repo --apply --out manifest.jsonl
  
  # Build Merkle tree from manifest
  python cli.py merkle --manifest manifest.jsonl --apply
  
  # Process handling file (dry-run)
  python cli.py handling-clamp --handling-path handling.meta
  
  # Process handling file (apply)
  python cli.py handling-clamp --handling-path handling.meta --apply --out ./output
  
  # Verify proofs
  python cli.py verify --manifest merkle_proofs.jsonl

Safety Notes:
  - Default behavior is DRY-RUN (no writes)
  - Use --apply flag to perform actual writes
  - Backups are created automatically before overwrites
  - No network calls or credentials used
"""
    )
    
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
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Dispatch to command handler
    if args.command == 'index':
        return cmd_index(args)
    elif args.command == 'merkle':
        return cmd_merkle(args)
    elif args.command == 'handling-clamp':
        return cmd_handling_clamp(args)
    elif args.command == 'verify':
        return cmd_verify(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
