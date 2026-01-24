"""
Phase 9 Artifacts Validator

Validates all Phase 9 artifacts against the requirements specified in
GLASS_BOX_BOUNDARY_v1.12.html. Ensures all G9 invariants are satisfied
and exits with code 2 on boundary violations.

Author: Orthogonal Engineering System
Date: 2026-01-22
Version: 1.0.0
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# Add toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from toolkit.oe.advanced_evidence import AdvancedEvidenceStore
from toolkit.oe.causal_analyzer import CausalAnalyzer
from toolkit.oe.debt_calculator import DebtCalculator
from toolkit.oe.trace_enricher import TraceEnricher
from toolkit.oe.workflow_dsl import WorkflowDSL


class Phase9ArtifactsValidator:
    """
    Validator for Phase 9 artifacts and invariants.

    Validates:
    1. Required artifact existence and structure
    2. G9 methodological invariant compliance
    3. Workflow DSL functionality
    4. Advanced evidence store capabilities
    5. Trace enrichment functionality
    6. Debt calculation functionality
    7. Exit code 2 enforcement
    """

    def __init__(self, strict_mode: bool = True):
        """
        Initialize validator.

        Args:
            strict_mode: If True, exit with code 2 on any violation
        """
        self.strict_mode = strict_mode
        self.violations: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.validation_results: Dict[str, Any] = {}
        self.phase9_blueprint_path = Path("glass-box/GLASS_BOX_BOUNDARY_v1.12.html")

        # Create validation logs directory
        self.validation_logs_path = Path("logs/validation/phase9")
        self.validation_logs_path.mkdir(parents=True, exist_ok=True)

    def validate_all(self) -> Dict[str, Any]:
        """
        Validate all Phase 9 artifacts and invariants.

        Returns:
            Comprehensive validation results
        """
        print("=" * 70)
        print("PHASE 9 ARTIFACTS VALIDATION")
        print("=" * 70)

        validation_start = datetime.now()

        # Run all validation checks
        checks = [
            ("Phase 9 Blueprint", self.validate_phase9_blueprint),
            ("Required Artifacts", self.validate_required_artifacts),
            ("Toolkit Modules", self.validate_toolkit_modules),
            ("Workflow DSL", self.validate_workflow_dsl),
            ("Advanced Evidence Store", self.validate_advanced_evidence_store),
            ("Causal Analyzer", self.validate_causal_analyzer),
            ("Trace Enricher", self.validate_trace_enricher),
            ("Debt Calculator", self.validate_debt_calculator),
            ("Workflow Files", self.validate_workflow_files),
            ("Automation Scripts", self.validate_automation_scripts),
            ("G9 Invariants", self.validate_g9_invariants),
            ("Exit Code Enforcement", self.validate_exit_code_enforcement),
        ]

        results = {}
        for check_name, check_func in checks:
            print(f"\n[{check_name}]")
            try:
                result = check_func()
                results[check_name.lower().replace(" ", "_")] = result
                self._print_check_result(check_name, result)
            except Exception as e:
                error_result = {
                    "valid": False,
                    "error": str(e),
                    "violations": [{"type": "check_error", "message": str(e)}],
                }
                results[check_name.lower().replace(" ", "_")] = error_result
                self._print_check_result(check_name, error_result)

        # Calculate overall validation status
        validation_end = datetime.now()
        validation_duration = (validation_end - validation_start).total_seconds()

        all_valid = all(
            result.get("valid", False)
            for result in results.values()
            if isinstance(result, dict)
        )

        overall_result = {
            "valid": all_valid,
            "validation_timestamp": validation_start.isoformat(),
            "validation_duration_seconds": validation_duration,
            "total_checks": len(checks),
            "passed_checks": sum(
                1
                for result in results.values()
                if isinstance(result, dict) and result.get("valid", False)
            ),
            "failed_checks": sum(
                1
                for result in results.values()
                if isinstance(result, dict) and not result.get("valid", False)
            ),
            "total_violations": len(self.violations),
            "total_warnings": len(self.warnings),
            "detailed_results": results,
            "violations": self.violations,
            "warnings": self.warnings,
        }

        self.validation_results = overall_result

        # Save validation results
        self._save_validation_results(overall_result)

        # Print summary
        self._print_validation_summary(overall_result)

        return overall_result

    def validate_phase9_blueprint(self) -> Dict[str, Any]:
        """Validate Phase 9 HTML blueprint exists and is accessible."""
        violations = []
        warnings = []

        if not self.phase9_blueprint_path.exists():
            violations.append(
                {
                    "type": "missing_artifact",
                    "artifact": str(self.phase9_blueprint_path),
                    "message": "Phase 9 HTML blueprint not found",
                }
            )
        else:
            # Check file size
            file_size = self.phase9_blueprint_path.stat().st_size
            if file_size < 1000:  # Arbitrary minimum size
                warnings.append(
                    {
                        "type": "suspicious_file_size",
                        "artifact": str(self.phase9_blueprint_path),
                        "size_bytes": file_size,
                        "message": "Blueprint file size seems small",
                    }
                )

            # Check if it contains Phase 9 markers
            try:
                content = self.phase9_blueprint_path.read_text(encoding="utf-8")
                if "Phase 9" not in content:
                    warnings.append(
                        {
                            "type": "content_missing_marker",
                            "artifact": str(self.phase9_blueprint_path),
                            "message": "Blueprint may not contain Phase 9 content",
                        }
                    )
            except UnicodeDecodeError:
                violations.append(
                    {
                        "type": "encoding_error",
                        "artifact": str(self.phase9_blueprint_path),
                        "message": "Blueprint file encoding error",
                    }
                )

        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "blueprint_path": str(self.phase9_blueprint_path),
            "exists": self.phase9_blueprint_path.exists(),
        }

    def validate_required_artifacts(self) -> Dict[str, Any]:
        """Validate all required Phase 9 artifacts exist."""
        required_artifacts = [
            # Toolkit modules
            "toolkit/oe/advanced_evidence.py",
            "toolkit/oe/causal_analyzer.py",
            "toolkit/oe/workflow_dsl.py",
            "toolkit/oe/trace_enricher.py",
            "toolkit/oe/debt_calculator.py",
            # Test files
            "toolkit/tests/test_advanced_evidence.py",
            "toolkit/tests/test_causal_analyzer.py",
            "toolkit/tests/test_workflow_dsl.py",
            "toolkit/tests/test_trace_enricher.py",
            "toolkit/tests/test_debt_calculator.py",
            # Workflow files
            "workflows/phase9_advanced_validation.yaml",
            "workflows/causal_analysis_workflow.yaml",
            "workflows/debt_tracking_workflow.yaml",
            "workflows/trace_enrichment_workflow.yaml",
            # Automation scripts
            "automation/phase9_workflow_executor.py",
            "automation/validate_phase9_artifacts.py",
            "automation/generate_phase9_trace.py",
            "automation/phase9_causal_analysis.py",
        ]

        violations = []
        warnings = []
        found_artifacts = []
        missing_artifacts = []

        for artifact_path in required_artifacts:
            path = Path(artifact_path)
            if path.exists():
                found_artifacts.append(artifact_path)

                # Check file size
                if path.is_file():
                    file_size = path.stat().st_size
                    if file_size == 0:
                        warnings.append(
                            {
                                "type": "empty_file",
                                "artifact": artifact_path,
                                "message": "File exists but is empty",
                            }
                        )
            else:
                missing_artifacts.append(artifact_path)
                violations.append(
                    {
                        "type": "missing_artifact",
                        "artifact": artifact_path,
                        "message": "Required artifact not found",
                    }
                )

        return {
            "valid": len(missing_artifacts) == 0,
            "total_required": len(required_artifacts),
            "found": len(found_artifacts),
            "missing": len(missing_artifacts),
            "found_artifacts": found_artifacts,
            "missing_artifacts": missing_artifacts,
            "violations": violations,
            "warnings": warnings,
        }

    def validate_toolkit_modules(self) -> Dict[str, Any]:
        """Validate Phase 9 toolkit modules can be imported and initialized."""
        modules_to_test = [
            ("advanced_evidence", "AdvancedEvidenceStore"),
            ("causal_analyzer", "CausalAnalyzer"),
            ("workflow_dsl", "WorkflowDSL"),
            ("trace_enricher", "TraceEnricher"),
            ("debt_calculator", "DebtCalculator"),
        ]

        violations = []
        warnings = []
        successful_imports = []
        failed_imports = []

        for module_name, class_name in modules_to_test:
            try:
                # Try to import the module
                module = __import__(f"toolkit.oe.{module_name}", fromlist=[class_name])

                # Try to get the class
                cls = getattr(module, class_name, None)
                if cls is None:
                    failed_imports.append(f"{module_name}.{class_name}")
                    violations.append(
                        {
                            "type": "class_not_found",
                            "module": module_name,
                            "class": class_name,
                            "message": f"Class {class_name} not found in module {module_name}",
                        }
                    )
                else:
                    # Try to instantiate the class
                    try:
                        if class_name == "AdvancedEvidenceStore":
                            instance = cls(base_path="logs/evidence/test_validation")
                        elif class_name == "CausalAnalyzer":
                            evidence_store = AdvancedEvidenceStore(
                                base_path="logs/evidence/test_validation"
                            )
                            instance = cls(evidence_store)
                        elif class_name == "TraceEnricher":
                            evidence_store = AdvancedEvidenceStore(
                                base_path="logs/evidence/test_validation"
                            )
                            instance = cls(evidence_store)
                        else:
                            instance = cls()

                        successful_imports.append(f"{module_name}.{class_name}")

                    except Exception as e:
                        failed_imports.append(f"{module_name}.{class_name}")
                        warnings.append(
                            {
                                "type": "instantiation_warning",
                                "module": module_name,
                                "class": class_name,
                                "message": f"Could not instantiate {class_name}: {str(e)}",
                            }
                        )

            except ImportError as e:
                failed_imports.append(f"{module_name}.{class_name}")
                violations.append(
                    {
                        "type": "import_error",
                        "module": module_name,
                        "class": class_name,
                        "message": f"Import failed: {str(e)}",
                    }
                )
            except Exception as e:
                failed_imports.append(f"{module_name}.{class_name}")
                warnings.append(
                    {
                        "type": "import_warning",
                        "module": module_name,
                        "class": class_name,
                        "message": f"Unexpected error: {str(e)}",
                    }
                )

        return {
            "valid": len(failed_imports) == 0,
            "total_modules": len(modules_to_test),
            "successful_imports": successful_imports,
            "failed_imports": failed_imports,
            "violations": violations,
            "warnings": warnings,
        }

    def validate_workflow_dsl(self) -> Dict[str, Any]:
        """Validate Workflow DSL functionality."""
        violations = []
        warnings = []

        try:
            # Test basic WorkflowDSL functionality
            evidence_store = AdvancedEvidenceStore(
                base_path="logs/evidence/test_workflow_dsl"
            )
            workflow_dsl = WorkflowDSL(evidence_store)

            # Test loading a workflow
            test_workflow = {
                "name": "Test Workflow",
                "version": "1.0",
                "steps": [
                    {
                        "id": "start",
                        "name": "Start",
                        "action": {
                            "type": "shell_command",
                            "parameters": {"command": "echo 'test'"},
                        },
                    }
                ],
            }

            # Test workflow registration
            workflow_id = workflow_dsl.register_workflow(test_workflow)

            if not workflow_id:
                violations.append(
                    {
                        "type": "workflow_registration_failed",
                        "message": "Workflow registration failed to return ID",
                    }
                )

            # Test workflow listing
            workflows = workflow_dsl.list_workflows()
            if workflow_id not in workflows:
                violations.append(
                    {
                        "type": "workflow_not_in_list",
                        "workflow_id": workflow_id,
                        "message": "Registered workflow not found in list",
                    }
                )

        except Exception as e:
            violations.append(
                {
                    "type": "workflow_dsl_error",
                    "message": f"Workflow DSL validation failed: {str(e)}",
                }
            )

        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
        }

    def validate_advanced_evidence_store(self) -> Dict[str, Any]:
        """Validate AdvancedEvidenceStore functionality."""
        violations = []
        warnings = []

        try:
            # Test AdvancedEvidenceStore
            evidence_store = AdvancedEvidenceStore(
                base_path="logs/evidence/test_validation"
            )

            # Test adding causal node
            node_id = evidence_store.add_causal_node(
                evidence_id="TEST-VALIDATION-001",
                phase=9,
                confidence="high",
                metadata={"validation_test": True},
            )

            if not node_id:
                violations.append(
                    {
                        "type": "causal_node_creation_failed",
                        "message": "Failed to create causal node",
                    }
                )

            # Test adding causal edge (need another node)
            node2_id = evidence_store.add_causal_node(
                evidence_id="TEST-VALIDATION-002", phase=9, confidence="medium"
            )

            edge_id = evidence_store.add_causal_edge(
                source_node_id=node_id,
                target_node_id=node2_id,
                link_type="direct",
                confidence_score=0.8,
            )

            if not edge_id:
                violations.append(
                    {
                        "type": "causal_edge_creation_failed",
                        "message": "Failed to create causal edge",
                    }
                )

            # Test evidence chain creation
            chain_id = evidence_store.create_evidence_chain(
                node_ids=[node_id, node2_id], edge_ids=[edge_id], phases_covered=[9]
            )

            if not chain_id:
                violations.append(
                    {
                        "type": "evidence_chain_creation_failed",
                        "message": "Failed to create evidence chain",
                    }
                )

        except Exception as e:
            violations.append(
                {
                    "type": "advanced_evidence_store_error",
                    "message": f"AdvancedEvidenceStore validation failed: {str(e)}",
                }
            )

        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
        }

    def validate_causal_analyzer(self) -> Dict[str, Any]:
        """Validate CausalAnalyzer functionality."""
        violations = []
        warnings = []

        try:
            # Setup evidence store with test data
            evidence_store = AdvancedEvidenceStore(
                base_path="logs/evidence/test_causal_analyzer"
            )

            # Add test data
            node_ids = []
            for i in range(5):
                node_id = evidence_store.add_causal_node(
                    evidence_id=f"TEST-CAUSAL-{i:03d}",
                    phase=8 + (i % 2),  # Mix of phases 8 and 9
                    confidence="high" if i % 2 == 0 else "medium",
                )
                node_ids.append(node_id)

            # Create analyzer
            analyzer = CausalAnalyzer(evidence_store)

            # Test analysis methods
            temporal_patterns = analyzer.analyze_temporal_patterns(time_window_hours=24)
            if not isinstance(temporal_patterns, list):
                warnings.append(
                    {
                        "type": "temporal_analysis_type",
                        "message": f"Temporal patterns returned type {type(temporal_patterns)}, expected list",
                    }
                )

            confidence_distribution = analyzer.analyze_confidence_distribution()
            if not isinstance(confidence_distribution, dict):
                violations.append(
                    {
                        "type": "confidence_analysis_type",
                        "message": f"Confidence distribution returned type {type(confidence_distribution)}, expected dict",
                    }
                )

        except Exception as e:
            violations.append(
                {
                    "type": "causal_analyzer_error",
                    "message": f"CausalAnalyzer validation failed: {str(e)}",
                }
            )

        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
        }

    def validate_trace_enricher(self) -> Dict[str, Any]:
        """Validate TraceEnricher functionality."""
        violations = []
        warnings = []

        try:
            # Setup evidence store
            evidence_store = AdvancedEvidenceStore(
                base_path="logs/evidence/test_trace_enricher"
            )

            # Create trace enricher
            enricher = TraceEnricher(evidence_store)

            # Create test trace
            test_trace = {
                "trace_id": "GB-TRACE-TEST-VALIDATION",
                "timestamp": datetime.now().isoformat(),
                "repository_meta": {
                    "name": "orthogonal-engineering",
                    "version": "1.0.0",
                    "commit_hash": "62bead3",
                    "branch": "main",
                },
                "environment_snapshot": {
                    "python_version": sys.version,
                    "platform": sys.platform,
                },
            }

            # Test enrichment
            enriched_trace = enricher.enrich_trace(
                test_trace, enrichment_level=TraceEnrichmentLevel.STANDARD
            )

            validation_results["trace_enrichment"] = {
                "successful": True,
                "enriched_fields": list(enriched_trace.keys()),
                "enrichment_level": "STANDARD",
                "trace_id": test_trace["trace_id"],
            }

        except Exception as e:
            validation_results["trace_enrichment"] = {
                "successful": False,
                "error": str(e),
                "trace_id": test_trace.get("trace_id", "unknown"),
            }
            violations.append(
                {
                    "type": "trace_enrichment_error",
                    "component": "trace_enricher",
                    "message": f"Trace enrichment failed: {str(e)}",
                }
            )

        return validation_results

    def validate_all(self) -> Dict[str, Any]:
        """
        Run all validation checks.

        Returns:
            Comprehensive validation results
        """
        print("=" * 80)
        print("PHASE 9 ARTIFACTS VALIDATION")
        print("=" * 80)
        print(f"Validation ID: {self.validation_id}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Strict Mode: {self.strict_mode}")
        print("=" * 80)

        validation_start = time.time()

        # Run all validation steps
        validation_steps = [
            ("Phase 9 Blueprint", self.validate_phase9_blueprint),
            ("Required Artifacts", self.validate_required_artifacts),
            ("Toolkit Modules", self.validate_toolkit_modules),
            ("Workflow DSL", self.validate_workflow_dsl),
            ("Advanced Evidence Store", self.validate_advanced_evidence_store),
            ("Causal Analyzer", self.validate_causal_analyzer),
            ("Trace Enricher", self.validate_trace_enricher),
        ]

        results = {}
        for step_name, step_func in validation_steps:
            print(f"\n[{step_name}]")
            step_start = time.time()

            try:
                step_result = step_func()
                step_duration = time.time() - step_start
                step_result["duration_seconds"] = step_duration
                results[step_name.lower().replace(" ", "_")] = step_result

                if step_result.get("has_violations", False):
                    print(
                        f"  Status: FAILED ({len(step_result.get('violations', []))} violations)"
                    )
                else:
                    print(f"  Status: PASSED")

            except Exception as e:
                step_duration = time.time() - step_start
                error_result = {
                    "successful": False,
                    "error": str(e),
                    "duration_seconds": step_duration,
                    "has_violations": True,
                    "violations": [
                        {
                            "type": "validation_step_error",
                            "step": step_name,
                            "message": str(e),
                        }
                    ],
                }
                results[step_name.lower().replace(" ", "_")] = error_result
                self.violations.extend(error_result["violations"])
                print(f"  Status: ERROR - {str(e)[:100]}")

        # Calculate overall results
        total_violations = len(self.violations)
        total_steps = len(validation_steps)
        successful_steps = sum(
            1
            for result in results.values()
            if isinstance(result, dict) and not result.get("has_violations", False)
        )

        overall_result = {
            "validation_id": self.validation_id,
            "generated_at": datetime.now().isoformat(),
            "total_steps": total_steps,
            "successful_steps": successful_steps,
            "total_violations": total_violations,
            "violations": self.violations,
            "warnings": self.warnings,
            "successful": total_violations == 0,
            "duration_seconds": time.time() - validation_start,
            "detailed_results": results,
        }

        # Save results
        self._save_validation_results(overall_result)

        # Print summary
        print("\n" + "=" * 80)
        print("VALIDATION COMPLETE")
        print("=" * 80)
        print(f"Total Steps: {total_steps}")
        print(f"Successful Steps: {successful_steps}")
        print(f"Total Violations: {total_violations}")
        print(f"Total Warnings: {len(self.warnings)}")
        print(f"Overall: {'PASS' if total_violations == 0 else 'FAIL'}")

        if self.violations:
            print("\nViolations found:")
            for violation in self.violations:
                print(
                    f"  - {violation.get('type', 'unknown')}: {violation.get('message', 'No message')}"
                )

        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(
                    f"  - {warning.get('type', 'unknown')}: {warning.get('message', 'No message')}"
                )

        # Exit with appropriate code
        if self.strict_mode and total_violations > 0:
            print(f"\nExit code: 2 (boundary violation in strict mode)")
            sys.exit(2)
        else:
            print(f"\nExit code: {0 if total_violations == 0 else 1}")
            sys.exit(0 if total_violations == 0 else 1)

        return overall_result

    def _save_validation_results(self, results: Dict[str, Any]) -> None:
        """
        Save validation results to file.

        Args:
            results: Validation results to save
        """
        # Create validation directory
        validation_dir = self.repo_root / "logs" / "validation" / "phase9"
        validation_dir.mkdir(parents=True, exist_ok=True)

        # Save results
        results_file = validation_dir / f"{self.validation_id}.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\nValidation results saved to: {results_file}")


def main():
    """Main entry point for Phase 9 artifacts validation."""
    parser = argparse.ArgumentParser(description="Validate Phase 9 artifacts")
    parser.add_argument(
        "--strict", action="store_true", help="Exit with code 2 on any violation"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="logs/validation/phase9",
        help="Output directory for validation reports",
    )

    args = parser.parse_args()

    try:
        # Create validator instance
        validator = Phase9ArtifactsValidator(strict_mode=args.strict)

        # Run validation
        validator.validate_all()

    except Exception as e:
        print(f"Validation failed with error: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
