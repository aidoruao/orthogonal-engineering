#!/usr/bin/env python3
"""
Merkle Chain Generator for 1B LOC Architecture

Builds Merkle tree from manifests and generates inclusion proofs.
Provides cryptographic commitment to all generated code.

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class MerkleNode:
    """Node in Merkle tree."""
    
    def __init__(self, hash_value: str, left=None, right=None, is_leaf=False, node_id=None):
        self.hash = hash_value
        self.left = left
        self.right = right
        self.is_leaf = is_leaf
        self.node_id = node_id


class MerkleTree:
    """Binary Merkle tree with inclusion proofs."""
    
    def __init__(self, leaf_hashes: List[Tuple[str, str]]):
        """
        Build Merkle tree from leaf hashes.
        
        Args:
            leaf_hashes: List of (node_id, hash) tuples
        """
        if not leaf_hashes:
            raise ValueError("Cannot build Merkle tree with no leaves")
        
        self.leaves = leaf_hashes
        self.leaf_count = len(leaf_hashes)
        self.root = self._build_tree(leaf_hashes)
        
    def _build_tree(self, leaves: List[Tuple[str, str]]) -> MerkleNode:
        """
        Build binary Merkle tree bottom-up.
        
        Args:
            leaves: List of (node_id, hash) tuples
            
        Returns:
            Root MerkleNode
        """
        # Create leaf nodes with 0x00 prefix
        nodes = [
            MerkleNode(
                hash_value=self._hash_leaf(h),
                is_leaf=True,
                node_id=node_id
            )
            for node_id, h in leaves
        ]
        
        # Build tree level by level
        while len(nodes) > 1:
            next_level = []
            
            for i in range(0, len(nodes), 2):
                left = nodes[i]
                
                # If odd number of nodes, duplicate last one
                if i + 1 < len(nodes):
                    right = nodes[i + 1]
                else:
                    right = nodes[i]
                
                # Combine with 0x01 prefix for internal nodes
                parent_hash = self._hash_internal(left.hash, right.hash)
                parent = MerkleNode(parent_hash, left=left, right=right)
                next_level.append(parent)
            
            nodes = next_level
        
        return nodes[0]
    
    def _hash_leaf(self, data: str) -> str:
        """Hash leaf with 0x00 prefix."""
        combined = b'\x00' + data.encode('utf-8')
        return hashlib.sha256(combined).hexdigest()
    
    def _hash_internal(self, left: str, right: str) -> str:
        """Hash internal node with 0x01 prefix."""
        combined = b'\x01' + left.encode('utf-8') + right.encode('utf-8')
        return hashlib.sha256(combined).hexdigest()
    
    def get_root_hash(self) -> str:
        """Get Merkle root hash."""
        return self.root.hash
    
    def get_proof(self, leaf_index: int) -> List[Tuple[str, str]]:
        """
        Get Merkle inclusion proof for a leaf.
        
        Args:
            leaf_index: Index of leaf (0-based)
            
        Returns:
            List of (hash, side) tuples where side is 'left' or 'right'
        """
        if leaf_index < 0 or leaf_index >= self.leaf_count:
            raise ValueError(f"Invalid leaf index: {leaf_index}")
        
        proof = []
        
        # Build path from leaf to root
        # Start at leaf level
        level_size = self.leaf_count
        current_index = leaf_index
        
        # Traverse up the tree
        nodes = [
            MerkleNode(
                hash_value=self._hash_leaf(h),
                is_leaf=True
            )
            for _, h in self.leaves
        ]
        
        while level_size > 1:
            # Find sibling
            if current_index % 2 == 0:
                # We're on the left, sibling is on the right
                sibling_index = current_index + 1
                side = 'right'
            else:
                # We're on the right, sibling is on the left
                sibling_index = current_index - 1
                side = 'left'
            
            # Get sibling hash (duplicate if at end)
            if sibling_index < len(nodes):
                sibling_hash = nodes[sibling_index].hash
            else:
                sibling_hash = nodes[current_index].hash
            
            proof.append((sibling_hash, side))
            
            # Move to parent level
            next_level = []
            for i in range(0, len(nodes), 2):
                left = nodes[i]
                right = nodes[i + 1] if i + 1 < len(nodes) else nodes[i]
                parent_hash = self._hash_internal(left.hash, right.hash)
                next_level.append(MerkleNode(parent_hash))
            
            nodes = next_level
            current_index = current_index // 2
            level_size = (level_size + 1) // 2
        
        return proof
    
    def verify_proof(
        self,
        leaf_hash: str,
        proof: List[Tuple[str, str]],
        root_hash: str
    ) -> bool:
        """
        Verify Merkle inclusion proof.
        
        Args:
            leaf_hash: Hash of leaf to verify
            proof: List of (hash, side) tuples
            root_hash: Expected root hash
            
        Returns:
            True if proof is valid
        """
        # Start with leaf hash (with 0x00 prefix)
        current = self._hash_leaf(leaf_hash)
        
        # Apply proof steps
        for sibling_hash, side in proof:
            if side == 'left':
                current = self._hash_internal(sibling_hash, current)
            else:
                current = self._hash_internal(current, sibling_hash)
        
        return current == root_hash


def build_merkle_from_manifests(manifest_files: List[str]) -> Tuple[str, Dict]:
    """
    Build Merkle tree from manifest files.
    
    Args:
        manifest_files: List of manifest JSONL file paths
        
    Returns:
        Tuple of (root_hash, proofs_dict)
    """
    print("Loading manifests...")
    
    # Collect all leaf hashes
    all_leaves = []
    
    for manifest_file in manifest_files:
        with open(manifest_file, 'r') as f:
            for line in f:
                entry = json.loads(line)
                all_leaves.append((entry['node_id'], entry['hash']))
    
    print(f"  Loaded {len(all_leaves):,} leaf nodes")
    
    # Sort for deterministic ordering
    all_leaves.sort(key=lambda x: x[0])
    
    print("Building Merkle tree...")
    tree = MerkleTree(all_leaves)
    root_hash = tree.get_root_hash()
    
    print(f"  Merkle root: {root_hash}")
    
    # Generate inclusion proofs
    print("Generating inclusion proofs...")
    proofs = {}
    
    for i, (node_id, leaf_hash) in enumerate(all_leaves):
        proof = tree.get_proof(i)
        proofs[node_id] = {
            "leaf_hash": leaf_hash,
            "proof": proof,
            "root": root_hash
        }
        
        if (i + 1) % 100000 == 0:
            print(f"  Generated {i + 1:,} / {len(all_leaves):,} proofs")
    
    return root_hash, proofs


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build Merkle tree from manifests (Yeshua Standard)"
    )
    parser.add_argument(
        "--manifests",
        type=str,
        nargs='+',
        help="Manifest JSONL files (supports wildcards)"
    )
    parser.add_argument(
        "--manifest-dir",
        type=str,
        default="manifests",
        help="Directory containing manifests (default: manifests/)"
    )
    parser.add_argument(
        "--output-root",
        type=str,
        default="merkle_roots/merkle_root.txt",
        help="Output file for Merkle root"
    )
    parser.add_argument(
        "--output-proofs",
        type=str,
        default="merkle_roots/merkle_proofs.jsonl",
        help="Output file for inclusion proofs"
    )
    parser.add_argument(
        "--recompute",
        action="store_true",
        help="Recompute and verify Merkle root"
    )
    
    args = parser.parse_args()
    
    # Get manifest files
    if args.manifests:
        manifest_files = args.manifests
    else:
        # Find all manifests in directory
        manifest_dir = Path(args.manifest_dir)
        manifest_files = list(manifest_dir.glob("batch_*_manifest.jsonl"))
        manifest_files = [str(f) for f in sorted(manifest_files)]
    
    if not manifest_files:
        print("ERROR: No manifest files found", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found {len(manifest_files)} manifest files")
    
    # Build Merkle tree
    root_hash, proofs = build_merkle_from_manifests(manifest_files)
    
    # Save root hash
    Path(args.output_root).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_root, 'w') as f:
        f.write(f"{root_hash}\n")
        f.write(f"# Merkle root for 1B LOC architecture (Yeshua Standard)\n")
        f.write(f"# Generated: {datetime.utcnow().isoformat()}Z\n")
        f.write(f"# Leaf count: {len(proofs):,}\n")
    
    print(f"\nMerkle root saved to: {args.output_root}")
    
    # Save proofs
    Path(args.output_proofs).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_proofs, 'w') as f:
        for node_id, proof_data in proofs.items():
            entry = {
                "node_id": node_id,
                **proof_data
            }
            f.write(json.dumps(entry) + '\n')
    
    print(f"Inclusion proofs saved to: {args.output_proofs}")
    print(f"\n✓ Merkle chain generation complete")
    print(f"  Root hash: {root_hash}")
    print(f"  Leaf nodes: {len(proofs):,}")


if __name__ == "__main__":
    main()
