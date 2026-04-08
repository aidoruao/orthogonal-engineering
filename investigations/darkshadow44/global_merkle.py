#!/usr/bin/env python3
"""
global_merkle.py - Compute Merkle tree root across all vendored DarkShadow44 repositories.

This script computes a cryptographic commitment (Merkle tree root) over all
vendored source code, enabling:
1. Cross-repo evidence anchoring
2. Immutability verification
3. Integration with cross_repo_adjunction.py infrastructure

Usage:
    python global_merkle.py [--update-manifests] [--verify]

Options:
    --update-manifests  Update VENDOR_MANIFEST.json files with computed roots
    --verify            Verify current manifests against computed roots
"""

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple


# Repositories to process
REPOSITORIES = [
    "DistantHorizonsStandalone",
    "Angelica",
    "ArchaicFix",
    "Spool",
    "SeasonalHorizons",
]


def sha256_file(filepath: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def compute_repo_merkle_root(repo_path: Path) -> Tuple[str, int]:
    """
    Compute Merkle tree root for a repository.
    
    Uses a simple but effective approach:
    1. Hash each file in src/
    2. Sort hashes lexicographically
    3. Concatenate and hash to get root
    
    Returns (root_hash, file_count)
    """
    src_path = repo_path / "src"
    if not src_path.exists():
        return ("" * 64, 0)
    
    # Collect all file hashes
    file_hashes: List[str] = []
    for filepath in sorted(src_path.rglob("*")):
        if filepath.is_file():
            file_hash = sha256_file(filepath)
            # Include relative path in hash to prevent collisions
            relative_path = str(filepath.relative_to(src_path))
            path_hash = hashlib.sha256(relative_path.encode()).hexdigest()
            combined = hashlib.sha256((file_hash + path_hash).encode()).hexdigest()
            file_hashes.append(combined)
    
    if not file_hashes:
        return ("0" * 64, 0)
    
    # Sort and compute root
    file_hashes.sort()
    root = hashlib.sha256(''.join(file_hashes).encode()).hexdigest()
    return (root, len(file_hashes))


def compute_global_merkle_root(repo_roots: Dict[str, str]) -> str:
    """
    Compute global Merkle root across all repositories.
    
    Combines individual repo roots with their names to prevent collision attacks.
    """
    combined_hashes = []
    for repo_name in sorted(repo_roots.keys()):
        repo_hash = repo_roots[repo_name]
        # Combine repo name with root hash
        name_hash = hashlib.sha256(repo_name.encode()).hexdigest()
        combined = hashlib.sha256((name_hash + repo_hash).encode()).hexdigest()
        combined_hashes.append(combined)
    
    combined_hashes.sort()
    return hashlib.sha256(''.join(combined_hashes).encode()).hexdigest()


def update_manifest(repo_path: Path, merkle_root: str, file_count: int) -> bool:
    """Update VENDOR_MANIFEST.json with computed Merkle root."""
    manifest_path = repo_path / "VENDOR_MANIFEST.json"
    if not manifest_path.exists():
        print(f"  Warning: No manifest found at {manifest_path}")
        return False
    
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        manifest['sha256_tree_root'] = merkle_root
        manifest['total_files'] = file_count
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return True
    except Exception as e:
        print(f"  Error updating manifest: {e}")
        return False


def verify_manifest(repo_path: Path, expected_root: str) -> bool:
    """Verify VENDOR_MANIFEST.json matches computed root."""
    manifest_path = repo_path / "VENDOR_MANIFEST.json"
    if not manifest_path.exists():
        return False
    
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        stored_root = manifest.get('sha256_tree_root', '')
        if stored_root == '<computed_by_global_merkle.py>':
            print(f"  Not yet computed (placeholder)")
            return False
        
        return stored_root == expected_root
    except Exception as e:
        print(f"  Error verifying manifest: {e}")
        return False


def main():
    """Main entry point."""
    update_manifests = '--update-manifests' in sys.argv
    verify_mode = '--verify' in sys.argv
    
    base_path = Path(__file__).parent
    
    print("=" * 80)
    print("Global Merkle Root Computation")
    print("=" * 80)
    print()
    
    repo_roots: Dict[str, str] = {}
    all_verified = True
    
    for repo_name in REPOSITORIES:
        repo_path = base_path / repo_name
        print(f"Processing {repo_name}...")
        
        root, file_count = compute_repo_merkle_root(repo_path)
        repo_roots[repo_name] = root
        
        print(f"  Files: {file_count}")
        print(f"  Root:  {root}")
        
        if verify_mode:
            verified = verify_manifest(repo_path, root)
            print(f"  Verified: {'✓' if verified else '✗'}")
            if not verified:
                all_verified = False
        
        if update_manifests:
            if update_manifest(repo_path, root, file_count):
                print(f"  Updated manifest")
        
        print()
    
    # Compute global root
    global_root = compute_global_merkle_root(repo_roots)
    print("-" * 80)
    print(f"Global Merkle Root: {global_root}")
    print("-" * 80)
    print()
    
    # Output summary
    print("Repository Summary:")
    print(f"  Total repositories: {len(REPOSITORIES)}")
    print(f"  Total files: {sum(f for _, f in [compute_repo_merkle_root(base_path / r) for r in REPOSITORIES])}")
    print()
    
    if verify_mode:
        print(f"Verification: {'All manifests verified ✓' if all_verified else 'Some manifests failed ✗'}")
        return 0 if all_verified else 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
