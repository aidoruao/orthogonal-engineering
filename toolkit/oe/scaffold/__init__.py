"""
Deterministic, Auditable Repository Scaffold

A comprehensive toolkit for repository-wide canonicalization, hashing,
Merkle tree construction, manifest generation, and GTA handling.meta
clamp pipeline processing.
"""

__version__ = "1.0.0"

from .canonicalizer import canonical_byte_representation
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
]
