"""
Merkle Tree Verification Example

Demonstrates:
- Building Merkle trees
- Generating inclusion proofs
- Verifying file integrity
"""

import sys
import tempfile
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from toolkit.oe.scaffold.merkle import build_merkle_tree, write_all_proofs
from toolkit.oe.scaffold.logger import ScaffoldLogger


def main():
    """Run Merkle tree verification example."""
    print("=" * 60)
    print("Merkle Tree Verification Example")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create logger
        logger = ScaffoldLogger(temp_path / "merkle_example.jsonl")
        logger.log_start("merkle_example")
        
        # Create sample files
        print("\n1. Creating Sample Files")
        print("-" * 40)
        
        files = []
        for i in range(5):
            f = temp_path / f"file{i}.txt"
            f.write_text(f"Content for file {i}\n", encoding="utf-8")
            files.append(f)
            print(f"  Created: {f.name}")
        
        logger.log_info("files_created", count=len(files))
        
        # Build Merkle tree
        print("\n2. Building Merkle Tree")
        print("-" * 40)
        
        tree = build_merkle_tree(files)
        root_hash = tree.get_root_hash()
        
        print(f"Files in tree: {len(tree.leaves)}")
        print(f"Root hash: {root_hash}")
        
        logger.log_info("merkle_tree_built", 
                       leaves=len(tree.leaves),
                       root_hash=root_hash)
        
        # Generate proofs
        print("\n3. Generating Inclusion Proofs")
        print("-" * 40)
        
        proofs_path = temp_path / "proofs.jsonl"
        write_all_proofs(tree, proofs_path)
        
        print(f"Proofs written to: {proofs_path.name}")
        
        # Show sample proof
        with open(proofs_path, "r") as f:
            import json
            first_proof = json.loads(f.readline())
            print(f"\nSample proof for: {Path(first_proof['file_path']).name}")
            print(f"  Leaf hash: {first_proof['leaf_hash'][:16]}...")
            print(f"  Root hash: {first_proof['root_hash'][:16]}...")
            print(f"  Proof path length: {len(first_proof['proof_path'])}")
        
        logger.log_info("proofs_generated", count=len(tree.leaves))
        
        # Verify individual file
        print("\n4. Verifying Individual File")
        print("-" * 40)
        
        test_file = files[2]
        proof = tree.get_proof(str(test_file))
        
        if proof:
            print(f"Proof found for: {test_file.name}")
            print(f"  File in tree: ✓")
            print(f"  Leaf hash: {proof['leaf_hash'][:16]}...")
            print(f"  Matches root: {proof['root_hash'] == root_hash}")
        else:
            print(f"No proof found for: {test_file.name}")
        
        logger.log_complete("merkle_example", 
                          files_verified=len(files),
                          root_hash=root_hash)
        
        print("\n" + "=" * 60)
        print("Merkle verification completed successfully!")
        print("=" * 60)


if __name__ == "__main__":
    main()
