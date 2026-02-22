"""
tests/test_axioms.py — Tests for the Foundational Axiom Layer

Validates axioms/peano.py, axioms/logic.py, axioms/yeshua_axioms.py

Author: Orthogonal Engineering
PR: #34
Version: 1.0.0
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from axioms.peano import (
    ZERO,
    peano_add,
    peano_mul,
    predecessor,
    successor,
    verify_p1,
    verify_p2,
    verify_p3,
    verify_p4,
    verify_p5_schema,
    proof_hash,
    proof_to_bytes,
    PeanoNat,
    PeanoProof,
)
from axioms.logic import (
    ProofObject,
    induction_rule,
    merkle_root_over_proofs,
    modus_ponens,
    universal_instantiation,
)
from axioms.yeshua_axioms import (
    YESHUA_AXIOMS,
    YeshuaClaim,
    YeshuaViolation,
    verify_yeshua_standard,
)

# ---------------------------------------------------------------------------
# Peano axioms
# ---------------------------------------------------------------------------


def test_p1_zero_is_natural():
    assert verify_p1() is True


def test_p2_successor_is_natural():
    for n in range(20):
        assert verify_p2(n) is True


def test_p3_successor_not_zero():
    for n in range(20):
        assert verify_p3(n) is True


def test_p4_successor_injectivity():
    for m in range(10):
        for n in range(10):
            assert verify_p4(m, n) is True


def test_p5_induction_schema():
    passed, cexs = verify_p5_schema(
        base_case=True,
        inductive_step_fn=lambda n: peano_add(n, 1) == n + 1,
        limit=100,
    )
    assert passed is True
    assert cexs == []


def test_p5_induction_base_fails():
    passed, cexs = verify_p5_schema(
        base_case=False,
        inductive_step_fn=lambda n: True,
    )
    assert passed is False
    assert len(cexs) == 1


def test_peano_add_commutative():
    for a in range(10):
        for b in range(10):
            assert peano_add(a, b) == peano_add(b, a)


def test_peano_mul_correct():
    assert peano_mul(0, 5) == 0
    assert peano_mul(3, 4) == 12
    assert peano_mul(7, 7) == 49


def test_proof_hash_64_chars():
    nat = PeanoNat(5)
    proof = nat + PeanoNat(3)
    assert len(proof_hash(proof)) == 64


def test_proof_to_bytes_is_bytes():
    nat = PeanoNat(2)
    proof = nat + PeanoNat(2)
    assert isinstance(proof_to_bytes(proof), bytes)


# ---------------------------------------------------------------------------
# Logic layer
# ---------------------------------------------------------------------------


def test_proof_object_valid():
    p = ProofObject("Axiom", ["P1: 0 is natural"], "Zero exists")
    assert p.is_valid() is True


def test_proof_object_equality():
    p1 = ProofObject("Axiom", ["P1"], "Zero")
    p2 = ProofObject("Axiom", ["P1"], "Zero")
    assert p1 == p2


def test_modus_ponens_true():
    result, proof = modus_ponens(True, True)
    assert result is True
    assert proof.is_valid()


def test_modus_ponens_false_antecedent():
    result, proof = modus_ponens(False, True)
    assert result is False


def test_universal_instantiation():
    result, proof = universal_instantiation(lambda x: x >= 0, 5)
    assert result is True
    assert proof.is_valid()


def test_induction_rule_passes():
    passed, proof = induction_rule(
        base_predicate=True,
        inductive_fn=lambda n: peano_add(n, 0) == n,
        limit=50,
    )
    assert passed is True
    assert proof.is_valid()


def test_induction_rule_fails_base():
    passed, proof = induction_rule(
        base_predicate=False,
        inductive_fn=lambda n: True,
        limit=50,
    )
    assert passed is False


def test_merkle_root_empty():
    root = merkle_root_over_proofs([])
    assert len(root) == 64


def test_merkle_root_deterministic():
    proofs = [
        ProofObject("Axiom", ["P1"], "A"),
        ProofObject("Rule", ["P2"], "B"),
    ]
    r1 = merkle_root_over_proofs(proofs)
    r2 = merkle_root_over_proofs(proofs)
    assert r1 == r2


def test_merkle_root_stable_across_order():
    p1 = ProofObject("A", [], "conclusion-a")
    p2 = ProofObject("B", [], "conclusion-b")
    r1 = merkle_root_over_proofs([p1, p2])
    r2 = merkle_root_over_proofs([p2, p1])
    assert r1 == r2  # sorted by hash


# ---------------------------------------------------------------------------
# Yeshua axioms
# ---------------------------------------------------------------------------


def test_yeshua_axioms_dict_has_eight():
    assert len(YESHUA_AXIOMS) == 8
    for i in range(1, 9):
        assert i in YESHUA_AXIOMS


def test_yeshua_claim_valid():
    proof = ProofObject("Axiom", ["P1"], "Zero exists")
    claim = YeshuaClaim(
        source="axioms/peano.py",
        statement="Zero is the additive identity",
        derivation=proof,
    )
    violations = verify_yeshua_standard(claim)
    assert violations == []


def test_yeshua_claim_empty_source_violates_axiom4():
    proof = ProofObject("Axiom", ["P1"], "Zero")
    claim = YeshuaClaim(source="", statement="Something", derivation=proof)
    violations = verify_yeshua_standard(claim)
    axiom_numbers = [v.axiom_number for v in violations]
    assert 4 in axiom_numbers


def test_yeshua_claim_is_reproducible():
    proof = ProofObject("Test", ["premise"], "conclusion")
    claim = YeshuaClaim("test.py", "Some claim", proof)
    assert claim.is_reproducible() is True


def test_yeshua_claim_is_hash_anchored():
    proof = ProofObject("Test", ["premise"], "conclusion")
    claim = YeshuaClaim("test.py", "Some claim", proof)
    assert claim.is_hash_anchored() is True


def test_yeshua_monetization_violates_axiom7():
    proof = ProofObject("Axiom", ["P1"], "Zero")
    claim = YeshuaClaim(
        source="test.py",
        statement="This requires a paywall subscription",
        derivation=proof,
    )
    violations = verify_yeshua_standard(claim)
    axiom_numbers = [v.axiom_number for v in violations]
    assert 7 in axiom_numbers
