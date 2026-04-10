"""D_ARC_AGI_3 implementation — ARC-AGI Abstract Reasoning Challenge

Layer: 3
CardinalStrength: PREDICATIVE

ARC-AGI tests abstraction and reasoning over symbolic grid transformations.
Chollet (2019): "On the Measure of Intelligence"
"""

from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from enum import Enum
from typing import List, Tuple


class TransformType(Enum):
    """Grid transformation types in ARC-AGI"""
    ROTATION = 1
    REFLECTION = 2
    TRANSLATION = 3
    SCALING = 4
    COLOR_MAP = 5
    PATTERN_FILL = 6


@dataclass
class GridState:
    """2D grid state (H x W)"""
    task_id: str
    height: int
    width: int
    cells: List[List[int]]  # 2D array of integer colors (0-9)


@dataclass
class ARCTask:
    """ARC-AGI task with train/test examples"""
    task_id: str
    train_inputs: List[GridState]
    train_outputs: List[GridState]
    test_inputs: List[GridState]
    test_outputs: List[GridState]


@dataclass
class ARCProgram:
    """Synthesized program for ARC task"""
    program_id: str
    task_id: str
    transform_sequence: List[TransformType]
    max_depth: int
    halts_deterministically: bool


@dataclass
class ARCPrediction:
    """Prediction on test input"""
    prediction_id: str
    task_id: str
    test_index: int
    predicted_grid: GridState
    proof_trace: List[str]


def grids_equal(g1: GridState, g2: GridState) -> bool:
    """Check if two grids are identical"""
    if g1.height != g2.height or g1.width != g2.width:
        return False
    for i in range(g1.height):
        for j in range(g1.width):
            if g1.cells[i][j] != g2.cells[i][j]:
                return False
    return True


def count_colors(grid: GridState) -> int:
    """Count distinct colors in grid"""
    colors = set()
    for row in grid.cells:
        for cell in row:
            colors.add(cell)
    return len(colors)
