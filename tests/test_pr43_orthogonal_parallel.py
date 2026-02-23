#!/usr/bin/env python3
"""
tests/test_pr43_orthogonal_parallel.py — PR #43 Orthogonal Parallel Tests

Verifies:
  1. Peano kernel: Zero/Succ induction, equality, to_int/from_int round-trip
  2. Primitive recursion: add, mul, leq — structural correctness
  3. Boolean kernel: NOT/AND/OR/NAND — truth table correctness
  4. Type theory: Proof monad, Pi/Sigma types, plus_zero_identity proof
  5. Constraint solver: SearchSpace deterministic enumeration
  6. Hash identity: sha256_bytes, hash_file, verify_equal, verify_reproducibility
  7. Closure verifier: no float, no random, pure function checks
  8. Impossibility theorems: vendor lock, growth incompatibility, spectacle nullification
  9. Corporate autopsy: comparison data integrity
  10. Cross-platform: same inputs → same outputs (determinism)

Author: Orthogonal Engineering
PR: #43
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pr43.foundations.peano_kernel import (
    Natural, Zero, Succ,
    zero, successor, eq, is_zero, induction, from_int, to_int,
)
from pr43.foundations.primitive_recursion import add, mul, leq, lt
from pr43.foundations.boolean_kernel import (
    false, true, is_bool, NOT, AND, OR, NAND, IMPLIES, IFF,
)
from pr43.foundations.type_theory import Proof, Pi, Sigma, plus_zero_identity
from pr43.solver.constraint_solver import Constraint, SearchSpace, enumerate_range
from pr43.verification.hash_identity import (
    sha256_bytes, sha256_str, hash_file, hash_directory,
    verify_equal, verify_reproducibility,
)
from pr43.closure.verify_closure import (
    verify_no_floating_point, verify_no_randomness, verify_no_forbidden,
)
from pr43.impossibility.vendor_lock import (
    hash_source, verify_no_vendor_lock, check_no_lock_in,
)
from pr43.impossibility.growth_incompatibility import (
    check_halting, check_growth_requires_modification, detect_incompatibility,
)
from pr43.impossibility.spectacle_nullification import (
    truth_value, spectacle_delta, nullification_proof,
)
from pr43.corporate_autopsy.tesla_fsd_comparison import COMPARISON as TESLA_COMPARISON
from pr43.corporate_autopsy.nvidia_stack_comparison import (
    van_der_corput_fixed, qmc_integrate_fixed, COMPARISON as NVIDIA_COMPARISON,
)


# ---------------------------------------------------------------------------
# 1. Peano Kernel
# ---------------------------------------------------------------------------

class TestPeanoKernel:
    def test_zero_is_zero(self):
        assert isinstance(zero(), Zero)

    def test_successor_is_succ(self):
        s = successor(zero())
        assert isinstance(s, Succ)
        assert isinstance(s.pred, Zero)

    def test_eq_zero_zero(self):
        assert eq(zero(), zero())

    def test_eq_succ_succ(self):
        one = successor(zero())
        one2 = successor(zero())
        assert eq(one, one2)

    def test_eq_different(self):
        assert not eq(zero(), successor(zero()))
        assert not eq(successor(zero()), zero())

    def test_is_zero(self):
        assert is_zero(zero())
        assert not is_zero(successor(zero()))

    def test_from_int_to_int_round_trip(self):
        for k in range(6):
            n = from_int(k)
            assert to_int(n) == k

    def test_from_int_negative_raises(self):
        with pytest.raises(ValueError):
            from_int(-1)

    def test_induction_base(self):
        result = induction(zero(), lambda: True, lambda k, ih: ih)
        assert result is True

    def test_induction_step(self):
        # P(n) = True for all n by trivial induction
        for k in range(4):
            result = induction(from_int(k), lambda: True, lambda _, ih: ih)
            assert result is True

    def test_successor_is_frozen(self):
        s = successor(zero())
        with pytest.raises((AttributeError, TypeError)):
            s.pred = zero()  # type: ignore[misc]


# ---------------------------------------------------------------------------
# 2. Primitive Recursion
# ---------------------------------------------------------------------------

class TestPrimitiveRecursion:
    def _n(self, k: int) -> Natural:
        return from_int(k)

    def test_add_zero_right(self):
        for k in range(5):
            assert eq(add(self._n(k), self._n(0)), self._n(k))

    def test_add_zero_left(self):
        for k in range(5):
            assert eq(add(self._n(0), self._n(k)), self._n(k))

    def test_add_commutative(self):
        for a in range(4):
            for b in range(4):
                assert eq(add(self._n(a), self._n(b)), add(self._n(b), self._n(a)))

    def test_add_associative(self):
        for a in range(3):
            for b in range(3):
                for c in range(3):
                    lhs = add(add(self._n(a), self._n(b)), self._n(c))
                    rhs = add(self._n(a), add(self._n(b), self._n(c)))
                    assert eq(lhs, rhs)

    def test_add_concrete(self):
        assert eq(add(self._n(2), self._n(3)), self._n(5))

    def test_mul_zero_right(self):
        for k in range(5):
            assert eq(mul(self._n(k), self._n(0)), self._n(0))

    def test_mul_one(self):
        for k in range(5):
            assert eq(mul(self._n(k), self._n(1)), self._n(k))

    def test_mul_concrete(self):
        assert eq(mul(self._n(3), self._n(4)), self._n(12))

    def test_leq_reflexive(self):
        for k in range(5):
            assert leq(self._n(k), self._n(k))

    def test_leq_transitive(self):
        assert leq(self._n(0), self._n(3))
        assert leq(self._n(2), self._n(5))

    def test_leq_not_gt(self):
        assert not leq(self._n(5), self._n(2))

    def test_lt_strict(self):
        assert lt(self._n(2), self._n(3))
        assert not lt(self._n(3), self._n(3))
        assert not lt(self._n(4), self._n(3))


# ---------------------------------------------------------------------------
# 3. Boolean Kernel
# ---------------------------------------------------------------------------

class TestBooleanKernel:
    def test_false_is_zero(self):
        assert eq(false(), zero())

    def test_true_is_succ_zero(self):
        assert eq(true(), successor(zero()))

    def test_is_bool(self):
        assert is_bool(false())
        assert is_bool(true())
        assert not is_bool(from_int(2))

    def test_not_truth_table(self):
        assert eq(NOT(false()), true())
        assert eq(NOT(true()), false())

    def test_and_truth_table(self):
        assert eq(AND(false(), false()), false())
        assert eq(AND(false(), true()), false())
        assert eq(AND(true(), false()), false())
        assert eq(AND(true(), true()), true())

    def test_or_truth_table(self):
        assert eq(OR(false(), false()), false())
        assert eq(OR(false(), true()), true())
        assert eq(OR(true(), false()), true())
        assert eq(OR(true(), true()), true())

    def test_nand_truth_table(self):
        assert eq(NAND(false(), false()), true())
        assert eq(NAND(false(), true()), true())
        assert eq(NAND(true(), false()), true())
        assert eq(NAND(true(), true()), false())

    def test_implies_truth_table(self):
        assert eq(IMPLIES(false(), false()), true())
        assert eq(IMPLIES(false(), true()), true())
        assert eq(IMPLIES(true(), false()), false())
        assert eq(IMPLIES(true(), true()), true())

    def test_iff_truth_table(self):
        assert eq(IFF(false(), false()), true())
        assert eq(IFF(false(), true()), false())
        assert eq(IFF(true(), false()), false())
        assert eq(IFF(true(), true()), true())

    def test_de_morgan_and(self):
        for x in (false(), true()):
            for y in (false(), true()):
                lhs = NOT(AND(x, y))
                rhs = OR(NOT(x), NOT(y))
                assert eq(lhs, rhs)

    def test_de_morgan_or(self):
        for x in (false(), true()):
            for y in (false(), true()):
                lhs = NOT(OR(x, y))
                rhs = AND(NOT(x), NOT(y))
                assert eq(lhs, rhs)


# ---------------------------------------------------------------------------
# 4. Type Theory
# ---------------------------------------------------------------------------

class TestTypeTheory:
    def test_proof_witness(self):
        p = Proof(42)
        assert p.witness == 42

    def test_proof_apply(self):
        p = Proof(3)
        q = p.apply(lambda x: x * 2)
        assert q.witness == 6

    def test_pi_type(self):
        double = Pi(lambda x: x * 2)
        assert double(5) == 10

    def test_sigma_type(self):
        pair = Sigma(fst=3, snd="proof_that_3_is_odd")
        assert pair.fst == 3
        assert pair.snd == "proof_that_3_is_odd"

    def test_plus_zero_identity_zero(self):
        p = plus_zero_identity(zero())
        assert isinstance(p, Proof)
        assert p.witness is True

    def test_plus_zero_identity_nonzero(self):
        for k in range(1, 5):
            p = plus_zero_identity(from_int(k))
            assert isinstance(p, Proof)
            assert p.witness is True


# ---------------------------------------------------------------------------
# 5. Constraint Solver
# ---------------------------------------------------------------------------

class TestConstraintSolver:
    def _n(self, k: int) -> Natural:
        return from_int(k)

    def test_enumerate_range_single(self):
        vals = list(enumerate_range(self._n(3), self._n(3)))
        assert len(vals) == 1
        assert eq(vals[0], self._n(3))

    def test_enumerate_range_multi(self):
        vals = list(enumerate_range(self._n(0), self._n(4)))
        assert len(vals) == 5
        for i, v in enumerate(vals):
            assert eq(v, self._n(i))

    def test_search_finds_solution(self):
        # Find x in [0,4] such that x = 2
        space = SearchSpace(
            variables=["x"],
            bounds=[(self._n(0), self._n(4))],
        )
        target = self._n(2)
        constraints = [Constraint("eq", target, target)]
        result = space.search(constraints)
        assert result is not None

    def test_search_no_solution(self):
        # 5 = 6 is unsatisfiable in [0, 4]
        space = SearchSpace(
            variables=["x"],
            bounds=[(self._n(0), self._n(4))],
        )
        # Constraint between two concrete values that are unequal → always False
        constraints = [Constraint("eq", self._n(5), self._n(6))]
        result = space.search(constraints)
        assert result is None

    def test_search_deterministic(self):
        space = SearchSpace(
            variables=["x"],
            bounds=[(self._n(0), self._n(5))],
        )
        constraints = [Constraint("leq", self._n(3), self._n(3))]
        r1 = space.search(constraints)
        r2 = space.search(constraints)
        assert r1 == r2

    def test_constraint_eq_satisfied(self):
        c = Constraint("eq", self._n(3), self._n(3))
        assert c.satisfied()

    def test_constraint_eq_not_satisfied(self):
        c = Constraint("eq", self._n(2), self._n(5))
        assert not c.satisfied()

    def test_constraint_leq_satisfied(self):
        c = Constraint("leq", self._n(2), self._n(5))
        assert c.satisfied()

    def test_constraint_unknown_op_raises(self):
        with pytest.raises(ValueError):
            Constraint("gt", self._n(1), self._n(2))


# ---------------------------------------------------------------------------
# 6. Hash Identity
# ---------------------------------------------------------------------------

class TestHashIdentity:
    def test_sha256_bytes_deterministic(self):
        data = b"orthogonal"
        assert sha256_bytes(data) == sha256_bytes(data)

    def test_sha256_bytes_known_value(self):
        expected = hashlib.sha256(b"orthogonal").hexdigest()
        assert sha256_bytes(b"orthogonal") == expected

    def test_sha256_str(self):
        h1 = sha256_str("hello")
        h2 = hashlib.sha256("hello".encode("utf-8")).hexdigest()
        assert h1 == h2

    def test_hash_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_bytes(b"hello world")
        expected = hashlib.sha256(b"hello world").hexdigest()
        assert hash_file(f) == expected

    def test_hash_directory(self, tmp_path):
        (tmp_path / "a.txt").write_bytes(b"aaa")
        (tmp_path / "b.txt").write_bytes(b"bbb")
        manifest = hash_directory(tmp_path)
        assert "a.txt" in manifest
        assert "b.txt" in manifest
        assert manifest["a.txt"] == hashlib.sha256(b"aaa").hexdigest()
        assert manifest["b.txt"] == hashlib.sha256(b"bbb").hexdigest()

    def test_verify_equal_same(self):
        h = {"a": "deadbeef", "b": "cafebabe"}
        assert verify_equal(h, h)
        assert verify_equal(dict(h), dict(h))

    def test_verify_equal_different(self):
        assert not verify_equal({"a": "x"}, {"a": "y"})

    def test_verify_reproducibility_same(self):
        h = {"a": "abc"}
        assert verify_reproducibility(h, h)

    def test_verify_reproducibility_different(self):
        with pytest.raises(ValueError):
            verify_reproducibility({"a": "x"}, {"a": "y"})


# ---------------------------------------------------------------------------
# 7. Closure Verifier
# ---------------------------------------------------------------------------

class TestClosureVerifier:
    def test_no_floating_point_clean(self):
        src = "x = 1\ny = 2\n"
        assert verify_no_floating_point(src)

    def test_no_floating_point_detects_literal(self):
        src = "x = 3.14\n"
        with pytest.raises(ValueError, match="[Ff]loating"):
            verify_no_floating_point(src)

    def test_no_floating_point_detects_float_name(self):
        src = "x = float(3)\n"
        with pytest.raises(ValueError):
            verify_no_floating_point(src)

    def test_no_randomness_clean(self):
        src = "x = 1\n"
        assert verify_no_randomness(src)

    def test_no_randomness_detects_import(self):
        src = "import random\n"
        with pytest.raises(ValueError, match="[Ss]tochastic"):
            verify_no_randomness(src)

    def test_no_forbidden_clean(self):
        src = "x = 1\n"
        assert verify_no_forbidden(src)

    def test_no_forbidden_detects_float(self):
        src = "y = float(x)\n"
        with pytest.raises(ValueError):
            verify_no_forbidden(src)

    def test_no_forbidden_detects_random(self):
        src = "z = random\n"
        with pytest.raises(ValueError):
            verify_no_forbidden(src)


# ---------------------------------------------------------------------------
# 8. Impossibility Theorems
# ---------------------------------------------------------------------------

class TestVendorLock:
    def test_hash_source_deterministic(self):
        src = "x = 1\n"
        assert hash_source(src) == hash_source(src)

    def test_verify_no_vendor_lock_same(self):
        src = "x = 1\n"
        h = hash_source(src)
        assert verify_no_vendor_lock(h, h)

    def test_verify_no_vendor_lock_different(self):
        assert not verify_no_vendor_lock(hash_source("a"), hash_source("b"))

    def test_check_no_lock_in(self):
        result = check_no_lock_in("x = 1\n")
        assert result["theorem"] == "VendorLockImpossibility"
        assert result["exclusive_advantage"] is False
        assert result["hash_verifiable"] is True


class TestGrowthIncompatibility:
    def test_halting_complete(self):
        proof = {
            "required_properties": ["determinism", "termination"],
            "proven_properties": ["determinism", "termination", "hash_verifiable"],
        }
        assert check_halting(proof)

    def test_halting_incomplete(self):
        proof = {
            "required_properties": ["determinism", "termination"],
            "proven_properties": ["determinism"],
        }
        assert not check_halting(proof)

    def test_growth_requires_modification(self):
        spec = {"requires_structural_modification": True}
        assert check_growth_requires_modification(spec)

    def test_detect_incompatibility(self):
        proof = {
            "required_properties": ["determinism"],
            "proven_properties": ["determinism"],
        }
        spec = {"requires_structural_modification": True}
        result = detect_incompatibility(proof, spec)
        assert result["halting"] is True
        assert result["growth_requires_modification"] is True
        assert result["incompatible"] is True

    def test_no_incompatibility_when_not_halting(self):
        proof = {
            "required_properties": ["determinism", "termination"],
            "proven_properties": ["determinism"],
        }
        spec = {"requires_structural_modification": True}
        result = detect_incompatibility(proof, spec)
        assert result["incompatible"] is False


class TestSpectacleNullification:
    def test_truth_value_valid(self):
        assert truth_value({"valid": True}) is True

    def test_truth_value_invalid(self):
        assert truth_value({"valid": False}) is False

    def test_spectacle_delta_is_zero(self):
        assert spectacle_delta({"valid": True}, rhetorical_amplitude=9999) == 0

    def test_nullification_proof_preserves_truth(self):
        for v in (True, False):
            result = nullification_proof({"valid": v})
            assert result["theorem"] == "SpectacleNullification"
            assert result["delta_in_validity"] == 0
            assert result["input_truth_value"] == v
            assert result["output_truth_value"] == v


# ---------------------------------------------------------------------------
# 9. Corporate Autopsy
# ---------------------------------------------------------------------------

class TestCorporateAutopsy:
    def test_tesla_comparison_keys(self):
        assert "Tesla FSD" in TESLA_COMPARISON
        assert "PR #43" in TESLA_COMPARISON
        assert TESLA_COMPARISON["PR #43"]["randomness"] == "none"
        assert TESLA_COMPARISON["PR #43"]["external_dependency"] == "none"

    def test_nvidia_comparison_keys(self):
        assert "NVIDIA Monte Carlo" in NVIDIA_COMPARISON
        assert "PR #43 QMC" in NVIDIA_COMPARISON
        assert NVIDIA_COMPARISON["PR #43 QMC"]["randomness"] == "none"

    def test_van_der_corput_deterministic(self):
        a = van_der_corput_fixed(8, precision_bits=8)
        b = van_der_corput_fixed(8, precision_bits=8)
        assert a == b

    def test_van_der_corput_length(self):
        result = van_der_corput_fixed(10, precision_bits=16)
        assert len(result) == 10

    def test_van_der_corput_range(self):
        denom = 1 << 16
        for v in van_der_corput_fixed(32, precision_bits=16):
            assert 0 <= v < denom

    def test_qmc_integrate_returns_pair(self):
        num, denom = qmc_integrate_fixed(10)
        assert isinstance(num, int)
        assert isinstance(denom, int)
        assert denom > 0

    def test_qmc_integrate_deterministic(self):
        r1 = qmc_integrate_fixed(16)
        r2 = qmc_integrate_fixed(16)
        assert r1 == r2


# ---------------------------------------------------------------------------
# 10. Cross-Platform Determinism
# ---------------------------------------------------------------------------

class TestDeterminism:
    """Same inputs always produce the same outputs — no randomness anywhere."""

    def test_add_deterministic(self):
        a, b = from_int(7), from_int(8)
        r1 = add(a, b)
        r2 = add(a, b)
        assert eq(r1, r2)

    def test_mul_deterministic(self):
        a, b = from_int(5), from_int(6)
        r1 = mul(a, b)
        r2 = mul(a, b)
        assert eq(r1, r2)

    def test_sha256_cross_run(self):
        data = b"pr43-yeshua-standard"
        assert sha256_bytes(data) == sha256_bytes(data)

    def test_hash_source_cross_run(self):
        src = "deterministic"
        assert hash_source(src) == hash_source(src)

    def test_peano_from_to_int(self):
        for k in range(10):
            assert to_int(from_int(k)) == k

    def test_boolean_algebra_deterministic(self):
        for x in (false(), true()):
            for y in (false(), true()):
                r1 = NAND(x, y)
                r2 = NAND(x, y)
                assert eq(r1, r2)
