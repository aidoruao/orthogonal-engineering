"""
Tests for halt condition enforcement — tests/test_halt_condition.py

Validates that HaltConditionError is raised deterministically when bounds
are exceeded, and that BoundedCounter and bounded() decorator work correctly.

Author: Orthogonal Engineering
PR: #32
Version: 1.0.0
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from oe_ifm.halt_condition import (
    HALT_EXCEEDED,
    BoundedCounter,
    HaltConditionError,
    bounded,
    check_bound,
    pe_finite_range,
)


# ---------------------------------------------------------------------------
# HaltConditionError
# ---------------------------------------------------------------------------


def test_halt_condition_error_attributes():
    """HaltConditionError carries limit_type, current, maximum."""
    exc = HaltConditionError("steps", 101, 100)
    assert exc.limit_type == "steps"
    assert exc.current == 101
    assert exc.maximum == 100
    assert exc.exit_code == HALT_EXCEEDED


def test_halt_exceeded_constant():
    """HALT_EXCEEDED is a distinct non-zero integer exit code."""
    assert isinstance(HALT_EXCEEDED, int)
    assert HALT_EXCEEDED != 0


# ---------------------------------------------------------------------------
# BoundedCounter — step limit
# ---------------------------------------------------------------------------


def test_bounded_counter_step_ok():
    """BoundedCounter accepts steps up to max_steps."""
    counter = BoundedCounter(max_steps=10)
    for _ in range(10):
        counter.step()
    assert counter.steps == 10


def test_bounded_counter_step_exceeded():
    """BoundedCounter raises HaltConditionError when steps > max_steps."""
    counter = BoundedCounter(max_steps=5)
    with pytest.raises(HaltConditionError) as exc_info:
        for _ in range(6):
            counter.step()
    assert exc_info.value.limit_type == "steps"


def test_bounded_counter_reset():
    """BoundedCounter.reset() clears all counters."""
    counter = BoundedCounter(max_steps=3)
    counter.step()
    counter.step()
    counter.reset()
    assert counter.steps == 0
    # Should be able to step again
    counter.step()
    assert counter.steps == 1


def test_bounded_counter_repr():
    """BoundedCounter repr is informative."""
    counter = BoundedCounter(max_steps=100, max_depth=10)
    counter.step(3)
    r = repr(counter)
    assert "steps=3/100" in r
    assert "depth=0/10" in r


# ---------------------------------------------------------------------------
# BoundedCounter — depth limit
# ---------------------------------------------------------------------------


def test_bounded_counter_depth_ok():
    """BoundedCounter tracks depth via context manager."""
    counter = BoundedCounter(max_depth=5)
    with counter.depth_context():
        assert counter.depth == 1
        with counter.depth_context():
            assert counter.depth == 2
        assert counter.depth == 1
    assert counter.depth == 0


def test_bounded_counter_depth_exceeded():
    """BoundedCounter raises HaltConditionError when depth > max_depth."""
    counter = BoundedCounter(max_depth=2)
    with pytest.raises(HaltConditionError) as exc_info:
        with counter.depth_context():
            with counter.depth_context():
                with counter.depth_context():  # depth = 3 > 2
                    pass
    assert exc_info.value.limit_type == "depth"


def test_depth_context_exits_on_exception():
    """Depth context manager decrements depth even on exception."""
    counter = BoundedCounter(max_depth=10)
    try:
        with counter.depth_context():
            assert counter.depth == 1
            raise RuntimeError("test")
    except RuntimeError:
        pass
    assert counter.depth == 0


# ---------------------------------------------------------------------------
# BoundedCounter — memory guard
# ---------------------------------------------------------------------------


def test_bounded_counter_memory_ok():
    """BoundedCounter accepts memory items up to max_memory_items."""
    counter = BoundedCounter(max_memory_items=10)
    for _ in range(10):
        counter.track_item()
    assert counter.memory_items == 10


def test_bounded_counter_memory_exceeded():
    """BoundedCounter raises HaltConditionError when memory exceeds limit."""
    counter = BoundedCounter(max_memory_items=5)
    with pytest.raises(HaltConditionError) as exc_info:
        for _ in range(6):
            counter.track_item()
    assert exc_info.value.limit_type == "memory"


def test_bounded_counter_no_memory_limit():
    """BoundedCounter with no memory limit never raises for memory."""
    counter = BoundedCounter()  # max_memory_items=None
    for _ in range(10_000):
        counter.track_item()  # should not raise


# ---------------------------------------------------------------------------
# check_bound
# ---------------------------------------------------------------------------


def test_check_bound_ok():
    """check_bound increments the counter without raising when under limit."""
    counter = BoundedCounter(max_steps=100)
    check_bound(counter)
    assert counter.steps == 1


def test_check_bound_exceeded():
    """check_bound raises HaltConditionError when limit exceeded."""
    counter = BoundedCounter(max_steps=2)
    check_bound(counter)
    check_bound(counter)
    with pytest.raises(HaltConditionError):
        check_bound(counter)


# ---------------------------------------------------------------------------
# bounded decorator
# ---------------------------------------------------------------------------


def test_bounded_decorator_injects_counter():
    """bounded() decorator injects a BoundedCounter as _counter kwarg."""
    @bounded(max_steps=100)
    def my_func(x, *, _counter):
        _counter.step()
        return x * 2

    result = my_func(5)
    assert result == 10


def test_bounded_decorator_fresh_counter_per_call():
    """Each call to a @bounded function gets a fresh BoundedCounter."""
    call_counts = []

    @bounded(max_steps=10)
    def accumulate(*, _counter):
        _counter.step(3)
        call_counts.append(_counter.steps)

    accumulate()
    accumulate()
    # Each call should start with steps=0
    assert call_counts == [3, 3]


def test_bounded_decorator_halt_on_exceeded():
    """@bounded function raises HaltConditionError when steps exceeded."""
    @bounded(max_steps=5)
    def greedy(*, _counter):
        for _ in range(10):
            _counter.step()

    with pytest.raises(HaltConditionError):
        greedy()


# ---------------------------------------------------------------------------
# pe_finite_range
# ---------------------------------------------------------------------------


def test_pe_finite_range_normal():
    """pe_finite_range returns a normal range for small inputs."""
    r = pe_finite_range(0, 5, max_steps=100)
    assert list(r) == [0, 1, 2, 3, 4]


def test_pe_finite_range_exceeds_max():
    """pe_finite_range raises HaltConditionError when size > max_steps."""
    with pytest.raises(HaltConditionError):
        pe_finite_range(0, 200, max_steps=100)


def test_pe_finite_range_with_counter():
    """pe_finite_range uses provided counter for step tracking."""
    counter = BoundedCounter(max_steps=50)
    r = pe_finite_range(0, 10, counter=counter, max_steps=50)
    assert list(r) == list(range(10))
    assert counter.steps == 10


def test_pe_finite_range_empty():
    """pe_finite_range handles empty range (stop <= start)."""
    r = pe_finite_range(5, 5)
    assert list(r) == []


# ---------------------------------------------------------------------------
# Deterministic halting — simulated recursive expansion
# ---------------------------------------------------------------------------


def test_deterministic_halt_on_deep_recursion():
    """
    A recursive function with BoundedCounter halts deterministically.

    Simulates a recursive tree expansion that would be infinite without bounds.
    """
    counter = BoundedCounter(max_depth=5, max_steps=1000)

    def expand(depth):
        counter.step()
        with counter.depth_context():
            if depth >= 4:
                return depth
            return expand(depth + 1)

    # Should succeed within bounds
    result = expand(0)
    assert result == 4


def test_deterministic_halt_exceeds_depth():
    """Recursive expansion halts when depth limit is exceeded."""
    counter = BoundedCounter(max_depth=3, max_steps=1000)

    def expand(depth):
        with counter.depth_context():
            return expand(depth + 1)

    with pytest.raises(HaltConditionError) as exc_info:
        expand(0)
    assert exc_info.value.limit_type == "depth"
    assert exc_info.value.exit_code == HALT_EXCEEDED
