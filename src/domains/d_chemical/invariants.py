#!/usr/bin/env python3
"""D_CHEMICAL Invariants — Thermal runaway, SIS, HAZOP, LOPA, ESD timing

Chemical process safety per IEC 61511 and OSHA PSM requirements.
All invariants use Fraction arithmetic for exact safety thresholds.
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    ReactorControl, SafetyInstrumentedSystem, HazmatContainment, EmergencyShutdown,
    SILLevel, thermal_runaway_margin, pressure_interlock_threshold,
    sil3_pfd_max, leak_detection_threshold, lel_alarm_threshold, esd_isolation_max_ms
)


def check_thermal_runaway_protection(reactor: ReactorControl) -> Tuple[bool, ProofObject]:
    """
    Thermal runaway interlock must activate before T_critical - 10°C margin.

    Falsifies if: temperature_c >= t_critical_c - 10°C
    falsifies_if: temperature_c >= t_critical_c - 10°C
    """
    margin = thermal_runaway_margin()
    threshold = reactor.t_critical_c - margin

    if reactor.temperature_c >= threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: Reactor {reactor.reactor_id} temperature {reactor.temperature_c}°C exceeds safety threshold {threshold}°C",
            premises=[
                f"Temp: {reactor.temperature_c}°C",
                f"T_critical: {reactor.t_critical_c}°C",
                f"Margin: {margin}°C"
            ],
            rule="thermal_runaway_interlock"
        )

    return True, ProofObject(
        conclusion=f"Reactor {reactor.reactor_id} thermal protection adequate",
        premises=[f"Temp: {reactor.temperature_c}°C < {threshold}°C"],
        rule="thermal_runaway_interlock"
    )


def check_pressure_interlock(reactor: ReactorControl) -> Tuple[bool, ProofObject]:
    """
    Pressure interlock activates at 90% of design pressure per ASME.

    Falsifies if: pressure_bar >= 0.9 * design_pressure_bar
    falsifies_if: pressure_bar >= 0.9 * design_pressure_bar
    """
    threshold_fraction = pressure_interlock_threshold()
    threshold = reactor.design_pressure_bar * threshold_fraction

    if reactor.pressure_bar >= threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: Reactor {reactor.reactor_id} pressure {reactor.pressure_bar} bar >= {threshold} bar (90% design)",
            premises=[
                f"Pressure: {reactor.pressure_bar} bar",
                f"Design: {reactor.design_pressure_bar} bar",
                f"Threshold: 90%"
            ],
            rule="asme_pressure_interlock"
        )

    return True, ProofObject(
        conclusion=f"Reactor {reactor.reactor_id} pressure within limits",
        premises=[f"Pressure: {reactor.pressure_bar} bar < {threshold} bar"],
        rule="asme_pressure_interlock"
    )


def check_sis_reliability(sis: SafetyInstrumentedSystem) -> Tuple[bool, ProofObject]:
    """
    SIL-3 systems require PFD_avg < 0.001 per IEC 61511.

    Falsifies if: sil_level == SIL3 AND pfd_avg >= 0.001
    falsifies_if: sil_level == SIL3 AND pfd_avg >= 0.001
    """
    if sis.sil_level == SILLevel.SIL3:
        max_pfd = sil3_pfd_max()

        if sis.pfd_avg >= max_pfd:
            return False, ProofObject(
                conclusion=f"VIOLATION: SIS {sis.sis_id} PFD {sis.pfd_avg} >= {max_pfd} (SIL-3 limit)",
                premises=[
                    f"PFD: {sis.pfd_avg}",
                    f"SIL level: {sis.sil_level.name}",
                    f"Max PFD: {max_pfd}"
                ],
                rule="iec_61511_sil3_pfd"
            )

    return True, ProofObject(
        conclusion=f"SIS {sis.sis_id} reliability adequate",
        premises=[f"SIL: {sis.sil_level.name}", f"PFD: {sis.pfd_avg}"],
        rule="iec_61511_sil_reliability"
    )


def check_leak_detection(hazmat: HazmatContainment) -> Tuple[bool, ProofObject]:
    """
    Leak detection at 10% LEL for flammable materials.

    Falsifies if: leak_detection_ppm >= lel_percent * 0.1
    falsifies_if: leak_detection_ppm >= lel_percent * 0.1
    """
    alarm_threshold = hazmat.lel_percent * lel_alarm_threshold()

    if hazmat.leak_detection_ppm >= alarm_threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: Zone {hazmat.zone_id} leak {hazmat.leak_detection_ppm} ppm >= {alarm_threshold} ppm (10% LEL)",
            premises=[
                f"Detected: {hazmat.leak_detection_ppm} ppm",
                f"LEL: {hazmat.lel_percent}%",
                f"Alarm: 10% LEL"
            ],
            rule="hazmat_leak_detection"
        )

    return True, ProofObject(
        conclusion=f"Zone {hazmat.zone_id} leak detection within limits",
        premises=[f"Leak: {hazmat.leak_detection_ppm} ppm"],
        rule="hazmat_leak_detection"
    )


def check_esd_timing(esd: EmergencyShutdown) -> Tuple[bool, ProofObject]:
    """
    ESD must isolate critical systems within 5000ms.

    Falsifies if: trigger_to_isolation_ms > 5000ms
    falsifies_if: trigger_to_isolation_ms > 5000ms
    """
    max_time = esd_isolation_max_ms()

    if esd.trigger_to_isolation_ms > max_time:
        return False, ProofObject(
            conclusion=f"VIOLATION: ESD {esd.esd_id} isolation time {esd.trigger_to_isolation_ms}ms > {max_time}ms",
            premises=[
                f"Time: {esd.trigger_to_isolation_ms}ms",
                f"Max: {max_time}ms"
            ],
            rule="esd_response_time"
        )

    return True, ProofObject(
        conclusion=f"ESD {esd.esd_id} response time adequate",
        premises=[f"Time: {esd.trigger_to_isolation_ms}ms <= {max_time}ms"],
        rule="esd_response_time"
    )
