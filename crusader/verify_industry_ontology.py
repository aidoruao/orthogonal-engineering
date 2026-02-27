"""
Industry Ontology Implementation Verification Script
===================================================

This script verifies the completeness of the industry ontology implementation
for the Crusader Combat Refrigerator system. It checks that all required
documentation exists and validates the structure against industry standards.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class IndustryOntologyVerifier:
    """Verification system for industry ontology implementation."""

    REQUIRED_FILES = {
        "certifications": [
            "ul_471_compliance.md",
            "food_safety.md",
            "energy_report.py",
        ],
        "hardware": [
            "refrigerant_spec.md",
        ],
        "supply_chain": [
            "bom.yaml",
        ],
        "manufacturing": [
            "assembly_instructions.md",
        ],
        "circular_economy": [
            "recycling.md",
        ],
        "tests/standards": [
            "industry_compliance_tests.py",
        ],
        ".": [
            "INDUSTRY_ONTOLOGY_IMPLEMENTATION_SUMMARY.md",
            "FINAL_INDUSTRY_ONTOLOGY_COMMIT.md",
        ],
    }

    INDUSTRY_STANDARDS = {
        "UL 471": "Safety for Commercial Refrigerators",
        "NSF/ANSI 7": "Commercial Refrigerators and Freezers",
        "FDA Food Code": "Food Safety Requirements",
        "DOE 10 CFR 429.14": "Energy Reporting",
        "EPA SNAP": "Refrigerant Approval",
        "EU WEEE": "Waste Electrical Equipment",
        "EPA R2/RIOS": "Electronics Recycling",
    }

    def __init__(self, base_dir: str = "."):
        """Initialize verifier with base directory."""
        self.base_dir = Path(base_dir)
        self.results = {}
        self.compliance_matrix = {}

    def verify_file_structure(self) -> Dict:
        """Verify all required files exist."""
        results = {
            "total_required": 0,
            "found": 0,
            "missing": [],
            "files": {},
        }

        for directory, files in self.REQUIRED_FILES.items():
            dir_path = self.base_dir / directory
            for filename in files:
                results["total_required"] += 1
                file_path = dir_path / filename

                if file_path.exists():
                    results["found"] += 1
                    file_info = {
                        "path": str(file_path.relative_to(self.base_dir)),
                        "exists": True,
                        "size_bytes": file_path.stat().st_size,
                        "sha256": self.calculate_file_hash(file_path),
                    }
                    results["files"][f"{directory}/{filename}"] = file_info
                else:
                    results["missing"].append(f"{directory}/{filename}")
                    results["files"][f"{directory}/{filename}"] = {
                        "path": str(file_path.relative_to(self.base_dir)),
                        "exists": False,
                    }

        results["coverage_percent"] = (
            results["found"] / results["total_required"] * 100
            if results["total_required"] > 0
            else 0
        )

        self.results["file_structure"] = results
        return results

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception:
            return "ERROR"

    def verify_industry_standards_coverage(self) -> Dict:
        """Verify coverage of industry standards in documentation."""
        standards_coverage = {}

        # Check UL 471 coverage
        ul_file = self.base_dir / "certifications" / "ul_471_compliance.md"
        if ul_file.exists():
            content = ul_file.read_text(encoding="utf-8", errors="ignore")
            standards_coverage["UL 471"] = {
                "covered": True,
                "file": "certifications/ul_471_compliance.md",
                "sections_found": self.count_sections(
                    content, ["Section 4", "Section 5", "Section 6"]
                ),
                "compliance_statement": "COMPLIANT BY DESIGN" in content,
            }

        # Check NSF/ANSI 7 coverage
        nsf_file = self.base_dir / "certifications" / "food_safety.md"
        if nsf_file.exists():
            content = nsf_file.read_text(encoding="utf-8", errors="ignore")
            standards_coverage["NSF/ANSI 7"] = {
                "covered": True,
                "file": "certifications/food_safety.md",
                "nsf_mentioned": "NSF/ANSI 7" in content or "NSF 7" in content,
                "material_safety": "Material Safety" in content,
            }

        # Check FDA coverage
        if nsf_file.exists():
            content = nsf_file.read_text(encoding="utf-8", errors="ignore")
            standards_coverage["FDA Food Code"] = {
                "covered": True,
                "file": "certifications/food_safety.md",
                "fda_mentioned": "FDA" in content,
                "temperature_control": "3-501.16"
                in content,  # FDA cold holding requirement
            }

        # Check DOE coverage
        doe_file = self.base_dir / "certifications" / "energy_report.py"
        if doe_file.exists():
            content = doe_file.read_text(encoding="utf-8", errors="ignore")
            standards_coverage["DOE 10 CFR 429.14"] = {
                "covered": True,
                "file": "certifications/energy_report.py",
                "doe_mentioned": "10 CFR 429.14" in content,
                "energy_reporting": "annual_energy_use_kwh" in content,
            }

        # Check EPA coverage
        epa_file = self.base_dir / "hardware" / "refrigerant_spec.md"
        if epa_file.exists():
            content = epa_file.read_text(encoding="utf-8", errors="ignore")
            standards_coverage["EPA SNAP"] = {
                "covered": True,
                "file": "hardware/refrigerant_spec.md",
                "epa_mentioned": "EPA" in content,
                "r290_approved": "R-290" in content and "SNAP" in content,
            }

        # Check recycling standards
        recycling_file = self.base_dir / "circular_economy" / "recycling.md"
        if recycling_file.exists():
            content = recycling_file.read_text(encoding="utf-8", errors="ignore")
            standards_coverage["EU WEEE"] = {
                "covered": "WEEE" in content,
                "file": "circular_economy/recycling.md",
                "weee_mentioned": "WEEE" in content,
            }
            standards_coverage["EPA R2/RIOS"] = {
                "covered": "R2/RIOS" in content,
                "file": "circular_economy/recycling.md",
                "r2_mentioned": "R2" in content or "RIOS" in content,
            }

        # Calculate coverage metrics
        total_standards = len(self.INDUSTRY_STANDARDS)
        covered_standards = sum(
            1 for std in standards_coverage.values() if std.get("covered")
        )

        standards_coverage["_metrics"] = {
            "total_industry_standards": total_standards,
            "covered_standards": covered_standards,
            "coverage_percent": covered_standards / total_standards * 100,
            "missing_standards": [
                std
                for std in self.INDUSTRY_STANDARDS
                if std not in standards_coverage
                or not standards_coverage[std].get("covered")
            ],
        }

        self.results["standards_coverage"] = standards_coverage
        return standards_coverage

    def count_sections(self, content: str, sections: List[str]) -> int:
        """Count how many of the specified sections are found in content."""
        return sum(1 for section in sections if section in content)

    def verify_supply_chain_completeness(self) -> Dict:
        """Verify supply chain documentation completeness."""
        bom_file = self.base_dir / "supply_chain" / "bom.yaml"
        results = {
            "bom_exists": bom_file.exists(),
            "component_categories": 0,
            "total_components": 0,
            "suppliers_mentioned": 0,
            "certifications_mentioned": 0,
        }

        if bom_file.exists():
            try:
                content = bom_file.read_text(encoding="utf-8", errors="ignore")
                # Simple analysis of BOM content
                results["component_categories"] = content.count("- part_number:")
                results["suppliers_mentioned"] = content.count("suppliers:")
                results["certifications_mentioned"] = content.count("certifications:")

                # Count approximate number of components
                lines = content.split("\n")
                in_component = False
                for line in lines:
                    if "part_number:" in line:
                        results["total_components"] += 1
                        in_component = True
                    elif in_component and line.strip() and not line.startswith("  "):
                        in_component = False
            except Exception as e:
                results["error"] = str(e)

        self.results["supply_chain"] = results
        return results

    def verify_manufacturing_documentation(self) -> Dict:
        """Verify manufacturing documentation completeness."""
        assembly_file = self.base_dir / "manufacturing" / "assembly_instructions.md"
        results = {
            "assembly_instructions_exist": assembly_file.exists(),
            "phases_defined": 0,
            "tools_listed": False,
            "quality_checkpoints": 0,
            "safety_procedures": False,
        }

        if assembly_file.exists():
            try:
                content = assembly_file.read_text(encoding="utf-8", errors="ignore")
                # Count assembly phases
                results["phases_defined"] = content.count("PHASE ")
                results["tools_listed"] = "TOOLS AND EQUIPMENT" in content
                results["quality_checkpoints"] = content.count("QUALITY CHECK")
                results["safety_procedures"] = "SAFETY" in content or "ESD" in content
            except Exception as e:
                results["error"] = str(e)

        self.results["manufacturing"] = results
        return results

    def verify_circular_economy(self) -> Dict:
        """Verify circular economy documentation."""
        recycling_file = self.base_dir / "circular_economy" / "recycling.md"
        results = {
            "recycling_documentation_exists": recycling_file.exists(),
            "recyclability_percentage": 0,
            "disassembly_procedures": False,
            "material_recovery": False,
            "compliance_standards": [],
        }

        if recycling_file.exists():
            try:
                content = recycling_file.read_text(encoding="utf-8", errors="ignore")
                # Extract recyclability percentage
                import re

                perc_match = re.search(r"(\d+\.?\d*)% recyclability", content)
                if perc_match:
                    results["recyclability_percentage"] = float(perc_match.group(1))

                results["disassembly_procedures"] = "DISASSEMBLY PROCEDURES" in content
                results["material_recovery"] = (
                    "MATERIAL RECOVERY" in content or "material recovery" in content
                )

                # Check for compliance standards
                standards = ["WEEE", "R2", "RIOS", "ISO 14001", "EPA"]
                results["compliance_standards"] = [
                    std for std in standards if std in content
                ]
            except Exception as e:
                results["error"] = str(e)

        self.results["circular_economy"] = results
        return results

    def verify_testing_framework(self) -> Dict:
        """Verify industry standards testing framework."""
        test_file = (
            self.base_dir / "tests" / "standards" / "industry_compliance_tests.py"
        )
        results = {
            "test_framework_exists": test_file.exists(),
            "test_classes": 0,
            "industry_standards_tested": [],
            "cryptographic_evidence": False,
        }

        if test_file.exists():
            try:
                content = test_file.read_text(encoding="utf-8", errors="ignore")
                # Count test classes
                results["test_classes"] = content.count("class.*Test")

                # Check for industry standards
                standards = ["UL 471", "NSF", "DOE", "FDA", "EPA"]
                results["industry_standards_tested"] = [
                    std for std in standards if std in content
                ]

                results["cryptographic_evidence"] = (
                    "sha256" in content
                    or "cryptographic" in content
                    or "witness" in content
                )
            except Exception as e:
                results["error"] = str(e)

        self.results["testing_framework"] = results
        return results

    def generate_compliance_matrix(self) -> Dict:
        """Generate comprehensive compliance matrix."""
        matrix = {}

        # File structure compliance
        file_results = self.results.get("file_structure", {})
        matrix["file_structure"] = {
            "requirement": "Complete documentation structure",
            "status": "COMPLIANT"
            if file_results.get("coverage_percent", 0) >= 80
            else "PARTIAL",
            "coverage": f"{file_results.get('coverage_percent', 0):.1f}%",
            "details": f"{file_results.get('found', 0)}/{file_results.get('total_required', 0)} files",
        }

        # Industry standards coverage
        standards_results = self.results.get("standards_coverage", {}).get(
            "_metrics", {}
        )
        matrix["industry_standards"] = {
            "requirement": "Industry standards coverage",
            "status": "COMPLIANT"
            if standards_results.get("coverage_percent", 0) >= 70
            else "PARTIAL",
            "coverage": f"{standards_results.get('coverage_percent', 0):.1f}%",
            "details": f"{standards_results.get('covered_standards', 0)}/{standards_results.get('total_industry_standards', 0)} standards",
        }

        # Supply chain
        supply_results = self.results.get("supply_chain", {})
        matrix["supply_chain"] = {
            "requirement": "Supply chain transparency",
            "status": "COMPLIANT" if supply_results.get("bom_exists") else "MISSING",
            "coverage": "COMPLETE"
            if supply_results.get("total_components", 0) > 20
            else "PARTIAL",
            "details": f"{supply_results.get('total_components', 0)} components documented",
        }

        # Manufacturing
        manufacturing_results = self.results.get("manufacturing", {})
        matrix["manufacturing"] = {
            "requirement": "Manufacturing documentation",
            "status": "COMPLIANT"
            if manufacturing_results.get("assembly_instructions_exist")
            else "MISSING",
            "coverage": "COMPLETE"
            if manufacturing_results.get("phases_defined", 0) >= 5
            else "PARTIAL",
            "details": f"{manufacturing_results.get('phases_defined', 0)} assembly phases",
        }

        # Circular economy
        circular_results = self.results.get("circular_economy", {})
        matrix["circular_economy"] = {
            "requirement": "Circular economy implementation",
            "status": "COMPLIANT"
            if circular_results.get("recycling_documentation_exists")
            else "MISSING",
            "coverage": "COMPLETE"
            if circular_results.get("recyclability_percentage", 0) >= 80
            else "PARTIAL",
            "details": f"{circular_results.get('recyclability_percentage', 0):.1f}% recyclability",
        }

        # Testing framework
        testing_results = self.results.get("testing_framework", {})
        matrix["testing_framework"] = {
            "requirement": "Compliance testing framework",
            "status": "COMPLIANT"
            if testing_results.get("test_framework_exists")
            else "MISSING",
            "coverage": "COMPLETE"
            if len(testing_results.get("industry_standards_tested", [])) >= 3
            else "PARTIAL",
            "details": f"{len(testing_results.get('industry_standards_tested', []))} standards tested",
        }

        # Calculate overall compliance
        compliant_items = sum(
            1 for item in matrix.values() if item["status"] == "COMPLIANT"
        )
        total_items = len(matrix)
        overall_percent = compliant_items / total_items * 100

        matrix["_overall"] = {
            "total_requirements": total_items,
            "compliant_requirements": compliant_items,
            "compliance_percentage": overall_percent,
            "status": "COMPLIANT" if overall_percent >= 80 else "PARTIAL",
        }

        self.compliance_matrix = matrix
        return matrix

    def run_all_checks(self) -> Dict:
        """Run all verification checks."""
        print("=" * 70)
        print("INDUSTRY ONTOLOGY IMPLEMENTATION VERIFICATION")
        print("=" * 70)

        print("\n1. Verifying file structure...")
        self.verify_file_structure()

        print("2. Verifying industry standards coverage...")
        self.verify_industry_standards_coverage()

        print("3. Verifying supply chain documentation...")
        self.verify_supply_chain_completeness()

        print("4. Verifying manufacturing documentation...")
        self.verify_manufacturing_documentation()

        print("5. Verifying circular economy implementation...")
        self.verify_circular_economy()

        print("6. Verifying testing framework...")
        self.verify_testing_framework()

        print("7. Generating compliance matrix...")
        self.generate_compliance_matrix()

        return self.results

    def print_summary(self) -> None:
        """Print comprehensive verification summary."""
        print("\n" + "=" * 70)
        print("INDUSTRY ONTOLOGY VERIFICATION SUMMARY")
        print("=" * 70)

        # File structure
        file_results = self.results.get("file_structure", {})
        print(
            f"\n1. FILE STRUCTURE: {file_results.get('found', 0)}/{file_results.get('total_required', 0)} files"
        )
        print(f"   Coverage: {file_results.get('coverage_percent', 0):.1f}%")
        if file_results.get("missing"):
            print(f"   Missing: {', '.join(file_results['missing'][:3])}")
            if len(file_results["missing"]) > 3:
                print(f"   ... and {len(file_results['missing']) - 3} more")

        # Industry standards
        standards_results = self.results.get("standards_coverage", {}).get(
            "_metrics", {}
        )
        print(
            f"\n2. INDUSTRY STANDARDS: {standards_results.get('covered_standards', 0)}/{standards_results.get('total_industry_standards', 0)} standards"
        )
        print(f"   Coverage: {standards_results.get('coverage_percent', 0):.1f}%")

        # Supply chain
        supply_results = self.results.get("supply_chain", {})
        print(
            f"\n3. SUPPLY CHAIN: {supply_results.get('total_components', 0)} components documented"
        )
        print(f"   BOM exists: {'YES' if supply_results.get('bom_exists') else 'NO'}")

        # Manufacturing
        manufacturing_results = self.results.get("manufacturing", {})
        print(
            f"\n4. MANUFACTURING: {manufacturing_results.get('phases_defined', 0)} assembly phases"
        )
        print(
            f"   Tools listed: {'YES' if manufacturing_results.get('tools_listed') else 'NO'}"
        )

        # Circular economy
        circular_results = self.results.get("circular_economy", {})
        print(
            f"\n5. CIRCULAR ECONOMY: {circular_results.get('recyclability_percentage', 0):.1f}% recyclability"
        )
        print(
            f"   Disassembly procedures: {'YES' if circular_results.get('disassembly_procedures') else 'NO'}"
        )

        # Testing framework
        testing_results = self.results.get("testing_framework", {})
        print(
            f"\n6. TESTING FRAMEWORK: {len(testing_results.get('industry_standards_tested', []))} standards tested"
        )
        print(
            f"   Cryptographic evidence: {'YES' if testing_results.get('cryptographic_evidence') else 'NO'}"
        )

        # Compliance matrix
        if self.compliance_matrix:
            print("\n" + "=" * 70)
            print("COMPLIANCE MATRIX")
            print("=" * 70)
            for key, value in self.compliance_matrix.items():
                if not key.startswith("_"):
                    print(f"\n{key.upper().replace('_', ' ')}:")
                    print(f"  Status: {value['status']}")
                    print(f"  Coverage: {value['coverage']}")
                    print(f"  Details: {value['details']}")

            overall = self.compliance_matrix.get("_overall", {})
            print("\n" + "=" * 70)
            print(f"OVERALL COMPLIANCE: {overall.get('compliance_percentage', 0):.1f}%")
            print(f"Status: {overall.get('status', 'UNKNOWN')}")
            print(
                f"Compliant: {overall.get('compliant_requirements', 0)}/{overall.get('total_requirements', 0)} requirements"
            )
            print("=" * 70)
