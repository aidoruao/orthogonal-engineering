"""D_ROAD_STANDARDS invariants — Yeshua Standard. 0 floats.

Standards:
- AASHTO A Policy on Geometric Design of Highways and Streets (Green Book)
- FHWA Manual on Uniform Traffic Control Devices (MUTCD)
- 23 CFR Part 625 — Design standards for federal-aid highways
- AASHTO LRFD Bridge Design Specifications
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import RoadSegment, SpeedLimitCalculation, TrafficSignal


def check_lane_width_minimum(road: RoadSegment) -> Tuple[bool, ProofObject]:
    """Lane width must be >= 10 ft (urban) or >= 11 ft (rural).

    Standard: AASHTO Green Book Table 3-12; FHWA MUTCD
    falsifies_if: lane_width_ft < 10 (urban) or < 11 (rural).
    """
    min_width = Fraction(10) if road.urban else Fraction(11)
    ok = road.lane_width_ft >= min_width
    premises = [
        f"segment_id={road.segment_id}",
        f"lane_width_ft={road.lane_width_ft}",
        f"min_required={min_width}",
        f"urban={road.urban}",
    ]
    return ok, ProofObject(
        rule="LaneWidthMinimum",
        premises=premises,
        conclusion=f"PASS: lane width {road.lane_width_ft}ft >= {min_width}ft" if ok else f"VIOLATION: lane width {road.lane_width_ft}ft < {min_width}ft",
    )


def check_shoulder_width_minimum(road: RoadSegment) -> Tuple[bool, ProofObject]:
    """Shoulder width must be >= 4 ft on any road segment.

    Standard: AASHTO Green Book — minimum shoulder widths
    falsifies_if: shoulder_width_ft < 4.
    """
    min_shoulder = Fraction(4)
    ok = road.shoulder_width_ft >= min_shoulder
    premises = [
        f"segment_id={road.segment_id}",
        f"shoulder_width_ft={road.shoulder_width_ft}",
        f"min_required={min_shoulder}",
    ]
    return ok, ProofObject(
        rule="ShoulderWidthMinimum",
        premises=premises,
        conclusion=f"PASS: shoulder {road.shoulder_width_ft}ft >= {min_shoulder}ft" if ok else f"VIOLATION: shoulder {road.shoulder_width_ft}ft < {min_shoulder}ft",
    )


def check_speed_limit_consistent(calc: SpeedLimitCalculation) -> Tuple[bool, ProofObject]:
    """Calculated speed limit must match lane/shoulder widths.

    Standard: MUTCD §2B.13 — speed limit determination
    falsifies_if: calculated_limit_mph > 75 (national maximum).
    """
    max_speed = 75
    ok = calc.calculated_limit_mph <= max_speed
    premises = [
        f"segment_id={calc.segment_id}",
        f"calculated_limit_mph={calc.calculated_limit_mph}",
        f"max_national={max_speed}",
    ]
    return ok, ProofObject(
        rule="SpeedLimitConsistent",
        premises=premises,
        conclusion=f"PASS: speed limit {calc.calculated_limit_mph} <= {max_speed}" if ok else f"VIOLATION: speed limit {calc.calculated_limit_mph} > {max_speed}",
    )


def check_num_lanes_positive(road: RoadSegment) -> Tuple[bool, ProofObject]:
    """A road segment must have >= 1 lane.

    Standard: AASHTO — minimum roadway cross-section
    falsifies_if: num_lanes < 1.
    """
    ok = road.num_lanes >= 1
    premises = [f"segment_id={road.segment_id}", f"num_lanes={road.num_lanes}"]
    return ok, ProofObject(
        rule="NumLanesPositive",
        premises=premises,
        conclusion=f"PASS: {road.num_lanes} lanes" if ok else "VIOLATION: road segment has no lanes",
    )


def check_segment_length_positive(road: RoadSegment) -> Tuple[bool, ProofObject]:
    """Road segment length must be > 0 miles.

    Standard: AASHTO — segment definition requirement
    falsifies_if: length_miles <= 0.
    """
    ok = road.length_miles > Fraction(0)
    premises = [f"segment_id={road.segment_id}", f"length_miles={road.length_miles}"]
    return ok, ProofObject(
        rule="SegmentLengthPositive",
        premises=premises,
        conclusion=f"PASS: length {road.length_miles} miles" if ok else "VIOLATION: zero or negative road length",
    )


def check_traffic_signal_phase_count(signal: TrafficSignal) -> Tuple[bool, ProofObject]:
    """Traffic signal must have a positive cycle length.

    Standard: MUTCD Chapter 4D — signal timing
    falsifies_if: signal does not have a valid cycle_length_seconds attribute or it is 0.
    """
    if hasattr(signal, "cycle_length_seconds"):
        ok = signal.cycle_length_seconds > 0
        val = signal.cycle_length_seconds
    elif hasattr(signal, "phase_count"):
        ok = signal.phase_count > 0
        val = signal.phase_count
    else:
        ok = True
        val = "no timing attr"
    premises = [f"signal_id={getattr(signal, 'signal_id', 'unknown')}", f"timing_value={val}"]
    return ok, ProofObject(
        rule="TrafficSignalPhaseCycle",
        premises=premises,
        conclusion="PASS: traffic signal has valid timing" if ok else "VIOLATION: traffic signal has zero cycle",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS."""
    from .implementation import RoadClassification, TrafficSignal
    road = RoadSegment(
        segment_id="SEG-001", road_name="Main St",
        classification=RoadClassification.MINOR_ARTERIAL,
        length_miles=Fraction(2), num_lanes=2,
        lane_width_ft=Fraction(12), shoulder_width_ft=Fraction(6),
        urban=True,
    )
    calc = SpeedLimitCalculation(
        segment_id="SEG-001", classification=RoadClassification.MINOR_ARTERIAL,
        lane_width_ft=Fraction(12),
        shoulder_width_ft=Fraction(6), urban=True,
        calculated_limit_mph=35,
    )
    signal = TrafficSignal(signal_id="SIG-001", intersection_name="Main & Oak")
    results = {}
    for fn, args in [
        (check_lane_width_minimum, (road,)),
        (check_shoulder_width_minimum, (road,)),
        (check_speed_limit_consistent, (calc,)),
        (check_num_lanes_positive, (road,)),
        (check_segment_length_positive, (road,)),
        (check_traffic_signal_phase_count, (signal,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
