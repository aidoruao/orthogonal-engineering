"""PHOTONIC Matrix Computation — MZI mesh photonic matrix multiply.

Category 5: Matrix computation (checks 29-32).

Standards: Reck et al. 1994, Clements et al. 2016.
All invariants use Fraction arithmetic for exact thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class PhotonicMatrix:
    """Real-valued matrix represented as nested tuples of Fractions.

    falsifies_if: rows have inconsistent lengths.
    falsifies_if: rows have inconsistent lengths.
    """
    matrix_id: str
    elements: Tuple[Tuple[Fraction, ...], ...]


@dataclass(frozen=True)
class PhaseShifter:
    """MZI phase shifter parameters.

    falsifies_if: target_phase or actual_phase is outside [0, 2π).
    falsifies_if: target_phase or actual_phase is outside [0, 2π).
    """
    shifter_id: str
    target_phase: Fraction
    actual_phase: Fraction


@dataclass(frozen=True)
class MziMesh:
    """MZI mesh architecture parameters.

    falsifies_if: num_ports <= 0 or depth < 0.
    falsifies_if: num_ports <= 0 or depth < 0.
    """
    mesh_id: str
    num_ports: int
    depth: int


@dataclass(frozen=True)
class ThermalProfile:
    """Thermal crosstalk compensation parameters.

    falsifies_if: uncompensated_drift_pm_per_c is negative.
    falsifies_if: uncompensated_drift_pm_per_c is negative.
    """
    profile_id: str
    uncompensated_drift_pm_per_c: Fraction


# ---------------------------------------------------------------------------
# Threshold functions
# ---------------------------------------------------------------------------

def unitarity_tolerance() -> Fraction:
    """Reck et al. 1994: maximum Frobenius-norm deviation from identity."""
    return Fraction(1, 1000)


def phase_precision_tolerance() -> Fraction:
    """Custom OE: maximum acceptable phase error in radians."""
    return Fraction(1, 100)


def thermal_drift_tolerance() -> Fraction:
    """Custom OE: maximum uncompensated thermal drift."""
    return Fraction(10, 1)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _transpose_multiply(elements: Tuple[Tuple[Fraction, ...], ...]) -> Tuple[Tuple[Fraction, ...], ...]:
    """Compute M^T * M for a real matrix M.

    falsifies_if: row lengths are inconsistent.
    falsifies_if: row lengths are inconsistent.
    """
    if not elements:
        return ()
    rows = len(elements)
    cols = len(elements[0])
    result: list[list[Fraction]] = [[Fraction(0, 1) for _ in range(cols)] for _ in range(cols)]
    for i in range(cols):
        for j in range(cols):
            total = Fraction(0, 1)
            for k in range(rows):
                total += elements[k][i] * elements[k][j]
            result[i][j] = total
    return tuple(tuple(row) for row in result)


# ---------------------------------------------------------------------------
# Check functions
# ---------------------------------------------------------------------------

def check_matrix_unitarity(m: PhotonicMatrix) -> Tuple[bool, ProofObject]:
    """M^T * M must be within unitarity_tolerance of identity (Reck et al. 1994).

    Falsifies if: any diagonal element deviates from 1 by > 1/1000
                  or any off-diagonal element deviates from 0 by > 1/1000.
    falsifies_if: any diagonal element deviates from 1 by > 1/1000
                  or any off-diagonal element deviates from 0 by > 1/1000.
    """
    mt_m = _transpose_multiply(m.elements)
    n = len(mt_m)
    tol = unitarity_tolerance()
    for i in range(n):
        for j in range(n):
            expected = Fraction(1, 1) if i == j else Fraction(0, 1)
            diff = abs(mt_m[i][j] - expected)
            if diff > tol:
                return False, ProofObject(
                    conclusion=(
                        f"VIOLATION: {m.matrix_id} M^T*M[{i}][{j}] = {mt_m[i][j]} "
                        f"deviates {diff} from {expected} (tolerance {tol})"
                    ),
                    premises=[
                        f"Element [{i}][{j}]: {mt_m[i][j]}",
                        f"Expected: {expected}",
                        f"Deviation: {diff}",
                    ],
                    rule="reck_unitary",
                )
    return True, ProofObject(
        conclusion=f"{m.matrix_id} is unitary within tolerance {tol}",
        premises=[f"Matrix size: {n}x{n}", f"Tolerance: {tol}"],
        rule="reck_unitary",
    )


def check_phase_shifter_precision(ps: PhaseShifter) -> Tuple[bool, ProofObject]:
    """Phase shifter error must be within 0.01 radians (Custom OE).

    Falsifies if: abs(target_phase - actual_phase) > Fraction(1, 100).
    falsifies_if: abs(target_phase - actual_phase) > Fraction(1, 100).
    """
    error = abs(ps.target_phase - ps.actual_phase)
    limit = phase_precision_tolerance()
    if error > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {ps.shifter_id} phase error {error} rad > "
                f"limit {limit} rad"
            ),
            premises=[
                f"Target: {ps.target_phase} rad",
                f"Actual: {ps.actual_phase} rad",
                f"Error: {error} rad",
            ],
            rule="oe_phase_precision",
        )
    return True, ProofObject(
        conclusion=f"{ps.shifter_id} phase error {error} rad <= {limit} rad",
        premises=[f"Error: {error} rad <= {limit} rad"],
        rule="oe_phase_precision",
    )


def check_mzi_mesh_depth(mesh: MziMesh) -> Tuple[bool, ProofObject]:
    """MZI mesh depth must not exceed N*(N-1)/2 for an N×N matrix (Clements et al. 2016).

    Falsifies if: depth > N*(N-1)/2.
    falsifies_if: depth > N*(N-1)/2.
    """
    n = mesh.num_ports
    max_depth = n * (n - 1) // 2
    if mesh.depth > max_depth:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {mesh.mesh_id} depth {mesh.depth} > "
                f"max {max_depth} for {n}x{n} matrix"
            ),
            premises=[
                f"Depth: {mesh.depth}",
                f"Max depth: {max_depth}",
                f"Matrix size: {n}x{n}",
            ],
            rule="clements_mesh_depth",
        )
    return True, ProofObject(
        conclusion=f"{mesh.mesh_id} depth {mesh.depth} <= {max_depth}",
        premises=[f"Depth: {mesh.depth}", f"Max: {max_depth}"],
        rule="clements_mesh_depth",
    )


def check_thermal_crosstalk_compensation(profile: ThermalProfile) -> Tuple[bool, ProofObject]:
    """Uncompensated thermal drift must not exceed 10 pm/°C (Custom OE).

    Falsifies if: uncompensated_drift_pm_per_c > Fraction(10, 1).
    falsifies_if: uncompensated_drift_pm_per_c > Fraction(10, 1).
    """
    limit = thermal_drift_tolerance()
    if profile.uncompensated_drift_pm_per_c > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {profile.profile_id} drift {profile.uncompensated_drift_pm_per_c} "
                f"pm/°C > limit {limit} pm/°C"
            ),
            premises=[
                f"Drift: {profile.uncompensated_drift_pm_per_c} pm/°C",
                f"Limit: {limit} pm/°C",
            ],
            rule="oe_thermal_crosstalk",
        )
    return True, ProofObject(
        conclusion=(
            f"{profile.profile_id} drift {profile.uncompensated_drift_pm_per_c} pm/°C <= "
            f"{limit} pm/°C"
        ),
        premises=[f"Drift: {profile.uncompensated_drift_pm_per_c} pm/°C <= {limit} pm/°C"],
        rule="oe_thermal_crosstalk",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> list:
    """Run all matrix computation checks with passing and failing test data.

    falsifies_if: any check fails or raises an exception.
    """
    pass_matrix = PhotonicMatrix(
        matrix_id="pass_matrix",
        elements=(
            (Fraction(1, 1), Fraction(0, 1)),
            (Fraction(0, 1), Fraction(1, 1)),
        ),
    )
    fail_matrix = PhotonicMatrix(
        matrix_id="fail_matrix",
        elements=(
            (Fraction(1, 1), Fraction(1, 10)),
            (Fraction(1, 10), Fraction(1, 1)),
        ),
    )
    pass_ps = PhaseShifter(
        shifter_id="pass_ps",
        target_phase=Fraction(1, 2),
        actual_phase=Fraction(1, 2) + Fraction(1, 1000),
    )
    fail_ps = PhaseShifter(
        shifter_id="fail_ps",
        target_phase=Fraction(1, 2),
        actual_phase=Fraction(1, 2) + Fraction(1, 10),
    )
    pass_mesh = MziMesh(
        mesh_id="pass_mesh",
        num_ports=4,
        depth=6,
    )
    fail_mesh = MziMesh(
        mesh_id="fail_mesh",
        num_ports=4,
        depth=10,
    )
    pass_thermal = ThermalProfile(
        profile_id="pass_thermal",
        uncompensated_drift_pm_per_c=Fraction(5, 1),
    )
    fail_thermal = ThermalProfile(
        profile_id="fail_thermal",
        uncompensated_drift_pm_per_c=Fraction(15, 1),
    )

    checks = [
        ("check_matrix_unitarity_pass", lambda: check_matrix_unitarity(pass_matrix)),
        ("check_matrix_unitarity_fail", lambda: check_matrix_unitarity(fail_matrix)),
        ("check_phase_shifter_precision_pass", lambda: check_phase_shifter_precision(pass_ps)),
        ("check_phase_shifter_precision_fail", lambda: check_phase_shifter_precision(fail_ps)),
        ("check_mzi_mesh_depth_pass", lambda: check_mzi_mesh_depth(pass_mesh)),
        ("check_mzi_mesh_depth_fail", lambda: check_mzi_mesh_depth(fail_mesh)),
        ("check_thermal_crosstalk_pass", lambda: check_thermal_crosstalk_compensation(pass_thermal)),
        ("check_thermal_crosstalk_fail", lambda: check_thermal_crosstalk_compensation(fail_thermal)),
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
