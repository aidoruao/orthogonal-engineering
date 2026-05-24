#!/usr/bin/env python3
"""
tools/sfi/interpolate.py — Optical Flow Frame Interpolation (Prototype)

Takes two consecutive frames and generates the intermediate frame
using dense optical flow (Farneback algorithm).

This is the CPU reference implementation. The GPU kernel (gpu_kernel.py)
must produce bit-identical output verified by verify.py.

Author: Orthogonal Engineering
Standard: Yeshua
testable_failure_condition: output frame hash differs from expected for given inputs
"""

from __future__ import annotations

import hashlib
from typing import Optional, Tuple

import numpy as np


def compute_optical_flow(
    frame_a: np.ndarray,
    frame_b: np.ndarray,
) -> np.ndarray:
    """
    Compute dense optical flow from frame A to frame B.

    Uses Farneback algorithm for dense motion estimation.

    Args:
        frame_a: Previous frame (H x W x C, uint8)
        frame_b: Current frame (H x W x C, uint8)

    Returns:
        Optical flow field (H x W x 2, float32). flow[y,x] = (dx, dy)
        where dx,dy is the motion vector from A to B at pixel (x,y).

    testable_failure_condition: flow shape != (H, W, 2) for valid inputs
    """
    try:
        import cv2
    except ImportError:
        raise ImportError(
            "OpenCV (cv2) is required for optical flow. "
            "Install with: pip install opencv-python"
        )

    # Convert to grayscale for optical flow computation
    gray_a = cv2.cvtColor(frame_a, cv2.COLOR_BGR2GRAY)
    gray_b = cv2.cvtColor(frame_b, cv2.COLOR_BGR2GRAY)

    # Compute dense optical flow using Farneback algorithm
    flow = cv2.calcOpticalFlowFarneback(
        gray_a, gray_b,
        None,  # flow initialization
        0.5,   # pyramid scale
        3,     # pyramid levels
        15,    # window size
        3,     # iterations
        5,     # poly_n
        1.2,   # poly_sigma
        0,     # flags
    )

    return flow


def warp_frame(
    frame: np.ndarray,
    flow: np.ndarray,
    factor: float = 0.5,
) -> np.ndarray:
    """
    Warp a frame along the optical flow field by a given factor.

    factor=0.0 returns the original frame.
    factor=0.5 returns the frame warped halfway along the flow.
    factor=1.0 returns the frame warped fully to the next frame.

    Args:
        frame: Source frame (H x W x C, uint8)
        flow: Optical flow field (H x W x 2, float32)
        factor: Warp factor in [0.0, 1.0]

    Returns:
        Warped frame (H x W x C, uint8)

    testable_failure_condition: output shape != input shape
    """
    H, W = flow.shape[:2]

    # Create pixel coordinate grid
    y_coords, x_coords = np.mgrid[0:H, 0:W].astype(np.float32)

    # Apply flow scaled by factor
    map_x = x_coords + flow[..., 0] * factor
    map_y = y_coords + flow[..., 1] * factor

    # Remap the frame using bilinear interpolation
    try:
        import cv2
    except ImportError:
        raise ImportError(
            "OpenCV (cv2) is required for frame warping. "
            "Install with: pip install opencv-python"
        )

    warped = cv2.remap(frame, map_x, map_y, cv2.INTER_LINEAR)

    return warped


def interpolate_frame(
    frame_a: np.ndarray,
    frame_b: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate the intermediate frame between frame_a and frame_b.

    Computes bidirectional optical flow and warps both frames
    to the midpoint, then blends them.

    Args:
        frame_a: Previous frame (H x W x C, uint8)
        frame_b: Current frame (H x W x C, uint8)

    Returns:
        Tuple of (interpolated_frame, flow_field)
        - interpolated_frame: Intermediate frame (H x W x C, uint8)
        - flow_field: Forward optical flow from A to B (H x W x 2, float32)

    testable_failure_condition: output frame shape != input frame shape
    testable_failure_condition: output frame is all zeros or all ones
    testable_failure_condition: output is identical to either input frame (no interpolation occurred)
    """
    # Compute forward flow (A → B)
    flow_ab = compute_optical_flow(frame_a, frame_b)

    # Compute backward flow (B → A) for occlusion handling
    flow_ba = compute_optical_flow(frame_b, frame_a)

    # Warp frame A forward by 0.5
    warped_a = warp_frame(frame_a, flow_ab, 0.5)

    # Warp frame B backward by 0.5
    warped_b = warp_frame(frame_b, flow_ba, 0.5)

    # Blend the two warped frames
    # Simple average for prototype; production would use occlusion-aware blending
    interpolated = ((warped_a.astype(np.float32) + warped_b.astype(np.float32)) / 2.0).astype(np.uint8)

    return interpolated, flow_ab


def frame_sha256(frame: np.ndarray) -> str:
    """
    Compute SHA-256 hash of a frame for verification.

    Args:
        frame: Image frame (numpy array)

    Returns:
        Hex-encoded SHA-256 hash string

    testable_failure_condition: hash differs for identical inputs
    """
    return hashlib.sha256(frame.tobytes()).hexdigest()


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Create synthetic test frames
    import cv2

    # Frame A: a white square on black background
    frame_a = np.zeros((256, 256, 3), dtype=np.uint8)
    cv2.rectangle(frame_a, (80, 80), (120, 120), (255, 255, 255), -1)

    # Frame B: the same square moved right by 20 pixels
    frame_b = np.zeros((256, 256, 3), dtype=np.uint8)
    cv2.rectangle(frame_b, (100, 80), (140, 120), (255, 255, 255), -1)

    print("Frame A hash:", frame_sha256(frame_a)[:16])
    print("Frame B hash:", frame_sha256(frame_b)[:16])

    # Interpolate
    mid, flow = interpolate_frame(frame_a, frame_b)

    print("Interpolated hash:", frame_sha256(mid)[:16])
    print("Flow shape:", flow.shape)
    print("Flow min/max:", flow.min(), flow.max())

    # Verification
    assert mid.shape == frame_a.shape, "Output shape mismatch"
    assert not np.array_equal(mid, frame_a), "Output identical to Frame A"
    assert not np.array_equal(mid, frame_b), "Output identical to Frame B"
    assert mid.max() > 0, "Output is all zeros"

    print("\n✅ All checks passed. Interpolation works.")
