"""PHOTONIC Reliability — MTBF, FIT rate, aging, temperature cycling,
humidity resistance, vibration tolerance.

Category 8: Reliability & Qualification (checks 49-54).

Standards: MIL-HDBK-217F, Telcordia SR-332, IEC 62380, Telcordia GR-468,
JEDEC JESD22-A104, JEDEC JESD22-A101, MIL-STD-883 Method 2007.
All invariants use Fraction arithmetic for exact thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class ReliabilityProfile:
    """Component reliability parameters per MIL-HDBK-217F / Telcordia SR-332.

    falsifies_if: mtbf_hours or fit is negative.
    falsifies_if: mtbf_hours or fit is negative.
    """
    component_id: str
    mtbf_hours: Fraction
    fit: Fraction


@dataclass(frozen=True)
class AgingProfile:
    """Optical aging parameters per Telcordia GR-468.

    falsifies_if: bol_loss_db or eol_loss_db is negative.
    falsifies_if: bol_loss_db or eol_loss_db is negative.
    """
    component_id: str
    bol_loss_db: Fraction
    eol_loss_db: Fraction


@dataclass(frozen=True)
class EnvironmentalStress:
    """Temperature cycling parameters per JEDEC JESD22-A104.

    falsifies_if: cycles_survived is negative.
    falsifies_if: cycles_survived is negative.
    """
    component_id: str
    cycles_survived: Fraction


@dataclass(frozen=True)
class HumidityTest:
    """Humidity resistance parameters per JEDEC JESD22-A101.

    falsifies_if: fails_85_85_test is True (component failed 85°C/85%RH 1000h).
    falsifies_if: fails_85_85_test is True.
    """
    component_id: str
    fails_85_85_test: bool


@dataclass(frozen=True)
class VibrationTest:
    """Vibration tolerance parameters per MIL-STD-883 Method 2007.

    falsifies_if: center_freq_hz is zero or negative.
    falsifies_if: center_freq_hz is zero or negative.
    """
    component_id: str
    resonance_shift_hz: Fraction
    center_freq_hz: Fraction


# ---------------------------------------------------------------------------
# Threshold functions
# ---------------------------------------------------------------------------

def mtbf_threshold() -> Fraction:
    """MIL-HDBK-217F / Telcordia SR-332 minimum MTBF: 100 000 hours."""
    return Fraction(100_000, 1)


def fit_threshold() -> Fraction:
    """IEC 62380 maximum FIT rate: 100 failures per 10^9 hours."""
    return Fraction(100, 1)


def aging_margin_threshold() -> Fraction:
    """Telcordia GR-468 maximum allowable aging degradation: 1 dB."""
    return Fraction(1, 1)


def temperature_cycling_threshold() -> Fraction:
    """JEDEC JESD22-A104 minimum survived cycles: 1000."""
    return Fraction(1000, 1)


def vibration_shift_fraction() -> Fraction:
    """MIL-STD-883 Method 2007 maximum resonance shift: 5% of center frequency."""
    return Fraction(5, 100)


# ---------------------------------------------------------------------------
# Check functions
# ---------------------------------------------------------------------------

def check_mtbf(profile: ReliabilityProfile) -> Tuple[bool, ProofObject]:
    """MTBF must be at least 100 000 hours per MIL-HDBK-217F / Telcordia SR-332.

    Falsifies if: mtbf_hours < Fraction(100_000, 1).
    falsifies_if: mtbf_hours < Fraction(100_000, 1).
    """
    limit = mtbf_threshold()
    if profile.mtbf_hours < limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {profile.component_id} MTBF {profile.mtbf_hours} h < "
                f"minimum {limit} h"
            ),
            premises=[
                f"MTBF: {profile.mtbf_hours} h",
                f"Minimum: {limit} h",
            ],
            rule="mil_hdbk_217f_mtbf",
        )
    return True, ProofObject(
        conclusion=f"{profile.component_id} MTBF {profile.mtbf_hours} h >= {limit} h",
        premises=[f"MTBF: {profile.mtbf_hours} h >= {limit} h"],
        rule="mil_hdbk_217f_mtbf",
    )


def check_fit_rate(profile: ReliabilityProfile) -> Tuple[bool, ProofObject]:
    """FIT rate must not exceed 100 per 10^9 hours per IEC 62380.

    Falsifies if: fit > Fraction(100, 1).
    falsifies_if: fit > Fraction(100, 1).
    """
    limit = fit_threshold()
    if profile.fit > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {profile.component_id} FIT {profile.fit} > "
                f"limit {limit}"
            ),
            premises=[
                f"FIT: {profile.fit}",
                f"Limit: {limit}",
            ],
            rule="iec_62380_fit_rate",
        )
    return True, ProofObject(
        conclusion=f"{profile.component_id} FIT {profile.fit} <= {limit}",
        premises=[f"FIT: {profile.fit} <= {limit}"],
        rule="iec_62380_fit_rate",
    )


def check_aging_margin(profile: AgingProfile) -> Tuple[bool, ProofObject]:
    """End-of-life loss minus beginning-of-life loss must not exceed 1 dB per Telcordia GR-468.

    Falsifies if: eol_loss_db - bol_loss_db > Fraction(1, 1).
    falsifies_if: eol_loss_db - bol_loss_db > Fraction(1, 1).
    """
    limit = aging_margin_threshold()
    degradation = profile.eol_loss_db - profile.bol_loss_db
    if degradation > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {profile.component_id} aging degradation {degradation} dB > "
                f"limit {limit} dB"
            ),
            premises=[
                f"BOL loss: {profile.bol_loss_db} dB",
                f"EOL loss: {profile.eol_loss_db} dB",
                f"Degradation: {degradation} dB",
                f"Limit: {limit} dB",
            ],
            rule="telcordia_gr468_aging",
        )
    return True, ProofObject(
        conclusion=f"{profile.component_id} aging degradation {degradation} dB <= {limit} dB",
        premises=[f"Degradation: {degradation} dB <= {limit} dB"],
        rule="telcordia_gr468_aging",
    )


def check_temperature_cycling(stress: EnvironmentalStress) -> Tuple[bool, ProofObject]:
    """Component must survive at least 1000 temperature cycles per JEDEC JESD22-A104.

    Falsifies if: cycles_survived < Fraction(1000, 1).
    falsifies_if: cycles_survived < Fraction(1000, 1).
    """
    limit = temperature_cycling_threshold()
    if stress.cycles_survived < limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {stress.component_id} survived {stress.cycles_survived} cycles < "
                f"minimum {limit} cycles"
            ),
            premises=[
                f"Survived: {stress.cycles_survived} cycles",
                f"Minimum: {limit} cycles",
            ],
            rule="jedec_jesd22_a104_temp_cycling",
        )
    return True, ProofObject(
        conclusion=(
            f"{stress.component_id} survived {stress.cycles_survived} cycles >= {limit} cycles"
        ),
        premises=[f"Survived: {stress.cycles_survived} cycles >= {limit} cycles"],
        rule="jedec_jesd22_a104_temp_cycling",
    )


def check_humidity_resistance(test: HumidityTest) -> Tuple[bool, ProofObject]:
    """Component must pass 85°C/85%RH 1000h test per JEDEC JESD22-A101.

    Falsifies if: fails_85_85_test is True.
    falsifies_if: fails_85_85_test is True.
    """
    if test.fails_85_85_test:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {test.component_id} failed 85°C/85%RH 1000h humidity test"
            ),
            premises=[
                f"Component: {test.component_id}",
                f"Test: 85°C/85%RH 1000h",
                f"Result: FAILED",
            ],
            rule="jedec_jesd22_a101_humidity",
        )
    return True, ProofObject(
        conclusion=f"{test.component_id} passed 85°C/85%RH 1000h humidity test",
        premises=[f"Component: {test.component_id}", f"Result: PASSED"],
        rule="jedec_jesd22_a101_humidity",
    )


def check_vibration_tolerance(test: VibrationTest) -> Tuple[bool, ProofObject]:
    """Resonance shift must not exceed 5% of center frequency per MIL-STD-883 Method 2007.

    Falsifies if: resonance_shift_hz / center_freq_hz > Fraction(5, 100).
    falsifies_if: resonance_shift_hz / center_freq_hz > Fraction(5, 100).
    """
    limit = vibration_shift_fraction()
    shift_fraction = test.resonance_shift_hz / test.center_freq_hz
    if shift_fraction > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {test.component_id} resonance shift {shift_fraction} "
                f"> limit {limit} of center freq"
            ),
            premises=[
                f"Resonance shift: {test.resonance_shift_hz} Hz",
                f"Center freq: {test.center_freq_hz} Hz",
                f"Shift fraction: {shift_fraction}",
                f"Limit: {limit}",
            ],
            rule="mil_std_883_vibration",
        )
    return True, ProofObject(
        conclusion=(
            f"{test.component_id} resonance shift {shift_fraction} <= {limit}"
        ),
        premises=[
            f"Shift fraction: {shift_fraction} <= {limit}",
        ],
        rule="mil_std_883_vibration",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> list:
    """Run all reliability checks with passing and failing test data.

    falsifies_if: any check fails or raises an exception.
    """
    pass_rel = ReliabilityProfile(
        component_id="pass_rel",
        mtbf_hours=Fraction(200_000, 1),
        fit=Fraction(50, 1),
    )
    fail_rel = ReliabilityProfile(
        component_id="fail_rel",
        mtbf_hours=Fraction(50_000, 1),
        fit=Fraction(150, 1),
    )
    pass_aging = AgingProfile(
        component_id="pass_aging",
        bol_loss_db=Fraction(1, 10),
        eol_loss_db=Fraction(3, 10),
    )
    fail_aging = AgingProfile(
        component_id="fail_aging",
        bol_loss_db=Fraction(1, 10),
        eol_loss_db=Fraction(15, 10),
    )
    pass_stress = EnvironmentalStress(
        component_id="pass_stress",
        cycles_survived=Fraction(1500, 1),
    )
    fail_stress = EnvironmentalStress(
        component_id="fail_stress",
        cycles_survived=Fraction(500, 1),
    )
    pass_hum = HumidityTest(
        component_id="pass_hum",
        fails_85_85_test=False,
    )
    fail_hum = HumidityTest(
        component_id="fail_hum",
        fails_85_85_test=True,
    )
    pass_vib = VibrationTest(
        component_id="pass_vib",
        resonance_shift_hz=Fraction(1, 100),
        center_freq_hz=Fraction(1, 1),
    )
    fail_vib = VibrationTest(
        component_id="fail_vib",
        resonance_shift_hz=Fraction(8, 100),
        center_freq_hz=Fraction(1, 1),
    )

    checks = [
        ("check_mtbf_pass", lambda: check_mtbf(pass_rel)),
        ("check_mtbf_fail", lambda: check_mtbf(fail_rel)),
        ("check_fit_rate_pass", lambda: check_fit_rate(pass_rel)),
        ("check_fit_rate_fail", lambda: check_fit_rate(fail_rel)),
        ("check_aging_margin_pass", lambda: check_aging_margin(pass_aging)),
        ("check_aging_margin_fail", lambda: check_aging_margin(fail_aging)),
        ("check_temperature_cycling_pass", lambda: check_temperature_cycling(pass_stress)),
        ("check_temperature_cycling_fail", lambda: check_temperature_cycling(fail_stress)),
        ("check_humidity_resistance_pass", lambda: check_humidity_resistance(pass_hum)),
        ("check_humidity_resistance_fail", lambda: check_humidity_resistance(fail_hum)),
        ("check_vibration_tolerance_pass", lambda: check_vibration_tolerance(pass_vib)),
        ("check_vibration_tolerance_fail", lambda: check_vibration_tolerance(fail_vib)),
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
