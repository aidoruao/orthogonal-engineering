#!/usr/bin/env python3
"""
Simple CLI wrapper for GTA V Enhanced Handling Pipeline

This is a minimal wrapper that calls the gta_handling_pipeline.py script
with proper argument forwarding. It's designed to be simple and focused
on the GTA V handling.meta processing task.

Usage:
    python gta_cli.py --subset 10 --dry-run
    python gta_cli.py --subset 100 --dry-run
    python gta_cli.py --subset 787 --dry-run
    python gta_cli.py --subset 787 --apply  (WARNING: modifies files!)
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.resolve()


def run_gta_pipeline(args):
    """Run the GTA V handling pipeline."""
    pipeline_script = REPO_ROOT / "gta_handling_pipeline.py"

    if not pipeline_script.exists():
        print(f"[ERROR] GTA pipeline script not found at {pipeline_script}")
        print("[INFO] Looking for script in:", pipeline_script)
        sys.exit(2)

    # Build command with all arguments
    cmd = [sys.executable, str(pipeline_script)]

    # Add required handling-path argument
    if args.handling_path:
        cmd += ["--handling-path", str(args.handling_path)]
    else:
        # Default path to GTA V Enhanced handling.meta
        default_path = r"C:\Games\steamapps\common\Grand Theft Auto V Enhanced\onigiri\common\data\handling.meta"
        cmd += ["--handling-path", default_path]
        print(f"[INFO] Using default handling path: {default_path}")

    # Add optional arguments
    if args.subset is not None:
        cmd += ["--subset", str(args.subset)]

    if args.out_dir:
        cmd += ["--out-dir", str(args.out_dir)]

    if args.dry_run:
        cmd += ["--dry-run"]

    if args.apply:
        cmd += ["--apply"]

    print("Running GTA V handling pipeline:", " ".join(cmd))

    try:
        rc = subprocess.run(cmd).returncode
        if rc != 0:
            print(f"[ERROR] GTA V handling pipeline exited with code {rc}")
            sys.exit(rc)
        print("[OK] GTA V handling pipeline completed successfully")
    except FileNotFoundError:
        print(f"[ERROR] Python interpreter not found at: {sys.executable}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to run pipeline: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="gta_cli.py",
        description="Simple CLI wrapper for GTA V Enhanced Handling Pipeline",
    )

    # Add arguments
    parser.add_argument(
        "--subset", type=int, help="Process only first N vehicles (for testing)"
    )
    parser.add_argument(
        "--handling-path",
        type=str,
        help="Path to handling.meta file (defaults to GTA V Enhanced path)",
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default="outputs/gta_handling_test",
        help="Output directory for results",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without modifying files (SAFE MODE - RECOMMENDED)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes (WARNING: modifies files! Use --dry-run first)",
    )

    args = parser.parse_args()

    # Safety warnings
    if args.apply:
        print("\n" + "=" * 60)
        print("WARNING: --apply flag detected!")
        print("This will MODIFY your handling.meta file.")
        print("=" * 60)
        response = input("\nAre you sure you want to continue? (yes/NO): ")
        if response.lower() != "yes":
            print("Operation cancelled.")
            sys.exit(0)

    if not args.dry_run and not args.apply:
        print("\n[INFO] Running in dry-run mode by default (no file modifications)")
        print("[INFO] Use --dry-run explicitly or --apply to modify files")
        args.dry_run = True

    # Run the pipeline
    run_gta_pipeline(args)


if __name__ == "__main__":
    main()
