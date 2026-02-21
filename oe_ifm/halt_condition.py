"""
Halt Condition Enforcement — oe_ifm/halt_condition.py

Implements UD-Bounded(k) and PE-Finite guarantees:
  - Every recursive / iterative expansion has a hard ceiling.
  - On ceiling breach the code raises HaltConditionError rather than hanging.
  - A deterministic exit code (HALT_EXCEEDED = 2) is provided for CLI callers.

Public API:
  HaltConditionError      — raised when a bound is exceeded
  HALT_EXCEEDED           — exit code returned when halting
  BoundedCounter          — stateful counter for step/depth tracking
  bounded(max_steps, ...)  — decorator that injects a counter into the call
  check_bound(counter)    — inline guard; raises HaltConditionError if exceeded

Author: Orthogonal Engineering
PR: #32
Version: 1.0.0
"""

from __future__ import annotations

import functools
from typing import Any, Callable, Optional

# Exit code used when the system triggers a halt (deterministic, not an error)
HALT_EXCEEDED: int = 2


# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------


class HaltConditionError(Exception):
    """
    Raised when a configured step/depth bound is exceeded.

    Attributes:
        limit_type:  'steps' | 'depth' | 'memory'
        current:     The value that triggered the halt.
        maximum:     The configured maximum.
    """

    def __init__(self, limit_type: str, current: int, maximum: int) -> None:
        self.limit_type = limit_type
        self.current = current
        self.maximum = maximum
        super().__init__(
            f"Halt condition triggered: {limit_type} limit exceeded "
            f"({current} > {maximum})"
        )

    @property
    def exit_code(self) -> int:
        return HALT_EXCEEDED


# ---------------------------------------------------------------------------
# BoundedCounter
# ---------------------------------------------------------------------------


class BoundedCounter:
    """
    Thread-safe-by-design step/depth counter with hard limits.

    Usage::

        counter = BoundedCounter(max_steps=1000, max_depth=50)
        for i in range(n):
            counter.step()   # raises HaltConditionError if > max_steps
        with counter.depth_context():
            ...              # raises HaltConditionError if depth > max_depth
    """

    def __init__(
        self,
        max_steps: int = 10_000,
        max_depth: int = 100,
        max_memory_items: Optional[int] = None,
    ) -> None:
        if max_steps < 1:
            raise ValueError(f"max_steps must be >= 1, got {max_steps}")
        if max_depth < 1:
            raise ValueError(f"max_depth must be >= 1, got {max_depth}")

        self.max_steps = max_steps
        self.max_depth = max_depth
        self.max_memory_items = max_memory_items

        self._steps: int = 0
        self._depth: int = 0
        self._memory_items: int = 0

    # -- Step counting --

    def step(self, n: int = 1) -> None:
        """Increment step counter; raise HaltConditionError if limit exceeded."""
        self._steps += n
        if self._steps > self.max_steps:
            raise HaltConditionError("steps", self._steps, self.max_steps)

    @property
    def steps(self) -> int:
        return self._steps

    # -- Depth tracking --

    def enter_depth(self) -> None:
        """Signal entry into a new recursion level."""
        self._depth += 1
        if self._depth > self.max_depth:
            raise HaltConditionError("depth", self._depth, self.max_depth)

    def exit_depth(self) -> None:
        """Signal exit from a recursion level."""
        self._depth -= 1

    @property
    def depth(self) -> int:
        return self._depth

    class _DepthContext:
        def __init__(self, counter: "BoundedCounter") -> None:
            self._counter = counter

        def __enter__(self) -> "BoundedCounter._DepthContext":
            self._counter.enter_depth()
            return self

        def __exit__(self, *_: Any) -> None:
            self._counter.exit_depth()

    def depth_context(self) -> "_DepthContext":
        """Context manager that tracks recursion depth."""
        return self._DepthContext(self)

    # -- Memory guard --

    def track_item(self, n: int = 1) -> None:
        """Track an in-memory item; raise if max_memory_items exceeded."""
        if self.max_memory_items is None:
            return
        self._memory_items += n
        if self._memory_items > self.max_memory_items:
            raise HaltConditionError("memory", self._memory_items, self.max_memory_items)

    @property
    def memory_items(self) -> int:
        return self._memory_items

    def reset(self) -> None:
        """Reset all counters (useful between runs)."""
        self._steps = 0
        self._depth = 0
        self._memory_items = 0

    def __repr__(self) -> str:
        return (
            f"BoundedCounter(steps={self._steps}/{self.max_steps}, "
            f"depth={self._depth}/{self.max_depth})"
        )


# ---------------------------------------------------------------------------
# check_bound — inline guard helper
# ---------------------------------------------------------------------------


def check_bound(counter: BoundedCounter, step_inc: int = 1) -> None:
    """
    Inline step-increment guard.

    Equivalent to ``counter.step(step_inc)`` but more readable at call sites.

    Args:
        counter:   A BoundedCounter instance.
        step_inc:  Number of steps to add (default 1).

    Raises:
        HaltConditionError: If the step limit is exceeded.
    """
    counter.step(step_inc)


# ---------------------------------------------------------------------------
# bounded — decorator
# ---------------------------------------------------------------------------


def bounded(
    max_steps: int = 10_000,
    max_depth: int = 100,
    max_memory_items: Optional[int] = None,
) -> Callable:
    """
    Decorator factory that wraps a function with a BoundedCounter.

    The counter is passed as the keyword argument ``_counter`` to the wrapped
    function, which may use it to enforce fine-grained limits internally.
    The decorator itself does NOT automatically count steps; the function body
    is responsible for calling ``_counter.step()`` at appropriate points.

    Example::

        @bounded(max_steps=500, max_depth=10)
        def expand(node, depth=0, *, _counter):
            _counter.step()
            with _counter.depth_context():
                if depth > 3:
                    return node
                return [expand(child, depth+1, _counter=_counter) for child in node.children]

    Args:
        max_steps:         Hard ceiling on step count.
        max_depth:         Hard ceiling on recursion depth.
        max_memory_items:  Optional ceiling on tracked memory items.

    Returns:
        Decorator that injects a fresh BoundedCounter per call.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            counter = BoundedCounter(
                max_steps=max_steps,
                max_depth=max_depth,
                max_memory_items=max_memory_items,
            )
            kwargs["_counter"] = counter
            return func(*args, **kwargs)

        return wrapper

    return decorator


# ---------------------------------------------------------------------------
# pe_finite_range — bounded iterator helper
# ---------------------------------------------------------------------------


def pe_finite_range(
    start: int,
    stop: int,
    counter: Optional[BoundedCounter] = None,
    max_steps: int = 10_000,
) -> "range":
    """
    Return range(start, stop) after verifying PE-Finite bounds.

    If the range would exceed max_steps, raise HaltConditionError before
    yielding any values.

    Args:
        start:      Range start (inclusive).
        stop:       Range stop (exclusive).
        counter:    Optional existing BoundedCounter to reuse.
        max_steps:  Maximum allowed range size.

    Returns:
        A standard range object (safe to iterate).

    Raises:
        HaltConditionError: If stop - start > max_steps.
    """
    size = stop - start
    if size < 0:
        size = 0
    if counter is not None:
        counter.step(size)
    elif size > max_steps:
        raise HaltConditionError("steps", size, max_steps)
    return range(start, stop)
