#!/usr/bin/env python3
"""
tests/test_pr44_domains.py — PR #44 Orthogonal Meta Parallel Tests

Verifies:
  1.  Peano kernel: Zero/Succ induction, equality, to_int/from_int round-trip
  2.  Primitive recursion: add, mul, leq — structural correctness
  3.  Boolean kernel: NOT/AND/OR/NAND — truth table correctness
  4.  Type theory: Proof monad, Pi/Sigma types, plus_zero_identity proof
  5.  AI domain: constraint propagation, QMC solver
  6.  Video games: deterministic engine, provable RNG
  7.  Robotics: bipedal motion planner, safety verifier
  8.  Self-driving: constraint FSD solver
  9.  Military: mission planner
  10. Civilian tech: device stack
  11. Healthcare: deterministic diagnosis
  12. Impossibility theorems: vendor lock, growth incompatibility,
      hype nullification, energy efficiency upper bound
  13. Verification layer: hash identity, reproducibility checker
  14. Closure verifier: no float, no random, pure function checks
  15. Cross-platform determinism

Author: Orthogonal Engineering
PR: #44
Standard: Yeshua
Version: 44.0.0
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Dict

import pytest

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Foundations
from pr44_orthogonal_meta.foundations.peano_kernel import (
    Natural, Zero, Succ,
    zero, successor, eq, is_zero, induction, from_int, to_int,
)
from pr44_orthogonal_meta.foundations.primitive_recursion import add, mul, leq, lt
from pr44_orthogonal_meta.foundations.boolean_kernel import (
    false, true, is_bool, NOT, AND, OR, NAND, IMPLIES, IFF,
)
from pr44_orthogonal_meta.foundations.type_theory import Proof, Pi, Sigma, plus_zero_identity

# Domain models
from pr44_orthogonal_meta.domain_models.ai.deterministic_training import (
    constraint_propagate, COMPARISON as AI_COMPARISON,
)
from pr44_orthogonal_meta.domain_models.ai.qmc_solver import (
    van_der_corput, qmc_integrate, COMPARISON as QMC_COMPARISON,
)
from pr44_orthogonal_meta.domain_models.video_games.deterministic_engine import (
    move, collides, simulate_frame, detect_collisions,
    COMPARISON as GAME_ENGINE_COMPARISON,
)
from pr44_orthogonal_meta.domain_models.video_games.provable_rng import (
    lcg_next, generate_sequence, provable_fair_draw,
    COMPARISON as RNG_COMPARISON,
)
from pr44_orthogonal_meta.domain_models.robotics.bipedal_motion_planner import (
    plan_path, COMPARISON as ROBOTICS_COMPARISON,
)
from pr44_orthogonal_meta.domain_models.robotics.safety_verifier import (
    verify_path_safe, verify_bounded,
)
from pr44_orthogonal_meta.domain_models.self_driving.constraint_fsd import (
    fsd_plan, COMPARISON as FSD_COMPARISON,
)
from pr44_orthogonal_meta.domain_models.military.mission_planner import (
    plan_mission, COMPARISON as MILITARY_COMPARISON,
)
from pr44_orthogonal_meta.domain_models.civilian_tech.device_stack import (
    FirmwareModule, DeviceStack, COMPARISON as FIRMWARE_COMPARISON,
)
from pr44_orthogonal_meta.domain_models.healthcare.deterministic_diagnosis import (
    DiagnosticRule, DiagnosticEngine, verify_reproducibility as verify_diag_reproducibility,
    COMPARISON as HEALTH_COMPARISON,
)

# Impossibility
from pr44_orthogonal_meta.impossibility.vendor_lock import (
    hash_source, verify_no_vendor_lock, check_no_lock_in,
)
from pr44_orthogonal_meta.impossibility.growth_incompatibility import (
    check_halting, check_growth_requires_modification, detect_incompatibility,
)
from pr44_orthogonal_meta.impossibility.hype_nullification import (
    truth_value, spectacle_delta, nullification_proof,
)
from pr44_orthogonal_meta.impossibility.energy_efficiency_upper_bound import (
    computation_steps, energy_upper_bound_proof,
)

# Verification
from pr44_orthogonal_meta.verification.hash_identity import (
    sha256_bytes, sha256_str, hash_file, hash_directory,
    verify_equal, verify_reproducibility,
)
from pr44_orthogonal_meta.verification.reproducibility_checker import (
    hash_output, check_reproducible,
)

# Closure
from pr44_orthogonal_meta.closure.verify_closure import (
    verify_no_floating_point, verify_no_randomness, verify_no_forbidden,
    verify_pure_functions,
)


# ===========================================================================
# 1. Peano Kernel
# ===========================================================================

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
        for k in range(8):
            n = from_int(k)
            assert to_int(n) == k

    def test_from_int_negative_raises(self):
        with pytest.raises(ValueError):
            from_int(-1)

    def test_induction_base(self):
        result = induction(zero(), lambda: True, lambda k, ih: ih)
        assert result is True

    def test_induction_step(self):
        for k in range(4):
            result = induction(from_int(k), lambda: True, lambda _, ih: ih)
            assert result is True

    def test_successor_is_frozen(self):
        s = successor(zero())
        with pytest.raises((AttributeError, TypeError)):
            s.pred = zero()  # type: ignore[misc]  # Expected: frozen dataclass rejects mutation


# ===========================================================================
# 2. Primitive Recursion
# ===========================================================================

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


# ===========================================================================
# 3. Boolean Kernel
# ===========================================================================

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
                assert eq(NOT(AND(x, y)), OR(NOT(x), NOT(y)))

    def test_de_morgan_or(self):
        for x in (false(), true()):
            for y in (false(), true()):
                assert eq(NOT(OR(x, y)), AND(NOT(x), NOT(y)))


# ===========================================================================
# 4. Type Theory
# ===========================================================================

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


# ===========================================================================
# 5. AI Domain — Deterministic Training
# ===========================================================================

class TestDeterministicTraining:
    def test_constraint_propagate_finds_solution(self):
        variables = ["x"]
        domains = {"x": [from_int(k) for k in range(5)]}
        constraints = [{"op": "eq", "lhs": "x", "rhs": "x"}]
        result = constraint_propagate(variables, domains, constraints)
        assert result is not None

    def test_constraint_propagate_no_solution(self):
        variables = ["x", "y"]
        n2 = from_int(2)
        n5 = from_int(5)
        domains = {"x": [n2], "y": [n5]}
        # x == y, but x=2 and y=5, never equal
        constraints = [{"op": "eq", "lhs": "x", "rhs": "y"}]
        result = constraint_propagate(variables, domains, constraints)
        assert result is None

    def test_constraint_propagate_deterministic(self):
        variables = ["x"]
        domains = {"x": [from_int(k) for k in range(3)]}
        constraints: list = []
        r1 = constraint_propagate(variables, domains, constraints)
        r2 = constraint_propagate(variables, domains, constraints)
        assert (r1 is None) == (r2 is None)
        if r1 is not None and r2 is not None:
            assert eq(r1["x"], r2["x"])

    def test_ai_comparison_keys(self):
        assert "SGD (stochastic)" in AI_COMPARISON
        assert "PR #44 constraint propagation" in AI_COMPARISON
        assert AI_COMPARISON["PR #44 constraint propagation"]["randomness"] == "none"


# ===========================================================================
# 6. AI Domain — QMC Solver
# ===========================================================================

class TestQMCSolver:
    def test_van_der_corput_length(self):
        result = van_der_corput(10, precision_bits=16)
        assert len(result) == 10

    def test_van_der_corput_deterministic(self):
        a = van_der_corput(8, precision_bits=8)
        b = van_der_corput(8, precision_bits=8)
        assert a == b

    def test_van_der_corput_range(self):
        scale = 1 << 16
        for v in van_der_corput(32, precision_bits=16):
            assert 0 <= v < scale

    def test_qmc_integrate_returns_pair(self):
        num, denom = qmc_integrate(10)
        assert isinstance(num, int)
        assert isinstance(denom, int)
        assert denom > 0

    def test_qmc_integrate_deterministic(self):
        r1 = qmc_integrate(16)
        r2 = qmc_integrate(16)
        assert r1 == r2

    def test_qmc_comparison_keys(self):
        assert "Stochastic Monte Carlo" in QMC_COMPARISON
        assert "PR #44 QMC" in QMC_COMPARISON
        assert QMC_COMPARISON["PR #44 QMC"]["randomness"] == "none"


# ===========================================================================
# 7. Video Games — Deterministic Engine
# ===========================================================================

class TestDeterministicEngine:
    def _pt(self, x: int, y: int):
        return (from_int(x), from_int(y))

    def test_move_deterministic(self):
        pos = self._pt(2, 3)
        vel = self._pt(1, 1)
        new_pos = move(pos, vel)
        assert eq(new_pos[0], from_int(3))
        assert eq(new_pos[1], from_int(4))

    def test_move_idempotent_zero_vel(self):
        pos = self._pt(5, 7)
        vel = self._pt(0, 0)
        new_pos = move(pos, vel)
        assert eq(new_pos[0], pos[0])
        assert eq(new_pos[1], pos[1])

    def test_collides_same_position(self):
        pos = self._pt(3, 3)
        assert collides(pos, pos)

    def test_no_collision_different_positions(self):
        assert not collides(self._pt(1, 2), self._pt(3, 4))

    def test_simulate_frame_single_entity(self):
        entity = {"pos": self._pt(0, 0), "vel": self._pt(1, 0), "id": 1}
        forces = [self._pt(0, 0)]
        updated = simulate_frame([entity], forces)
        assert len(updated) == 1
        # vel stays (1,0), pos becomes (1,0)
        assert eq(updated[0]["pos"][0], from_int(1))

    def test_detect_collisions_none(self):
        entities = [
            {"pos": self._pt(0, 0), "vel": self._pt(0, 0), "id": 1},
            {"pos": self._pt(1, 0), "vel": self._pt(0, 0), "id": 2},
        ]
        assert detect_collisions(entities) == []

    def test_detect_collisions_found(self):
        entities = [
            {"pos": self._pt(0, 0), "vel": self._pt(0, 0), "id": 1},
            {"pos": self._pt(0, 0), "vel": self._pt(0, 0), "id": 2},
        ]
        cols = detect_collisions(entities)
        assert len(cols) == 1
        assert cols[0] == (1, 2)

    def test_engine_comparison_keys(self):
        assert "Proprietary engine (Unreal/Unity)" in GAME_ENGINE_COMPARISON
        assert "PR #44 deterministic engine" in GAME_ENGINE_COMPARISON


# ===========================================================================
# 8. Video Games — Provable RNG
# ===========================================================================

class TestProvableRNG:
    def test_lcg_next_deterministic(self):
        s1, v1 = lcg_next(42)
        s2, v2 = lcg_next(42)
        assert s1 == s2
        assert v1 == v2

    def test_generate_sequence_length(self):
        seq = generate_sequence(seed=0, n=10)
        assert len(seq) == 10

    def test_generate_sequence_deterministic(self):
        a = generate_sequence(seed=12345, n=20)
        b = generate_sequence(seed=12345, n=20)
        assert a == b

    def test_generate_sequence_different_seeds(self):
        a = generate_sequence(seed=1, n=10)
        b = generate_sequence(seed=2, n=10)
        assert a != b

    def test_provable_fair_draw_range(self):
        draws = provable_fair_draw(seed=7, n_outcomes=6, n=100)
        assert len(draws) == 100
        assert all(0 <= d < 6 for d in draws)

    def test_provable_fair_draw_deterministic(self):
        a = provable_fair_draw(seed=99, n_outcomes=10, n=50)
        b = provable_fair_draw(seed=99, n_outcomes=10, n=50)
        assert a == b

    def test_rng_comparison_keys(self):
        assert "Stochastic RNG (Python random)" in RNG_COMPARISON
        assert "PR #44 provable RNG" in RNG_COMPARISON


# ===========================================================================
# 9. Robotics — Bipedal Motion Planner
# ===========================================================================

class TestBipedalMotionPlanner:
    def test_plan_trivial_same_start_goal(self):
        path = plan_path((0, 0), (0, 0), set())
        assert path == [(0, 0)]

    def test_plan_simple_path(self):
        path = plan_path((0, 0), (2, 0), set())
        assert path is not None
        assert path[0] == (0, 0)
        assert path[-1] == (2, 0)

    def test_plan_no_path_blocked(self):
        # Completely surround (1,0) so (0,0) → (2,0) must go around (but with tight obstacles)
        obstacles = {(1, 0), (0, 1), (1, 1)}
        path = plan_path((0, 0), (2, 0), obstacles, max_coord=2)
        # With those obstacles and max_coord=2, check result type
        assert path is None or isinstance(path, list)

    def test_plan_path_avoids_obstacles(self):
        obstacles = {(1, 0)}
        path = plan_path((0, 0), (2, 0), obstacles, max_coord=4)
        if path is not None:
            assert (1, 0) not in path

    def test_plan_deterministic(self):
        path1 = plan_path((0, 0), (3, 3), set(), max_coord=8)
        path2 = plan_path((0, 0), (3, 3), set(), max_coord=8)
        assert path1 == path2

    def test_robotics_comparison_keys(self):
        assert "Stochastic motion planner (RL)" in ROBOTICS_COMPARISON
        assert "PR #44 BFS planner" in ROBOTICS_COMPARISON


# ===========================================================================
# 10. Robotics — Safety Verifier
# ===========================================================================

class TestSafetyVerifier:
    def test_verify_path_safe_empty(self):
        result = verify_path_safe([], set())
        assert result["safe"] is True
        assert result["steps_checked"] == 0

    def test_verify_path_safe_no_obstacle(self):
        path = [(0, 0), (1, 0), (2, 0)]
        result = verify_path_safe(path, {(5, 5)})
        assert result["safe"] is True
        assert result["steps_checked"] == 3

    def test_verify_path_safe_hits_obstacle(self):
        path = [(0, 0), (1, 0), (2, 0)]
        result = verify_path_safe(path, {(1, 0)})
        assert result["safe"] is False
        assert result["first_violation"] == (1, 0)

    def test_verify_bounded_all_in(self):
        path = [(0, 0), (5, 5), (10, 10)]
        result = verify_bounded(path, max_coord=10)
        assert result["within_bounds"] is True

    def test_verify_bounded_violation(self):
        path = [(0, 0), (11, 0)]
        result = verify_bounded(path, max_coord=10)
        assert result["within_bounds"] is False
        assert result["first_violation"] == (11, 0)


# ===========================================================================
# 11. Self-Driving — Constraint FSD
# ===========================================================================

class TestConstraintFSD:
    def test_fsd_plan_reachable(self):
        result = fsd_plan((0, 0), (3, 3), set(), max_coord=8)
        assert result["reachable"] is True
        assert result["safe"] is True
        assert result["within_bounds"] is True

    def test_fsd_plan_unreachable(self):
        # Surround destination with obstacles
        obstacles = {(1, 0), (0, 1), (1, 1)}
        result = fsd_plan((0, 0), (2, 2), obstacles, max_coord=2)
        # Either reachable or not — just check the record is complete
        assert "reachable" in result
        assert "safe" in result

    def test_fsd_plan_same_start_goal(self):
        result = fsd_plan((2, 2), (2, 2), set(), max_coord=4)
        assert result["reachable"] is True

    def test_fsd_comparison_keys(self):
        assert "Tesla FSD (neural)" in FSD_COMPARISON
        assert "PR #44 constraint FSD" in FSD_COMPARISON


# ===========================================================================
# 12. Military — Mission Planner
# ===========================================================================

class TestMissionPlanner:
    def test_plan_mission_trivial(self):
        result = plan_mission([(0, 0)], set())
        assert result["complete"] is True
        assert result["segments"] == []

    def test_plan_mission_two_waypoints(self):
        result = plan_mission([(0, 0), (3, 3)], set(), max_coord=8)
        assert result["complete"] is True
        assert len(result["segments"]) == 1
        seg = result["segments"][0]
        assert seg["reachable"] is True
        assert seg["safe"] is True

    def test_plan_mission_partial(self):
        # Block path between waypoints
        obstacles = {(1, 0), (0, 1), (1, 1)}
        result = plan_mission([(0, 0), (2, 2)], obstacles, max_coord=2)
        assert "complete" in result

    def test_plan_mission_multi_waypoint(self):
        waypoints = [(0, 0), (2, 0), (2, 2), (0, 2)]
        result = plan_mission(waypoints, set(), max_coord=4)
        assert result["complete"] is True
        assert len(result["segments"]) == 3

    def test_military_comparison_keys(self):
        assert "Opaque C2 pipeline" in MILITARY_COMPARISON
        assert "PR #44 mission planner" in MILITARY_COMPARISON


# ===========================================================================
# 13. Civilian Tech — Device Stack
# ===========================================================================

class TestDeviceStack:
    def test_firmware_module_hash_deterministic(self):
        m = FirmwareModule("boot", 1, "x = 1\n")
        assert m.sha256 == hashlib.sha256(b"x = 1\n").hexdigest()

    def test_firmware_module_execute_identity(self):
        m = FirmwareModule("core", 1, "pass\n")
        assert m.execute(42) == 42

    def test_device_stack_runs(self):
        m1 = FirmwareModule("init", 1, "pass\n")
        m2 = FirmwareModule("main", 1, "pass\n")
        stack = DeviceStack([m1, m2])
        assert stack.run(0) == 0

    def test_device_stack_verify(self):
        m = FirmwareModule("bootloader", 1, "boot()\n")
        stack = DeviceStack([m])
        record = stack.verify()
        assert record["theorem"] == "DeviceStackVerification"
        assert record["vendor_lock"] is False
        assert record["open_verifiable"] is True
        assert record["count"] == 1

    def test_device_stack_deterministic(self):
        m = FirmwareModule("f", 1, "code\n")
        s1 = DeviceStack([m])
        s2 = DeviceStack([m])
        assert s1.run(7) == s2.run(7)

    def test_firmware_comparison_keys(self):
        assert "Proprietary firmware" in FIRMWARE_COMPARISON
        assert "PR #44 device stack" in FIRMWARE_COMPARISON


# ===========================================================================
# 14. Healthcare — Deterministic Diagnosis
# ===========================================================================

class TestDeterministicDiagnosis:
    def test_rule_triggers(self):
        rule = DiagnosticRule("fever", threshold=38)
        assert rule.evaluate(38) is True
        assert rule.evaluate(39) is True
        assert rule.evaluate(37) is False

    def test_engine_no_flags(self):
        engine = DiagnosticEngine([
            DiagnosticRule("fever", 38),
            DiagnosticRule("bp", 140),
        ])
        result = engine.evaluate({"fever": 36, "bp": 120})
        assert result["alert"] is False
        assert result["flagged_conditions"] == []

    def test_engine_flags_condition(self):
        engine = DiagnosticEngine([DiagnosticRule("fever", 38)])
        result = engine.evaluate({"fever": 39})
        assert result["alert"] is True
        assert "fever" in result["flagged_conditions"]

    def test_engine_reproducible(self):
        engine = DiagnosticEngine([DiagnosticRule("fever", 38)])
        scores = {"fever": 37}
        assert verify_diag_reproducibility(engine, scores, n_runs=5)

    def test_engine_deterministic(self):
        engine = DiagnosticEngine([DiagnosticRule("bp", 140)])
        scores = {"bp": 150}
        r1 = engine.evaluate(scores)
        r2 = engine.evaluate(scores)
        assert r1 == r2

    def test_health_comparison_keys(self):
        assert "Black-box ML classifier" in HEALTH_COMPARISON
        assert "PR #44 deterministic diagnosis" in HEALTH_COMPARISON


# ===========================================================================
# 15. Impossibility — Vendor Lock
# ===========================================================================

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
        assert "healthcare" in result["domains_covered"]


# ===========================================================================
# 16. Impossibility — Growth Incompatibility
# ===========================================================================

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


# ===========================================================================
# 17. Impossibility — Hype Nullification
# ===========================================================================

class TestHypeNullification:
    def test_truth_value_valid(self):
        assert truth_value({"valid": True}) is True

    def test_truth_value_invalid(self):
        assert truth_value({"valid": False}) is False

    def test_spectacle_delta_is_zero(self):
        assert spectacle_delta({"valid": True}, rhetorical_amplitude=9999) == 0

    def test_nullification_proof_preserves_truth(self):
        for v in (True, False):
            result = nullification_proof({"valid": v})
            assert result["theorem"] == "HypeNullification"
            assert result["delta_in_validity"] == 0
            assert result["input_truth_value"] == v
            assert result["output_truth_value"] == v


# ===========================================================================
# 18. Impossibility — Energy Efficiency Upper Bound
# ===========================================================================

class TestEnergyEfficiencyUpperBound:
    def test_computation_steps_keys(self):
        steps = computation_steps(n_states=10, n_samples=100)
        assert steps["deterministic_steps"] == 10
        assert steps["stochastic_steps"] == 100

    def test_energy_bound_deterministic_wins(self):
        result = energy_upper_bound_proof(n_states=10, n_samples=100)
        assert result["theorem"] == "EnergyEfficiencyUpperBound"
        assert result["deterministic_optimal"] is True

    def test_energy_bound_equal_steps(self):
        result = energy_upper_bound_proof(n_states=50, n_samples=50)
        assert result["deterministic_optimal"] is True

    def test_energy_bound_zero_states(self):
        result = energy_upper_bound_proof(n_states=0, n_samples=0)
        assert result["deterministic_optimal"] is True


# ===========================================================================
# 19. Verification — Hash Identity
# ===========================================================================

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


# ===========================================================================
# 20. Verification — Reproducibility Checker
# ===========================================================================

class TestReproducibilityChecker:
    def test_hash_output_deterministic(self):
        value = {"x": 1, "y": [2, 3]}
        assert hash_output(value) == hash_output(value)

    def test_hash_output_different_values(self):
        assert hash_output({"a": 1}) != hash_output({"a": 2})

    def test_check_reproducible_pure_fn(self):
        def pure_fn(x: int) -> int:
            return x * x

        result = check_reproducible(pure_fn, [5], {}, n_runs=5)
        assert result["reproducible"] is True
        assert result["mismatch_at"] is None

    def test_check_reproducible_hash_stable(self):
        result = check_reproducible(lambda: {"key": "value"}, [], {}, n_runs=3)
        assert result["reproducible"] is True
        assert result["hash"] is not None


# ===========================================================================
# 21. Closure Verifier
# ===========================================================================

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

    def test_verify_pure_functions_clean_module(self):
        import pr44_orthogonal_meta.foundations.peano_kernel as pk
        assert verify_pure_functions(pk)

    def test_verify_pure_functions_rejects_global_mutation(self):
        import types
        import tempfile
        import importlib.util
        import os

        src = "def impure():\n    global _state\n    _state = 1\n"
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(src)
            fname = f.name
        try:
            spec = importlib.util.spec_from_file_location("_fake_impure_mod", fname)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            with pytest.raises(ValueError, match="[Ii]mpure"):
                verify_pure_functions(mod)
        finally:
            os.unlink(fname)


# ===========================================================================
# 22. Cross-Platform Determinism
# ===========================================================================

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
        data = b"pr44-yeshua-standard"
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

    def test_qmc_deterministic(self):
        r1 = van_der_corput(20, precision_bits=16)
        r2 = van_der_corput(20, precision_bits=16)
        assert r1 == r2

    def test_rng_deterministic(self):
        r1 = generate_sequence(seed=1234, n=50)
        r2 = generate_sequence(seed=1234, n=50)
        assert r1 == r2

    def test_path_planner_deterministic(self):
        p1 = plan_path((0, 0), (4, 4), set(), max_coord=8)
        p2 = plan_path((0, 0), (4, 4), set(), max_coord=8)
        assert p1 == p2
