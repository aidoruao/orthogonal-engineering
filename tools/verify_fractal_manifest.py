#!/usr/bin/env python3
"""
Fractal Manifest Verifier

This script verifies the integrity of generated fractal code by:
1. Reading the manifest JSONL file
2. Re-scanning the generated directory tree
3. Recounting LOC and file counts
4. Recomputing SHA-256 hashes
5. Comparing against manifest claims

Exit codes:
    0: Verification passed
    1: Verification failed (mismatch detected)
    2: Error during verification

Usage:
    python tools/verify_fractal_manifest.py ./out/fractal_manifest.jsonl
    python tools/verify_fractal_manifest.py ./out/fractal_manifest.jsonl --verbose
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def count_lines_in_file(file_path: Path) -> int:
    """Count lines in a file."""
    with open(file_path, "r") as f:
        return sum(1 for _ in f)


def load_manifest(manifest_path: Path) -> Dict:
    """
    Load manifest from JSONL file.
    
    Returns:
        Dictionary with 'header' and 'batches' keys
    """
    header = None
    batches = []
    
    with open(manifest_path, "r") as f:
        for line in f:
            if not line.strip():
                continue
            
            entry = json.loads(line)
            entry_type = entry.get("type", "unknown")
            
            if entry_type == "header":
                header = entry
            elif entry_type == "batch":
                batches.append(entry)
    
    if header is None:
        raise ValueError("Manifest missing header entry")
    
    return {
        "header": header,
        "batches": batches
    }


def verify_batch(batch_meta: Dict, output_root: Path, verbose: bool = False) -> Dict:
    """
    Verify a single batch against its metadata.
    
    Returns:
        Dictionary with verification results
    """
    batch_name = batch_meta["batch_name"]
    batch_path = output_root / batch_name
    
    if verbose:
        print(f"  Verifying batch: {batch_name}")
    
    # Check batch directory exists
    if not batch_path.exists():
        return {
            "batch_id": batch_meta["batch_id"],
            "success": False,
            "error": f"Batch directory not found: {batch_path}"
        }
    
    if not batch_path.is_dir():
        return {
            "batch_id": batch_meta["batch_id"],
            "success": False,
            "error": f"Batch path is not a directory: {batch_path}"
        }
    
    # Scan files in batch
    shard_files = sorted(batch_path.glob("shard_*.py"))
    actual_files = len(shard_files)
    expected_files = batch_meta["files_in_batch"]
    
    if actual_files != expected_files:
        return {
            "batch_id": batch_meta["batch_id"],
            "success": False,
            "error": f"File count mismatch: expected {expected_files}, found {actual_files}"
        }
    
    # Count LOC and compute hashes
    batch_loc = 0
    file_hashes = []
    
    for shard_path in shard_files:
        lines = count_lines_in_file(shard_path)
        batch_loc += lines
        
        file_hash = compute_file_hash(shard_path)
        file_hashes.append(file_hash)
    
    # Check LOC
    expected_loc = batch_meta["loc_in_batch"]
    if batch_loc != expected_loc:
        return {
            "batch_id": batch_meta["batch_id"],
            "success": False,
            "error": f"LOC mismatch: expected {expected_loc}, found {batch_loc}"
        }
    
    # Compute batch hash
    batch_hash_input = "".join(file_hashes)
    batch_hash = hashlib.sha256(batch_hash_input.encode("utf-8")).hexdigest()
    
    expected_batch_hash = batch_meta["sha256_batch"]
    if batch_hash != expected_batch_hash:
        return {
            "batch_id": batch_meta["batch_id"],
            "success": False,
            "error": f"Batch hash mismatch: expected {expected_batch_hash[:16]}..., found {batch_hash[:16]}..."
        }
    
    return {
        "batch_id": batch_meta["batch_id"],
        "success": True,
        "files": actual_files,
        "loc": batch_loc
    }


class FractalManifestVerifier:
    """Verifies fractal code generation manifest."""
    
    def __init__(self, manifest_path: Path, verbose: bool = False):
        self.manifest_path = manifest_path
        self.verbose = verbose
        self.manifest_data = None
        self.output_root = None
    
    def verify(self) -> bool:
        """
        Run full verification.
        
        Returns:
            True if verification passed, False otherwise
        """
        print(f"=== Fractal Manifest Verifier ===")
        print(f"Manifest: {self.manifest_path}")
        print()
        
        # Load manifest
        try:
            self.manifest_data = load_manifest(self.manifest_path)
        except Exception as e:
            print(f"❌ Failed to load manifest: {e}")
            return False
        
        header = self.manifest_data["header"]
        batches = self.manifest_data["batches"]
        
        print(f"Run ID: {header['run_id']}")
        print(f"Timestamp: {header['timestamp']}")
        print(f"Generator Version: {header.get('generator_version', 'unknown')}")
        print(f"Expected LOC: {header['results']['actual_loc']:,}")
        print(f"Expected Files: {header['results']['total_files']:,}")
        print(f"Expected Batches: {header['results']['total_batches']}")
        print()
        
        # Determine output root from first batch path
        if batches:
            first_batch_path = Path(batches[0]["batch_path"])
            self.output_root = first_batch_path.parent
        else:
            print(f"❌ No batches found in manifest")
            return False
        
        print(f"Output root: {self.output_root}")
        print(f"Verifying {len(batches)} batches...")
        print()
        
        # Verify each batch
        verification_results = []
        total_loc_verified = 0
        total_files_verified = 0
        failed_batches = []
        
        for batch_meta in batches:
            result = verify_batch(batch_meta, self.output_root, self.verbose)
            verification_results.append(result)
            
            if result["success"]:
                total_loc_verified += result["loc"]
                total_files_verified += result["files"]
            else:
                failed_batches.append(result)
                print(f"❌ Batch {result['batch_id']} failed: {result['error']}")
        
        # Compare totals
        expected_loc = header["results"]["actual_loc"]
        expected_files = header["results"]["total_files"]
        expected_batches = header["results"]["total_batches"]
        
        print()
        print(f"=== Verification Results ===")
        
        success = True
        
        # Check LOC
        if total_loc_verified != expected_loc:
            print(f"❌ Total LOC mismatch: expected {expected_loc:,}, verified {total_loc_verified:,}")
            success = False
        else:
            print(f"✓ Total LOC verified: {total_loc_verified:,}")
        
        # Check files
        if total_files_verified != expected_files:
            print(f"❌ Total files mismatch: expected {expected_files:,}, verified {total_files_verified:,}")
            success = False
        else:
            print(f"✓ Total files verified: {total_files_verified:,}")
        
        # Check batches
        verified_batches = len([r for r in verification_results if r["success"]])
        if verified_batches != expected_batches:
            print(f"❌ Batch count mismatch: expected {expected_batches}, verified {verified_batches}")
            success = False
        else:
            print(f"✓ Total batches verified: {verified_batches}")
        
        # Summary
        print()
        if success:
            print("✅ VERIFICATION PASSED")
            print(f"   All {total_files_verified:,} files totaling {total_loc_verified:,} LOC verified successfully")
        else:
            print("❌ VERIFICATION FAILED")
            if failed_batches:
                print(f"   {len(failed_batches)} batch(es) failed verification")
        
        return success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Verify fractal code generation manifest"
    )
    parser.add_argument(
        "manifest",
        type=str,
        help="Path to manifest JSONL file to verify"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    manifest_path = Path(args.manifest)
    
    # Check manifest exists
    if not manifest_path.exists():
        print(f"❌ Manifest file not found: {manifest_path}", file=sys.stderr)
        return 2
    
    # Create verifier
    verifier = FractalManifestVerifier(
        manifest_path=manifest_path,
        verbose=args.verbose
    )
    
    # Run verification
    try:
        success = verifier.verify()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user")
        return 2
    except Exception as e:
        print(f"\n❌ Error during verification: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
