"""D_ROAD_STANDARDS invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: MUTCD, AASHTO Green Book
"""

from fractions import Fraction
from datetime import datetime, timedelta
from src.domains.d_road_standards.implementation import (
    SpeedLimitEngine,
    SignalTimingEngine,
    MaintenanceScheduler,
    RoadStandardsAuditor,
    RoadSegment,
    TrafficSignal,
    TrafficConditions,
    MaintenanceSchedule,
    SpeedLimitCalculation,
    SignalTimingPlan,
    RoadClassification,
    SignalPhase,
    MaintenanceType,
)


def check_speed_limit_deterministic() -> bool:
    """
    Invariant: Speed limit is deterministic per road classification.
    Falsification: If same road characteristics produce different limits.
    """
    engine = SpeedLimitEngine()
    
    # Create a road segment
    segment = RoadSegment(
        segment_id="R001",
        road_name="Main Street",
        classification=RoadClassification.PRINCIPAL_ARTERIAL,
        length_miles=Fraction(2),
        num_lanes=4,
        lane_width_ft=Fraction(11),
        shoulder_width_ft=Fraction(4),
        urban=True,
    )
    
    # Calculate multiple times
    calc1 = engine.calculate_speed_limit(segment)
    calc2 = engine.calculate_speed_limit(segment)
    calc3 = engine.calculate_speed_limit(segment)
    
    # Should be identical (deterministic)
    assert calc1.calculated_limit_mph == calc2.calculated_limit_mph, (
        "Speed limit calculation must be deterministic"
    )
    assert calc2.calculated_limit_mph == calc3.calculated_limit_mph, (
        "Speed limit calculation must be reproducible"
    )
    
    return True


def check_speed_limit_by_classification() -> bool:
    """
    Invariant: Different classifications produce different limits.
    Falsification: If all classifications produce same limit.
    """
    engine = SpeedLimitEngine()
    
    # Test different classifications
    results = {}
    for classification in [
        RoadClassification.LOCAL_RESIDENTIAL,
        RoadClassification.MINOR_ARTERIAL,
        RoadClassification.PRINCIPAL_ARTERIAL,
    ]:
        segment = RoadSegment(
            segment_id=f"R_{classification.name}",
            road_name="Test Road",
            classification=classification,
            length_miles=Fraction(1),
            num_lanes=2,
            lane_width_ft=Fraction(11),
            shoulder_width_ft=Fraction(4),
            urban=True,
        )
        calc = engine.calculate_speed_limit(segment)
        results[classification.name] = calc.calculated_limit_mph
    
    # Residential should be lower than arterial
    assert results["LOCAL_RESIDENTIAL"] < results["PRINCIPAL_ARTERIAL"], (
        "Residential speed limit should be lower than arterial"
    )
    
    # Minor arterial should be between residential and principal
    assert results["LOCAL_RESIDENTIAL"] <= results["MINOR_ARTERIAL"] <= results["PRINCIPAL_ARTERIAL"], (
        "Minor arterial should be between residential and principal"
    )
    
    return True


def check_signal_timing_reproducible() -> bool:
    """
    Invariant: Signal timing is reproducible for given traffic conditions.
    Falsification: If same conditions produce different timing plans.
    """
    engine = SignalTimingEngine()
    
    signal = TrafficSignal(
        signal_id="S001",
        intersection_name="Main & 1st",
    )
    
    conditions = TrafficConditions(
        intersection_id="I001",
        timestamp=datetime.now(),
        approach_volumes={
            "north": 500,
            "south": 500,
            "east": 300,
            "west": 300,
        },
        detector_occupancy={},
        pedestrian_calls={},
    )
    
    # Calculate timing multiple times
    plan1 = engine.calculate_timing(signal, conditions)
    plan2 = engine.calculate_timing(signal, conditions)
    plan3 = engine.calculate_timing(signal, conditions)
    
    # All should be identical
    assert plan1.green_times == plan2.green_times == plan3.green_times, (
        "Signal timing must be reproducible"
    )
    assert plan1.cycle_length == plan2.cycle_length == plan3.cycle_length, (
        "Cycle length must be reproducible"
    )
    assert plan1.traffic_conditions_hash == plan2.traffic_conditions_hash, (
        "Conditions hash must match"
    )
    
    return True


def check_signal_timing_responds_to_volume() -> bool:
    """
    Invariant: Higher volume approaches receive more green time.
    Falsification: If low-volume approach gets more green than high-volume.
    """
    engine = SignalTimingEngine()
    
    signal = TrafficSignal(
        signal_id="S002",
        intersection_name="Main & 2nd",
    )
    
    # High volume on north-south
    high_ns_conditions = TrafficConditions(
        intersection_id="I002",
        timestamp=datetime.now(),
        approach_volumes={
            "north": 800,
            "south": 800,
            "east": 200,
            "west": 200,
        },
        detector_occupancy={},
        pedestrian_calls={},
    )
    
    plan = engine.calculate_timing(signal, high_ns_conditions)
    
    # North should have more green than east
    assert plan.green_times["north"] > plan.green_times["east"], (
        "High-volume approach should get more green time"
    )
    
    return True


def check_maintenance_schedule_logged() -> bool:
    """
    Invariant: Maintenance schedule is logged and executed.
    Falsification: If unexecuted maintenance passes compliance check.
    """
    scheduler = MaintenanceScheduler()
    
    # Create schedule
    schedule = scheduler.create_schedule(
        schedule_id="M001",
        segment_id="R001",
        maintenance_type=MaintenanceType.PAVEMENT_REPAIR,
        scheduled_date=datetime.now(),
    )
    
    # Check before execution
    result_before = scheduler.check_schedule_compliance(schedule.schedule_id)
    assert result_before["executed"] is False, (
        "Unexecuted maintenance should not be marked executed"
    )
    assert result_before["compliant"] is False, (
        "Unexecuted maintenance should not be compliant"
    )
    
    # Execute maintenance
    scheduler.execute_maintenance(
        schedule_id="M001",
        work_order="WO-2024-001",
        crew="Crew A",
    )
    
    # Check after execution
    result_after = scheduler.check_schedule_compliance(schedule.schedule_id)
    assert result_after["executed"] is True, (
        "Executed maintenance should be marked executed"
    )
    assert result_after["documented"] is True, (
        "Maintenance with work order should be documented"
    )
    assert result_after["has_crew_assignment"] is True, (
        "Maintenance should have crew assignment"
    )
    assert result_after["compliant"] is True, (
        "Executed and documented maintenance should be compliant"
    )
    
    return True


def check_maintenance_requires_work_order() -> bool:
    """
    Invariant: Maintenance requires work order number.
    Falsification: If maintenance without work order passes compliance.
    """
    scheduler = MaintenanceScheduler()
    
    schedule = scheduler.create_schedule(
        schedule_id="M002",
        segment_id="R002",
        maintenance_type=MaintenanceType.SIGN_REPLACEMENT,
        scheduled_date=datetime.now(),
    )
    
    # Mark as completed without work order (invalid)
    schedule.completed = True
    schedule.executed_date = datetime.now()
    # Missing: work_order_number
    
    result = scheduler.check_schedule_compliance(schedule.schedule_id)
    assert result["documented"] is False, (
        "Maintenance without work order should not be documented"
    )
    assert result["compliant"] is False, (
        "Maintenance without work order should not be compliant"
    )
    
    return True


def check_urban_rural_speed_difference() -> bool:
    """
    Invariant: Rural roads have higher speed limits than urban for same classification.
    Falsification: If urban and rural produce same limits when they shouldn't.
    """
    engine = SpeedLimitEngine()
    
    # Urban arterial
    urban_segment = RoadSegment(
        segment_id="R_URBAN",
        road_name="Urban Arterial",
        classification=RoadClassification.PRINCIPAL_ARTERIAL,
        length_miles=Fraction(5),
        num_lanes=4,
        lane_width_ft=Fraction(11),
        shoulder_width_ft=Fraction(4),
        urban=True,
    )
    
    # Rural arterial (same classification)
    rural_segment = RoadSegment(
        segment_id="R_RURAL",
        road_name="Rural Arterial",
        classification=RoadClassification.PRINCIPAL_ARTERIAL,
        length_miles=Fraction(5),
        num_lanes=4,
        lane_width_ft=Fraction(11),
        shoulder_width_ft=Fraction(4),
        urban=False,
    )
    
    urban_limit = engine.calculate_speed_limit(urban_segment)
    rural_limit = engine.calculate_speed_limit(rural_segment)
    
    # Rural should generally be higher (or at least not lower)
    assert rural_limit.calculated_limit_mph >= urban_limit.calculated_limit_mph, (
        "Rural speed limit should be >= urban for same classification"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("speed_deterministic", check_speed_limit_deterministic),
        ("speed_by_classification", check_speed_limit_by_classification),
        ("signal_reproducible", check_signal_timing_reproducible),
        ("signal_volume_response", check_signal_timing_responds_to_volume),
        ("maintenance_logged", check_maintenance_schedule_logged),
        ("maintenance_work_order", check_maintenance_requires_work_order),
        ("urban_rural_difference", check_urban_rural_speed_difference),
    ]
    
    for name, check_func in checks:
        try:
            check_func()
            results[name] = "PASS"
        except AssertionError as e:
            results[name] = f"FAIL: {e}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    
    return results
