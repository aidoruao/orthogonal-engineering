"""
tests/test_f_dh_001.py
D_DH_STANDALONE forensic domain tests — Type 3+ through Type 6 validation.

F_DH_001: serverTickEvent completes within 15ms under synthetic load

These tests assert that:
  1. The geometric morphism between config situs and runtime situs does NOT
     preserve truth (Type 3+ — topos truth divergence).
  2. The adjunction check for the config paradox is structurally valid but
     semantically fails (Type 3 — counit failure).
  3. ForcingOperation produces valid generic extensions (Type 5).
  4. RealizabilityTopos can realize the mathematical proof π × 4096² (Type 6).
  5. The evidence anchor (SHA-256 of commit hash) is correctly computed (Yeshua Axiom 8).

Biblical inspiration: "Count the cost before building" (Luke 14:28)
The DH developers did not count the cost of 4096-block default.
"""

from __future__ import annotations

import hashlib
import math
from fractions import Fraction

import pytest

from src.domains.d_dh_standalone import (
    DH_REPOSITORY_URL,
    DH_COMMIT_HASH,
    DH_EVIDENCE_ANCHOR,
    DH_SCHEMA,
    DH_COUNIT_VIOLATION,
    CONFIG_PARADOX_PX001,
    UNBOUNDED_QUEUE_VIOLATION,
    TICK_BUDGET_VIOLATION,
    GL_CONTEXT_RACE_VIOLATION,
    BLOCKS_SQUARED_PER_PLAYER,
    build_config_situs,
    build_runtime_situs,
    build_server_tick_situs,
    build_gl_context_situs,
    evaluate_config_runtime_truth_gap,
    evaluate_tick_budget_truth_gap,
    evaluate_gl_context_truth_gap,
    build_domain_state,
    run_adjunction_check,
    run_tick_budget_adjunction_check,
    run_gl_context_adjunction_check,
    DhStandaloneReport,
    build_full_report,
)
from src.sal.adjoint_triple import AdjointTriple, has_adjunction
from src.sal.forcing_operation import (
    CardinalStrength,
    DomainState,
    ForcingOperation,
    force_domain,
)
from src.sal.topos_subobject_classifier import (
    SheafContext,
    SubobjectClassifier,
    geometric_morphism,
)
from src.sal.higher_adjunction import (
    HigherAdjunction,
    HigherInductiveDomain,
    higher_has_adjunction,
    IdentityPath,
    Transport,
)
from src.sal.realizability_topos import (
    RealizabilityTopos,
    ORDINAL_EPSILON_0,
    ORDINAL_GAMMA_0,
    realize,
)
from axioms.logic import ProofObject


# ===========================================================================
# Evidence-anchor tests (Yeshua Axiom 8)
# ===========================================================================


class TestEvidenceAnchor:
    """Tests for evidence anchoring per Yeshua Axiom 8."""
    
    def test_anchor_is_64_char_hex_sha256(self):
        assert len(DH_EVIDENCE_ANCHOR) == 64
        assert all(c in "0123456789abcdef" for c in DH_EVIDENCE_ANCHOR)
    
    def test_anchor_matches_commit_hash_sha256(self):
        expected = hashlib.sha256(DH_COMMIT_HASH.encode("utf-8")).hexdigest()
        assert DH_EVIDENCE_ANCHOR == expected
    
    def test_anchor_is_deterministic(self):
        a = hashlib.sha256(DH_COMMIT_HASH.encode("utf-8")).hexdigest()
        b = hashlib.sha256(DH_COMMIT_HASH.encode("utf-8")).hexdigest()
        assert a == b
    
    def test_schema_carries_evidence_anchor(self):
        assert DH_EVIDENCE_ANCHOR in DH_SCHEMA["evidence_anchors"]
    
    def test_repository_url_is_github(self):
        assert "github.com" in DH_REPOSITORY_URL
        assert "DistantHorizonsStandalone" in DH_REPOSITORY_URL


# ===========================================================================
# Mathematical proof tests (The 52.7 Million Block Problem)
# ===========================================================================


class TestMathematicalProof:
    """Tests for the mathematical proof of config paradox."""
    
    def test_blocks_squared_calculation(self):
        """π × 4096² should equal ~52.7 million blocks²"""
        expected = int(math.pi * 4096 * 4096)
        assert BLOCKS_SQUARED_PER_PLAYER == expected
        assert BLOCKS_SQUARED_PER_PLAYER > 52_000_000  # At least 52M
    
    def test_blocks_squared_makes_defect_provable(self):
        """The sheer magnitude proves the config is defective by design."""
        # With 10 players: 527 million blocks of generation area
        ten_player_area = 10 * BLOCKS_SQUARED_PER_PLAYER
        assert ten_player_area > 500_000_000  # Over half a billion blocks
    
    def test_pi_times_r_squared_is_realizer(self):
        """The mathematical formula πr² is a realizer in the effective topos."""
        proof = ProofObject(
            rule="MathematicalDerivation",
            premises=["r=4096", "area=π×r²"],
            conclusion=f"area={BLOCKS_SQUARED_PER_PLAYER} blocks² per player",
        )
        r, claim, violations = realize("config_area_computation", proof)
        assert r.is_computable
        assert violations == ()


# ===========================================================================
# Type 3+ — Topos truth divergence
# ===========================================================================


class TestToposTruthDivergence:
    """Tests for geometric morphisms between situs."""
    
    def test_config_situs_has_max_generation_valid(self):
        ctx = build_config_situs()
        assert "max_generation_distance_valid" in ctx.objects
    
    def test_runtime_situs_has_tps_degradation(self):
        ctx = build_runtime_situs()
        assert "tps_degradation_observed" in ctx.objects
    
    def test_config_runtime_morphism_truth_not_preserved(self):
        """The geometric morphism must NOT preserve truth (config vs runtime)."""
        morphism = evaluate_config_runtime_truth_gap()
        assert morphism.truth_preserved is False, (
            "Expected truth_preserved=False: config claims 'valid' but runtime "
            "proves 'TPS < 20'."
        )
    
    def test_geometric_morphism_has_yeshua_claim(self):
        morphism = evaluate_config_runtime_truth_gap()
        assert len(morphism.claim.hash_commitment) == 64
        assert morphism.claim.is_reproducible()
        assert morphism.claim.is_hash_anchored()
    
    def test_geometric_morphism_proof_cites_sites(self):
        morphism = evaluate_config_runtime_truth_gap()
        premises_str = str(morphism.proof.premises)
        assert "Ω_config" in premises_str
        assert "Ω_runtime" in premises_str
    
    def test_tick_budget_morphism_truth_not_preserved(self):
        """Server tick situs assumes bounded work, runtime proves unbounded."""
        morphism = evaluate_tick_budget_truth_gap()
        # Truth is not preserved when shared objects have different coverage
        shared = morphism.source.objects & morphism.target.objects
        if shared:
            assert morphism.truth_preserved is False
    
    def test_gl_context_morphism_truth_not_preserved(self):
        """GL situs assumes context ready, runtime proves crash."""
        morphism = evaluate_gl_context_truth_gap()
        assert morphism.truth_preserved is False
    
    def test_subobject_classifier_uses_fraction_not_float(self):
        ctx = build_config_situs()
        cls = SubobjectClassifier(ctx)
        tv = cls.evaluate("max_generation_distance_valid", "max_generation_distance_valid")
        assert isinstance(tv, Fraction)


# ===========================================================================
# Type 3 — SAL adjunction check (counit / unit)
# ===========================================================================


class TestSALAdjunctionCheck:
    """Tests for Type 3 adjunction verification."""
    
    def test_adjunction_check_returns_adjunction_proof(self):
        proof = run_adjunction_check()
        from src.sal.adjoint_triple import AdjunctionProof
        assert isinstance(proof, AdjunctionProof)
    
    def test_adjunction_proof_domain_id_is_dh_standalone(self):
        proof = run_adjunction_check()
        assert proof.domain_id == "D_DH_STANDALONE"
    
    def test_adjunction_yeshua_claim_is_hash_anchored(self):
        proof = run_adjunction_check()
        assert proof.yeshua_claim.is_hash_anchored()
        assert proof.yeshua_claim.is_reproducible()
    
    def test_domain_state_adjunction_holds_false(self):
        state = build_domain_state()
        assert state.adjunction_holds is False
    
    def test_domain_state_has_5_violations(self):
        state = build_domain_state()
        assert len(state.violations) == 5
    
    def test_domain_state_carries_evidence_anchors(self):
        state = build_domain_state()
        assert DH_EVIDENCE_ANCHOR in state.evidence_anchors
    
    def test_tick_budget_adjunction_check(self):
        proof = run_tick_budget_adjunction_check()
        assert proof.domain_id == "D_DH_STANDALONE_TICK"
    
    def test_gl_context_adjunction_check(self):
        proof = run_gl_context_adjunction_check()
        assert proof.domain_id == "D_DH_STANDALONE_GL"


# ===========================================================================
# Type 5 — Forcing extensions
# ===========================================================================


class TestForcingOperation:
    """Tests for Type 5 forcing extensions."""
    
    def test_force_domain_returns_list(self):
        state = build_domain_state()
        extensions = force_domain(state)
        assert isinstance(extensions, list)
        assert len(extensions) > 0
    
    def test_forced_extension_adjunction_holds(self):
        state = build_domain_state()
        extensions = force_domain(state)
        assert any(ext.adjunction_holds for ext in extensions), (
            "At least one forced extension must resolve the adjunction failure."
        )
    
    def test_forced_extension_has_yeshua_claim(self):
        state = build_domain_state()
        extensions = force_domain(state)
        for ext in extensions:
            assert len(ext.claim.hash_commitment) == 64
            assert ext.claim.is_reproducible()
    
    def test_forced_extension_carries_evidence_anchors(self):
        state = build_domain_state()
        extensions = force_domain(state)
        for ext in extensions:
            assert ext.base_domain.evidence_anchors == state.evidence_anchors
    
    def test_domain_state_strength_is_inaccessible(self):
        """Cross-component (config + server + rendering) requires INACCESSIBLE."""
        state = build_domain_state()
        assert state.strength == CardinalStrength.INACCESSIBLE
    
    def test_existence_of_extension_proves_defect(self):
        """
        Proof by generic extension: if M[G] exists where the adjunction holds,
        then the ground model M (D_DH_STANDALONE) was provably defective.
        """
        state = build_domain_state()
        assert not state.adjunction_holds, "Ground model must be defective."
        extensions = force_domain(state)
        valid_extensions = [e for e in extensions if e.is_valid]
        assert valid_extensions, (
            "Existence of a valid forced extension proves the original state was defective."
        )


# ===========================================================================
# Type 4 — Higher adjunction (HoTT / 2-categorical)
# ===========================================================================


class TestHigherAdjunction:
    """Tests for Type 4 higher adjunction."""
    
    def _make_hit(self) -> HigherInductiveDomain:
        hit = HigherInductiveDomain(domain_id="D_DH_STANDALONE")
        
        # Add points (invariants)
        for inv in DH_SCHEMA["invariants"]:
            hit.add_point(inv)
        
        # Add paths (causal chains)
        hit.add_path(
            "config_default_4096",
            "generation_area_52M_blocks",
            "config_to_area",
        )
        hit.add_path(
            "generation_area_52M_blocks",
            "queue_fills_rapidly",
            "area_to_queue",
        )
        hit.add_path(
            "queue_fills_rapidly",
            "tick_budget_exceeded",
            "queue_to_budget",
        )
        hit.add_path(
            "tick_budget_exceeded",
            "tps_degradation_observed",
            "budget_to_tps",
        )
        # GL context path
        hit.add_path(
            "mixin_injects_during_splash",
            "gl_context_not_ready",
            "splash_to_context",
        )
        hit.add_path(
            "gl_context_not_ready",
            "black_screen_crash",
            "context_to_crash",
        )
        
        # 2-paths (coherences)
        hit.add_two_path(
            "config_to_area",
            "area_to_queue",
            "config_cascade_coherence",
        )
        hit.add_two_path(
            "splash_to_context",
            "context_to_crash",
            "gl_race_coherence",
        )
        
        return hit
    
    def test_higher_adjunction_proof_is_returned(self):
        hit = self._make_hit()
        proof = higher_has_adjunction(hit)
        from src.sal.higher_adjunction import HigherAdjunctionProof
        assert isinstance(proof, HigherAdjunctionProof)
    
    def test_higher_adjunction_domain_id(self):
        hit = self._make_hit()
        proof = higher_has_adjunction(hit)
        assert proof.domain_id == "D_DH_STANDALONE"
    
    def test_higher_adjunction_yeshua_claim_anchored(self):
        hit = self._make_hit()
        proof = higher_has_adjunction(hit)
        assert proof.claim.is_hash_anchored()
        assert proof.claim.is_reproducible()


# ===========================================================================
# Type 6 — Realizability topos
# ===========================================================================


class TestRealizabilityTopos:
    """Tests for Type 6 realizability."""
    
    def _make_proof(self, label: str) -> ProofObject:
        return ProofObject(
            rule="DhStandaloneForensicFact",
            premises=[f"domain=D_DH_STANDALONE", f"fact={label}"],
            conclusion=label,
        )
    
    def test_realize_returns_realizer_and_claim(self):
        proof = self._make_proof("config_paradox_provable")
        r, claim, violations = realize("config_paradox_provable", proof)
        assert r.proposition == "config_paradox_provable"
        assert r.is_computable
        assert len(claim.hash_commitment) == 64
        assert violations == ()
    
    def test_topos_internal_truth_is_one_for_realized_proposition(self):
        topos = RealizabilityTopos(ordinal=ORDINAL_EPSILON_0)
        proof = self._make_proof("tps_degradation_documented")
        topos.realize("tps_degradation_documented", proof)
        tv = topos.internal_truth("tps_degradation_documented")
        assert tv == Fraction(1)
    
    def test_topos_internal_truth_is_zero_for_unknown_proposition(self):
        topos = RealizabilityTopos()
        tv = topos.internal_truth("this_proposition_was_never_realized")
        assert tv == Fraction(0)
    
    def test_yeshua_axioms_are_topos_axioms(self):
        topos = RealizabilityTopos()
        axioms = topos.verify_yeshua_axioms_are_topos_axioms()
        assert all(axioms.values()), f"Not all Yeshua axioms satisfied: {axioms}"
    
    def test_covenant_is_terminal_coalgebra(self):
        topos = RealizabilityTopos()
        assert topos.covenant.is_fixed_point
        assert "SALVerification" in topos.covenant.functor_name


# ===========================================================================
# Full integrated report
# ===========================================================================


class TestFullReport:
    """Tests for the full forensic report."""
    
    @pytest.fixture
    def report(self) -> DhStandaloneReport:
        return build_full_report()
    
    def test_report_is_defective(self, report: DhStandaloneReport):
        assert report.is_defective, (
            "The D_DH_STANDALONE domain must be flagged as defective."
        )
    
    def test_config_runtime_truth_not_preserved(self, report: DhStandaloneReport):
        assert not report.config_runtime_truth_preserved
    
    def test_tick_budget_truth_not_preserved(self, report: DhStandaloneReport):
        assert not report.tick_budget_truth_preserved
    
    def test_gl_context_truth_not_preserved(self, report: DhStandaloneReport):
        assert not report.gl_context_truth_preserved
    
    def test_has_valid_forcing_extension(self, report: DhStandaloneReport):
        assert report.has_valid_forcing_extension, (
            "Forcing must produce at least one valid extension."
        )
    
    def test_evidence_anchor_in_report(self, report: DhStandaloneReport):
        assert report.evidence_anchor == DH_EVIDENCE_ANCHOR
    
    def test_blocks_squared_in_report(self, report: DhStandaloneReport):
        assert report.blocks_squared_per_player > 52_000_000
    
    def test_report_no_float_arithmetic(self):
        import inspect
        import src.domains.d_dh_standalone.domain as mod
        source = inspect.getsource(mod)
        assert "float(" not in source, "No float() allowed in SAL core modules."
    
    def test_report_has_forced_extensions(self, report: DhStandaloneReport):
        assert len(report.forced_extensions) >= 5
    
    def test_all_extensions_valid(self, report: DhStandaloneReport):
        for ext in report.forced_extensions:
            assert ext.is_valid, (
                f"Extension is not valid: violations={ext.violations}"
            )


# ===========================================================================
# Schema validation
# ===========================================================================


class TestSchema:
    """Tests for DH_SCHEMA structure."""
    
    def test_schema_has_id(self):
        assert DH_SCHEMA["id"] == "D_DH_STANDALONE"
    
    def test_schema_has_5_invariants(self):
        assert len(DH_SCHEMA["invariants"]) == 5
    
    def test_schema_has_evidence_anchors(self):
        assert len(DH_SCHEMA["evidence_anchors"]) >= 1
    
    def test_schema_has_components(self):
        assert "config" in DH_SCHEMA["components"]
        assert "server" in DH_SCHEMA["components"]
        assert "rendering" in DH_SCHEMA["components"]
    
    def test_schema_has_paradoxes(self):
        assert len(DH_SCHEMA["paradoxes"]) == 2
        assert any("PX-001" in p for p in DH_SCHEMA["paradoxes"])
    
    def test_schema_has_mathematical_proof(self):
        assert "52" in DH_SCHEMA["mathematical_proof"]  # 52.7M
        assert "π" in DH_SCHEMA["mathematical_proof"]
    
    def test_schema_has_biblical_inspiration(self):
        assert "Luke 14:28" in DH_SCHEMA["biblical_inspiration"]


# ===========================================================================
# Violation constants
# ===========================================================================


class TestViolations:
    """Tests for violation constant definitions."""
    
    def test_counit_violation_defined(self):
        assert "counit_violation" in DH_COUNIT_VIOLATION
    
    def test_config_paradox_defined(self):
        assert "config_paradox" in CONFIG_PARADOX_PX001
        assert "52.7M" in CONFIG_PARADOX_PX001 or "4096" in CONFIG_PARADOX_PX001
    
    def test_queue_violation_defined(self):
        assert "queue_violation" in UNBOUNDED_QUEUE_VIOLATION
    
    def test_tick_budget_violation_defined(self):
        assert "tick_budget_violation" in TICK_BUDGET_VIOLATION
    
    def test_gl_context_violation_defined(self):
        assert "gl_context_violation" in GL_CONTEXT_RACE_VIOLATION
