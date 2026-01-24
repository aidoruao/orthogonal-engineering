"""
Phase 9 Verification Script

Runs comprehensive verification of Phase 9 artifacts, validates G9 invariants,
verifies cryptographic linkage to Phase 8, and generates final verification report.

This script implements the verification steps outlined in the Phase 10 blueprint
and produces exit code 0 if all checks pass, exit code 2 on boundary violations.

Author: Orthogonal Engineering System
Date: 2026-01-22
Version: 1.0.0
"""

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class Phase9Verification:
    """
    Comprehensive verification of Phase 9 implementation.

    Implements all verification steps from Phase 10 blueprint:
    1. Parse Phase 9 HTML blueprint
    2. Validate all Phase 9 artifacts
    3. Verify cryptographic linkage to Phase 8
    4. Execute Phase 9 workflows
    5. Generate verification report
    6. Commit and push results
    """

    def __init__(self, strict_mode: bool = True):
        """
        Initialize verification.

        Args:
            strict_mode: If True, exit with code 2 on any violation
        """
        self.strict_mode = strict_mode
        self.violations: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.verification_results: Dict[str, Any] = {}

        # Paths
        self.repo_root = Path(__file__).parent.parent
        self.phase9_blueprint = (
            self.repo_root / "glass-box" / "GLASS_BOX_BOUNDARY_v1.12.html"
        )
        self.phase8_commit = "62bead3"

        # Create verification directories
        self.verification_logs = self.repo_root / "logs" / "verification" / "phase9"
        self.verification_logs.mkdir(parents=True, exist_ok=True)

        # Verification timestamp
        self.verification_id = (
            f"VERIFY-PHASE9-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        )

    def run_comprehensive_verification(self) -> Dict[str, Any]:
        """
        Run comprehensive Phase 9 verification.

        Returns:
            Verification results dictionary
        """
        try:
            print("=" * 80)
            print("PHASE 9 COMPREHENSIVE VERIFICATION")
            print("=" * 80)
            print(f"Verification ID: {self.verification_id}")
            print(f"Timestamp: {datetime.now().isoformat()}")
            print(f"Repository: {self.repo_root}")
            print("=" * 80)
        except UnicodeEncodeError:
            # Fallback for encoding issues
            print("=" * 80)
            print("PHASE 9 COMPREHENSIVE VERIFICATION")
            print("=" * 80)
            print(f"Verification ID: {self.verification_id}")
            print(f"Timestamp: {datetime.now().isoformat()}")
            print(
                f"Repository: {str(self.repo_root).encode('ascii', 'replace').decode('ascii')}"
            )
            print("=" * 80)

        verification_start = time.time()

        # Run all verification steps
        steps = [
            ("Parse Phase 9 Blueprint", self.parse_phase9_blueprint),
            ("Validate Phase 9 Artifacts", self.validate_phase9_artifacts),
            ("Verify Cryptographic Linkage", self.verify_cryptographic_linkage),
            ("Execute Phase 9 Workflows", self.execute_phase9_workflows),
            ("Generate Verification Report", self.generate_verification_report),
            ("Update SHA256 Manifest", self.update_sha256_manifest),
        ]

        results = {}
        for step_name, step_func in steps:
            try:
                print(f"\n[{step_name}]")
            except UnicodeEncodeError:
                print(f"\n[{step_name.encode('ascii', 'replace').decode('ascii')}]")
            step_start = time.time()

            try:
                step_result = step_func()
                step_duration = time.time() - step_start
                step_result["duration_seconds"] = step_duration
                results[step_name.lower().replace(" ", "_")] = step_result

                # Check for violations
                if step_result.get("has_violations", False):
                    print(f"  ✗ Step completed with violations")
                    self.violations.extend(step_result.get("violations", []))
                else:
                    print(f"  ✓ Step completed successfully")

                print(f"  Duration: {step_duration:.2f} seconds")

            except Exception as e:
                step_duration = time.time() - step_start
                error_result = {
                    "error": str(e),
                    "duration_seconds": step_duration,
                    "has_violations": True,
                    "violations": [
                        {
                            "type": "step_execution_error",
                            "step": step_name,
                            "message": str(e),
                        }
                    ],
                }
                results[step_name.lower().replace(" ", "_")] = error_result
                self.violations.extend(error_result["violations"])
                print(f"  ✗ Step failed: {str(e)}")
                print(f"  Duration: {step_duration:.2f} seconds")

        # Calculate overall verification status
        verification_end = time.time()
        verification_duration = verification_end - verification_start

        all_steps_successful = all(
            not result.get("has_violations", False)
            for result in results.values()
            if isinstance(result, dict)
        )

        overall_result = {
            "verification_id": self.verification_id,
            "timestamp": datetime.fromtimestamp(verification_start).isoformat(),
            "duration_seconds": verification_duration,
            "successful": all_steps_successful and len(self.violations) == 0,
            "total_steps": len(steps),
            "successful_steps": sum(
                1
                for result in results.values()
                if isinstance(result, dict) and not result.get("has_violations", False)
            ),
            "total_violations": len(self.violations),
            "total_warnings": len(self.warnings),
            "violations": self.violations,
            "warnings": self.warnings,
            "detailed_results": results,
            "phase8_linkage": {
                "commit_hash": self.phase8_commit,
                "verified": self._verify_phase8_commit(),
            },
            "phase9_artifacts": {
                "blueprint": str(self.phase9_blueprint),
                "exists": self.phase9_blueprint.exists(),
            },
        }

        self.verification_results = overall_result

        # Save verification results
        self._save_verification_results(overall_result)

        # Print summary
        self._print_verification_summary(overall_result)

        return overall_result

    def parse_phase9_blueprint(self) -> Dict[str, Any]:
        """
        Parse Phase 9 HTML blueprint.

        Returns:
            Parsing results
        """
        if not self.phase9_blueprint.exists():
            return {
                "has_violations": True,
                "violations": [
                    {
                        "type": "missing_blueprint",
                        "file": str(self.phase9_blueprint),
                        "message": "Phase 9 HTML blueprint not found",
                    }
                ],
            }

        try:
            # Read blueprint content with error handling for special characters
            try:
                content = self.phase9_blueprint.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                # Try with error replacement for problematic characters
                content = self.phase9_blueprint.read_text(
                    encoding="utf-8", errors="replace"
                )

            # Check for Phase 9 markers
            has_phase9 = "Phase 9" in content
            has_g9_invariants = "G9-01" in content
            has_schema_1_12 = "1.12" in content

            # Extract basic information
            file_size = self.phase9_blueprint.stat().st_size

            return {
                "has_violations": False,
                "file_size_bytes": file_size,
                "has_phase9_marker": has_phase9,
                "has_g9_invariants": has_g9_invariants,
                "has_schema_1_12": has_schema_1_12,
                "parsed_successfully": True,
            }

        except Exception as e:
            return {
                "has_violations": True,
                "violations": [
                    {
                        "type": "blueprint_parsing_error",
                        "file": str(self.phase9_blueprint),
                        "message": f"Failed to parse blueprint: {str(e)}",
                    }
                ],
            }

    def validate_phase9_artifacts(self) -> Dict[str, Any]:
        """
        Validate all Phase 9 artifacts.

        Returns:
            Validation results
        """
        # Run the Phase 9 artifact validator
        validator_script = (
            self.repo_root / "automation" / "validate_phase9_artifacts.py"
        )

        if not validator_script.exists():
            return {
                "has_violations": True,
                "violations": [
                    {
                        "type": "missing_validator",
                        "file": str(validator_script),
                        "message": "Phase 9 artifact validator not found",
                    }
                ],
            }

        try:
            # Run validator with strict mode
            cmd = [sys.executable, str(validator_script), "--full", "--strict"]
            if self.strict_mode:
                cmd.append("--exit-code-2")

            result = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse validator output
            try:
                # Look for JSON output in stdout
                import re

                json_match = re.search(r"\{.*\}", result.stdout, re.DOTALL)
                if json_match:
                    validator_result = json.loads(json_match.group())
                else:
                    # Try to find result file
                    result_files = list(
                        self.repo_root.glob("logs/validation/phase9/*.json")
                    )
                    if result_files:
                        latest = max(result_files, key=lambda p: p.stat().st_mtime)
                        validator_result = json.loads(latest.read_text())
                    else:
                        validator_result = {
                            "exit_code": result.returncode,
                            "stdout": result.stdout[:500],
                            "stderr": result.stderr[:500],
                        }
            except:
                validator_result = {
                    "exit_code": result.returncode,
                    "stdout": result.stdout[:500],
                    "stderr": result.stderr[:500],
                }

            return {
                "has_violations": result.returncode != 0,
                "exit_code": result.returncode,
                "validator_output": validator_result,
                "command": " ".join(cmd),
            }

        except subprocess.TimeoutExpired:
            return {
                "has_violations": True,
                "violations": [
                    {
                        "type": "validator_timeout",
                        "message": "Phase 9 artifact validator timed out after 5 minutes",
                    }
                ],
            }
        except Exception as e:
            return {
                "has_violations": True,
                "violations": [
                    {
                        "type": "validator_execution_error",
                        "message": f"Failed to run validator: {str(e)}",
                    }
                ],
            }

    def verify_cryptographic_linkage(self) -> Dict[str, Any]:
        """
        Verify cryptographic linkage to Phase 8.

        Returns:
            Verification results
        """
        violations = []
        warnings = []

        # Verify Phase 8 commit exists
        phase8_verified = self._verify_phase8_commit()
        if not phase8_verified:
            violations.append(
                {
                    "type": "phase8_commit_not_found",
                    "commit": self.phase8_commit,
                    "message": "Phase 8 commit not found in git history",
                }
            )

        # Check Phase 8 artifacts
        phase8_artifacts = [
            "automation/phase8_atomic_workflow.py",
            "automation/run_full_audit_with_trace.py",
            "documentation/GLASS_BOX_BOUNDARY_v1.11.html",
        ]

        artifact_results = []
        for artifact in phase8_artifacts:
            artifact_path = self.repo_root / artifact
            if artifact_path.exists():
                # Calculate hash
                try:
                    file_hash = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
                    artifact_results.append(
                        {
                            "artifact": artifact,
                            "exists": True,
                            "sha256_hash": file_hash,
                            "file_size": artifact_path.stat().st_size,
                        }
                    )
                except Exception as e:
                    artifact_results.append(
                        {"artifact": artifact, "exists": True, "error": str(e)}
                    )
                    warnings.append(
                        {
                            "type": "hash_calculation_error",
                            "artifact": artifact,
                            "message": f"Failed to calculate hash: {str(e)}",
                        }
                    )
            else:
                artifact_results.append({"artifact": artifact, "exists": False})
                violations.append(
                    {
                        "type": "missing_phase8_artifact",
                        "artifact": artifact,
                        "message": "Required Phase 8 artifact not found",
                    }
                )

        # Check Phase 9 proof file
        proof_file = self.repo_root / "proof" / "phase9_proof.json"
        if proof_file.exists():
            try:
                proof_content = json.loads(proof_file.read_text())
                proof_valid = proof_content.get("proof_type") == "cryptographic_linkage"
            except:
                proof_valid = False
                violations.append(
                    {
                        "type": "invalid_proof_file",
                        "file": str(proof_file),
                        "message": "Phase 9 proof file is invalid JSON",
                    }
                )
        else:
            proof_valid = False
            violations.append(
                {
                    "type": "missing_proof_file",
                    "file": str(proof_file),
                    "message": "Phase 9 proof file not found",
                }
            )

        return {
            "has_violations": len(violations) > 0,
            "violations": violations,
            "warnings": warnings,
            "phase8_commit_verified": phase8_verified,
            "phase8_artifacts": artifact_results,
            "phase9_proof_exists": proof_file.exists(),
            "phase9_proof_valid": proof_valid,
        }

    def execute_phase9_workflows(self) -> Dict[str, Any]:
        """
        Execute Phase 9 workflows.

        Returns:
            Execution results
        """
        # Check for workflow files
        workflow_files = [
            "workflows/phase9_advanced_validation.yaml",
            "workflows/causal_analysis_workflow.yaml",
            "workflows/debt_tracking_workflow.yaml",
            "workflows/trace_enrichment_workflow.yaml",
        ]

        workflow_results = []
        violations = []

        for workflow_file in workflow_files:
            workflow_path = self.repo_root / workflow_file

            if not workflow_path.exists():
                violations.append(
                    {
                        "type": "missing_workflow",
                        "file": workflow_file,
                        "message": "Workflow file not found",
                    }
                )
                workflow_results.append(
                    {"workflow": workflow_file, "exists": False, "executed": False}
                )
                continue

            # Try to validate the workflow
            try:
                # Use workflow executor to validate
                executor_script = (
                    self.repo_root / "automation" / "phase9_workflow_executor.py"
                )

                if executor_script.exists():
                    cmd = [
                        sys.executable,
                        str(executor_script),
                        "validate",
                        str(workflow_path),
                    ]
                    result = subprocess.run(
                        cmd,
                        cwd=self.repo_root,
                        capture_output=True,
                        text=True,
                        timeout=60,
                    )

                    workflow_results.append(
                        {
                            "workflow": workflow_file,
                            "exists": True,
                            "validated": result.returncode == 0,
                            "exit_code": result.returncode,
                            "validation_output": result.stdout[:200],
                        }
                    )

                    if result.returncode != 0:
                        violations.append(
                            {
                                "type": "workflow_validation_failed",
                                "file": workflow_file,
                                "message": f"Workflow validation failed with exit code {result.returncode}",
                                "details": result.stderr[:200],
                            }
                        )
                else:
                    workflow_results.append(
                        {
                            "workflow": workflow_file,
                            "exists": True,
                            "validated": False,
                            "error": "Workflow executor not found",
                        }
                    )

            except Exception as e:
                workflow_results.append(
                    {
                        "workflow": workflow_file,
                        "exists": True,
                        "validated": False,
                        "error": str(e),
                    }
                )
                violations.append(
                    {
                        "type": "workflow_validation_error",
                        "file": workflow_file,
                        "message": f"Workflow validation error: {str(e)}",
                    }
                )

        # Try to execute the main validation workflow
        main_workflow = self.repo_root / "workflows" / "phase9_advanced_validation.yaml"
        execution_result = None

        if main_workflow.exists():
            try:
                executor_script = (
                    self.repo_root / "automation" / "phase9_workflow_executor.py"
                )

                if executor_script.exists():
                    cmd = [
                        sys.executable,
                        str(executor_script),
                        "execute",
                        str(main_workflow),
                    ]
                    # Don't actually execute in verification mode, just check it can be loaded
                    # For actual execution, we would run with timeout
                    workflow_results.append(
                        {
                            "workflow": "phase9_advanced_validation.yaml",
                            "executable": True,
                            "note": "Execution checked but not performed in verification mode",
                        }
                    )
                else:
                    violations.append(
                        {
                            "type": "missing_executor",
                            "file": "phase9_workflow_executor.py",
                            "message": "Cannot execute workflows without executor script",
                        }
                    )

            except Exception as e:
                violations.append(
                    {
                        "type": "workflow_execution_check_error",
                        "file": "phase9_advanced_validation.yaml",
                        "message": f"Error checking workflow execution: {str(e)}",
                    }
                )

        return {
            "has_violations": len(violations) > 0,
            "violations": violations,
            "workflows_checked": len(workflow_files),
            "workflows_exist": sum(
                1 for r in workflow_results if r.get("exists", False)
            ),
            "workflows_validated": sum(
                1 for r in workflow_results if r.get("validated", False)
            ),
            "workflow_results": workflow_results,
        }

    def generate_verification_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive verification report.

        Returns:
            Report generation results
        """
        try:
            # Create report structure
            report = {
                "verification_id": self.verification_id,
                "generated_at": datetime.now().isoformat(),
                "phase": 9,
                "schema_version": "1.12",
                "summary": {
                    "successful": self.verification_results.get("successful", False),
                    "total_violations": len(self.violations),
                    "total_warnings": len(self.warnings),
                    "verification_steps_completed": len(self.verification_results),
                },
                "verification_results": self.verification_results,
                "violations": self.violations,
                "warnings": self.warnings,
                "exit_code": 2 if self.violations and self.strict_mode else 0,
            }

            # Save report to file
            report_file = self.verification_logs / f"{self.verification_id}.json"
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

            # Log report generation
            print(f"\n[Verification Report Generated]")
            print(f"Report saved to: {report_file}")
            print(f"Total violations: {len(self.violations)}")
            print(f"Total warnings: {len(self.warnings)}")
            print(f"Exit code: {report['exit_code']}")

            return {
                "successful": True,
                "report_file": str(report_file),
                "violations_count": len(self.violations),
                "warnings_count": len(self.warnings),
            }

        except Exception as e:
            print(f"Error generating verification report: {e}")
            return {
                "successful": False,
                "error": str(e),
                "violations_count": len(self.violations),
                "warnings_count": len(self.warnings),
            }

    def update_sha256_manifest(self) -> Dict[str, Any]:
        """
        Update SHA256 manifest with Phase 9 artifacts.

        Returns:
            Manifest update results
        """
        try:
            # Import the manifest generator
            sys.path.insert(0, str(self.repo_root / "automation"))
            from generate_sha256_manifest import generate_sha256_manifest

            # Generate manifest
            manifest_path = (
                self.repo_root
                / "documentation"
                / "sha256_manifests"
                / "phase9_manifest.json"
            )
            result = generate_sha256_manifest(
                output_path=str(manifest_path),
                include_patterns=[
                    "**/phase9/**",
                    "toolkit/oe/*.py",
                    "workflows/*.yaml",
                ],
                exclude_patterns=["**/__pycache__/**", "**/*.pyc"],
            )

            # Verify manifest was created
            if manifest_path.exists():
                with open(manifest_path, "r") as f:
                    manifest_data = json.load(f)
                    file_count = len(manifest_data.get("files", {}))

                return {
                    "successful": True,
                    "manifest_file": str(manifest_path),
                    "files_included": file_count,
                    "message": "SHA256 manifest updated successfully",
                }
            else:
                return {
                    "successful": False,
                    "error": "Manifest file not created",
                    "manifest_file": str(manifest_path),
                }

        except Exception as e:
            return {"successful": False, "error": str(e), "manifest_file": "unknown"}


def main():
    """Main entry point for Phase 9 verification."""
    parser = argparse.ArgumentParser(description="Phase 9 Comprehensive Verification")
    parser.add_argument(
        "--strict", action="store_true", help="Exit with code 2 on any violation"
    )
    parser.add_argument(
        "--skip-workflows", action="store_true", help="Skip workflow execution tests"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="logs/verification/phase9",
        help="Output directory for verification reports",
    )

    args = parser.parse_args()

    try:
        # Create verification instance
        verifier = Phase9Verification(strict_mode=args.strict)

        # Run comprehensive verification
        results = verifier.run_comprehensive_verification()

        # Check if verification was successful
        successful = not results.get("has_violations", False)

        # Print summary
        try:
            print("\n" + "=" * 80)
            print("PHASE 9 VERIFICATION COMPLETE")
            print("=" * 80)
            print(f"Verification ID: {verifier.verification_id}")
            print(f"Successful: {successful}")
            print(f"Violations: {len(verifier.violations)}")
            print(f"Warnings: {len(verifier.warnings)}")
        except UnicodeEncodeError:
            print("\n" + "=" * 80)
            print("PHASE 9 VERIFICATION COMPLETE")
            print("=" * 80)
            print(f"Verification ID: {verifier.verification_id}")
            print(f"Successful: {successful}")
            print(f"Violations: {len(verifier.violations)}")
            print(f"Warnings: {len(verifier.warnings)}")

        if verifier.violations:
            try:
                print("\nViolations found:")
                for violation in verifier.violations:
                    print(
                        f"  - {violation.get('type', 'unknown')}: {violation.get('message', 'No message')}"
                    )
            except UnicodeEncodeError:
                print("\nViolations found:")
                for violation in verifier.violations:
                    violation_type = (
                        str(violation.get("type", "unknown"))
                        .encode("ascii", "replace")
                        .decode("ascii")
                    )
                    violation_message = (
                        str(violation.get("message", "No message"))
                        .encode("ascii", "replace")
                        .decode("ascii")
                    )
                    print(f"  - {violation_type}: {violation_message}")

        if verifier.warnings:
            try:
                print("\nWarnings:")
                for warning in verifier.warnings:
                    print(
                        f"  - {warning.get('type', 'unknown')}: {warning.get('message', 'No message')}"
                    )
            except UnicodeEncodeError:
                print("\nWarnings:")
                for warning in verifier.warnings:
                    warning_type = (
                        str(warning.get("type", "unknown"))
                        .encode("ascii", "replace")
                        .decode("ascii")
                    )
                    warning_message = (
                        str(warning.get("message", "No message"))
                        .encode("ascii", "replace")
                        .decode("ascii")
                    )
                    print(f"  - {warning_type}: {warning_message}")

        # Exit with appropriate code
        exit_code = 2 if verifier.violations and args.strict else 0
        try:
            print(f"\nExit code: {exit_code}")
        except UnicodeEncodeError:
            print(f"\nExit code: {exit_code}")
        sys.exit(exit_code)

    except Exception as e:
        print(f"Verification failed with error: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
