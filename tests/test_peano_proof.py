"""
Tests for Peano Kernel proof objects — tests/test_peano_proof.py

Validates that PeanoProof, PeanoNat, and proof-producing arithmetic functions
behave correctly and produce auditable derivations.

Author: Orthogonal Engineering
PR: #32
Version: 1.0.0
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from oe_ifm.peano_kernel import (
    PeanoNat,
    PeanoProof,
    peano_add_proof,
    peano_mul_proof,
    predecessor_proof,
    proof_add,
    successor_proof,
)


# ---------------------------------------------------------------------------
# PeanoProof integrity
# ---------------------------------------------------------------------------


def test_proof_has_value():
    """PeanoProof carries the computed integer value."""
    proof = peano_add_proof(3, 5)
    assert proof.value == 8


def test_proof_has_steps():
    """PeanoProof carries a non-empty derivation step list."""
    proof = peano_add_proof(2, 4)
    assert isinstance(proof.steps, list)
    assert len(proof.steps) >= 1


def test_proof_has_hash():
    """PeanoProof carries a 64-char hex SHA-256 proof_hash."""
    proof = peano_add_proof(1, 1)
    assert isinstance(proof.proof_hash, str)
    assert len(proof.proof_hash) == 64


def test_proof_is_valid():
    """PeanoProof.is_valid() returns True for an untampered proof."""
    proof = peano_add_proof(7, 3)
    assert proof.is_valid()


def test_proof_invalid_after_tampering():
    """PeanoProof.is_valid() returns False after steps are modified."""
    proof = peano_add_proof(4, 6)
    proof.steps.append("tampered step")
    assert not proof.is_valid()


def test_proof_serialise_round_trip():
    """PeanoProof.to_dict() / from_dict() round-trips correctly."""
    proof = peano_add_proof(5, 7)
    d = proof.to_dict()
    restored = PeanoProof.from_dict(d)
    assert restored.value == proof.value
    assert restored.proof_hash == proof.proof_hash
    assert restored.is_valid()


def test_proof_int_equality():
    """PeanoProof == int compares by value."""
    proof = peano_add_proof(3, 4)
    assert proof == 7
    assert int(proof) == 7


# ---------------------------------------------------------------------------
# Arithmetic proof functions
# ---------------------------------------------------------------------------


def test_successor_proof():
    """successor_proof(n) returns PeanoProof with value n+1."""
    for n in [0, 1, 9, 99]:
        proof = successor_proof(n)
        assert proof.value == n + 1
        assert proof.is_valid()


def test_predecessor_proof():
    """predecessor_proof(n) returns PeanoProof with value n-1."""
    for n in [1, 2, 10, 100]:
        proof = predecessor_proof(n)
        assert proof.value == n - 1
        assert proof.is_valid()


def test_peano_add_proof_zero():
    """peano_add_proof(a, 0) == a (additive identity)."""
    for a in [0, 1, 42, 100]:
        proof = peano_add_proof(a, 0)
        assert proof.value == a
        assert proof.is_valid()


def test_peano_add_proof_commutativity():
    """peano_add_proof(a, b).value == peano_add_proof(b, a).value."""
    pairs = [(0, 0), (1, 2), (5, 7), (10, 20)]
    for a, b in pairs:
        assert peano_add_proof(a, b).value == peano_add_proof(b, a).value


def test_peano_add_proof_negative_b_raises():
    """peano_add_proof with negative b raises ValueError."""
    with pytest.raises(ValueError):
        peano_add_proof(5, -1)


def test_peano_mul_proof_zero():
    """peano_mul_proof(a, 0) == 0."""
    for a in [0, 1, 7, 42]:
        proof = peano_mul_proof(a, 0)
        assert proof.value == 0
        assert proof.is_valid()


def test_peano_mul_proof_one():
    """peano_mul_proof(a, 1) == a."""
    for a in [0, 1, 5, 13]:
        proof = peano_mul_proof(a, 1)
        assert proof.value == a
        assert proof.is_valid()


def test_peano_mul_proof_correctness():
    """peano_mul_proof(a, b).value == a * b."""
    pairs = [(2, 3), (4, 5), (7, 8), (0, 9)]
    for a, b in pairs:
        proof = peano_mul_proof(a, b)
        assert proof.value == a * b
        assert proof.is_valid()


def test_proof_add_chains():
    """proof_add combines two proofs and returns correct value."""
    p1 = peano_add_proof(3, 2)   # = 5
    p2 = peano_add_proof(1, 4)   # = 5
    combined = proof_add(p1, p2)  # = 10
    assert combined.value == 10
    assert combined.is_valid()
    assert len(combined.steps) > len(p1.steps) + len(p2.steps)


# ---------------------------------------------------------------------------
# PeanoNat wrapper
# ---------------------------------------------------------------------------


def test_peano_nat_basic():
    """PeanoNat wraps a non-negative integer."""
    n = PeanoNat(7)
    assert n.value == 7
    assert int(n) == 7


def test_peano_nat_negative_raises():
    """PeanoNat rejects negative integers."""
    with pytest.raises(ValueError):
        PeanoNat(-1)


def test_peano_nat_add_returns_proof():
    """PeanoNat + PeanoNat returns a PeanoProof."""
    a = PeanoNat(3)
    b = PeanoNat(5)
    result = a + b
    assert isinstance(result, PeanoProof)
    assert result.value == 8
    assert result.is_valid()


def test_peano_nat_add_int():
    """PeanoNat + int returns a PeanoProof."""
    a = PeanoNat(4)
    result = a + 6
    assert result.value == 10


def test_peano_nat_mul_returns_proof():
    """PeanoNat * PeanoNat returns a PeanoProof."""
    a = PeanoNat(3)
    b = PeanoNat(4)
    result = a * b
    assert isinstance(result, PeanoProof)
    assert result.value == 12
    assert result.is_valid()


def test_peano_nat_successor():
    """PeanoNat.successor() returns PeanoProof with value + 1."""
    n = PeanoNat(9)
    proof = n.successor()
    assert proof.value == 10
    assert proof.is_valid()


def test_peano_nat_predecessor():
    """PeanoNat.predecessor() returns PeanoProof with value - 1."""
    n = PeanoNat(5)
    proof = n.predecessor()
    assert proof.value == 4
    assert proof.is_valid()


def test_peano_nat_equality():
    """PeanoNat equality works against int and other PeanoNat."""
    assert PeanoNat(5) == PeanoNat(5)
    assert PeanoNat(5) == 5
    assert PeanoNat(5) != PeanoNat(6)


# ---------------------------------------------------------------------------
# Determinism — same inputs always produce same proof hash
# ---------------------------------------------------------------------------


def test_proof_deterministic():
    """Same inputs always produce the same proof hash."""
    h1 = peano_add_proof(10, 20).proof_hash
    h2 = peano_add_proof(10, 20).proof_hash
    assert h1 == h2


def test_different_inputs_different_hash():
    """Different inputs produce different proof hashes."""
    h1 = peano_add_proof(10, 20).proof_hash
    h2 = peano_add_proof(10, 21).proof_hash
    assert h1 != h2
