#!/usr/bin/env python3
"""
Example: Basic Repository Indexing

This example demonstrates how to:
1. Generate a manifest for a repository
2. Verify the manifest
3. Display summary statistics
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from canonicalization_scaffold.manifest import ManifestGenerator

def main():
    # Configuration
    repo_path = Path.cwd()  # Current directory
    output_dir = Path("./canonical_output")
    output_dir.mkdir(exist_ok=True)
    
    manifest_path = output_dir / "manifest.jsonl"
    
    print("=" * 60)
    print("Repository Indexing Example")
    print("=" * 60)
    print()
    
    # Step 1: Generate manifest
    print("Step 1: Generating manifest...")
    print(f"  Repository: {repo_path}")
    print(f"  Output: {manifest_path}")
    print()
    
    generator = ManifestGenerator()
    
    # Exclude common directories
    exclude_patterns = {'.git', '__pycache__', 'node_modules', '.DS_Store'}
    
    count = generator.write_manifest(
        repo_path,
        manifest_path,
        exclude_patterns=exclude_patterns
    )
    
    print(f"✓ Manifest generated: {count} files processed")
    print()
    
    # Step 2: Analyze manifest
    print("Step 2: Analyzing manifest...")
    
    file_types = {}
    total_size = 0
    
    for entry in ManifestGenerator.load_manifest(manifest_path):
        file_type = entry.get("file_type", "unknown")
        file_size = entry.get("size", 0)
        
        file_types[file_type] = file_types.get(file_type, 0) + 1
        total_size += file_size
    
    print(f"  Total files: {count}")
    print(f"  Total size: {total_size:,} bytes ({total_size / 1024 / 1024:.2f} MB)")
    print()
    print("  Files by type:")
    for file_type, type_count in sorted(file_types.items()):
        print(f"    {file_type}: {type_count}")
    print()
    
    # Step 3: Verify manifest
    print("Step 3: Verifying manifest...")
    
    results = ManifestGenerator.verify_manifest(manifest_path, repo_path)
    
    print(f"  Total entries: {results['total']}")
    print(f"  ✓ Verified: {results['verified']}")
    print(f"  ✗ Mismatched: {results['mismatched']}")
    print(f"  ✗ Missing: {results['missing']}")
    
    if results['mismatched'] == 0 and results['missing'] == 0:
        print()
        print("✓ All files verified successfully!")
    else:
        print()
        print("⚠ Some files failed verification:")
        for error in results['errors'][:5]:  # Show first 5 errors
            print(f"    {error['file']}: {error['error']}")
    
    print()
    print("=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == '__main__':
    main()
