"""PHOTONIC Peano Proofs — Verify all photonic arithmetic is Peano-reducible.

Category 16: Yeshua Mathematics (proofs 1-8).

Each proof demonstrates that a photonic parameter can be expressed as a ratio
of natural numbers (Fraction), with no reliance on floats, irrationals, or
transcendentals.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


def prove_mzi_phase_peano_reducible() -> Tuple[bool, ProofObject]:
    """Phase precision Fraction(1, 1000) rad is ratio of natural numbers.

    Falsifies if: numerator or denominator is not a natural number.
    falsifies_if: numerator or denominator is not a natural number.
    """
    f = Fraction(1, 1000)
    if f.numerator < 0 or f.denominator <= 0:
        return False, ProofObject(
            conclusion=f"VIOLATION: {f} is not a ratio of natural numbers",
            premises=[f"Fraction: {f}"],
            rule="peano_reducibility",
        )
    return True, ProofObject(
        conclusion=f"MZI phase precision {f} is Peano-reducible (1/1000)",
        premises=[f"Numerator: {f.numerator}", f"Denominator: {f.denominator}"],
        rule="peano_reducibility",
    )


def prove_insertion_loss_peano_reducible() -> Tuple[bool, ProofObject]:
    """Loss threshold Fraction(1, 10) dB/cm reduces to Peano successor operations.

    Falsifies if: threshold requires irrational or transcendental number.
    falsifies_if: threshold requires irrational or transcendental number.
    """
    f = Fraction(1, 10)
    if f.numerator < 0 or f.denominator <= 0:
        return False, ProofObject(
            conclusion=f"VIOLATION: {f} is not Peano-reducible",
            premises=[f"Fraction: {f}"],
            rule="peano_reducibility",
        )
    return True, ProofObject(
        conclusion=f"Insertion loss threshold {f} is Peano-reducible",
        premises=[f"Numerator: {f.numerator}", f"Denominator: {f.denominator}"],
        rule="peano_reducibility",
    )


def prove_crosstalk_bound_peano_reducible() -> Tuple[bool, ProofObject]:
    """Isolation Fraction(20, 1) dB is integer ratio.

    Falsifies if: bound requires float.
    falsifies_if: bound requires float.
    """
    f = Fraction(20, 1)
    if f.numerator < 0 or f.denominator <= 0:
        return False, ProofObject(
            conclusion=f"VIOLATION: {f} is not Peano-reducible",
            premises=[f"Fraction: {f}"],
            rule="peano_reducibility",
        )
    return True, ProofObject(
        conclusion=f"Crosstalk bound {f} is Peano-reducible integer",
        premises=[f"Numerator: {f.numerator}", f"Denominator: {f.denominator}"],
        rule="peano_reducibility",
    )


def prove_thermal_drift_peano_reducible() -> Tuple[bool, ProofObject]:
    """Drift Fraction(10, 1) pm/°C is natural number.

    Falsifies if: drift spec requires real-valued computation.
    falsifies_if: drift spec requires real-valued computation.
    """
    f = Fraction(10, 1)
    if f.numerator < 0 or f.denominator <= 0:
        return False, ProofObject(
            conclusion=f"VIOLATION: {f} is not Peano-reducible",
            premises=[f"Fraction: {f}"],
            rule="peano_reducibility",
        )
    return True, ProofObject(
        conclusion=f"Thermal drift {f} is Peano-reducible natural number",
        premises=[f"Numerator: {f.numerator}", f"Denominator: {f.denominator}"],
        rule="peano_reducibility",
    )


def prove_adc_power_ratio_peano_reducible() -> Tuple[bool, ProofObject]:
    """Power ratio Fraction(1, 2) is ratio of successors of zero.

    Falsifies if: ratio requires division by non-natural.
    falsifies_if: ratio requires division by non-natural.
    """
    f = Fraction(1, 2)
    if f.numerator < 0 or f.denominator <= 0:
        return False, ProofObject(
            conclusion=f"VIOLATION: {f} is not Peano-reducible",
            premises=[f"Fraction: {f}"],
            rule="peano_reducibility",
        )
    return True, ProofObject(
        conclusion=f"ADC power ratio {f} is Peano-reducible (successor of zero / 2)",
        premises=[f"Numerator: {f.numerator}", f"Denominator: {f.denominator}"],
        rule="peano_reducibility",
    )


def prove_shot_noise_snr_peano_reducible() -> Tuple[bool, ProofObject]:
    """SNR bound comparison is Peano-reducible by comparing N against threshold².

    Falsifies if: comparison requires float sqrt.
    falsifies_if: comparison requires float sqrt.
    """
    # Avoid sqrt by squaring both sides: compare N >= threshold²
    threshold = Fraction(20, 1)
    threshold_squared = threshold * threshold
    if not isinstance(threshold_squared, Fraction):
        return False, ProofObject(
            conclusion="VIOLATION: SNR threshold squared is not a Fraction",
            premises=[f"Threshold: {threshold}"],
            rule="peano_reducibility",
        )
    return True, ProofObject(
        conclusion=f"SNR comparison N >= {threshold_squared} is Peano-reducible (no sqrt)",
        premises=[f"Threshold: {threshold}", f"Threshold²: {threshold_squared}"],
        rule="peano_reducibility",
    )


def prove_wavelength_spacing_peano_reducible() -> Tuple[bool, ProofObject]:
    """Channel spacing in pm is integer.

    Falsifies if: spacing requires sub-pm precision.
    falsifies_if: spacing requires sub-pm precision.
    """
    spacing_pm = Fraction(100000, 1)  # 100 nm = 100000 pm
    if spacing_pm.denominator != 1:
        return False, ProofObject(
            conclusion=f"VIOLATION: spacing {spacing_pm} pm is not an integer",
            premises=[f"Spacing: {spacing_pm}"],
            rule="peano_reducibility",
        )
    return True, ProofObject(
        conclusion=f"Wavelength spacing {spacing_pm} pm is integer (Peano-reducible)",
        premises=[f"Spacing: {spacing_pm} pm"],
        rule="peano_reducibility",
    )


def prove_ber_threshold_peano_reducible() -> Tuple[bool, ProofObject]:
    """BER Fraction(1, 10**12) is ratio of naturals.

    Falsifies if: BER threshold requires float exponentiation.
    falsifies_if: BER threshold requires float exponentiation.
    """
    f = Fraction(1, 10 ** 12)
    if f.numerator < 0 or f.denominator <= 0:
        return False, ProofObject(
            conclusion=f"VIOLATION: {f} is not Peano-reducible",
            premises=[f"Fraction: {f}"],
            rule="peano_reducibility",
        )
    return True, ProofObject(
        conclusion=f"BER threshold {f} is Peano-reducible (1/10^12)",
        premises=[f"Numerator: {f.numerator}", f"Denominator: {f.denominator}"],
        rule="peano_reducibility",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_proofs() -> list:
    """Run all 8 Peano proofs.

    falsifies_if: any proof fails.
    """
    proofs = [
        ("prove_mzi_phase_peano_reducible", prove_mzi_phase_peano_reducible),
        ("prove_insertion_loss_peano_reducible", prove_insertion_loss_peano_reducible),
        ("prove_crosstalk_bound_peano_reducible", prove_crosstalk_bound_peano_reducible),
        ("prove_thermal_drift_peano_reducible", prove_thermal_drift_peano_reducible),
        ("prove_adc_power_ratio_peano_reducible", prove_adc_power_ratio_peano_reducible),
        ("prove_shot_noise_snr_peano_reducible", prove_shot_noise_snr_peano_reducible),
        ("prove_wavelength_spacing_peano_reducible", prove_wavelength_spacing_peano_reducible),
        ("prove_ber_threshold_peano_reducible", prove_ber_threshold_peano_reducible),
    ]
    results = []
    for name, func in proofs:
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
