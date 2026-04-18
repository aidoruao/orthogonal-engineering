#!/usr/bin/env python3
"""
CAS CLI - Command-line interface for content-addressable storage operations.

Safety-first design:
- Dry-run mode by default
- Mandatory backups for modifications
- No automatic git push
- Local-only operations

Subcommands:
  hash            Compute SHA-256 hash of files
  process         Process files through pipeline
  backup          Manage backups
  manifest        Manage manifests
  index           Generate file manifest
  merkle          Build Merkle tree from manifest
  handling-clamp  Process GTA handling.meta files
  verify          Verify manifest or Merkle proofs
  classify        Classify artifact state with configurable thresholds

Example usage:
    python cli.py hash file.txt
    python cli.py process file.txt --dry-run
    python cli.py manifest create files/*.txt
    python cli.py index --repo /path/to/repo
    python cli.py merkle --manifest manifest.jsonl --apply

Author: Orthogonal Engineering
Date: 2026-02-16
Version: 1.0.0
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from backup import BackupManager
from handling_pipeline import HandlingPipeline
from hasher import hash_file, sha256_hex
from logger import get_logger, create_logger
from manifest import Manifest, generate_manifest
from merkle import MerkleTreeBuilder, verify_inclusion_proof
from threshold_loader import load_thresholds
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
        output_dir=args.output_dir,
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
                filepath, pattern=args.pattern or "*", recursive=args.recursive
            )
            results.extend(dir_results)
        else:
            # Process single file
            result = pipeline.process_file(
                filepath, create_backup=not args.no_backup
            )
            results.append(result)

    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for result in results:
            status = (
                "✓"
                if all(
                    s.get("status") in ["success", "skipped"]
                    for s in result.get("stages", {}).values()
                )
                else "✗"
            )
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
        print(
            f"  Status: {'✓ VERIFIED' if results['verified'] else '✗ FAILED'}"
        )

        if args.verbose:
            for detail in results["details"]:
                status_symbol = "✓" if detail["status"] == "valid" else "✗"
                print(f"  {status_symbol} {detail['path']} ({detail['status']})")


def cmd_index(args):
    """Index command - generate file manifest."""
    print(
        f"{'DRY RUN - ' if not args.apply else ''}Indexing repository: {args.repo}"
    )

    # Create logger
    logger = create_logger("indexing_pipeline")
    logger.log_start("index", {"repo": str(args.repo), "dry_run": not args.apply})

    # Prepare output path
    if args.out:
        output_path = Path(args.out)
    else:
        output_path = (
            Path(args.manifest) if args.manifest else Path("manifest.jsonl")
        )

    # Prepare exclude patterns
    exclude_patterns = None
    if args.subset:
        # Subset mode - only index specific patterns
        patterns = args.subset.split(",")
    else:
        patterns = None
        # Default excludes
        exclude_patterns = [
            ".git/**",
            "**/__pycache__/**",
            "**/*.pyc",
            "**/node_modules/**",
            "**/.env",
        ]

    if not args.apply:
        # Dry run - just show what would be done
        logger.log_info("index", f"Would create manifest at: {output_path}")
        print(f"Would create manifest at: {output_path}")
        print(f"Repository: {args.repo}")
        if patterns:
            print(f"Patterns: {patterns}")
        if exclude_patterns:
            print(f"Exclude: {exclude_patterns}")
        logger.log_complete("index", {"dry_run": True})
        return 0

    # Actually generate manifest
    try:
        summary = generate_manifest(
            repo_path=Path(args.repo),
            output_path=output_path,
            patterns=patterns,
            exclude_patterns=exclude_patterns,
        )

        print(json.dumps(summary, indent=2))
        logger.log_complete("index", summary)
        return 0
    except Exception as e:
        logger.log_error("index", str(e))
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_merkle(args):
    """Merkle command - build Merkle tree from manifest."""
    print(
        f"{'DRY RUN - ' if not args.apply else ''}Building Merkle tree from: {args.manifest}"
    )

    # Create logger
    logger = create_logger("merkle_pipeline")
    logger.log_start(
        "merkle", {"manifest": str(args.manifest), "dry_run": not args.apply}
    )

    # Read manifest
    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"Error: Manifest not found: {manifest_path}", file=sys.stderr)
        logger.log_error("merkle", f"Manifest not found: {manifest_path}")
        return 1

    # Build Merkle tree
    builder = MerkleTreeBuilder()

    with open(manifest_path, "r") as f:
        for line in f:
            entry = json.loads(line)
            # Use canonical hash as the content
            canonical_bytes = bytes.fromhex(entry["canonical_hash"])
            builder.add_leaf(entry["canonical_path"], canonical_bytes)

    root_hash = builder.build_tree()

    summary = {"root_hash": root_hash, "total_leaves": len(builder.leaves)}

    print(f"Merkle Root: {root_hash}")
    print(f"Total Leaves: {len(builder.leaves)}")

    if not args.apply:
        logger.log_info("merkle", "Dry run - would write proofs")
        print("Dry run - proofs not written")
        logger.log_complete("merkle", {**summary, "dry_run": True})
        return 0

    # Write proofs
    if args.out:
        proofs_path = Path(args.out)
    else:
        proofs_path = manifest_path.parent / "merkle_proofs.jsonl"

    builder.write_proofs(proofs_path)
    summary["proofs_path"] = str(proofs_path)

    print(f"Proofs written to: {proofs_path}")
    logger.log_complete("merkle", summary)

    return 0


def cmd_handling_clamp(args):
    """Handling-clamp command - process GTA handling.meta files."""
    print(
        f"{'DRY RUN - ' if not args.apply else ''}Processing handling file: {args.handling_path}"
    )

    # Create logger
    logger = create_logger("hello_world_handling_pipeline")

    # Process file
    result = HandlingPipeline().process_file(
        input_path=Path(args.handling_path),
        output_dir=Path(args.out) if args.out else Path("./output"),
        dry_run=not args.apply,
    )

    if result["success"]:
        print(json.dumps(result, indent=2))
        return 0
    else:
        print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
        return 1


def cmd_classify(args):
    """Classify command - classify artifact state with thresholds."""
    from fractions import Fraction

    from src.sal.state_classification import classify_artifact

    thresholds = load_thresholds(args.threshold_config, args.threshold)
    score = Fraction(args.score)

    state_label, (success, proof) = classify_artifact(
        path=args.path,
        checksum=args.checksum,
        metrics={"score": score},
        thresholds=thresholds,
    )

    result = {
        "state": state_label,
        "success": success,
        "thresholds": {k: str(v) for k, v in thresholds.items()},
        "proof_hash": proof.proof_hash,
        "falsifies_if": proof.falsifies_if,
    }
    print(json.dumps(result, indent=2))
    return 0 if success else 1


def cmd_forensic_commit(args):
    """Forensic-commit command - generate forensic commit JSON and trailer."""
    import subprocess

    from audit.forensic_commit import (
        build_forensic_commit,
        generate_commit_trailer,
        write_forensic_commit,
    )

    thresholds = load_thresholds(args.threshold_config, args.threshold)

    # Resolve commit sha
    commit_sha = args.commit_sha
    if not commit_sha:
        try:
            commit_sha = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip()
        except Exception:
            commit_sha = "UNKNOWN"

    authors = args.author or ["unknown"]
    co_authors = args.co_author or []

    metadata = {
        "commit_sha": commit_sha,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "authors": authors,
        "co_authors": co_authors,
    }

    artifacts = []
    for f in args.files:
        filepath = Path(f)
        if filepath.exists():
            artifacts.append({
                "path": str(filepath.resolve()),
                "size": filepath.stat().st_size,
            })
        else:
            print(f"Warning: file not found: {f}", file=sys.stderr)

    forensic_obj = build_forensic_commit(metadata, artifacts, thresholds)
    filepath = write_forensic_commit(forensic_obj, args.dest_dir)
    trailer = generate_commit_trailer(forensic_obj)

    print(f"Forensic commit written to: {filepath}")
    print("\n--- Commit Trailer ---")
    print(trailer)
    return 0


def cmd_verify(args):
    """Verify command - verify manifest or Merkle proofs."""
    print(f"Verifying: {args.manifest}")

    # Create logger
    logger = create_logger("handling_verification_pipeline")
    logger.log_start("verify", {"manifest": str(args.manifest)})

    manifest_path = Path(args.manifest)

    if not manifest_path.exists():
        print(f"Error: File not found: {manifest_path}", file=sys.stderr)
        logger.log_error("verify", f"File not found: {manifest_path}")
        return 1

    # Check if it's a proof file
    if "proof" in manifest_path.name:
        # Verify Merkle proofs
        valid_count = 0
        invalid_count = 0

        with open(manifest_path, "r") as f:
            for line in f:
                proof = json.loads(line)
                if verify_inclusion_proof(proof):
                    valid_count += 1
                else:
                    invalid_count += 1
                    print(f"Invalid proof for: {proof['path']}")

        print(f"Valid proofs: {valid_count}")
        print(f"Invalid proofs: {invalid_count}")

        summary = {"valid": valid_count, "invalid": invalid_count}
        logger.log_complete("verify", summary)

        return 0 if invalid_count == 0 else 1
    else:
        # Verify manifest integrity
        print("Manifest verification not yet implemented")
        logger.log_info("verify", "Manifest verification placeholder")
        return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CAS CLI - Content-Addressable Storage Operations",
        epilog="Safety-first: Dry-run mode by default, backups mandatory, no auto-push",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Hash command
    hash_parser = subparsers.add_parser("hash", help="Compute SHA-256 hash of files")
    hash_parser.add_argument("files", nargs="+", help="Files to hash")

    # Process command
    process_parser = subparsers.add_parser(
        "process", help="Process files through pipeline"
    )
    process_parser.add_argument(
        "files", nargs="+", help="Files or directories to process"
    )
    process_parser.add_argument(
        "--dry-run", action="store_true", default=True, help="Dry-run mode (default: True)"
    )
    process_parser.add_argument(
        "--live", dest="dry_run", action="store_false", help="Live mode (disables dry-run)"
    )
    process_parser.add_argument(
        "--no-backup", action="store_true", help="Skip backup creation (NOT RECOMMENDED)"
    )
    process_parser.add_argument(
        "--backup-dir", type=str, help="Backup directory (default: ./backups)"
    )
    process_parser.add_argument(
        "--output-dir", type=str, help="Output directory (default: ./output)"
    )
    process_parser.add_argument(
        "--pattern", type=str, help="File pattern for directories (default: *)"
    )
    process_parser.add_argument(
        "--recursive", action="store_true", help="Process directories recursively"
    )
    process_parser.add_argument("--json", action="store_true", help="Output results as JSON")
    process_parser.add_argument("--verbose", action="store_true", help="Verbose output")

    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Manage backups")
    backup_parser.add_argument(
        "action", choices=["create", "list", "cleanup"], help="Backup action"
    )
    backup_parser.add_argument("files", nargs="*", help="Files to backup")
    backup_parser.add_argument(
        "--backup-dir", type=str, help="Backup directory (default: ./backups)"
    )
    backup_parser.add_argument("--pattern", type=str, help="Pattern for listing backups")
    backup_parser.add_argument(
        "--keep", type=int, default=10, help="Number of backups to keep when cleaning up"
    )

    # Manifest command
    manifest_parser = subparsers.add_parser("manifest", help="Manage manifests")
    manifest_parser.add_argument(
        "action", choices=["create", "verify"], help="Manifest action"
    )
    manifest_parser.add_argument("files", nargs="*", help="Files for manifest")
    manifest_parser.add_argument("--manifest", type=str, help="Manifest file path (for verify)")
    manifest_parser.add_argument("--name", type=str, help="Manifest name (for create)")
    manifest_parser.add_argument("--output", type=str, help="Output path (for create)")
    manifest_parser.add_argument("--verbose", action="store_true", help="Verbose output")

    # Index command
    index_parser = subparsers.add_parser("index", help="Generate file manifest")
    index_parser.add_argument("--repo", type=str, default=".", help="Repository path")
    index_parser.add_argument(
        "--manifest", type=str, help="Output manifest path (deprecated, use --out)"
    )
    index_parser.add_argument("--out", type=str, help="Output manifest path")
    index_parser.add_argument(
        "--subset", type=str, help="Comma-separated file patterns to include"
    )
    index_parser.add_argument(
        "--apply", action="store_true", help="Apply changes (default is dry-run)"
    )

    # Merkle command
    merkle_parser = subparsers.add_parser("merkle", help="Build Merkle tree")
    merkle_parser.add_argument(
        "--manifest", type=str, required=True, help="Input manifest.jsonl"
    )
    merkle_parser.add_argument("--out", type=str, help="Output proofs path")
    merkle_parser.add_argument(
        "--apply", action="store_true", help="Apply changes (default is dry-run)"
    )

    # Handling-clamp command
    handling_parser = subparsers.add_parser(
        "handling-clamp", help="Process GTA handling.meta"
    )
    handling_parser.add_argument(
        "--handling-path", type=str, required=True, help="Path to handling.meta"
    )
    handling_parser.add_argument("--out", type=str, help="Output directory")
    handling_parser.add_argument(
        "--apply", action="store_true", help="Apply changes (default is dry-run)"
    )

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify manifest or proofs")
    verify_parser.add_argument(
        "--manifest", type=str, required=True, help="Manifest or proof file to verify"
    )

    # Classify command
    classify_parser = subparsers.add_parser(
        "classify", help="Classify artifact state with configurable thresholds"
    )
    classify_parser.add_argument(
        "--path", type=str, required=True, help="Artifact file path"
    )
    classify_parser.add_argument(
        "--checksum", type=str, required=True, help="Artifact checksum"
    )
    classify_parser.add_argument(
        "--score", type=str, required=True, help="Score as rational (e.g., 247/1)"
    )
    classify_parser.add_argument(
        "--threshold-config", type=str, help="Path to threshold YAML config"
    )
    classify_parser.add_argument(
        "--threshold", type=str, action="append", help="Override threshold key=value"
    )

    # Forensic-commit command
    forensic_parser = subparsers.add_parser(
        "forensic-commit", help="Generate forensic commit JSON and trailer"
    )
    forensic_parser.add_argument(
        "--files", nargs="+", required=True, help="Files to include in forensic commit"
    )
    forensic_parser.add_argument(
        "--commit-sha", type=str, help="Commit SHA (default: git HEAD)"
    )
    forensic_parser.add_argument(
        "--author", type=str, action="append", help="Author(s)"
    )
    forensic_parser.add_argument(
        "--co-author", type=str, action="append", help="Co-author(s)"
    )
    forensic_parser.add_argument(
        "--threshold-config", type=str, help="Path to threshold YAML config"
    )
    forensic_parser.add_argument(
        "--threshold", type=str, action="append", help="Override threshold key=value"
    )
    forensic_parser.add_argument(
        "--dest-dir", type=str, default="audit/forensic_commits", help="Output directory"
    )

    # Parse arguments
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
        elif args.command == "index":
            return cmd_index(args)
        elif args.command == "merkle":
            return cmd_merkle(args)
        elif args.command == "handling-clamp":
            return cmd_handling_clamp(args)
        elif args.command == "verify":
            return cmd_verify(args)
        elif args.command == "classify":
            return cmd_classify(args)
        elif args.command == "forensic-commit":
            return cmd_forensic_commit(args)
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
