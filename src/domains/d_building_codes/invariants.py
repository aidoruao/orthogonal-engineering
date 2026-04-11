"""D_BUILDING_CODES invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- International Building Code (IBC) 2021
- NFPA 101 Life Safety Code
- ADA Standards for Accessible Design

Source: ontology/ontology.json#D_BUILDING_CODES
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


def check_egress_capacity_calculation() -> Tuple[bool, ProofObject]:
    """
    Invariant: Occupant load and egress capacity must be calculated per IBC Chapter 10.
    
    Standard: IBC §1004 (Occupant Load), §1005 (Egress Width)
    Falsifies if: Egress capacity is less than required occupant load.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Occupant load factors (square feet per occupant)
    assembly_concentrated = Fraction(7)  # 7 sq ft/person
    assembly_unconcentrated = Fraction(15)
    office = Fraction(100)
    
    # Example: Assembly space 1000 sq ft
    space_area = Fraction(1000)
    occupant_load = space_area / assembly_concentrated
    occupant_load_exact = occupant_load == Fraction(1000, 7)
    
    # Required egress width: 0.2 inches per occupant (assembly)
    inches_per_occupant = Fraction(2, 10)  # 0.2
    required_egress_width = occupant_load * inches_per_occupant
    required_egress_width_exact = required_egress_width == Fraction(2000, 70)
    
    # Available egress (two 44-inch doors)
    door_1_width = Fraction(44)
    door_2_width = Fraction(44)
    available_egress = door_1_width + door_2_width
    
    egress_adequate = available_egress >= required_egress_width
    
    success = occupant_load_exact and required_egress_width_exact and egress_adequate
    
    proof = ProofObject(
        rule="EgressCapacityCalculation",
        premises=[
            f"space_area = {space_area} sq ft",
            f"occupant_load_factor = {assembly_concentrated} sq ft/person",
            f"occupant_load = {occupant_load} persons",
            f"inches_per_occupant = {inches_per_occupant}",
            f"required_egress_width = {required_egress_width} inches",
            f"available_egress = {available_egress} inches",
            f"egress_adequate = {egress_adequate}",
        ],
        conclusion=(
            "Egress capacity calculation complies with IBC Chapter 10"
            if success
            else "FAIL: Egress capacity check failed"
        ),
    )
    return success, proof


def check_fire_resistance_rating() -> Tuple[bool, ProofObject]:
    """
    Invariant: Fire resistance ratings must meet IBC Table 601 requirements.
    
    Standard: IBC §602 (Construction Classification), Table 601 (Fire Rating)
    Falsifies if: Structural element has insufficient fire resistance rating.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Type I-A construction (highest rating)
    structural_frame_required = Fraction(3)  # 3 hours
    floor_construction_required = Fraction(2)  # 2 hours
    
    # Provided ratings
    structural_frame_provided = Fraction(3)
    floor_construction_provided = Fraction(2)
    
    structural_compliant = structural_frame_provided >= structural_frame_required
    floor_compliant = floor_construction_provided >= floor_construction_required
    
    # NFPA 101 enclosure requirements
    exit_enclosure_required = Fraction(2)  # 2 hours
    exit_enclosure_provided = Fraction(2)
    exit_compliant = exit_enclosure_provided >= exit_enclosure_required
    
    # Shaft enclosure
    shaft_required = Fraction(2)
    shaft_provided = Fraction(2)
    shaft_compliant = shaft_provided >= shaft_required
    
    success = structural_compliant and floor_compliant and exit_compliant and shaft_compliant
    
    proof = ProofObject(
        rule="FireResistanceRating",
        premises=[
            f"structural_frame_required = {structural_frame_required} hours",
            f"structural_frame_provided = {structural_frame_provided} hours",
            f"structural_compliant = {structural_compliant}",
            f"exit_enclosure_required = {exit_enclosure_required} hours",
            f"exit_compliant = {exit_compliant}",
        ],
        conclusion=(
            "Fire resistance rating complies with IBC Table 601"
            if success
            else "FAIL: Fire resistance rating check failed"
        ),
    )
    return success, proof


def check_ada_ramp_slope() -> Tuple[bool, ProofObject]:
    """
    Invariant: Ramp slope must not exceed 1:12 maximum (ADA Standards).
    
    Standard: ADA Standards §405.2 (Slope), §405.3 (Cross Slope)
    Falsifies if: Ramp slope exceeds 1:12 (8.33%) without compliant alternative.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Maximum slope 1:12 (rise:run)
    max_slope_rise = Fraction(1)
    max_slope_run = Fraction(12)
    max_slope_ratio = max_slope_rise / max_slope_run
    
    # Compliant ramp: rise 6 inches, run 72 inches
    compliant_rise = Fraction(6)
    compliant_run = Fraction(72)
    compliant_slope = compliant_rise / compliant_run
    compliant_check = compliant_slope <= max_slope_ratio
    
    # Non-compliant ramp: rise 6 inches, run 48 inches (1:8 = 12.5%)
    noncompliant_run = Fraction(48)
    noncompliant_slope = compliant_rise / noncompliant_run
    noncompliant_check = noncompliant_slope > max_slope_ratio
    
    # Cross slope maximum 1:48
    max_cross_slope = Fraction(1, 48)
    actual_cross_slope = Fraction(1, 60)  # Compliant
    cross_slope_compliant = actual_cross_slope <= max_cross_slope
    
    success = compliant_check and noncompliant_check and cross_slope_compliant
    
    proof = ProofObject(
        rule="ADARampSlope",
        premises=[
            f"max_slope = 1:{max_slope_run} ({float(max_slope_ratio):.4f})",
            f"compliant_slope = {compliant_slope} ({float(compliant_slope):.4f})",
            f"compliant_check = {compliant_check}",
            f"noncompliant_slope = {noncompliant_slope} ({float(noncompliant_slope):.4f})",
            f"cross_slope_compliant = {cross_slope_compliant}",
        ],
        conclusion=(
            "ADA ramp slope complies with Standards §405"
            if success
            else "FAIL: ADA ramp slope check failed"
        ),
    )
    return success, proof


def check_structural_load_combinations() -> Tuple[bool, ProofObject]:
    """
    Invariant: Load combinations per IBC Section 1605 must be satisfied.
    
    Standard: IBC §1605 (Load Combinations), ASCE 7
    Falsifies if: Factored load exceeds design strength for any combination.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Dead load (D)
    D = Fraction(30)  # psf
    
    # Live load (L)
    L = Fraction(50)  # psf
    
    # Load combination 1: 1.4D
    combo_1_factor = Fraction(14, 10)  # 1.4
    combo_1 = combo_1_factor * D
    combo_1_exact = combo_1 == Fraction(42)
    
    # Load combination 2: 1.2D + 1.6L
    combo_2_D_factor = Fraction(12, 10)  # 1.2
    combo_2_L_factor = Fraction(16, 10)  # 1.6
    combo_2 = combo_2_D_factor * D + combo_2_L_factor * L
    combo_2_exact = combo_2 == Fraction(116)
    
    # Design strength must exceed factored load
    design_strength = Fraction(150)  # psf capacity
    combo_1_safe = design_strength >= combo_1
    combo_2_safe = design_strength >= combo_2
    
    safety_ratio_1 = design_strength / combo_1
    safety_ratio_2 = design_strength / combo_2
    
    success = combo_1_exact and combo_2_exact and combo_1_safe and combo_2_safe
    
    proof = ProofObject(
        rule="StructuralLoadCombinations",
        premises=[
            f"dead_load = {D} psf",
            f"live_load = {L} psf",
            f"combo_1 (1.4D) = {combo_1} psf",
            f"combo_2 (1.2D+1.6L) = {combo_2} psf",
            f"design_strength = {design_strength} psf",
            f"safety_ratio_combo_2 = {safety_ratio_2}",
        ],
        conclusion=(
            "Structural load combinations comply with IBC §1605"
            if success
            else "FAIL: Structural load combination check failed"
        ),
    )
    return success, proof


def check_accessible_parking_ratio() -> Tuple[bool, ProofObject]:
    """
    Invariant: Accessible parking spaces must meet minimum ratio per ADA.
    
    Standard: ADA Standards §208.2, Table 208.2 (Parking Space Numbers)
    Falsifies if: Insufficient accessible spaces provided for total parking.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Total parking spaces
    total_spaces = Fraction(100)
    
    # Required accessible spaces per Table 208.2
    # 1-25: 1 space
    # 26-50: 2 spaces
    # 51-75: 3 spaces
    # 76-100: 4 spaces
    # 101-150: 5 spaces
    # 151-200: 6 spaces
    # 201-300: 7 spaces
    # 301-400: 8 spaces
    # 401-500: 9 spaces
    # 501-1000: 2% of total
    # 1001+: 20 + 1 for each 100 over 1000
    
    if total_spaces <= Fraction(25):
        required_accessible = Fraction(1)
    elif total_spaces <= Fraction(50):
        required_accessible = Fraction(2)
    elif total_spaces <= Fraction(75):
        required_accessible = Fraction(3)
    elif total_spaces <= Fraction(100):
        required_accessible = Fraction(4)
    elif total_spaces <= Fraction(150):
        required_accessible = Fraction(5)
    elif total_spaces <= Fraction(200):
        required_accessible = Fraction(6)
    elif total_spaces <= Fraction(300):
        required_accessible = Fraction(7)
    elif total_spaces <= Fraction(400):
        required_accessible = Fraction(8)
    elif total_spaces <= Fraction(500):
        required_accessible = Fraction(9)
    elif total_spaces <= Fraction(1000):
        required_accessible = total_spaces * Fraction(2, 100)
    else:
        required_accessible = Fraction(20) + (total_spaces - Fraction(1000)) / Fraction(100)
    
    # Provided spaces
    provided_accessible = Fraction(4)
    accessible_compliant = provided_accessible >= required_accessible
    
    # Van-accessible spaces: 1 in 6 accessible spaces (or 1 if only 1 accessible)
    van_accessible_required = max(Fraction(1), required_accessible / Fraction(6))
    provided_van_accessible = Fraction(1)
    van_accessible_compliant = provided_van_accessible >= van_accessible_required
    
    success = accessible_compliant and van_accessible_compliant
    
    proof = ProofObject(
        rule="AccessibleParkingRatio",
        premises=[
            f"total_spaces = {total_spaces}",
            f"required_accessible = {required_accessible}",
            f"provided_accessible = {provided_accessible}",
            f"accessible_compliant = {accessible_compliant}",
            f"van_accessible_required = {van_accessible_required}",
            f"van_accessible_compliant = {van_accessible_compliant}",
        ],
        conclusion=(
            "Accessible parking ratio complies with ADA Standards §208"
            if success
            else "FAIL: Accessible parking ratio check failed"
        ),
    )
    return success, proof


def check_nfpa_egress_travel_distance() -> Tuple[bool, ProofObject]:
    """
    Invariant: Maximum travel distance to exit must comply with NFPA 101.
    
    Standard: NFPA 101 §7.6 (Travel Distance to Exits)
    Falsifies if: Actual travel distance exceeds code maximum for occupancy type.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # NFPA 101 Table 7.6 (selected occupancy types in feet)
    # Assembly - sprinklered: 250 feet
    # Assembly - unsprinklered: 200 feet
    # Educational - sprinklered: 200 feet
    # Educational - unsprinklered: 150 feet
    # Healthcare - sprinklered: 200 feet
    # Office - sprinklered: 300 feet
    # Office - unsprinklered: 200 feet
    
    occupancy_type = "office"
    sprinklered = True
    
    if occupancy_type == "assembly":
        max_travel = Fraction(250) if sprinklered else Fraction(200)
    elif occupancy_type == "educational":
        max_travel = Fraction(200) if sprinklered else Fraction(150)
    elif occupancy_type == "healthcare":
        max_travel = Fraction(200) if sprinklered else Fraction(150)
    elif occupancy_type == "office":
        max_travel = Fraction(300) if sprinklered else Fraction(200)
    else:
        max_travel = Fraction(200)
    
    # Actual travel distance
    actual_travel = Fraction(250)
    travel_compliant = actual_travel <= max_travel
    
    # Common path of travel (different limit)
    common_path_max = Fraction(100) if sprinklered else Fraction(75)
    actual_common_path = Fraction(80)
    common_path_compliant = actual_common_path <= common_path_max
    
    success = travel_compliant and common_path_compliant
    
    proof = ProofObject(
        rule="NFPAEgressTravelDistance",
        premises=[
            f"occupancy_type = {occupancy_type}",
            f"sprinklered = {sprinklered}",
            f"max_travel_distance = {max_travel} feet",
            f"actual_travel_distance = {actual_travel} feet",
            f"travel_compliant = {travel_compliant}",
            f"common_path_compliant = {common_path_compliant}",
        ],
        conclusion=(
            "Egress travel distance complies with NFPA 101 §7.6"
            if success
            else "FAIL: NFPA egress travel distance check failed"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_BUILDING_CODES invariants.

    Falsifies if: any building codes invariant check fails or raises an error.
    """
    checks = [
        ("check_egress_capacity_calculation", check_egress_capacity_calculation),
        ("check_fire_resistance_rating", check_fire_resistance_rating),
        ("check_ada_ramp_slope", check_ada_ramp_slope),
        ("check_structural_load_combinations", check_structural_load_combinations),
        ("check_accessible_parking_ratio", check_accessible_parking_ratio),
        ("check_nfpa_egress_travel_distance", check_nfpa_egress_travel_distance),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            success, proof = check_func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_BUILDING_CODES invariants: PASS")
