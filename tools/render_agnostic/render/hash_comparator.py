#!/usr/bin/env python3
"""
tools/render_agnostic/render/hash_comparator.py — PR #41 Per-Frame Hash Comparator

Provides per-frame SHA-256 hash verification for the dual-path render pipeline.

LOGOS principle: truth or nothing.  If GPU output hash ≠ CPU reference hash,
the GPU output is discarded and the CPU frame is shown.

Author: Orthogonal Engineering
PR: #41
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class FrameVerificationResult:
    """Result of comparing CPU and GPU frame hashes for a single frame."""

    frame_index: int
    cpu_hash: str
    gpu_hash: Optional[str]
    verified: bool
    path_used: str  # "cpu_reference" | "gpu_verified" | "gpu_rejected"
    resolution: tuple[int, int]  # (width, height)

    def to_dict(self) -> dict:
        return {
            "frame": self.frame_index,
            "cpu_hash": self.cpu_hash,
            "gpu_hash": self.gpu_hash,
            "verified": self.verified,
            "path_used": self.path_used,
            "resolution": list(self.resolution),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"))


@dataclass
class RenderLedger:
    """
    Append-only render ledger: records per-frame verification results.

    Corresponds to render_ledger.jsonl in the problem statement.
    """

    entries: list[FrameVerificationResult] = field(default_factory=list)

    def append(self, result: FrameVerificationResult) -> None:
        self.entries.append(result)

    def to_jsonl(self) -> str:
        lines = [e.to_json() for e in self.entries]
        return "\n".join(lines) + ("\n" if lines else "")

    def write(self, path: Path) -> None:
        path.write_text(self.to_jsonl(), encoding="utf-8")

    @classmethod
    def read(cls, path: Path) -> "RenderLedger":
        ledger = cls()
        if not path.exists():
            return ledger
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            ledger.entries.append(
                FrameVerificationResult(
                    frame_index=d["frame"],
                    cpu_hash=d["cpu_hash"],
                    gpu_hash=d.get("gpu_hash"),
                    verified=d["verified"],
                    path_used=d["path_used"],
                    resolution=tuple(d["resolution"]),
                )
            )
        return ledger

    def verify_integrity(self) -> tuple[bool, list[str]]:
        """
        Verify that all verified entries have consistent hash values.

        Returns (ok, errors).
        """
        errors: list[str] = []
        for entry in self.entries:
            if entry.path_used == "gpu_verified":
                if entry.cpu_hash != entry.gpu_hash:
                    errors.append(
                        f"Frame {entry.frame_index}: path_used=gpu_verified but "
                        f"cpu_hash={entry.cpu_hash!r} != gpu_hash={entry.gpu_hash!r}"
                    )
            if not entry.verified:
                if entry.path_used == "gpu_verified":
                    errors.append(
                        f"Frame {entry.frame_index}: path_used=gpu_verified but verified=False"
                    )
        return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# Comparison function
# ---------------------------------------------------------------------------

def compare_frame_hashes(
    frame_index: int,
    cpu_bytes: bytes,
    gpu_bytes: Optional[bytes],
    resolution: tuple[int, int],
) -> FrameVerificationResult:
    """
    Compare CPU and GPU frame hashes and return a FrameVerificationResult.

    Parameters
    ----------
    frame_index : Frame index (t).
    cpu_bytes   : Rendered bytes from the CPU reference path.
    gpu_bytes   : Rendered bytes from the GPU path (None if GPU unavailable).
    resolution  : (width, height) tuple.

    Returns
    -------
    FrameVerificationResult with path_used set to one of:
        "cpu_reference"  — no GPU bytes provided
        "gpu_verified"   — GPU hash matches CPU hash
        "gpu_rejected"   — GPU hash differs from CPU hash
    """
    cpu_hash = hashlib.sha256(cpu_bytes).hexdigest()

    if gpu_bytes is None:
        return FrameVerificationResult(
            frame_index=frame_index,
            cpu_hash=cpu_hash,
            gpu_hash=None,
            verified=True,
            path_used="cpu_reference",
            resolution=resolution,
        )

    gpu_hash = hashlib.sha256(gpu_bytes).hexdigest()

    if cpu_hash == gpu_hash:
        return FrameVerificationResult(
            frame_index=frame_index,
            cpu_hash=cpu_hash,
            gpu_hash=gpu_hash,
            verified=True,
            path_used="gpu_verified",
            resolution=resolution,
        )
    else:
        # KENOSIS: GPU output discarded; CPU reference used.
        # verified=False: GPU hash did not match CPU reference hash.
        return FrameVerificationResult(
            frame_index=frame_index,
            cpu_hash=cpu_hash,
            gpu_hash=gpu_hash,
            verified=False,
            path_used="gpu_rejected",
            resolution=resolution,
        )
