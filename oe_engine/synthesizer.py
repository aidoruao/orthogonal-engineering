"""oe_engine/synthesizer.py — ARC-AGI program synthesizer.

Bounded-depth BFS program synthesis over TransformType compositions.
No LLM, no randomness. Deterministic: ARCTask → Optional[ARCProgram].

Synthesis procedure:
    1. BFS over TransformType sequences, depth 1 .. MAX_SYNTHESIS_DEPTH
    2. For each candidate sequence apply composed transforms to all train inputs
    3. Return first sequence where every predicted output matches the train output
    4. Wrap result in ARCProgram + ProofObject with full trace

The six canonical transforms operate on GridState without external parameters:

    ROTATION     — rotate 90° clockwise  (changes H/W)
    REFLECTION   — horizontal mirror     (preserves H/W)
    TRANSLATION  — cycle columns right   (preserves H/W)
    SCALING      — transpose grid        (swaps H/W)
    COLOR_MAP    — invert colors 9-c     (preserves H/W)
    PATTERN_FILL — shift colors +1 mod 10 (preserves H/W)

Standard: Chollet (2019) "On the Measure of Intelligence", Sec 3.1.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, Iterator, List, Optional, Tuple

from axioms.logic import ProofObject
from src.domains.d_arc_agi_3.implementation import (
    ARCProgram,
    ARCTask,
    GridState,
    TransformType,
    grids_equal,
)

__all__ = [
    "ARCSynthesizer",
    "SynthesisResult",
    "check_synthesis_result_integrity",
    "MAX_SYNTHESIS_DEPTH",
    "MAX_ITERATIONS",
]

# Practical bounds — keep BFS tractable in O(6^6) = 46 656 max candidates
MAX_SYNTHESIS_DEPTH: int = 6
MAX_ITERATIONS: int = 10_000

_ALL_TRANSFORMS: List[TransformType] = list(TransformType)


# ---------------------------------------------------------------------------
# Grid transform primitives (integer arithmetic only — no float, no Fraction)
# ---------------------------------------------------------------------------


def _rotate_cw(grid: GridState) -> GridState:
    """Rotate grid 90° clockwise.

    New dimensions: height=old.width, width=old.height.
    new[j][H-1-i] = old[i][j]  for all i in [0,H), j in [0,W).

    Falsifies if: output.height != input.width or output.width != input.height.
    falsifies_if: output.height != input.width or output.width != input.height.
    """
    h, w = grid.height, grid.width
    cells = [[grid.cells[h - 1 - j][i] for j in range(h)] for i in range(w)]
    return GridState(task_id=grid.task_id, height=w, width=h, cells=cells)


def _reflect_h(grid: GridState) -> GridState:
    """Flip grid horizontally (mirror left-right).

    new[i][j] = old[i][W-1-j]  for all i, j.

    Falsifies if: output[i][j] != input[i][W-1-j] for any i, j.
    falsifies_if: output[i][j] != input[i][W-1-j] for any i, j.
    """
    cells = [list(reversed(row)) for row in grid.cells]
    return GridState(task_id=grid.task_id, height=grid.height, width=grid.width, cells=cells)


def _translate_r(grid: GridState) -> GridState:
    """Cycle all columns right by one position (last column wraps to first).

    new[i][j] = old[i][(j - 1) % W]  for all i, j.

    Falsifies if: output[i][0] != input[i][W-1] for any i.
    falsifies_if: output[i][0] != input[i][W-1] for any i.
    """
    cells = [row[-1:] + row[:-1] for row in grid.cells]
    return GridState(task_id=grid.task_id, height=grid.height, width=grid.width, cells=cells)


def _transpose(grid: GridState) -> GridState:
    """Transpose grid — swap rows and columns.

    New dimensions: height=old.width, width=old.height.
    new[j][i] = old[i][j]  for all i in [0,H), j in [0,W).

    Falsifies if: output[j][i] != input[i][j] for any i, j.
    falsifies_if: output[j][i] != input[i][j] for any i, j.
    """
    h, w = grid.height, grid.width
    cells = [[grid.cells[i][j] for i in range(h)] for j in range(w)]
    return GridState(task_id=grid.task_id, height=w, width=h, cells=cells)


def _invert_colors(grid: GridState) -> GridState:
    """Invert ARC color values: new_color = 9 - old_color (range 0-9).

    Falsifies if: any output cell != 9 - input cell.
    falsifies_if: any output cell != 9 - input cell.
    """
    cells = [[9 - c for c in row] for row in grid.cells]
    return GridState(task_id=grid.task_id, height=grid.height, width=grid.width, cells=cells)


def _shift_colors(grid: GridState) -> GridState:
    """Shift all color values +1 mod 10.

    Falsifies if: any output cell != (input cell + 1) % 10.
    falsifies_if: any output cell != (input cell + 1) % 10.
    """
    cells = [[(c + 1) % 10 for c in row] for row in grid.cells]
    return GridState(task_id=grid.task_id, height=grid.height, width=grid.width, cells=cells)


_TRANSFORM_FN = {
    TransformType.ROTATION: _rotate_cw,
    TransformType.REFLECTION: _reflect_h,
    TransformType.TRANSLATION: _translate_r,
    TransformType.SCALING: _transpose,
    TransformType.COLOR_MAP: _invert_colors,
    TransformType.PATTERN_FILL: _shift_colors,
}


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SynthesisResult:
    """Outcome of one ARC synthesis run.

    Invariant: success=True iff program is not None and
    program.transform_sequence is non-empty.

    Falsifies if: success=True and program is None, or
    success=False and program is not None.
    falsifies_if: success=True and program is None, or
    success=False and program is not None.
    """

    task_id: str
    success: bool
    program: Optional[ARCProgram]
    proof: ProofObject
    iterations: int        # number of candidate sequences evaluated
    depth_reached: int     # deepest sequence length evaluated


# ---------------------------------------------------------------------------
# Synthesizer
# ---------------------------------------------------------------------------


class ARCSynthesizer:
    """Bounded-depth BFS program synthesizer for ARC-AGI tasks.

    Searches the Cartesian product of TransformType^depth for depth 1..max_depth,
    evaluating at most max_iterations candidates. Returns the shortest transform
    sequence that maps every training input to its expected output.

    Determinism guarantee: same task → same program (or same failure), because
    BFS order over itertools.product is lexicographic and reproducible.

    Falsifies if: synthesize() returns success=True but any train pair is not
    correctly solved by the returned program's transform_sequence.
    falsifies_if: synthesize() returns success=True but applying the returned
    transform_sequence to any train input does not equal the train output.
    """

    def __init__(
        self,
        max_depth: int = MAX_SYNTHESIS_DEPTH,
        max_iterations: int = MAX_ITERATIONS,
    ) -> None:
        """Initialise synthesizer with search bounds.

        Falsifies if: max_depth <= 0 or max_iterations <= 0.
        falsifies_if: max_depth <= 0 or max_iterations <= 0.
        """
        if max_depth <= 0:
            raise ValueError(f"max_depth must be > 0, got {max_depth}")
        if max_iterations <= 0:
            raise ValueError(f"max_iterations must be > 0, got {max_iterations}")
        self._max_depth = max_depth
        self._max_iterations = max_iterations

    # ------------------------------------------------------------------
    # Public transform helpers (also used by tests)
    # ------------------------------------------------------------------

    def apply_transform(self, grid: GridState, transform: TransformType) -> GridState:
        """Apply a single canonical transform to a grid.

        Falsifies if: transform is not in TransformType or grid is not a GridState.
        falsifies_if: transform is not in TransformType or grid is not a GridState.
        """
        return _TRANSFORM_FN[transform](grid)

    def apply_sequence(self, grid: GridState, sequence: List[TransformType]) -> GridState:
        """Apply a sequence of transforms left-to-right.

        Empty sequence returns the grid unchanged.

        Falsifies if: empty sequence returns a different grid.
        falsifies_if: empty sequence returns a different grid.
        """
        result = grid
        for t in sequence:
            result = _TRANSFORM_FN[t](result)
        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _matches_all_train(self, task: ARCTask, sequence: List[TransformType]) -> bool:
        """Return True iff applying sequence to every train input equals the train output."""
        for inp, out in zip(task.train_inputs, task.train_outputs):
            if not grids_equal(self.apply_sequence(inp, sequence), out):
                return False
        return True

    def _bfs_sequences(self) -> Iterator[List[TransformType]]:
        """Yield transform sequences in BFS order: depth 1, 2, …, max_depth."""
        for depth in range(1, self._max_depth + 1):
            for seq in itertools.product(_ALL_TRANSFORMS, repeat=depth):
                yield list(seq)

    # ------------------------------------------------------------------
    # Main synthesis entry point
    # ------------------------------------------------------------------

    def synthesize(self, task: ARCTask) -> SynthesisResult:
        """Find the shortest transform sequence solving the task.

        Runs BFS, returning the first sequence that maps all training inputs
        to their expected outputs. If no solution is found within the budget,
        returns success=False.

        Standard: Chollet (2019) "On the Measure of Intelligence", Sec 3.1.

        Falsifies if: returned success=True but any train pair is unsolved.
        falsifies_if: returned success=True but applying the transform sequence
        to any train input does not produce the corresponding train output.
        """
        if not task.train_inputs or not task.train_outputs:
            return SynthesisResult(
                task_id=task.task_id,
                success=False,
                program=None,
                proof=ProofObject(
                    rule="arc_synthesizer",
                    premises=[f"task={task.task_id}", "train_count=0"],
                    conclusion=f"FAIL: task {task.task_id} has no training examples",
                ),
                iterations=0,
                depth_reached=0,
            )

        iterations = 0
        depth_reached = 0

        for seq in self._bfs_sequences():
            if iterations >= self._max_iterations:
                break
            depth_reached = max(depth_reached, len(seq))
            iterations += 1

            if self._matches_all_train(task, seq):
                program = ARCProgram(
                    program_id=f"syn_{task.task_id}_{iterations}",
                    task_id=task.task_id,
                    transform_sequence=seq,
                    max_depth=len(seq),
                    halts_deterministically=True,
                )
                proof = ProofObject(
                    rule="arc_synthesizer",
                    premises=[
                        f"task={task.task_id}",
                        f"train_pairs={len(task.train_inputs)}",
                        f"sequence=[{', '.join(t.name for t in seq)}]",
                        f"depth={len(seq)}",
                        f"iterations={iterations}",
                    ],
                    conclusion=(
                        f"PASS: program found for {task.task_id} "
                        f"after {iterations} candidates, depth {len(seq)}"
                    ),
                )
                return SynthesisResult(
                    task_id=task.task_id,
                    success=True,
                    program=program,
                    proof=proof,
                    iterations=iterations,
                    depth_reached=depth_reached,
                )

        return SynthesisResult(
            task_id=task.task_id,
            success=False,
            program=None,
            proof=ProofObject(
                rule="arc_synthesizer",
                premises=[
                    f"task={task.task_id}",
                    f"max_depth={self._max_depth}",
                    f"max_iterations={self._max_iterations}",
                    f"iterations_run={iterations}",
                    f"depth_reached={depth_reached}",
                ],
                conclusion=(
                    f"FAIL: no program found for {task.task_id} "
                    f"within {iterations} candidates, depth 1-{depth_reached}"
                ),
            ),
            iterations=iterations,
            depth_reached=depth_reached,
        )


# ---------------------------------------------------------------------------
# Standalone integrity check (follows Tuple[bool, ProofObject] convention)
# ---------------------------------------------------------------------------


def check_synthesis_result_integrity(
    result: SynthesisResult,
) -> Tuple[bool, ProofObject]:
    """Verify internal consistency of a SynthesisResult.

    Rules:
      - success=True  → program is not None and transform_sequence is non-empty.
      - success=False → program is None.

    Standard: Chollet (2019) "On the Measure of Intelligence".

    Falsifies if: success=True and program is None, or transform_sequence is
    empty; or success=False and program is not None.
    falsifies_if: success=True and program is None or has empty transform_sequence,
    or success=False and program is not None.
    """
    if result.success and result.program is None:
        return False, ProofObject(
            rule="synthesis_result_integrity",
            premises=[f"task={result.task_id}", "success=True", "program=None"],
            conclusion=f"VIOLATION: {result.task_id} success=True but program is None",
        )
    if result.success and result.program is not None:
        if not result.program.transform_sequence:
            return False, ProofObject(
                rule="synthesis_result_integrity",
                premises=[
                    f"task={result.task_id}",
                    "success=True",
                    "transform_sequence=[]",
                ],
                conclusion=f"VIOLATION: {result.task_id} program has empty transform sequence",
            )
    if not result.success and result.program is not None:
        return False, ProofObject(
            rule="synthesis_result_integrity",
            premises=[
                f"task={result.task_id}",
                "success=False",
                f"program={result.program.program_id}",
            ],
            conclusion=f"VIOLATION: {result.task_id} success=False but program is not None",
        )
    return True, ProofObject(
        rule="synthesis_result_integrity",
        premises=[
            f"task={result.task_id}",
            f"success={result.success}",
            f"has_program={result.program is not None}",
            f"iterations={result.iterations}",
        ],
        conclusion=f"SynthesisResult for {result.task_id} is internally consistent",
    )
