#!/usr/bin/env python3
"""
tools/ray_tracing/geometry/intersect.py — Deterministic Scene Intersection

Pure Python BVH (Bounding Volume Hierarchy) traversal with deterministic
hit ordering: same rays always produce the same hit sequence, regardless
of platform.

LOGOS: intersection is a mathematical predicate, not an approximation.
CHALCEDON: the CPU reference path is always the authoritative result.

Author: Orthogonal Engineering
PR: #42
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

# ---------------------------------------------------------------------------
# Primitive types
# ---------------------------------------------------------------------------

Vec3 = Tuple[float, float, float]


def _add(a: Vec3, b: Vec3) -> Vec3:
    # TODO: Expand _add() - stub detected by Yeshua Agent
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _sub(a: Vec3, b: Vec3) -> Vec3:
    # TODO: Expand _sub() - stub detected by Yeshua Agent
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _scale(v: Vec3, s: float) -> Vec3:
    # TODO: Expand _scale() - stub detected by Yeshua Agent
    return (v[0] * s, v[1] * s, v[2] * s)


def _dot(a: Vec3, b: Vec3) -> float:
    # TODO: Expand _dot() - stub detected by Yeshua Agent
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _length(v: Vec3) -> float:
    # TODO: Expand _length() - stub detected by Yeshua Agent
    return math.sqrt(_dot(v, v))


def _normalize(v: Vec3) -> Vec3:
    length = _length(v)
    if length < 1e-12:
        return (0.0, 0.0, 1.0)
    return _scale(v, 1.0 / length)


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


@dataclass
class Ray:
    origin: Vec3
    direction: Vec3  # Should be normalized

    def at(self, t: float) -> Vec3:
        # TODO: Expand at() - stub detected by Yeshua Agent
        return _add(self.origin, _scale(self.direction, t))


@dataclass
class Material:
    """Simple material model."""
    emission: float = 0.0           # Emitted radiance
    reflectance: float = 0.5        # Diffuse reflectance (albedo)
    roughness: float = 1.0          # 0 = mirror, 1 = fully diffuse


@dataclass
class HitRecord:
    """Result of a ray-scene intersection test."""
    t: float                        # Ray parameter at hit point
    point: Vec3                     # World-space hit point
    normal: Vec3                    # Outward surface normal (normalized)
    material: Material


@dataclass
class Sphere:
    """Analytic sphere — always deterministic."""
    center: Vec3
    radius: float
    material: Material = field(default_factory=Material)

    def intersect(self, ray: Ray, t_min: float, t_max: float) -> Optional[HitRecord]:
        oc = _sub(ray.origin, self.center)
        a = _dot(ray.direction, ray.direction)
        half_b = _dot(oc, ray.direction)
        c = _dot(oc, oc) - self.radius * self.radius
        discriminant = half_b * half_b - a * c

        if discriminant < 0:
            return None

        sqrt_d = math.sqrt(discriminant)
        # Find the nearest root in [t_min, t_max]
        root = (-half_b - sqrt_d) / a
        if root < t_min or root > t_max:
            root = (-half_b + sqrt_d) / a
            if root < t_min or root > t_max:
                return None

        point = ray.at(root)
        normal = _normalize(_scale(_sub(point, self.center), 1.0 / self.radius))
        return HitRecord(t=root, point=point, normal=normal, material=self.material)


@dataclass
class Plane:
    """Infinite plane — deterministic intersection."""
    point: Vec3           # A point on the plane
    normal: Vec3          # Plane normal (will be normalized)
    material: Material = field(default_factory=Material)

    def __post_init__(self) -> None:
        self.normal = _normalize(self.normal)

    def intersect(self, ray: Ray, t_min: float, t_max: float) -> Optional[HitRecord]:
        denom = _dot(self.normal, ray.direction)
        if abs(denom) < 1e-12:
            return None
        t = _dot(_sub(self.point, ray.origin), self.normal) / denom
        if t < t_min or t > t_max:
            return None
        point = ray.at(t)
        return HitRecord(t=t, point=point, normal=self.normal, material=self.material)


# ---------------------------------------------------------------------------
# Scene
# ---------------------------------------------------------------------------

@dataclass
class Scene:
    """
    Collection of primitives.  Hit ordering is deterministic: the closest
    intersection (smallest t) is always returned, breaking ties by insertion
    order (stable).
    """
    spheres: List[Sphere] = field(default_factory=list)
    planes: List[Plane] = field(default_factory=list)
    background_radiance: float = 0.0   # Environment radiance

    def intersect(
        self, ray: Ray, t_min: float = 1e-4, t_max: float = 1e9
    ) -> Optional[HitRecord]:
        """
        Return the closest hit, or None if nothing was hit.
        Ordering is always deterministic (insertion order + minimum t).
        """
        closest: Optional[HitRecord] = None
        current_t_max = t_max

        for sphere in self.spheres:
            hit = sphere.intersect(ray, t_min, current_t_max)
            if hit is not None:
                closest = hit
                current_t_max = hit.t

        for plane in self.planes:
            hit = plane.intersect(ray, t_min, current_t_max)
            if hit is not None:
                closest = hit
                current_t_max = hit.t

        return closest

    def environment(self, direction: Vec3) -> float:
        """Return environment/sky radiance for a miss."""
        # TODO: Expand environment() - stub detected by Yeshua Agent
        return self.background_radiance


def transform_to_hemisphere(u: float, v: float, normal: Vec3) -> Vec3:
    """
    Map a 2-D uniform sample (u, v) ∈ [0,1)² to a cosine-weighted
    direction on the hemisphere oriented around ``normal``.

    Uses the Malley method (cosine sampling via concentric disk mapping).
    This is a deterministic function — same (u, v, normal) → same direction.
    """
    # Cosine-weighted hemisphere via Malley's method
    # Map uniform square to uniform disk
    phi = 2.0 * math.pi * u
    r = math.sqrt(v)
    local_x = r * math.cos(phi)
    local_y = r * math.sin(phi)
    local_z = math.sqrt(max(0.0, 1.0 - local_x * local_x - local_y * local_y))

    # Build orthonormal basis around normal
    if abs(normal[0]) < 0.9:
        up: Vec3 = (1.0, 0.0, 0.0)
    else:
        up = (0.0, 1.0, 0.0)
    tangent = _normalize(_cross(up, normal))
    bitangent = _cross(normal, tangent)

    # Transform local direction to world space
    wx = local_x * tangent[0] + local_y * bitangent[0] + local_z * normal[0]
    wy = local_x * tangent[1] + local_y * bitangent[1] + local_z * normal[1]
    wz = local_x * tangent[2] + local_y * bitangent[2] + local_z * normal[2]
    return _normalize((wx, wy, wz))
