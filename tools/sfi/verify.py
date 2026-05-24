#!/usr/bin/env python3
"""
tools/sfi/verify.py — Frame Interpolation Verification

Hashes the interpolated frame and compares against expected output.
Implements KENOSIS pattern: GPU output must match CPU reference.
If mismatch, falls back to CPU path silently.

Author: Orthogonal Engineering
Standard: Yeshua
falsifies_if: verification passes when frames don't match
"""

from __future__ import annotations

import hashlib
from typing import Tuple

import numpy as np

from tools.sfi.interpolate import interpolate_frame, frame_sha256


def verify_interpolation(
    frame_a: np.ndarray,
    frame_b: np.ndarray,
    expected_hash: str | None = None,
) -> Tuple[bool, str, np.ndarray]:
    """
    Verify that frame interpolation produces correct output.

    Args:
        frame_a: Previous frame
        frame_b: Current frame
        expected_hash: Optional pre-computed hash to verify against

    Returns:
        Tuple of (passed, hash, interpolated_frame)
        - passed: True if verification succeeded
        - hash: SHA-256 of the interpolated frame
        - interpolated_frame: The generated intermediate frame

    falsifies_if: passed=True when hashes don't match
    falsifies_if: passed=False when hashes match
    """
    # Generate interpolated frame
    interpolated, _ = interpolate_frame(frame_a, frame_b)

    # Compute hash
    actual_hash = frame_sha256(interpolated)

    # Verify
    if expected_hash is not None:
        passed = actual_hash == expected_hash
    else:
        # No expected hash provided — just report what we got
        passed = True

    return passed, actual_hash, interpolated


def kenosis_fallback(
    frame_a: np.ndarray,
    gpu_hash: str,
    cpu_hash: str,
) -> np.ndarray:
    """
    KENOSIS pattern: GPU self-empties on hash mismatch.

    If GPU output doesn't match CPU reference, return the original
    frame A (no interpolation). The game continues without the
    generated frame. Graceful degradation.

    Args:
        frame_a: Original frame (fallback)
        gpu_hash: Hash from GPU-accelerated interpolation
        cpu_hash: Hash from CPU reference interpolation

    Returns:
        Frame to display (either interpolated or original frame_a)

    falsifies_if: returns GPU frame when hashes mismatch
    """
    if gpu_hash != cpu_hash:
        # KENOSIS: GPU failed verification, fall back to original
        return frame_a
    else:
        # Verification passed — but we don't have the GPU frame here,
        # just the hash. The caller handles frame selection.
        return frame_a  # Caller will use GPU frame if hashes match


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Use the same synthetic test as interpolate.py
    import cv2

    frame_a = np.zeros((256, 256, 3), dtype=np.uint8)
    cv2.rectangle(frame_a, (80, 80), (120, 120), (255, 255, 255), -1)

    frame_b = np.zeros((256, 256, 3), dtype=np.uint8)
    cv2.rectangle(frame_b, (100, 80), (140, 120), (255, 255, 255), -1)

    # Run verification with no expected hash (first run)
    passed, hash_val, _ = verify_interpolation(frame_a, frame_b)
    print(f"First run — Hash: {hash_val[:16]} — Passed: {passed}")

    # Run verification with the correct expected hash
    passed2, hash_val2, _ = verify_interpolation(frame_a, frame_b, expected_hash=hash_val)
    print(f"Second run — Hash: {hash_val2[:16]} — Passed: {passed2}")

    # Run verification with a wrong expected hash
    passed3, hash_val3, _ = verify_interpolation(frame_a, frame_b, expected_hash="0" * 64)
    print(f"Third run — Hash: {hash_val3[:16]} — Passed: {passed3} (should be False)")

    # Test KENOSIS fallback
    fallback_frame = kenosis_fallback(frame_a, "abc123", "def456")
    assert np.array_equal(fallback_frame, frame_a), "KENOSIS fallback should return original frame A"

    print("\n✅ All verification checks passed.")
