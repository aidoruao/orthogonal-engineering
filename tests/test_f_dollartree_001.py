"""
tests/test_f_dollartree_001.py
D_DOLLARTREE forensic domain tests — Type 3+ through Type 6 validation.

These tests assert that:
  1. The geometric morphism between the officer's situs and the video-evidence
     situs does NOT preserve truth (Type 3+ — topos truth divergence).
  2. The adjunction check for the contradicted schema is structurally valid
     (the SAL kernel shapes are correct) but the domain state records violations
     (Type 3 — counit failure at the semantic level).
  3. ForcingOperation produces at least one valid generic extension (Type 5 —
     existence of the forced branch proves the original state was defective).
  4. RealizabilityTopos can realize the paradox statement and all 8 Yeshua
     axioms hold in the effective topos (Type 6).
  5. The evidence anchor (SHA-256 of the YouTube URL) is correctly computed
     and matches the expected value (Yeshua Axiom 8).
"""

from __future__ import annotations

import hashlib
from fractions import Fraction

import pytest

from src.domains.d_dollartree.domain import (
    EVIDENCE_URL_SHORT,
    EVIDENCE_ANCHOR_SHA256,
    DOLLARTREE_SCHEMA,
    DOLLARTREE_COUNIT_VIOLATION,
    build_officer_situs,
    build_video_situs,
    build_domain_state,
    evaluate_topos_truth_gap,
    run_adjunction_check,
    build_full_report,
    DollarTreeReport,
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
    def test_anchor_is_64_char_hex_sha256(self):
        assert len(EVIDENCE_ANCHOR_SHA256) == 64
        assert all(c in "0123456789abcdef" for c in EVIDENCE_ANCHOR_SHA256)

    def test_anchor_matches_url_sha256(self):
        expected = hashlib.sha256(EVIDENCE_URL_SHORT.encode("utf-8")).hexdigest()
        assert EVIDENCE_ANCHOR_SHA256 == expected

    def test_anchor_is_deterministic(self):
        a = hashlib.sha256(EVIDENCE_URL_SHORT.encode("utf-8")).hexdigest()
        b = hashlib.sha256(EVIDENCE_URL_SHORT.encode("utf-8")).hexdigest()
        assert a == b

    def test_schema_carries_evidence_anchor(self):
        assert EVIDENCE_ANCHOR_SHA256 in DOLLARTREE_SCHEMA["evidence_anchors"]


# ===========================================================================
# Type 3+ — Topos truth divergence
# ===========================================================================


class TestToposTruthDivergence:
    def test_officer_situs_has_lawful_detention_object(self):
        ctx = build_officer_situs()
        assert "lawful_detention" in ctx.objects

    def test_video_situs_has_contradictory_order_object(self):
        ctx = build_video_situs()
        assert "contradictory_order" in ctx.objects

    def test_geometric_morphism_truth_not_preserved(self):
        """The geometric morphism between the two sites must NOT preserve truth."""
        morphism = evaluate_topos_truth_gap()
        assert morphism.truth_preserved is False, (
            "Expected truth_preserved=False: the officer situs and video situs "
            "disagree on 'lawful_detention'."
        )

    def test_geometric_morphism_has_yeshua_claim(self):
        morphism = evaluate_topos_truth_gap()
        assert len(morphism.claim.hash_commitment) == 64
        assert morphism.claim.is_reproducible()
        assert morphism.claim.is_hash_anchored()

    def test_geometric_morphism_proof_cites_sites(self):
        morphism = evaluate_topos_truth_gap()
        premises_str = str(morphism.proof.premises)
        assert "Ω_officer" in premises_str
        assert "Ω_video" in premises_str

    def test_subobject_classifier_uses_fraction_not_float(self):
        ctx = build_officer_situs()
        cls = SubobjectClassifier(ctx)
        tv = cls.evaluate("lawful_detention", "lawful_detention")
        assert isinstance(tv, Fraction), f"Expected Fraction, got {type(tv)}"

    def test_heyting_meet_fraction_values(self):
        p = Fraction(1)
        q = Fraction(0)
        assert SubobjectClassifier.meet(p, q) == Fraction(0)
        assert SubobjectClassifier.meet(p, p) == Fraction(1)

    def test_heyting_implies_fraction_values(self):
        # p ⇒ q when p ≤ q
        assert SubobjectClassifier.heyting_implies(Fraction(0), Fraction(1)) == Fraction(1)
        # p ⇒ q = q when p > q
        result = SubobjectClassifier.heyting_implies(Fraction(1), Fraction(0))
        assert result == Fraction(0)


# ===========================================================================
# Type 3 — SAL adjunction check (counit / unit)
# ===========================================================================


class TestSALAdjunctionCheck:
    def test_adjunction_check_returns_adjunction_proof(self):
        proof = run_adjunction_check()
        from src.sal.adjoint_triple import AdjunctionProof
        assert isinstance(proof, AdjunctionProof)

    def test_adjunction_proof_domain_id_is_dollartree(self):
        proof = run_adjunction_check()
        assert proof.domain_id == "D_DOLLARTREE"

    def test_adjunction_yeshua_claim_is_hash_anchored(self):
        proof = run_adjunction_check()
        assert proof.yeshua_claim.is_hash_anchored()
        assert proof.yeshua_claim.is_reproducible()

    def test_domain_state_adjunction_holds_false(self):
        state = build_domain_state()
        assert state.adjunction_holds is False

    def test_domain_state_has_violations(self):
        state = build_domain_state()
        assert len(state.violations) > 0

    def test_domain_state_carries_evidence_anchors(self):
        state = build_domain_state()
        assert EVIDENCE_ANCHOR_SHA256 in state.evidence_anchors


# ===========================================================================
# Type 5 — Forcing extensions
# ===========================================================================


class TestForcingOperation:
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

    def test_forced_extension_strength_at_least_predicative(self):
        state = build_domain_state()
        extensions = force_domain(state)
        for ext in extensions:
            assert ext.strength_used >= CardinalStrength.PEANO

    def test_trivial_extension_for_healthy_domain(self):
        healthy = DomainState(
            domain_id="D_HEALTHY",
            invariants=["all_good"],
            adjunction_holds=True,
            violations=[],
            strength=CardinalStrength.PEANO,
        )
        extensions = force_domain(healthy)
        assert len(extensions) == 1
        assert extensions[0].adjunction_holds is True
        assert extensions[0].conditions == ()

    def test_existence_of_extension_proves_defect(self):
        """
        Proof by generic extension: if M[G] exists where the adjunction holds,
        then the ground model M (D_DOLLARTREE) was provably defective.
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
    def _make_hit(self) -> HigherInductiveDomain:
        hit = HigherInductiveDomain(domain_id="D_DOLLARTREE")
        for inv in DOLLARTREE_SCHEMA["invariants"]:
            hit.add_point(inv)
        hit.add_path(
            "officer_ordered_leave",
            "officer_blocked_exit",
            "contradictory_path",
        )
        hit.add_two_path(
            "contradictory_path",
            "refl_lawful_state",
            "paradox_coherence",
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
        assert proof.domain_id == "D_DOLLARTREE"

    def test_higher_adjunction_yeshua_claim_anchored(self):
        hit = self._make_hit()
        proof = higher_has_adjunction(hit)
        assert proof.claim.is_hash_anchored()
        assert proof.claim.is_reproducible()

    def test_identity_path_refl(self):
        p = IdentityPath.refl("lawful_state")
        assert p.is_refl
        assert p.left == p.right

    def test_identity_path_j_elim_computes_on_refl(self):
        p = IdentityPath.refl(42)
        result = p.j_elim("P", "base_value")
        assert result == "base_value"

    def test_transport_on_refl_is_identity(self):
        p = IdentityPath.refl("lawful")
        t = Transport(path=p, transported_value="evidence", family_name="P")
        assert t.result == "evidence"

    def test_higher_inductive_domain_schema_conversion(self):
        hit = self._make_hit()
        schema = hit.to_schema()
        assert schema["id"] == "D_DOLLARTREE"
        assert len(schema["invariants"]) == len(DOLLARTREE_SCHEMA["invariants"])
        assert len(schema["paths"]) == 1
        assert schema["paths"][0]["label"] == "contradictory_path"


# ===========================================================================
# Type 6 — Realizability topos
# ===========================================================================


class TestRealizabilityTopos:
    def _make_proof(self, label: str) -> ProofObject:
        return ProofObject(
            rule="DollarTreeForensicFact",
            premises=[f"incident=D_DOLLARTREE", f"fact={label}"],
            conclusion=label,
        )

    def test_realize_returns_realizer_and_claim(self):
        proof = self._make_proof("paradox_is_provably_defective")
        r, claim, violations = realize("paradox_is_provably_defective", proof)
        assert r.proposition == "paradox_is_provably_defective"
        assert r.is_computable
        assert len(claim.hash_commitment) == 64
        assert violations == ()

    def test_topos_internal_truth_is_one_for_realized_proposition(self):
        topos = RealizabilityTopos(ordinal=ORDINAL_EPSILON_0)
        proof = self._make_proof("unlawful_detention_documented")
        topos.realize("unlawful_detention_documented", proof)
        tv = topos.internal_truth("unlawful_detention_documented")
        assert tv == Fraction(1)

    def test_topos_internal_truth_is_zero_for_unknown_proposition(self):
        topos = RealizabilityTopos()
        tv = topos.internal_truth("this_proposition_was_never_realized")
        assert tv == Fraction(0)

    def test_yeshua_axioms_are_topos_axioms(self):
        topos = RealizabilityTopos()
        axioms = topos.verify_yeshua_axioms_are_topos_axioms()
        assert all(axioms.values()), f"Not all Yeshua axioms satisfied in Eff: {axioms}"

    def test_covenant_is_terminal_coalgebra(self):
        topos = RealizabilityTopos()
        assert topos.covenant.is_fixed_point
        assert "SALVerification" in topos.covenant.functor_name

    def test_ordinal_epsilon_0_less_than_gamma_0(self):
        assert ORDINAL_EPSILON_0 < ORDINAL_GAMMA_0

    def test_realizer_compute_without_witness_fn_returns_conclusion(self):
        proof = self._make_proof("my_conclusion")
        r, _, _ = realize("my_conclusion", proof)
        assert r.compute() == "my_conclusion"


# ===========================================================================
# Full integrated report
# ===========================================================================


class TestFullReport:
    @pytest.fixture
    def report(self) -> DollarTreeReport:
        return build_full_report()

    def test_report_is_defective(self, report: DollarTreeReport):
        assert report.is_defective, (
            "The D_DOLLARTREE incident must be flagged as defective."
        )

    def test_topos_truth_not_preserved(self, report: DollarTreeReport):
        assert not report.topos_truth_preserved

    def test_has_valid_forcing_extension(self, report: DollarTreeReport):
        assert report.has_valid_forcing_extension, (
            "Forcing must produce at least one valid extension."
        )

    def test_evidence_anchor_in_report(self, report: DollarTreeReport):
        assert report.evidence_anchor == EVIDENCE_ANCHOR_SHA256

    def test_report_no_float_arithmetic(self):
        import inspect
        import src.domains.d_dollartree.domain as mod
        source = inspect.getsource(mod)
        assert "float(" not in source, "No float() allowed in SAL core modules."
