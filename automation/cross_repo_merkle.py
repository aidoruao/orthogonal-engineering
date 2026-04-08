"""Cross-Repository Merkle Root Computation.

Cryptographically binds all 3 repositories into a single verifiable artifact:
- orthogonal-engineering (this repo)
- sigma-lora-covenant
- truthsystems-mod

Usage: python automation/cross_repo_merkle.py
Output: CROSS_REPO_MERKLE_ROOT.txt
"""

import hashlib
import os
from pathlib import Path
from typing import List, Tuple


def compute_file_hash(filepath: str) -> str:
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def collect_files(directory: str, extensions: Tuple[str, ...]) -> List[Tuple[str, str]]:
    """Collect all files with given extensions, return (relative_path, hash)."""
    files = []
    base_path = Path(directory)
    
    for ext in extensions:
        for filepath in base_path.rglob(f"*{ext}"):
            # Skip __pycache__, .git, etc.
            if any(part.startswith('.') or part == '__pycache__' for part in filepath.parts):
                continue
            
            try:
                file_hash = compute_file_hash(str(filepath))
                rel_path = str(filepath.relative_to(base_path))
                files.append((rel_path, file_hash))
            except (IOError, OSError):
                continue
    
    return sorted(files)  # Sort for determinism


def merkle_hash(left: str, right: str) -> str:
    """Compute parent hash from two child hashes."""
    combined = bytes.fromhex(left) + bytes.fromhex(right)
    return hashlib.sha256(combined).hexdigest()


def build_merkle_tree(leaves: List[str]) -> List[List[str]]:
    """Build Merkle tree from leaf hashes. Returns all levels."""
    if not leaves:
        return []
    
    # Pad to power of 2
    current_level = leaves[:]
    while len(current_level) & (len(current_level) - 1):  # Not power of 2
        current_level.append(current_level[-1])  # Duplicate last
    
    tree = [current_level]
    
    # Build tree bottom-up
    while len(current_level) > 1:
        next_level = []
        for i in range(0, len(current_level), 2):
            parent = merkle_hash(current_level[i], current_level[i+1])
            next_level.append(parent)
        tree.append(next_level)
        current_level = next_level
    
    return tree


def compute_cross_repo_merkle():
    """Compute Merkle root across all 3 repositories."""
    
    print("Computing cross-repository Merkle root...")
    print("=" * 60)
    
    # Repository paths
    repos = {
        'orthogonal-engineering': ('~/orthogonal-engineering', ('.py', '.md', '.json', '.yaml', '.yml')),
        'sigma-lora-covenant': ('~/sigma-lora-covenant', ('.py', '.md', '.json')),
        'truthsystems-mod': ('~/truthsystems-mod', ('.java', '.md', '.json')),
    }
    
    all_hashes = []
    
    for repo_name, (path, extensions) in repos.items():
        expanded_path = os.path.expanduser(path)
        
        if not os.path.exists(expanded_path):
            print(f"⚠️  {repo_name}: Directory not found at {expanded_path}")
            continue
        
        print(f"\n📁 {repo_name}")
        print(f"   Path: {expanded_path}")
        
        files = collect_files(expanded_path, extensions)
        
        print(f"   Files: {len(files)}")
        
        # Add repo prefix to paths
        for rel_path, file_hash in files:
            prefixed_path = f"{repo_name}/{rel_path}"
            # Hash the path + content hash
            combined = hashlib.sha256((prefixed_path + file_hash).encode()).hexdigest()
            all_hashes.append(combined)
            
            if len(files) <= 5 or files.index((rel_path, file_hash)) < 3:
                print(f"   - {rel_path}: {file_hash[:16]}...")
            elif files.index((rel_path, file_hash)) == 3:
                print(f"   ... and {len(files) - 3} more files")
    
    if not all_hashes:
        print("\n❌ No files found!")
        return None
    
    print(f"\n📊 Total leaf hashes: {len(all_hashes)}")
    
    # Build Merkle tree
    tree = build_merkle_tree(all_hashes)
    root = tree[-1][0] if tree else None
    
    if root:
        print(f"\n🔐 Merkle Root: {root}")
        print(f"   Tree depth: {len(tree)}")
        
        # Write to file
        output_file = "CROSS_REPO_MERKLE_ROOT.txt"
        with open(output_file, 'w') as f:
            f.write(f"Cross-Repository Merkle Root\n")
            f.write(f"Generated: 2026-04-08\n")
            f.write(f"Total files: {len(all_hashes)}\n")
            f.write(f"Tree depth: {len(tree)}\n")
            f.write(f"\nROOT: {root}\n")
            f.write(f"\nRepositories included:\n")
            for repo_name in repos:
                f.write(f"  - {repo_name}\n")
        
        print(f"\n📝 Written to: {output_file}")
        
        return root
    
    return None


def verify_consistency():
    """Verify the Merkle root is consistent with current state."""
    output_file = "CROSS_REPO_MERKLE_ROOT.txt"
    
    if not os.path.exists(output_file):
        print("No existing Merkle root found.")
        return False
    
    # Read existing root
    with open(output_file) as f:
        for line in f:
            if line.startswith("ROOT: "):
                existing_root = line[6:].strip()
                break
        else:
            print("Invalid Merkle root file format.")
            return False
    
    # Compute new root
    new_root = compute_cross_repo_merkle()
    
    if new_root == existing_root:
        print("\n✅ Merkle root consistent — repositories unchanged")
        return True
    else:
        print(f"\n⚠️  Merkle root changed!")
        print(f"   Old: {existing_root[:32]}...")
        print(f"   New: {new_root[:32]}...")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        verify_consistency()
    else:
        compute_cross_repo_merkle()
