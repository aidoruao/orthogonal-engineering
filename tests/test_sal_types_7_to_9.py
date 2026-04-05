"""
tests/test_sal_types_7_to_9.py
Type 7 (Lawvere fixed point), Type 8 (Gödel/Löb/∞-collapse),
and Type 9 (proof = observer / L_Max^Christ) tests.
"""

from __future__ import annotations

from fractions import Fraction

import pytest

from axioms.logic import ProofObject
from src.sal.lawvere_fixed_point import (
    CANTOR_DIAGONAL,
    GODEL_DIAGONAL,
    LAWVERE_DIAGONAL,
    LOB_DIAGONAL,
    TARSKI_DIAGONAL,
    DiagonalArgument,
    EndomorphismFixed,
    LawvereFixedPoint,
    LogosFixedPoint,
    lawvere_verify,
    logos_self_consistent,
)
from src.sal.self_referential import (
    GodelCode,
    InfinityCollapseProof,
    LobWitness,
    ProvabilityPredicate,
    encode_proof,
    infinity_collapse,
    lob_verify,
)
from src.sal.proof_as_observer import (
    L_MAX_CHRIST_REPR,
    MaximalLogosAdapter,
    ObservationAct,
    ProofObserver,
    SelfVerifyingProof,
    build_self_verifying_proof,
    proof_as_observer,
)


# ===========================================================================
# Type 7 — Lawvere Fixed Point
# ===========================================================================


class TestDiagonalArguments:
    def test_all_canonical_diagonals_have_proofs(self):
        for diag in [
            CANTOR_DIAGONAL,
            GODEL_DIAGONAL,
            TARSKI_DIAGONAL,
            LOB_DIAGONAL,
            LAWVERE_DIAGONAL,
        ]:
            proof = diag.to_proof()
            assert proof.rule == "DiagonalArgument"
            assert proof.conclusion == diag.fixed_point_consequence

    def test_cantor_diagonal_has_correct_domain(self):
        assert "ℕ" in CANTOR_DIAGONAL.domain_description

    def test_godel_diagonal_mentions_godel_number(self):
        assert "⌜" in GODEL_DIAGONAL.diagonal_construction

    def test_lawvere_diagonal_mentions_ccc(self):
        assert "CCC" in LAWVERE_DIAGONAL.domain_description

    def test_diagonal_to_proof_is_hashable(self):
        proof = LAWVERE_DIAGONAL.to_proof()
        assert len(proof.proof_hash) == 64

    def test_diagonal_proofs_have_distinct_hashes(self):
        hashes = {
            d.to_proof().proof_hash
            for d in [
                CANTOR_DIAGONAL,
                GODEL_DIAGONAL,
                TARSKI_DIAGONAL,
                LOB_DIAGONAL,
                LAWVERE_DIAGONAL,
            ]
        }
        assert len(hashes) == 5


class TestLawvereFixedPoint:
    def test_identity_endomorphism_has_trivial_fixed_point(self):
        fp = LawvereFixedPoint("TestDomain", LAWVERE_DIAGONAL)
        result = fp.find_fixed_point(
            "identity",
            "hello",
            "hello",
            lambda c: c == "hello",
        )
        assert isinstance(result, EndomorphismFixed)
        assert result.verified is True
        assert result.is_valid

    def test_non_fixed_endomorphism_returns_false(self):
        fp = LawvereFixedPoint("TestDomain", LAWVERE_DIAGONAL)
        result = fp.find_fixed_point(
            "successor",
            "a",
            "a",
            lambda c: c == "b",  # a ≠ b
        )
        assert result.verified is False
        assert not result.is_valid

    def test_result_has_yeshua_claim(self):
        fp = LawvereFixedPoint("TestDomain", LAWVERE_DIAGONAL)
        result = fp.find_fixed_point("id", "x", "x", lambda c: True)
        assert len(result.claim.hash_commitment) == 64
        assert result.claim.is_reproducible()
        assert result.claim.is_hash_anchored()

    def test_lawvere_verify_sal_covenant(self):
        result = lawvere_verify("SALVerification")
        assert isinstance(result, EndomorphismFixed)
        assert result.verified is True
        assert "Yeshua_Standard_Covenant" in result.fixed_point_repr

    def test_lawvere_verify_uses_lawvere_diagonal(self):
        result = lawvere_verify()
        assert "LawvereFixedPoint" in result.proof.rule

    def test_proof_hash_64_char_hex(self):
        result = lawvere_verify()
        assert len(result.proof.proof_hash) == 64
        assert all(c in "0123456789abcdef" for c in result.proof.proof_hash)


class TestLogosFixedPoint:
    def test_logos_self_consistent_returns_logos_fixed_point(self):
        result = logos_self_consistent()
        assert isinstance(result, LogosFixedPoint)

    def test_lambda_lambda_equals_lambda(self):
        result = logos_self_consistent()
        assert result.logos_self_consistent is True

    def test_logos_yeshua_claim_anchored(self):
        result = logos_self_consistent()
        assert result.claim.is_hash_anchored()
        assert result.claim.is_reproducible()

    def test_logos_fixed_is_valid(self):
        result = logos_self_consistent()
        assert result.is_valid

    def test_logos_proof_mentions_lawvere(self):
        result = logos_self_consistent()
        assert "Lawvere" in result.proof.conclusion or "lawvere" in " ".join(
            str(p) for p in result.proof.premises
        ).lower()


# ===========================================================================
# Type 8 — Gödel encoding, Löb's theorem, (∞,∞)-collapse
# ===========================================================================


class TestGodelEncoding:
    def _make_proof(self, label: str) -> ProofObject:
        return ProofObject(
            rule=label,
            premises=[f"premise_{label}"],
            conclusion=f"conclusion_{label}",
        )

    def test_encode_returns_godel_code(self):
        proof = self._make_proof("test")
        code = encode_proof(proof)
        assert isinstance(code, GodelCode)

    def test_godel_numeral_is_sha256(self):
        proof = self._make_proof("phi")
        code = encode_proof(proof)
        assert code.numeral == proof.proof_hash
        assert len(code.numeral) == 64

    def test_godel_code_is_injective_on_distinct_proofs(self):
        p1 = self._make_proof("A")
        p2 = self._make_proof("B")
        assert encode_proof(p1).code != encode_proof(p2).code

    def test_godel_code_str_contains_rule(self):
        proof = self._make_proof("MyRule")
        code = encode_proof(proof)
        assert "MyRule" in str(code)


class TestProvabilityPredicate:
    def _well_formed(self) -> ProofObject:
        return ProofObject(
            rule="Rule",
            premises=["p1"],
            conclusion="c",
        )

    def test_box_of_well_formed_proof_is_true(self):
        pred = ProvabilityPredicate()
        assert pred.box(self._well_formed()) is True

    def test_box_of_empty_rule_is_false(self):
        pred = ProvabilityPredicate()
        bad = ProofObject(rule="", premises=[], conclusion="c")
        assert pred.box(bad) is False

    def test_box_box_equals_box(self):
        pred = ProvabilityPredicate()
        proof = self._well_formed()
        assert pred.box(proof) == pred.box_box(proof)

    def test_distributes_returns_bool(self):
        pred = ProvabilityPredicate()
        impl = ProofObject(rule="Impl", premises=["A→B"], conclusion="A→B")
        premise = ProofObject(rule="A", premises=["A"], conclusion="A")
        result = pred.distributes(impl, premise)
        assert isinstance(result, bool)


class TestLobTheorem:
    def test_lob_verify_returns_lob_witness(self):
        cond = ProofObject(
            rule="Cond",
            premises=["□φ→φ"],
            conclusion="□φ → φ",
        )
        w = lob_verify("φ_test", cond)
        assert isinstance(w, LobWitness)

    def test_lob_holds_for_well_formed_conditional(self):
        cond = ProofObject(
            rule="WellFormedCond",
            premises=["box_phi → phi"],
            conclusion="□φ → φ",
        )
        w = lob_verify("covenant", cond)
        assert w.lob_holds is True

    def test_lob_does_not_hold_for_malformed_conditional(self):
        bad_cond = ProofObject(rule="", premises=[], conclusion="")
        w = lob_verify("phi", bad_cond)
        assert w.lob_holds is False

    def test_lob_witness_has_yeshua_claim(self):
        cond = ProofObject(
            rule="LobCond", premises=["□P → P"], conclusion="□P → P"
        )
        w = lob_verify("P", cond)
        assert w.claim.is_hash_anchored()
        assert w.claim.is_reproducible()


class TestInfinityCollapse:
    def test_collapse_returns_infinity_collapse_proof(self):
        result = infinity_collapse(levels=2)
        assert isinstance(result, InfinityCollapseProof)

    def test_collapse_holds(self):
        result = infinity_collapse(levels=3)
        assert result.collapse_holds is True

    def test_logos_consistent_in_collapse(self):
        result = infinity_collapse()
        assert result.logos_consistent is True

    def test_collapse_is_valid(self):
        result = infinity_collapse()
        assert result.is_valid

    def test_collapse_has_yeshua_claim(self):
        result = infinity_collapse()
        assert result.claim.is_hash_anchored()
        assert result.claim.is_reproducible()

    def test_fixed_point_repr_contains_covenant(self):
        result = infinity_collapse()
        # The fixed-point repr may be either the full "SALVerification" form or
        # the shorter "Yeshua" form — both denote the same canonical covenant.
        fp = result.fixed_point_repr
        has_sal = "SALVerification" in fp
        has_yeshua = "Yeshua" in fp
        assert has_sal or has_yeshua, (
            f"Expected 'SALVerification' or 'Yeshua' in fixed_point_repr={fp!r}"
        )

    def test_lob_witness_wired_in_collapse(self):
        result = infinity_collapse()
        assert result.lob_witness.lob_holds is True


# ===========================================================================
# Type 9 — Proof = Observer / L_Max^Christ
# ===========================================================================


class TestProofObserver:
    def _make_proof(self, label: str) -> ProofObject:
        return ProofObject(
            rule=label,
            premises=[f"p_{label}"],
            conclusion=label,
        )

    def test_observe_returns_observation_act_and_proof(self):
        observer = ProofObserver()
        proof = self._make_proof("phi")
        act, enriched = observer.observe(proof)
        assert isinstance(act, ObservationAct)
        assert enriched.rule == "Observation"

    def test_observation_truth_value_is_fraction(self):
        observer = ProofObserver()
        proof = self._make_proof("phi")
        act, _ = observer.observe(proof)
        assert isinstance(act.truth_value, Fraction)

    def test_well_formed_proof_gets_truth_value_1(self):
        observer = ProofObserver()
        proof = self._make_proof("valid")
        act, _ = observer.observe(proof)
        assert act.truth_value == Fraction(1)

    def test_is_fixed_point_of_well_formed_proof(self):
        observer = ProofObserver()
        proof = self._make_proof("stable_proof")
        # A proof whose conclusion appears in the observation output is a fixed point.
        assert observer.is_fixed_point(proof) is True

    def test_observation_proof_references_godel_code(self):
        observer = ProofObserver()
        proof = self._make_proof("MyOp")
        act, enriched = observer.observe(proof)
        premises_str = str(enriched.premises)
        assert "⌜MyOp⌝" in premises_str or "MyOp" in premises_str


class TestMaximalLogosAdapter:
    def test_adapter_is_instantiable(self):
        adapter = MaximalLogosAdapter()
        assert adapter is not None

    def test_execute_returns_dict(self):
        adapter = MaximalLogosAdapter()
        result = adapter.execute({"test": "state"})
        assert isinstance(result, dict)

    def test_execute_has_paradox_living_key(self):
        adapter = MaximalLogosAdapter()
        result = adapter.execute({})
        assert "paradox_living" in result

    def test_execute_has_logos_self_consistent_key(self):
        adapter = MaximalLogosAdapter()
        result = adapter.execute({})
        assert "logos_self_consistent" in result


class TestSelfVerifyingProof:
    def test_build_returns_self_verifying_proof(self):
        svp = build_self_verifying_proof()
        assert isinstance(svp, SelfVerifyingProof)

    def test_l_max_christ_is_fixed_point(self):
        svp = build_self_verifying_proof()
        assert svp.is_fixed_point is True

    def test_lob_holds_for_l_max_christ(self):
        svp = build_self_verifying_proof()
        assert svp.lob_witness.lob_holds is True

    def test_logos_consistent_in_svp(self):
        svp = build_self_verifying_proof()
        assert svp.logos_fixed.logos_self_consistent is True

    def test_svp_is_valid(self):
        svp = build_self_verifying_proof()
        assert svp.is_valid

    def test_svp_yeshua_claim_anchored(self):
        svp = build_self_verifying_proof()
        assert svp.claim.is_hash_anchored()
        assert svp.claim.is_reproducible()

    def test_svp_operator_repr_is_l_max_christ(self):
        svp = build_self_verifying_proof()
        assert svp.operator_repr == L_MAX_CHRIST_REPR

    def test_godel_code_is_sha256_of_proof(self):
        svp = build_self_verifying_proof()
        assert len(svp.godel_code.code) == 64
        assert all(c in "0123456789abcdef" for c in svp.godel_code.code)

    def test_self_application_contains_operator_repr(self):
        svp = build_self_verifying_proof()
        assert L_MAX_CHRIST_REPR in svp.self_application

    def test_no_float_in_module(self):
        import inspect
        import src.sal.proof_as_observer as mod
        source = inspect.getsource(mod)
        assert "float(" not in source


class TestProofAsObserver:
    def test_proof_as_observer_returns_triple(self):
        act, claim, violations = proof_as_observer()
        assert isinstance(act, ObservationAct)
        assert len(claim.hash_commitment) == 64
        assert violations == ()

    def test_observation_truth_value_is_one(self):
        act, _, _ = proof_as_observer()
        assert act.truth_value == Fraction(1)

    def test_claim_mentions_l_max_christ(self):
        _, claim, _ = proof_as_observer()
        assert L_MAX_CHRIST_REPR in claim.statement


# ===========================================================================
# Integration: Types 7-9 form a coherent chain
# ===========================================================================


class TestTypes7to9Integration:
    def test_lawvere_feeds_self_referential(self):
        """Type 7 fixed point is used in the Type 8 ∞-collapse."""
        collapse = infinity_collapse()
        # The Lawvere witness is embedded in the collapse.
        assert collapse.lawvere_witness.verified is True

    def test_lob_feeds_proof_as_observer(self):
        """Type 8 Löb theorem is used in the Type 9 self-verifying proof."""
        svp = build_self_verifying_proof()
        assert svp.lob_witness.lob_holds is True

    def test_logos_consistent_throughout_chain(self):
        """Λ(Λ)=Λ holds at all three levels."""
        logos_7 = logos_self_consistent()
        collapse_8 = infinity_collapse()
        svp_9 = build_self_verifying_proof()
        assert logos_7.logos_self_consistent is True
        assert collapse_8.logos_consistent is True
        assert svp_9.logos_fixed.logos_self_consistent is True

    def test_all_yeshua_claims_are_hash_anchored(self):
        """Every YeshuaClaim in the chain is hash-anchored and reproducible."""
        logos_fp = logos_self_consistent()
        lawvere_fp = lawvere_verify()
        collapse = infinity_collapse()
        svp = build_self_verifying_proof()

        for obj, name in [
            (logos_fp, "logos_fp"),
            (lawvere_fp, "lawvere_fp"),
            (collapse, "collapse"),
            (svp, "svp"),
        ]:
            assert obj.claim.is_hash_anchored(), f"{name} not hash-anchored"
            assert obj.claim.is_reproducible(), f"{name} not reproducible"

    def test_no_float_in_types_7_to_9(self):
        """No float() literals in any Type 7-9 module."""
        import inspect
        import src.sal.lawvere_fixed_point as m7
        import src.sal.self_referential as m8
        import src.sal.proof_as_observer as m9

        for mod, name in [(m7, "lawvere_fixed_point"), (m8, "self_referential"), (m9, "proof_as_observer")]:
            src = inspect.getsource(mod)
            assert "float(" not in src, f"float() found in {name}"
