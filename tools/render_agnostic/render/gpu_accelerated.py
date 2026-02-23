#!/usr/bin/env python3
"""
tools/render_agnostic/render/gpu_accelerated.py — PR #41 Optional GPU Path

This module provides an optional GPU-accelerated render path.  The GPU path
is NOT authoritative: its output must match the CPU reference frame hash
(computed by cpu_reference.py) before being accepted for display.

KENOSIS principle: the GPU path self-empties on hash mismatch.  If the GPU
output hash differs from the CPU reference hash, or if no GPU is present,
this module falls back to the CPU path silently.

CHALCEDON principle: the GPU serves the mathematics, not vice versa.
GPU is optional acceleration, not required dependency.

Author: Orthogonal Engineering
PR: #41
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
from typing import Optional

from tools.render_agnostic.render.cpu_reference import (
    RGBPixel,
    frame_sha256,
    render_frame as cpu_render_frame,
)

# ---------------------------------------------------------------------------
# GPU availability detection
# ---------------------------------------------------------------------------


def is_gpu_available() -> bool:
    """
    Return True if any GPU compute backend is available (CUDA or OpenCL).

    Detection is purely probing — no GPU is required.  This function never
    raises; it returns False on any error.
    """
    return _probe_cuda() or _probe_opencl()


def _probe_cuda() -> bool:
    """Return True if a CUDA-capable device is accessible."""
    try:
        import importlib
        cupy = importlib.import_module("cupy")
        return int(cupy.cuda.runtime.getDeviceCount()) > 0
    except Exception:
        return False


def _probe_opencl() -> bool:
    """Return True if any OpenCL platform is accessible."""
    try:
        import importlib
        pyopencl = importlib.import_module("pyopencl")
        platforms = pyopencl.get_platforms()
        return len(platforms) > 0
    except Exception:
        return False


# ---------------------------------------------------------------------------
# GPU render stub (extensible)
# ---------------------------------------------------------------------------


def _gpu_render_frame(
    seed: bytes,
    style: dict,
    width: int,
    height: int,
    t: int = 0,
) -> Optional[bytes]:
    """
    Attempt to render a frame using GPU acceleration.

    Returns the rendered bytes on success, or None if GPU render fails.
    The caller is responsible for comparing the returned bytes against the
    CPU reference output via the hash comparator.

    This implementation is a stub.  Concrete GPU backends (CUDA, OpenCL,
    Metal) plug in here.  The interface contract is:

        Input:  seed (32 bytes), style dict, width, height, t (frame index)
        Output: bytes of length width * height * 3  (r, g, b uint8 per pixel)
                OR None on any failure

    The stub delegates to the CPU path as a placeholder.  A real GPU backend
    replaces the inner body while keeping the same contract.
    """
    try:
        if not is_gpu_available():
            return None
        # Placeholder: real GPU kernel would be dispatched here.
        # For now, return None to signal "no GPU backend installed".
        return None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Dual-path render function
# ---------------------------------------------------------------------------


def render_frame_dual_path(
    seed: bytes,
    style: dict,
    width: int,
    height: int,
    t: int = 0,
) -> tuple[bytes, str]:
    """
    Render a frame using dual-path execution (CPU + optional GPU).

    Protocol
    --------
    1. Always render via CPU reference path (authoritative).
    2. If GPU is available, render via GPU path.
    3. Compare SHA-256 hashes of both outputs.
    4. If hashes match: return GPU bytes (faster) with path="gpu_verified".
    5. If hashes differ OR no GPU: return CPU bytes with path="cpu_reference".

    Parameters
    ----------
    seed, style, width, height, t : render parameters (same as cpu_reference.render_frame)

    Returns
    -------
    (frame_bytes, path_used) where path_used is one of:
        "cpu_reference"   — CPU path used (GPU absent or rejected)
        "gpu_verified"    — GPU path used and verified against CPU
        "gpu_rejected"    — GPU path produced different hash; CPU used
    """
    # Step 1: CPU reference (always)
    cpu_bytes = cpu_render_frame(seed, style, width, height, t)
    cpu_hash = frame_sha256(cpu_bytes)

    # Step 2: Try GPU path
    gpu_bytes = _gpu_render_frame(seed, style, width, height, t)

    if gpu_bytes is None:
        return cpu_bytes, "cpu_reference"

    # Step 3: Compare hashes
    gpu_hash = frame_sha256(gpu_bytes)
    if cpu_hash == gpu_hash:
        return gpu_bytes, "gpu_verified"
    else:
        # KENOSIS: GPU self-empties; CPU reference displayed silently
        return cpu_bytes, "gpu_rejected"
