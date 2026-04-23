"""D_ARC_AGI implementation — ARC-AGI Excedent

Layer: 3 (Regulatory/Research)
CardinalStrength: PREDICATIVE

ARC-AGI benchmark evaluation, compositional depth, novel rule transfer.
"""

from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple


@dataclass(frozen=True)
class ARCTask:
    """Single ARC-AGI task."""
    task_id: str
    input_grid: Tuple[Tuple[int, ...], ...]
    output_grid: Tuple[Tuple[int, ...], ...]
    rule_description: str
    compositional_depth: int


@dataclass(frozen=True)
class ARCScore:
    """Aggregate ARC-AGI score for a model."""
    model_id: str
    tasks_solved: int
    tasks_total: int
    solve_rate: Fraction
    compositional_max_depth: int
    novel_rule_rate: Fraction
