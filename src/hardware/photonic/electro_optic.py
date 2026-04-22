"""PHOTONIC Electro-Optic — ADC/DAC and E-O/O-E conversion.

Category 6: ADC/DAC & Electro-Optic Conversion (checks 37-43).

Standards: IEEE 1241, IEEE 1658, Custom OE, Landauer inversion.
All invariants use Fraction arithmetic for exact thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class AdcConverter:
    """Analog-to-digital converter parameters.

    falsifies_if: effective_bits is negative.
    falsifies_if: effective_bits is negative.
    """
    adc_id: str
    effective_bits: Fraction


@dataclass(frozen=True)
class DacConverter:
    """Digital-to-analog converter parameters.

    falsifies_if: sfdr_dbc is negative.
    falsifies_if: sfdr_dbc is negative.
    """
    dac_id: str
    sfdr_dbc: Fraction


@dataclass(frozen=True)
class OpticalModulator:
    """Electro-optic modulator parameters.

    falsifies_if: bandwidth_ghz or vpi_volts is negative.
    falsifies_if: bandwidth_ghz or vpi_volts is negative.
    """
    modulator_id: str
    bandwidth_ghz: Fraction
    vpi_volts: Fraction


@dataclass(frozen=True)
class Photodetector:
    """Photodetector / receiver front-end parameters.

    falsifies_if: responsivity is negative.
    falsifies_if: responsivity is negative.
    """
    detector_id: str
    responsivity: Fraction


@dataclass(frozen=True)
class TransimpedanceAmplifier:
    """Transimpedance amplifier parameters.

    falsifies_if: tia_gain_ohms is negative.
    falsifies_if: tia_gain_ohms is negative.
    """
    tia_id: str
    tia_gain_ohms: Fraction


@dataclass(frozen=True)
class ElectroOpticSystem:
    """System-level electro-optic power budget.

    falsifies_if: total_power is zero or negative.
    falsifies_if: total_power is zero or negative.
    """
    system_id: str
    adc_dac_power: Fraction
    total_power: Fraction


# ---------------------------------------------------------------------------
# Threshold functions
# ---------------------------------------------------------------------------

def adc_resolution_threshold() -> Fraction:
    """IEEE 1241 minimum effective bits: 8 bits."""
    return Fraction(8, 1)


def dac_sfdr_threshold() -> Fraction:
    """IEEE 1658 minimum SFDR: 40 dBc."""
    return Fraction(40, 1)


def modulator_bandwidth_threshold() -> Fraction:
    """Custom OE minimum modulator bandwidth for 50 Gbaud: 25 GHz."""
    return Fraction(25, 1)


def modulator_vpi_threshold() -> Fraction:
    """Custom OE maximum Vπ: 2 V."""
    return Fraction(2, 1)


def photodetector_responsivity_threshold() -> Fraction:
    """Custom OE minimum responsivity at 1550 nm: 0.8 A/W."""
    return Fraction(8, 10)


def transimpedance_gain_threshold() -> Fraction:
    """Custom OE minimum TIA gain: 5000 Ω."""
    return Fraction(5000, 1)


def eo_conversion_power_fraction() -> Fraction:
    """Landauer inversion — E-O/O-E power must stay below half of total."""
    return Fraction(1, 2)


# ---------------------------------------------------------------------------
# Check functions
# ---------------------------------------------------------------------------

def check_adc_resolution(adc: AdcConverter) -> Tuple[bool, ProofObject]:
    """ADC effective resolution must be at least 8 bits per IEEE 1241.

    Falsifies if: effective_bits < Fraction(8, 1).
    falsifies_if: effective_bits < Fraction(8, 1).
    """
    limit = adc_resolution_threshold()
    if adc.effective_bits < limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {adc.adc_id} effective bits {adc.effective_bits} < "
                f"minimum {limit}"
            ),
            premises=[
                f"Effective bits: {adc.effective_bits}",
                f"Minimum: {limit}",
            ],
            rule="ieee_1241_adc_resolution",
        )
    return True, ProofObject(
        conclusion=f"{adc.adc_id} effective bits {adc.effective_bits} >= {limit}",
        premises=[f"Effective bits: {adc.effective_bits} >= {limit}"],
        rule="ieee_1241_adc_resolution",
    )


def check_dac_sfdr(dac: DacConverter) -> Tuple[bool, ProofObject]:
    """DAC SFDR must be at least 40 dBc per IEEE 1658.

    Falsifies if: sfdr_dbc < Fraction(40, 1).
    falsifies_if: sfdr_dbc < Fraction(40, 1).
    """
    limit = dac_sfdr_threshold()
    if dac.sfdr_dbc < limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {dac.dac_id} SFDR {dac.sfdr_dbc} dBc < "
                f"minimum {limit} dBc"
            ),
            premises=[
                f"SFDR: {dac.sfdr_dbc} dBc",
                f"Minimum: {limit} dBc",
            ],
            rule="ieee_1658_dac_sfdr",
        )
    return True, ProofObject(
        conclusion=f"{dac.dac_id} SFDR {dac.sfdr_dbc} dBc >= {limit} dBc",
        premises=[f"SFDR: {dac.sfdr_dbc} dBc >= {limit} dBc"],
        rule="ieee_1658_dac_sfdr",
    )


def check_modulator_bandwidth(mod: OpticalModulator) -> Tuple[bool, ProofObject]:
    """Modulator bandwidth must be at least 25 GHz for 50 Gbaud (Custom OE).

    Falsifies if: bandwidth_ghz < Fraction(25, 1).
    falsifies_if: bandwidth_ghz < Fraction(25, 1).
    """
    limit = modulator_bandwidth_threshold()
    if mod.bandwidth_ghz < limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {mod.modulator_id} bandwidth {mod.bandwidth_ghz} GHz < "
                f"minimum {limit} GHz"
            ),
            premises=[
                f"Bandwidth: {mod.bandwidth_ghz} GHz",
                f"Minimum: {limit} GHz",
            ],
            rule="oe_modulator_bandwidth",
        )
    return True, ProofObject(
        conclusion=f"{mod.modulator_id} bandwidth {mod.bandwidth_ghz} GHz >= {limit} GHz",
        premises=[f"Bandwidth: {mod.bandwidth_ghz} GHz >= {limit} GHz"],
        rule="oe_modulator_bandwidth",
    )


def check_modulator_vpi(mod: OpticalModulator) -> Tuple[bool, ProofObject]:
    """Modulator Vπ must not exceed 2 V (Custom OE).

    Falsifies if: vpi_volts > Fraction(2, 1).
    falsifies_if: vpi_volts > Fraction(2, 1).
    """
    limit = modulator_vpi_threshold()
    if mod.vpi_volts > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {mod.modulator_id} Vπ {mod.vpi_volts} V > "
                f"maximum {limit} V"
            ),
            premises=[
                f"Vπ: {mod.vpi_volts} V",
                f"Maximum: {limit} V",
            ],
            rule="oe_modulator_vpi",
        )
    return True, ProofObject(
        conclusion=f"{mod.modulator_id} Vπ {mod.vpi_volts} V <= {limit} V",
        premises=[f"Vπ: {mod.vpi_volts} V <= {limit} V"],
        rule="oe_modulator_vpi",
    )


def check_photodetector_responsivity(det: Photodetector) -> Tuple[bool, ProofObject]:
    """Photodetector responsivity must be at least 0.8 A/W at 1550 nm (Custom OE).

    Falsifies if: responsivity < Fraction(8, 10).
    falsifies_if: responsivity < Fraction(8, 10).
    """
    limit = photodetector_responsivity_threshold()
    if det.responsivity < limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {det.detector_id} responsivity {det.responsivity} A/W < "
                f"minimum {limit} A/W"
            ),
            premises=[
                f"Responsivity: {det.responsivity} A/W",
                f"Minimum: {limit} A/W",
            ],
            rule="oe_photodetector_responsivity",
        )
    return True, ProofObject(
        conclusion=f"{det.detector_id} responsivity {det.responsivity} A/W >= {limit} A/W",
        premises=[f"Responsivity: {det.responsivity} A/W >= {limit} A/W"],
        rule="oe_photodetector_responsivity",
    )


def check_transimpedance_gain(tia: TransimpedanceAmplifier) -> Tuple[bool, ProofObject]:
    """TIA gain must be at least 5000 Ω (Custom OE).

    Falsifies if: tia_gain_ohms < Fraction(5000, 1).
    falsifies_if: tia_gain_ohms < Fraction(5000, 1).
    """
    limit = transimpedance_gain_threshold()
    if tia.tia_gain_ohms < limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {tia.tia_id} TIA gain {tia.tia_gain_ohms} Ω < "
                f"minimum {limit} Ω"
            ),
            premises=[
                f"TIA gain: {tia.tia_gain_ohms} Ω",
                f"Minimum: {limit} Ω",
            ],
            rule="oe_transimpedance_gain",
        )
    return True, ProofObject(
        conclusion=f"{tia.tia_id} TIA gain {tia.tia_gain_ohms} Ω >= {limit} Ω",
        premises=[f"TIA gain: {tia.tia_gain_ohms} Ω >= {limit} Ω"],
        rule="oe_transimpedance_gain",
    )


def check_eo_conversion_power(sys: ElectroOpticSystem) -> Tuple[bool, ProofObject]:
    """E-O/O-E conversion power must stay below half of total system power (Landauer inversion).

    If ADC/DAC power exceeds 50% of total, the photonic advantage is nullified.

    Falsifies if: adc_dac_power > Fraction(1, 2) * total_power.
    falsifies_if: adc_dac_power > Fraction(1, 2) * total_power.
    """
    limit = sys.total_power * eo_conversion_power_fraction()
    if sys.adc_dac_power > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {sys.system_id} E-O/O-E power {sys.adc_dac_power} > "
                f"half of total {limit} — photonic advantage nullified"
            ),
            premises=[
                f"ADC/DAC power: {sys.adc_dac_power}",
                f"Total power: {sys.total_power}",
                f"Limit (50%): {limit}",
            ],
            rule="landauer_inversion_eo_power",
        )
    return True, ProofObject(
        conclusion=(
            f"{sys.system_id} E-O/O-E power {sys.adc_dac_power} <= "
            f"half of total {limit}"
        ),
        premises=[
            f"ADC/DAC power: {sys.adc_dac_power}",
            f"Total power: {sys.total_power}",
        ],
        rule="landauer_inversion_eo_power",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> list:
    """Run all electro-optic checks with passing and failing test data.

    falsifies_if: any check fails or raises an exception.
    """
    pass_adc = AdcConverter(adc_id="pass_adc", effective_bits=Fraction(10, 1))
    fail_adc = AdcConverter(adc_id="fail_adc", effective_bits=Fraction(6, 1))
    pass_dac = DacConverter(dac_id="pass_dac", sfdr_dbc=Fraction(50, 1))
    fail_dac = DacConverter(dac_id="fail_dac", sfdr_dbc=Fraction(30, 1))
    pass_mod = OpticalModulator(
        modulator_id="pass_mod",
        bandwidth_ghz=Fraction(30, 1),
        vpi_volts=Fraction(15, 10),
    )
    fail_mod = OpticalModulator(
        modulator_id="fail_mod",
        bandwidth_ghz=Fraction(10, 1),
        vpi_volts=Fraction(3, 1),
    )
    pass_det = Photodetector(detector_id="pass_det", responsivity=Fraction(9, 10))
    fail_det = Photodetector(detector_id="fail_det", responsivity=Fraction(5, 10))
    pass_tia = TransimpedanceAmplifier(tia_id="pass_tia", tia_gain_ohms=Fraction(6000, 1))
    fail_tia = TransimpedanceAmplifier(tia_id="fail_tia", tia_gain_ohms=Fraction(3000, 1))
    pass_sys = ElectroOpticSystem(
        system_id="pass_sys",
        adc_dac_power=Fraction(3, 10),
        total_power=Fraction(1, 1),
    )
    fail_sys = ElectroOpticSystem(
        system_id="fail_sys",
        adc_dac_power=Fraction(6, 10),
        total_power=Fraction(1, 1),
    )

    checks = [
        ("check_adc_resolution_pass", lambda: check_adc_resolution(pass_adc)),
        ("check_adc_resolution_fail", lambda: check_adc_resolution(fail_adc)),
        ("check_dac_sfdr_pass", lambda: check_dac_sfdr(pass_dac)),
        ("check_dac_sfdr_fail", lambda: check_dac_sfdr(fail_dac)),
        ("check_modulator_bandwidth_pass", lambda: check_modulator_bandwidth(pass_mod)),
        ("check_modulator_bandwidth_fail", lambda: check_modulator_bandwidth(fail_mod)),
        ("check_modulator_vpi_pass", lambda: check_modulator_vpi(pass_mod)),
        ("check_modulator_vpi_fail", lambda: check_modulator_vpi(fail_mod)),
        ("check_photodetector_responsivity_pass", lambda: check_photodetector_responsivity(pass_det)),
        ("check_photodetector_responsivity_fail", lambda: check_photodetector_responsivity(fail_det)),
        ("check_transimpedance_gain_pass", lambda: check_transimpedance_gain(pass_tia)),
        ("check_transimpedance_gain_fail", lambda: check_transimpedance_gain(fail_tia)),
        ("check_eo_conversion_power_pass", lambda: check_eo_conversion_power(pass_sys)),
        ("check_eo_conversion_power_fail", lambda: check_eo_conversion_power(fail_sys)),
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
