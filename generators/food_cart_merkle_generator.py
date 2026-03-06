#!/usr/bin/env python3
"""
Food Cart Merkle Root Generator
================================

Generates Merkle root from the manifest.

Implements INV-MERKLE-001 and INV-MERKLE-002.

Authority: out/food_cart_manifest.jsonl
Version: 1.0.0
"""

import hashlib
import json
import sys
from pathlib import Path
from typing import List


class MerkleTree:
    """Simple Merkle tree implementation for manifest verification."""
    
    def __init__(self, leaves: List[str]):
        """
        Initialize Merkle tree with leaf hashes.
        
        Args:
            leaves: List of leaf node hashes (hex strings)
        """
        self.leaves = leaves
        self.root = None
        
    def compute_root(self) -> str:
        """
        Compute Merkle root from leaves.
        
        INV-MERKLE-001: Merkle root must match manifest.
        INV-MERKLE-002: Changing any node changes root.
        
        Returns:
            Merkle root hash (hex string)
        """
        if not self.leaves:
            # Empty tree has null root
            return hashlib.sha256(b"null").hexdigest()
            
        # Start with leaves as current level
        current_level = [bytes.fromhex(leaf) for leaf in self.leaves]
        
        # Build tree bottom-up
        while len(current_level) > 1:
            next_level = []
            
            # Process pairs
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                
                # If odd number of nodes, duplicate last one (standard Merkle tree behavior)
                if i + 1 < len(current_level):
                    right = current_level[i + 1]
                else:
                    right = left
                    
                # Compute parent hash: H(left || right)
                combined = left + right
                parent = hashlib.sha256(combined).digest()
                next_level.append(parent)
                
            current_level = next_level
            
        # Root is the single remaining hash
        self.root = current_level[0].hex()
        return self.root


class MerkleRootGenerator:
    """Generates Merkle root from manifest."""
    
    def __init__(self, manifest_path: str):
        """
        Initialize generator.
        
        Args:
            manifest_path: Path to food_cart_manifest.jsonl
        """
        self.manifest_path = Path(manifest_path)
        
    def generate_merkle_root(self, output_path: str) -> str:
        """
        Generate Merkle root from manifest.
        
        Args:
            output_path: Path to write merkle root file
            
        Returns:
            Merkle root hash (hex string)
        """
        if not self.manifest_path.exists():
            print(f"❌ Manifest not found: {self.manifest_path}")
            sys.exit(1)
            
        print(f"🌳 Computing Merkle root from manifest...")
        
        # Load manifest entries
        entries = []
        with open(self.manifest_path, 'r') as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
                    
        print(f"   Loaded {len(entries)} manifest entries")
        
        # Extract content hashes (these are our leaf nodes)
        leaf_hashes = [entry['content_hash'] for entry in entries]
        
        # Build Merkle tree
        tree = MerkleTree(leaf_hashes)
        merkle_root = tree.compute_root()
        
        print(f"   Merkle root: {merkle_root}")
        
        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(merkle_root + '\n')
            
        print(f"✅ Wrote Merkle root to {output_path}")
        
        return merkle_root
        
    def verify_merkle_root(self, root_path: str) -> bool:
        """
        Verify Merkle root against manifest.
        
        Returns:
            True if root matches, False otherwise
        """
        root_file = Path(root_path)
        
        if not root_file.exists():
            print(f"❌ Merkle root file not found: {root_path}")
            return False
            
        print(f"🔍 Verifying Merkle root...")
        
        # Read stored root
        with open(root_file, 'r') as f:
            stored_root = f.read().strip()
            
        # Compute expected root
        entries = []
        with open(self.manifest_path, 'r') as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
                    
        leaf_hashes = [entry['content_hash'] for entry in entries]
        tree = MerkleTree(leaf_hashes)
        expected_root = tree.compute_root()
        
        # INV-MERKLE-001: Merkle root must match manifest
        if stored_root != expected_root:
            print(f"❌ INV-MERKLE-001 failed: Merkle root mismatch")
            print(f"   Stored:   {stored_root}")
            print(f"   Expected: {expected_root}")
            return False
            
        print(f"   ✅ INV-MERKLE-001: Merkle root matches manifest")
        print(f"   Root: {stored_root}")
        
        return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate Merkle root from Food Cart manifest"
    )
    parser.add_argument(
        "--manifest",
        default="out/food_cart_manifest.jsonl",
        help="Path to manifest JSONL file"
    )
    parser.add_argument(
        "--output",
        default="out/food_cart_merkle_root.txt",
        help="Output path for Merkle root"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify Merkle root after generation"
    )
    
    args = parser.parse_args()
    
    # Generate
    generator = MerkleRootGenerator(args.manifest)
    generator.generate_merkle_root(args.output)
    
    # Verify if requested
    if args.verify:
        print()
        valid = generator.verify_merkle_root(args.output)
        if not valid:
            print()
            print("❌ Merkle root verification failed!")
            sys.exit(1)
        else:
            print()
            print("✅ Merkle root verification passed!")


if __name__ == "__main__":
    main()
