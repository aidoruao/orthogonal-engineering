"""
Manifest management for content-addressable storage.

Provides manifest creation, validation, and management for CAS operations.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from hasher import hash_file
from merkle import MerkleTree


class Manifest:
    """Manifest for tracking content-addressable files."""

    def __init__(self, name: str = "manifest"):
        self.name = name
        self.entries: List[Dict[str, Any]] = []

    def add_entry(self, filepath: Union[str, Path]) -> None:
        """Add a file entry to the manifest."""
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        entry = {
            "path": str(filepath),
            "hash": hash_file(filepath),
            "size": filepath.stat().st_size,
        }
        self.entries.append(entry)

    def save(self, output_path: Union[str, Path]) -> None:
        """Save manifest to JSON file."""
        output_path = Path(output_path)
        data = {
            "name": self.name,
            "entries": self.entries,
        }
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

    def get_merkle_root(self) -> Optional[str]:
        """Compute Merkle root of all entry hashes."""
        if not self.entries:
            return None
        hashes = [entry["hash"] for entry in self.entries]
        tree = MerkleTree(hashes)
        return tree.get_root_hash()

    @classmethod
    def load(cls, path: Union[str, Path]) -> "Manifest":
        """Load manifest from JSON file."""
        path = Path(path)
        with open(path, "r") as f:
            data = json.load(f)

        manifest = cls(name=data.get("name", "manifest"))
        manifest.entries = data.get("entries", [])
        return manifest

    def verify(self) -> Dict[str, Any]:
        """Verify all entries in the manifest."""
        valid = 0
        invalid = 0
        missing = 0
        details = []

        for entry in self.entries:
            filepath = Path(entry["path"])
            if not filepath.exists():
                missing += 1
                details.append({"path": str(filepath), "status": "missing"})
                continue

            actual_hash = hash_file(filepath)
            if actual_hash == entry["hash"]:
                valid += 1
                details.append({"path": str(filepath), "status": "valid"})
            else:
                invalid += 1
                details.append({"path": str(filepath), "status": "invalid"})

        return {
            "total": len(self.entries),
            "valid": valid,
            "invalid": invalid,
            "missing": missing,
            "verified": invalid == 0 and missing == 0,
            "details": details,
        }


def generate_manifest(
    repo_path: Path,
    output_path: Path,
    patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Generate a manifest for a repository."""
    repo_path = Path(repo_path)
    output_path = Path(output_path)

    manifest = Manifest(name="repo_manifest")

    # Collect files
    if patterns:
        files = set()
        for pattern in patterns:
            files.update(repo_path.rglob(pattern))
    else:
        files = set(repo_path.rglob("*"))

    # Filter
    filtered = []
    for f in files:
        if not f.is_file():
            continue

        # Exclude
        if exclude_patterns:
            excluded = False
            for excl in exclude_patterns:
                # Simple glob matching
                if excl.endswith("/**"):
                    prefix = excl[:-3]
                    if prefix in str(f.relative_to(repo_path)):
                        excluded = True
                        break
                elif excl.startswith("**/*"):
                    suffix = excl[3:]
                    if str(f).endswith(suffix):
                        excluded = True
                        break
                elif excl.startswith("**"):
                    suffix = excl[2:]
                    if suffix in str(f):
                        excluded = True
                        break
            if excluded:
                continue

        filtered.append(f)

    for f in sorted(filtered):
        manifest.add_entry(f)

    manifest.save(output_path)

    return {
        "manifest_path": str(output_path),
        "entries": len(manifest.entries),
        "merkle_root": manifest.get_merkle_root(),
    }
