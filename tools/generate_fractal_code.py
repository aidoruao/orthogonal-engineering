#!/usr/bin/env python3
"""
Fractal Code Generator for 1B LOC System

This script generates a verifiable, deterministic code pattern that can scale to
1 billion lines of code (1B LOC) as an external artifact, not stored in Git.

The generator creates:
- Deterministic Python code files with fractal/recursive patterns
- Batch-organized output directory structure
- JSONL manifest with metadata, counts, and SHA-256 hashes
- Compact proof of generation (manifest stored in Git, generated code is not)

Usage:
    python tools/generate_fractal_code.py --target-loc 1000000000 --apply
    python tools/generate_fractal_code.py --target-loc 10000 --apply  # Small test run
"""

import argparse
import hashlib
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


# Constants (Configuration Layer)
DEFAULT_TARGET_LOC = 1_000_000_000
DEFAULT_LINES_PER_FILE = 1000
DEFAULT_FILES_PER_BATCH = 10_000
DEFAULT_OUTPUT_ROOT = "./out"
DEFAULT_MANIFEST_PATH = "./out/fractal_manifest.jsonl"
DEFAULT_SEED = 42


def get_git_commit_sha() -> Optional[str]:
    """Get current git commit SHA if available."""
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def generate_shard_content(
    shard_index: int,
    batch_index: int,
    lines_per_file: int,
    seed: int
) -> str:
    """
    Generate deterministic Python code content for a shard file.
    
    The pattern is a simple fractal-like structure with:
    - Deterministic functions based on indices
    - Parametric variation per batch/shard
    - Exactly lines_per_file lines of code
    
    Args:
        shard_index: Index of the shard within the batch
        batch_index: Index of the batch
        lines_per_file: Target number of lines to generate
        seed: Random seed for deterministic variation
    
    Returns:
        String containing exactly lines_per_file lines of Python code
    """
    lines = []
    
    # Header comment (counts as 2 lines)
    lines.append(f"# Fractal Shard {batch_index:06d}_{shard_index:06d}")
    lines.append(f"# Generated deterministically with seed={seed}")
    
    # Calculate derived parameters
    param_a = (shard_index * 7 + batch_index * 13 + seed) % 1000
    param_b = (shard_index * 11 + batch_index * 17 + seed) % 500
    
    # Generate function definitions
    # Each function is ~10 lines, so we calculate how many we need
    num_functions = (lines_per_file - 2) // 10
    remaining_lines = (lines_per_file - 2) % 10
    
    for func_idx in range(num_functions):
        func_name = f"fractal_{batch_index}_{shard_index}_{func_idx}"
        lines.append(f"\ndef {func_name}(x, y={param_a}, z={param_b}):")
        lines.append(f'    """Fractal function {func_idx} in batch {batch_index}, shard {shard_index}."""')
        lines.append(f"    a = x * {param_a} + y")
        lines.append(f"    b = y * {param_b} + z")
        lines.append(f"    c = (a + b) % 1000")
        lines.append(f"    d = (a * b) % 500")
        lines.append(f"    result = c + d")
        lines.append(f"    return result")
        lines.append("")
    
    # Add remaining lines as simple variable assignments
    for i in range(remaining_lines):
        var_name = f"var_{batch_index}_{shard_index}_{i}"
        var_value = (param_a * i + param_b) % 10000
        lines.append(f"{var_name} = {var_value}")
    
    # Ensure we have exactly the right number of lines
    content = "\n".join(lines)
    actual_lines = content.count("\n") + 1
    
    # Adjust if needed (should be exact, but this is a safety check)
    if actual_lines < lines_per_file:
        for i in range(lines_per_file - actual_lines):
            content += f"\n# Padding line {i}"
    elif actual_lines > lines_per_file:
        # Shouldn't happen, but truncate if it does
        content = "\n".join(content.split("\n")[:lines_per_file])
    
    return content


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def compute_content_hash(content: str) -> str:
    """Compute SHA-256 hash of string content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class FractalCodeGenerator:
    """Generates fractal code pattern with verifiable manifest."""
    
    def __init__(
        self,
        target_loc: int,
        lines_per_file: int,
        files_per_batch: int,
        output_root: Path,
        manifest_path: Path,
        seed: int,
        dry_run: bool = True
    ):
        self.target_loc = target_loc
        self.lines_per_file = lines_per_file
        self.files_per_batch = files_per_batch
        self.output_root = output_root
        self.manifest_path = manifest_path
        self.seed = seed
        self.dry_run = dry_run
        
        # Calculate derived values
        self.loc_per_file = lines_per_file
        self.loc_per_batch = files_per_batch * self.loc_per_file
        self.num_batches = (target_loc + self.loc_per_batch - 1) // self.loc_per_batch
        
        # Tracking
        self.total_loc_generated = 0
        self.total_files_generated = 0
        self.batch_metadata: List[Dict] = []
        
    def generate(self) -> Dict:
        """
        Generate all batches and files.
        
        Returns:
            Dictionary with generation summary
        """
        run_id = str(uuid.uuid4())
        run_timestamp = datetime.now(timezone.utc).isoformat()
        generator_version = get_git_commit_sha() or "unknown"
        
        print(f"=== Fractal Code Generator ===")
        print(f"Run ID: {run_id}")
        print(f"Timestamp: {run_timestamp}")
        print(f"Generator Version: {generator_version}")
        print(f"Target LOC: {self.target_loc:,}")
        print(f"Lines per file: {self.lines_per_file:,}")
        print(f"Files per batch: {self.files_per_batch:,}")
        print(f"LOC per batch: {self.loc_per_batch:,}")
        print(f"Number of batches: {self.num_batches}")
        print(f"Output root: {self.output_root}")
        print(f"Manifest: {self.manifest_path}")
        print(f"Seed: {self.seed}")
        print(f"Dry run: {self.dry_run}")
        print()
        
        if self.dry_run:
            print("⚠️  DRY RUN MODE - No files will be written")
            print("    Use --apply to actually generate files")
            print()
        
        # Create output directory structure
        if not self.dry_run:
            self.output_root.mkdir(parents=True, exist_ok=True)
            self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        
        start_time = time.time()
        
        # Generate batches
        for batch_idx in range(self.num_batches):
            # Check if we've reached the target
            if self.total_loc_generated >= self.target_loc:
                break
            
            batch_result = self._generate_batch(batch_idx)
            self.batch_metadata.append(batch_result)
            
            # Progress reporting
            if (batch_idx + 1) % 10 == 0 or batch_idx == 0:
                elapsed = time.time() - start_time
                loc_per_sec = self.total_loc_generated / elapsed if elapsed > 0 else 0
                eta_seconds = (self.target_loc - self.total_loc_generated) / loc_per_sec if loc_per_sec > 0 else 0
                print(f"Progress: Batch {batch_idx + 1}/{self.num_batches} | "
                      f"LOC: {self.total_loc_generated:,}/{self.target_loc:,} | "
                      f"Files: {self.total_files_generated:,} | "
                      f"Speed: {loc_per_sec:,.0f} LOC/s | "
                      f"ETA: {eta_seconds/60:.1f} min")
        
        end_time = time.time()
        elapsed_total = end_time - start_time
        
        # Write manifest
        manifest_data = {
            "run_id": run_id,
            "timestamp": run_timestamp,
            "generator_version": generator_version,
            "config": {
                "target_loc": self.target_loc,
                "lines_per_file": self.lines_per_file,
                "files_per_batch": self.files_per_batch,
                "seed": self.seed
            },
            "results": {
                "actual_loc": self.total_loc_generated,
                "total_files": self.total_files_generated,
                "total_batches": len(self.batch_metadata),
                "elapsed_seconds": elapsed_total
            },
            "batches": self.batch_metadata
        }
        
        if not self.dry_run:
            # Write as JSONL (one entry per line for large files)
            with open(self.manifest_path, "w") as f:
                # Write header
                header = {
                    "type": "header",
                    "run_id": run_id,
                    "timestamp": run_timestamp,
                    "generator_version": generator_version,
                    "config": manifest_data["config"],
                    "results": manifest_data["results"]
                }
                f.write(json.dumps(header) + "\n")
                
                # Write each batch as a separate line
                for batch_meta in self.batch_metadata:
                    batch_entry = {
                        "type": "batch",
                        "run_id": run_id,
                        **batch_meta
                    }
                    f.write(json.dumps(batch_entry) + "\n")
            
            print(f"\n✓ Manifest written to: {self.manifest_path}")
        else:
            print(f"\n⚠️  Manifest NOT written (dry run)")
        
        # Summary
        print(f"\n=== Generation Complete ===")
        print(f"Total LOC generated: {self.total_loc_generated:,}")
        print(f"Total files generated: {self.total_files_generated:,}")
        print(f"Total batches: {len(self.batch_metadata)}")
        print(f"Time elapsed: {elapsed_total:.2f} seconds")
        print(f"Average speed: {self.total_loc_generated/elapsed_total:,.0f} LOC/s")
        
        return manifest_data
    
    def _generate_batch(self, batch_idx: int) -> Dict:
        """Generate a single batch of files."""
        batch_name = f"batch_{batch_idx:06d}"
        batch_path = self.output_root / batch_name
        
        if not self.dry_run:
            batch_path.mkdir(parents=True, exist_ok=True)
        
        batch_file_hashes = []
        batch_loc = 0
        batch_files = 0
        
        # Determine how many files to generate in this batch
        remaining_loc = self.target_loc - self.total_loc_generated
        files_to_generate = min(
            self.files_per_batch,
            (remaining_loc + self.loc_per_file - 1) // self.loc_per_file
        )
        
        for file_idx in range(files_to_generate):
            shard_name = f"shard_{file_idx:06d}.py"
            shard_path = batch_path / shard_name
            
            # Generate content
            content = generate_shard_content(
                shard_index=file_idx,
                batch_index=batch_idx,
                lines_per_file=self.lines_per_file,
                seed=self.seed
            )
            
            # Count actual lines
            actual_lines = content.count("\n") + 1
            
            # Compute hash
            content_hash = compute_content_hash(content)
            
            # Write file
            if not self.dry_run:
                with open(shard_path, "w") as f:
                    f.write(content)
            
            batch_file_hashes.append(content_hash)
            batch_loc += actual_lines
            batch_files += 1
            
            self.total_loc_generated += actual_lines
            self.total_files_generated += 1
        
        # Compute batch hash (hash of concatenated file hashes)
        batch_hash_input = "".join(batch_file_hashes)
        batch_hash = hashlib.sha256(batch_hash_input.encode("utf-8")).hexdigest()
        
        return {
            "batch_id": batch_idx,
            "batch_name": batch_name,
            "batch_path": str(batch_path),
            "files_in_batch": batch_files,
            "loc_in_batch": batch_loc,
            "sha256_batch": batch_hash
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate deterministic fractal code pattern for 1B LOC verification"
    )
    parser.add_argument(
        "--target-loc",
        type=int,
        default=DEFAULT_TARGET_LOC,
        help=f"Target lines of code to generate (default: {DEFAULT_TARGET_LOC:,})"
    )
    parser.add_argument(
        "--lines-per-file",
        type=int,
        default=DEFAULT_LINES_PER_FILE,
        help=f"Lines per generated file (default: {DEFAULT_LINES_PER_FILE})"
    )
    parser.add_argument(
        "--files-per-batch",
        type=int,
        default=DEFAULT_FILES_PER_BATCH,
        help=f"Files per batch directory (default: {DEFAULT_FILES_PER_BATCH:,})"
    )
    parser.add_argument(
        "--output-root",
        type=str,
        default=DEFAULT_OUTPUT_ROOT,
        help=f"Root directory for generated files (default: {DEFAULT_OUTPUT_ROOT})"
    )
    parser.add_argument(
        "--manifest",
        type=str,
        default=DEFAULT_MANIFEST_PATH,
        help=f"Path to output manifest file (default: {DEFAULT_MANIFEST_PATH})"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=f"Random seed for deterministic generation (default: {DEFAULT_SEED})"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually generate files (default is dry-run)"
    )
    
    args = parser.parse_args()
    
    # Convert paths
    output_root = Path(args.output_root)
    manifest_path = Path(args.manifest)
    
    # Create generator
    generator = FractalCodeGenerator(
        target_loc=args.target_loc,
        lines_per_file=args.lines_per_file,
        files_per_batch=args.files_per_batch,
        output_root=output_root,
        manifest_path=manifest_path,
        seed=args.seed,
        dry_run=not args.apply
    )
    
    # Run generation
    try:
        generator.generate()
        return 0
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error during generation: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
