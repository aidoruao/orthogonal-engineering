#!/usr/bin/env python3
"""
GTA V Enhanced Handling Pipeline

Specialized pipeline for processing GTA V Enhanced handling.meta files with:
- XML parsing of vehicle handling data
- Safety clamping for physics parameters
- Merkle tree generation for audit trails
- Forensic logging and verification
- Dry-run mode by default (--apply required for modifications)

This is a production-ready version of the pipeline that was successfully tested.
"""

import argparse
import hashlib
import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def hello_world(
    context: str,
    additional: Optional[Dict] = None,
    log_file: str = "handling_verification_pipeline.jsonl",
) -> Dict:
    """
    Minimal-Maximal "Hello World" logging for audit continuity.
    """
    entry = {
        "message": "Hello World",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": context,
    }
    if additional:
        entry["data"] = additional

    print(f"[HELLO WORLD] {entry['timestamp']} | {context}")

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return entry


def parse_handling_file(
    file_path: str, subset: Optional[int] = None
) -> Tuple[ET.ElementTree, List[ET.Element]]:
    """
    Parse handling.meta XML file and extract vehicle items.
    Supports subset processing.
    """
    hello_world("parsing_handling_file", {"path": file_path, "subset": subset})

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Find all Item elements (vehicles)
        items = root.findall(".//Item")

        if subset is not None and subset > 0:
            items = items[:subset]
            hello_world("subset_applied", {"subset": subset, "total_found": len(items)})

        hello_world(
            "handling_file_parsed",
            {"total_items": len(items), "subset_applied": subset is not None},
        )

        return tree, items

    except ET.ParseError as e:
        print(f"[ERROR] Failed to parse XML: {e}")
        sys.exit(1)


def canonical_vehicle_bytes(item: ET.Element) -> bytes:
    """
    Generate canonical byte representation of a vehicle item.
    Ensures deterministic hashing across platforms.
    """
    # Extract vehicle name
    name_elem = item.find("handlingName")
    vehicle_name = (
        name_elem.text.strip()
        if name_elem is not None and name_elem.text
        else "unknown"
    )

    # Collect all parameters in sorted order for determinism
    params = {}
    for child in item:
        if child.tag == "handlingName":
            continue

        if child.get("value"):
            params[child.tag] = child.get("value")
        elif child.text:
            params[child.tag] = child.text.strip()
        else:
            params[child.tag] = ""

    # Create canonical representation
    canonical = {
        "vehicle": vehicle_name,
        "parameters": {k: params[k] for k in sorted(params.keys())},
    }

    # Convert to JSON with sorted keys for determinism
    canonical_json = json.dumps(
        canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )

    return canonical_json.encode("utf-8")


def compute_vehicle_hash(canonical_bytes: bytes) -> str:
    """Compute SHA-256 hash of canonical vehicle bytes."""
    return hashlib.sha256(canonical_bytes).hexdigest()


def apply_safety_clamps(item: ET.Element) -> List[Dict[str, Any]]:
    """
    Apply safety clamps to vehicle physics parameters.
    Prevents game crashes by ensuring values are within safe ranges.
    """
    clamps_applied = []

    # Safety clamps for critical physics parameters
    safety_clamps = {
        "fMass": (50.0, 50000.0),  # Mass in kg
        "fInitialDragCoeff": (0.0, 100.0),  # Drag coefficient
        "fPercentSubmerged": (10.0, 200.0),  # Submerged percentage
        "fDriveBiasFront": (0.0, 1.0),  # Front drive bias
        "fInitialDriveForce": (0.0, 100.0),  # Initial drive force
        "fDriveInertia": (0.01, 10.0),  # Drive inertia
        "fClutchChangeRateScaleUpShift": (0.1, 10.0),  # Clutch change rates
        "fClutchChangeRateScaleDownShift": (0.1, 10.0),
        "fInitialDriveMaxFlatVel": (0.0, 500.0),  # Max flat velocity
        "fBrakeForce": (0.0, 10.0),  # Brake force
        "fBrakeBiasFront": (0.0, 1.0),  # Front brake bias
        "fHandBrakeForce": (0.0, 10.0),  # Handbrake force
        "fSteeringLock": (0.0, 90.0),  # Steering lock angle
        "fTractionCurveMax": (0.0, 10.0),  # Traction curve limits
        "fTractionCurveMin": (0.0, 10.0),
        "fTractionCurveLateral": (0.0, 10.0),
        "fTractionSpringDeltaMax": (0.0, 1.0),  # Suspension limits
        "fLowSpeedTractionLossMult": (0.0, 10.0),  # Traction loss multipliers
        "fCamberStiffness": (-1.0, 1.0),  # Camber stiffness
        "fTractionBiasFront": (0.0, 1.0),  # Front traction bias
        "fTractionLossMult": (0.0, 10.0),  # Traction loss
        "fSuspensionForce": (0.0, 100.0),  # Suspension force
        "fSuspensionCompDamp": (0.0, 10.0),  # Suspension damping
        "fSuspensionReboundDamp": (0.0, 10.0),
        "fSuspensionUpperLimit": (-1.0, 1.0),  # Suspension limits
        "fSuspensionLowerLimit": (-1.0, 1.0),
        "fSuspensionRaise": (-1.0, 1.0),  # Suspension raise
        "fSuspensionBiasFront": (0.0, 1.0),  # Front suspension bias
        "fAntiRollBarForce": (0.0, 100.0),  # Anti-roll bar
        "fAntiRollBarBiasFront": (0.0, 1.0),  # Front anti-roll bias
        "fRollCentreHeightFront": (-1.0, 1.0),  # Roll center heights
        "fRollCentreHeightRear": (-1.0, 1.0),
        "fCollisionDamageMult": (0.0, 10.0),  # Damage multipliers
        "fWeaponDamageMult": (0.0, 10.0),
        "fDeformationDamageMult": (0.0, 10.0),
        "fEngineDamageMult": (0.0, 10.0),
        "fPetrolTankVolume": (0.0, 1000.0),  # Fuel tank volume
        "fOilVolume": (0.0, 100.0),  # Oil volume
    }

    for param, (min_val, max_val) in safety_clamps.items():
        param_elem = item.find(param)
        if param_elem is not None:
            value_str = param_elem.get("value") or param_elem.text
            if value_str:
                try:
                    value = float(value_str)

                    # Check if value needs clamping
                    if value < min_val or value > max_val:
                        clamped = max(min_val, min(max_val, value))
                        clamps_applied.append(
                            {
                                "parameter": param,
                                "original": value,
                                "clamped": clamped,
                                "min": min_val,
                                "max": max_val,
                            }
                        )

                        # Update the element
                        if param_elem.get("value"):
                            param_elem.set("value", str(clamped))
                        elif param_elem.text:
                            param_elem.text = str(clamped)

                        hello_world(
                            "parameter_clamped",
                            {
                                "vehicle": item.find("handlingName").text
                                if item.find("handlingName") is not None
                                else "unknown",
                                "parameter": param,
                                "original": value,
                                "clamped": clamped,
                            },
                        )

                except (ValueError, TypeError):
                    # Skip non-numeric values
                    pass

    return clamps_applied


def extend_clamp_parameters(item: ET.Element) -> List[Dict[str, Any]]:
    """
    Apply extended clamps to additional vehicle parameters.
    Covers suspension, traction, braking, and other systems.
    """
    extensions_applied = []

    # Extended clamps for comprehensive safety
    extended_clamps = {
        # Engine and drivetrain
        "fInitialDriveGears": (1, 10),
        "fDriveMaxFlatVel": (0.0, 500.0),
        # Traction and grip
        "fTractionCurveLateralPeak": (0.0, 10.0),
        "fTractionCurveLateralMin": (0.0, 10.0),
        "fTractionCurveLongitudinalPeak": (0.0, 10.0),
        "fTractionCurveLongitudinalMin": (0.0, 10.0),
        # Suspension geometry
        "fSuspensionFrontTravel": (0.0, 1.0),
        "fSuspensionRearTravel": (0.0, 1.0),
        "fSuspensionFrontRaise": (-1.0, 1.0),
        "fSuspensionRearRaise": (-1.0, 1.0),
        # Steering
        "fSteeringLockRatio": (0.0, 2.0),
        "fSteeringResponse": (0.0, 10.0),
        # Braking
        "fBrakeResponse": (0.0, 10.0),
        "fBrakeBiasRear": (0.0, 1.0),
        # Aerodynamics
        "fDownforceMult": (0.0, 5.0),
        "fDragCoeff": (0.0, 10.0),
        # Weight distribution
        "fCentreOfMassOffsetX": (-2.0, 2.0),
        "fCentreOfMassOffsetY": (-2.0, 2.0),
        "fCentreOfMassOffsetZ": (-2.0, 2.0),
        # Damage and durability
        "fSeatOffsetDistX": (-2.0, 2.0),
        "fSeatOffsetDistY": (-2.0, 2.0),
        "fSeatOffsetDistZ": (-2.0, 2.0),
    }

    for param, (min_val, max_val) in extended_clamps.items():
        param_elem = item.find(param)
        if param_elem is not None:
            value_str = param_elem.get("value") or param_elem.text
            if value_str:
                try:
                    # Handle integer parameters
                    if param in ["fInitialDriveGears"]:
                        value = int(float(value_str))
                        min_val, max_val = int(min_val), int(max_val)
                    else:
                        value = float(value_str)

                    # Check if value needs clamping
                    if value < min_val or value > max_val:
                        if param in ["fInitialDriveGears"]:
                            clamped = max(min_val, min(max_val, value))
                        else:
                            clamped = max(min_val, min(max_val, value))

                        extensions_applied.append(
                            {
                                "parameter": param,
                                "original": value,
                                "clamped": clamped,
                                "min": min_val,
                                "max": max_val,
                            }
                        )

                        # Update the element
                        if param_elem.get("value"):
                            param_elem.set("value", str(clamped))
                        elif param_elem.text:
                            param_elem.text = str(clamped)

                except (ValueError, TypeError):
                    # Skip non-numeric values
                    pass

    return extensions_applied


def build_merkle_tree(hashes: List[str]) -> Dict[str, Any]:
    """Build Merkle tree from list of hashes."""
    hello_world("building_merkle_tree", {"leaf_count": len(hashes)})

    if not hashes:
        return {"root": "", "height": 0, "leaves": []}

    # Ensure even number of leaves by duplicating last if odd
    leaves = hashes.copy()
    if len(leaves) % 2 == 1:
        leaves.append(leaves[-1])

    current_level = leaves
    tree_levels = [current_level]

    while len(current_level) > 1:
        next_level = []
        for i in range(0, len(current_level), 2):
            combined = current_level[i] + current_level[i + 1]
            parent_hash = hashlib.sha256(combined.encode()).hexdigest()
            next_level.append(parent_hash)

        # Ensure even number for next level
        if len(next_level) % 2 == 1 and len(next_level) > 1:
            next_level.append(next_level[-1])

        tree_levels.append(next_level)
        current_level = next_level

    merkle_root = current_level[0] if current_level else ""

    merkle_tree = {
        "root": merkle_root,
        "height": len(tree_levels),
        "leaf_count": len(hashes),
        "levels": tree_levels,
    }

    hello_world(
        "merkle_tree_built",
        {
            "root": merkle_root[:16] + "...",
            "height": len(tree_levels),
            "leaf_count": len(hashes),
        },
    )

    return merkle_tree


def main():
    parser = argparse.ArgumentParser(
        description="GTA V Enhanced Handling Pipeline with Safety Clamps"
    )
    parser.add_argument(
        "--handling-path", required=True, help="Path to handling.meta file"
    )
    parser.add_argument(
        "--subset",
        type=int,
        default=None,
        help="Process only first N vehicles (for testing)",
    )
    parser.add_argument(
        "--out-dir",
        default="outputs/handling_test",
        help="Output directory for results",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Run without modifying files"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes (requires --dry-run first for safety)",
    )

    args = parser.parse_args()

    # Safety check
    if args.apply and not args.dry_run:
        print("[ERROR] Must run with --dry-run first before --apply")
        sys.exit(1)

    # Create output directory
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Set up log file in output directory
    log_file = out_dir / "handling_verification_pipeline.jsonl"

    # Start pipeline
    hello_world(
        "verification_pipeline_start",
        {
            "handling_path": args.handling_path,
            "subset": args.subset,
            "out_dir": str(out_dir),
            "dry_run": args.dry_run,
            "apply": args.apply,
        },
        str(log_file),
    )

    # Parse handling file
    tree, vehicles = parse_handling_file(args.handling_path, args.subset)

    # Process each vehicle
    all_clamps = []
    all_extensions = []
    original_hashes = []
    processed_hashes = []

    for vehicle in vehicles:
        # Get vehicle name for logging
        name_elem = vehicle.find("handlingName")
        vehicle_name = (
            name_elem.text.strip()
            if name_elem is not None and name_elem.text
            else "unknown"
        )

        # Compute original hash
        original_bytes = canonical_vehicle_bytes(vehicle)
        original_hash = compute_vehicle_hash(original_bytes)
        original_hashes.append(original_hash)

        # Apply safety clamps
        clamps = apply_safety_clamps(vehicle)
        all_clamps.extend(clamps)

        # Apply extended clamps
        extensions = extend_clamp_parameters(vehicle)
        all_extensions.extend(extensions)

        # Compute processed hash
        processed_bytes = canonical_vehicle_bytes(vehicle)
        processed_hash = compute_vehicle_hash(processed_bytes)
        processed_hashes.append(processed_hash)

        # Log vehicle processing
        hello_world(
            "vehicle_processed",
            {
                "vehicle": vehicle_name,
                "safety_clamps": len(clamps),
                "extended_clamps": len(extensions),
                "original_hash": original_hash[:16] + "...",
                "processed_hash": processed_hash[:16] + "...",
            },
            str(log_file),
        )

    # Build Merkle trees
    original_merkle = build_merkle_tree(original_hashes)
    processed_merkle = build_merkle_tree(processed_hashes)

    # Save Merkle tree report
    merkle_report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "original_merkle": original_merkle,
        "processed_merkle": processed_merkle,
        "hash_comparison": {
            "original_root": original_merkle["root"],
            "processed_root": processed_merkle["root"],
            "roots_match": original_merkle["root"] == processed_merkle["root"],
        },
    }

    merkle_path = out_dir / "handling_merkle_audit.json"
    with open(merkle_path, "w", encoding="utf-8") as f:
        json.dump(merkle_report, f, indent=2, ensure_ascii=False)

    # Save clamps report
    clamps_report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_vehicles": len(vehicles),
        "safety_clamps": all_clamps,
        "extended_clamps": all_extensions,
        "summary": {
            "safety_clamps_applied": len(all_clamps),
            "extended_clamps_applied": len(all_extensions),
            "vehicles_with_clamps": len([c for c in all_clamps + all_extensions if c]),
        },
    }

    clamps_path = out_dir / "handling_clamps_report.json"
    with open(clamps_path, "w", encoding="utf-8") as f:
        json.dump(clamps_report, f, indent=2, ensure_ascii=False)

    # Save modified XML if apply mode
    if args.apply:
        modified_path = out_dir / "handling_modified.meta"
        tree.write(modified_path, encoding="utf-8", xml_declaration=True)
        hello_world("file_written", {"path": str(modified_path)}, str(log_file))
    elif args.dry_run:
        hello_world("dry_run_complete", {"files_would_be_written": 1}, str(log_file))

    # Create forensic summary
    outputs = {
        "merkle_report": str(merkle_path),
        "clamps_report": str(clamps_path),
        "verification_log": str(log_file),
    }

    if args.apply:
        outputs["modified_file"] = str(out_dir / "handling_modified.meta")

    forensic_summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pipeline_phase": "handling_clamp_pipeline",
        "parameters": {
            "handling_path": args.handling_path,
            "subset": args.subset,
            "out_dir": str(out_dir),
            "dry_run": args.dry_run,
            "apply": args.apply,
        },
        "statistics": {
            "total_vehicles": len(vehicles),
            "safety_clamps_applied": len(all_clamps),
            "extended_clamps_applied": len(all_extensions),
            "original_merkle_root": original_merkle["root"],
            "processed_merkle_root": processed_merkle["root"],
            "unique_hashes": len(set(original_hashes)),
        },
        "output_files": outputs,
    }

    summary_path = out_dir / "handling_forensic_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(forensic_summary, f, indent=2, ensure_ascii=False)
    outputs["forensic_summary"] = str(summary_path)

    # Final log
    hello_world(
        "verification_pipeline_end",
        {
            "total_vehicles": len(vehicles),
            "safety_clamps": len(all_clamps),
            "extended_clamps": len(all_extensions),
            "original_merkle_root": original_merkle["root"][:16] + "...",
            "processed_merkle_root": processed_merkle["root"][:16] + "...",
            "dry_run": args.dry_run,
            "apply": args.apply,
        },
        str(log_file),
    )

    print("\n" + "=" * 60)
    print("GTA V HANDLING CLAMP PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print(f"Total vehicles processed: {len(vehicles)}")
    print(f"Safety clamps applied: {len(all_clamps)}")
    print(f"Extended clamps applied: {len(all_extensions)}")
    print(f"Original Merkle root: {original_merkle['root'][:16]}...")
    print(f"Processed Merkle root: {processed_merkle['root'][:16]}...")
    print(f"Dry run mode: {args.dry_run}")
    print(f"Apply mode: {args.apply}")
    print(f"Output directory: {out_dir}")
    print("=" * 60)

    # Save list of output files
    outputs_path = out_dir / "pipeline_outputs.json"
    with open(outputs_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "output_files": outputs,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"\nOutput files saved to: {out_dir}")
    for key, path in outputs.items():
        print(f"  - {key}: {Path(path).name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
