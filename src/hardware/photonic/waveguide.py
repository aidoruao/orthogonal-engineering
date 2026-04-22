"""PHOTONIC Waveguide — Silicon photonic waveguide parameters.

Category 5: Waveguide (checks 33-36).

Standards: Custom OE literature, ITU-T G.652.
All invariants use Fraction arithmetic for exact thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class SiliconWaveguide:
    """Silicon photonic waveguide physical parameters.

    falsifies_if: any parameter is negative.
    falsifies_if: any parameter is negative.
    """
    waveguide_id: str
    propagation_loss_db_per_cm: Fraction
    bend_radius_um: Fraction
    confinement_factor: Fraction
    dispersion_ps_per_nm_km: Fraction


# ---------------------------------------------------------------------------
# Threshold functions
# ---------------------------------------------------------------------------

def propagation_loss_threshold() -> Fraction:
    """Custom OE / literature maximum propagation loss: 1 dB/cm."""
    return Fraction(1, 1)


def bend_radius_threshold() -> Fraction:
    """Custom OE minimum bend radius for silicon: 5 µm."""
    return Fraction(5, 1)


def confinement_threshold() -> Fraction:
    """Custom OE minimum mode confinement factor: 0.8."""
    return Fraction(8, 10)


def dispersion_threshold() -> Fraction:
    """ITU-T G.652 maximum waveguide dispersion: 18 ps/(nm·km)."""
    return Fraction(18, 1)


# ---------------------------------------------------------------------------
# Check functions
# ---------------------------------------------------------------------------

def check_propagation_loss(wg: SiliconWaveguide) -> Tuple[bool, ProofObject]:
    """Propagation loss must not exceed 1 dB/cm (Custom OE / literature).

    Falsifies if: propagation_loss_db_per_cm > Fraction(1, 1).
    falsifies_if: propagation_loss_db_per_cm > Fraction(1, 1).
    """
    limit = propagation_loss_threshold()
    if wg.propagation_loss_db_per_cm > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {wg.waveguide_id} propagation loss {wg.propagation_loss_db_per_cm} "
                f"dB/cm > limit {limit} dB/cm"
            ),
            premises=[
                f"Loss: {wg.propagation_loss_db_per_cm} dB/cm",
                f"Limit: {limit} dB/cm",
            ],
            rule="oe_propagation_loss",
        )
    return True, ProofObject(
        conclusion=f"{wg.waveguide_id} loss {wg.propagation_loss_db_per_cm} dB/cm <= {limit} dB/cm",
        premises=[f"Loss: {wg.propagation_loss_db_per_cm} dB/cm <= {limit} dB/cm"],
        rule="oe_propagation_loss",
    )


def check_bend_radius_minimum(wg: SiliconWaveguide) -> Tuple[bool, ProofObject]:
    """Bend radius must be at least 5 µm for silicon (Custom OE).

    Falsifies if: bend_radius_um < Fraction(5, 1).
    falsifies_if: bend_radius_um < Fraction(5, 1).
    """
    limit = bend_radius_threshold()
    if wg.bend_radius_um < limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {wg.waveguide_id} bend radius {wg.bend_radius_um} µm < "
                f"minimum {limit} µm"
            ),
            premises=[
                f"Bend radius: {wg.bend_radius_um} µm",
                f"Minimum: {limit} µm",
            ],
            rule="oe_bend_radius",
        )
    return True, ProofObject(
        conclusion=f"{wg.waveguide_id} bend radius {wg.bend_radius_um} µm >= {limit} µm",
        premises=[f"Bend radius: {wg.bend_radius_um} µm >= {limit} µm"],
        rule="oe_bend_radius",
    )


def check_mode_confinement(wg: SiliconWaveguide) -> Tuple[bool, ProofObject]:
    """Mode confinement factor must be at least 0.8 (Custom OE).

    Falsifies if: confinement_factor < Fraction(8, 10).
    falsifies_if: confinement_factor < Fraction(8, 10).
    """
    limit = confinement_threshold()
    if wg.confinement_factor < limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {wg.waveguide_id} confinement {wg.confinement_factor} < "
                f"minimum {limit}"
            ),
            premises=[
                f"Confinement: {wg.confinement_factor}",
                f"Minimum: {limit}",
            ],
            rule="oe_mode_confinement",
        )
    return True, ProofObject(
        conclusion=f"{wg.waveguide_id} confinement {wg.confinement_factor} >= {limit}",
        premises=[f"Confinement: {wg.confinement_factor} >= {limit}"],
        rule="oe_mode_confinement",
    )


def check_waveguide_dispersion(wg: SiliconWaveguide) -> Tuple[bool, ProofObject]:
    """Waveguide dispersion must not exceed 18 ps/(nm·km) per ITU-T G.652.

    Falsifies if: dispersion_ps_per_nm_km > Fraction(18, 1).
    falsifies_if: dispersion_ps_per_nm_km > Fraction(18, 1).
    """
    limit = dispersion_threshold()
    if wg.dispersion_ps_per_nm_km > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {wg.waveguide_id} dispersion {wg.dispersion_ps_per_nm_km} "
                f"ps/(nm·km) > limit {limit} ps/(nm·km)"
            ),
            premises=[
                f"Dispersion: {wg.dispersion_ps_per_nm_km} ps/(nm·km)",
                f"Limit: {limit} ps/(nm·km)",
            ],
            rule="itu_g652_dispersion",
        )
    return True, ProofObject(
        conclusion=(
            f"{wg.waveguide_id} dispersion {wg.dispersion_ps_per_nm_km} ps/(nm·km) <= "
            f"{limit} ps/(nm·km)"
        ),
        premises=[f"Dispersion: {wg.dispersion_ps_per_nm_km} ps/(nm·km) <= {limit} ps/(nm·km)"],
        rule="itu_g652_dispersion",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> list:
    """Run all waveguide checks with passing and failing test data.

    falsifies_if: any check fails or raises an exception.
    """
    pass_wg = SiliconWaveguide(
        waveguide_id="pass_wg",
        propagation_loss_db_per_cm=Fraction(3, 10),
        bend_radius_um=Fraction(10, 1),
        confinement_factor=Fraction(9, 10),
        dispersion_ps_per_nm_km=Fraction(10, 1),
    )
    fail_wg = SiliconWaveguide(
        waveguide_id="fail_wg",
        propagation_loss_db_per_cm=Fraction(2, 1),
        bend_radius_um=Fraction(2, 1),
        confinement_factor=Fraction(5, 10),
        dispersion_ps_per_nm_km=Fraction(25, 1),
    )

    checks = [
        ("check_propagation_loss_pass", lambda: check_propagation_loss(pass_wg)),
        ("check_propagation_loss_fail", lambda: check_propagation_loss(fail_wg)),
        ("check_bend_radius_minimum_pass", lambda: check_bend_radius_minimum(pass_wg)),
        ("check_bend_radius_minimum_fail", lambda: check_bend_radius_minimum(fail_wg)),
        ("check_mode_confinement_pass", lambda: check_mode_confinement(pass_wg)),
        ("check_mode_confinement_fail", lambda: check_mode_confinement(fail_wg)),
        ("check_waveguide_dispersion_pass", lambda: check_waveguide_dispersion(pass_wg)),
        ("check_waveguide_dispersion_fail", lambda: check_waveguide_dispersion(fail_wg)),
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
