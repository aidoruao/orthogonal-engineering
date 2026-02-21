"""
Merkle tree module for orthogonal-engineering.

Implements binary Merkle tree construction with the following specification:
- Leaf nodes: SHA-256(0x00 || canonical_bytes)
- Internal nodes: SHA-256(0x01 || left_hash || right_hash)
- Leaves ordered by canonical file path (UTF-8 lexicographic)
- Produces root hash and per-leaf inclusion proofs

Author: Orthogonal Engineering System
Date: 2026-02-16
Version: 1.1.0
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class MerkleTree:
    """Binary Merkle tree with deterministic construction."""

    def __init__(self):
        self.leaves: List[Tuple[str, str]] = []  # [(path, hash), ...]
        self.root: str = ""
        self.tree_levels: List[List[str]] = []

    def add_leaf(self, path: str, leaf_hash: str) -> None:
        """
        Add a leaf to the tree.

        Args:
            path: Canonical path (will be sorted lexicographically)
            leaf_hash: Hash of canonical bytes (64-char hex string)
        """
        self.leaves.append((path, leaf_hash))

    def build(self) -> str:
        """
        Build the Merkle tree and return the root hash.

        Returns:
            Root hash as hex string
        """
        if not self.leaves:
            self.root = hashlib.sha256(b'').hexdigest()
            return self.root

        # Sort leaves by path (UTF-8 lexicographic)
        self.leaves.sort(key=lambda x: x[0])

        # Build leaf level with 0x00 prefix
        current_level = []
        for _path, leaf_hash in self.leaves:
            leaf_data = b'\x00' + bytes.fromhex(leaf_hash)
            current_level.append(hashlib.sha256(leaf_data).hexdigest())

        self.tree_levels = [current_level.copy()]

        # Build upper levels
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                internal_data = b'\x01' + bytes.fromhex(left) + bytes.fromhex(right)
                next_level.append(hashlib.sha256(internal_data).hexdigest())

            self.tree_levels.append(next_level.copy())
            current_level = next_level

        self.root = current_level[0]
        return self.root

    def get_inclusion_proof(self, path: str) -> Dict[str, Any]:
        """
        Get inclusion proof for a specific path.

        Args:
            path: Path to get proof for

        Returns:
            Proof as dictionary with path, leaf_hash, proof, and root

        Raises:
            ValueError: If path not found in tree
        """
        leaf_index: Optional[int] = None
        leaf_hash: Optional[str] = None
        for i, (p, h) in enumerate(self.leaves):
            if p == path:
                leaf_index = i
                leaf_hash = h
                break

        if leaf_index is None:
            raise ValueError(f"Path not found in tree: {path}")

        proof_hashes = []
        index = leaf_index

        for level in self.tree_levels[:-1]:
            if index % 2 == 0:
                sibling_index = index + 1
                sibling_hash = level[sibling_index] if sibling_index < len(level) else level[index]
                proof_hashes.append({'position': 'right', 'hash': sibling_hash})
            else:
                sibling_index = index - 1
                proof_hashes.append({'position': 'left', 'hash': level[sibling_index]})
            index = index // 2

        return {
            'path': path,
            'leaf_hash': leaf_hash,
            'proof': proof_hashes,
            'root': self.root,
        }

    def export_proofs_jsonl(self, output_path: Path) -> None:
        """
        Export inclusion proofs for all leaves as JSONL.

        Args:
            output_path: Path to output JSONL file
        """
        with open(output_path, 'w') as f:
            for path, _ in self.leaves:
                proof = self.get_inclusion_proof(path)
                f.write(json.dumps(proof, separators=(',', ':')) + '\n')


def build_merkle_tree_from_files(file_hashes: List[Tuple[str, str]]) -> MerkleTree:
    """
    Build a Merkle tree from a list of (canonical_path, hash) tuples.

    Args:
        file_hashes: List of (canonical_path, hash) tuples

    Returns:
        Built MerkleTree with root computed
    """
    tree = MerkleTree()
    for path, hash_value in file_hashes:
        tree.add_leaf(path, hash_value)
    tree.build()
    return tree


def verify_inclusion_proof(proof: Dict[str, Any]) -> bool:
    """
    Verify a Merkle inclusion proof.

    Args:
        proof: Proof dictionary with path, leaf_hash, proof, and root

    Returns:
        True if proof is valid
    """
    leaf_data = b'\x00' + bytes.fromhex(proof['leaf_hash'])
    current_hash = hashlib.sha256(leaf_data).hexdigest()

    for step in proof['proof']:
        if step['position'] == 'left':
            internal_data = b'\x01' + bytes.fromhex(step['hash']) + bytes.fromhex(current_hash)
        else:
            internal_data = b'\x01' + bytes.fromhex(current_hash) + bytes.fromhex(step['hash'])
        current_hash = hashlib.sha256(internal_data).hexdigest()

    return current_hash == proof['root']
