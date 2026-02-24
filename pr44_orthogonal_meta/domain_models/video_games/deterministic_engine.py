# pr44_orthogonal_meta/domain_models/video_games/deterministic_engine.py
# PR #44 — Orthogonal Meta Parallel
# Standard: Yeshua
#
# Deterministic physics/render engine over ℕ.
# Replaces proprietary stochastic engines.
# All positions, velocities, and collisions resolved in ℕ².
# No DRM, no microtransactions, no stochastic variance.

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from ...foundations.peano_kernel import Natural, from_int, to_int, eq, zero
from ...foundations.primitive_recursion import add, leq

# A 2D point in ℕ²
Point = Tuple[Natural, Natural]


def move(pos: Point, velocity: Point) -> Point:
    """Deterministic Euler step: new_pos = pos + velocity (component-wise)."""
    return (add(pos[0], velocity[0]), add(pos[1], velocity[1]))


def collides(a: Point, b: Point) -> bool:
    """Axis-aligned collision: True iff positions are structurally equal."""
    return eq(a[0], b[0]) and eq(a[1], b[1])


def simulate_frame(
    entities: List[Dict],
    forces: List[Point],
) -> List[Dict]:
    """
    Advance all entities by one deterministic frame.

    entities: list of {"pos": Point, "vel": Point, "id": int}
    forces:   per-entity force vectors (added to velocity)

    Returns updated entity list. Fully deterministic; no floats.
    """
    updated = []
    for i, entity in enumerate(entities):
        force = forces[i] if i < len(forces) else (zero(), zero())
        new_vel = (add(entity["vel"][0], force[0]), add(entity["vel"][1], force[1]))
        new_pos = move(entity["pos"], new_vel)
        updated.append({"pos": new_pos, "vel": new_vel, "id": entity["id"]})
    return updated


def detect_collisions(entities: List[Dict]) -> List[Tuple[int, int]]:
    """
    Return list of (id_a, id_b) pairs that collide in this frame.
    O(n²) deterministic check. No stochastic broadphase.
    """
    collisions = []
    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            if collides(entities[i]["pos"], entities[j]["pos"]):
                collisions.append((entities[i]["id"], entities[j]["id"]))
    return collisions


COMPARISON = {
    "Proprietary engine (Unreal/Unity)": {
        "physics": "floating-point with numerical drift",
        "randomness": "engine-seeded pseudo-random",
        "verifiability": "closed-source, opaque",
        "lock_in": "vendor license required",
    },
    "PR #44 deterministic engine": {
        "physics": "exact integer arithmetic over ℕ²",
        "randomness": "none",
        "verifiability": "hash-verifiable, open",
        "lock_in": "none",
    },
}
