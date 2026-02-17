"""
CLI module for orthogonal-engineering canonicalization and Merkle tree tools.

Provides command-line interface with subcommands for:
- index: Generate file index and manifest
- merkle: Build Merkle tree and generate proofs
- handling-clamp: Apply clamps to handling.meta
- verify: Verify hashes and Merkle proofs
- dry-run: Preview handling.meta changes
- backup: Create backups
- restore: Restore from backups

Author: Orthogonal Engineering System
Date: 2026-02-16
Version: 1.0.0
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List

from .canonicalizer import canonical_byte_representation
from .handling_pipeline import HandlingPipeline, VehicleClampRule
from .hasher import hash_file
from .logger import HandlingPipelineLogger, StructuredLogger, VerificationPipelineLogger
from .manifest import ManifestGenerator
from .merkle import MerkleTree


def cmd_index(args):
    """Generate file index and manifest."""
    print(f"Indexing repository: {args.repo_path}")
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize manifest generator
    generator = ManifestGenerator(args.repo_path, checkpoint_interval=args.checkpoint_interval)
    
    # Generate manifest
    manifest_path = output_dir / 'manifest.jsonl'
    
    exclude_patterns = args.exclude.split(',') if args.exclude else ['.git', '__pycache__', '*.pyc']
    
    print(f"Scanning directory...")
    generator.generate_streaming_manifest(
        manifest_path,
        directory=args.repo_path,
        pattern=args.pattern,
        exclude_patterns=exclude_patterns
    )
    
    print(f"Manifest saved to: {manifest_path}")


def cmd_merkle(args):
    """Build Merkle tree and generate proofs."""
    print(f"Building Merkle tree for: {args.repo_path}")
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load manifest or scan directory
    if args.manifest:
        print(f"Loading manifest from: {args.manifest}")
        generator = ManifestGenerator(args.repo_path)
        entries = generator.load_manifest(args.manifest)
        file_paths = [entry.file_path for entry in entries]
    else:
        print("Scanning directory for files...")
        repo_path = Path(args.repo_path)
        exclude_patterns = args.exclude.split(',') if args.exclude else ['.git', '__pycache__', '*.pyc']
        
        file_paths = []
        for file_path in repo_path.rglob('*'):
            if not file_path.is_file():
                continue
            
            # Check exclusions
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern in str(file_path):
                    should_exclude = True
                    break
            
            if not should_exclude:
                file_paths.append(str(file_path))
    
    print(f"Building Merkle tree with {len(file_paths)} files...")
    tree = MerkleTree(file_paths, base_path=args.repo_path)
    
    # Get root hash
    root_hash = tree.get_root_hash()
    print(f"Merkle root: {root_hash}")
    
    # Export proofs
    proofs_path = output_dir / 'merkle_proofs.jsonl'
    tree.export_proofs_jsonl(proofs_path)
    print(f"Proofs saved to: {proofs_path}")
    
    # Save root hash
    root_path = output_dir / 'merkle_root.txt'
    with open(root_path, 'w') as f:
        f.write(root_hash)
    print(f"Root hash saved to: {root_path}")


def cmd_handling_clamp(args):
    """Apply clamps to handling.meta file."""
    print(f"Processing handling.meta: {args.handling_file}")
    
    # Create output directory for logs
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize logger
    logger = HandlingPipelineLogger(output_dir)
    logger.log_hello_world()
    
    # Initialize pipeline
    pipeline = HandlingPipeline(args.handling_file, logger)
    
    # Load config if provided
    if args.config:
        print(f"Loading config from: {args.config}")
        with open(args.config, 'r') as f:
            config = json.load(f)
        
        # Add rules from config
        for rule_config in config.get('clamp_rules', []):
            rule = VehicleClampRule(
                field_name=rule_config['field_name'],
                min_value=rule_config.get('min_value'),
                max_value=rule_config.get('max_value'),
                allowed_values=rule_config.get('allowed_values')
            )
            pipeline.add_clamp_rule(rule)
    else:
        # Use default rules
        print("Using default clamp rules")
        pipeline.add_default_clamp_rules()
    
    # Process
    result = pipeline.process(dry_run=False, backup=args.backup)
    
    print(f"\nProcessing complete:")
    print(f"  Vehicles processed: {result['vehicles_processed']}")
    print(f"  Fields checked: {result['total_fields_checked']}")
    print(f"  Changes made: {result['changes_made']}")
    print(f"  Backup created: {result['backup_created']}")
    
    logger.close()


def cmd_verify(args):
    """Verify hashes and Merkle proofs."""
    print(f"Verifying files in: {args.repo_path}")
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize logger
    logger = VerificationPipelineLogger(output_dir)
    
    # Load manifest
    if not args.manifest:
        print("Error: --manifest is required for verification")
        return
    
    print(f"Loading manifest from: {args.manifest}")
    generator = ManifestGenerator(args.repo_path)
    entries = generator.load_manifest(args.manifest)
    
    # Verify each file
    verified_count = 0
    failed_count = 0
    
    for entry in entries:
        try:
            # Compute current hash
            actual_hash = hash_file(entry.file_path)
            verified = actual_hash == entry.canonical_hash
            
            if verified:
                verified_count += 1
            else:
                failed_count += 1
            
            # Log result
            logger.log_hash_verification(
                entry.file_path,
                entry.canonical_hash,
                actual_hash,
                verified
            )
            
            if not verified:
                print(f"FAILED: {entry.file_path}")
        except Exception as e:
            failed_count += 1
            print(f"ERROR: {entry.file_path}: {e}")
    
    print(f"\nVerification complete:")
    print(f"  Verified: {verified_count}")
    print(f"  Failed: {failed_count}")
    
    logger.close()


def cmd_dry_run(args):
    """Preview handling.meta changes without applying."""
    print(f"Dry-run for handling.meta: {args.handling_file}")
    
    # Create output directory for logs
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize logger
    logger = HandlingPipelineLogger(output_dir)
    
    # Initialize pipeline
    pipeline = HandlingPipeline(args.handling_file, logger)
    
    # Load config if provided
    if args.config:
        print(f"Loading config from: {args.config}")
        with open(args.config, 'r') as f:
            config = json.load(f)
        
        # Add rules from config
        for rule_config in config.get('clamp_rules', []):
            rule = VehicleClampRule(
                field_name=rule_config['field_name'],
                min_value=rule_config.get('min_value'),
                max_value=rule_config.get('max_value'),
                allowed_values=rule_config.get('allowed_values')
            )
            pipeline.add_clamp_rule(rule)
    else:
        # Use default rules
        print("Using default clamp rules")
        pipeline.add_default_clamp_rules()
    
    # Process in dry-run mode
    result = pipeline.process(dry_run=True, backup=False)
    
    print(f"\nDry-run complete:")
    print(f"  Vehicles processed: {result['vehicles_processed']}")
    print(f"  Fields checked: {result['total_fields_checked']}")
    print(f"  Changes that would be made: {result['changes_made']}")
    print(f"\nCheck log file for details: {output_dir}/hello_world_handling_pipeline.jsonl")
    
    logger.close()


def cmd_backup(args):
    """Create backup of handling.meta file."""
    file_path = Path(args.handling_file)
    backup_path = file_path.with_suffix('.meta.backup')
    
    import shutil
    shutil.copy2(file_path, backup_path)
    
    print(f"Backup created: {backup_path}")


def cmd_restore(args):
    """Restore handling.meta from backup."""
    file_path = Path(args.handling_file)
    backup_path = file_path.with_suffix('.meta.backup')
    
    if not backup_path.exists():
        print(f"Error: Backup not found: {backup_path}")
        return
    
    import shutil
    shutil.copy2(backup_path, file_path)
    
    print(f"Restored from backup: {backup_path}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Canonicalization and Merkle tree tools for orthogonal-engineering',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Index command
    parser_index = subparsers.add_parser('index', help='Generate file index and manifest')
    parser_index.add_argument('repo_path', help='Path to repository')
    parser_index.add_argument('--output-dir', default='./canon_output', help='Output directory')
    parser_index.add_argument('--pattern', help='Glob pattern to filter files')
    parser_index.add_argument('--exclude', help='Comma-separated exclusion patterns')
    parser_index.add_argument('--checkpoint-interval', type=int, default=100, help='Checkpoint interval')
    parser_index.set_defaults(func=cmd_index)
    
    # Merkle command
    parser_merkle = subparsers.add_parser('merkle', help='Build Merkle tree and generate proofs')
    parser_merkle.add_argument('repo_path', help='Path to repository')
    parser_merkle.add_argument('--output-dir', default='./canon_output', help='Output directory')
    parser_merkle.add_argument('--manifest', help='Use existing manifest file')
    parser_merkle.add_argument('--exclude', help='Comma-separated exclusion patterns')
    parser_merkle.set_defaults(func=cmd_merkle)
    
    # Handling-clamp command
    parser_clamp = subparsers.add_parser('handling-clamp', help='Apply clamps to handling.meta')
    parser_clamp.add_argument('handling_file', help='Path to handling.meta file')
    parser_clamp.add_argument('--output-dir', default='./canon_output', help='Output directory for logs')
    parser_clamp.add_argument('--config', help='Path to config JSON file')
    parser_clamp.add_argument('--no-backup', dest='backup', action='store_false', help='Skip backup creation')
    parser_clamp.set_defaults(func=cmd_handling_clamp)
    
    # Verify command
    parser_verify = subparsers.add_parser('verify', help='Verify hashes and Merkle proofs')
    parser_verify.add_argument('repo_path', help='Path to repository')
    parser_verify.add_argument('--manifest', required=True, help='Path to manifest file')
    parser_verify.add_argument('--output-dir', default='./canon_output', help='Output directory')
    parser_verify.set_defaults(func=cmd_verify)
    
    # Dry-run command
    parser_dry = subparsers.add_parser('dry-run', help='Preview handling.meta changes')
    parser_dry.add_argument('handling_file', help='Path to handling.meta file')
    parser_dry.add_argument('--output-dir', default='./canon_output', help='Output directory for logs')
    parser_dry.add_argument('--config', help='Path to config JSON file')
    parser_dry.set_defaults(func=cmd_dry_run)
    
    # Backup command
    parser_backup = subparsers.add_parser('backup', help='Create backup of handling.meta')
    parser_backup.add_argument('handling_file', help='Path to handling.meta file')
    parser_backup.set_defaults(func=cmd_backup)
    
    # Restore command
    parser_restore = subparsers.add_parser('restore', help='Restore from backup')
    parser_restore.add_argument('handling_file', help='Path to handling.meta file')
    parser_restore.set_defaults(func=cmd_restore)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    args.func(args)


if __name__ == '__main__':
    main()
