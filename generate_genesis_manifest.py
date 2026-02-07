"""
GENESIS MANIFEST GENERATOR
Canonical byte enumeration for immutable commit
Authority: FINAL
Generated: 2026-02-07
"""

from pathlib import Path
import hashlib
from datetime import datetime, timezone
import yaml

def compute_sha256(filepath: Path) -> str:
    """Compute SHA-256 of raw file bytes"""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def enumerate_repository(root: Path, ignore_patterns: set) -> list:
    """Enumerate all files with byte-exact hashes"""
    files = []
    
    for item in sorted(root.rglob('*')):
        # Skip ignored patterns
        if any(pattern in str(item) for pattern in ignore_patterns):
            continue
        
        if item.is_file():
            rel_path = str(item.relative_to(root)).replace('\\', '/')
            size = item.stat().st_size
            sha256 = compute_sha256(item)
            
            files.append({
                'path': rel_path,
                'bytes': size,
                'sha256': sha256
            })
    
    return files

def generate_genesis_manifest(repo_root: str, repo_name: str, output_path: str):
    """Generate GENESIS_MANIFEST.yaml"""
    root = Path(repo_root)
    
    # Ignore patterns
    ignore = {'.git', '__pycache__', '.pyc', 'node_modules', '.cache'}
    
    # Enumerate all files
    files = enumerate_repository(root, ignore)
    
    # Generate manifest
    manifest = {
        'repo': repo_name,
        'hash_algorithm': 'sha256',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'total_files': len(files),
        'total_bytes': sum(f['bytes'] for f in files),
        'files': files
    }
    
    # Write manifest
    output = Path(output_path)
    with open(output, 'w') as f:
        yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)
    
    print(f"GENESIS_MANIFEST generated: {output}")
    print(f"  Files: {len(files)}")
    print(f"  Total bytes: {manifest['total_bytes']:,}")
    
    return manifest

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python generate_genesis_manifest.py <repo_root> <repo_name>")
        sys.exit(1)
    
    repo_root = sys.argv[1]
    repo_name = sys.argv[2]
    output = Path(repo_root) / "GENESIS_MANIFEST.yaml"
    
    generate_genesis_manifest(repo_root, repo_name, str(output))
