"""
<<<<<<< HEAD
Deterministic, auditable Python scaffold for orthogonal-engineering.

This scaffold provides tools for deterministic file canonicalization, hashing,
Merkle tree construction, and auditable logging for local repository operations.

Key principles:
- Deterministic: Same input always produces same output
- Auditable: All operations logged with timestamps and step IDs
- Safe: Defaults to dry-run mode, requires --apply for modifications
- Backup-first: Mandatory backups before any modifications

Modules:
- canonicalizer: Deterministic byte representation of files
- hasher: SHA-256 hashing of canonical bytes
- merkle: Binary Merkle tree construction
- manifest: JSONL manifest streaming
- logger: JSONL logging with monotonic step IDs
- handling_pipeline: GTA handling.meta parser
- cli: Command-line interface
=======
Deterministic, Auditable Repository Scaffold

A comprehensive toolkit for repository-wide canonicalization, hashing,
Merkle tree construction, manifest generation, and GTA handling.meta
clamp pipeline processing.
>>>>>>> copilot/add-deterministic-auditable-scaffold
"""

__version__ = "1.0.0"

from .canonicalizer import canonical_byte_representation
<<<<<<< HEAD
from .hasher import hash_file, hash_bytes
from .logger import ScaffoldLogger
from .merkle import MerkleTree
from .manifest import ManifestBuilder

__all__ = [
    "canonical_byte_representation",
    "hash_file",
    "hash_bytes",
    "ScaffoldLogger",
    "MerkleTree",
    "ManifestBuilder",
=======
from .hasher import compute_hash, compute_file_hash
from .merkle import MerkleTree, build_merkle_tree
from .manifest import generate_manifest
from .logger import ScaffoldLogger

__all__ = [
    "canonical_byte_representation",
    "compute_hash",
    "compute_file_hash",
    "MerkleTree",
    "build_merkle_tree",
    "generate_manifest",
    "ScaffoldLogger",
>>>>>>> copilot/add-deterministic-auditable-scaffold
]
