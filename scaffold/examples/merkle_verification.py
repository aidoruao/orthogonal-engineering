"""
Merkle Tree Verification Example

Demonstrates Merkle tree construction and verification.
"""

from pathlib import Path
import tempfile
import shutil

from scaffold import MerkleTree


def main():
    """Run Merkle tree verification example."""
    print("=" * 60)
    print("Merkle Tree Verification Example")
    print("=" * 60)
    
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Create test files
        print("\n--- Creating Test Files ---")
        files = []
        for i in range(5):
            file_path = temp_dir / f"file{i}.txt"
            file_path.write_text(f"This is test file number {i}\nWith some content")
            files.append(file_path)
            print(f"✓ Created: {file_path.name}")
        
        # Build Merkle tree
        print("\n--- Building Merkle Tree ---")
        tree = MerkleTree()
        
        for file_path in files:
            tree.add_file(file_path)
            print(f"✓ Added: {file_path.name}")
        
        tree.build()
        root_hash = tree.get_root_hash()
        print(f"\n✓ Tree built successfully")
        print(f"Root hash: {root_hash}")
        print(f"Total leaves: {len(tree.leaves)}")
        
        # Generate and verify inclusion proofs
        print("\n--- Verifying Inclusion Proofs ---")
        for file_path in files:
            proof = tree.get_inclusion_proof(file_path)
            
            if proof:
                is_valid = proof.verify()
                status = "✓ VALID" if is_valid else "✗ INVALID"
                print(f"{status}: {file_path.name}")
                print(f"  Leaf hash: {proof.leaf_hash[:16]}...")
                print(f"  Proof path length: {len(proof.siblings)}")
            else:
                print(f"✗ No proof for {file_path.name}")
        
        # Verify entire tree
        print("\n--- Tree Verification ---")
        if tree.verify_tree():
            print("✓ Entire tree verification: PASSED")
        else:
            print("✗ Entire tree verification: FAILED")
        
        # Export proofs
        print("\n--- Exporting Proofs ---")
        proofs_file = temp_dir / "merkle_proofs.jsonl"
        tree.export_proofs_jsonl(proofs_file)
        print(f"✓ Proofs exported to: {proofs_file.name}")
        
        # Read and display proof structure
        import json
        with open(proofs_file, 'r') as f:
            first_proof = json.loads(f.readline())
        
        print("\nExample proof structure:")
        print(f"  Leaf path: {first_proof['leaf_path']}")
        print(f"  Leaf hash: {first_proof['leaf_hash'][:16]}...")
        print(f"  Root hash: {first_proof['root_hash'][:16]}...")
        print(f"  Proof path steps: {len(first_proof['proof_path'])}")
        
        # Demonstrate determinism
        print("\n--- Testing Determinism ---")
        tree2 = MerkleTree()
        for file_path in files:
            tree2.add_file(file_path)
        tree2.build()
        root_hash2 = tree2.get_root_hash()
        
        if root_hash == root_hash2:
            print("✓ Tree root is deterministic")
            print(f"  First build:  {root_hash}")
            print(f"  Second build: {root_hash2}")
        else:
            print("✗ Tree root is NOT deterministic")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        print("\n✓ Cleanup complete")
    
    print("\n" + "=" * 60)
    print("Merkle tree verification example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
