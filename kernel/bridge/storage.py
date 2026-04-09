"""Storage Bridge — Content-addressed persistent storage.

The VFS already uses SHA-256 hashes. A StorageCap grants the right
to read/write blobs by hash. The underlying storage can be anything:
a file on the host, a raw partition, IPFS, SQLite.
The kernel doesn't care. It only cares that hash matches content.

Yeshua Inversion: Don't write filesystem drivers. Mediate content-addressed blobs.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict
from fractions import Fraction
import hashlib

from axioms.logic import ProofObject


@dataclass(frozen=True)
class StorageCap:
    """Capability for storage access."""
    process_id: str
    read_allowed: bool
    write_allowed: bool
    quota: Fraction  # Maximum bytes


@dataclass
class Blob:
    """A content-addressed blob."""
    content_hash: str  # SHA-256 of content
    size: Fraction
    content: bytes  # The actual data
    
    def verify_integrity(self) -> bool:
        """Verify that content_hash matches actual content."""
        actual_hash = hashlib.sha256(self.content).hexdigest()
        return actual_hash == self.content_hash


@dataclass
class StorageBridgeState:
    """State of the storage bridge."""
    caps: Dict[str, List[StorageCap]] = field(default_factory=dict)
    blobs: Dict[str, Blob] = field(default_factory=dict)  # content_hash -> Blob
    usage: Dict[str, Fraction] = field(default_factory=dict)  # process_id -> bytes stored


def storage_write(state: StorageBridgeState,
                 process_id: str,
                 content: bytes,
                 cap: StorageCap) -> Tuple[str, StorageBridgeState, ProofObject]:
    """Write blob. Returns content hash. Capability-gated.
    
    Verifies:
    - Process holds write cap
    - Quota not exceeded
    - Hash matches content (integrity)
    
    Args:
        state: Current storage bridge state
        process_id: Process writing
        content: Content to write
        cap: Storage capability
    
    Returns:
        (content_hash, new_state, proof)
    """
    # Verify process holds this cap
    process_caps = state.caps.get(process_id, [])
    if cap not in process_caps:
        return "", state, ProofObject(
            rule="StorageWrite",
            premises=[f"process={process_id}", "cap not held"],
            conclusion="write denied: invalid capability"
        )
    
    # Check write permission
    if not cap.write_allowed:
        return "", state, ProofObject(
            rule="StorageWrite",
            premises=[f"process={process_id}", "write_allowed=False"],
            conclusion="write denied: no write permission"
        )
    
    # Check quota
    size = Fraction(len(content))
    used = state.usage.get(process_id, Fraction(0))
    if used + size > cap.quota:
        return "", state, ProofObject(
            rule="StorageWrite",
            premises=[
                f"used={used}",
                f"size={size}",
                f"quota={cap.quota}"
            ],
            conclusion="write denied: quota exceeded"
        )
    
    # Compute hash
    content_hash = hashlib.sha256(content).hexdigest()
    
    # Create blob
    blob = Blob(
        content_hash=content_hash,
        size=size,
        content=content
    )
    
    # Update state
    new_blobs = state.blobs.copy()
    new_blobs[content_hash] = blob
    
    new_usage = state.usage.copy()
    new_usage[process_id] = used + size
    
    new_state = StorageBridgeState(
        caps=state.caps,
        blobs=new_blobs,
        usage=new_usage
    )
    
    proof = ProofObject(
        rule="StorageWrite",
        premises=[
            f"process={process_id}",
            f"size={size}",
            f"hash={content_hash[:16]}..."
        ],
        conclusion="blob written"
    )
    
    return content_hash, new_state, proof


def storage_read(state: StorageBridgeState,
                process_id: str,
                content_hash: str,
                cap: StorageCap) -> Tuple[Optional[bytes], StorageBridgeState, ProofObject]:
    """Read blob by hash. Capability-gated.
    
    Verifies:
    - Process holds read cap
    - Hash exists
    - Returned content matches hash (integrity on read)
    
    Args:
        state: Current storage bridge state
        process_id: Process reading
        content_hash: Hash of blob to read
        cap: Storage capability
    
    Returns:
        (content, new_state, proof)
    """
    # Verify process holds this cap
    process_caps = state.caps.get(process_id, [])
    if cap not in process_caps:
        return None, state, ProofObject(
            rule="StorageRead",
            premises=[f"process={process_id}", "cap not held"],
            conclusion="read denied: invalid capability"
        )
    
    # Check read permission
    if not cap.read_allowed:
        return None, state, ProofObject(
            rule="StorageRead",
            premises=[f"process={process_id}", "read_allowed=False"],
            conclusion="read denied: no read permission"
        )
    
    # Check if blob exists
    blob = state.blobs.get(content_hash)
    if blob is None:
        return None, state, ProofObject(
            rule="StorageRead",
            premises=[f"hash={content_hash[:16]}...", "not found"],
            conclusion="read failed: blob not found"
        )
    
    # Verify integrity on read
    if not blob.verify_integrity():
        return None, state, ProofObject(
            rule="StorageRead",
            premises=[f"hash={content_hash[:16]}...", "integrity check failed"],
            conclusion="read failed: corruption detected"
        )
    
    proof = ProofObject(
        rule="StorageRead",
        premises=[
            f"process={process_id}",
            f"hash={content_hash[:16]}...",
            f"size={blob.size}"
        ],
        conclusion="blob read"
    )
    
    return blob.content, state, proof


def check_integrity(state: StorageBridgeState) -> Tuple[bool, ProofObject]:
    """Every blob's content_hash == SHA-256(content).
    
    Args:
        state: Storage bridge state
    
    Returns:
        (intact, proof)
    """
    violations = []
    
    for content_hash, blob in state.blobs.items():
        if not blob.verify_integrity():
            violations.append(content_hash)
    
    intact = len(violations) == 0
    
    proof = ProofObject(
        rule="IntegrityCheck",
        premises=[
            f"blobs={len(state.blobs)}",
            f"violations={len(violations)}"
        ],
        conclusion=f"intact={intact}"
    )
    
    return intact, proof


def check_quota_bounded(state: StorageBridgeState) -> Tuple[bool, ProofObject]:
    """No process exceeds its storage quota.
    
    Args:
        state: Storage bridge state
    
    Returns:
        (bounded, proof)
    """
    violations = []
    
    for process_id, caps in state.caps.items():
        used = state.usage.get(process_id, Fraction(0))
        for cap in caps:
            if used > cap.quota:
                violations.append(process_id)
                break
    
    bounded = len(violations) == 0
    
    proof = ProofObject(
        rule="QuotaBounded",
        premises=[
            f"processes={len(state.caps)}",
            f"violations={len(violations)}"
        ],
        conclusion=f"bounded={bounded}"
    )
    
    return bounded, proof
