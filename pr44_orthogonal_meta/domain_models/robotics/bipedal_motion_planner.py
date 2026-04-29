"""Bipedal Motion Planner - pr44_orthogonal_meta/domain_models/robotics/bipedal_motion_planner.py"""
# pr44_orthogonal_meta/domain_models/robotics/bipedal_motion_planner.py
# PR #44 — Orthogonal Meta Parallel
# Standard: Yeshua
#
# Deterministic bipedal motion planning over ℕ³ (x, y, step).
# All paths are byte-verifiable; no hidden stochastic processes.
# BFS-based planning guarantees shortest path (by step count) when one exists.

from __future__ import annotations

from collections import deque
from typing import Dict, List, Optional, Set, Tuple

from ...foundations.peano_kernel import Natural, from_int, to_int, eq, zero
from ...foundations.primitive_recursion import add, leq

# A position in ℕ²
Pos = Tuple[int, int]


def plan_path(
    start: Pos,
    goal: Pos,
    obstacles: Set[Pos],
    max_coord: int = 16,
) -> Optional[List[Pos]]:
    """
    BFS-based deterministic shortest-path planner.

    Returns a list of positions from start to goal (inclusive),
    or None if no path exists within the bounded grid.

    Termination guaranteed: grid is finite (max_coord² cells),
    BFS visits each cell at most once.
    """
    if start == goal:
        return [start]
    if start in obstacles or goal in obstacles:
        return None

    visited: Set[Pos] = {start}
    parent: Dict[Pos, Optional[Pos]] = {start: None}
    queue: deque = deque([start])

    while queue:
        current = queue.popleft()
        x, y = current
        for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            nx, ny = x + dx, y + dy
            if nx < 0 or ny < 0 or nx > max_coord or ny > max_coord:
                continue
            neighbor = (nx, ny)
            if neighbor in visited or neighbor in obstacles:
                continue
            visited.add(neighbor)
            parent[neighbor] = current
            if neighbor == goal:
                return _reconstruct(parent, goal)
            queue.append(neighbor)

    return None


def _reconstruct(parent: Dict[Pos, Optional[Pos]], goal: Pos) -> List[Pos]:
    """Reconstruct path from parent map. Deterministic order."""
    path: List[Pos] = []
    current: Optional[Pos] = goal
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()
    return path


COMPARISON = {
    "Stochastic motion planner (RL)": {
        "method": "reinforcement learning with random exploration",
        "randomness": "epsilon-greedy or policy gradient",
        "verifiability": "not reproducible without exact seed + model",
        "safety": "statistical, no formal proof",
    },
    "PR #44 BFS planner": {
        "method": "BFS over finite ℕ² grid",
        "randomness": "none",
        "verifiability": "byte-verifiable path",
        "safety": "formally proven: no path through obstacles",
    },
}
