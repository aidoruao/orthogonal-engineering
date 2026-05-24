#!/usr/bin/env python3
"""
tools/sfi/gpu_kernel.py — GPU-Accelerated Frame Interpolation (Specification)

This module defines the interface and invariants for the CUDA-accelerated
optical flow and frame warping kernels.

The GPU implementation MUST produce bit-identical output to the CPU
reference implementation (interpolate.py). Verification is enforced
by verify.py using the KENOSIS pattern.

CUDA toolkit is NOT required to import this module. The GPU path is
detected at runtime. If CUDA is unavailable, execution falls back
to the CPU path silently.

Author: Orthogonal Engineering
Standard: Yeshua
falsifies_if: GPU output hash differs from CPU reference hash
falsifies_if: GPU path executes when CUDA is unavailable
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))

from tools.sfi.interpolate import interpolate_frame as cpu_interpolate, frame_sha256
from tools.sfi.verify import kenosis_fallback

import numpy as np


# ---------------------------------------------------------------------------
# GPU availability detection (from gpu_accelerated.py pattern)
# ---------------------------------------------------------------------------

def is_cuda_available() -> bool:
    """
    Return True if CUDA toolkit and a CUDA-capable GPU are accessible.

    Detection is purely probing — no GPU is required. This function
    never raises; it returns False on any error.
    """
    try:
        import subprocess
        result = subprocess.run(
            ["nvcc", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


# ---------------------------------------------------------------------------
# GPU Kernel Specification
# ---------------------------------------------------------------------------

def gpu_compute_optical_flow(
    frame_a: np.ndarray,
    frame_b: np.ndarray,
) -> np.ndarray | None:
    """
    GPU-accelerated dense optical flow using CUDA.

    The output MUST be bit-identical to the CPU reference for the
    same inputs.

    Args:
        frame_a: Previous frame (H x W x C, uint8)
        frame_b: Current frame (H x W x C, uint8)

    Returns:
        Optical flow field (H x W x 2, float32), or None if CUDA unavailable.

    falsifies_if: output differs from CPU reference for same inputs
    falsifies_if: returns non-None when CUDA is unavailable
    """
    if not is_cuda_available():
        return None

    # Placeholder: CUDA Farneback implementation goes here
    return None


def gpu_warp_frame(
    frame: np.ndarray,
    flow: np.ndarray,
    factor: float = 0.5,
) -> np.ndarray | None:
    """
    GPU-accelerated frame warping using CUDA.

    Args:
        frame: Source frame (H x W x C, uint8)
        flow: Optical flow field (H x W x 2, float32)
        factor: Warp factor in [0.0, 1.0]

    Returns:
        Warped frame (H x W x C, uint8), or None if CUDA unavailable.

    falsifies_if: output differs from CPU reference for same inputs
    """
    if not is_cuda_available():
        return None

    # Placeholder: CUDA remap implementation goes here
    return None


def gpu_interpolate_frame(
    frame_a: np.ndarray,
    frame_b: np.ndarray,
) -> tuple[np.ndarray | None, np.ndarray | None]:
    """
    GPU-accelerated frame interpolation.

    Computes bidirectional optical flow and generates the intermediate
    frame entirely on GPU. Falls back to CPU if CUDA unavailable.

    Args:
        frame_a: Previous frame (H x W x C, uint8)
        frame_b: Current frame (H x W x C, uint8)

    Returns:
        Tuple of (interpolated_frame, flow_field) or (None, None) if
        CUDA unavailable.

    falsifies_if: GPU output hash differs from CPU reference hash
    """
    if not is_cuda_available():
        return None, None

    flow_ab = gpu_compute_optical_flow(frame_a, frame_b)
    flow_ba = gpu_compute_optical_flow(frame_b, frame_a)

    if flow_ab is None or flow_ba is None:
        return None, None

    warped_a = gpu_warp_frame(frame_a, flow_ab, 0.5)
    warped_b = gpu_warp_frame(frame_b, flow_ba, 0.5)

    if warped_a is None or warped_b is None:
        return None, None

    interpolated = ((warped_a.astype(np.float32) + warped_b.astype(np.float32)) / 2.0).astype(np.uint8)

    return interpolated, flow_ab


# ---------------------------------------------------------------------------
# KENOSIS Pipeline
# ---------------------------------------------------------------------------

def sovereign_interpolate(
    frame_a: np.ndarray,
    frame_b: np.ndarray,
) -> np.ndarray:
    """
    Sovereign frame interpolation with automatic GPU/CPU fallback.

    Attempts GPU path first. If GPU unavailable or output doesn't
    match CPU reference, falls back to CPU path silently (KENOSIS).

    This is the single entry point for external code.

    Args:
        frame_a: Previous frame
        frame_b: Current frame

    Returns:
        Interpolated frame (or frame_a if interpolation fails entirely)

    falsifies_if: returns frame identical to frame_a or frame_b
    """
    # Try GPU path
    gpu_frame, _ = gpu_interpolate_frame(frame_a, frame_b)

    if gpu_frame is not None:
        # Verify GPU output against CPU reference
        cpu_frame, _ = cpu_interpolate(frame_a, frame_b)

        gpu_hash = frame_sha256(gpu_frame)
        cpu_hash = frame_sha256(cpu_frame)

        if gpu_hash == cpu_hash:
            return gpu_frame
        else:
            return cpu_frame

    # GPU unavailable — use CPU path directly
    cpu_frame, _ = cpu_interpolate(frame_a, frame_b)
    return cpu_frame


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import cv2

    frame_a = np.zeros((256, 256, 3), dtype=np.uint8)
    cv2.rectangle(frame_a, (80, 80), (120, 120), (255, 255, 255), -1)

    frame_b = np.zeros((256, 256, 3), dtype=np.uint8)
    cv2.rectangle(frame_b, (100, 80), (140, 120), (255, 255, 255), -1)

    print(f"CUDA available: {is_cuda_available()}")

    result = sovereign_interpolate(frame_a, frame_b)
    print(f"Output shape: {result.shape}")
    print(f"Output hash: {frame_sha256(result)[:16]}")

    result2 = sovereign_interpolate(frame_a, frame_b)
    assert np.array_equal(result, result2), "Determinism check failed"

    print("\n✅ GPU kernel specification complete. CPU fallback verified.")
