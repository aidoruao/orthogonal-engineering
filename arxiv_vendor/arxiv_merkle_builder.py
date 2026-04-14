#!/usr/bin/env python3
"""
arXiv Merkle Builder — Build Merkle trees over metadata manifests.

Computes per-category Merkle roots and a grand root over all categories.
Uses the OE Merkle specification:
  Leaf: SHA-256(0x00 || hash_bytes)
  Internal: SHA-256(0x01 || left || right)

Standard: Yeshua
Version: 1.0.0
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class MerkleTree:
    """Binary Merkle tree with deterministic construction."""

    def __init__(self):
        self.leaves: List[Tuple[str, str]] = []
        self.root: str = ""
        self.tree_levels: List[List[str]] = []

    def add_leaf(self, path: str, leaf_hash: str) -> None:
        self.leaves.append((path, leaf_hash))

    def build(self) -> str:
        if not self.leaves:
            self.root = hashlib.sha256(b"").hexdigest()
            return self.root

        self.leaves.sort(key=lambda x: x[0])
        current_level = []
        for _path, leaf_hash in self.leaves:
            leaf_data = b"\x00" + bytes.fromhex(leaf_hash)
            current_level.append(hashlib.sha256(leaf_data).hexdigest())

        self.tree_levels = [current_level.copy()]
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                internal_data = b"\x01" + bytes.fromhex(left) + bytes.fromhex(right)
                next_level.append(hashlib.sha256(internal_data).hexdigest())
            self.tree_levels.append(next_level.copy())
            current_level = next_level

        self.root = current_level[0]
        return self.root


def build_category_merkle(metadata_dir: Path, category_id: str) -> Tuple[str, int]:
    jsonl_path = metadata_dir / f"{category_id.replace('.', '_')}.jsonl"
    if not jsonl_path.exists():
        return "", 0

    tree = MerkleTree()
    count = 0
    with open(jsonl_path, "r") as f:
        for idx, line in enumerate(f):
            line = line.rstrip("\n")
            if not line:
                continue
            h = hashlib.sha256(line.encode("utf-8")).hexdigest()
            tree.add_leaf(f"{category_id}/{idx}", h)
            count += 1

    root = tree.build()
    return root, count


def main():
    parser = argparse.ArgumentParser(description="arXiv Merkle Builder")
    parser.add_argument("--metadata-dir", default="arxiv_vendor/metadata")
    parser.add_argument("--output-dir", default="arxiv_vendor/merkle_roots")
    args = parser.parse_args()

    metadata_dir = Path(args.metadata_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Discover categories from metadata files
    category_roots: Dict[str, str] = {}
    category_counts: Dict[str, int] = {}

    for jsonl_file in sorted(metadata_dir.glob("*.jsonl")):
        if jsonl_file.name.endswith("_hashes.jsonl"):
            continue
        if jsonl_file.name == "materialization_summary.json":
            continue
        cat_id = jsonl_file.stem.replace("_", ".")
        root, count = build_category_merkle(metadata_dir, cat_id)
        if root:
            category_roots[cat_id] = root
            category_counts[cat_id] = count
            per_cat_path = output_dir / f"{jsonl_file.stem}_root.json"
            with open(per_cat_path, "w") as f:
                json.dump({"category": cat_id, "merkle_root": root, "paper_count": count}, f, indent=2)
            print(f"Category {cat_id}: root={root} count={count}")

    # Grand root over all category roots
    grand_tree = MerkleTree()
    for cat_id in sorted(category_roots):
        grand_tree.add_leaf(cat_id, category_roots[cat_id])
    grand_root = grand_tree.build()

    grand_path = output_dir / "arxiv_grand_root.json"
    with open(grand_path, "w") as f:
        json.dump(
            {
                "merkle_root": grand_root,
                "category_count": len(category_roots),
                "categories": {cat: {"root": category_roots[cat], "count": category_counts[cat]} for cat in sorted(category_roots)},
            },
            f,
            indent=2,
        )
    print(f"Grand root: {grand_root}")


if __name__ == "__main__":
    main()
