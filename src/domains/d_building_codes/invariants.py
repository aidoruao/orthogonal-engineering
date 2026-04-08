"""D_BUILDING_CODES invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: International Building Code (IBC), NFPA 101, ADA Standards
"""

from fractions import Fraction
from datetime import datetime, timedelta
from src.domains.d_building_codes.implementation import (
    StructuralEngineer,
    FireEgressPlanner,
    ADAComplianceChecker,
    BuildingCodeAuditor,
    BuildingStructure,
    LoadCalculation,
    StructuralLoad,
    EgressSystem,
    EgressComponent,
    ADAFeature,
    AccessibleRoute,
    OccupancyType,
    ConstructionType,
    LoadType,
    EgressComponentType,
)


def check_structural_load_within_tolerance() -> bool:
    """
    Invariant: Structural load calculations within IBC tolerance.
    Falsification: If calculated load exceeds capacity (safety ratio < 1.0).
    """
    engineer = StructuralEngineer()
    
    # Safe design - capacity exceeds load
    safe_calc = LoadCalculation(
        calculation_id="C001",
        building_id="B001",
        element="Beam_A1",
        dead_load=Fraction(30),  # 30 psf
        live_load=Fraction(50),  # 50 psf
        calculated_capacity=Fraction(200),  # Can handle 200 psf
        applied_load=Fraction(128),  # Factored load
    )
    
    result = engineer.check_member_capacity(safe_calc)
    assert result["within_tolerance"] is True, (
        "Safe design should be within tolerance"
    )
    assert result["compliant"] is True, (
        "Safe design should be compliant"
    )
    assert safe_calc.safety_ratio >= Fraction(1), (
        "Safety ratio should be >= 1.0"
    )
    
    # Unsafe design - load exceeds capacity
    unsafe_calc = LoadCalculation(
        calculation_id="C002",
        building_id="B001",
        element="Beam_A2",
        dead_load=Fraction(30),
        live_load=Fraction(50),
        calculated_capacity=Fraction(100),  # Can only handle 100 psf
        applied_load=Fraction(128),  # But needs 128 psf
    )
    
    result2 = engineer.check_member_capacity(unsafe_calc)
    assert result2["within_tolerance"] is False, (
        "Unsafe design should not be within tolerance"
    )
    assert result2["compliant"] is False, (
        "Unsafe design should not be compliant"
    )
    assert unsafe_calc.safety_ratio < Fraction(1), (
        "Safety ratio should be < 1.0 for unsafe design"
    )
    
    return True


def check_fire_egress_requirements_met() -> bool:
    """
    Invariant: Fire egress requirements met for occupancy type.
    Falsification: If insufficient exits for occupant load.
    """
    planner = FireEgressPlanner()
    
    # Small assembly (200 occupants) - requires 2 exits
    small_egress = EgressSystem(
        building_id="B001",
        occupancy_type=OccupancyType.ASSEMBLY,
        occupant_load=200,
        exits=[
            EgressComponent(
                component_id="E1",
                component_type=EgressComponentType.DOOR,
                width_inches=Fraction(72),
                capacity_persons=150,
            ),
            EgressComponent(
                component_id="E2",
                component_type=EgressComponentType.DOOR,
                width_inches=Fraction(72),
                capacity_persons=150,
            ),
        ],
    )
    
    result = planner.check_egress_capacity(small_egress)
    assert result["egress_compliant"] is True, (
        "200 occupants with 2 exits should be compliant"
    )
    assert result["required_exits"] == 2, (
        "200 occupants requires 2 exits"
    )
    
    # Large assembly (750 occupants) - requires 3 exits
    large_egress = EgressSystem(
        building_id="B002",
        occupancy_type=OccupancyType.ASSEMBLY,
        occupant_load=750,
        exits=[
            EgressComponent(
                component_id="E1",
                component_type=EgressComponentType.DOOR,
                width_inches=Fraction(72),
                capacity_persons=300,
            ),
            EgressComponent(
                component_id="E2",
                component_type=EgressComponentType.DOOR,
                width_inches=Fraction(72),
                capacity_persons=300,
            ),
            EgressComponent(
                component_id="E3",
                component_type=EgressComponentType.DOOR,
                width_inches=Fraction(72),
                capacity_persons=300,
            ),
        ],
    )
    
    result2 = planner.check_egress_capacity(large_egress)
    assert result2["egress_compliant"] is True, (
        "750 occupants with 3 exits should be compliant"
    )
    assert result2["required_exits"] == 3, (
        "750 occupants requires 3 exits"
    )
    
    # Non-compliant: 750 occupants with only 2 exits
    noncompliant_egress = EgressSystem(
        building_id="B003",
        occupancy_type=OccupancyType.ASSEMBLY,
        occupant_load=750,
        exits=[
            EgressComponent(
                component_id="E1",
                component_type=EgressComponentType.DOOR,
                width_inches=Fraction(72),
                capacity_persons=300,
            ),
            EgressComponent(
                component_id="E2",
                component_type=EgressComponentType.DOOR,
                width_inches=Fraction(72),
                capacity_persons=300,
            ),
        ],
    )
    
    result3 = planner.check_egress_capacity(noncompliant_egress)
    assert result3["egress_compliant"] is False, (
        "750 occupants with only 2 exits should be non-compliant"
    )
    
    return True


def check_ada_accessibility_enforced() -> bool:
    """
    Invariant: ADA accessibility enforced for public accommodations.
    Falsification: If accessibility violations are not detected.
    """
    checker = ADAComplianceChecker()
    
    # Compliant ramp (1:12 slope)
    compliant_ramp = checker.check_ramp_slope(
        rise_inches=Fraction(1),
        run_inches=Fraction(12),
    )
    assert compliant_ramp["compliant"] is True, (
        "1:12 ramp slope should be compliant"
    )
    assert compliant_ramp["slope"] <= checker.MAX_RAMP_SLOPE, (
        "Slope should be <= max allowed"
    )
    
    # Non-compliant ramp (too steep)
    steep_ramp = checker.check_ramp_slope(
        rise_inches=Fraction(1),
        run_inches=Fraction(8),  # 1:8 slope - too steep
    )
    assert steep_ramp["compliant"] is False, (
        "1:8 ramp slope should be non-compliant"
    )
    assert steep_ramp["slope"] > checker.MAX_RAMP_SLOPE, (
        "Steep slope should exceed max allowed"
    )
    
    # Compliant accessible parking
    compliant_parking = checker.check_accessible_parking(
        total_spaces=100,
        accessible_spaces=2,
    )
    assert compliant_parking["compliant"] is True, (
        "2 accessible spaces for 100 total should be compliant"
    )
    
    # Non-compliant accessible parking
    noncompliant_parking = checker.check_accessible_parking(
        total_spaces=100,
        accessible_spaces=1,  # Need at least 2
    )
    assert noncompliant_parking["compliant"] is False, (
        "1 accessible space for 100 total should be non-compliant"
    )
    
    return True


def check_accessible_route_compliance() -> bool:
    """
    Invariant: Accessible routes must have all compliant components.
    Falsification: If route with noncompliant component passes check.
    """
    checker = ADAComplianceChecker()
    
    # Fully compliant route
    compliant_route = AccessibleRoute(
        route_id="R001",
        start_location="Entrance",
        end_location="Main Hall",
        components=[
            ADAFeature(
                feature_id="F1",
                feature_type="ramp",
                slope_ratio=Fraction(1, 12),
                width_inches=Fraction(36),
                compliant=True,
            ),
            ADAFeature(
                feature_id="F2",
                feature_type="door",
                width_inches=Fraction(36),
                compliant=True,
            ),
        ],
    )
    
    result = checker.check_accessible_route(compliant_route)
    assert result["fully_compliant"] is True, (
        "Route with all compliant components should be fully compliant"
    )
    
    # Route with noncompliant component
    noncompliant_route = AccessibleRoute(
        route_id="R002",
        start_location="Entrance",
        end_location="Upper Level",
        components=[
            ADAFeature(
                feature_id="F1",
                feature_type="ramp",
                slope_ratio=Fraction(1, 12),
                width_inches=Fraction(36),
                compliant=True,
            ),
            ADAFeature(
                feature_id="F2",
                feature_type="ramp",
                slope_ratio=Fraction(1, 8),  # Too steep
                width_inches=Fraction(30),  # Too narrow
                compliant=False,
                noncompliance_issues=["slope too steep", "width insufficient"],
            ),
        ],
    )
    
    result2 = checker.check_accessible_route(noncompliant_route)
    assert result2["fully_compliant"] is False, (
        "Route with noncompliant component should not be fully compliant"
    )
    assert result2["noncompliant_count"] == 1, (
        "Should detect 1 noncompliant component"
    )
    
    return True


def check_egress_width_requirements() -> bool:
    """
    Invariant: Egress components must meet minimum width requirements.
    Falsification: If narrow egress component passes width check.
    """
    # Compliant door (44 inches minimum)
    compliant_door = EgressComponent(
        component_id="D1",
        component_type=EgressComponentType.DOOR,
        width_inches=Fraction(44),
        capacity_persons=100,
        required_width_inches=Fraction(44),
    )
    
    assert compliant_door.width_compliant is True, (
        "44-inch door should meet 44-inch requirement"
    )
    
    # Non-compliant door (too narrow)
    narrow_door = EgressComponent(
        component_id="D2",
        component_type=EgressComponentType.DOOR,
        width_inches=Fraction(32),  # Below minimum
        capacity_persons=50,
        required_width_inches=Fraction(44),
    )
    
    assert narrow_door.width_compliant is False, (
        "32-inch door should not meet 44-inch requirement"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("structural_tolerance", check_structural_load_within_tolerance),
        ("fire_egress", check_fire_egress_requirements_met),
        ("ada_accessibility", check_ada_accessibility_enforced),
        ("accessible_route", check_accessible_route_compliance),
        ("egress_width", check_egress_width_requirements),
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
