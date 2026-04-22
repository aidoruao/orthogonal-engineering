"""Tests for photonic packaging checks.

Category 12: Packaging & Interconnect test suite.
"""

from fractions import Fraction

from axioms.logic import ProofObject
from src.hardware.photonic.packaging import (
    CoPackagedOptics,
    DieAttach,
    FiberArray,
    HermeticSeal,
    SolderJoint,
    WireBond,
    check_co_packaged_optics_pitch,
    check_die_attach_void,
    check_fiber_array_alignment,
    check_hermetic_seal,
    check_solder_joint_reliability,
    check_wire_bond_pull_strength,
    run_all_invariants,
)


def test_fiber_array_alignment_pass() -> None:
    arr = FiberArray(array_id="a1", alignment_error_um=Fraction(3, 10))
    ok, proof = check_fiber_array_alignment(arr)
    assert ok is True
    assert isinstance(proof, ProofObject)


def test_fiber_array_alignment_fail() -> None:
    arr = FiberArray(array_id="a2", alignment_error_um=Fraction(7, 10))
    ok, proof = check_fiber_array_alignment(arr)
    assert ok is False


def test_co_packaged_optics_pitch_pass() -> None:
    pkg = CoPackagedOptics(package_id="p1", pitch_um=Fraction(300, 1))
    ok, proof = check_co_packaged_optics_pitch(pkg)
    assert ok is True


def test_co_packaged_optics_pitch_fail() -> None:
    pkg = CoPackagedOptics(package_id="p2", pitch_um=Fraction(200, 1))
    ok, proof = check_co_packaged_optics_pitch(pkg)
    assert ok is False


def test_solder_joint_reliability_pass() -> None:
    joint = SolderJoint(joint_id="s1", reflow_cycles=Fraction(5, 1), failed=False)
    ok, proof = check_solder_joint_reliability(joint)
    assert ok is True


def test_solder_joint_reliability_fail() -> None:
    joint = SolderJoint(joint_id="s2", reflow_cycles=Fraction(2, 1), failed=False)
    ok, proof = check_solder_joint_reliability(joint)
    assert ok is False


def test_wire_bond_pull_strength_pass() -> None:
    bond = WireBond(bond_id="w1", pull_force_gf=Fraction(4, 1))
    ok, proof = check_wire_bond_pull_strength(bond)
    assert ok is True


def test_wire_bond_pull_strength_fail() -> None:
    bond = WireBond(bond_id="w2", pull_force_gf=Fraction(2, 1))
    ok, proof = check_wire_bond_pull_strength(bond)
    assert ok is False


def test_hermetic_seal_pass() -> None:
    seal = HermeticSeal(seal_id="h1", leak_rate=Fraction(1, 1_000_000_000))
    ok, proof = check_hermetic_seal(seal)
    assert ok is True


def test_hermetic_seal_fail() -> None:
    seal = HermeticSeal(seal_id="h2", leak_rate=Fraction(1, 10_000_000))
    ok, proof = check_hermetic_seal(seal)
    assert ok is False


def test_die_attach_void_pass() -> None:
    attach = DieAttach(attach_id="d1", void_percentage=Fraction(15, 100))
    ok, proof = check_die_attach_void(attach)
    assert ok is True


def test_die_attach_void_fail() -> None:
    attach = DieAttach(attach_id="d2", void_percentage=Fraction(35, 100))
    ok, proof = check_die_attach_void(attach)
    assert ok is False


def test_run_all_invariants() -> None:
    results = run_all_invariants()
    assert len(results) == 12
    passes = [ok for _, ok, _ in results if ok]
    fails = [ok for _, ok, _ in results if not ok]
    assert len(passes) == 6
    assert len(fails) == 6
