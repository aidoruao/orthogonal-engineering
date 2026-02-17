"""
Deterministic Auditable Python Scaffold

A local-run, dry-run-default scaffold for auditable file processing with
mandatory backups, canonical byte representation, Merkle tree verification,
and JSONL logging.

Version: 1.0.0
Author: Orthogonal Engineering
"""

__version__ = "1.0.0"

from .canonicalizer import canonical_byte_representation
from .hasher import compute_file_hash, compute_hash
from .logger import ScaffoldLogger
from .manifest import ManifestGenerator
from .merkle import MerkleTree

__all__ = [
    "canonical_byte_representation",
    "compute_file_hash",
    "compute_hash",
    "ScaffoldLogger",
    "ManifestGenerator",
    "MerkleTree",
]
