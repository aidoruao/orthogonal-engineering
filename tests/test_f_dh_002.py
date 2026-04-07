"""
tests/test_f_dh_002.py
F_DH_002: No GL calls execute during splash screen phase

Tests that MixinFramebuffer has proper GL context guards.
"""

import pytest
from fractions import Fraction

from src.domains.d_dh_standalone import (
    build_gl_context_situs,
    evaluate_gl_context_truth_gap,
    run_gl_context_adjunction_check,
    GL_CONTEXT_RACE_VIOLATION,
)
from src.sal.topos_subobject_classifier import SubobjectClassifier
from src.sal.realizability_topos import RealizabilityTopos, realize
from axioms.logic import ProofObject


class TestGLContextGuard:
    """F_DH_002: GL context readiness tests."""
    
    def test_gl_situs_has_context_ready_object(self):
        ctx = build_gl_context_situs()
        assert "gl_context_ready" in ctx.objects
    
    def test_gl_situs_has_splash_screen_object(self):
        ctx = build_gl_context_situs()
        assert "splash_screen_complete" in ctx.objects
    
    def test_gl_context_ready_uncovered(self):
        """GL context ready has no valid covering during splash."""
        ctx = build_gl_context_situs()
        assert ctx.covers.get("gl_context_ready") == []
    
    def test_geometric_morphism_truth_not_preserved(self):
        """The GL situs assumes context ready, reality proves crash."""
        morphism = evaluate_gl_context_truth_gap()
        assert morphism.truth_preserved is False, (
            "GL situs claims context is ready but runtime proves black screen crash."
        )
    
    def test_morphism_proof_cites_gl_sites(self):
        morphism = evaluate_gl_context_truth_gap()
        premises_str = str(morphism.proof.premises)
        assert "Ω_gl" in premises_str
    
    def test_gl_violation_in_schema(self):
        assert "gl_context_violation" in GL_CONTEXT_RACE_VIOLATION
        assert "splash" in GL_CONTEXT_RACE_VIOLATION.lower() or "MixinFramebuffer" in GL_CONTEXT_RACE_VIOLATION


class TestGLAdjunction:
    """Type 3 adjunction tests for GL context."""
    
    def test_gl_adjunction_check_returns_proof(self):
        proof = run_gl_context_adjunction_check()
        from src.sal.adjoint_triple import AdjunctionProof
        assert isinstance(proof, AdjunctionProof)
    
    def test_gl_adjunction_domain_id(self):
        proof = run_gl_context_adjunction_check()
        assert "DH" in proof.domain_id
        assert "GL" in proof.domain_id


class TestGLRealizability:
    """Type 6 realizability tests for GL defect."""
    
    def test_gl_defect_is_realizable(self):
        proof = ProofObject(
            rule="GLContextAnalysis",
            premises=["MixinFramebuffer.java:31-52", "FML splash screen"],
            conclusion="GL calls execute before context ready",
        )
        r, claim, violations = realize("gl_context_race", proof)
        assert r.is_computable
        assert violations == ()
    
    def test_gl_realizer_computes_conclusion(self):
        proof = ProofObject(
            rule="GLContextAnalysis",
            premises=["MixinFramebuffer.java"],
            conclusion="black_screen_crash",
        )
        r, _, _ = realize("gl_crash_prediction", proof)
        assert r.compute() == "black_screen_crash"


class TestSplashScreenBoundary:
    """Tests for splash screen boundary paradox."""
    
    def test_boundary_paradox_documented(self):
        """PX-002: Mixin executes during FML's splash, outside DH's boundary."""
        from src.domains.d_dh_standalone import DH_SCHEMA
        assert any("PX-002" in p or "splash" in p.lower() for p in DH_SCHEMA["paradoxes"])
    
    def test_mixin_does_not_check_splash(self):
        """The actual Mixin does not check isSplashScreenActive()."""
        # This is documented in the source analysis
        from src.domains.d_dh_standalone.invariants import check_gl_context_guard
        result = check_gl_context_guard()
        assert not result.passed  # Should fail — no splash guard exists
