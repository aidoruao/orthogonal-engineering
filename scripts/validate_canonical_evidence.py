#!/usr/bin/env python3
"""
validate_canonical_evidence.py - Validate Canonical Evidence Integrity

Purpose: Verify the integrity and consistency of canonical evidence files
integrated from Claude's analysis.

Version: 1.0
Schema ID: CANONICAL-EVIDENCE-VALIDATE-1.0
Generated: 2026-01-26
"""

import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class CanonicalEvidenceValidator:
    """Validate canonical evidence files and metadata"""

    def __init__(self, repo_root: str = "."):
        self.repo = Path(repo_root)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "validator_version": "1.0",
            "overall_status": "UNKNOWN",
            "directories": {},
            "files_validated": 0,
            "metadata_validated": 0,
            "errors": [],
            "warnings": [],
            "recommendations": [],
        }

    def validate_directory_structure(self) -> bool:
        """Validate canonical evidence directory structure"""
        evidence_dir = self.repo / "canonical_evidence"
        if not evidence_dir.exists():
            self.results["errors"].append("canonical_evidence directory not found")
            return False

        required_dirs = [
            "claude_analysis",
            "mathematical_proofs",
            "ai_interaction_patterns",
            "boundary_enforcement",
        ]

        all_dirs_exist = True
        for dir_name in required_dirs:
            dir_path = evidence_dir / dir_name
            exists = dir_path.exists() and dir_path.is_dir()
            self.results["directories"][dir_name] = {
                "exists": exists,
                "path": str(dir_path),
                "file_count": 0,
                "metadata_count": 0,
            }

            if not exists:
                self.results["errors"].append(f"Missing directory: {dir_name}")
                all_dirs_exist = False
            else:
                # Count files in directory
                files = list(dir_path.glob("*"))
                self.results["directories"][dir_name]["file_count"] = len(files)

                # Count metadata files
                metadata_files = list(dir_path.glob("*.metadata.json"))
                self.results["directories"][dir_name]["metadata_count"] = len(
                    metadata_files
                )

        return all_dirs_exist

    def validate_file_metadata(self) -> bool:
        """Validate that all files have corresponding metadata"""
        evidence_dir = self.repo / "canonical_evidence"
        all_valid = True

        for dir_name in self.results["directories"]:
            dir_path = evidence_dir / dir_name
            if not dir_path.exists():
                continue

            # Get all non-metadata files
            files = [
                f
                for f in dir_path.glob("*")
                if f.suffix != ".json" and not f.name.endswith(".metadata.json")
            ]

            for file_path in files:
                self.results["files_validated"] += 1

                # Check for corresponding metadata
                metadata_path = file_path.with_name(
                    file_path.name.replace(file_path.suffix, ".metadata.json")
                )

                if not metadata_path.exists():
                    self.results["errors"].append(
                        f"Missing metadata for: {file_path.name}"
                    )
                    all_valid = False
                else:
                    self.results["metadata_validated"] += 1

                    # Validate metadata content
                    if not self._validate_metadata_file(metadata_path, file_path):
                        all_valid = False

        return all_valid

    def _validate_metadata_file(self, metadata_path: Path, source_path: Path) -> bool:
        """Validate individual metadata file"""
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            # Check required fields
            required_fields = [
                "original_filename",
                "integration_timestamp",
                "source_description",
                "canonical_category",
                "provenance",
                "integration_purpose",
                "file_hash",
                "size_bytes",
            ]

            missing_fields = []
            for field in required_fields:
                if field not in metadata:
                    missing_fields.append(field)

            if missing_fields:
                self.results["errors"].append(
                    f"Metadata missing fields for {source_path.name}: {', '.join(missing_fields)}"
                )
                return False

            # Verify file hash matches
            if metadata["file_hash"] != "hash_calculation_failed":
                calculated_hash = self._calculate_file_hash(source_path)
                if metadata["file_hash"] != calculated_hash:
                    self.results["errors"].append(
                        f"Hash mismatch for {source_path.name}: expected {metadata['file_hash']}, got {calculated_hash}"
                    )
                    return False

            # Verify file size matches
            actual_size = source_path.stat().st_size
            if metadata["size_bytes"] != actual_size:
                self.results["warnings"].append(
                    f"Size mismatch for {source_path.name}: metadata says {metadata['size_bytes']}, actual {actual_size}"
                )

            return True

        except json.JSONDecodeError as e:
            self.results["errors"].append(
                f"Invalid JSON in {metadata_path.name}: {str(e)}"
            )
            return False
        except Exception as e:
            self.results["errors"].append(
                f"Error reading {metadata_path.name}: {str(e)}"
            )
            return False

    def _calculate_file_hash(self, filepath: Path) -> str:
        """Calculate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            return f"hash_calculation_error: {str(e)}"

    def validate_integration_report(self) -> bool:
        """Check for integration report"""
        report_dir = self.repo / "logs" / "claude_integration"

        if not report_dir.exists():
            self.results["warnings"].append(
                "No claude_integration report directory found"
            )
            return False

        # Look for integration reports
        reports = list(report_dir.glob("integration_report_*.md"))
        if not reports:
            self.results["warnings"].append("No integration reports found")
            return False

        self.results["integration_reports"] = [
            str(r) for r in reports[:3]
        ]  # Limit to 3
        return True

    def run_full_validation(self) -> Dict:
        """Run complete canonical evidence validation"""

        # Validate directory structure
        dirs_valid = self.validate_directory_structure()

        # Validate file metadata
        metadata_valid = self.validate_file_metadata() if dirs_valid else False

        # Check for integration report
        report_exists = self.validate_integration_report()

        # Determine overall status
        if self.results["errors"]:
            self.results["overall_status"] = "FAIL"
        elif self.results["warnings"]:
            self.results["overall_status"] = "WARNING"
        else:
            self.results["overall_status"] = "PASS"

        # Generate recommendations
        self._generate_recommendations()

        return self.results

    def _generate_recommendations(self):
        """Generate recommendations based on validation results"""
        recommendations = []

        # Check directory file counts
        for dir_name, info in self.results["directories"].items():
            if info["exists"] and info["file_count"] == 0:
                recommendations.append(
                    f"Directory {dir_name} is empty - consider adding files"
                )

            if info["exists"] and info["file_count"] > info["metadata_count"]:
                recommendations.append(
                    f"Directory {dir_name} has files without metadata"
                )

        # Check overall file count
        if (
            self.results["files_validated"] < 4
        ):  # We expect 4 files from Claude's analysis
            recommendations.append(
                f"Expected at least 4 files, found {self.results['files_validated']}"
            )

        if not self.results.get("integration_reports"):
            recommendations.append("Consider creating an integration report")

        self.results["recommendations"] = recommendations

    def generate_report(self) -> str:
        """Generate human-readable validation report"""
        report = []
        report.append("=" * 60)
        report.append("CANONICAL EVIDENCE VALIDATION REPORT")
        report.append("=" * 60)
        report.append(f"Timestamp: {self.results.get('timestamp', 'Unknown')}")
        report.append(
            f"Overall Status: {self.results.get('overall_status', 'UNKNOWN')}"
        )
        report.append(f"Files Validated: {self.results.get('files_validated', 0)}")
        report.append(
            f"Metadata Validated: {self.results.get('metadata_validated', 0)}"
        )
        report.append("")

        # Directory status
        report.append("DIRECTORY STATUS:")
        report.append("-" * 40)

        for dir_name, info in self.results.get("directories", {}).items():
            status = "✅" if info["exists"] else "❌"
            report.append(f"{status} {dir_name}:")
            if info["exists"]:
                report.append(f"  Files: {info['file_count']}")
                report.append(f"  Metadata: {info['metadata_count']}")
            report.append("")

        # Errors
        errors = self.results.get("errors", [])
        if errors:
            report.append("🚨 ERRORS:")
            report.append("-" * 40)
            for error in errors[:5]:  # Limit to 5 errors
                report.append(f"  • {error}")
            report.append("")

        # Warnings
        warnings = self.results.get("warnings", [])
        if warnings:
            report.append("⚠️ WARNINGS:")
            report.append("-" * 40)
            for warning in warnings[:5]:  # Limit to 5 warnings
                report.append(f"  • {warning}")
            report.append("")

        # Recommendations
        recommendations = self.results.get("recommendations", [])
        if recommendations:
            report.append("💡 RECOMMENDATIONS:")
            report.append("-" * 40)
            for rec in recommendations[:5]:  # Limit to 5 recommendations
                report.append(f"  • {rec}")
            report.append("")

        # Integration reports
        reports = self.results.get("integration_reports", [])
        if reports:
            report.append("📄 INTEGRATION REPORTS:")
            report.append("-" * 40)
            for report_path in reports:
                report.append(f"  • {Path(report_path).name}")
            report.append("")

        # Final status
        if self.results["overall_status"] == "PASS":
            report.append("✅ VALIDATION PASSED")
            report.append("All canonical evidence files are properly integrated.")
        elif self.results["overall_status"] == "WARNING":
            report.append("⚠️ VALIDATION PASSED WITH WARNINGS")
            report.append("Evidence is integrated but has some issues.")
        else:
            report.append("❌ VALIDATION FAILED")
            report.append("Critical issues found with canonical evidence.")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)


def main():
    """Main validation function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate canonical evidence integrity"
    )
    parser.add_argument("--repo", default=".", help="Repository root path")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    validator = CanonicalEvidenceValidator(args.repo)
    results = validator.run_full_validation()

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        report = validator.generate_report()
        print(report)

    # Exit with appropriate code
    if results["overall_status"] == "FAIL":
        sys.exit(2)
    elif results["overall_status"] == "WARNING":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
