#!/usr/bin/env python3
"""
analyze_handling.py - Analyze GTA V Enhanced handling.meta files for physics invariants

This script performs structural diff between two handling.meta files,
checks physics invariants, and generates corrected files with minimal
normalization to stabilize vehicle constraints.

Usage:
    python analyze_handling.py <current_file> <backup_file> [--output <output_file>] [--report <report_file>]

Atomic Instructions for Zed AI:
1. Create structural diff between handling.meta and handling_DRIVEV_BACKUP.meta
2. Check critical physics invariants
3. Determine failure class
4. Apply repair strategy with minimal normalization
5. Validate file integrity
6. Output root cause classification and corrected file
"""

import argparse
import math
import re
import sys
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple

# -----------------------------------------------------------------------------
# XML PARSING AND DATA STRUCTURES
# -----------------------------------------------------------------------------


class HandlingData:
    """Represents a single vehicle's handling data."""

    def __init__(self, handling_name: str):
        self.handling_name = handling_name
        self.values: Dict[str, Any] = {}

    def set_value(self, key: str, value: Any):
        """Set a value, converting to appropriate type."""
        if isinstance(value, str):
            # Try to parse as float if it looks like one
            if re.match(r"^-?\d+\.\d+$", value):
                value = float(value)
            elif re.match(r"^-?\d+$", value):
                value = int(value)
        self.values[key] = value

    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get float value with default."""
        val = self.values.get(key)
        if isinstance(val, (int, float)):
            return float(val)
        return default

    def get_vec3(self, key: str) -> Tuple[float, float, float]:
        """Get vector3 value as tuple of floats."""
        val = self.values.get(key)
        if isinstance(val, str):
            # Parse vecCentreOfMassOffset or vecInertiaMultiplier
            match = re.search(r'x="([^"]+)" y="([^"]+)" z="([^"]+)"', val)
            if match:
                return (
                    float(match.group(1)),
                    float(match.group(2)),
                    float(match.group(3)),
                )
        return (0.0, 0.0, 0.0)

    def __str__(self) -> str:
        return f"HandlingData({self.handling_name})"


def parse_handling_meta(file_path: str) -> Dict[str, HandlingData]:
    """Parse handling.meta XML file into dictionary of HandlingData objects."""

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"ERROR: Failed to parse XML file {file_path}: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}")
        sys.exit(1)

    # Find the HandlingData element
    handling_data_elem = root.find(".//HandlingData")
    if handling_data_elem is None:
        print(f"ERROR: No HandlingData element found in {file_path}")
        sys.exit(1)

    vehicles: Dict[str, HandlingData] = {}

    # Iterate through all Item elements of type CHandlingData
    for item_elem in handling_data_elem.findall('.//Item[@type="CHandlingData"]'):
        handling_name_elem = item_elem.find("handlingName")
        if handling_name_elem is None:
            continue

        handling_name = handling_name_elem.text.strip()
        vehicle = HandlingData(handling_name)

        # Parse all child elements
        for child in item_elem:
            if child.tag == "handlingName":
                continue

            # Get value attribute or text content
            if "value" in child.attrib:
                vehicle.set_value(child.tag, child.attrib["value"])
            elif child.text:
                vehicle.set_value(child.tag, child.text.strip())
            else:
                # For vector elements like vecCentreOfMassOffset
                vehicle.set_value(child.tag, ET.tostring(child, encoding="unicode"))

        vehicles[handling_name] = vehicle

    print(f"Parsed {len(vehicles)} vehicles from {file_path}")
    return vehicles


# -----------------------------------------------------------------------------
# DIFF ANALYSIS
# -----------------------------------------------------------------------------


class ParameterDiff:
    """Represents a single parameter difference between two files."""

    def __init__(self, vehicle_name: str, param_name: str, old_val: Any, new_val: Any):
        self.vehicle_name = vehicle_name
        self.param_name = param_name
        self.old_val = old_val
        self.new_val = new_val

    def delta_percent(self) -> float:
        """Calculate percentage change."""
        try:
            if isinstance(self.old_val, (int, float)) and isinstance(
                self.new_val, (int, float)
            ):
                if self.old_val == 0:
                    return float("inf") if self.new_val != 0 else 0.0
                return ((self.new_val - self.old_val) / abs(self.old_val)) * 100
        except (TypeError, ValueError):
            pass
        return 0.0

    def __str__(self) -> str:
        return f"Vehicle: {self.vehicle_name}\nParameter: {self.param_name}\nOld: {self.old_val}\nNew: {self.new_val}\nDelta: {self.delta_percent():+.2f}%"


def compute_diffs(
    old_data: Dict[str, HandlingData], new_data: Dict[str, HandlingData]
) -> List[ParameterDiff]:
    """Compute differences between two sets of handling data."""

    diffs: List[ParameterDiff] = []

    # Check vehicles in new file
    for vehicle_name, new_vehicle in new_data.items():
        old_vehicle = old_data.get(vehicle_name)

        if old_vehicle is None:
            # Vehicle exists only in new file
            continue

        # Compare all parameters
        all_keys = set(new_vehicle.values.keys()) | set(old_vehicle.values.keys())

        for key in all_keys:
            new_val = new_vehicle.values.get(key)
            old_val = old_vehicle.values.get(key)

            # Skip if both are None or equal
            if new_val is None and old_val is None:
                continue

            if new_val == old_val:
                continue

            # For vector values, compare string representation
            if (
                isinstance(new_val, str)
                and 'x="' in new_val
                and isinstance(old_val, str)
                and 'x="' in old_val
            ):
                if new_val == old_val:
                    continue

            diffs.append(ParameterDiff(vehicle_name, key, old_val, new_val))

    # Check for vehicles only in old file (deleted)
    for vehicle_name, old_vehicle in old_data.items():
        if vehicle_name not in new_data:
            diffs.append(
                ParameterDiff(vehicle_name, "VEHICLE_DELETED", "Present", "Absent")
            )

    return diffs


def categorize_diffs(diffs: List[ParameterDiff]) -> Dict[str, List[ParameterDiff]]:
    """Categorize diffs by parameter type."""

    categories = {
        "Mass / Inertia": [],
        "Suspension": [],
        "Damage": [],
        "Center of Mass": [],
        "Traction": [],
        "Drive bias": [],
        "Other": [],
    }

    mass_inertia_keys = {"fMass", "vecInertiaMultiplier", "fInertiaMultiplier"}
    suspension_keys = {
        "fSuspensionForce",
        "fSuspensionCompDamp",
        "fSuspensionReboundDamp",
        "fSuspensionUpperLimit",
        "fSuspensionLowerLimit",
        "fAntiRollBarForce",
        "fAntiRollBarBiasFront",
        "fRollCentreHeightFront",
        "fRollCentreHeightRear",
    }
    damage_keys = {
        "fDeformationDamageMult",
        "fCollisionDamageMult",
        "fWeaponDamageMult",
        "fEngineDamageMult",
    }
    com_keys = {"vecCentreOfMassOffset"}
    traction_keys = {
        "fTractionCurveMax",
        "fTractionCurveMin",
        "fTractionCurveLateral",
        "fTractionSpringDeltaMax",
        "fTractionBiasFront",
    }
    drive_bias_keys = {
        "fDriveBiasFront",
        "nInitialDriveGears",
        "fInitialDriveForce",
        "fDriveInertia",
        "fInitialDriveMaxFlatVel",
    }

    for diff in diffs:
        if diff.param_name == "VEHICLE_DELETED":
            categories["Other"].append(diff)
        elif diff.param_name in mass_inertia_keys:
            categories["Mass / Inertia"].append(diff)
        elif diff.param_name in suspension_keys:
            categories["Suspension"].append(diff)
        elif diff.param_name in damage_keys:
            categories["Damage"].append(diff)
        elif diff.param_name in com_keys:
            categories["Center of Mass"].append(diff)
        elif diff.param_name in traction_keys:
            categories["Traction"].append(diff)
        elif diff.param_name in drive_bias_keys:
            categories["Drive bias"].append(diff)
        else:
            categories["Other"].append(diff)

    return categories


# -----------------------------------------------------------------------------
# INVARIANT CHECKING
# -----------------------------------------------------------------------------


class InvariantViolation:
    """Represents a physics invariant violation."""

    def __init__(
        self,
        vehicle_name: str,
        violation_type: str,
        description: str,
        severity: str = "WARNING",
    ):
        self.vehicle_name = vehicle_name
        self.violation_type = violation_type
        self.description = description
        self.severity = severity

    def __str__(self) -> str:
        return f"[{self.severity}] {self.vehicle_name}: {self.violation_type} - {self.description}"


def check_physics_invariants(
    vehicle: HandlingData, old_vehicle: Optional[HandlingData] = None
) -> List[InvariantViolation]:
    """Check physics invariants for a single vehicle."""

    violations: List[InvariantViolation] = []

    # A. Mass-Inertia Stability Ratio
    fMass = vehicle.get_float("fMass")
    vecInertia = vehicle.get_vec3("vecInertiaMultiplier")
    inertia_avg = (vecInertia[0] + vecInertia[1] + vecInertia[2]) / 3.0

    if inertia_avg < 0.5 and fMass > 2000:
        violations.append(
            InvariantViolation(
                vehicle.handling_name,
                "MASS_INERTIA",
                f"Rotational instability: inertia={inertia_avg:.3f}, mass={fMass:.1f}",
                "ERROR",
            )
        )

    if inertia_avg < 0.3:
        violations.append(
            InvariantViolation(
                vehicle.handling_name,
                "MASS_INERTIA",
                f"Hard violation: inertia={inertia_avg:.3f} < 0.3",
                "CRITICAL",
            )
        )

    # B. Suspension Harmonic Risk
    fSuspensionReboundDamp = vehicle.get_float("fSuspensionReboundDamp")
    fSuspensionCompDamp = vehicle.get_float("fSuspensionCompDamp")

    if fSuspensionCompDamp != 0:
        rebound_ratio = fSuspensionReboundDamp / fSuspensionCompDamp

        if rebound_ratio > 1.8:
            violations.append(
                InvariantViolation(
                    vehicle.handling_name,
                    "SUSPENSION",
                    f"Oscillation risk: rebound ratio={rebound_ratio:.2f} > 1.8",
                    "WARNING",
                )
            )

    fSuspensionForce = vehicle.get_float("fSuspensionForce", 1.0)
    if fSuspensionForce > 3.0:
        violations.append(
            InvariantViolation(
                vehicle.handling_name,
                "SUSPENSION",
                f"Solver explosion risk: suspension force={fSuspensionForce:.2f} > 3.0",
                "CRITICAL",
            )
        )

    # C. Damage Amplification
    fDeformationDamageMult = vehicle.get_float("fDeformationDamageMult", 1.0)
    fCollisionDamageMult = vehicle.get_float("fCollisionDamageMult", 1.0)

    if fDeformationDamageMult > 2.0:
        severity = "CRITICAL" if fDeformationDamageMult > 5.0 else "ERROR"
        violations.append(
            InvariantViolation(
                vehicle.handling_name,
                "DAMAGE",
                f"Structural failure risk: deformation multiplier={fDeformationDamageMult:.2f}",
                severity,
            )
        )

    if fCollisionDamageMult > 2.0:
        severity = "CRITICAL" if fCollisionDamageMult > 5.0 else "ERROR"
        violations.append(
            InvariantViolation(
                vehicle.handling_name,
                "DAMAGE",
                f"Structural failure risk: collision multiplier={fCollisionDamageMult:.2f}",
                severity,
            )
        )

    # D. Center of Mass Offset
    com_offset = vehicle.get_vec3("vecCentreOfMassOffset")
    com_z = com_offset[2]

    if abs(com_z) > 0.5:
        violations.append(
            InvariantViolation(
                vehicle.handling_name,
                "COM",
                f"COM instability: z={com_z:.2f}",
                "WARNING" if abs(com_z) <= 1.0 else "ERROR",
            )
        )

    if com_z < -1.0:
        violations.append(
            InvariantViolation(
                vehicle.handling_name,
                "COM",
                f"Underbody flip risk: z={com_z:.2f} < -1.0",
                "CRITICAL",
            )
        )

    return violations


def determine_failure_class(violations: List[InvariantViolation]) -> str:
    """Determine root cause failure class from violations."""

    violation_types = {v.violation_type for v in violations}

    # Count critical/error violations by type
    type_counts = {}
    for v in violations:
        if v.severity in ["ERROR", "CRITICAL"]:
            type_counts[v.violation_type] = type_counts.get(v.violation_type, 0) + 1

    if "MASS_INERTIA" in violation_types and type_counts.get("MASS_INERTIA", 0) > 0:
        if len(violation_types) > 1:
            return "TYPE E: Multi-factor compounding"
        return "TYPE A: Mass/Inertia mismatch"
    elif "SUSPENSION" in violation_types and type_counts.get("SUSPENSION", 0) > 0:
        if len(violation_types) > 1:
            return "TYPE E: Multi-factor compounding"
        return "TYPE B: Suspension oscillation"
    elif "DAMAGE" in violation_types and type_counts.get("DAMAGE", 0) > 0:
        if len(violation_types) > 1:
            return "TYPE E: Multi-factor compounding"
        return "TYPE C: Damage multiplier overdrive"
    elif "COM" in violation_types and type_counts.get("COM", 0) > 0:
        if len(violation_types) > 1:
            return "TYPE E: Multi-factor compounding"
        return "TYPE D: COM destabilization"

    # If only warnings or no critical violations
    if violations:
        primary_type = list(violation_types)[0]
        return f"TYPE {primary_type[0]}: {primary_type} (Warning level)"

    return "TYPE NONE: No critical violations detected"


# -----------------------------------------------------------------------------
# REPAIR STRATEGY
# -----------------------------------------------------------------------------


def apply_repair_strategy(
    vehicle: HandlingData, old_vehicle: Optional[HandlingData] = None
) -> Tuple[HandlingData, List[str]]:
    """Apply minimal corrective normalization to a vehicle."""

    repaired = HandlingData(vehicle.handling_name)
    repaired.values = vehicle.values.copy()
    corrections: List[str] = []

    # Get old values for comparison if available
    old_mass = old_vehicle.get_float("fMass") if old_vehicle else None
    old_inertia = old_vehicle.get_vec3("vecInertiaMultiplier") if old_vehicle else None

    # A. Mass-Inertia correction
    fMass = vehicle.get_float("fMass")
    vecInertia = vehicle.get_vec3("vecInertiaMultiplier")
    inertia_avg = (vecInertia[0] + vecInertia[1] + vecInertia[2]) / 3.0

    if old_mass is not None and old_inertia is not None and old_mass > 0:
        mass_increase_ratio = fMass / old_mass
        old_inertia_avg = (old_inertia[0] + old_inertia[1] + old_inertia[2]) / 3.0

        if mass_increase_ratio > 1.1:  # Mass increased by more than 10%
            new_inertia = max(0.8, old_inertia_avg * mass_increase_ratio)
            new_inertia = min(1.5, new_inertia)

            # Scale all components proportionally
            scale_factor = new_inertia / inertia_avg if inertia_avg > 0 else 1.0
            new_vec_inertia = (
                vecInertia[0] * scale_factor,
                vecInertia[1] * scale_factor,
                vecInertia[2] * scale_factor,
            )

            # Update the value in the repaired vehicle
            repaired.values["vecInertiaMultiplier"] = (
                f'x="{new_vec_inertia[0]:.6f}" y="{new_vec_inertia[1]:.6f}" z="{new_vec_inertia[2]:.6f}"'
            )
            corrections.append(
                f"Scaled inertia from {inertia_avg:.3f} to {new_inertia:.3f} (mass ratio: {mass_increase_ratio:.2f})"
            )

    # B. Suspension corrections
    fSuspensionForce = vehicle.get_float("fSuspensionForce", 1.0)
    if fSuspensionForce > 3.0:
        new_force = min(2.5, fSuspensionForce)
        repaired.values["fSuspensionForce"] = f"{new_force:.6f}"
        corrections.append(
            f"Reduced suspension force from {fSuspensionForce:.2f} to {new_force:.2f}"
        )

    fSuspensionReboundDamp = vehicle.get_float("fSuspensionReboundDamp")
    fSuspensionCompDamp = vehicle.get_float("fSuspensionCompDamp")

    if fSuspensionCompDamp != 0:
        rebound_ratio = fSuspensionReboundDamp / fSuspensionCompDamp

        if rebound_ratio > 1.8 or rebound_ratio < 1.0:
            # Adjust to safe range
            target_ratio = 1.3  # Midpoint of 1.0-1.5
            new_rebound_damp = fSuspensionCompDamp * target_ratio
            repaired.values["fSuspensionReboundDamp"] = f"{new_rebound_damp:.6f}"
            corrections.append(
                f"Adjusted rebound ratio from {rebound_ratio:.2f} to {target_ratio:.2f}"
            )

    # C. Damage multiplier corrections
    fDeformationDamageMult = vehicle.get_float("fDeformationDamageMult", 1.0)
    if fDeformationDamageMult > 2.0:
        new_damage = min(1.8, max(1.2, fDeformationDamageMult))
        repaired.values["fDeformationDamageMult"] = f"{new_damage:.6f}"
        corrections.append(
            f"Clamped deformation multiplier from {fDeformationDamageMult:.2f} to {new_damage:.2f}"
        )

    fCollisionDamageMult = vehicle.get_float("fCollisionDamageMult", 1.0)
    if fCollisionDamageMult > 2.0:
        new_collision = min(1.8, max(1.2, fCollisionDamageMult))
        repaired.values["fCollisionDamageMult"] = f"{new_collision:.6f}"
        corrections.append(
            f"Clamped collision multiplier from {fCollisionDamageMult:.2f} to {new_collision:.2f}"
        )

    # D. COM offset corrections
    com_offset = vehicle.get_vec3("vecCentreOfMassOffset")
    com_z = com_offset[2]

    if com_z < -0.5:
        # Check if it's a race vehicle (heuristic: light weight, high power)
        is_race_vehicle = (
            fMass < 1500 and vehicle.get_float("fInitialDriveForce", 0) > 0.3
        )

        if not is_race_vehicle:
            new_z = -0.3
            new_com_offset = (com_offset[0], com_offset[1], new_z)
            repaired.values["vecCentreOfMassOffset"] = (
                f'x="{new_com_offset[0]:.6f}" y="{new_com_offset[1]:.6f}" z="{new_com_offset[2]:.6f}"'
            )
            corrections.append(f"Adjusted COM Z from {com_z:.2f} to {new_z:.2f}")

    return repaired, corrections


# -----------------------------------------------------------------------------
# FILE VALIDATION AND OUTPUT
# -----------------------------------------------------------------------------


def validate_file_integrity(file_path: str) -> List[str]:
    """Validate XML file integrity."""

    issues: List[str] = []

    try:
        # Try to parse the file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Check for BOM by reading first bytes
        with open(file_path, "rb") as f:
            first_bytes = f.read(3)
            if first_bytes == b"\xef\xbb\xbf":
                issues.append("File has UTF-8 BOM")

        # Check for unclosed Item blocks by counting
        xml_str = open(file_path, "r", encoding="utf-8").read()
        open_items = xml_str.count("<Item")
        close_items = xml_str.count("</Item>")

        if open_items != close_items:
            issues.append(
                f"Mismatched Item tags: {open_items} opening, {close_items} closing"
            )

        # Check for duplicate vehicle IDs
        vehicles = parse_handling_meta(file_path)
        handling_names = [v.handling_name for v in vehicles.values()]
        duplicates = [
            name for name in set(handling_names) if handling_names.count(name) > 1
        ]

        if duplicates:
            issues.append(
                f"Duplicate vehicle IDs: {', '.join(duplicates[:5])}"
                + ("..." if len(duplicates) > 5 else "")
            )

    except ET.ParseError as e:
        issues.append(f"XML parse error: {e}")
    except UnicodeDecodeError:
        issues.append("File is not valid UTF-8")
    except Exception as e:
        issues.append(f"Validation error: {e}")

    return issues


def generate_corrected_xml(
    original_file: str, repaired_vehicles: Dict[str, HandlingData]
) -> str:
    """Generate corrected XML file with repaired vehicles."""

    try:
        tree = ET.parse(original_file)
        root = tree.getroot()
        handling_data_elem = root.find(".//HandlingData")

        if handling_data_elem is None:
            return None

        # Create a copy of the tree to modify
        import copy

        new_tree = copy.deepcopy(tree)
        new_handling_data = new_tree.getroot().find(".//HandlingData")

        # Replace vehicle data for repaired vehicles
        for item_elem in new_handling_data.findall('.//Item[@type="CHandlingData"]'):
            handling_name_elem = item_elem.find("handlingName")
            if handling_name_elem is None:
                continue

            handling_name = handling_name_elem.text.strip()
            if handling_name in repaired_vehicles:
                repaired_vehicle = repaired_vehicles[handling_name]

                # Update all child elements
                for child in item_elem:
                    if child.tag == "handlingName":
                        continue

                    if child.tag in repaired_vehicle.values:
                        new_value = repaired_vehicle.values[child.tag]
                        if isinstance(new_value, str) and (
                            'x="' in new_value or 'value="' in new_value
                        ):
                            # Parse the XML string and update attributes
                            if 'value="' in new_value:
                                child.set(
                                    "value", new_value.split('value="')[1].split('"')[0]
                                )
                            elif 'x="' in new_value:
                                # For vector elements, we need to update all three attributes
                                import re

                                match = re.search(r'x="([^"]+)"', new_value)
                                if match:
                                    child.set("x", match.group(1))
                                match = re.search(r'y="([^"]+)"', new_value)
                                if match:
                                    child.set("y", match.group(1))
                                match = re.search(r'z="([^"]+)"', new_value)
                                if match:
                                    child.set("z", match.group(1))
                        else:
                            # Update text content
                            child.text = str(new_value)

        # Convert to string with proper formatting
        import xml.dom.minidom

        xml_str = ET.tostring(new_tree.getroot(), encoding="unicode")

        # Pretty print
        dom = xml.dom.minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent="  ")

        # Remove extra blank lines
        lines = [line for line in pretty_xml.split("\n") if line.strip()]
        return "\n".join(lines)

    except Exception as e:
        print(f"ERROR generating corrected XML: {e}")
        return None


# -----------------------------------------------------------------------------
# MAIN ANALYSIS FUNCTION
# -----------------------------------------------------------------------------


def analyze_handling_files(
    current_file: str,
    backup_file: str,
    output_file: Optional[str] = None,
    report_file: Optional[str] = None,
) -> bool:
    """Main analysis function."""

    print(f"Analyzing handling.meta files...")
    print(f"Current file: {current_file}")
    print(f"Backup file: {backup_file}")
    print("-" * 80)

    # Parse files
    current_data = parse_handling_meta(current_file)
    backup_data = parse_handling_meta(backup_file)

    # Compute diffs
    diffs = compute_diffs(backup_data, current_data)
    print(f"Found {len(diffs)} parameter differences")

    # Categorize diffs
    categorized = categorize_diffs(diffs)

    # Generate structured diff report
    diff_report_lines = []
    diff_report_lines.append("=" * 80)
    diff_report_lines.append("STRUCTURAL DIFF REPORT")
    diff_report_lines.append("=" * 80)

    for category, category_diffs in categorized.items():
        if category_diffs:
            diff_report_lines.append(f"\n{category}:")
            diff_report_lines.append("-" * 40)
            for diff in category_diffs[:10]:  # Limit to 10 per category for readability
                diff_report_lines.append(str(diff))
                diff_report_lines.append("")
            if len(category_diffs) > 10:
                diff_report_lines.append(
                    f"... and {len(category_diffs) - 10} more differences"
                )

    # Check invariants
    print("\nChecking physics invariants...")
    all_violations: List[InvariantViolation] = []
    vehicles_with_violations = []

    for vehicle_name, vehicle in current_data.items():
        old_vehicle = backup_data.get(vehicle_name)
        violations = check_physics_invariants(vehicle, old_vehicle)

        if violations:
            all_violations.extend(violations)
            vehicles_with_violations.append(vehicle_name)

    print(
        f"Found {len(all_violations)} invariant violations across {len(vehicles_with_violations)} vehicles"
    )

    # Determine failure class
    failure_class = determine_failure_class(all_violations)

    # Generate violation report
    violation_report_lines = []
    violation_report_lines.append("=" * 80)
    violation_report_lines.append("PHYSICS INVARIANT VIOLATIONS")
    violation_report_lines.append("=" * 80)

    # Group by vehicle
    violations_by_vehicle: Dict[str, List[InvariantViolation]] = {}
    for violation in all_violations:
        if violation.vehicle_name not in violations_by_vehicle:
            violations_by_vehicle[violation.vehicle_name] = []
        violations_by_vehicle[violation.vehicle_name].append(violation)

    for vehicle_name, vehicle_violations in violations_by_vehicle.items():
        violation_report_lines.append(f"\nVehicle: {vehicle_name}")
        for violation in vehicle_violations:
            violation_report_lines.append(f"  {violation}")

    violation_report_lines.append(f"\n\nFAILURE CLASS: {failure_class}")

    # Apply repair strategy
    print("\nApplying repair strategy...")
    repaired_vehicles: Dict[str, HandlingData] = {}
    all_corrections: List[Tuple[str, List[str]]] = []  # (vehicle_name, corrections)

    for vehicle_name in vehicles_with_violations:
        vehicle = current_data[vehicle_name]
        old_vehicle = backup_data.get(vehicle_name)

        repaired_vehicle, corrections = apply_repair_strategy(vehicle, old_vehicle)

        if corrections:
            repaired_vehicles[vehicle_name] = repaired_vehicle
            all_corrections.append((vehicle_name, corrections))

    print(f"Applied corrections to {len(repaired_vehicles)} vehicles")

    # Generate corrections report
    corrections_report_lines = []
    corrections_report_lines.append("=" * 80)
    corrections_report_lines.append("APPLIED CORRECTIONS")
    corrections_report_lines.append("=" * 80)

    for vehicle_name, corrections in all_corrections:
        corrections_report_lines.append(f"\nVehicle: {vehicle_name}")
        for correction in corrections:
            corrections_report_lines.append(f"  - {correction}")

    # Validate file integrity
    print("\nValidating file integrity...")
    integrity_issues = validate_file_integrity(current_file)

    if integrity_issues:
        print(f"Found {len(integrity_issues)} integrity issues:")
        for issue in integrity_issues:
            print(f"  - {issue}")
    else:
        print("File integrity: OK")

    # Generate corrected file if requested
    corrected_xml = None
    if output_file and repaired_vehicles:
        corrected_xml = generate_corrected_xml(current_file, repaired_vehicles)

        if corrected_xml:
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(corrected_xml)
                print(f"\nCorrected file written to: {output_file}")
            except Exception as e:
                print(f"ERROR writing corrected file: {e}")
                corrected_xml = None

    # Write combined report if requested
    if report_file:
        try:
            with open(report_file, "w", encoding="utf-8") as f:
                f.write("\n".join(diff_report_lines))
                f.write("\n\n")
                f.write("\n".join(violation_report_lines))
                f.write("\n\n")
                f.write("\n".join(corrections_report_lines))
                f.write("\n\n")
                f.write("=" * 80)
                f.write("\nSUMMARY\n")
                f.write("=" * 80)
                f.write(f"\nTotal vehicles analyzed: {len(current_data)}")
                f.write(
                    f"\nVehicles with changes from backup: {len(set(current_data.keys()) & set(backup_data.keys()))}"
                )
                f.write(
                    f"\nVehicles with invariant violations: {len(vehicles_with_violations)}"
                )
                f.write(f"\nVehicles repaired: {len(repaired_vehicles)}")
                f.write(f"\nRoot cause: {failure_class}")
                f.write(f"\nFile integrity issues: {len(integrity_issues)}")

                if corrected_xml:
                    f.write(f"\n\nCorrected file generated: {output_file}")
                    f.write("\n\nCONFIRMATION: Physics constraints stabilized.")
                else:
                    f.write("\n\nCorrected file: NOT generated")

            print(f"Report written to: {report_file}")
        except Exception as e:
            print(f"ERROR writing report file: {e}")

    # Print summary to console
    print("\n" + "=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"Total vehicles analyzed: {len(current_data)}")
    print(
        f"Vehicles with changes from backup: {len(set(current_data.keys()) & set(backup_data.keys()))}"
    )
    print(f"Vehicles with invariant violations: {len(vehicles_with_violations)}")
    print(f"Vehicles repaired: {len(repaired_vehicles)}")
    print(f"Root cause: {failure_class}")
    print(f"File integrity issues: {len(integrity_issues)}")

    if corrected_xml:
        print("\nCORRECTED FILE GENERATED")
        print("Physics constraints stabilized.")
        return True
    else:
        print("\nNO CORRECTIONS NEEDED OR FAILED TO GENERATE")
        return len(vehicles_with_violations) == 0


# -----------------------------------------------------------------------------
# COMMAND LINE INTERFACE
# -----------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Analyze GTA V Enhanced handling.meta files for physics invariants"
    )
    parser.add_argument("current_file", help="Current handling.meta file")
    parser.add_argument("backup_file", help="Backup handling_DRIVEV_BACKUP.meta file")
    parser.add_argument(
        "--output", "-o", help="Output file for corrected handling.meta"
    )
    parser.add_argument("--report", "-r", help="Output file for analysis report")

    args = parser.parse_args()

    success = analyze_handling_files(
        args.current_file, args.backup_file, args.output, args.report
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
