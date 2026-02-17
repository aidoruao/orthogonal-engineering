#!/usr/bin/env python3
"""
Example: Merkle Tree Construction

This example demonstrates how to:
1. Build a Merkle tree from files
2. Generate inclusion proofs
3. Verify inclusion proofs
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from canonicalization_scaffold.canonicalizer import canonical_byte_representation
from canonicalization_scaffold.merkle import build_merkle_tree

def main():
    # Create some test files
    test_dir = Path("./test_files")
    test_dir.mkdir(exist_ok=True)
    
    test_files = {
        "file1.txt": "Hello, World!",
        "file2.txt": "Merkle trees are cool",
        "file3.txt": "Deterministic hashing",
    }
    
    print("=" * 60)
    print("Merkle Tree Construction Example")
    print("=" * 60)
    print()
    
    # Step 1: Create test files
    print("Step 1: Creating test files...")
    for filename, content in test_files.items():
        file_path = test_dir / filename
        file_path.write_text(content)
        print(f"  Created: {filename}")
    print()
    
    # Step 2: Get canonical bytes
    print("Step 2: Getting canonical bytes...")
    file_hashes = {}
    for filename in test_files.keys():
        file_path = test_dir / filename
        canonical_bytes = canonical_byte_representation(file_path)
        file_hashes[filename] = canonical_bytes
        print(f"  {filename}: {len(canonical_bytes)} bytes")
    print()
    
    # Step 3: Build Merkle tree
    print("Step 3: Building Merkle tree...")
    root_hash, tree = build_merkle_tree(file_hashes)
    
    print(f"  Root hash: {root_hash}")
    print(f"  Leaves: {len(tree.leaves)}")
    print()
    
    # Step 4: Generate inclusion proofs
    print("Step 4: Generating inclusion proofs...")
    for filename in test_files.keys():
        proof = tree.get_inclusion_proof(filename)
        print(f"  {filename}:")
        print(f"    Proof length: {len(proof)}")
        print(f"    Leaf hash: {tree.leaf_map[filename]}")
    print()
    
    # Step 5: Verify inclusion proofs
    print("Step 5: Verifying inclusion proofs...")
    all_valid = True
    
    for filename in test_files.keys():
        proof = tree.get_inclusion_proof(filename)
        canonical_bytes = file_hashes[filename]
        
        is_valid = tree.verify_inclusion_proof(
            filename,
            canonical_bytes,
            proof,
            root_hash
        )
        
        status = "✓" if is_valid else "✗"
        print(f"  {status} {filename}: {'Valid' if is_valid else 'Invalid'}")
        
        all_valid = all_valid and is_valid
    
    print()
    
    if all_valid:
        print("✓ All inclusion proofs verified successfully!")
    else:
        print("✗ Some proofs failed verification")
    
    # Step 6: Export proofs
    output_dir = Path("./canonical_output")
    output_dir.mkdir(exist_ok=True)
    proofs_path = output_dir / "merkle_proofs.jsonl"
    
    print()
    print("Step 6: Exporting proofs...")
    tree.export_proofs_jsonl(proofs_path)
    print(f"  Proofs saved to: {proofs_path}")
    
    # Read and display first proof
    import json
    with open(proofs_path, 'r') as f:
        first_proof = json.loads(f.readline())
    
    print()
    print("  Example proof record:")
    print(f"    File: {first_proof['file_path']}")
    print(f"    Leaf hash: {first_proof['leaf_hash'][:16]}...")
    print(f"    Proof steps: {len(first_proof['proof'])}")
    print(f"    Root hash: {first_proof['root_hash'][:16]}...")
    
    print()
    print("=" * 60)
    print("Example completed!")
    print("=" * 60)
    
    # Cleanup
    print()
    print("Cleaning up test files...")
    import shutil
    shutil.rmtree(test_dir)
    print("✓ Done")


if __name__ == '__main__':
    main()
