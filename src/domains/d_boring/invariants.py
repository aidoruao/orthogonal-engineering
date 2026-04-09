#!/usr/bin/env python3
"""D_BORING Invariants — Tunnel boring, geotechnical, TBM operations

Verifies TBM advance rates, ground pressure limits, segment alignment, grouting, subsidence.
BTS (British Tunnelling Society), ITA (International Tunnelling Association).
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    TBM, GroundConditions, TunnelSegment, TBMAdvance, SegmentInstallation,
    SubsidenceMonitoring, GroundType, TBMType,
    tbm_standard_advance_rate, alignment_tolerance_threshold,
    grouting_volume_per_ring, subsidence_limit_mm
)


def check_tbm_advance_rate(tbm: TBM, ground: GroundConditions) -> Tuple[bool, ProofObject]:
    """
    TBM advance rate must be within expected range for ground type.

    BTS guidelines: Advance rates vary by ground type (10-50 mm/min typical).
    Falsifies if: advance_rate exceeds 2x standard rate for ground type
    """
    standard_rate = tbm_standard_advance_rate(ground.ground_type)
    max_rate = standard_rate * 2

    if tbm.advance_rate_mm_per_min > max_rate:
        return False, ProofObject(
            conclusion=f"VIOLATION: TBM {tbm.tbm_id} advance rate {tbm.advance_rate_mm_per_min} mm/min exceeds max {max_rate} for {ground.ground_type.name}",
            premises=[
                f"Advance rate: {tbm.advance_rate_mm_per_min} mm/min",
                f"Ground type: {ground.ground_type.name}",
                f"Standard rate: {standard_rate} mm/min",
                f"Max rate: {max_rate} mm/min"
            ],
            rule="tbm_advance_rate"
        )

    return True, ProofObject(
        conclusion=f"TBM {tbm.tbm_id} advance rate {tbm.advance_rate_mm_per_min} mm/min within spec for {ground.ground_type.name}",
        premises=[f"Rate: {tbm.advance_rate_mm_per_min} mm/min <= {max_rate} mm/min"],
        rule="tbm_advance_rate"
    )


def check_ground_pressure_limits(advance: TBMAdvance, ground: GroundConditions) -> Tuple[bool, ProofObject]:
    """
    TBM face pressure must balance ground/water pressure to prevent collapse or blow-out.

    ITA guidelines: Face pressure = ground pressure + water pressure (typically 100-500 kPa).
    Falsifies if: face_pressure < ground_pressure or face_pressure > 2x ground_pressure
    """
    min_face_pressure = advance.ground_pressure_kpa
    max_face_pressure = advance.ground_pressure_kpa * 2

    if advance.face_pressure_kpa < min_face_pressure:
        return False, ProofObject(
            conclusion=f"VIOLATION: TBM {advance.tbm_id} face pressure {advance.face_pressure_kpa} kPa too low (risk of collapse)",
            premises=[
                f"Face pressure: {advance.face_pressure_kpa} kPa",
                f"Ground pressure: {advance.ground_pressure_kpa} kPa",
                f"Required: >= {min_face_pressure} kPa"
            ],
            rule="ground_pressure_balance"
        )

    if advance.face_pressure_kpa > max_face_pressure:
        return False, ProofObject(
            conclusion=f"VIOLATION: TBM {advance.tbm_id} face pressure {advance.face_pressure_kpa} kPa too high (risk of blow-out)",
            premises=[
                f"Face pressure: {advance.face_pressure_kpa} kPa",
                f"Ground pressure: {advance.ground_pressure_kpa} kPa",
                f"Max: {max_face_pressure} kPa"
            ],
            rule="ground_pressure_balance"
        )

    return True, ProofObject(
        conclusion=f"TBM {advance.tbm_id} face pressure {advance.face_pressure_kpa} kPa balanced",
        premises=[f"{min_face_pressure} kPa <= {advance.face_pressure_kpa} kPa <= {max_face_pressure} kPa"],
        rule="ground_pressure_balance"
    )


def check_segment_alignment(installation: SegmentInstallation) -> Tuple[bool, ProofObject]:
    """
    Tunnel segment alignment deviation must be within tolerance.

    BTS: Typical tolerance +/- 10mm for precast segments.
    Falsifies if: alignment_deviation_mm > tolerance
    """
    tolerance = alignment_tolerance_threshold()

    if installation.alignment_deviation_mm > tolerance:
        return False, ProofObject(
            conclusion=f"VIOLATION: Segment {installation.segment_id} alignment deviation {installation.alignment_deviation_mm} mm exceeds {tolerance} mm",
            premises=[
                f"Deviation: {installation.alignment_deviation_mm} mm",
                f"Tolerance: {tolerance} mm",
                f"Ring: {installation.ring_number}"
            ],
            rule="segment_alignment"
        )

    return True, ProofObject(
        conclusion=f"Segment {installation.segment_id} alignment within tolerance",
        premises=[f"Deviation: {installation.alignment_deviation_mm} mm <= {tolerance} mm"],
        rule="segment_alignment"
    )


def check_grouting_coverage(installation: SegmentInstallation) -> Tuple[bool, ProofObject]:
    """
    Grouting volume must meet minimum requirements to fill annular void.

    ITA: Typical grouting volume 3-5 m3 per ring.
    Falsifies if: grouting_volume_m3 < minimum required volume
    """
    min_volume = grouting_volume_per_ring()

    if installation.grouting_volume_m3 < min_volume:
        return False, ProofObject(
            conclusion=f"VIOLATION: Installation {installation.installation_id} grouting volume {installation.grouting_volume_m3} m3 below minimum {min_volume} m3",
            premises=[
                f"Grouting volume: {installation.grouting_volume_m3} m3",
                f"Minimum: {min_volume} m3",
                f"Ring: {installation.ring_number}"
            ],
            rule="grouting_coverage"
        )

    return True, ProofObject(
        conclusion=f"Installation {installation.installation_id} grouting volume adequate",
        premises=[f"Volume: {installation.grouting_volume_m3} m3 >= {min_volume} m3"],
        rule="grouting_coverage"
    )


def check_subsidence_tolerance(monitoring: SubsidenceMonitoring) -> Tuple[bool, ProofObject]:
    """
    Surface settlement must be within acceptable limits.

    BTS guidelines: Typical limit < 30mm for urban tunneling.
    Falsifies if: settlement_mm > limit
    """
    limit = subsidence_limit_mm()

    if monitoring.settlement_mm > limit:
        return False, ProofObject(
            conclusion=f"VIOLATION: Location {monitoring.location} settlement {monitoring.settlement_mm} mm exceeds limit {limit} mm",
            premises=[
                f"Settlement: {monitoring.settlement_mm} mm",
                f"Limit: {limit} mm",
                f"Days after passage: {monitoring.days_after_passage}",
                f"Horizontal displacement: {monitoring.horizontal_displacement_mm} mm"
            ],
            rule="subsidence_tolerance"
        )

    return True, ProofObject(
        conclusion=f"Location {monitoring.location} settlement within tolerance",
        premises=[f"Settlement: {monitoring.settlement_mm} mm <= {limit} mm"],
        rule="subsidence_tolerance"
    )


def check_tbm_operational_status(tbm: TBM) -> Tuple[bool, ProofObject]:
    """
    Operational TBMs must have valid thrust force and cutterhead RPM.

    Falsifies if: operational but thrust_force_kn <= 0 or cutterhead_rpm <= 0
    """
    if tbm.operational:
        if tbm.thrust_force_kn <= 0:
            return False, ProofObject(
                conclusion=f"VIOLATION: TBM {tbm.tbm_id} operational but thrust force {tbm.thrust_force_kn} kN invalid",
                premises=[
                    f"Operational: {tbm.operational}",
                    f"Thrust force: {tbm.thrust_force_kn} kN"
                ],
                rule="tbm_operational"
            )

        if tbm.cutterhead_rpm <= 0:
            return False, ProofObject(
                conclusion=f"VIOLATION: TBM {tbm.tbm_id} operational but cutterhead RPM {tbm.cutterhead_rpm} invalid",
                premises=[
                    f"Operational: {tbm.operational}",
                    f"Cutterhead RPM: {tbm.cutterhead_rpm}"
                ],
                rule="tbm_operational"
            )

    return True, ProofObject(
        conclusion=f"TBM {tbm.tbm_id} operational status valid",
        premises=[f"Operational: {tbm.operational}", f"Thrust: {tbm.thrust_force_kn} kN", f"RPM: {tbm.cutterhead_rpm}"],
        rule="tbm_operational"
    )


def check_water_bearing_ground(ground: GroundConditions, advance: TBMAdvance) -> Tuple[bool, ProofObject]:
    """
    Water-bearing ground requires EPB or slurry TBM for face pressure control.

    ITA: Open-face TBMs cannot handle water-bearing ground.
    Falsifies if: ground is WATER_BEARING but pressure control inadequate
    """
    if ground.ground_type == GroundType.WATER_BEARING:
        # For water-bearing ground, face pressure must be significantly higher
        water_pressure_estimate = ground.water_table_depth_m * Fraction(10, 1)  # ~10 kPa per meter
        min_face_pressure = advance.ground_pressure_kpa + water_pressure_estimate

        if advance.face_pressure_kpa < min_face_pressure:
            return False, ProofObject(
                conclusion=f"VIOLATION: Water-bearing ground requires face pressure >= {min_face_pressure} kPa (ground + water)",
                premises=[
                    f"Ground type: WATER_BEARING",
                    f"Water table: {ground.water_table_depth_m} m",
                    f"Face pressure: {advance.face_pressure_kpa} kPa",
                    f"Required: >= {min_face_pressure} kPa"
                ],
                rule="water_bearing_ground"
            )

    return True, ProofObject(
        conclusion=f"Water-bearing ground pressure control adequate",
        premises=[f"Ground type: {ground.ground_type.name}", f"Face pressure: {advance.face_pressure_kpa} kPa"],
        rule="water_bearing_ground"
    )


def check_segment_installation_sequence(installation: SegmentInstallation, segment: TunnelSegment) -> Tuple[bool, ProofObject]:
    """
    Segments must be installed before grouting.

    Falsifies if: grouting_complete but not installed
    """
    if segment.grouting_complete and not segment.installed:
        return False, ProofObject(
            conclusion=f"VIOLATION: Segment {segment.segment_id} grouted before installation",
            premises=[
                f"Installed: {segment.installed}",
                f"Grouting complete: {segment.grouting_complete}"
            ],
            rule="segment_sequence"
        )

    return True, ProofObject(
        conclusion=f"Segment {segment.segment_id} installation sequence valid",
        premises=[f"Installed: {segment.installed}", f"Grouted: {segment.grouting_complete}"],
        rule="segment_sequence"
    )
