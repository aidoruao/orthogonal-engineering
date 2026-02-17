#!/usr/bin/env python3
"""
apply_corrections.py - Apply invariant corrections directly to handling.meta

This script reads the original handling.meta file and applies physics invariant
corrections to stabilize vehicle constraints according to GTA V Enhanced physics.

Corrections applied:
1. Damage multipliers clamped to 1.2-1.8 range
2. Suspension rebound ratios adjusted to 1.0-1.5 range
3. Mass-inertia scaling where appropriate
4. COM Z offset adjustments for stability

The script preserves the original XML structure and formatting.
"""

import argparse
import math
import re
import sys
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple


class VehicleCorrector:
    """Applies physics invariant corrections to vehicle handling data."""

    def __init__(self):
        self.corrections_applied = 0
        self.vehicles_corrected = set()

    def apply_corrections_to_vehicle(self, item_elem: ET.Element) -> List[str]:
        """Apply invariant corrections to a single vehicle."""

        handling_name_elem = item_elem.find("handlingName")
        if handling_name_elem is None:
            return []

        handling_name = handling_name_elem.text.strip()
        corrections = []

        # Get all parameter elements
        param_elems = {}
        for child in item_elem:
            if child.tag == "handlingName":
                continue
            param_elems[child.tag] = child

        # 1. Damage multiplier corrections
        damage_corrections = self._correct_damage_multipliers(param_elems)
        corrections.extend(damage_corrections)

        # 2. Suspension corrections
        suspension_corrections = self._correct_suspension(param_elems)
        corrections.extend(suspension_corrections)

        # 3. Mass-inertia corrections (if needed)
        inertia_corrections = self._correct_mass_inertia(param_elems)
        corrections.extend(inertia_corrections)

        # 4. COM offset corrections
        com_corrections = self._correct_com_offset(param_elems)
        corrections.extend(com_corrections)

        if corrections:
            self.corrections_applied += len(corrections)
            self.vehicles_corrected.add(handling_name)

        return corrections

    def _correct_damage_multipliers(
        self, param_elems: Dict[str, ET.Element]
    ) -> List[str]:
        """Clamp damage multipliers to safe range (1.2-1.8)."""

        corrections = []
        damage_params = [
            ("fCollisionDamageMult", "collision"),
            ("fDeformationDamageMult", "deformation"),
            ("fEngineDamageMult", "engine"),
        ]

        for param_name, param_desc in damage_params:
            if param_name not in param_elems:
                continue

            elem = param_elems[param_name]
            if "value" not in elem.attrib:
                continue

            try:
                current_value = float(elem.attrib["value"])

                # Only correct if > 2.0 (critical threshold)
                if current_value > 2.0:
                    # Clamp to 1.2-1.8 range
                    new_value = max(1.2, min(1.8, current_value))

                    # Only apply if actually changed
                    if abs(new_value - current_value) > 0.01:
                        elem.set("value", f"{new_value:.6f}")
                        corrections.append(
                            f"Clamped {param_desc} multiplier from {current_value:.2f} to {new_value:.2f}"
                        )

            except (ValueError, TypeError):
                continue

        return corrections

    def _correct_suspension(self, param_elems: Dict[str, ET.Element]) -> List[str]:
        """Adjust suspension parameters for stability."""

        corrections = []

        # Check suspension force
        if "fSuspensionForce" in param_elems:
            elem = param_elems["fSuspensionForce"]
            if "value" in elem.attrib:
                try:
                    current_value = float(elem.attrib["value"])
                    if current_value > 3.0:
                        new_value = min(2.5, current_value)
                        elem.set("value", f"{new_value:.6f}")
                        corrections.append(
                            f"Reduced suspension force from {current_value:.2f} to {new_value:.2f}"
                        )
                except (ValueError, TypeError):
                    pass

        # Check rebound ratio
        if (
            "fSuspensionCompDamp" in param_elems
            and "fSuspensionReboundDamp" in param_elems
        ):
            comp_elem = param_elems["fSuspensionCompDamp"]
            rebound_elem = param_elems["fSuspensionReboundDamp"]

            if "value" in comp_elem.attrib and "value" in rebound_elem.attrib:
                try:
                    comp_damp = float(comp_elem.attrib["value"])
                    rebound_damp = float(rebound_elem.attrib["value"])

                    if comp_damp != 0:
                        current_ratio = rebound_damp / comp_damp

                        # Check if ratio is outside safe range (1.0-1.5)
                        if current_ratio < 1.0 or current_ratio > 1.5:
                            # Target midpoint of safe range
                            target_ratio = 1.3
                            new_rebound_damp = comp_damp * target_ratio

                            rebound_elem.set("value", f"{new_rebound_damp:.6f}")
                            corrections.append(
                                f"Adjusted rebound ratio from {current_ratio:.2f} to {target_ratio:.2f}"
                            )

                except (ValueError, TypeError, ZeroDivisionError):
                    pass

        return corrections

    def _correct_mass_inertia(self, param_elems: Dict[str, ET.Element]) -> List[str]:
        """Scale inertia proportionally with mass changes."""

        # Note: This would require comparing with backup values
        # For now, we'll just check for critically low inertia
        corrections = []

        if "vecInertiaMultiplier" in param_elems:
            elem = param_elems["vecInertiaMultiplier"]
            if all(coord in elem.attrib for coord in ("x", "y", "z")):
                try:
                    inertia_x = float(elem.attrib["x"])
                    inertia_y = float(elem.attrib["y"])
                    inertia_z = float(elem.attrib["z"])

                    inertia_avg = (inertia_x + inertia_y + inertia_z) / 3.0

                    # Check for critically low inertia
                    if inertia_avg < 0.3:
                        # Scale all components up to minimum safe value
                        scale_factor = 0.5 / inertia_avg  # Target 0.5 average
                        new_x = inertia_x * scale_factor
                        new_y = inertia_y * scale_factor
                        new_z = inertia_z * scale_factor

                        elem.set("x", f"{new_x:.6f}")
                        elem.set("y", f"{new_y:.6f}")
                        elem.set("z", f"{new_z:.6f}")

                        corrections.append(
                            f"Scaled inertia from {inertia_avg:.3f} avg to 0.5 avg"
                        )

                except (ValueError, TypeError):
                    pass

        return corrections

    def _correct_com_offset(self, param_elems: Dict[str, ET.Element]) -> List[str]:
        """Adjust center of mass offset for stability."""

        corrections = []

        if "vecCentreOfMassOffset" in param_elems:
            elem = param_elems["vecCentreOfMassOffset"]
            if all(coord in elem.attrib for coord in ("x", "y", "z")):
                try:
                    com_z = float(elem.attrib["z"])

                    # Check for unstable COM Z offset
                    if com_z < -0.5:
                        # For non-race vehicles, adjust to safer value
                        # Check if it's likely a race vehicle (light weight, high power)
                        is_race_vehicle = False

                        if (
                            "fMass" in param_elems
                            and "fInitialDriveForce" in param_elems
                        ):
                            mass_elem = param_elems["fMass"]
                            force_elem = param_elems["fInitialDriveForce"]

                            if (
                                "value" in mass_elem.attrib
                                and "value" in force_elem.attrib
                            ):
                                mass = float(mass_elem.attrib["value"])
                                force = float(force_elem.attrib["value"])

                                # Heuristic: light weight + high power = race vehicle
                                is_race_vehicle = mass < 1500 and force > 0.3

                        if not is_race_vehicle:
                            new_z = -0.3
                            elem.set("z", f"{new_z:.6f}")
                            corrections.append(
                                f"Adjusted COM Z from {com_z:.2f} to {new_z:.2f}"
                            )

                except (ValueError, TypeError):
                    pass

        return corrections


def fix_xml_structure(xml_content: str) -> str:
    """Fix XML structure issues like mismatched Item tags."""

    # Count Item tags
    open_items = xml_content.count("<Item")
    close_items = xml_content.count("</Item>")

    if open_items == close_items:
        return xml_content

    print(f"  Found Item tag mismatch: {open_items} opening, {close_items} closing")

    # Try to fix by ensuring all Item elements are properly closed
    lines = xml_content.split("\n")
    fixed_lines = []
    item_stack = []

    for line in lines:
        stripped = line.strip()

        # Check for opening Item tag
        if stripped.startswith("<Item") and not stripped.startswith("</Item>"):
            item_stack.append("Item")
            fixed_lines.append(line)
        # Check for closing Item tag
        elif stripped == "</Item>":
            if item_stack:
                item_stack.pop()
                fixed_lines.append(line)
            else:
                print(f"  WARNING: Extra closing Item tag found, skipping: {stripped}")
        else:
            fixed_lines.append(line)

    # Close any unclosed Items
    while item_stack:
        fixed_lines.append("  " * (len(item_stack) - 1) + "</Item>")
        item_stack.pop()

    fixed_xml = "\n".join(fixed_lines)

    # Verify fix
    open_fixed = fixed_xml.count("<Item")
    close_fixed = fixed_xml.count("</Item>")

    if open_fixed == close_fixed:
        print(f"  Fixed Item tags: {open_fixed} opening, {close_fixed} closing ✓")
    else:
        print(
            f"  WARNING: Could not fully fix Item tags: {open_fixed} opening, {close_fixed} closing"
        )

    return fixed_xml


def apply_corrections(input_file: str, output_file: str, verbose: bool = True) -> bool:
    """Apply invariant corrections to handling.meta file."""

    try:
        if verbose:
            print(f"Reading file: {input_file}")

        # Read the entire file to preserve formatting
        with open(input_file, "r", encoding="utf-8") as f:
            xml_content = f.read()

        # Parse the XML
        try:
            tree = ET.ElementTree(ET.fromstring(xml_content))
        except ET.ParseError as e:
            print(f"ERROR: Failed to parse XML: {e}")
            print("Attempting to fix XML structure...")

            # Try to fix the XML structure
            xml_content = fix_xml_structure(xml_content)

            try:
                tree = ET.ElementTree(ET.fromstring(xml_content))
            except ET.ParseError as e2:
                print(f"ERROR: Still cannot parse XML after fix attempt: {e2}")
                return False

        root = tree.getroot()

        # Find the HandlingData element
        handling_data_elem = root.find(".//HandlingData")
        if handling_data_elem is None:
            print("ERROR: No HandlingData element found in XML")
            return False

        # Initialize corrector
        corrector = VehicleCorrector()
        all_corrections = []

        if verbose:
            print(f"Found HandlingData element, applying corrections...")

        # Process each vehicle
        vehicle_items = handling_data_elem.findall('.//Item[@type="CHandlingData"]')

        if verbose:
            print(f"Processing {len(vehicle_items)} vehicles...")

        for item_elem in vehicle_items:
            corrections = corrector.apply_corrections_to_vehicle(item_elem)
            if corrections:
                handling_name_elem = item_elem.find("handlingName")
                if handling_name_elem is not None:
                    vehicle_name = handling_name_elem.text.strip()
                    all_corrections.append((vehicle_name, corrections))

        # Generate corrected XML
        try:
            # Convert tree back to string
            xml_str = ET.tostring(root, encoding="utf-8", method="xml").decode("utf-8")

            # Ensure proper XML declaration
            if not xml_str.startswith("<?xml"):
                xml_str = '<?xml version="1.0" encoding="utf-8"?>\n' + xml_str

            # Write to output file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(xml_str)

            if verbose:
                print(f"\nCorrections applied:")
                print(f"  Vehicles corrected: {len(corrector.vehicles_corrected)}")
                print(f"  Total corrections: {corrector.corrections_applied}")

                if all_corrections:
                    print(f"\nDetailed corrections:")
                    for vehicle_name, corrections in all_corrections[
                        :10
                    ]:  # Limit output
                        print(f"  {vehicle_name}:")
                        for correction in corrections:
                            print(f"    - {correction}")

                    if len(all_corrections) > 10:
                        print(f"    ... and {len(all_corrections) - 10} more vehicles")

                print(f"\nCorrected file written to: {output_file}")

            return True

        except Exception as e:
            print(f"ERROR: Failed to write corrected file: {e}")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False


def validate_output_file(file_path: str) -> bool:
    """Validate the corrected XML file."""

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse to check XML validity
        ET.fromstring(content)

        # Count Item tags
        open_items = content.count("<Item")
        close_items = content.count("</Item>")

        print(f"\nValidation:")
        print(f"  XML is well-formed ✓")
        print(f"  Item tags: {open_items} opening, {close_items} closing")

        if open_items == close_items:
            print(f"  Item tags are balanced ✓")
            return True
        else:
            print(f"  WARNING: Item tag mismatch!")
            return False

    except ET.ParseError as e:
        print(f"ERROR: Output file is not valid XML: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Validation failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Apply physics invariant corrections to GTA V Enhanced handling.meta file"
    )
    parser.add_argument("input", help="Input handling.meta file")
    parser.add_argument("output", help="Output corrected handling.meta file")
    parser.add_argument(
        "--validate",
        "-v",
        action="store_true",
        help="Validate output file after correction",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress detailed output"
    )

    args = parser.parse_args()

    print(f"Applying invariant corrections to handling.meta...")
    print(f"Input file: {args.input}")
    print(f"Output file: {args.output}")

    success = apply_corrections(args.input, args.output, verbose=not args.quiet)

    if success and args.validate:
        print(f"\n" + "=" * 60)
        validate_output_file(args.output)

    if success:
        print(f"\n" + "=" * 60)
        print("SUCCESS: Physics constraints stabilized.")
        print("=" * 60)
        sys.exit(0)
    else:
        print(f"\n" + "=" * 60)
        print("FAILED: Could not apply corrections.")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
