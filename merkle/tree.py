"""
Merkle tree implementation for content verification.

Provides hierarchical hashing for efficient content verification.
Implements a deterministic binary Merkle tree with:
- Leaf nodes: sha256(0x00 || canonical_bytes)
- Internal nodes: sha256(0x01 || left_hash || right_hash)
- Leaves ordered by canonical path (UTF-8 lexicographic)
- JSONL inclusion proofs output

Author: Orthogonal Engineering
Date: 2026-02-16
Version: 1.0.0
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from hasher import hash_data, sha256_hex


class MerkleNode:
    """Node in a Merkle tree."""

    def __init__(
        self,
        hash_value: str,
        left: Optional["MerkleNode"] = None,
        right: Optional["MerkleNode"] = None,
        path: Optional[str] = None,
    ):
        self.hash_value = hash_value
        self.left = left
        self.right = right
        self.path = path
        self.is_leaf = left is None and right is None


class MerkleTree:
    """Merkle tree for hierarchical content verification."""

    def __init__(self, leaves: List[str]):
        """
        Build Merkle tree from leaf hashes.

        Args:
            leaves: List of leaf hash values

        Raises:
            ValueError: If leaves list is empty
        """
        if not leaves:
            raise ValueError("Cannot create Merkle tree with no leaves")

        self.leaves = leaves
        self.root = self._build_tree(leaves)

    def _build_tree(self, hashes: List[str]) -> MerkleNode:
        """
        Recursively build Merkle tree.

        Args:
            hashes: List of hash values

        Returns:
            Root node of the tree
        """
        if len(hashes) == 1:
            return MerkleNode(hashes[0])

        # Build leaf nodes
        nodes = [MerkleNode(h) for h in hashes]

        # Build tree bottom-up
        while len(nodes) > 1:
            next_level = []

            for i in range(0, len(nodes), 2):
                left = nodes[i]
                right = nodes[i + 1] if i + 1 < len(nodes) else left

                # Combine hashes
                combined = left.hash_value + right.hash_value
                parent_hash = hash_data(combined)

                parent = MerkleNode(parent_hash, left, right)
                next_level.append(parent)

            nodes = next_level

        return nodes[0]

    def get_root_hash(self) -> str:
        """Get root hash of the tree."""
        return self.root.hash_value

    def get_proof(self, index: int) -> List[Tuple[str, str]]:
        """
        Get Merkle proof for leaf at index.

        Args:
            index: Index of leaf to prove

        Returns:
            List of (hash, position) tuples for proof path

        Raises:
            IndexError: If index is out of range
        """
        if index < 0 or index >= len(self.leaves):
            raise IndexError(
                f"Index {index} out of range for {len(self.leaves)} leaves"
            )

        proof = []
        nodes = [MerkleNode(h) for h in self.leaves]

        # Track current index as we go up the tree
        current_index = index

        while len(nodes) > 1:
            next_level = []

            for i in range(0, len(nodes), 2):
                left = nodes[i]
                right = nodes[i + 1] if i + 1 < len(nodes) else left

                # If this pair contains our node, add sibling to proof
                if i == current_index or i + 1 == current_index:
                    if i == current_index and i + 1 < len(nodes):
                        # Our node is on left, add right sibling
                        proof.append((right.hash_value, "right"))
                    elif i + 1 == current_index:
                        # Our node is on right, add left sibling
                        proof.append((left.hash_value, "left"))

                combined = left.hash_value + right.hash_value
                parent_hash = hash_data(combined)
                parent = MerkleNode(parent_hash, left, right)
                next_level.append(parent)

            # Update current index for next level
            current_index = current_index // 2
            nodes = next_level

        return proof

    def verify_proof(self, leaf_hash: str, index: int, proof: List[Tuple[str, str]]) -> bool:
        """
        Verify Merkle proof for a leaf.

        Args:
            leaf_hash: Hash of the leaf to verify
            index: Index of the leaf
            proof: Proof path from get_proof()

        Returns:
            True if proof is valid
        """
        current_hash = leaf_hash

        for sibling_hash, position in proof:
            if position == "left":
                combined = sibling_hash + current_hash
            else:
                combined = current_hash + sibling_hash

            current_hash = hash_data(combined)

        return current_hash == self.root.hash_value


class MerkleTreeBuilder:
    """Build binary Merkle trees with inclusion proofs."""

    def __init__(self):
        """Initialize Merkle tree builder."""
        self.leaves: List[MerkleNode] = []
        self.root: Optional[MerkleNode] = None

    def add_leaf(self, canonical_path: str, canonical_bytes: bytes) -> None:
        """
        Add a leaf node to the tree.

        Leaf hash = sha256(0x00 || canonical_bytes)

        Args:
            canonical_path: Canonical path for ordering
            canonical_bytes: Canonicalized file content
        """
        # Compute leaf hash: sha256(0x00 || data)
        leaf_data = b"\x00" + canonical_bytes
        leaf_hash = sha256_hex(leaf_data)

        leaf = MerkleNode(leaf_hash, path=canonical_path)
        self.leaves.append(leaf)

    def build_tree(self) -> str:
        """
        Build the Merkle tree and return the root hash.

        Leaves are ordered by canonical path (UTF-8 lexicographic).
        Internal nodes: sha256(0x01 || left_hash || right_hash)

        Returns:
            Root hash as hexadecimal string
        """
        if not self.leaves:
            # Empty tree
            return sha256_hex(b"")

        # Sort leaves by canonical path (UTF-8 lexicographic)
        sorted_leaves = sorted(self.leaves, key=lambda n: n.path.encode("utf-8") if n.path else b"")

        # Build tree bottom-up
        current_level = sorted_leaves

        while len(current_level) > 1:
            next_level = []

            # Process pairs
            for i in range(0, len(current_level), 2):
                left = current_level[i]

                if i + 1 < len(current_level):
                    # We have a pair
                    right = current_level[i + 1]
                else:
                    # Odd number of nodes, duplicate the last one
                    right = current_level[i]

                # Compute internal node hash: sha256(0x01 || left_hash || right_hash)
                internal_data = (
                    b"\x01"
                    + bytes.fromhex(left.hash_value)
                    + bytes.fromhex(right.hash_value)
                )
                internal_hash = sha256_hex(internal_data)

                internal_node = MerkleNode(internal_hash, left, right)
                next_level.append(internal_node)

            current_level = next_level

        self.root = current_level[0]
        return self.root.hash_value

    def generate_inclusion_proof(self, target_path: str) -> Dict:
        """
        Generate inclusion proof for a specific file.

        Args:
            target_path: Canonical path of the file

        Returns:
            Inclusion proof dictionary with path, sibling hashes, and directions
        """
        if not self.root:
            raise ValueError("Tree must be built before generating proofs")

        # Find the leaf
        target_leaf = None
        sorted_leaves = sorted(
            self.leaves, key=lambda n: n.path.encode("utf-8") if n.path else b""
        )

        for i, leaf in enumerate(sorted_leaves):
            if leaf.path == target_path:
                target_leaf = leaf
                break

        if not target_leaf:
            raise ValueError(f"Path not found in tree: {target_path}")

        # Build proof by traversing from leaf to root
        proof = {
            "path": target_path,
            "leaf_hash": target_leaf.hash_value,
            "siblings": [],
            "root_hash": self.root.hash_value,
        }

        # Reconstruct path to root
        current_level = sorted_leaves
        current_index = sorted_leaves.index(target_leaf)

        while len(current_level) > 1:
            # Determine sibling
            if current_index % 2 == 0:
                # We're the left child
                if current_index + 1 < len(current_level):
                    sibling_hash = current_level[current_index + 1].hash_value
                    direction = "right"
                else:
                    # Duplicate ourselves
                    sibling_hash = current_level[current_index].hash_value
                    direction = "right"
            else:
                # We're the right child
                sibling_hash = current_level[current_index - 1].hash_value
                direction = "left"

            proof["siblings"].append({"hash": sibling_hash, "direction": direction})

            # Move up to parent level
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                if i + 1 < len(current_level):
                    right = current_level[i + 1]
                else:
                    right = current_level[i]

                internal_data = (
                    b"\x01"
                    + bytes.fromhex(left.hash_value)
                    + bytes.fromhex(right.hash_value)
                )
                internal_hash = sha256_hex(internal_data)
                internal_node = MerkleNode(internal_hash, left, right)
                next_level.append(internal_node)

            current_level = next_level
            current_index = current_index // 2

        return proof

    def write_proofs(self, output_path: Path) -> None:
        """
        Write inclusion proofs for all leaves to JSONL file.

        Args:
            output_path: Path to output JSONL file
        """
        if not self.root:
            raise ValueError("Tree must be built before writing proofs")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            for leaf in self.leaves:
                proof = self.generate_inclusion_proof(leaf.path)
                f.write(json.dumps(proof) + "\n")


def verify_inclusion_proof(proof: Dict) -> bool:
    """
    Verify an inclusion proof.

    Args:
        proof: Inclusion proof dictionary

    Returns:
        True if proof is valid, False otherwise
    """
    # Start with leaf hash
    current_hash = proof["leaf_hash"]

    # Apply siblings to reconstruct root
    for sibling in proof["siblings"]:
        sibling_hash = sibling["hash"]
        direction = sibling["direction"]

        if direction == "right":
            # Sibling is on the right
            internal_data = (
                b"\x01"
                + bytes.fromhex(current_hash)
                + bytes.fromhex(sibling_hash)
            )
        else:
            # Sibling is on the left
            internal_data = (
                b"\x01"
                + bytes.fromhex(sibling_hash)
                + bytes.fromhex(current_hash)
            )

        current_hash = sha256_hex(internal_data)

    # Check if we reached the correct root
    return current_hash == proof["root_hash"]
