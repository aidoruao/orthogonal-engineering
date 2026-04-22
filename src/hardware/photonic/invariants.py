"""PHOTONIC Invariants — GDSII & TRL 9 photonic computation campaign

Category 1: Domain foundation
All invariants use Fraction arithmetic for exact thresholds.
"""

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    MachZehnderInterferometer,
    PhotonicChip,
    PhotonicWaveguide,
    extinction_ratio_db,
    minimum_bend_radius,
    v_number,
)


def check_single_mode_condition(wg: PhotonicWaveguide) -> Tuple[bool, ProofObject]:
    """Waveguide must be single-mode per Marcuse criterion.

    Falsifies if: V-number >= Fraction(2405, 1000).
    falsifies_if: V-number >= Fraction(2405, 1000).
    """
    v = v_number(wg)
    threshold = Fraction(2405, 1000)

    if v >= threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: Waveguide V-number {v} >= {threshold} (multi-mode)",
            premises=[
                f"V-number: {v}",
                f"Threshold: {threshold}",
                f"Core width: {wg.core_width} nm",
                f"Wavelength: {wg.wavelength_nm} nm",
            ],
            rule="marcuse_single_mode",
        )

    return True, ProofObject(
        conclusion=f"Waveguide single-mode OK (V={v} < {threshold})",
        premises=[f"V-number: {v} < {threshold}"],
        rule="marcuse_single_mode",
    )


def check_bend_loss_budget(
    wg: PhotonicWaveguide, bend_radius_um: Fraction
) -> Tuple[bool, ProofObject]:
    """Bend radius must exceed minimum for wavelength to avoid excessive loss.

    Falsifies if: bend_radius_um <= minimum_bend_radius(wavelength_nm).
    falsifies_if: bend_radius_um <= minimum_bend_radius(wavelength_nm).
    """
    min_radius = minimum_bend_radius(wg.wavelength_nm)

    if bend_radius_um <= min_radius:
        return False, ProofObject(
            conclusion=f"VIOLATION: Bend radius {bend_radius_um} um <= minimum {min_radius} um",
            premises=[
                f"Bend radius: {bend_radius_um} um",
                f"Minimum: {min_radius} um",
                f"Wavelength: {wg.wavelength_nm} nm",
            ],
            rule="bend_loss_budget",
        )

    return True, ProofObject(
        conclusion=f"Bend radius {bend_radius_um} um > minimum {min_radius} um",
        premises=[f"Bend radius: {bend_radius_um} um > {min_radius} um"],
        rule="bend_loss_budget",
    )


def check_insertion_loss_budget(
    chip: PhotonicChip, link_budget_db: Fraction
) -> Tuple[bool, ProofObject]:
    """Total insertion loss must be within link budget.

    Falsifies if: total_insertion_loss_db >= link_budget_db.
    falsifies_if: total_insertion_loss_db >= link_budget_db.
    """
    if chip.total_insertion_loss_db >= link_budget_db:
        return False, ProofObject(
            conclusion=f"VIOLATION: Insertion loss {chip.total_insertion_loss_db} dB >= budget {link_budget_db} dB",
            premises=[
                f"Insertion loss: {chip.total_insertion_loss_db} dB",
                f"Link budget: {link_budget_db} dB",
            ],
            rule="insertion_loss_budget",
        )

    return True, ProofObject(
        conclusion=f"Insertion loss {chip.total_insertion_loss_db} dB < budget {link_budget_db} dB",
        premises=[f"Insertion loss: {chip.total_insertion_loss_db} dB < {link_budget_db} dB"],
        rule="insertion_loss_budget",
    )


def check_extinction_ratio(mzi: MachZehnderInterferometer) -> Tuple[bool, ProofObject]:
    """Extinction ratio must exceed 20 dB for digital modulation.

    Falsifies if: ER <= Fraction(20, 1).
    falsifies_if: ER <= Fraction(20, 1).
    """
    er = extinction_ratio_db(mzi)
    threshold = Fraction(20, 1)

    if er <= threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: Extinction ratio {er} dB <= {threshold} dB",
            premises=[
                f"ER: {er} dB",
                f"Threshold: {threshold} dB",
                f"Splitting ratio: {mzi.splitting_ratio}",
            ],
            rule="extinction_ratio_digital",
        )

    return True, ProofObject(
        conclusion=f"Extinction ratio {er} dB > {threshold} dB",
        premises=[f"ER: {er} dB > {threshold} dB"],
        rule="extinction_ratio_digital",
    )


def check_phase_error_tolerance(mzi: MachZehnderInterferometer) -> Tuple[bool, ProofObject]:
    """Phase error must be below 0.01 radians.

    Falsifies if: phase_shift >= Fraction(1, 100).
    falsifies_if: phase_shift >= Fraction(1, 100).
    """
    threshold = Fraction(1, 100)

    if mzi.phase_shift >= threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: Phase error {mzi.phase_shift} rad >= {threshold} rad",
            premises=[
                f"Phase shift: {mzi.phase_shift} rad",
                f"Threshold: {threshold} rad",
            ],
            rule="phase_error_tolerance",
        )

    return True, ProofObject(
        conclusion=f"Phase error {mzi.phase_shift} rad < {threshold} rad",
        premises=[f"Phase shift: {mzi.phase_shift} rad < {threshold} rad"],
        rule="phase_error_tolerance",
    )


def check_thermal_tuning_range(
    tuning_range_nm: Fraction, fsr_nm: Fraction
) -> Tuple[bool, ProofObject]:
    """Thermal tuning range must cover the free spectral range.

    Falsifies if: tuning_range_nm < fsr_nm.
    falsifies_if: tuning_range_nm < fsr_nm.
    """
    if tuning_range_nm < fsr_nm:
        return False, ProofObject(
            conclusion=f"VIOLATION: Tuning range {tuning_range_nm} nm < FSR {fsr_nm} nm",
            premises=[
                f"Tuning range: {tuning_range_nm} nm",
                f"FSR: {fsr_nm} nm",
            ],
            rule="thermal_tuning_range",
        )

    return True, ProofObject(
        conclusion=f"Tuning range {tuning_range_nm} nm >= FSR {fsr_nm} nm",
        premises=[f"Tuning range: {tuning_range_nm} nm >= {fsr_nm} nm"],
        rule="thermal_tuning_range",
    )


def run_all_invariants() -> dict:
    """Run all PHOTONIC invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    wg = PhotonicWaveguide(
        core_width=Fraction(500, 1),
        cladding_index=Fraction(144, 100),
        core_index=Fraction(330, 100),
        wavelength_nm=Fraction(1550, 1),
        propagation_loss_db_per_cm=Fraction(1, 10),
    )
    mzi = MachZehnderInterferometer(
        arm_length_1=Fraction(100, 1),
        arm_length_2=Fraction(100, 1),
        phase_shift=Fraction(0, 1),
        splitting_ratio=Fraction(1, 2),
    )
    chip = PhotonicChip(
        waveguides=(wg,),
        mzis=(mzi,),
        total_insertion_loss_db=Fraction(3, 1),
        chip_area_mm2=Fraction(10, 1),
    )

    checks = [
        ("check_single_mode_condition", lambda: check_single_mode_condition(wg)),
        (
            "check_bend_loss_budget",
            lambda: check_bend_loss_budget(wg, Fraction(20000, 1)),
        ),
        (
            "check_insertion_loss_budget",
            lambda: check_insertion_loss_budget(chip, Fraction(10, 1)),
        ),
        ("check_extinction_ratio", lambda: check_extinction_ratio(mzi)),
        ("check_phase_error_tolerance", lambda: check_phase_error_tolerance(mzi)),
        (
            "check_thermal_tuning_range",
            lambda: check_thermal_tuning_range(Fraction(20, 1), Fraction(10, 1)),
        ),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            result = func()
            if isinstance(result, tuple) and len(result) == 2:
                success, proof = result
                results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
            else:
                passed = getattr(result, "passed", True)
                results[name] = "PASS" if passed else "FAIL: " + str(
                    getattr(result, "evidence", result)
                )
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results
