#!/usr/bin/env python3
"""
tools/ray_tracing/geometry/bvh_builder.py — Surface Area Heuristic BVH Builder

Builds a Bounding Volume Hierarchy (BVH) using the Surface Area Heuristic
(SAH) for optimal ray-scene acceleration.

Key properties:
  - Construction is deterministic: same scene → same BVH topology.
  - Traversal order is deterministic: same ray → same hit sequence.
  - Pure Python, zero external dependencies.

Mathematical basis:
  SAH cost = C_trav + |S_L|/|S_parent| × N_L × C_isect
                    + |S_R|/|S_parent| × N_R × C_isect

where |S| is surface area of the bounding box and N is primitive count.

LOGOS: BVH construction is a deterministic function of scene geometry.
CHALCEDON: BVH serves the path tracer; it never changes the result.

Author: Orthogonal Engineering
PR: #42
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Union

from .intersect import HitRecord, Plane, Ray, Scene, Sphere, _dot, _normalize

# ---------------------------------------------------------------------------
# Cost constants for the Surface Area Heuristic
# ---------------------------------------------------------------------------

C_TRAV = 1.0    # Cost of traversing a BVH node
C_ISECT = 4.0   # Cost of a primitive intersection test

Vec3 = Tuple[float, float, float]


# ---------------------------------------------------------------------------
# Axis-Aligned Bounding Box (AABB)
# ---------------------------------------------------------------------------

@dataclass
class AABB:
    """Axis-Aligned Bounding Box."""
    min_point: Vec3 = (math.inf, math.inf, math.inf)
    max_point: Vec3 = (-math.inf, -math.inf, -math.inf)

    def surface_area(self) -> float:
        """2*(dx*dy + dy*dz + dx*dz)."""
        dx = self.max_point[0] - self.min_point[0]
        dy = self.max_point[1] - self.min_point[1]
        dz = self.max_point[2] - self.min_point[2]
        return 2.0 * (dx * dy + dy * dz + dx * dz)

    def centroid(self) -> Vec3:
        return (
            (self.min_point[0] + self.max_point[0]) * 0.5,
            (self.min_point[1] + self.max_point[1]) * 0.5,
            (self.min_point[2] + self.max_point[2]) * 0.5,
        )

    def expand(self, other: "AABB") -> "AABB":
        """Return the union of self and other."""
        return AABB(
            min_point=(
                min(self.min_point[0], other.min_point[0]),
                min(self.min_point[1], other.min_point[1]),
                min(self.min_point[2], other.min_point[2]),
            ),
            max_point=(
                max(self.max_point[0], other.max_point[0]),
                max(self.max_point[1], other.max_point[1]),
                max(self.max_point[2], other.max_point[2]),
            ),
        )

    def intersect_ray(self, ray: Ray, t_min: float, t_max: float) -> bool:
        """Slab method AABB-ray test.  Deterministic."""
        for axis in range(3):
            inv_d = 1.0 / (ray.direction[axis] if abs(ray.direction[axis]) > 1e-12 else math.copysign(1e-12, ray.direction[axis]))
            t0 = (self.min_point[axis] - ray.origin[axis]) * inv_d
            t1 = (self.max_point[axis] - ray.origin[axis]) * inv_d
            if inv_d < 0.0:
                t0, t1 = t1, t0
            t_min = max(t_min, t0)
            t_max = min(t_max, t1)
            if t_max <= t_min:
                return False
        return True


def _sphere_aabb(s: Sphere) -> AABB:
    r = s.radius
    return AABB(
        min_point=(s.center[0] - r, s.center[1] - r, s.center[2] - r),
        max_point=(s.center[0] + r, s.center[1] + r, s.center[2] + r),
    )


def _plane_aabb(p: Plane) -> AABB:
    """Planes are infinite; return a large finite box."""
    INF = 1e6
    return AABB(min_point=(-INF, -INF, -INF), max_point=(INF, INF, INF))


# ---------------------------------------------------------------------------
# BVH node
# ---------------------------------------------------------------------------

Primitive = Union[Sphere, Plane]


@dataclass
class BVHNode:
    bounds: AABB
    left: Optional["BVHNode"] = None
    right: Optional["BVHNode"] = None
    primitives: List[Primitive] = field(default_factory=list)

    @property
    def is_leaf(self) -> bool:
        return self.left is None and self.right is None


# ---------------------------------------------------------------------------
# SAH BVH builder
# ---------------------------------------------------------------------------

_N_BUCKETS = 12  # Number of SAH evaluation buckets


@dataclass
class _Bucket:
    count: int = 0
    bounds: AABB = field(default_factory=AABB)


def _primitive_aabb(prim: Primitive) -> AABB:
    if isinstance(prim, Sphere):
        return _sphere_aabb(prim)
    return _plane_aabb(prim)


def _sah_split(
    prims: List[Primitive],
    aabbs: List[AABB],
    parent_bounds: AABB,
    centroid_bounds: AABB,
) -> Tuple[List[Primitive], List[Primitive]]:
    """
    Split ``prims`` into two groups using the Surface Area Heuristic.

    Tries each axis; chooses the split axis and bucket boundary that
    minimises SAH cost.  Falls back to midpoint split if SAH gives no
    improvement over a leaf.
    """
    best_cost = C_ISECT * len(prims)
    best_axis = 0
    best_split = _N_BUCKETS // 2

    parent_sa = parent_bounds.surface_area()
    if parent_sa < 1e-12:
        mid = len(prims) // 2
        return prims[:mid], prims[mid:]

    cx_min = centroid_bounds.min_point
    cx_max = centroid_bounds.max_point
    cx_extent = (
        cx_max[0] - cx_min[0],
        cx_max[1] - cx_min[1],
        cx_max[2] - cx_min[2],
    )

    for axis in range(3):
        if cx_extent[axis] < 1e-12:
            continue

        # Assign each primitive to a bucket
        buckets = [_Bucket() for _ in range(_N_BUCKETS)]
        centroids = [aabb.centroid() for aabb in aabbs]
        for idx, (prim, aabb, centroid) in enumerate(zip(prims, aabbs, centroids)):
            b = int(
                _N_BUCKETS * (centroid[axis] - cx_min[axis]) / cx_extent[axis]
            )
            b = min(b, _N_BUCKETS - 1)
            buckets[b].count += 1
            buckets[b].bounds = buckets[b].bounds.expand(aabb)

        # Evaluate SAH cost for each possible split
        for split in range(1, _N_BUCKETS):
            # Left half [0, split)
            left_b = AABB()
            left_n = 0
            for b in range(split):
                if buckets[b].count > 0:
                    left_b = left_b.expand(buckets[b].bounds)
                    left_n += buckets[b].count

            # Right half [split, N_BUCKETS)
            right_b = AABB()
            right_n = 0
            for b in range(split, _N_BUCKETS):
                if buckets[b].count > 0:
                    right_b = right_b.expand(buckets[b].bounds)
                    right_n += buckets[b].count

            left_sa = left_b.surface_area()
            right_sa = right_b.surface_area()
            cost = (
                C_TRAV
                + (left_sa / parent_sa) * left_n * C_ISECT
                + (right_sa / parent_sa) * right_n * C_ISECT
            )

            if cost < best_cost:
                best_cost = cost
                best_axis = axis
                best_split = split

    # Partition by best split
    centroids = [aabb.centroid() for aabb in aabbs]
    split_val = (
        cx_min[best_axis]
        + best_split * cx_extent[best_axis] / _N_BUCKETS
    )
    left = [p for p, c in zip(prims, centroids) if c[best_axis] < split_val]
    right = [p for p, c in zip(prims, centroids) if c[best_axis] >= split_val]

    if not left or not right:
        mid = len(prims) // 2
        return prims[:mid], prims[mid:]

    return left, right


def build_bvh(primitives: List[Primitive], max_leaf_size: int = 4) -> Optional[BVHNode]:
    """
    Build a BVH using the Surface Area Heuristic.

    Parameters
    ----------
    primitives : List[Primitive]
        Spheres and/or Planes to include.
    max_leaf_size : int
        Maximum number of primitives in a leaf node.

    Returns
    -------
    BVHNode or None
        Root node of the BVH, or None if the primitive list is empty.
    """
    if not primitives:
        return None

    aabbs = [_primitive_aabb(p) for p in primitives]

    # Compute bounds of all primitives
    bounds = aabbs[0]
    for a in aabbs[1:]:
        bounds = bounds.expand(a)

    # Compute centroid bounds
    centroid_bounds = AABB(
        min_point=aabbs[0].centroid(),
        max_point=aabbs[0].centroid(),
    )
    for a in aabbs[1:]:
        c = a.centroid()
        centroid_bounds = centroid_bounds.expand(
            AABB(min_point=c, max_point=c)
        )

    if len(primitives) <= max_leaf_size:
        return BVHNode(bounds=bounds, primitives=list(primitives))

    left_prims, right_prims = _sah_split(primitives, aabbs, bounds, centroid_bounds)
    left_node = build_bvh(left_prims, max_leaf_size)
    right_node = build_bvh(right_prims, max_leaf_size)

    return BVHNode(
        bounds=bounds,
        left=left_node,
        right=right_node,
    )


# ---------------------------------------------------------------------------
# BVH traversal
# ---------------------------------------------------------------------------

def intersect_bvh(
    node: Optional[BVHNode],
    ray: Ray,
    t_min: float = 1e-4,
    t_max: float = 1e9,
) -> Optional[HitRecord]:
    """
    Deterministic BVH traversal.  Same ray always returns the same hit.
    Left child is always traversed before right child (stable ordering).
    """
    if node is None:
        return None

    if not node.bounds.intersect_ray(ray, t_min, t_max):
        return None

    if node.is_leaf:
        closest: Optional[HitRecord] = None
        current_t_max = t_max
        for prim in node.primitives:
            hit = prim.intersect(ray, t_min, current_t_max)
            if hit is not None:
                closest = hit
                current_t_max = hit.t
        return closest

    # Traverse left then right; keep track of closest hit
    left_hit = intersect_bvh(node.left, ray, t_min, t_max)
    new_t_max = left_hit.t if left_hit is not None else t_max
    right_hit = intersect_bvh(node.right, ray, t_min, new_t_max)

    if right_hit is not None:
        return right_hit
    return left_hit


def build_bvh_scene(scene: Scene) -> Optional[BVHNode]:
    """
    Build a BVH from all primitives in ``scene``.

    Planes are included but will not benefit from the BVH (their AABB is
    the whole world).  They are added to the primitive list last so that
    bounded geometry is tested first.
    """
    primitives: List[Primitive] = list(scene.spheres) + list(scene.planes)
    return build_bvh(primitives)
