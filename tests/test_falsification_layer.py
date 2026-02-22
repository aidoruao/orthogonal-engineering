"""
tests/test_falsification.py — Tests for Popperian Enforcement Layer

Note: The existing tests/test_falsification.py covers F-001..F-005 assumptions.
This file adds tests for the new falsification/ package.

Author: Orthogonal Engineering
PR: #34
Version: 1.0.0
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

# Re-run existing assumption tests first
from tests.test_falsification import *  # noqa: F401,F403

from falsification.hypothesis import Hypothesis, FalsificationResult, register_hypothesis, HYPOTHESIS_REGISTRY
from falsification.counterexample_engine import (
    CounterexampleFound,
    run_falsification,
    run_all_hypotheses,
)
import falsification.property_tests as _pt  # noqa: F401 — registers H-001..H-005

# ---------------------------------------------------------------------------
# Hypothesis dataclass
# ---------------------------------------------------------------------------


def test_hypothesis_survives_empty_domain():
    h = Hypothesis(
        hypothesis_id="TEST-001",
        claim="Vacuously true on empty domain",
        assumptions=[],
        invariant=lambda x: False,  # would fail on any witness
        domain=[],
    )
    result = h.attempt_falsification()
    assert result.survived is True


def test_hypothesis_detects_counterexample():
    h = Hypothesis(
        hypothesis_id="TEST-002",
        claim="Always fails",
        assumptions=[],
        invariant=lambda x: x != 0,
        domain=[0, 1, 2],
    )
    result = h.attempt_falsification()
    assert result.survived is False
    assert result.counterexample == 0


def test_falsification_result_to_dict():
    r = FalsificationResult(
        hypothesis_id="TEST-003",
        survived=True,
        detail="No counterexample",
    )
    d = r.to_dict()
    assert d["survived"] is True
    assert d["hypothesis_id"] == "TEST-003"


# ---------------------------------------------------------------------------
# Counterexample engine
# ---------------------------------------------------------------------------


def test_run_all_hypotheses_returns_list():
    h = Hypothesis(
        hypothesis_id="ENGINE-001",
        claim="1 == 1",
        assumptions=[],
        invariant=lambda x: x == x,
        domain=[1, 2, 3],
    )
    results = run_all_hypotheses([h])
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0].survived is True


def test_run_falsification_raises_on_counterexample():
    h = Hypothesis(
        hypothesis_id="ENGINE-002",
        claim="All x > 100",
        assumptions=[],
        invariant=lambda x: x > 100,
        domain=[0, 1, 2],
    )
    with pytest.raises(CounterexampleFound):
        run_falsification([h], raise_on_counterexample=True)


def test_run_falsification_no_raise():
    h = Hypothesis(
        hypothesis_id="ENGINE-003",
        claim="All x < 0",
        assumptions=[],
        invariant=lambda x: x < 0,
        domain=[0, 1],
    )
    results = run_falsification([h], raise_on_counterexample=False)
    assert len(results) == 1
    assert results[0].survived is False


# ---------------------------------------------------------------------------
# Property tests (H-001..H-005)
# ---------------------------------------------------------------------------


def test_all_registered_property_hypotheses_survive():
    """All H-00x hypotheses registered in property_tests must survive."""
    from falsification.hypothesis import HYPOTHESIS_REGISTRY
    repo_hypotheses = [h for h in HYPOTHESIS_REGISTRY if h.hypothesis_id.startswith("H-")]
    assert len(repo_hypotheses) >= 5
    results = run_all_hypotheses(repo_hypotheses)
    failures = [r for r in results if not r.survived]
    assert failures == [], f"Hypotheses failed: {[r.hypothesis_id for r in failures]}"
