#!/usr/bin/env python3
"""
tools/ray_tracing/transport/indirect_light.py — Indirect Illumination via QMC

Diffuse and glossy indirect illumination using Sobol' hemisphere sampling.

Sampling strategies:
  - Diffuse:  cosine-weighted hemisphere (Malley's method via Sobol')
  - Glossy:   GGX importance sampling via Sobol' (placeholder — pure diffuse
              fallback for zero-dependency implementation)

LOGOS: hemisphere samples are deterministic — noise-free inter-bounce light.
KENOSIS: stochastic hemisphere sampling self-empties; replaced by Sobol'.

Author: Orthogonal Engineering
PR: #42
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import math
from typing import Tuple

from ..geometry.intersect import HitRecord, Ray, Scene, Vec3, _dot, transform_to_hemisphere
from ..samplers.sobol import advance_sobol_seed, sobol_sequence

# ---------------------------------------------------------------------------
# Indirect illumination
# ---------------------------------------------------------------------------

def indirect_diffuse(
    hit: HitRecord,
    incident_dir: Vec3,
    seed: bytes,
    scene: Scene,
    depth: int,
    *,
    n_samples: int = 4,
    max_depth: int = 8,
) -> float:
    """
    Estimate indirect diffuse illumination via Sobol' cosine-weighted sampling.

    ``n_samples`` Sobol' hemisphere directions are traced; their average is
    returned.  All directions are deterministic functions of ``seed`` and
    ``depth``.

    Parameters
    ----------
    hit : HitRecord
        Surface intersection point.
    incident_dir : Vec3
        Direction of the incident ray (from camera/previous bounce).
    seed : bytes
        Deterministic per-pixel seed.
    scene : Scene
        Scene for recursive tracing.
    depth : int
        Current recursion depth.
    n_samples : int
        Number of indirect hemisphere samples.
    max_depth : int
        Maximum path depth.

    Returns
    -------
    float
        Estimated indirect diffuse radiance.
    """
    if depth >= max_depth:
        return 0.0

    # Derive deterministic per-depth seed
    depth_seed = advance_sobol_seed(seed, depth)

    # Sobol' 2-D samples for hemisphere directions
    sobol_2d = sobol_sequence(2, n_samples, depth_seed[:8])

    total = 0.0
    for i, (u, v) in enumerate(sobol_2d):
        reflect_dir = transform_to_hemisphere(u, v, hit.normal)
        cos_theta = max(0.0, _dot(reflect_dir, hit.normal))
        if cos_theta <= 0.0:
            continue

        # Recurse — import here to avoid circular dependency
        from .path_tracer import trace_path_deterministic
        sample_seed = advance_sobol_seed(depth_seed, i)
        incoming = trace_path_deterministic(
            Ray(hit.point, reflect_dir),
            depth + 1,
            sample_seed,
            scene,
            max_depth=max_depth,
        )
        # Lambertian BRDF × cos / PDF; PDF = cos/π for cosine sampling → π cancels
        total += hit.material.reflectance * incoming

    return total / n_samples if n_samples > 0 else 0.0


def indirect_glossy(
    hit: HitRecord,
    incident_dir: Vec3,
    seed: bytes,
    scene: Scene,
    depth: int,
    *,
    n_samples: int = 4,
    max_depth: int = 8,
) -> float:
    """
    Estimate indirect glossy illumination.

    For materials with roughness < 1.0 this interpolates between a perfect
    mirror reflection and the diffuse estimate.  The interpolation weight is
    (1 - roughness), fully deterministic.

    For roughness == 1.0 this is identical to ``indirect_diffuse``.
    """
    if depth >= max_depth:
        return 0.0

    roughness = hit.material.roughness
    if roughness >= 1.0:
        return indirect_diffuse(
            hit, incident_dir, seed, scene, depth,
            n_samples=n_samples, max_depth=max_depth,
        )

    # Perfect mirror direction
    cos_i = _dot(incident_dir, hit.normal)
    mirror_dir: Vec3 = (
        incident_dir[0] - 2.0 * cos_i * hit.normal[0],
        incident_dir[1] - 2.0 * cos_i * hit.normal[1],
        incident_dir[2] - 2.0 * cos_i * hit.normal[2],
    )

    from .path_tracer import trace_path_deterministic
    mirror_seed = advance_sobol_seed(seed, depth + 1000)
    mirror_radiance = trace_path_deterministic(
        Ray(hit.point, mirror_dir),
        depth + 1,
        mirror_seed,
        scene,
        max_depth=max_depth,
    )

    diffuse_radiance = indirect_diffuse(
        hit, incident_dir, seed, scene, depth,
        n_samples=n_samples, max_depth=max_depth,
    )

    gloss_weight = 1.0 - roughness
    return gloss_weight * mirror_radiance + roughness * diffuse_radiance
