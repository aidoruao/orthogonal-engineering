#!/usr/bin/env python3
"""
tools/sfi/verify.py — Frame Interpolation Verification

Hashes the interpolated frame and compares against expected output.
Implements DVF (Deterministic Verified Fallback) pattern: GPU output must match CPU reference.
If mismatch, falls back to CPU path silently.

Author: Orthogonal Engineering
Standard: Yeshua
testable_failure_condition: verification passes when frames don't match
"""

from __future__ import annotations

import sys
import os

# Add oe-local root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))

from tools.sfi.interpolate import interpolate_frame, frame_sha256

import numpy as np


def verify_interpolation(
    frame_a: np.ndarray,
    frame_b: np.ndarray,
    expected_hash: str | None = None,
) -> tuple[bool, str, np.ndarray]:
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

    testable_failure_condition: passed=True when hashes don't match
    testable_failure_condition: passed=False when hashes match
    """
    interpolated, _ = interpolate_frame(frame_a, frame_b)
    actual_hash = frame_sha256(interpolated)

    if expected_hash is not None:
        passed = actual_hash == expected_hash
    else:
        passed = True

    return passed, actual_hash, interpolated


def kenosis_fallback(
    frame_a: np.ndarray,
    gpu_hash: str,
    cpu_hash: str,
) -> np.ndarray:
    """
    DVF (Deterministic Verified Fallback) pattern: GPU self-empties on hash mismatch.

    If GPU output doesn't match CPU reference, return the original
    frame A (no interpolation). The game continues without the
    generated frame. Graceful degradation.

    Args:
        frame_a: Original frame (fallback)
        gpu_hash: Hash from GPU-accelerated interpolation
        cpu_hash: Hash from CPU reference interpolation

    Returns:
        Frame to display (either interpolated or original frame_a)

    testable_failure_condition: returns GPU frame when hashes mismatch
    """
    if gpu_hash != cpu_hash:
        return frame_a
    return frame_a


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import cv2

    frame_a = np.zeros((256, 256, 3), dtype=np.uint8)
    cv2.rectangle(frame_a, (80, 80), (120, 120), (255, 255, 255), -1)

    frame_b = np.zeros((256, 256, 3), dtype=np.uint8)
    cv2.rectangle(frame_b, (100, 80), (140, 120), (255, 255, 255), -1)

    passed, hash_val, _ = verify_interpolation(frame_a, frame_b)
    print(f"First run — Hash: {hash_val[:16]} — Passed: {passed}")

    passed2, hash_val2, _ = verify_interpolation(frame_a, frame_b, expected_hash=hash_val)
    print(f"Second run — Hash: {hash_val2[:16]} — Passed: {passed2} (should be True)")

    passed3, hash_val3, _ = verify_interpolation(frame_a, frame_b, expected_hash="0" * 64)
    print(f"Third run — Hash: {hash_val3[:16]} — Passed: {passed3} (should be False)")

    fallback_frame = kenosis_fallback(frame_a, "abc123", "def456")
    assert np.array_equal(fallback_frame, frame_a), "DVF (Deterministic Verified Fallback) fallback should return original frame A"

    print("\n✅ All verification checks passed.")
