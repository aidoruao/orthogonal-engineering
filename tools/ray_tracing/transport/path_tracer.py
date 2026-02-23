#!/usr/bin/env python3
"""
tools/ray_tracing/transport/path_tracer.py — Deterministic Path Tracer

Pure deterministic recursive light transport.  No Russian roulette.
No random branching.  Seed advancement is a deterministic function of depth.

Rendering equation:
    L(o) = Le(o) + ∫_Ω f_r(i, o) L(i) cos θ_i dω_i

Evaluated via Sobol' quasi-Monte Carlo instead of stochastic sampling:
    L(o) ≈ Le(o) + f_r(i*, o) L(i*) cos θ_i*
    where i* = transform_to_hemisphere(sobol_hemisphere_2d(seed, depth))

Convergence: O((log N)^d / N) vs O(1/√N) for Monte Carlo.

LOGOS: trace_path is a pure function — same inputs always yield same output.
CHALCEDON: CPU path is always authoritative; GPU path optional.
KENOSIS: random sampling self-empties, replaced by deterministic sequences.

Author: Orthogonal Engineering
PR: #42
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import math
from typing import Optional

from ..geometry.intersect import HitRecord, Ray, Scene, Vec3, _dot, transform_to_hemisphere
from ..samplers.sobol import advance_sobol_seed, sobol_hemisphere_2d

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_DEPTH = 8         # Maximum path depth (no Russian roulette)
T_MIN = 1e-4          # Epsilon to avoid self-intersection


# ---------------------------------------------------------------------------
# BRDF — simple Lambertian
# ---------------------------------------------------------------------------

def _lambertian_brdf(
    hit: HitRecord,
    in_dir: Vec3,
    out_dir: Vec3,
) -> float:
    """
    Lambertian BRDF: f_r = reflectance / π.

    Deterministic function of hit material; no random component.
    """
    cos_theta = max(0.0, _dot(out_dir, hit.normal))
    return hit.material.reflectance * cos_theta / math.pi


# ---------------------------------------------------------------------------
# Core path tracer
# ---------------------------------------------------------------------------

def trace_path_deterministic(
    ray: Ray,
    depth: int,
    seed: bytes,
    scene: Scene,
    *,
    max_depth: int = MAX_DEPTH,
) -> float:
    """
    Evaluate the rendering equation at ``ray`` using a single deterministic
    path of length up to ``max_depth``.

    Parameters
    ----------
    ray : Ray
        The ray to trace.
    depth : int
        Current recursion depth (0 = primary ray).
    seed : bytes
        Deterministic per-pixel seed.  Advanced at each depth.
    scene : Scene
        The scene to trace against.
    max_depth : int
        Maximum path length.

    Returns
    -------
    float
        Estimated radiance along the ray.
    """
    if depth > max_depth:
        return 0.0

    hit = scene.intersect(ray)
    if hit is None:
        return scene.environment(ray.direction)

    # Emission — always included
    emission = hit.material.emission

    # Deterministic reflection direction from Sobol' hemisphere
    new_seed = advance_sobol_seed(seed, depth)
    u, v = sobol_hemisphere_2d(new_seed, depth)
    reflect_dir = transform_to_hemisphere(u, v, hit.normal)

    # BRDF × cosine
    brdf_cos = _lambertian_brdf(hit, ray.direction, reflect_dir)

    # Recursive radiance — deterministic
    incoming = trace_path_deterministic(
        Ray(hit.point, reflect_dir),
        depth + 1,
        new_seed,
        scene,
        max_depth=max_depth,
    )

    return emission + brdf_cos * incoming


def render_pixel(
    x: int,
    y: int,
    width: int,
    height: int,
    seed: bytes,
    scene: Scene,
    *,
    n_samples: int = 16,
    fov_radians: float = math.pi / 3,
    max_depth: int = MAX_DEPTH,
) -> float:
    """
    Render a single pixel at (x, y) by averaging ``n_samples`` deterministic
    path traces.

    The sample directions are drawn from a Sobol' sequence; the n-th sample
    is a deterministic function of (x, y, n, seed).

    Returns
    -------
    float
        Radiance estimate for the pixel.
    """
    from ..samplers.sobol import sobol_sequence

    # Derive per-pixel seed from frame seed + pixel coordinates
    pixel_seed = hashlib.sha256(
        seed + x.to_bytes(4, "big") + y.to_bytes(4, "big")
    ).digest()

    aspect = width / height
    tan_half_fov = math.tan(fov_radians / 2.0)

    # 2-D Sobol' samples for sub-pixel jitter
    samples_2d = sobol_sequence(2, n_samples, pixel_seed)

    total = 0.0
    for s in samples_2d:
        jitter_x, jitter_y = s[0], s[1]
        # Map pixel + jitter to normalised device coordinates
        ndc_x = (x + jitter_x) / width * 2.0 - 1.0
        ndc_y = 1.0 - (y + jitter_y) / height * 2.0
        # Camera ray (simple pinhole, looking down -Z)
        ray_dir_x = ndc_x * aspect * tan_half_fov
        ray_dir_y = ndc_y * tan_half_fov
        ray_dir_z = -1.0
        length = math.sqrt(
            ray_dir_x ** 2 + ray_dir_y ** 2 + ray_dir_z ** 2
        )
        ray = Ray(
            origin=(0.0, 0.0, 0.0),
            direction=(
                ray_dir_x / length,
                ray_dir_y / length,
                ray_dir_z / length,
            ),
        )
        # Derive per-sample seed deterministically
        sample_seed = hashlib.sha256(
            pixel_seed + x.to_bytes(4, "big") + y.to_bytes(4, "big")
        ).digest()
        total += trace_path_deterministic(
            ray, depth=0, seed=sample_seed, scene=scene, max_depth=max_depth
        )

    return total / n_samples
