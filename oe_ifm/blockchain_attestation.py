"""
Blockchain Attestation Layer — oe_ifm/blockchain_attestation.py

Blockchain-inspired deterministic attestation for cross-platform verification.

This is NOT a real blockchain:
  - No mining or proof-of-work.
  - No network consensus.
  - Timestamps are externally supplied (not system clock) so blocks are
    reproducible across platforms.
  - The chain is a deterministic Merkle hash chain: each block's hash depends
    only on its content and the previous block's hash.

Purpose: provide a cryptographically auditable, tamper-evident log of
cross-platform verification results that can be independently reproduced from
the same inputs on any OS.

Author: Orthogonal Engineering
PR: #28
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import json
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Block
# ---------------------------------------------------------------------------

class AttestationBlock:
    """A single block in the deterministic attestation chain."""

    GENESIS_HASH = "0" * 64  # Deterministic genesis (no randomness)

    def __init__(
        self,
        previous_hash: str,
        data: bytes,
        timestamp: int,
        sequence: int,
        label: str = "",
    ):
        """Create an attestation block.

        Args:
            previous_hash: SHA-256 hex digest of the previous block.
            data: Arbitrary payload bytes (e.g. Merkle root, test result).
            timestamp: Externally supplied logical timestamp (NOT system clock).
                       Use a commit epoch, CI run ID, or other auditable source.
            sequence: Monotonically increasing block index (0, 1, 2, …).
            label: Human-readable label for this block (e.g. "ubuntu-py311").
        """
        self.previous_hash = previous_hash
        self.data_hash = hashlib.sha256(data).hexdigest()
        self.timestamp = timestamp
        self.sequence = sequence
        self.label = label
        self.hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Compute deterministic block hash from canonical JSON serialisation."""
        block_dict = {
            "previous": self.previous_hash,
            "data_hash": self.data_hash,
            "timestamp": self.timestamp,
            "sequence": self.sequence,
            "label": self.label,
        }
        canonical = json.dumps(block_dict, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict:
        """Serialise block to a plain dict for storage / transmission."""
        return {
            "sequence": self.sequence,
            "label": self.label,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "data_hash": self.data_hash,
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "AttestationBlock":
        """Reconstruct a block from its serialised dict (for verification)."""
        block = cls.__new__(cls)
        block.previous_hash = d["previous_hash"]
        block.data_hash = d["data_hash"]
        block.timestamp = d["timestamp"]
        block.sequence = d["sequence"]
        block.label = d["label"]
        block.hash = d["hash"]
        return block


# ---------------------------------------------------------------------------
# Chain
# ---------------------------------------------------------------------------

class AttestationChain:
    """Deterministic Merkle hash chain for cross-platform attestation."""

    def __init__(self):
        self.blocks: List[AttestationBlock] = []

    @property
    def tip(self) -> Optional[AttestationBlock]:
        """Most recent block, or None for an empty chain."""
        return self.blocks[-1] if self.blocks else None

    def append(
        self,
        data: bytes,
        timestamp: int,
        label: str = "",
    ) -> AttestationBlock:
        """Append a new block to the chain.

        Args:
            data: Payload bytes to attest.
            timestamp: Externally supplied logical timestamp.
            label: Human-readable description.

        Returns:
            The newly created and appended block.
        """
        previous_hash = self.tip.hash if self.tip else AttestationBlock.GENESIS_HASH
        sequence = len(self.blocks)
        block = AttestationBlock(
            previous_hash=previous_hash,
            data=data,
            timestamp=timestamp,
            sequence=sequence,
            label=label,
        )
        self.blocks.append(block)
        return block

    def verify(self) -> bool:
        """Verify the entire chain's integrity.

        Checks that:
          1. Each block's stored hash matches its recomputed hash.
          2. Each block's previous_hash matches the prior block's hash.

        Returns:
            True if the chain is intact; False otherwise.
        """
        for i, block in enumerate(self.blocks):
            # 1. Verify stored hash is correct
            recomputed = block._compute_hash()
            if block.hash != recomputed:
                return False
            # 2. Verify linkage
            if i == 0:
                expected_prev = AttestationBlock.GENESIS_HASH
            else:
                expected_prev = self.blocks[i - 1].hash
            if block.previous_hash != expected_prev:
                return False
        return True

    def chain_hash(self) -> str:
        """Return a single hash summarising the entire chain (tip hash)."""
        if not self.blocks:
            return AttestationBlock.GENESIS_HASH
        return self.tip.hash

    def to_list(self) -> List[Dict]:
        """Serialise chain to a list of dicts for JSON output."""
        return [b.to_dict() for b in self.blocks]

    @classmethod
    def from_list(cls, blocks: List[Dict]) -> "AttestationChain":
        """Reconstruct chain from serialised list of dicts."""
        chain = cls()
        chain.blocks = [AttestationBlock.from_dict(d) for d in blocks]
        return chain


# ---------------------------------------------------------------------------
# Convenience builder
# ---------------------------------------------------------------------------

def create_attestation_block(
    previous_hash: str,
    data: bytes,
    timestamp: int,
    sequence: int = 0,
    label: str = "",
) -> Dict:
    """Create a single deterministic attestation block and return its dict.

    Args:
        previous_hash: SHA-256 hex digest of the previous block.
        data: Payload bytes.
        timestamp: Externally supplied logical timestamp (NOT system clock).
        sequence: Block index.
        label: Human-readable label.

    Returns:
        Block as a plain dict (serialisable to JSON).
    """
    block = AttestationBlock(
        previous_hash=previous_hash,
        data=data,
        timestamp=timestamp,
        sequence=sequence,
        label=label,
    )
    return block.to_dict()
