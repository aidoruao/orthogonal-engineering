"""tests/test_oe_synthesizer.py — ARCSynthesizer falsification tests.

Tests cover:
  - Individual transform primitives (all 6 TransformType)
  - apply_sequence: identity and multi-step
  - Synthesis of single-transform tasks (ROTATION, REFLECTION, COLOR_MAP)
  - Synthesis of two-transform tasks
  - Determinism: same task → identical result
  - Failure case: task with no solution in budget
  - check_synthesis_result_integrity: valid and invalid results
  - Max-iterations safety bound
"""

from fractions import Fraction
from typing import List

import pytest

from axioms.logic import ProofObject
from oe_engine.synthesizer import (
    ARCSynthesizer,
    SynthesisResult,
    check_synthesis_result_integrity,
    MAX_SYNTHESIS_DEPTH,
    MAX_ITERATIONS,
    _rotate_cw,
    _reflect_h,
    _translate_r,
    _transpose,
    _invert_colors,
    _shift_colors,
)
from src.domains.d_arc_agi_3.implementation import (
    ARCProgram,
    ARCTask,
    GridState,
    TransformType,
    grids_equal,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_grid(cells: List[List[int]], task_id: str = "t0") -> GridState:
    """Build a GridState from a 2-D list."""
    return GridState(
        task_id=task_id,
        height=len(cells),
        width=len(cells[0]) if cells else 0,
        cells=cells,
    )


def make_single_pair_task(
    inp: GridState, out: GridState, task_id: str = "t0"
) -> ARCTask:
    """Construct a one-pair ARCTask."""
    return ARCTask(
        task_id=task_id,
        train_inputs=[inp],
        train_outputs=[out],
        test_inputs=[inp],
        test_outputs=[out],
    )


# ---------------------------------------------------------------------------
# Transform primitive tests
# ---------------------------------------------------------------------------


def test_rotate_cw_3x2() -> None:
    """Rotation of a 3x2 grid produces a 2x3 grid."""
    g = make_grid([[1, 2], [3, 4], [5, 6]])
    r = _rotate_cw(g)
    assert r.height == 2
    assert r.width == 3
    # new[j][H-1-i] = old[i][j]
    # row 0: old[2][0]=5, old[1][0]=3, old[0][0]=1
    assert r.cells[0] == [5, 3, 1]
    assert r.cells[1] == [6, 4, 2]


def test_rotate_cw_four_times_identity() -> None:
    """Rotating a square grid 4 times returns the original."""
    g = make_grid([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    result = g
    for _ in range(4):
        result = _rotate_cw(result)
    assert grids_equal(result, g)


def test_reflect_h_identity_on_symmetric() -> None:
    """Horizontally reflecting a palindrome row is a no-op."""
    g = make_grid([[1, 2, 1], [3, 3, 3]])
    r = _reflect_h(g)
    assert grids_equal(r, g)


def test_reflect_h_reverses_row() -> None:
    """Reflection reverses every row."""
    g = make_grid([[1, 2, 3]])
    r = _reflect_h(g)
    assert r.cells[0] == [3, 2, 1]


def test_translate_r_wraps() -> None:
    """Cyclic right shift wraps last column to first."""
    g = make_grid([[1, 2, 3]])
    r = _translate_r(g)
    assert r.cells[0] == [3, 1, 2]


def test_translate_r_n_times_identity() -> None:
    """Cycling right W times returns the original."""
    g = make_grid([[1, 2, 3, 4]])
    result = g
    for _ in range(4):
        result = _translate_r(result)
    assert grids_equal(result, g)


def test_transpose_square() -> None:
    """Transposing a square grid swaps rows and columns."""
    g = make_grid([[1, 2], [3, 4]])
    t = _transpose(g)
    assert t.cells[0] == [1, 3]
    assert t.cells[1] == [2, 4]


def test_transpose_dimensions() -> None:
    """Transpose of H×W grid is W×H."""
    g = make_grid([[1, 2, 3], [4, 5, 6]])
    t = _transpose(g)
    assert t.height == 3
    assert t.width == 2


def test_invert_colors_range() -> None:
    """All colors inverted: new = 9 - old."""
    g = make_grid([[0, 5, 9]])
    r = _invert_colors(g)
    assert r.cells[0] == [9, 4, 0]


def test_invert_colors_twice_identity() -> None:
    """Inverting twice returns original."""
    g = make_grid([[1, 2, 3], [7, 8, 9]])
    r = _invert_colors(_invert_colors(g))
    assert grids_equal(r, g)


def test_shift_colors_wraps() -> None:
    """Shift +1 mod 10: color 9 wraps to 0."""
    g = make_grid([[8, 9, 0]])
    r = _shift_colors(g)
    assert r.cells[0] == [9, 0, 1]


def test_shift_colors_ten_times_identity() -> None:
    """Shifting 10 times returns original (mod 10)."""
    g = make_grid([[1, 5, 9]])
    result = g
    for _ in range(10):
        result = _shift_colors(result)
    assert grids_equal(result, g)


# ---------------------------------------------------------------------------
# apply_sequence tests
# ---------------------------------------------------------------------------


def test_apply_sequence_empty_is_identity() -> None:
    """Empty sequence returns the grid unchanged."""
    syn = ARCSynthesizer()
    g = make_grid([[1, 2], [3, 4]])
    result = syn.apply_sequence(g, [])
    assert grids_equal(result, g)


def test_apply_sequence_two_reflections() -> None:
    """Reflecting twice is identity."""
    syn = ARCSynthesizer()
    g = make_grid([[1, 2, 3]])
    r = syn.apply_sequence(g, [TransformType.REFLECTION, TransformType.REFLECTION])
    assert grids_equal(r, g)


def test_apply_sequence_color_then_invert() -> None:
    """COLOR_MAP twice is identity: 9-(9-c) = c."""
    syn = ARCSynthesizer()
    g = make_grid([[0, 4, 9]])
    r = syn.apply_sequence(g, [TransformType.COLOR_MAP, TransformType.COLOR_MAP])
    assert grids_equal(r, g)


# ---------------------------------------------------------------------------
# Synthesis — single transform
# ---------------------------------------------------------------------------


def test_synthesis_finds_reflection() -> None:
    """Synthesizer finds REFLECTION for a task where output = reflect_h(input)."""
    syn = ARCSynthesizer()
    inp = make_grid([[1, 2, 3], [4, 5, 6]])
    out = _reflect_h(inp)
    task = make_single_pair_task(inp, out, task_id="t_reflect")
    result = syn.synthesize(task)

    assert result.success
    assert result.program is not None
    assert result.proof.is_valid()
    assert isinstance(result.program.transform_sequence, list)
    assert len(result.program.transform_sequence) >= 1
    assert result.program.halts_deterministically


def test_synthesis_finds_color_inversion() -> None:
    """Synthesizer finds COLOR_MAP for a task where output = invert_colors(input)."""
    syn = ARCSynthesizer()
    inp = make_grid([[0, 5, 9]])
    out = _invert_colors(inp)
    task = make_single_pair_task(inp, out, task_id="t_color")
    result = syn.synthesize(task)

    assert result.success
    assert result.program is not None
    # The single-transform solution should be found at depth 1
    assert len(result.program.transform_sequence) == 1
    assert result.program.transform_sequence[0] == TransformType.COLOR_MAP


def test_synthesis_finds_transpose() -> None:
    """Synthesizer finds SCALING (transpose) for a square task."""
    syn = ARCSynthesizer()
    inp = make_grid([[1, 2], [3, 4]])
    out = _transpose(inp)
    task = make_single_pair_task(inp, out, task_id="t_transpose")
    result = syn.synthesize(task)

    assert result.success
    assert result.program is not None
    assert len(result.program.transform_sequence) == 1
    assert result.program.transform_sequence[0] == TransformType.SCALING


def test_synthesis_finds_translation() -> None:
    """Synthesizer finds TRANSLATION for a task where output = translate_r(input)."""
    syn = ARCSynthesizer()
    inp = make_grid([[1, 2, 3]])
    out = _translate_r(inp)
    task = make_single_pair_task(inp, out, task_id="t_translate")
    result = syn.synthesize(task)

    assert result.success
    assert result.program is not None
    assert len(result.program.transform_sequence) == 1


def test_synthesis_finds_shift_colors() -> None:
    """Synthesizer finds PATTERN_FILL for a task where output = shift_colors(input)."""
    syn = ARCSynthesizer()
    inp = make_grid([[0, 1, 9]])
    out = _shift_colors(inp)
    task = make_single_pair_task(inp, out, task_id="t_shift")
    result = syn.synthesize(task)

    assert result.success
    assert result.program is not None
    assert len(result.program.transform_sequence) == 1
    assert result.program.transform_sequence[0] == TransformType.PATTERN_FILL


# ---------------------------------------------------------------------------
# Synthesis — two transforms
# ---------------------------------------------------------------------------


def test_synthesis_finds_two_transform_sequence() -> None:
    """Synthesizer finds a depth-2 sequence (reflect + invert)."""
    syn = ARCSynthesizer()
    inp = make_grid([[1, 2, 3]])
    out = _invert_colors(_reflect_h(inp))
    task = make_single_pair_task(inp, out, task_id="t_two")
    result = syn.synthesize(task)

    assert result.success
    assert result.program is not None
    # BFS finds shortest first; depth-2 solution exists
    assert len(result.program.transform_sequence) <= 2


# ---------------------------------------------------------------------------
# Synthesis — multiple training pairs
# ---------------------------------------------------------------------------


def test_synthesis_two_train_pairs() -> None:
    """Synthesizer works with two training pairs for COLOR_MAP task."""
    syn = ARCSynthesizer()
    inp1 = make_grid([[0, 9]], task_id="t_multi")
    inp2 = make_grid([[3, 6]], task_id="t_multi")
    out1 = _invert_colors(inp1)
    out2 = _invert_colors(inp2)
    task = ARCTask(
        task_id="t_multi",
        train_inputs=[inp1, inp2],
        train_outputs=[out1, out2],
        test_inputs=[inp1],
        test_outputs=[out1],
    )
    result = syn.synthesize(task)
    assert result.success
    assert result.program is not None


# ---------------------------------------------------------------------------
# Synthesis — failure cases
# ---------------------------------------------------------------------------


def test_synthesis_empty_task_fails() -> None:
    """Synthesizer returns failure for task with no training examples."""
    syn = ARCSynthesizer()
    task = ARCTask(
        task_id="t_empty",
        train_inputs=[],
        train_outputs=[],
        test_inputs=[],
        test_outputs=[],
    )
    result = syn.synthesize(task)
    assert not result.success
    assert result.program is None
    assert result.proof.is_valid()


def test_synthesis_unsolvable_within_budget() -> None:
    """Synthesizer returns failure when no sequence matches in tiny budget."""
    # Use max_iterations=1 and a task that requires depth > 1
    syn = ARCSynthesizer(max_depth=1, max_iterations=1)
    # Task whose solution is reflect + invert (depth 2) — no depth-1 solution exists
    # unless REFLECTION alone happens to match, so use a carefully constructed grid
    inp = make_grid([[1, 0], [0, 1]])   # identity-invariant under reflection
    # Output is something no single transform produces
    out = make_grid([[2, 3], [4, 5]])
    task = make_single_pair_task(inp, out, task_id="t_fail")
    result = syn.synthesize(task)
    assert not result.success
    assert result.program is None


def test_synthesis_max_iterations_respected() -> None:
    """Synthesizer never evaluates more candidates than max_iterations."""
    syn = ARCSynthesizer(max_depth=6, max_iterations=5)
    inp = make_grid([[7, 8, 9]])
    out = make_grid([[0, 1, 2]])   # hard to solve in 5 iterations
    task = make_single_pair_task(inp, out, task_id="t_budget")
    result = syn.synthesize(task)
    # May or may not find solution, but iterations must be <= 5
    assert result.iterations <= 5


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_synthesis_deterministic() -> None:
    """Same task returns the same program on repeated calls."""
    syn = ARCSynthesizer()
    inp = make_grid([[0, 5]])
    out = _invert_colors(inp)
    task = make_single_pair_task(inp, out, task_id="t_det")
    r1 = syn.synthesize(task)
    r2 = syn.synthesize(task)
    assert r1.success == r2.success
    assert r1.iterations == r2.iterations
    assert r1.program is not None and r2.program is not None
    assert r1.program.transform_sequence == r2.program.transform_sequence
    assert r1.proof.proof_hash == r2.proof.proof_hash


def test_apply_sequence_deterministic() -> None:
    """Same grid + sequence always produces the same output."""
    syn = ARCSynthesizer()
    g = make_grid([[1, 2, 3], [4, 5, 6]])
    seq = [TransformType.REFLECTION, TransformType.COLOR_MAP]
    r1 = syn.apply_sequence(g, seq)
    r2 = syn.apply_sequence(g, seq)
    assert grids_equal(r1, r2)


# ---------------------------------------------------------------------------
# ProofObject integrity
# ---------------------------------------------------------------------------


def test_synthesis_proof_is_valid() -> None:
    """Proof in SynthesisResult passes is_valid() hash check."""
    syn = ARCSynthesizer()
    inp = make_grid([[1, 2]])
    out = _reflect_h(inp)
    task = make_single_pair_task(inp, out, task_id="t_proof")
    result = syn.synthesize(task)
    assert result.proof.is_valid()


# ---------------------------------------------------------------------------
# check_synthesis_result_integrity
# ---------------------------------------------------------------------------


def test_integrity_check_valid_success() -> None:
    """Integrity check passes for a successful result with a valid program."""
    syn = ARCSynthesizer()
    inp = make_grid([[9, 0]])
    out = _invert_colors(inp)
    task = make_single_pair_task(inp, out, task_id="t_int")
    result = syn.synthesize(task)
    ok, proof = check_synthesis_result_integrity(result)
    assert ok
    assert proof.is_valid()


def test_integrity_check_valid_failure() -> None:
    """Integrity check passes for a failure result with no program."""
    task = ARCTask(
        task_id="t_no",
        train_inputs=[],
        train_outputs=[],
        test_inputs=[],
        test_outputs=[],
    )
    syn = ARCSynthesizer()
    result = syn.synthesize(task)
    ok, proof = check_synthesis_result_integrity(result)
    assert ok
    assert proof.is_valid()


def test_integrity_check_rejects_success_without_program() -> None:
    """Integrity check fails when success=True but program is None."""
    dummy_proof = ProofObject(rule="test", premises=[], conclusion="ok")
    bad_result = SynthesisResult(
        task_id="bad",
        success=True,
        program=None,
        proof=dummy_proof,
        iterations=0,
        depth_reached=0,
    )
    ok, proof = check_synthesis_result_integrity(bad_result)
    assert not ok
    assert "VIOLATION" in proof.conclusion


def test_integrity_check_rejects_failure_with_program() -> None:
    """Integrity check fails when success=False but program is not None."""
    dummy_proof = ProofObject(rule="test", premises=[], conclusion="ok")
    fake_program = ARCProgram(
        program_id="fake",
        task_id="bad",
        transform_sequence=[TransformType.ROTATION],
        max_depth=1,
        halts_deterministically=True,
    )
    bad_result = SynthesisResult(
        task_id="bad",
        success=False,
        program=fake_program,
        proof=dummy_proof,
        iterations=1,
        depth_reached=1,
    )
    ok, proof = check_synthesis_result_integrity(bad_result)
    assert not ok
    assert "VIOLATION" in proof.conclusion


def test_integrity_check_rejects_success_with_empty_sequence() -> None:
    """Integrity check fails when success=True but transform_sequence is empty."""
    dummy_proof = ProofObject(rule="test", premises=[], conclusion="ok")
    empty_program = ARCProgram(
        program_id="empty",
        task_id="bad",
        transform_sequence=[],
        max_depth=0,
        halts_deterministically=True,
    )
    bad_result = SynthesisResult(
        task_id="bad",
        success=True,
        program=empty_program,
        proof=dummy_proof,
        iterations=0,
        depth_reached=0,
    )
    ok, proof = check_synthesis_result_integrity(bad_result)
    assert not ok
    assert "VIOLATION" in proof.conclusion


# ---------------------------------------------------------------------------
# Constructor validation
# ---------------------------------------------------------------------------


def test_synthesizer_rejects_zero_depth() -> None:
    """ARCSynthesizer raises ValueError for max_depth <= 0."""
    with pytest.raises(ValueError, match="max_depth"):
        ARCSynthesizer(max_depth=0)


def test_synthesizer_rejects_zero_iterations() -> None:
    """ARCSynthesizer raises ValueError for max_iterations <= 0."""
    with pytest.raises(ValueError, match="max_iterations"):
        ARCSynthesizer(max_iterations=0)


# ---------------------------------------------------------------------------
# Constants sanity
# ---------------------------------------------------------------------------


def test_constants() -> None:
    """MAX_SYNTHESIS_DEPTH and MAX_ITERATIONS are positive integers."""
    assert isinstance(MAX_SYNTHESIS_DEPTH, int) and MAX_SYNTHESIS_DEPTH > 0
    assert isinstance(MAX_ITERATIONS, int) and MAX_ITERATIONS > 0
