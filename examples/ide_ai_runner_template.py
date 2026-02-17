#!/usr/bin/env python3
"""
IDE AI Runner Template (Python)

Example script for running deterministic pipeline operations.

IMPORTANT: This is a TEMPLATE. Customize paths and parameters for your use.

Usage: python ide_ai_runner_template.py
"""

import subprocess
import sys
from pathlib import Path


# Configuration - CUSTOMIZE THESE
REPO_PATH = Path("/path/to/your/repository")
VAULT_PATH = Path("/home/yourname/your_vault")  # NOT the example path!
OUTPUT_DIR = Path("./pipeline_output")


def run_command(cmd, description, check=True):
    """Run a command and display output."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(map(str, cmd))}\n")
    
    result = subprocess.run(cmd, check=check)
    return result.returncode == 0


def main():
    """Main pipeline execution."""
    print("Deterministic Pipeline Runner")
    print("=" * 60)
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Index Repository (Dry-Run)
    success = run_command(
        ["python", "cli.py", "index", 
         "--repo", str(REPO_PATH),
         "--out", str(OUTPUT_DIR / "manifest.jsonl")],
        "[1/5] Indexing repository (dry-run)"
    )
    
    if not success:
        print("Dry-run failed. Aborting.")
        return 1
    
    # Pause for review
    input("\nReview the output above. Press Enter to continue with actual indexing, or Ctrl+C to abort: ")
    
    # Step 2: Index Repository (Apply)
    success = run_command(
        ["python", "cli.py", "index",
         "--repo", str(REPO_PATH),
         "--out", str(OUTPUT_DIR / "manifest.jsonl"),
         "--apply"],
        "[2/5] Indexing repository (apply)"
    )
    
    if not success:
        print("Indexing failed. Aborting.")
        return 1
    
    # Step 3: Build Merkle Tree
    success = run_command(
        ["python", "cli.py", "merkle",
         "--manifest", str(OUTPUT_DIR / "manifest.jsonl"),
         "--apply"],
        "[3/5] Building Merkle tree"
    )
    
    if not success:
        print("Merkle tree building failed. Continuing anyway...")
    
    # Step 4: Verify Proofs
    proofs_file = OUTPUT_DIR / "merkle_proofs.jsonl"
    if proofs_file.exists():
        run_command(
            ["python", "cli.py", "verify",
             "--manifest", str(proofs_file)],
            "[4/5] Verifying Merkle proofs",
            check=False
        )
    
    # Step 5: Finalize Vault (if exists)
    if VAULT_PATH.exists():
        run_command(
            ["python", "core/alpha_omega_finalizer.py",
             "--vault-dir", str(VAULT_PATH),
             "--apply"],
            "[5/5] Finalizing vault",
            check=False
        )
    else:
        print(f"\n[5/5] Vault path does not exist, skipping finalization")
        print(f"      Vault path: {VAULT_PATH}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Pipeline execution complete!")
    print("=" * 60)
    print(f"Outputs in: {OUTPUT_DIR}")
    print(f"Logs in: ./logs/")
    
    # Display file counts
    manifest_file = OUTPUT_DIR / "manifest.jsonl"
    if manifest_file.exists():
        with open(manifest_file, 'r') as f:
            line_count = sum(1 for _ in f)
        print(f"\nManifest entries: {line_count}")
    
    if proofs_file.exists():
        with open(proofs_file, 'r') as f:
            proof_count = sum(1 for _ in f)
        print(f"Merkle proofs: {proof_count}")
    
    print("\nReview logs in ./logs/ for detailed operation history")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)
