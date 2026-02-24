#!/usr/bin/env python3
"""
tests/test_pr45_uvdtl.py — PR #45 Universal Verifiability & Deterministic Transparency Layer

Verifies:
  1.  Arithmetic Domain: Natural numbers, finite tuples, rational encoding,
      canonical strings, total function application
  2.  Trace Interface: primitive step validation, trace_successor/zero_test/add,
      tuple_construction, projection, public trace() dispatcher
  3.  Canonical Serialization: UTF-8, LF, sorted keys, type annotation,
      no-float guard, state_hash determinism, canonical equality
  4.  Hidden State Eliminator: declared-seed PRNG, sequence reproducibility,
      clock/randomness audit helpers
  5.  Function Classifier: FunctionManifest validation, FunctionRegistry,
      PR45 pre-built manifests, verify_all_total
  6.  Resource Bounds: cost functions for all operations
  7.  Locked Environment: BuildSpec canonical bytes, build_hash, BuildRecord
  8.  Cross-Platform Verifier: artifact/state equality, multi-environment check
  9.  Parallel Determinism: partition, map_reduce, sorted_fold, hash_sort_key,
      verify_no_shared_state
  10. Append-Only Witness: WitnessChain, GENESIS_HASH, recompute, verify_integrity
  11. Claim Registry: Claim, ClaimRegistry, PR45 built-in claims, verify_all
  12. Forkability: ForkabilitySpec, check_forkability, assert_forkable
  13. Transparency Invariants: all five invariants, verify_all_invariants
  14. Cross-system determinism

Author: Orthogonal Engineering
PR: #45
Standard: Yeshua
Version: 45.0.0
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any, Dict

import pytest

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Foundations
from pr45_uvdtl.foundations.arithmetic_domain import (
    Natural, Zero, Succ,
    zero, successor, from_int, to_int, nat_eq,
    make_tuple, tuple_project,
    make_canonical_string, CANONICAL_ALPHABET,
    Rational, apply_total,
    COMPARISON as ARITH_COMPARISON,
)
from pr45_uvdtl.foundations.trace_interface import (
    PrimitiveStep, Trace, PRIMITIVE_STEPS,
    trace_successor, trace_zero_test, trace_add,
    trace_tuple_construction, trace_projection,
    trace,
    COMPARISON as TRACE_COMPARISON,
)

# State
from pr45_uvdtl.state.canonical_serialization import (
    canonical_encode, state_hash,
    verify_canonical_equal, verify_hash_equal,
    COMPARISON as CANON_COMPARISON,
)
from pr45_uvdtl.state.hidden_state_eliminator import (
    derive_seed, prng, generate_sequence,
    assert_no_system_clock, assert_no_os_randomness,
    COMPARISON as HIDDEN_COMPARISON,
)

# Totality
from pr45_uvdtl.totality.function_classifier import (
    FunctionManifest, FunctionRegistry, PR45_MANIFESTS,
    COMPARISON as CLASSIFIER_COMPARISON,
)
from pr45_uvdtl.totality.resource_bounds import (
    cost, list_operations,
    cost_zero_test, cost_successor, cost_add, cost_mul,
    cost_sha256, cost_derive_seed, cost_prng,
    COMPARISON as BOUNDS_COMPARISON,
)

# Build
from pr45_uvdtl.build.locked_environment import (
    BuildSpec, BuildRecord, create_build_record,
    COMPARISON as BUILD_COMPARISON,
)
from pr45_uvdtl.build.cross_platform_verifier import (
    verify_artifact_equal, verify_state_equal,
    verify_build_reproducible, verify_multi_environment,
    COMPARISON as CROSS_COMPARISON,
)

# Parallel
from pr45_uvdtl.parallel.deterministic_reduction import (
    partition, map_reduce, sorted_fold, hash_sort_key,
    verify_no_shared_state,
    COMPARISON as PARALLEL_COMPARISON,
)

# Witness
from pr45_uvdtl.witness.append_only_witness import (
    WitnessEntry, WitnessChain, GENESIS_HASH,
    COMPARISON as WITNESS_COMPARISON,
)
from pr45_uvdtl.witness.claim_registry import (
    Claim, ClaimRegistry, build_pr45_claim_registry,
    COMPARISON as CLAIM_COMPARISON,
)

# Forkability
from pr45_uvdtl.forkability.forkability_checker import (
    ForkabilitySpec, check_forkability, assert_forkable,
    PR45_FORKABILITY,
    COMPARISON as FORK_COMPARISON,
)

# Invariants
from pr45_uvdtl.invariants.transparency_invariants import (
    invariant_1_equal_input_equal_output,
    invariant_2_equal_output_equal_hash,
    invariant_3_equal_hash_equal_artifact,
    invariant_4_no_mutation_without_trace,
    invariant_5_trace_finite_reproducible,
    verify_all_invariants,
    COMPARISON as INV_COMPARISON,
)


# ===========================================================================
# 1. Arithmetic Domain
# ===========================================================================

class TestArithmeticDomain:
    def test_zero_is_Zero(self):
        assert isinstance(zero(), Zero)

    def test_successor_is_Succ(self):
        s = successor(zero())
        assert isinstance(s, Succ)
        assert isinstance(s.pred, Zero)

    def test_nat_eq_zero_zero(self):
        assert nat_eq(zero(), zero())

    def test_nat_eq_succ_succ(self):
        one = successor(zero())
        one2 = successor(zero())
        assert nat_eq(one, one2)

    def test_nat_eq_different(self):
        assert not nat_eq(zero(), successor(zero()))

    def test_from_int_to_int_round_trip(self):
        for k in range(8):
            assert to_int(from_int(k)) == k

    def test_from_int_negative_raises(self):
        with pytest.raises(ValueError):
            from_int(-1)

    def test_make_tuple(self):
        t = make_tuple(zero(), successor(zero()))
        assert len(t) == 2
        assert isinstance(t[0], Zero)

    def test_tuple_project(self):
        one = successor(zero())
        t = make_tuple(zero(), one)
        assert nat_eq(tuple_project(t, 0), zero())
        assert nat_eq(tuple_project(t, 1), one)

    def test_tuple_project_out_of_range(self):
        t = make_tuple(zero())
        with pytest.raises(IndexError):
            tuple_project(t, 5)

    def test_make_canonical_string_valid(self):
        s = make_canonical_string("abc123")
        assert s == "abc123"

    def test_make_canonical_string_invalid(self):
        with pytest.raises(ValueError):
            make_canonical_string("hello world")  # space not in alphabet

    def test_rational_valid(self):
        r = Rational(numerator=3, denominator=4)
        assert r.as_pair() == (3, 4)

    def test_rational_zero_denominator_raises(self):
        with pytest.raises(ValueError):
            Rational(numerator=1, denominator=0)

    def test_rational_negative_denominator_raises(self):
        with pytest.raises(ValueError):
            Rational(numerator=1, denominator=-1)

    def test_rational_negative_numerator_raises(self):
        with pytest.raises(ValueError):
            Rational(numerator=-1, denominator=1)

    def test_apply_total(self):
        result = apply_total(successor, zero())
        assert isinstance(result, Succ)

    def test_succ_is_frozen(self):
        s = successor(zero())
        with pytest.raises((AttributeError, TypeError)):
            s.pred = zero()  # type: ignore[misc]

    def test_comparison_keys(self):
        assert "Float arithmetic (IEEE 754)" in ARITH_COMPARISON
        assert "PR #45 Arithmetic Domain" in ARITH_COMPARISON


# ===========================================================================
# 2. Trace Interface
# ===========================================================================

class TestTraceInterface:
    def test_primitive_step_valid(self):
        for kind in PRIMITIVE_STEPS:
            step = PrimitiveStep(kind=kind)
            assert step.kind == kind

    def test_primitive_step_invalid(self):
        with pytest.raises(ValueError):
            PrimitiveStep(kind="unbounded_loop")

    def test_trace_successor(self):
        t = trace_successor(3)
        assert t.operation_id == "successor"
        assert t.length() == 1
        assert t.steps[0].kind == "successor"

    def test_trace_zero_test_zero(self):
        t = trace_zero_test(0)
        assert t.length() == 1
        assert "True" in t.steps[0].detail

    def test_trace_zero_test_nonzero(self):
        t = trace_zero_test(5)
        assert "False" in t.steps[0].detail

    def test_trace_add_zero(self):
        t = trace_add(3, 0)
        # Only the bounded_recursion frame, no successor steps
        assert t.length() == 1
        assert t.steps[0].kind == "bounded_recursion"

    def test_trace_add_steps(self):
        t = trace_add(2, 3)
        # 1 bounded_recursion frame + 3 successor steps
        assert t.length() == 4
        kinds = [s.kind for s in t.steps]
        assert kinds[0] == "bounded_recursion"
        assert all(k == "successor" for k in kinds[1:])

    def test_trace_tuple_construction(self):
        t = trace_tuple_construction([1, 2, 3])
        assert t.length() == 1
        assert t.steps[0].kind == "tuple_construction"

    def test_trace_projection(self):
        t = trace_projection([10, 20, 30], 1)
        assert t.length() == 1
        assert t.steps[0].kind == "projection"
        assert "20" in t.steps[0].detail

    def test_trace_is_finite(self):
        t = trace_add(5, 5)
        assert t.is_finite()

    def test_trace_recompute_deterministic(self):
        t = trace_add(4, 4)
        steps_a = t.recompute()
        steps_b = t.recompute()
        assert steps_a == steps_b

    def test_trace_dispatcher_successor(self):
        t = trace("successor", n=7)
        assert t.operation_id == "successor"

    def test_trace_dispatcher_zero_test(self):
        t = trace("zero_test", n=0)
        assert t.operation_id == "zero_test"

    def test_trace_dispatcher_add(self):
        t = trace("add", a=2, b=3)
        assert "add" in t.operation_id

    def test_trace_dispatcher_tuple(self):
        t = trace("tuple_construction", values=[1, 2])
        assert t.steps[0].kind == "tuple_construction"

    def test_trace_dispatcher_projection(self):
        t = trace("projection", values=[10, 20], index=0)
        assert t.steps[0].kind == "projection"

    def test_trace_dispatcher_unknown_raises(self):
        with pytest.raises(ValueError):
            trace("unknown_op")

    def test_comparison_keys(self):
        assert "Black-box neural operation" in TRACE_COMPARISON
        assert "PR #45 trace_interface" in TRACE_COMPARISON


# ===========================================================================
# 3. Canonical Serialization
# ===========================================================================

class TestCanonicalSerialization:
    def _state(self) -> Dict[str, Any]:
        return {"version": 1, "name": "test", "active": True}

    def test_canonical_encode_is_bytes(self):
        result = canonical_encode(self._state())
        assert isinstance(result, bytes)

    def test_canonical_encode_utf8(self):
        result = canonical_encode(self._state())
        result.decode("utf-8")  # must not raise

    def test_canonical_encode_lf_only(self):
        result = canonical_encode(self._state())
        assert b"\r" not in result

    def test_canonical_encode_deterministic(self):
        s = self._state()
        assert canonical_encode(s) == canonical_encode(s)

    def test_canonical_encode_sorted_keys(self):
        s1 = {"b": 2, "a": 1}
        s2 = {"a": 1, "b": 2}
        assert canonical_encode(s1) == canonical_encode(s2)

    def test_canonical_encode_type_annotation(self):
        result = canonical_encode({"x": 1}).decode("utf-8")
        assert "__type__" in result

    def test_canonical_encode_no_float_raises(self):
        with pytest.raises(TypeError):
            canonical_encode({"x": 3.14})

    def test_canonical_encode_nested_no_float_raises(self):
        with pytest.raises(TypeError):
            canonical_encode({"nested": {"val": 1.5}})

    def test_state_hash_deterministic(self):
        s = self._state()
        assert state_hash(s) == state_hash(s)

    def test_state_hash_changes_with_state(self):
        s1 = {"x": 1}
        s2 = {"x": 2}
        assert state_hash(s1) != state_hash(s2)

    def test_state_hash_is_sha256(self):
        s = self._state()
        expected = hashlib.sha256(canonical_encode(s)).hexdigest()
        assert state_hash(s) == expected

    def test_verify_canonical_equal_same(self):
        s = self._state()
        assert verify_canonical_equal(s, dict(s))

    def test_verify_canonical_equal_different(self):
        assert not verify_canonical_equal({"x": 1}, {"x": 2})

    def test_verify_hash_equal_same(self):
        s = self._state()
        assert verify_hash_equal(s, dict(s))

    def test_verify_hash_equal_different(self):
        assert not verify_hash_equal({"x": 1}, {"x": 2})

    def test_none_value_allowed(self):
        result = canonical_encode({"x": None})
        assert b"null" in result

    def test_bool_value_allowed(self):
        result = canonical_encode({"flag": True}).decode("utf-8")
        assert "bool" in result

    def test_comparison_keys(self):
        assert "Ad-hoc JSON serialisation" in CANON_COMPARISON
        assert "PR #45 canonical_encode" in CANON_COMPARISON


# ===========================================================================
# 4. Hidden State Eliminator
# ===========================================================================

class TestHiddenStateEliminator:
    _PREV_HASH = hashlib.sha256(b"state0").hexdigest()
    _INPUT = "declared_input_A"

    def test_derive_seed_deterministic(self):
        s1 = derive_seed(self._PREV_HASH, self._INPUT)
        s2 = derive_seed(self._PREV_HASH, self._INPUT)
        assert s1 == s2

    def test_derive_seed_is_hex(self):
        s = derive_seed(self._PREV_HASH, self._INPUT)
        assert len(s) == 64
        int(s, 16)  # must not raise

    def test_derive_seed_different_inputs(self):
        s1 = derive_seed(self._PREV_HASH, "A")
        s2 = derive_seed(self._PREV_HASH, "B")
        assert s1 != s2

    def test_prng_deterministic(self):
        seed = derive_seed(self._PREV_HASH, self._INPUT)
        assert prng(seed, 0) == prng(seed, 0)

    def test_prng_different_counters(self):
        seed = derive_seed(self._PREV_HASH, self._INPUT)
        assert prng(seed, 0) != prng(seed, 1)

    def test_prng_is_int(self):
        seed = derive_seed(self._PREV_HASH, self._INPUT)
        assert isinstance(prng(seed, 0), int)

    def test_generate_sequence_deterministic(self):
        seed = derive_seed(self._PREV_HASH, self._INPUT)
        seq1 = generate_sequence(seed, 10)
        seq2 = generate_sequence(seed, 10)
        assert seq1 == seq2

    def test_generate_sequence_length(self):
        seed = derive_seed(self._PREV_HASH, self._INPUT)
        seq = generate_sequence(seed, 5)
        assert len(seq) == 5

    def test_assert_no_system_clock_clean(self):
        src = "x = 1\n"
        assert assert_no_system_clock(src)

    def test_assert_no_system_clock_detects(self):
        src = "t = time.time()\n"
        with pytest.raises(ValueError, match="clock"):
            assert_no_system_clock(src)

    def test_assert_no_os_randomness_clean(self):
        src = "x = 1\n"
        assert assert_no_os_randomness(src)

    def test_assert_no_os_randomness_detects(self):
        src = "b = os.urandom(16)\n"
        with pytest.raises(ValueError, match="[Oo][Ss] randomness|OS randomness"):
            assert_no_os_randomness(src)

    def test_comparison_keys(self):
        assert "os.urandom / secrets" in HIDDEN_COMPARISON
        assert "PR #45 declared-seed PRNG" in HIDDEN_COMPARISON


# ===========================================================================
# 5. Function Classifier
# ===========================================================================

class TestFunctionClassifier:
    def _make_manifest(self, **overrides) -> FunctionManifest:
        defaults = dict(
            name="f",
            input_domain="ℕ",
            output_domain="ℕ",
            total=True,
            measure="n",
            decreases=True,
            recursion_kind="structural",
        )
        defaults.update(overrides)
        return FunctionManifest(**defaults)

    def test_valid_manifest(self):
        m = self._make_manifest()
        assert m.total is True

    def test_non_total_raises(self):
        with pytest.raises(ValueError, match="total"):
            self._make_manifest(total=False)

    def test_illegal_recursion_kind_raises(self):
        with pytest.raises(ValueError, match="recursion kind"):
            self._make_manifest(recursion_kind="unbounded_loop")

    def test_all_permitted_recursion_kinds(self):
        for kind in ["structural", "primitive", "bounded_iteration", "none"]:
            m = self._make_manifest(recursion_kind=kind)
            assert m.recursion_kind == kind

    def test_manifest_as_dict_keys(self):
        m = self._make_manifest()
        d = m.as_dict()
        assert "name" in d
        assert "input_domain" in d
        assert "output_domain" in d
        assert "total" in d
        assert "measure" in d
        assert "decreases" in d
        assert "recursion_kind" in d

    def test_registry_register_and_get(self):
        reg = FunctionRegistry()
        m = self._make_manifest(name="my_fn")
        reg.register(m)
        assert reg.get("my_fn").name == "my_fn"

    def test_registry_duplicate_raises(self):
        reg = FunctionRegistry()
        m = self._make_manifest(name="dup")
        reg.register(m)
        with pytest.raises(ValueError, match="Duplicate"):
            reg.register(m)

    def test_registry_get_missing_raises(self):
        reg = FunctionRegistry()
        with pytest.raises(KeyError):
            reg.get("missing")

    def test_registry_verify_all_total(self):
        reg = FunctionRegistry()
        for m in PR45_MANIFESTS:
            try:
                reg.register(m)
            except ValueError:
                pass  # duplicates from earlier registrations
        assert reg.verify_all_total()

    def test_pr45_manifests_non_empty(self):
        assert len(PR45_MANIFESTS) >= 3

    def test_pr45_manifests_all_total(self):
        for m in PR45_MANIFESTS:
            assert m.total is True

    def test_all_manifests_sorted(self):
        reg = FunctionRegistry()
        for m in PR45_MANIFESTS:
            try:
                reg.register(m)
            except ValueError:
                pass
        names = [d["name"] for d in reg.all_manifests()]
        assert names == sorted(names)

    def test_comparison_keys(self):
        assert "Undocumented function" in CLASSIFIER_COMPARISON
        assert "PR #45 FunctionManifest" in CLASSIFIER_COMPARISON


# ===========================================================================
# 6. Resource Bounds
# ===========================================================================

class TestResourceBounds:
    def test_cost_zero_test(self):
        assert cost_zero_test() == 1

    def test_cost_successor(self):
        assert cost_successor() == 1

    def test_cost_add(self):
        assert cost_add(3) == 3
        assert cost_add(0) == 0

    def test_cost_mul(self):
        assert cost_mul(3, 4) == 12
        assert cost_mul(0, 10) == 0

    def test_cost_sha256_single_block(self):
        assert cost_sha256(1) == 1
        assert cost_sha256(64) == 1

    def test_cost_sha256_two_blocks(self):
        assert cost_sha256(65) == 2

    def test_cost_derive_seed(self):
        assert cost_derive_seed() == 2

    def test_cost_prng(self):
        assert cost_prng() == 1

    def test_cost_dispatcher_zero_test(self):
        assert cost("zero_test", n=0) == 1

    def test_cost_dispatcher_successor(self):
        assert cost("successor", n=0) == 1

    def test_cost_dispatcher_add(self):
        assert cost("add", b=5) == 5

    def test_cost_dispatcher_mul(self):
        assert cost("mul", a=3, b=3) == 9

    def test_cost_dispatcher_unknown_raises(self):
        with pytest.raises(ValueError):
            cost("nonexistent_op")

    def test_list_operations_sorted(self):
        ops = list_operations()
        assert ops == sorted(ops)

    def test_cost_deterministic(self):
        assert cost("add", b=7) == cost("add", b=7)

    def test_comparison_keys(self):
        assert "Profiling-only cost" in BOUNDS_COMPARISON
        assert "PR #45 cost()" in BOUNDS_COMPARISON


# ===========================================================================
# 7. Locked Environment
# ===========================================================================

class TestLockedEnvironment:
    def _spec(self) -> BuildSpec:
        return BuildSpec(
            language="python",
            language_version="3.11.0",
            dependencies={"pydantic": "1.10.0", "pytest": "7.4.0"},
            compiler_flags=["-O", "-W"],
            entry_point="python -m pytest",
        )

    def test_build_spec_canonical_bytes_is_bytes(self):
        assert isinstance(self._spec().canonical_bytes(), bytes)

    def test_build_spec_canonical_bytes_deterministic(self):
        s = self._spec()
        assert s.canonical_bytes() == s.canonical_bytes()

    def test_build_spec_build_hash_is_sha256(self):
        s = self._spec()
        expected = hashlib.sha256(s.canonical_bytes()).hexdigest()
        assert s.build_hash() == expected

    def test_build_spec_sorted_deps(self):
        # Same deps different order → same canonical bytes
        s1 = BuildSpec(
            language="python",
            language_version="3.11.0",
            dependencies={"b": "2.0", "a": "1.0"},
            compiler_flags=[],
            entry_point="run",
        )
        s2 = BuildSpec(
            language="python",
            language_version="3.11.0",
            dependencies={"a": "1.0", "b": "2.0"},
            compiler_flags=[],
            entry_point="run",
        )
        assert s1.canonical_bytes() == s2.canonical_bytes()

    def test_create_build_record(self):
        spec = self._spec()
        record = create_build_record(spec, b"artifact", b"state")
        assert record.build_hash == spec.build_hash()
        assert record.artifact_hash == hashlib.sha256(b"artifact").hexdigest()
        assert record.state_hash == hashlib.sha256(b"state").hexdigest()

    def test_build_record_as_dict_keys(self):
        spec = self._spec()
        record = create_build_record(spec, b"art", b"state")
        d = record.as_dict()
        assert "build_hash" in d
        assert "artifact_hash" in d
        assert "state_hash" in d

    def test_comparison_keys(self):
        assert "Ad-hoc build script" in BUILD_COMPARISON
        assert "PR #45 BuildSpec" in BUILD_COMPARISON


# ===========================================================================
# 8. Cross-Platform Verifier
# ===========================================================================

class TestCrossPlatformVerifier:
    def _record(self, artifact: bytes = b"art", state: bytes = b"st") -> BuildRecord:
        spec = BuildSpec(
            language="python",
            language_version="3.11.0",
            dependencies={},
            compiler_flags=[],
            entry_point="run",
        )
        return create_build_record(spec, artifact, state)

    def test_verify_artifact_equal_same(self):
        r = self._record()
        assert verify_artifact_equal(r, r)

    def test_verify_artifact_equal_different_raises(self):
        r1 = self._record(artifact=b"art1")
        r2 = self._record(artifact=b"art2")
        with pytest.raises(ValueError, match="artifact"):
            verify_artifact_equal(r1, r2)

    def test_verify_state_equal_same(self):
        r = self._record()
        assert verify_state_equal(r, r)

    def test_verify_state_equal_different_raises(self):
        r1 = self._record(state=b"s1")
        r2 = self._record(state=b"s2")
        with pytest.raises(ValueError, match="state"):
            verify_state_equal(r1, r2)

    def test_verify_build_reproducible_same(self):
        r = self._record()
        result = verify_build_reproducible(r, r)
        assert result["reproducible"] is True
        assert result["artifact_equal"] is True
        assert result["state_equal"] is True

    def test_verify_build_reproducible_different(self):
        r1 = self._record(artifact=b"a1", state=b"s1")
        r2 = self._record(artifact=b"a2", state=b"s2")
        result = verify_build_reproducible(r1, r2)
        assert result["reproducible"] is False

    def test_verify_multi_environment_empty(self):
        result = verify_multi_environment([])
        assert result["all_equal"] is True

    def test_verify_multi_environment_all_same(self):
        r = self._record()
        result = verify_multi_environment([r, r, r])
        assert result["all_equal"] is True

    def test_verify_multi_environment_mismatch(self):
        r1 = self._record(artifact=b"a1")
        r2 = self._record(artifact=b"a2")
        result = verify_multi_environment([r1, r2])
        assert result["all_equal"] is False

    def test_comparison_keys(self):
        assert "Platform-dependent build" in CROSS_COMPARISON
        assert "PR #45 cross_platform_verifier" in CROSS_COMPARISON


# ===========================================================================
# 9. Parallel Determinism
# ===========================================================================

class TestParallelDeterminism:
    def test_partition_basic(self):
        parts = partition([1, 2, 3, 4, 5], 2)
        assert len(parts) == 2
        total = sum(len(p) for p in parts)
        assert total == 5

    def test_partition_all_items_covered(self):
        items = list(range(10))
        parts = partition(items, 3)
        flat = [x for p in parts for x in p]
        assert flat == items

    def test_partition_deterministic(self):
        items = list(range(7))
        assert partition(items, 3) == partition(items, 3)

    def test_partition_zero_parts_raises(self):
        with pytest.raises(ValueError):
            partition([1, 2], 0)

    def test_partition_immutable_parts(self):
        parts = partition([1, 2, 3], 2)
        for p in parts:
            assert isinstance(p, tuple)

    def test_map_reduce_sum(self):
        result = map_reduce(
            [1, 2, 3, 4, 5],
            mapper=lambda x: x * 2,
            reducer=lambda a, b: a + b,
            sort_key=lambda x: x,
            initial=0,
        )
        assert result == sum(x * 2 for x in [1, 2, 3, 4, 5])

    def test_map_reduce_deterministic(self):
        items = [5, 3, 1, 4, 2]
        r1 = map_reduce(items, lambda x: x, lambda a, b: a + b, lambda x: x, 0)
        r2 = map_reduce(items, lambda x: x, lambda a, b: a + b, lambda x: x, 0)
        assert r1 == r2

    def test_sorted_fold_deterministic(self):
        outputs = [3, 1, 2]
        s1 = sorted_fold(outputs, sort_key=lambda x: x)
        s2 = sorted_fold(outputs, sort_key=lambda x: x)
        assert s1 == s2

    def test_sorted_fold_order(self):
        outputs = [3, 1, 2]
        result = sorted_fold(outputs, sort_key=lambda x: x)
        assert result == [1, 2, 3]

    def test_hash_sort_key_deterministic(self):
        v = {"a": 1, "b": 2}
        assert hash_sort_key(v) == hash_sort_key(v)

    def test_hash_sort_key_different_values(self):
        assert hash_sort_key({"a": 1}) != hash_sort_key({"a": 2})

    def test_verify_no_shared_state_same(self):
        results = [1, 2, 3]
        assert verify_no_shared_state(results, list(results))

    def test_verify_no_shared_state_different_raises(self):
        with pytest.raises(ValueError):
            verify_no_shared_state([1, 2, 3], [1, 2, 4])

    def test_comparison_keys(self):
        assert "Unordered parallel reduce" in PARALLEL_COMPARISON
        assert "PR #45 deterministic_reduction" in PARALLEL_COMPARISON


# ===========================================================================
# 10. Append-Only Witness
# ===========================================================================

class TestAppendOnlyWitness:
    _BUILD_HASH = hashlib.sha256(b"build").hexdigest()
    _TRACE_HASH = hashlib.sha256(b"trace").hexdigest()

    def _chain(self) -> WitnessChain:
        return WitnessChain()

    def test_genesis_hash_is_sha256(self):
        expected = hashlib.sha256(b"genesis").hexdigest()
        assert GENESIS_HASH == expected

    def test_new_chain_starts_at_genesis(self):
        chain = self._chain()
        assert chain.chain_hash == GENESIS_HASH

    def test_new_chain_empty(self):
        chain = self._chain()
        assert chain.length == 0

    def test_append_returns_entry(self):
        chain = self._chain()
        new_hash = hashlib.sha256(b"state1").hexdigest()
        entry = chain.append(new_hash, "op1", self._TRACE_HASH, self._BUILD_HASH)
        assert isinstance(entry, WitnessEntry)
        assert entry.new_hash == new_hash
        assert entry.previous_hash == GENESIS_HASH

    def test_append_increments_length(self):
        chain = self._chain()
        for i in range(5):
            chain.append(hashlib.sha256(f"s{i}".encode()).hexdigest(), f"op{i}",
                         self._TRACE_HASH, self._BUILD_HASH)
        assert chain.length == 5

    def test_chain_hash_changes_on_append(self):
        chain = self._chain()
        h_before = chain.chain_hash
        chain.append(hashlib.sha256(b"s1").hexdigest(), "op1", self._TRACE_HASH, self._BUILD_HASH)
        assert chain.chain_hash != h_before

    def test_verify_integrity_empty(self):
        chain = self._chain()
        assert chain.verify_integrity()

    def test_verify_integrity_after_appends(self):
        chain = self._chain()
        for i in range(5):
            chain.append(hashlib.sha256(f"s{i}".encode()).hexdigest(), f"op{i}",
                         self._TRACE_HASH, self._BUILD_HASH)
        assert chain.verify_integrity()

    def test_recompute_matches_chain_hash(self):
        chain = self._chain()
        for i in range(3):
            chain.append(hashlib.sha256(f"s{i}".encode()).hexdigest(), f"op{i}",
                         self._TRACE_HASH, self._BUILD_HASH)
        assert chain.recompute_chain_hash() == chain.chain_hash

    def test_entries_returns_copy(self):
        chain = self._chain()
        chain.append(hashlib.sha256(b"s1").hexdigest(), "op1", self._TRACE_HASH, self._BUILD_HASH)
        entries = chain.entries()
        assert len(entries) == 1
        # Modifying the returned list does not affect the chain
        entries.clear()
        assert chain.length == 1

    def test_witness_entry_canonical_bytes_deterministic(self):
        entry = WitnessEntry(
            previous_hash="prev",
            new_hash="new",
            operation_id="op",
            trace_hash="th",
            build_hash="bh",
        )
        assert entry.canonical_bytes() == entry.canonical_bytes()

    def test_witness_entry_hash_is_sha256(self):
        entry = WitnessEntry(
            previous_hash="prev",
            new_hash="new",
            operation_id="op",
            trace_hash="th",
            build_hash="bh",
        )
        expected = hashlib.sha256(entry.canonical_bytes()).hexdigest()
        assert entry.entry_hash() == expected

    def test_comparison_keys(self):
        assert "Mutable audit log" in WITNESS_COMPARISON
        assert "PR #45 WitnessChain" in WITNESS_COMPARISON


# ===========================================================================
# 11. Claim Registry
# ===========================================================================

class TestClaimRegistry:
    def _claim(self, claim_id: str = "C-test") -> Claim:
        return Claim(
            claim_id=claim_id,
            domain="test",
            mapping="x → y",
            invariants=("inv1",),
            verification_procedure="run test",
        )

    def test_claim_requires_nonempty_id(self):
        with pytest.raises(ValueError):
            Claim(
                claim_id="",
                domain="d",
                mapping="m",
                invariants=(),
                verification_procedure="run",
            )

    def test_claim_requires_procedure(self):
        with pytest.raises(ValueError, match="verification_procedure"):
            Claim(
                claim_id="X",
                domain="d",
                mapping="m",
                invariants=(),
                verification_procedure="",
            )

    def test_claim_as_dict_keys(self):
        d = self._claim().as_dict()
        assert "claim_id" in d
        assert "domain" in d
        assert "mapping" in d
        assert "invariants" in d
        assert "verification_procedure" in d

    def test_registry_register_and_get(self):
        reg = ClaimRegistry()
        c = self._claim()
        reg.register(c, verifier=lambda: True)
        assert reg.get("C-test").claim_id == "C-test"

    def test_registry_duplicate_raises(self):
        reg = ClaimRegistry()
        c = self._claim()
        reg.register(c, verifier=lambda: True)
        with pytest.raises(ValueError, match="Duplicate"):
            reg.register(c, verifier=lambda: True)

    def test_registry_verify_single(self):
        reg = ClaimRegistry()
        reg.register(self._claim("CX"), verifier=lambda: True)
        assert reg.verify("CX") is True

    def test_registry_verify_all(self):
        reg = ClaimRegistry()
        reg.register(self._claim("C1"), verifier=lambda: True)
        reg.register(self._claim("C2"), verifier=lambda: True)
        results = reg.verify_all()
        assert all(results.values())

    def test_pr45_claim_registry_has_five_claims(self):
        reg = build_pr45_claim_registry()
        claims = reg.all_claims()
        assert len(claims) >= 5

    def test_pr45_claim_registry_verify_all(self):
        reg = build_pr45_claim_registry()
        results = reg.verify_all()
        assert all(results.values())

    def test_pr45_claim_registry_sorted(self):
        reg = build_pr45_claim_registry()
        ids = [c["claim_id"] for c in reg.all_claims()]
        assert ids == sorted(ids)

    def test_comparison_keys(self):
        assert "Informal system claim" in CLAIM_COMPARISON
        assert "PR #45 ClaimRegistry" in CLAIM_COMPARISON


# ===========================================================================
# 12. Forkability
# ===========================================================================

class TestForkability:
    def test_fully_forkable(self):
        spec = ForkabilitySpec(
            no_central_signing=True,
            no_remote_validation_gate=True,
            verification_scripts_in_repo=True,
            offline_reproducible=True,
        )
        assert spec.is_forkable() is True

    def test_not_forkable_missing_one(self):
        spec = ForkabilitySpec(
            no_central_signing=False,
            no_remote_validation_gate=True,
            verification_scripts_in_repo=True,
            offline_reproducible=True,
        )
        assert spec.is_forkable() is False

    def test_not_forkable_all_false(self):
        spec = ForkabilitySpec(
            no_central_signing=False,
            no_remote_validation_gate=False,
            verification_scripts_in_repo=False,
            offline_reproducible=False,
        )
        assert spec.is_forkable() is False

    def test_check_forkability_returns_dict(self):
        result = check_forkability(PR45_FORKABILITY)
        assert "forkable" in result
        assert "no_central_signing" in result

    def test_assert_forkable_succeeds(self):
        assert assert_forkable(PR45_FORKABILITY) is True

    def test_assert_forkable_raises_on_unforkable(self):
        spec = ForkabilitySpec(
            no_central_signing=False,
            no_remote_validation_gate=True,
            verification_scripts_in_repo=True,
            offline_reproducible=True,
        )
        with pytest.raises(ValueError, match="no_central_signing"):
            assert_forkable(spec)

    def test_pr45_forkability_is_forkable(self):
        assert PR45_FORKABILITY.is_forkable() is True

    def test_comparison_keys(self):
        assert "Centralised build service" in FORK_COMPARISON
        assert "PR #45 forkability" in FORK_COMPARISON


# ===========================================================================
# 13. Transparency Invariants
# ===========================================================================

class TestTransparencyInvariants:
    _STATE = {"version": 1, "name": "pr45"}
    _HASH_A = hashlib.sha256(b"a").hexdigest()
    _HASH_B = hashlib.sha256(b"b").hexdigest()

    def _empty_trace(self) -> Trace:
        return Trace(operation_id="noop")

    def _non_empty_trace(self) -> Trace:
        t = Trace(operation_id="succ")
        t.append(PrimitiveStep("successor", "succ(0)=1"))
        return t

    def test_invariant_1_same_state(self):
        assert invariant_1_equal_input_equal_output(self._STATE, dict(self._STATE))

    def test_invariant_1_different_state_vacuous(self):
        assert invariant_1_equal_input_equal_output({"x": 1}, {"x": 2})

    def test_invariant_2_same_bytes(self):
        b = b"canonical"
        h = hashlib.sha256(b).hexdigest()
        assert invariant_2_equal_output_equal_hash(b, b, h, h)

    def test_invariant_2_different_bytes_vacuous(self):
        b1, b2 = b"aaa", b"bbb"
        h1 = hashlib.sha256(b1).hexdigest()
        h2 = hashlib.sha256(b2).hexdigest()
        assert invariant_2_equal_output_equal_hash(b1, b2, h1, h2)

    def test_invariant_3_same_state_hash(self):
        art = hashlib.sha256(b"artifact").hexdigest()
        assert invariant_3_equal_hash_equal_artifact(self._HASH_A, self._HASH_A, art, art)

    def test_invariant_3_different_hash_vacuous(self):
        art1 = hashlib.sha256(b"a1").hexdigest()
        art2 = hashlib.sha256(b"a2").hexdigest()
        assert invariant_3_equal_hash_equal_artifact(self._HASH_A, self._HASH_B, art1, art2)

    def test_invariant_4_no_trace_identity_ok(self):
        # Same hash → identity transition, no trace required
        t = self._empty_trace()
        assert invariant_4_no_mutation_without_trace(t, self._HASH_A, self._HASH_A)

    def test_invariant_4_no_trace_different_hash_raises(self):
        t = self._empty_trace()
        with pytest.raises(ValueError, match="trace"):
            invariant_4_no_mutation_without_trace(t, self._HASH_A, self._HASH_B)

    def test_invariant_4_with_trace_ok(self):
        t = self._non_empty_trace()
        assert invariant_4_no_mutation_without_trace(t, self._HASH_A, self._HASH_B)

    def test_invariant_5_finite_and_reproducible(self):
        t = self._non_empty_trace()
        assert invariant_5_trace_finite_reproducible(t)

    def test_invariant_5_empty_trace_ok(self):
        t = self._empty_trace()
        assert invariant_5_trace_finite_reproducible(t)

    def test_verify_all_invariants_identity(self):
        t = self._empty_trace()
        art = hashlib.sha256(b"art").hexdigest()
        results = verify_all_invariants(
            state=self._STATE,
            trace=t,
            old_hash=self._HASH_A,
            new_hash=self._HASH_A,  # identity: same hash → no trace needed
            artifact_hash=art,
        )
        assert all(results.values())

    def test_verify_all_invariants_with_trace(self):
        t = self._non_empty_trace()
        art = hashlib.sha256(b"art").hexdigest()
        results = verify_all_invariants(
            state=self._STATE,
            trace=t,
            old_hash=self._HASH_A,
            new_hash=self._HASH_B,
            artifact_hash=art,
        )
        assert all(results.values())

    def test_comparison_keys(self):
        assert "Unverified system" in INV_COMPARISON
        assert "PR #45 transparency_invariants" in INV_COMPARISON


# ===========================================================================
# 14. Cross-System Determinism
# ===========================================================================

class TestCrossSystemDeterminism:
    """All components produce identical outputs on identical inputs — no hidden state."""

    def test_canonical_encode_cross_run(self):
        s = {"x": 1, "y": True}
        assert canonical_encode(s) == canonical_encode(s)

    def test_state_hash_cross_run(self):
        s = {"pr": 45}
        assert state_hash(s) == state_hash(s)

    def test_prng_cross_run(self):
        seed = derive_seed("aaa", "bbb")
        assert prng(seed, 0) == prng(seed, 0)

    def test_trace_add_cross_run(self):
        t1 = trace_add(10, 5)
        t2 = trace_add(10, 5)
        assert t1.steps == t2.steps

    def test_witness_chain_cross_run(self):
        def _build_chain() -> str:
            chain = WitnessChain()
            for i in range(4):
                chain.append(
                    hashlib.sha256(f"s{i}".encode()).hexdigest(),
                    f"op{i}",
                    hashlib.sha256(b"trace").hexdigest(),
                    hashlib.sha256(b"build").hexdigest(),
                )
            return chain.chain_hash

        assert _build_chain() == _build_chain()

    def test_partition_cross_run(self):
        items = list(range(20))
        assert partition(items, 4) == partition(items, 4)

    def test_hash_sort_key_cross_run(self):
        v = {"operation": "add", "result": 42}
        assert hash_sort_key(v) == hash_sort_key(v)
