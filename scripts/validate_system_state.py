#!/usr/bin/env python3
"""
validate_system_state.py - System State Validation Script

Purpose: Validate the entire Orthogonal Engineering system state,
including contract compliance, proof integrity, and phase correctness.

Version: 1.0
Schema ID: SYSTEM-STATE-VALIDATE-1.0
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class SystemStateValidator:
    """Validate complete system state for Orthogonal Engineering"""

    def __init__(self, root_path: str = "."):
        self.root = Path(root_path)
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "validator_version": "1.0",
            "overall_status": "UNKNOWN",
            "components": {},
            "violations": [],
            "recommendations": [],
            "exit_code": 0,
        }

    def validate_contract_files(self) -> Dict:
        """Validate required contract and state files exist"""
        component = {
            "name": "contract_files",
            "status": "PASS",
            "checks": [],
            "missing": [],
        }

        required_files = [
            "AI_INTERACTION_CONTRACT.md",
            "STATE.md",
            "proof/LOGOS_IDENTITY_PROOF.md",
            "AGENT.md",
            "ONBOARDING_FOR_AI_AGENTS.md",
            "documentation/GLASS_BOX_BOUNDARY_v1.11.html",
        ]

        for file_path in required_files:
            full_path = self.root / file_path
            if full_path.exists():
                component["checks"].append(
                    {
                        "file": file_path,
                        "status": "EXISTS",
                        "size": full_path.stat().st_size,
                    }
                )
            else:
                component["status"] = "FAIL"
                component["missing"].append(file_path)
                self.results["violations"].append(f"Missing required file: {file_path}")

        return component

    def validate_proof_integrity(self) -> Dict:
        """Validate proof file structure and content"""
        component = {
            "name": "proof_integrity",
            "status": "PASS",
            "checks": [],
            "warnings": [],
        }

        proof_path = self.root / "proof" / "LOGOS_IDENTITY_PROOF.md"
        if not proof_path.exists():
            component["status"] = "FAIL"
            component["checks"].append(
                {
                    "check": "proof_exists",
                    "status": "FAIL",
                    "detail": "Proof file missing",
                }
            )
            return component

        try:
            with open(proof_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for required sections
            required_sections = [
                r"FORMAL PROOF",
                r"FALSIFICATION POINTS",
                r"THEOREM.*Λ ≡ Jesus",
                r"ESTABLISHED.*CLOSED",
            ]

            for section in required_sections:
                if re.search(section, content, re.IGNORECASE):
                    component["checks"].append(
                        {
                            "check": f"section_{section[:20]}",
                            "status": "PASS",
                            "detail": f"Found: {section}",
                        }
                    )
                else:
                    component["status"] = "FAIL"
                    component["checks"].append(
                        {
                            "check": f"section_{section[:20]}",
                            "status": "FAIL",
                            "detail": f"Missing: {section}",
                        }
                    )

            # Check for mathematical notation
            math_patterns = [r"Λ ≡", r"Coherent\(.*\)", r"∃Λ", r"Theorem.*:"]
            math_found = 0
            for pattern in math_patterns:
                if re.search(pattern, content):
                    math_found += 1

            if math_found >= 3:
                component["checks"].append(
                    {
                        "check": "mathematical_notation",
                        "status": "PASS",
                        "detail": f"Found {math_found}/4 math patterns",
                    }
                )
            else:
                component["status"] = "WARNING"
                component["warnings"].append(
                    f"Limited mathematical notation: {math_found}/4 patterns"
                )

        except Exception as e:
            component["status"] = "ERROR"
            component["checks"].append(
                {
                    "check": "proof_readable",
                    "status": "ERROR",
                    "detail": f"Failed to read proof: {str(e)}",
                }
            )

        return component

    def validate_state_consistency(self) -> Dict:
        """Validate STATE.md consistency with other files"""
        component = {
            "name": "state_consistency",
            "status": "PASS",
            "checks": [],
            "inconsistencies": [],
        }

        state_path = self.root / "STATE.md"
        if not state_path.exists():
            component["status"] = "FAIL"
            return component

        try:
            with open(state_path, "r", encoding="utf-8") as f:
                state_content = f.read()

            # Check state declares compilation mode
            if re.search(r"COMPILATION MODE", state_content, re.IGNORECASE):
                component["checks"].append(
                    {
                        "check": "declares_compilation",
                        "status": "PASS",
                        "detail": "State declares compilation mode",
                    }
                )
            else:
                component["status"] = "FAIL"
                component["inconsistencies"].append(
                    "STATE.md does not declare compilation mode"
                )

            # Check for established proofs declaration
            if re.search(r"ESTABLISHED PROOFS.*CLOSED", state_content, re.DOTALL):
                component["checks"].append(
                    {
                        "check": "declares_proofs",
                        "status": "PASS",
                        "detail": "State declares established proofs",
                    }
                )
            else:
                component["status"] = "WARNING"
                component["inconsistencies"].append(
                    "STATE.md may not clearly declare proofs as closed"
                )

            # Check version consistency
            version_match = re.search(r"Version:\s*([\d.]+)", state_content)
            if version_match:
                component["checks"].append(
                    {
                        "check": "has_version",
                        "status": "PASS",
                        "detail": f"Version: {version_match.group(1)}",
                    }
                )
            else:
                component["status"] = "WARNING"
                component["inconsistencies"].append("STATE.md missing version")

        except Exception as e:
            component["status"] = "ERROR"
            component["checks"].append(
                {
                    "check": "state_readable",
                    "status": "ERROR",
                    "detail": f"Failed to read state: {str(e)}",
                }
            )

        return component

    def validate_contract_consistency(self) -> Dict:
        """Validate AI_INTERACTION_CONTRACT.md consistency"""
        component = {
            "name": "contract_consistency",
            "status": "PASS",
            "checks": [],
            "issues": [],
        }

        contract_path = self.root / "AI_INTERACTION_CONTRACT.md"
        if not contract_path.exists():
            component["status"] = "FAIL"
            return component

        try:
            with open(contract_path, "r", encoding="utf-8") as f:
                contract_content = f.read()

            # Check for forbidden patterns section
            if re.search(r"FORBIDDEN.*PATTERNS", contract_content, re.DOTALL):
                component["checks"].append(
                    {
                        "check": "has_forbidden_patterns",
                        "status": "PASS",
                        "detail": "Contract defines forbidden patterns",
                    }
                )
            else:
                component["status"] = "FAIL"
                component["issues"].append(
                    "Contract missing forbidden patterns section"
                )

            # Check for allowed operations
            if re.search(r"ALLOWED.*OPERATIONS", contract_content, re.DOTALL):
                component["checks"].append(
                    {
                        "check": "has_allowed_operations",
                        "status": "PASS",
                        "detail": "Contract defines allowed operations",
                    }
                )
            else:
                component["status"] = "FAIL"
                component["issues"].append(
                    "Contract missing allowed operations section"
                )

            # Check for phase seal
            if re.search(r"PHASE SEAL", contract_content, re.IGNORECASE):
                component["checks"].append(
                    {
                        "check": "has_phase_seal",
                        "status": "PASS",
                        "detail": "Contract defines phase seal",
                    }
                )
            else:
                component["status"] = "WARNING"
                component["issues"].append("Contract missing explicit phase seal")

            # Check for violation handling
            if re.search(r"VIOLATION.*HANDLING", contract_content, re.DOTALL):
                component["checks"].append(
                    {
                        "check": "has_violation_handling",
                        "status": "PASS",
                        "detail": "Contract defines violation handling",
                    }
                )
            else:
                component["status"] = "WARNING"
                component["issues"].append("Contract missing violation handling")

        except Exception as e:
            component["status"] = "ERROR"
            component["checks"].append(
                {
                    "check": "contract_readable",
                    "status": "ERROR",
                    "detail": f"Failed to read contract: {str(e)}",
                }
            )

        return component

    def validate_script_integrity(self) -> Dict:
        """Validate script files exist and are executable"""
        component = {
            "name": "script_integrity",
            "status": "PASS",
            "checks": [],
            "missing_scripts": [],
        }

        required_scripts = [
            "scripts/verify_ai_phase.py",
        ]

        for script_path in required_scripts:
            full_path = self.root / script_path
            if full_path.exists():
                # Check if it's a Python file
                if script_path.endswith(".py"):
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            first_line = f.readline()
                        if first_line.startswith("#!/usr/bin/env python"):
                            component["checks"].append(
                                {
                                    "file": script_path,
                                    "status": "EXECUTABLE",
                                    "detail": "Has Python shebang",
                                }
                            )
                        else:
                            component["status"] = "WARNING"
                            component["checks"].append(
                                {
                                    "file": script_path,
                                    "status": "WARNING",
                                    "detail": "Missing Python shebang",
                                }
                            )
                    except:
                        component["checks"].append(
                            {
                                "file": script_path,
                                "status": "EXISTS",
                                "detail": "File exists",
                            }
                        )
                else:
                    component["checks"].append(
                        {
                            "file": script_path,
                            "status": "EXISTS",
                            "detail": "File exists",
                        }
                    )
            else:
                component["status"] = "WARNING"
                component["missing_scripts"].append(script_path)
                component["checks"].append(
                    {
                        "file": script_path,
                        "status": "MISSING",
                        "detail": "Script file not found",
                    }
                )

        return component

    def validate_directory_structure(self) -> Dict:
        """Validate required directory structure"""
        component = {
            "name": "directory_structure",
            "status": "PASS",
            "checks": [],
            "missing_dirs": [],
        }

        required_dirs = [
            "proof",
            "scripts",
            "documentation",
            "automation",
            "logs",
            "toolkit/oe",
        ]

        for dir_path in required_dirs:
            full_path = self.root / dir_path
            if full_path.exists() and full_path.is_dir():
                component["checks"].append(
                    {
                        "directory": dir_path,
                        "status": "EXISTS",
                        "detail": "Directory exists",
                    }
                )
            else:
                component["status"] = "WARNING"
                component["missing_dirs"].append(dir_path)
                component["checks"].append(
                    {
                        "directory": dir_path,
                        "status": "MISSING",
                        "detail": "Directory not found",
                    }
                )

        return component

    def run_full_validation(self) -> Dict:
        """Run complete system validation"""
        components = []

        # Run all validations
        components.append(self.validate_contract_files())
        components.append(self.validate_proof_integrity())
        components.append(self.validate_state_consistency())
        components.append(self.validate_contract_consistency())
        components.append(self.validate_script_integrity())
        components.append(self.validate_directory_structure())

        # Store components
        self.results["components"] = {
            comp["name"]: {
                "status": comp["status"],
                "checks": comp.get("checks", []),
                "issues": comp.get("issues", []),
                "warnings": comp.get("warnings", []),
                "missing": comp.get("missing", []),
                "inconsistencies": comp.get("inconsistencies", []),
            }
            for comp in components
        }

        # Determine overall status
        statuses = [comp["status"] for comp in components]
        if "FAIL" in statuses:
            self.results["overall_status"] = "FAIL"
            self.results["exit_code"] = 2
        elif "ERROR" in statuses:
            self.results["overall_status"] = "ERROR"
            self.results["exit_code"] = 3
        elif "WARNING" in statuses:
            self.results["overall_status"] = "WARNING"
            self.results["exit_code"] = 1
        else:
            self.results["overall_status"] = "PASS"
            self.results["exit_code"] = 0

        # Generate recommendations
        self._generate_recommendations(components)

        return self.results

    def _generate_recommendations(self, components: List[Dict]) -> None:
        """Generate recommendations based on validation results"""
        recommendations = []

        for comp in components:
            if comp["status"] == "FAIL":
                if comp["name"] == "contract_files":
                    missing = comp.get("missing", [])
                    if missing:
                        recommendations.append(
                            f"Create missing required files: {', '.join(missing[:3])}"
                        )
                elif comp["name"] == "proof_integrity":
                    recommendations.append(
                        "Fix proof file structure - ensure all required sections exist"
                    )
                elif comp["name"] == "state_consistency":
                    recommendations.append(
                        "Update STATE.md to clearly declare compilation mode and established proofs"
                    )
                elif comp["name"] == "contract_consistency":
                    recommendations.append(
                        "Update AI_INTERACTION_CONTRACT.md with required sections"
                    )

            elif comp["status"] == "WARNING":
                if comp["name"] == "script_integrity":
                    missing = comp.get("missing_scripts", [])
                    if missing:
                        recommendations.append(
                            f"Consider creating scripts: {', '.join(missing[:2])}"
                        )
                elif comp["name"] == "directory_structure":
                    missing = comp.get("missing_dirs", [])
                    if missing:
                        recommendations.append(
                            f"Create directories for better organization: {', '.join(missing[:3])}"
                        )

        self.results["recommendations"] = recommendations

    def generate_report(self, results: Dict) -> str:
        """Generate human-readable validation report"""
        report = []
        report.append("=" * 70)
        report.append("ORTHOGONAL ENGINEERING - SYSTEM STATE VALIDATION REPORT")
        report.append("=" * 70)
        report.append(f"Timestamp: {results.get('timestamp', 'Unknown')}")
        report.append(f"Overall Status: {results.get('overall_status', 'UNKNOWN')}")
        report.append(f"Exit Code: {results.get('exit_code', 0)}")
        report.append("")

        # Component summary
        report.append("COMPONENT VALIDATION SUMMARY:")
        report.append("-" * 40)

        components = results.get("components", {})
        for name, data in components.items():
            status = data.get("status", "UNKNOWN")
            status_symbol = (
                "✅" if status == "PASS" else "⚠️" if status == "WARNING" else "❌"
            )
            report.append(f"{status_symbol} {name}: {status}")

        report.append("")

        # Detailed component reports
        for name, data in components.items():
            if data.get("status") in ["FAIL", "WARNING", "ERROR"]:
                report.append(f"DETAILED: {name.upper()}")
                report.append("-" * 30)

                checks = data.get("checks", [])
                for check in checks:
                    status = check.get("status", "UNKNOWN")
                    symbol = (
                        "✓" if status == "PASS" else "⚠" if status == "WARNING" else "✗"
                    )
                    report.append(
                        f"  {symbol} {check.get('check', 'Unknown')}: {check.get('detail', '')}"
                    )

                issues = data.get("issues", [])
                if issues:
                    report.append("  Issues:")
                    for issue in issues[:3]:  # Limit to 3 issues
                        report.append(f"    • {issue}")

                warnings = data.get("warnings", [])
                if warnings:
                    report.append("  Warnings:")
                    for warning in warnings[:3]:
                        report.append(f"    • {warning}")

                missing = data.get("missing", [])
                if missing:
                    report.append("  Missing:")
                    for item in missing[:3]:
                        report.append(f"    • {item}")

                report.append("")

        # Violations
        violations = results.get("violations", [])
        if violations:
            report.append("🚨 CRITICAL VIOLATIONS:")
            report.append("-" * 30)
            for violation in violations[:5]:  # Limit to 5 violations
                report.append(f"• {violation}")
            report.append("")

        # Recommendations
        recommendations = results.get("recommendations", [])
        if recommendations:
            report.append("💡 RECOMMENDATIONS:")
            report.append("-" * 30)
            for rec in recommendations[:5]:  # Limit to 5 recommendations
                report.append(f"• {rec}")
            report.append("")

        # Final status
        if results.get("overall_status") == "PASS":
            report.append
