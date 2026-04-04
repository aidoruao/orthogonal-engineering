#!/usr/bin/env python3
"""
cli_diagnose.py — standalone CLI entry point for RepoDiagnoser.

Usage
-----
    python -m tools.repo_diagnoser.cli_diagnose --url https://github.com/owner/repo
    python -m tools.repo_diagnoser.cli_diagnose --url https://github.com/owner/repo --depth 0
    python -m tools.repo_diagnoser.cli_diagnose --url https://github.com/owner/repo --ref main
    python -m tools.repo_diagnoser.cli_diagnose --local /path/to/already-cloned-repo
    python -m tools.repo_diagnoser.cli_diagnose --url ... --out-proofs proofs.jsonl --apply
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from tools.repo_diagnoser.diagnoser import RepoDiagnoser


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cli_diagnose",
        description="Clone and analyse a public Git repository.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyse a remote repo (shallow clone, dry-run)
  python -m tools.repo_diagnoser.cli_diagnose --url https://github.com/owner/repo

  # Full clone, specific branch, write inclusion proofs
  python -m tools.repo_diagnoser.cli_diagnose \\
      --url https://github.com/owner/repo --depth 0 --ref main \\
      --out-proofs proofs.jsonl --apply

  # Analyse an already-cloned local directory
  python -m tools.repo_diagnoser.cli_diagnose --local /tmp/repo_analysis/repo

Safety notes:
  - Default is DRY-RUN: no files are written unless --apply is passed.
  - Clones are placed in /tmp/repo_analysis (override with --clone-dir).
""",
    )

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--url", metavar="URL", help="Public Git repository URL to clone.")
    source.add_argument(
        "--local", metavar="PATH", help="Path to an already-cloned local repository."
    )

    parser.add_argument(
        "--depth",
        type=int,
        default=1,
        metavar="N",
        help="Shallow-clone depth (default: 1).  Use 0 for a full clone.",
    )
    parser.add_argument(
        "--ref",
        metavar="REF",
        default=None,
        help="Branch or tag to check out (default: repository default branch).",
    )
    parser.add_argument(
        "--clone-dir",
        metavar="DIR",
        default="/tmp/repo_analysis",
        help="Base directory for clones (default: /tmp/repo_analysis).",
    )
    parser.add_argument(
        "--out-proofs",
        metavar="FILE",
        default=None,
        help="Write Merkle inclusion proofs to this JSONL file (requires --apply).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        default=False,
        help="Perform writes (proofs file, etc.).  Default is dry-run.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Print summary as JSON instead of human-readable text.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Enable debug logging.",
    )
    return parser


def _print_summary(result: dict, use_json: bool) -> None:
    """Print the analysis summary to stdout."""
    summary = {
        "repo_path": result.get("repo_path", ""),
        "merkle_root": result["merkle_root"],
        "file_count": len(result["file_hashes"]),
        "scan_timestamp": result["scan"].get("scan_timestamp", ""),
    }
    if use_json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"  Repo path  : {summary['repo_path']}")
        print(f"  Files      : {summary['file_count']}")
        print(f"  Merkle root: {summary['merkle_root']}")
        print(f"  Scanned at : {summary['scan_timestamp']}")


def main(argv=None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    log = logging.getLogger("cli_diagnose")

    diagnoser = RepoDiagnoser(clone_dir=args.clone_dir)

    # -- obtain repository path -------------------------------------------
    if args.url:
        mode = "DRY RUN — " if not args.apply else ""
        print(f"{mode}Cloning {args.url} …")
        if not args.apply:
            print("  (pass --apply to perform the clone and analysis)")
            return 0
        try:
            result = diagnoser.diagnose(args.url, depth=args.depth, ref=args.ref)
        except RuntimeError as exc:
            log.error("%s", exc)
            return 1
    else:
        repo_path = Path(args.local)
        if not repo_path.is_dir():
            log.error("Local path does not exist or is not a directory: %s", repo_path)
            return 1
        print(f"Analysing local repository: {repo_path}")
        result = diagnoser.analyze(repo_path)
        result["repo_path"] = str(repo_path)

    # -- optional proofs output -------------------------------------------
    if args.out_proofs:
        if not args.apply:
            print(f"DRY RUN — would write proofs to: {args.out_proofs}")
        else:
            proofs_path = Path(args.out_proofs)
            result["tree"].export_proofs_jsonl(proofs_path)
            print(f"Inclusion proofs written to: {proofs_path}")

    # -- summary ----------------------------------------------------------
    print("\nDiagnosis complete.")
    _print_summary(result, use_json=args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
