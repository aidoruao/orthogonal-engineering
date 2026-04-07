"""
tests/test_f_dh_004.py
F_DH_004: Chunk event queue has bounded size

Tests that the ConcurrentLinkedQueue has a size limit.
"""

import pytest
from fractions import Fraction

from src.domains.d_dh_standalone import (
    build_server_tick_situs,
    UNBOUNDED_QUEUE_VIOLATION,
)
from src.domains.d_dh_standalone.invariants import check_queue_boundedness
from src.sal.realizability_topos import RealizabilityTopos, realize
from axioms.logic import ProofObject


class TestQueueBoundedness:
    """F_DH_004: Queue bound tests."""
    
    def test_tick_situs_has_work_bounded_object(self):
        ctx = build_server_tick_situs()
        assert "work_is_bounded" in ctx.objects
    
    def test_work_is_bounded_uncovered(self):
        """The 'work is bounded' claim has no valid covering — false."""
        ctx = build_server_tick_situs()
        assert ctx.covers.get("work_is_bounded") == []
    
    def test_queue_violation_documented(self):
        assert "queue_violation" in UNBOUNDED_QUEUE_VIOLATION
        assert "unbounded" in UNBOUNDED_QUEUE_VIOLATION.lower() or "ConcurrentLinkedQueue" in UNBOUNDED_QUEUE_VIOLATION


class TestQueueInvariant:
    """Executable invariant checks for queue."""
    
    def test_queue_boundedness_check_fails(self):
        """The actual queue has no size limit."""
        result = check_queue_boundedness()
        assert not result.passed  # Should fail — queue is unbounded
    
    def test_queue_check_identifies_location(self):
        result = check_queue_boundedness()
        assert result.violation_location is not None
        assert "ForgeServerProxy" in result.violation_location or "chunkLoadEvents" in result.violation_location
    
    def test_queue_check_recommends_cap(self):
        result = check_queue_boundedness()
        assert result.recommended_fix is not None
        assert "20" in result.recommended_fix or "1000" in result.recommended_fix or "cap" in result.recommended_fix.lower()


class TestQueueRealizability:
    """Type 6 realizability for queue defect."""
    
    def test_queue_growth_is_realizable(self):
        """The unbounded queue growth is a computable realizer."""
        proof = ProofObject(
            rule="QueueAnalysis",
            premises=["ConcurrentLinkedQueue", "no size limit"],
            conclusion="queue_grows_without_bound",
        )
        r, claim, violations = realize("queue_unbounded", proof)
        assert r.is_computable
        assert violations == ()


class TestTickBudgetRelation:
    """Tests relating queue to tick budget."""
    
    def test_unbounded_queue_exhausts_budget(self):
        """The unbounded queue causes tick budget violation."""
        from src.domains.d_dh_standalone import TICK_BUDGET_VIOLATION
        assert "queue" in TICK_BUDGET_VIOLATION.lower() or "unbounded" in TICK_BUDGET_VIOLATION.lower() or "budget" in TICK_BUDGET_VIOLATION.lower()
    
    def test_tick_situs_assumes_bounded(self):
        ctx = build_server_tick_situs()
        # The tick situs assumes work is bounded
        assert "work_is_bounded" in ctx.objects
        # But this assumption is false in reality
        assert ctx.covers.get("work_is_bounded") == []
