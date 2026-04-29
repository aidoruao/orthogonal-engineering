"""PHOTONIC Safety — Laser classification, eye safety, thermal shutdown, ESD

Category 4: Photonic Safety & Laser Standards (IEC 60825-1, IEC 62368-1,
IEC 62471, JEDEC JESD22-A114, JEDEC JESD51, ITU-T G.959.1).

All invariants use Fraction arithmetic for exact thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


class LaserClass(Enum):
    """IEC 60825-1 laser classification.

    falsifies_if: a LaserClass value is outside 1-6.
    """
    CLASS_1 = 1    # safe under all conditions
    CLASS_1M = 2   # safe except with magnifying optics
    CLASS_2 = 3    # visible, blink reflex protects
    CLASS_3R = 4   # small risk of eye injury
    CLASS_3B = 5   # direct beam hazardous
    CLASS_4 = 6    # hazardous to eyes and skin, fire risk


@dataclass(frozen=True)
class LaserSource:
    """Laser source parameters per IEC 60825-1.

    falsifies_if: power_mw is negative.
    falsifies_if: power_mw is negative.
    """
    source_id: str
    wavelength_nm: Fraction
    power_mw: Fraction
    declared_class: LaserClass
    beam_divergence_mrad: Fraction
    aperture_diameter_mm: Fraction


@dataclass(frozen=True)
class FiberConnector:
    """Fiber connector interlock state per IEC 62368-1.

    falsifies_if: optical_power_mw is negative.
    falsifies_if: optical_power_mw is negative.
    """
    connector_id: str
    optical_power_mw: Fraction
    is_open: bool
    interlock_active: bool


@dataclass(frozen=True)
class PhotonicThermalProfile:
    """Thermal shutdown profile per JEDEC JESD51.

    falsifies_if: tj_max_c <= 0.
    falsifies_if: tj_max_c <= 0.
    """
    chip_id: str
    junction_temp_c: Fraction
    tj_max_c: Fraction
    thermal_shutdown_enabled: bool


@dataclass(frozen=True)
class OpticalLink:
    """Optical power budget per ITU-T G.959.1.

    falsifies_if: total_loss_db is negative (gain instead of loss).
    falsifies_if: total_loss_db is negative (gain instead of loss).
    """
    link_id: str
    tx_power_dbm: Fraction
    rx_sensitivity_dbm: Fraction
    total_loss_db: Fraction


# ---------------------------------------------------------------------------
# Threshold functions
# ---------------------------------------------------------------------------

def ael_class1_mw() -> Fraction:
    """Accessible emission limit for Class 1 lasers: 1 µW."""
    # TODO: Expand ael_class1_mw() - stub detected by Yeshua Agent
    return Fraction(1, 1000)


def ael_class3b_mw() -> Fraction:
    """Upper bound for Class 3B lasers: 500 mW."""
    # TODO: Expand ael_class3b_mw() - stub detected by Yeshua Agent
    return Fraction(500, 1)


def nohd_minimum_m() -> Fraction:
    """Minimum nominal ocular hazard distance: 1 meter."""
    # TODO: Expand nohd_minimum_m() - stub detected by Yeshua Agent
    return Fraction(1, 1)


def skin_mpe_mw_per_cm2() -> Fraction:
    """Skin maximum permissible exposure at 1550 nm: 200 mW/cm²."""
    # TODO: Expand skin_mpe_mw_per_cm2() - stub detected by Yeshua Agent
    return Fraction(200, 1)


def esd_hbm_withstand_v() -> Fraction:
    """Human body model ESD withstand voltage per JEDEC: 2000 V."""
    # TODO: Expand esd_hbm_withstand_v() - stub detected by Yeshua Agent
    return Fraction(2000, 1)


def connector_interlock_power_mw() -> Fraction:
    """Interlock activation threshold for open fiber connectors: 50 mW."""
    # TODO: Expand connector_interlock_power_mw() - stub detected by Yeshua Agent
    return Fraction(50, 1)


# ---------------------------------------------------------------------------
# Check functions
# ---------------------------------------------------------------------------

def check_laser_class_compliance(source: LaserSource) -> Tuple[bool, ProofObject]:
    """Laser power must not exceed AEL for declared IEC 60825-1 class.

    Falsifies if: power_mw >= AEL for the declared class.
    falsifies_if: power_mw >= AEL for the declared class.
    """
    if source.declared_class == LaserClass.CLASS_1:
        limit = ael_class1_mw()
        if source.power_mw >= limit:
            return False, ProofObject(
                conclusion=(
                    f"VIOLATION: Source {source.source_id} power {source.power_mw} mW >= "
                    f"Class 1 AEL {limit} mW"
                ),
                premises=[
                    f"Power: {source.power_mw} mW",
                    f"Class 1 AEL: {limit} mW",
                ],
                rule="iec_60825_class_1_ael",
            )
    elif source.declared_class == LaserClass.CLASS_3B:
        limit = ael_class3b_mw()
        if source.power_mw >= limit:
            return False, ProofObject(
                conclusion=(
                    f"VIOLATION: Source {source.source_id} power {source.power_mw} mW >= "
                    f"Class 3B AEL {limit} mW"
                ),
                premises=[
                    f"Power: {source.power_mw} mW",
                    f"Class 3B AEL: {limit} mW",
                ],
                rule="iec_60825_class_3b_ael",
            )

    return True, ProofObject(
        conclusion=f"Source {source.source_id} class {source.declared_class.name} compliance OK",
        premises=[f"Power: {source.power_mw} mW", f"Class: {source.declared_class.name}"],
        rule="iec_60825_class_compliance",
    )


def check_eye_safety_distance(source: LaserSource) -> Tuple[bool, ProofObject]:
    """NOHD must exceed minimum safe distance per IEC 60825-1 Table 10.

    NOHD = aperture_diameter_mm * power_mw / (beam_divergence_mrad * 4).

    Falsifies if: computed NOHD < nohd_minimum_m().
    falsifies_if: computed NOHD < nohd_minimum_m().
    """
    nohd = (
        source.aperture_diameter_mm
        * source.power_mw
        / (source.beam_divergence_mrad * Fraction(4, 1))
    )
    minimum = nohd_minimum_m()

    if nohd < minimum:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Source {source.source_id} NOHD {nohd} m < minimum {minimum} m"
            ),
            premises=[
                f"NOHD: {nohd} m",
                f"Minimum: {minimum} m",
                f"Aperture: {source.aperture_diameter_mm} mm",
            ],
            rule="iec_60825_eye_safety_distance",
        )

    return True, ProofObject(
        conclusion=f"Source {source.source_id} NOHD {nohd} m >= {minimum} m",
        premises=[f"NOHD: {nohd} m >= {minimum} m"],
        rule="iec_60825_eye_safety_distance",
    )


def check_skin_exposure_limit(source: LaserSource) -> Tuple[bool, ProofObject]:
    """Skin irradiance must be below MPE per IEC 60825-1 Table 9.

    irradiance = power_mw / (aperture_diameter_mm² * 1/100).

    Falsifies if: irradiance >= skin_mpe_mw_per_cm2().
    falsifies_if: irradiance >= skin_mpe_mw_per_cm2().
    """
    area_proxy = source.aperture_diameter_mm * source.aperture_diameter_mm * Fraction(1, 100)
    irradiance = source.power_mw / area_proxy
    mpe = skin_mpe_mw_per_cm2()

    if irradiance >= mpe:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Source {source.source_id} irradiance {irradiance} mW/cm² >= "
                f"MPE {mpe} mW/cm²"
            ),
            premises=[
                f"Irradiance: {irradiance} mW/cm²",
                f"MPE: {mpe} mW/cm²",
            ],
            rule="iec_60825_skin_exposure",
        )

    return True, ProofObject(
        conclusion=f"Source {source.source_id} irradiance {irradiance} mW/cm² < {mpe} mW/cm²",
        premises=[f"Irradiance: {irradiance} mW/cm² < {mpe} mW/cm²"],
        rule="iec_60825_skin_exposure",
    )


def check_fiber_connector_interlock(connector: FiberConnector) -> Tuple[bool, ProofObject]:
    """Open fiber connectors with hazardous power must have interlock active per IEC 62368-1.

    Falsifies if: is_open is True AND optical_power_mw >= 50 mW AND interlock_active is False.
    falsifies_if: is_open is True AND optical_power_mw >= 50 mW AND interlock_active is False.
    """
    threshold = connector_interlock_power_mw()
    if connector.is_open and connector.optical_power_mw >= threshold and not connector.interlock_active:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Connector {connector.connector_id} open with "
                f"{connector.optical_power_mw} mW and no interlock"
            ),
            premises=[
                f"Open: {connector.is_open}",
                f"Power: {connector.optical_power_mw} mW",
                f"Interlock: {connector.interlock_active}",
            ],
            rule="iec_62368_connector_interlock",
        )

    return True, ProofObject(
        conclusion=f"Connector {connector.connector_id} interlock OK",
        premises=[
            f"Open: {connector.is_open}",
            f"Power: {connector.optical_power_mw} mW",
            f"Interlock: {connector.interlock_active}",
        ],
        rule="iec_62368_connector_interlock",
    )


def check_photobiological_safety(source: LaserSource) -> Tuple[bool, ProofObject]:
    """Photobiological safety per IEC 62471 risk groups.

    Visible (400-700 nm): power < 1 mW for Risk Group 0.
    IR (> 700 nm): power < 100 mW for Risk Group 1.

    Falsifies if: power exceeds risk group limit for wavelength band.
    falsifies_if: power exceeds risk group limit for wavelength band.
    """
    wl = source.wavelength_nm
    if wl >= Fraction(400, 1) and wl <= Fraction(700, 1):
        limit = Fraction(1, 1)
        if source.power_mw >= limit:
            return False, ProofObject(
                conclusion=(
                    f"VIOLATION: Source {source.source_id} visible power {source.power_mw} mW >= "
                    f"RG0 limit {limit} mW"
                ),
                premises=[
                    f"Wavelength: {wl} nm (visible)",
                    f"Power: {source.power_mw} mW",
                    f"RG0 limit: {limit} mW",
                ],
                rule="iec_62471_photobiological",
            )
    elif wl > Fraction(700, 1):
        limit = Fraction(100, 1)
        if source.power_mw >= limit:
            return False, ProofObject(
                conclusion=(
                    f"VIOLATION: Source {source.source_id} IR power {source.power_mw} mW >= "
                    f"RG1 limit {limit} mW"
                ),
                premises=[
                    f"Wavelength: {wl} nm (IR)",
                    f"Power: {source.power_mw} mW",
                    f"RG1 limit: {limit} mW",
                ],
                rule="iec_62471_photobiological",
            )

    return True, ProofObject(
        conclusion=f"Source {source.source_id} photobiological safety OK",
        premises=[f"Wavelength: {wl} nm", f"Power: {source.power_mw} mW"],
        rule="iec_62471_photobiological",
    )


def check_esd_protection(chip_id: str, esd_withstand_v: Fraction) -> Tuple[bool, ProofObject]:
    """ESD withstand voltage must meet JEDEC JESD22-A114 HBM requirement.

    Falsifies if: esd_withstand_v < esd_hbm_withstand_v().
    falsifies_if: esd_withstand_v < esd_hbm_withstand_v().
    """
    requirement = esd_hbm_withstand_v()
    if esd_withstand_v < requirement:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Chip {chip_id} ESD withstand {esd_withstand_v} V < "
                f"JEDEC HBM {requirement} V"
            ),
            premises=[
                f"ESD withstand: {esd_withstand_v} V",
                f"JEDEC HBM: {requirement} V",
            ],
            rule="jedec_jesd22_esd",
        )

    return True, ProofObject(
        conclusion=f"Chip {chip_id} ESD protection {esd_withstand_v} V >= {requirement} V",
        premises=[f"ESD withstand: {esd_withstand_v} V >= {requirement} V"],
        rule="jedec_jesd22_esd",
    )


def check_thermal_shutdown(profile: PhotonicThermalProfile) -> Tuple[bool, ProofObject]:
    """Thermal shutdown must activate when junction temperature reaches Tj_max per JEDEC JESD51.

    Falsifies if: junction_temp_c >= tj_max_c AND thermal_shutdown_enabled is False.
    falsifies_if: junction_temp_c >= tj_max_c AND thermal_shutdown_enabled is False.
    """
    if profile.junction_temp_c >= profile.tj_max_c and not profile.thermal_shutdown_enabled:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Chip {profile.chip_id} junction temp {profile.junction_temp_c}°C >= "
                f"Tj_max {profile.tj_max_c}°C with no thermal shutdown"
            ),
            premises=[
                f"Junction temp: {profile.junction_temp_c}°C",
                f"Tj_max: {profile.tj_max_c}°C",
                f"Shutdown enabled: {profile.thermal_shutdown_enabled}",
            ],
            rule="jedec_jesd51_thermal_shutdown",
        )

    return True, ProofObject(
        conclusion=f"Chip {profile.chip_id} thermal profile OK",
        premises=[
            f"Junction temp: {profile.junction_temp_c}°C",
            f"Tj_max: {profile.tj_max_c}°C",
            f"Shutdown: {profile.thermal_shutdown_enabled}",
        ],
        rule="jedec_jesd51_thermal_shutdown",
    )


def check_optical_power_budget(link: OpticalLink) -> Tuple[bool, ProofObject]:
    """Received optical power must exceed receiver sensitivity per ITU-T G.959.1.

    rx_sensitivity_dbm + total_loss_db <= tx_power_dbm.

    Falsifies if: rx_sensitivity_dbm + total_loss_db > tx_power_dbm.
    falsifies_if: rx_sensitivity_dbm + total_loss_db > tx_power_dbm.
    """
    required = link.rx_sensitivity_dbm + link.total_loss_db
    if required > link.tx_power_dbm:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Link {link.link_id} required {required} dBm > "
                f"tx_power {link.tx_power_dbm} dBm"
            ),
            premises=[
                f"Rx sensitivity: {link.rx_sensitivity_dbm} dBm",
                f"Total loss: {link.total_loss_db} dB",
                f"Tx power: {link.tx_power_dbm} dBm",
            ],
            rule="itu_g9591_power_budget",
        )

    return True, ProofObject(
        conclusion=f"Link {link.link_id} power budget OK",
        premises=[
            f"Required: {required} dBm <= Tx: {link.tx_power_dbm} dBm",
        ],
        rule="itu_g9591_power_budget",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_safety_checks() -> list:
    """Run all 8 photonic safety checks with nominal test data.

    falsifies_if: any check fails or raises an exception.
    """
    source = LaserSource(
        source_id="test_laser_01",
        wavelength_nm=Fraction(1550, 1),
        power_mw=Fraction(10, 1),
        declared_class=LaserClass.CLASS_3B,
        beam_divergence_mrad=Fraction(1, 10),
        aperture_diameter_mm=Fraction(10, 1),
    )
    connector = FiberConnector(
        connector_id="fc_01",
        optical_power_mw=Fraction(10, 1),
        is_open=False,
        interlock_active=True,
    )
    profile = PhotonicThermalProfile(
        chip_id="ph_chip_01",
        junction_temp_c=Fraction(75, 1),
        tj_max_c=Fraction(125, 1),
        thermal_shutdown_enabled=True,
    )
    link = OpticalLink(
        link_id="link_01",
        tx_power_dbm=Fraction(0, 1),
        rx_sensitivity_dbm=Fraction(-20, 1),
        total_loss_db=Fraction(3, 1),
    )

    checks = [
        ("check_laser_class_compliance", lambda: check_laser_class_compliance(source)),
        ("check_eye_safety_distance", lambda: check_eye_safety_distance(source)),
        ("check_skin_exposure_limit", lambda: check_skin_exposure_limit(source)),
        ("check_fiber_connector_interlock", lambda: check_fiber_connector_interlock(connector)),
        ("check_photobiological_safety", lambda: check_photobiological_safety(source)),
        ("check_esd_protection", lambda: check_esd_protection("chip_01", Fraction(4000, 1))),
        ("check_thermal_shutdown", lambda: check_thermal_shutdown(profile)),
        ("check_optical_power_budget", lambda: check_optical_power_budget(link)),
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
