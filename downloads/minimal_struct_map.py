#!/usr/bin/env python3
"""
minimal_struct_map.py — Minimal structural map contingency
Simplified version for DAG fallback scenarios.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def generate_minimal_map():
    """Generate minimal structural map of the repository."""
    print("📁 Generating minimal structural map...")

    # Basic repository structure
    repo_root = Path(".")

    # Core directories to include
    core_dirs = [
        "automation",
        "toolkit/oe",
        "documentation",
        ".rules",
        "logs",
        "downloads",
        "analysis",
        "evidence",
        ".ide_ai_sessions",
    ]

    # Key files to track
    key_files = [
        "AGENT.md",
        "AI_INSTRUCTIONS.md",
        "ONBOARD_FIRST.md",
        "_START_HERE.md",
        "automation/run_full_audit_with_trace.py",
        "automation/run_autofix_integration.py",
        "toolkit/oe/autofix_engine.py",
        "toolkit/oe/boundary_spellcheck.py",
        "toolkit/oe/ide_ai_integration.py",
        "documentation/GLASS_BOX_BOUNDARY_v1.11.html",
        ".rules/ORTHOGONAL_GB_ORIGIN.rules",
    ]

    # Build minimal map
    minimal_map = {
        "map_id": f"MINIMAL-STRUCT-MAP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "generator": "minimal_struct_map.py",
        "purpose": "Contingency structural map for DAG fallback scenarios",
        "repository": {
            "name": "orthogonal-engineering-clean",
            "root": str(repo_root.absolute()),
            "generation_time": datetime.utcnow().isoformat() + "Z",
        },
        "core_directories": {},
        "key_files": {},
        "verification": {
            "status": "minimal_check",
            "completeness": "partial",
            "notes": "This is a minimal map for contingency use only",
        },
    }

    # Check core directories
    print("\nChecking core directories:")
    for dir_path in core_dirs:
        path = Path(dir_path)
        if path.exists():
            # Count files in directory
            try:
                file_count = len(list(path.rglob("*"))) if path.is_dir() else 0
                dir_count = (
                    len([d for d in path.iterdir() if d.is_dir()])
                    if path.is_dir()
                    else 0
                )

                minimal_map["core_directories"][dir_path] = {
                    "exists": True,
                    "is_directory": path.is_dir(),
                    "file_count": file_count,
                    "subdirectory_count": dir_count,
                }
                print(f"  ✓ {dir_path} ({file_count} files, {dir_count} subdirs)")
            except Exception as e:
                minimal_map["core_directories"][dir_path] = {
                    "exists": True,
                    "error": str(e),
                }
                print(f"  ⚠ {dir_path} (error: {str(e)})")
        else:
            minimal_map["core_directories"][dir_path] = {
                "exists": False,
                "is_directory": False,
            }
            print(f"  ✗ {dir_path} (MISSING)")

    # Check key files
    print("\nChecking key files:")
    for file_path in key_files:
        path = Path(file_path)
        if path.exists():
            try:
                file_size = path.stat().st_size
                modified_time = datetime.fromtimestamp(path.stat().st_mtime).isoformat()

                minimal_map["key_files"][file_path] = {
                    "exists": True,
                    "size_bytes": file_size,
                    "size_human": f"{file_size / 1024:.1f} KB",
                    "modified": modified_time,
                    "is_file": path.is_file(),
                }
                print(f"  ✓ {file_path} ({file_size / 1024:.1f} KB)")
            except Exception as e:
                minimal_map["key_files"][file_path] = {
                    "exists": True,
                    "error": str(e),
                }
                print(f"  ⚠ {file_path} (error: {str(e)})")
        else:
            minimal_map["key_files"][file_path] = {
                "exists": False,
                "is_file": False,
            }
            print(f"  ✗ {file_path} (MISSING)")

    # Calculate statistics
    existing_dirs = sum(
        1
        for info in minimal_map["core_directories"].values()
        if info.get("exists", False)
    )
    existing_files = sum(
        1 for info in minimal_map["key_files"].values() if info.get("exists", False)
    )

    minimal_map["statistics"] = {
        "total_core_directories": len(core_dirs),
        "existing_core_directories": existing_dirs,
        "total_key_files": len(key_files),
        "existing_key_files": existing_files,
        "directory_coverage": f"{existing_dirs / len(core_dirs) * 100:.1f}%",
        "file_coverage": f"{existing_files / len(key_files) * 100:.1f}%",
    }

    # Add contingency information
    minimal_map["contingency_info"] = {
        "triggered_by": "DAG fallback scenario",
        "recovery_instructions": [
            "Use this map to understand repository structure",
            "Check missing directories and files",
            "Run full structural map generator when available",
            "Review AGENT.md for system architecture",
        ],
        "next_steps": [
            "Verify critical paths exist",
            "Check automation scripts are executable",
            "Validate boundary enforcement layers",
            "Run light audit if possible",
        ],
    }

    return minimal_map


def save_map(minimal_map, output_dir="downloads"):
    """Save minimal map to files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    # Save as JSON
    json_file = output_path / f"minimal_structural_map_{timestamp}.json"
    with open(json_file, "w") as f:
        json.dump(minimal_map, f, indent=2)

    # Save as YAML if available
    yaml_file = None
    try:
        import yaml

        yaml_file = output_path / f"minimal_structural_map_{timestamp}.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump(minimal_map, f, sort_keys=False)
    except ImportError:
        yaml_file = None

    return json_file, yaml_file


def main():
    """Main entry point for minimal structural map generator."""
    print("=" * 60)
    print("MINIMAL STRUCTURAL MAP GENERATOR")
    print("=" * 60)
    print("Purpose: Contingency map for DAG fallback scenarios")
    print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
    print()

    try:
        # Generate minimal map
        minimal_map = generate_minimal_map()

        # Save map
        json_file, yaml_file = save_map(minimal_map)

        # Print summary
        print(f"\n{'=' * 60}")
        print("MINIMAL STRUCTURAL MAP GENERATION COMPLETE")
        print(f"{'=' * 60}")

        stats = minimal_map["statistics"]
        print(
            f"Core directories: {stats['existing_core_directories']}/{stats['total_core_directories']} ({stats['directory_coverage']})"
        )
        print(
            f"Key files: {stats['existing_key_files']}/{stats['total_key_files']} ({stats['file_coverage']})"
        )

        print(f"\n📄 JSON map saved to: {json_file}")
        if yaml_file:
            print(f"📄 YAML map saved to: {yaml_file}")

        # Show critical status
        critical_dirs = ["automation", "toolkit/oe", "documentation"]
        critical_missing = []

        for dir_path in critical_dirs:
            if not minimal_map["core_directories"][dir_path]["exists"]:
                critical_missing.append(dir_path)

        if critical_missing:
            print(f"\n⚠  CRITICAL WARNING: Missing directories:")
            for missing_dir in critical_missing:
                print(f"   • {missing_dir}")
            print(
                f"\n   Action required: These directories are essential for system operation."
            )

        print(f"\n✅ Minimal structural map generated successfully.")
        print(f"   Use for contingency planning and recovery operations.")
        print(f"{'=' * 60}")

        return 0

    except Exception as e:
        print(f"\n❌ Error generating minimal map: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
