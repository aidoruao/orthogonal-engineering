"""PHOTONIC Packaging — Fiber alignment, co-packaged optics pitch, solder joints,
wire bond pull strength, hermetic seal, die attach voids.

Category 12: Packaging & Interconnect (checks 73-78).

Standards: Custom OE, OIF CEI-112G, IPC J-STD-020, MIL-STD-883.
All invariants use Fraction arithmetic for exact thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class FiberArray:
    """Fiber array alignment parameters.

    falsifies_if: alignment_error_um is negative.
    falsifies_if: alignment_error_um is negative.
    """
    array_id: str
    alignment_error_um: Fraction


@dataclass(frozen=True)
class CoPackagedOptics:
    """Co-packaged optics pitch parameters.

    falsifies_if: pitch_um is negative.
    falsifies_if: pitch_um is negative.
    """
    package_id: str
    pitch_um: Fraction


@dataclass(frozen=True)
class SolderJoint:
    """Solder joint reliability parameters.

    falsifies_if: reflow_cycles is negative.
    falsifies_if: reflow_cycles is negative.
    """
    joint_id: str
    reflow_cycles: Fraction
    failed: bool


@dataclass(frozen=True)
class WireBond:
    """Wire bond pull strength parameters.

    falsifies_if: pull_force_gf is negative.
    falsifies_if: pull_force_gf is negative.
    """
    bond_id: str
    pull_force_gf: Fraction


@dataclass(frozen=True)
class HermeticSeal:
    """Hermetic seal leak rate parameters.

    falsifies_if: leak_rate is negative.
    falsifies_if: leak_rate is negative.
    """
    seal_id: str
    leak_rate: Fraction


@dataclass(frozen=True)
class DieAttach:
    """Die attach void parameters.

    falsifies_if: void_percentage is negative or > 1.
    falsifies_if: void_percentage is negative or > 1.
    """
    attach_id: str
    void_percentage: Fraction


# ---------------------------------------------------------------------------
# Threshold functions
# ---------------------------------------------------------------------------

def fiber_alignment_threshold() -> Fraction:
    """Custom OE maximum fiber array alignment error: 0.5 µm."""
    # TODO: Expand fiber_alignment_threshold() - stub detected by Yeshua Agent
    return Fraction(1, 2)


def co_packaged_optics_pitch_threshold() -> Fraction:
    """OIF CEI-112G minimum pitch for standard fiber array: 250 µm."""
    # TODO: Expand co_packaged_optics_pitch_threshold() - stub detected by Yeshua Agent
    return Fraction(250, 1)


def solder_reflow_threshold() -> Fraction:
    """IPC J-STD-020 minimum reflow cycles without failure: 3."""
    # TODO: Expand solder_reflow_threshold() - stub detected by Yeshua Agent
    return Fraction(3, 1)


def wire_bond_pull_threshold() -> Fraction:
    """MIL-STD-883 Method 2011 minimum pull force for 25 µm Au wire: 3 gf."""
    # TODO: Expand wire_bond_pull_threshold() - stub detected by Yeshua Agent
    return Fraction(3, 1)


def hermetic_leak_threshold() -> Fraction:
    """MIL-STD-883 Method 1014 maximum leak rate: 1e-8 atm·cc/s."""
    # TODO: Expand hermetic_leak_threshold() - stub detected by Yeshua Agent
    return Fraction(1, 100_000_000)


def die_void_threshold() -> Fraction:
    """Custom OE maximum die attach void percentage: 25%."""
    # TODO: Expand die_void_threshold() - stub detected by Yeshua Agent
    return Fraction(25, 100)


# ---------------------------------------------------------------------------
# Check functions
# ---------------------------------------------------------------------------

def check_fiber_array_alignment(arr: FiberArray) -> Tuple[bool, ProofObject]:
    """Fiber array alignment error must not exceed 0.5 µm (Custom OE).

    Falsifies if: alignment_error_um > Fraction(1, 2).
    falsifies_if: alignment_error_um > Fraction(1, 2).
    """
    limit = fiber_alignment_threshold()
    if arr.alignment_error_um > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {arr.array_id} alignment error {arr.alignment_error_um} µm > "
                f"limit {limit} µm"
            ),
            premises=[
                f"Alignment error: {arr.alignment_error_um} µm",
                f"Limit: {limit} µm",
            ],
            rule="oe_fiber_alignment",
        )
    return True, ProofObject(
        conclusion=f"{arr.array_id} alignment error {arr.alignment_error_um} µm <= {limit} µm",
        premises=[f"Alignment error: {arr.alignment_error_um} µm <= {limit} µm"],
        rule="oe_fiber_alignment",
    )


def check_co_packaged_optics_pitch(pkg: CoPackagedOptics) -> Tuple[bool, ProofObject]:
    """Co-packaged optics pitch must be at least 250 µm per OIF CEI-112G.

    Falsifies if: pitch_um < Fraction(250, 1).
    falsifies_if: pitch_um < Fraction(250, 1).
    """
    limit = co_packaged_optics_pitch_threshold()
    if pkg.pitch_um < limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {pkg.package_id} pitch {pkg.pitch_um} µm < "
                f"minimum {limit} µm"
            ),
            premises=[
                f"Pitch: {pkg.pitch_um} µm",
                f"Minimum: {limit} µm",
            ],
            rule="oif_cei_112g_pitch",
        )
    return True, ProofObject(
        conclusion=f"{pkg.package_id} pitch {pkg.pitch_um} µm >= {limit} µm",
        premises=[f"Pitch: {pkg.pitch_um} µm >= {limit} µm"],
        rule="oif_cei_112g_pitch",
    )


def check_solder_joint_reliability(joint: SolderJoint) -> Tuple[bool, ProofObject]:
    """Solder joint must survive at least 3 reflow cycles per IPC J-STD-020.

    Falsifies if: reflow_cycles < Fraction(3, 1) OR failed is True.
    falsifies_if: reflow_cycles < Fraction(3, 1) or failed is True.
    """
    limit = solder_reflow_threshold()
    if joint.reflow_cycles < limit or joint.failed:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {joint.joint_id} reflow {joint.reflow_cycles} cycles < "
                f"minimum {limit} or failed={joint.failed}"
            ),
            premises=[
                f"Reflow cycles: {joint.reflow_cycles}",
                f"Failed: {joint.failed}",
                f"Minimum: {limit}",
            ],
            rule="ipc_j_std_020_solder",
        )
    return True, ProofObject(
        conclusion=f"{joint.joint_id} solder joint reliable ({joint.reflow_cycles} cycles >= {limit})",
        premises=[f"Reflow cycles: {joint.reflow_cycles} >= {limit}", f"Failed: {joint.failed}"],
        rule="ipc_j_std_020_solder",
    )


def check_wire_bond_pull_strength(bond: WireBond) -> Tuple[bool, ProofObject]:
    """Wire bond pull strength must be at least 3 gf per MIL-STD-883 Method 2011.

    Falsifies if: pull_force_gf < Fraction(3, 1).
    falsifies_if: pull_force_gf < Fraction(3, 1).
    """
    limit = wire_bond_pull_threshold()
    if bond.pull_force_gf < limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {bond.bond_id} pull force {bond.pull_force_gf} gf < "
                f"minimum {limit} gf"
            ),
            premises=[
                f"Pull force: {bond.pull_force_gf} gf",
                f"Minimum: {limit} gf",
            ],
            rule="mil_std_883_wire_bond",
        )
    return True, ProofObject(
        conclusion=f"{bond.bond_id} pull force {bond.pull_force_gf} gf >= {limit} gf",
        premises=[f"Pull force: {bond.pull_force_gf} gf >= {limit} gf"],
        rule="mil_std_883_wire_bond",
    )


def check_hermetic_seal(seal: HermeticSeal) -> Tuple[bool, ProofObject]:
    """Hermetic seal leak rate must not exceed 1e-8 atm·cc/s per MIL-STD-883 Method 1014.

    Falsifies if: leak_rate > Fraction(1, 100_000_000).
    falsifies_if: leak_rate > Fraction(1, 100_000_000).
    """
    limit = hermetic_leak_threshold()
    if seal.leak_rate > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {seal.seal_id} leak rate {seal.leak_rate} atm·cc/s > "
                f"limit {limit} atm·cc/s"
            ),
            premises=[
                f"Leak rate: {seal.leak_rate} atm·cc/s",
                f"Limit: {limit} atm·cc/s",
            ],
            rule="mil_std_883_hermetic",
        )
    return True, ProofObject(
        conclusion=f"{seal.seal_id} leak rate {seal.leak_rate} atm·cc/s <= {limit} atm·cc/s",
        premises=[f"Leak rate: {seal.leak_rate} atm·cc/s <= {limit} atm·cc/s"],
        rule="mil_std_883_hermetic",
    )


def check_die_attach_void(attach: DieAttach) -> Tuple[bool, ProofObject]:
    """Die attach void percentage must not exceed 25% (Custom OE).

    Falsifies if: void_percentage > Fraction(25, 100).
    falsifies_if: void_percentage > Fraction(25, 100).
    """
    limit = die_void_threshold()
    if attach.void_percentage > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {attach.attach_id} void {attach.void_percentage} > "
                f"limit {limit}"
            ),
            premises=[
                f"Void: {attach.void_percentage}",
                f"Limit: {limit}",
            ],
            rule="oe_die_attach_void",
        )
    return True, ProofObject(
        conclusion=f"{attach.attach_id} void {attach.void_percentage} <= {limit}",
        premises=[f"Void: {attach.void_percentage} <= {limit}"],
        rule="oe_die_attach_void",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> list:
    """Run all packaging checks with passing and failing test data.

    falsifies_if: any check fails or raises an exception.
    """
    pass_arr = FiberArray(array_id="pass_arr", alignment_error_um=Fraction(3, 10))
    fail_arr = FiberArray(array_id="fail_arr", alignment_error_um=Fraction(7, 10))
    pass_pkg = CoPackagedOptics(package_id="pass_pkg", pitch_um=Fraction(300, 1))
    fail_pkg = CoPackagedOptics(package_id="fail_pkg", pitch_um=Fraction(200, 1))
    pass_joint = SolderJoint(joint_id="pass_joint", reflow_cycles=Fraction(5, 1), failed=False)
    fail_joint = SolderJoint(joint_id="fail_joint", reflow_cycles=Fraction(2, 1), failed=False)
    pass_bond = WireBond(bond_id="pass_bond", pull_force_gf=Fraction(4, 1))
    fail_bond = WireBond(bond_id="fail_bond", pull_force_gf=Fraction(2, 1))
    pass_seal = HermeticSeal(seal_id="pass_seal", leak_rate=Fraction(1, 1_000_000_000))
    fail_seal = HermeticSeal(seal_id="fail_seal", leak_rate=Fraction(1, 10_000_000))
    pass_attach = DieAttach(attach_id="pass_attach", void_percentage=Fraction(15, 100))
    fail_attach = DieAttach(attach_id="fail_attach", void_percentage=Fraction(35, 100))

    checks = [
        ("check_fiber_array_alignment_pass", lambda: check_fiber_array_alignment(pass_arr)),
        ("check_fiber_array_alignment_fail", lambda: check_fiber_array_alignment(fail_arr)),
        ("check_co_packaged_optics_pitch_pass", lambda: check_co_packaged_optics_pitch(pass_pkg)),
        ("check_co_packaged_optics_pitch_fail", lambda: check_co_packaged_optics_pitch(fail_pkg)),
        ("check_solder_joint_reliability_pass", lambda: check_solder_joint_reliability(pass_joint)),
        ("check_solder_joint_reliability_fail", lambda: check_solder_joint_reliability(fail_joint)),
        ("check_wire_bond_pull_strength_pass", lambda: check_wire_bond_pull_strength(pass_bond)),
        ("check_wire_bond_pull_strength_fail", lambda: check_wire_bond_pull_strength(fail_bond)),
        ("check_hermetic_seal_pass", lambda: check_hermetic_seal(pass_seal)),
        ("check_hermetic_seal_fail", lambda: check_hermetic_seal(fail_seal)),
        ("check_die_attach_void_pass", lambda: check_die_attach_void(pass_attach)),
        ("check_die_attach_void_fail", lambda: check_die_attach_void(fail_attach)),
    ]

    results = []
    for name, func in checks:
        try:
            ok, proof = func()
            results.append((name, ok, proof))
        except Exception as exc:
            fake_proof = ProofObject(
                conclusion=f"ERROR in {name}: {exc}",
                premises=[],
                rule=name,
            )
            results.append((name, False, fake_proof))

    return results
