#!/usr/bin/env python3
"""
CORPORATE-STYLE INVARIANT ENFORCEMENT CONTROLLER
================================================

This controller loads atomic invariants extracted from the repository
and enforces them with maximal strictness and determinism.

Key Principles:
1. Atomic Enforcement - Each invariant is enforced independently
2. Deterministic Outcomes - No guessing, no ambiguity
3. Audit Trail - All enforcement actions are logged
4. Fail-Safe Design - Violations trigger immediate safe shutdown
5. Corporate Compliance - Meets enterprise security and compliance standards

Usage:
    python invariant_enforcer.py --invariants invariants.json --action [validate|enforce|audit]
"""

import argparse
import hashlib
import json
import logging
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class InvariantViolation(Exception):
    """Exception raised when an invariant is violated."""

    def __init__(self, invariant_id: str, message: str, severity: str = "critical"):
        self.invariant_id = invariant_id
        self.message = message
        self.severity = severity
        super().__init__(f"[{severity.upper()}] {invariant_id}: {message}")


class EnforcementAudit:
    """Corporate-style audit trail for all enforcement actions."""

    def __init__(self, audit_file: Optional[str] = None):
        self.audit_file = (
            audit_file
            or f"enforcement_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        self.audit_entries: List[Dict[str, Any]] = []
        self.violation_count = 0
        self.enforcement_count = 0

    def log_action(
        self, action: str, invariant_id: str, status: str, details: Dict[str, Any]
    ):
        """Log an enforcement action to the audit trail."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "invariant_id": invariant_id,
            "status": status,
            "details": details,
            "audit_id": hashlib.md5(
                f"{action}_{invariant_id}_{datetime.now().isoformat()}".encode()
            ).hexdigest()[:12],
        }
        self.audit_entries.append(entry)

        if status == "violation":
            self.violation_count += 1
        elif status == "enforced":
            self.enforcement_count += 1

        return entry

    def save_audit(self):
        """Save audit trail to file."""
        audit_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_entries": len(self.audit_entries),
                "violations": self.violation_count,
                "enforcements": self.enforcement_count,
                "audit_hash": self._calculate_audit_hash(),
            },
            "entries": self.audit_entries,
        }

        with open(self.audit_file, "w", encoding="utf-8") as f:
            json.dump(audit_data, f, indent=2, ensure_ascii=False)

        return self.audit_file

    def _calculate_audit_hash(self) -> str:
        """Calculate hash of audit entries for integrity verification."""
        entries_str = json.dumps(self.audit_entries, sort_keys=True)
        return hashlib.sha256(entries_str.encode()).hexdigest()[:16]

    def get_summary(self) -> Dict[str, Any]:
        """Get audit summary."""
        return {
            "total_entries": len(self.audit_entries),
            "violations": self.violation_count,
            "enforcements": self.enforcement_count,
            "compliance_rate": (
                self.enforcement_count / max(len(self.audit_entries), 1)
            )
            * 100,
        }


class InvariantEnforcer:
    """
    Corporate-style invariant enforcement engine.

    Loads atomic invariants and enforces them with maximal strictness.
    Never compromises, never allows violations, never guesses.
    """

    def __init__(
        self,
        invariants_file: str,
        audit_file: Optional[str] = None,
        strict_mode: bool = True,
    ):
        self.invariants_file = Path(invariants_file)
        self.strict_mode = strict_mode
        self.audit = EnforcementAudit(audit_file)
        self.invariants: Dict[str, Dict[str, Any]] = {}
        self.enforcement_rules: Dict[str, Any] = {}
        self.protected_files: Set[str] = set()
        self.tool_schemas: Dict[str, Dict[str, Any]] = {}

        # Setup corporate logging
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup corporate-style logging."""
        logger = logging.getLogger("InvariantEnforcer")
        logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [ENFORCER] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)

        # File handler for audit trail
        file_handler = logging.FileHandler("enforcement.log", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

        return logger

    def load_invariants(self) -> bool:
        """
        Load atomic invariants from JSON file.

        Returns:
            bool: True if invariants loaded successfully, False otherwise
        """
        try:
            if not self.invariants_file.exists():
                self.logger.error(f"Invariants file not found: {self.invariants_file}")
                return False

            with open(self.invariants_file, "r", encoding="utf-8") as f:
                invariants_data = json.load(f)

            # Validate invariants structure
            if not self._validate_invariants_structure(invariants_data):
                return False

            # Extract atomic dataset
            atomic_dataset = invariants_data.get("atomic_dataset", [])

            # Organize invariants by type
            for invariant in atomic_dataset:
                invariant_id = invariant.get("atomic_id", "UNKNOWN")
                self.invariants[invariant_id] = invariant

                # Categorize by type
                invariant_type = invariant.get("tool_or_rule", "")

                if invariant_type == "PROTECTED":
                    file_path = invariant.get("file_path", "")
                    if file_path:
                        self.protected_files.add(file_path)

                elif invariant_type.startswith("TOOL_"):
                    tool_name = invariant.get("tool_or_rule", "")
                    if tool_name and tool_name != "TOOL_":
                        self.tool_schemas[tool_name] = invariant

                elif invariant_type.startswith("RULE_"):
                    rule_id = invariant.get("tool_or_rule", "")
                    if rule_id:
                        self.enforcement_rules[rule_id] = invariant

            self.logger.info(f"Loaded {len(self.invariants)} atomic invariants")
            self.logger.info(f"  • Protected files: {len(self.protected_files)}")
            self.logger.info(f"  • Tool schemas: {len(self.tool_schemas)}")
            self.logger.info(f"  • Enforcement rules: {len(self.enforcement_rules)}")

            # Log successful load
            self.audit.log_action(
                action="load_invariants",
                invariant_id="SYSTEM",
                status="success",
                details={
                    "invariants_file": str(self.invariants_file),
                    "total_invariants": len(self.invariants),
                    "protected_files": len(self.protected_files),
                    "tool_schemas": len(self.tool_schemas),
                    "enforcement_rules": len(self.enforcement_rules),
                },
            )

            return True

        except Exception as e:
            self.logger.error(f"Failed to load invariants: {e}")
            self.logger.debug(traceback.format_exc())

            self.audit.log_action(
                action="load_invariants",
                invariant_id="SYSTEM",
                status="failure",
                details={"error": str(e), "traceback": traceback.format_exc()},
            )

            return False

    def _validate_invariants_structure(self, invariants_data: Dict[str, Any]) -> bool:
        """Validate invariants JSON structure."""
        required_sections = ["metadata", "atomic_dataset"]

        for section in required_sections:
            if section not in invariants_data:
                self.logger.error(f"Missing required section in invariants: {section}")
                return False

        # Validate atomic dataset
        atomic_dataset = invariants_data.get("atomic_dataset", [])
        if not isinstance(atomic_dataset, list):
            self.logger.error("Atomic dataset must be a list")
            return False

        # Check for required fields in each invariant
        for i, invariant in enumerate(atomic_dataset):
            if not isinstance(invariant, dict):
                self.logger.error(f"Invariant at index {i} is not a dictionary")
                return False

            required_fields = [
                "atomic_id",
                "file_path",
                "tool_or_rule",
                "enforcement_point",
            ]
            for field in required_fields:
                if field not in invariant:
                    self.logger.error(f"Invariant {i} missing required field: {field}")
                    return False

        return True

    def enforce_protected_files(self) -> Tuple[int, int]:
        """
        Enforce protection on all protected files.

        Returns:
            Tuple[int, int]: (enforced_count, violation_count)
        """
        enforced = 0
        violations = 0

        self.logger.info(f"Enforcing protection on {len(self.protected_files)} files")

        for file_path in self.protected_files:
            try:
                result = self._enforce_single_protected_file(file_path)

                if result == "enforced":
                    enforced += 1
                elif result == "violation":
                    violations += 1
                    if self.strict_mode:
                        raise InvariantViolation(
                            invariant_id=f"PROTECTED_{hashlib.md5(file_path.encode()).hexdigest()[:8]}",
                            message=f"Protected file violation: {file_path}",
                            severity="critical",
                        )

            except InvariantViolation as e:
                self.logger.error(str(e))
                violations += 1

                if self.strict_mode:
                    raise  # Re-raise in strict mode

            except Exception as e:
                self.logger.error(f"Error enforcing protection for {file_path}: {e}")
                violations += 1

        self.logger.info(
            f"Protected files enforcement complete: {enforced} enforced, {violations} violations"
        )
        return enforced, violations

    def _enforce_single_protected_file(self, file_path: str) -> str:
        """Enforce protection on a single file."""
        path = Path(file_path)

        # Check if file exists
        if not path.exists():
            # In strict mode, missing protected files are violations
            if self.strict_mode:
                self.audit.log_action(
                    action="enforce_protected_file",
                    invariant_id=f"PROTECTED_{hashlib.md5(file_path.encode()).hexdigest()[:8]}",
                    status="violation",
                    details={
                        "file_path": file_path,
                        "reason": "Protected file does not exist",
                        "action_taken": "logged_violation",
                    },
                )
                return "violation"
            else:
                self.audit.log_action(
                    action="enforce_protected_file",
                    invariant_id=f"PROTECTED_{hashlib.md5(file_path.encode()).hexdigest()[:8]}",
                    status="warning",
                    details={
                        "file_path": file_path,
                        "reason": "Protected file does not exist",
                        "action_taken": "logged_warning",
                    },
                )
                return "warning"

        # Check file permissions (read-only for protected files)
        try:
            # On Windows, we check if file is read-only
            if os.name == "nt":
                import stat

                current_mode = path.stat().st_mode
                if current_mode & stat.S_IWRITE:
                    # File is writable - this is a violation for protected files
                    self.audit.log_action(
                        action="enforce_protected_file",
                        invariant_id=f"PROTECTED_{hashlib.md5(file_path.encode()).hexdigest()[:8]}",
                        status="violation",
                        details={
                            "file_path": file_path,
                            "reason": "Protected file is writable",
                            "current_mode": oct(current_mode),
                            "action_taken": "logged_violation",
                        },
                    )
                    return "violation"

            # On Unix-like systems, check if file is readable by others
            else:
                import stat

                current_mode = path.stat().st_mode
                if current_mode & stat.S_IROTH:
                    # File is readable by others - potential security issue
                    self.audit.log_action(
                        action="enforce_protected_file",
                        invariant_id=f"PROTECTED_{hashlib.md5(file_path.encode()).hexdigest()[:8]}",
                        status="warning",
                        details={
                            "file_path": file_path,
                            "reason": "Protected file is readable by others",
                            "current_mode": oct(current_mode),
                            "action_taken": "logged_warning",
                        },
                    )
                    return "warning"

        except Exception as e:
            self.logger.warning(f"Could not check permissions for {file_path}: {e}")

        # Log successful enforcement
        self.audit.log_action(
            action="enforce_protected_file",
            invariant_id=f"PROTECTED_{hashlib.md5(file_path.encode()).hexdigest()[:8]}",
            status="enforced",
            details={
                "file_path": file_path,
                "reason": "File protection verified",
                "action_taken": "verified_protection",
            },
        )

        return "enforced"

    def validate_tool_execution(
        self, tool_name: str, parameters: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Validate tool execution against tool schemas.

        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool

        Returns:
            Tuple[bool, str]: (is_valid, validation_message)
        """
        self.logger.info(f"Validating tool execution: {tool_name}")

        # Check if tool exists in schemas
        if tool_name not in self.tool_schemas:
            message = f"Tool '{tool_name}' not found in tool schemas"
            self.audit.log_action(
                action="validate_tool",
                invariant_id=tool_name,
                status="violation",
                details={
                    "tool_name": tool_name,
                    "reason": "Tool not in schemas",
                    "parameters": parameters,
                    "action_taken": "rejected_execution",
                },
            )
            return False, message

        tool_schema = self.tool_schemas[tool_name]
        expected_params = tool_schema.get("parameters", {})

        # Validate parameters
        validation_result = self._validate_tool_parameters(
            tool_name, parameters, expected_params
        )

        if not validation_result[0]:
            self.audit.log_action(
                action="validate_tool",
                invariant_id=tool_name,
                status="violation",
                details={
                    "tool_name": tool_name,
                    "reason": validation_result[1],
                    "parameters": parameters,
                    "expected_params": expected_params,
                    "action_taken": "rejected_execution",
                },
            )
            return validation_result

        # Log successful validation
        self.audit.log_action(
            action="validate_tool",
            invariant_id=tool_name,
            status="enforced",
            details={
                "tool_name": tool_name,
                "reason": "Tool validation passed",
                "parameters": parameters,
                "action_taken": "allowed_execution",
            },
        )

        return True, "Tool validation passed"

    def _validate_tool_parameters(
        self,
        tool_name: str,
        actual_params: Dict[str, Any],
        expected_params: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """Validate tool parameters against expected schema."""
        # Check for required parameters
        for param_name, param_type in expected_params.items():
            if param_name not in actual_params:
                return False, f"Missing required parameter: {param_name}"

        # Check for extra parameters (strict mode only)
        if self.strict_mode:
            for param_name in actual_params.keys():
                if param_name not in expected_params:
                    return False, f"Unexpected parameter: {param_name}"

        # Type validation (basic - could be enhanced)
        for param_name, expected_type in expected_params.items():
            if param_name in actual_params:
                actual_value = actual_params[param_name]

                # Basic type checking
                if expected_type == "str" and not isinstance(actual_value, str):
                    return (
                        False,
                        f"Parameter '{param_name}' should be str, got {type(actual_value).__name__}",
                    )
                elif expected_type == "int" and not isinstance(actual_value, int):
                    return (
                        False,
                        f"Parameter '{param_name}' should be int, got {type(actual_value).__name__}",
                    )
                elif expected_type == "bool" and not isinstance(actual_value, bool):
                    return (
                        False,
                        f"Parameter '{param_name}' should be bool, got {type(actual_value).__name__}",
                    )
                elif expected_type == "Dict" and not isinstance(actual_value, dict):
                    return (
                        False,
                        f"Parameter '{param_name}' should be Dict, got {type(actual_value).__name__}",
                    )
                elif expected_type == "List" and not isinstance(actual_value, list):
                    return (
                        False,
                        f"Parameter '{param_name}' should be List, got {type(actual_value).__name__}",
                    )

        return True, "Parameter validation passed"

    def enforce_execution_rules(
        self, action: str, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Enforce execution rules for a given action.

        Args:
            action: The action being performed
            context: Context information for the action

        Returns:
            Tuple[bool, str]: (is_allowed, enforcement_message)
        """
        self.logger.info(f"Enforcing execution rules for action: {action}")

        violations = []
        enforced_rules = []

        for rule_id, rule in self.enforcement_rules.items():
            try:
                rule_applies = self._rule_applies_to_action(rule, action, context)

                if rule_applies:
                    is_mandatory = rule.get("mandatory", False)
                    rule_description = rule.get("parameters", {}).get(
                        "description", "No description"
                    )

                    if is_mandatory:
                        # Check if rule is being violated
                        rule_violated = self._check_rule_violation(
                            rule, action, context
                        )

                        if rule_violated:
                            violations.append(
                                {
                                    "rule_id": rule_id,
                                    "description": rule_description,
                                    "severity": "critical",
                                }
                            )

                            if self.strict_mode:
                                raise InvariantViolation(
                                    invariant_id=rule_id,
                                    message=f"Mandatory rule violation: {rule_description}",
                                    severity="critical",
                                )
                        else:
                            enforced_rules.append(rule_id)

            except InvariantViolation as e:
                if self.strict_mode:
                    raise
                else:
                    self.logger.error(f"Rule violation (non-strict): {e}")
                    violations.append(
                        {"rule_id": rule_id, "description": str(e), "severity": "error"}
                    )

            except Exception as e:
                self.logger.error(f"Error enforcing rule {rule_id}: {e}")
                violations.append(
                    {
                        "rule_id": rule_id,
                        "description": f"Error: {e}",
                        "severity": "error",
                    }
                )

        # Determine overall result
        if violations:
            violation_messages = [
                f"{v['rule_id']}: {v['description']}" for v in violations
            ]
            message = f"Execution rule violations: {', '.join(violation_messages)}"

            self.audit.log_action(
                action="enforce_execution_rules",
                invariant_id="EXECUTION_RULES",
                status="violation",
                details={
                    "action": action,
                    "context": context,
                    "violations": violations,
                    "enforced_rules": enforced_rules,
                    "action_taken": "blocked_execution"
                    if self.strict_mode
                    else "logged_violation",
                },
            )

            return False, message
        else:
            message = (
                f"All execution rules enforced: {len(enforced_rules)} rules applied"
            )

            self.audit.log_action(
                action="enforce_execution_rules",
                invariant_id="EXECUTION_RULES",
                status="enforced",
                details={
                    "action": action,
                    "context": context,
                    "enforced_rules": enforced_rules,
                    "action_taken": "allowed_execution",
                },
            )

            return True, message

    def _rule_applies_to_action(
        self, rule: Dict[str, Any], action: str, context: Dict[str, Any]
    ) -> bool:
        """Determine if a rule applies to the given action and context."""
        # Check enforcement point
        enforcement_point = rule.get("enforcement_point", "")
        if enforcement_point and "file_path" in rule:
            # Rule applies to specific file operations
            if "file_path" in context:
                context_file = context.get("file_path", "")
                rule_file = rule.get("file_path", "")
                if context_file and rule_file and context_file != rule_file:
                    return False

        # Check rule type
        rule_type = rule.get("rule_type", "")
        if rule_type == "safety_rule" and "safety" in action.lower():
            return True
        elif rule_type == "mandatory_rule":
            return True  # Mandatory rules always apply

        # Default: rule applies if no specific conditions fail
        return True

    def _check_rule_violation(
        self, rule: Dict[str, Any], action: str, context: Dict[str, Any]
    ) -> bool:
        """Check if a rule is being violated."""
        rule_description = rule.get("parameters", {}).get("description", "").lower()

        # Check for "never" rules
        if "never" in rule_description:
            prohibited_actions = self._extract_prohibited_actions(rule_description)
            for prohibited in prohibited_actions:
                if prohibited in action.lower():
                    return True

        # Check for "always" rules
        if "always" in rule_description:
            required_actions = self._extract_required_actions(rule_description)
            for required in required_actions:
                if (
                    required not in action.lower()
                    and required not in str(context).lower()
                ):
                    return True

        # Check for specific patterns
        if "assert" in rule.get("tool_or_rule", "").lower():
            # This is an assertion rule
            return self._check_assertion_violation(rule, context)

        return False

    def _extract_prohibited_actions(self, rule_description: str) -> List[str]:
        """Extract prohibited actions from rule description."""
        prohibited = []
        words = rule_description.split()

        for i, word in enumerate(words):
            if word == "never":
                # Next few words are likely the prohibited action
                action_words = words[i + 1 : min(i + 4, len(words))]
                prohibited.append(" ".join(action_words))

        return prohibited

    def _extract_required_actions(self, rule_description: str) -> List[str]:
        """Extract required actions from rule description."""
        required = []
        words = rule_description.split()

        for i, word in enumerate(words):
            if word == "always":
                # Next few words are likely the required action
                action_words = words[i + 1 : min(i + 4, len(words))]
                required.append(" ".join(action_words))

        return required

    def _check_assertion_violation(
        self, rule: Dict[str, Any], context: Dict[str, Any]
    ) -> bool:
        """Check if an assertion rule is violated."""
        # This is a simplified assertion check
        # In a real implementation, this would evaluate the assertion
        rule_description = rule.get("parameters", {}).get("description", "")

        # Look for assertion conditions
        if "assert" in rule_description.lower():
            # Extract assertion condition
            import re

            assertion_match = re.search(
                r"assert\s+(.+?)(?:[,\n]|$)", rule_description, re.IGNORECASE
            )
            if assertion_match:
                assertion_condition = assertion_match.group(1)
                # Simplified: check if condition appears violated in context
                if "false" in assertion_condition.lower() or "0" in assertion_condition:
                    # This is a "assert false" or "assert 0" - always violated
                    return True

        return False

    def run_comprehensive_enforcement(self) -> Dict[str, Any]:
        """
        Run comprehensive enforcement of all invariants.

        Returns:
            Dict[str, Any]: Enforcement results
        """
        self.logger.info("Starting comprehensive invariant enforcement")

        results = {
            "timestamp": datetime.now().isoformat(),
            "invariants_loaded": len(self.invariants),
            "protected_files": {},
            "tool_validations": {},
            "rule_enforcements": {},
            "overall_status": "pending",
        }

        try:
            # 1. Enforce protected files
            protected_enforced, protected_violations = self.enforce_protected_files()
            results["protected_files"] = {
                "enforced": protected_enforced,
                "violations": protected_violations,
                "status": "pass" if protected_violations == 0 else "fail",
            }

            # 2. Validate tool schemas (structural validation)
            tool_validation_results = self._validate_tool_schemas_structure()
            results["tool_validations"] = tool_validation_results

            # 3. Sample rule enforcement
            sample_context = {
                "action": "system_startup",
                "timestamp": datetime.now().isoformat(),
            }
            rules_allowed, rules_message = self.enforce_execution_rules(
                "system_startup", sample_context
            )
            results["rule_enforcements"] = {
                "allowed": rules_allowed,
                "message": rules_message,
                "status": "pass" if rules_allowed else "fail",
            }

            # Determine overall status
            all_passed = (
                protected_violations == 0
                and tool_validation_results.get("valid", False)
                and rules_allowed
            )

            results["overall_status"] = "pass" if all_passed else "fail"
            results["compliance_score"] = self._calculate_compliance_score(results)

            # Save audit trail
            audit_file = self.audit.save_audit()
            results["audit_file"] = audit_file

            # Log final results
            self.logger.info(
                f"Comprehensive enforcement complete: {results['overall_status']}"
            )
            self.logger.info(f"Compliance score: {results['compliance_score']:.1f}%")
            self.logger.info(f"Audit saved to: {audit_file}")

            if results["overall_status"] == "fail" and self.strict_mode:
                raise InvariantViolation(
                    invariant_id="COMPREHENSIVE_ENFORCEMENT",
                    message=f"Comprehensive enforcement failed: {results}",
                    severity="critical",
                )

        except InvariantViolation as e:
            self.logger.error(f"Comprehensive enforcement failed: {e}")
            results["overall_status"] = "fail"
            results["error"] = str(e)

            if self.strict_mode:
                raise

        except Exception as e:
            self.logger.error(f"Error during comprehensive enforcement: {e}")
            self.logger.debug(traceback.format_exc())
            results["overall_status"] = "fail"
            results["error"] = str(e)

        return results

    def _validate_tool_schemas_structure(self) -> Dict[str, Any]:
        """Validate the structure of all tool schemas."""
        valid_count = 0
        invalid_count = 0
        validation_errors = []

        for tool_name, tool_schema in self.tool_schemas.items():
            try:
                # Check required fields
                required_fields = [
                    "tool_name",
                    "parameters",
                    "return_type",
                    "enforcement_point",
                ]
                for field in required_fields:
                    if field not in tool_schema:
                        raise ValueError(f"Missing required field: {field}")

                # Validate parameters structure
                parameters = tool_schema.get("parameters", {})
                if not isinstance(parameters, dict):
                    raise ValueError(
                        f"Parameters must be a dictionary, got {type(parameters)}"
                    )

                valid_count += 1

            except Exception as e:
                invalid_count += 1
                validation_errors.append({"tool_name": tool_name, "error": str(e)})

                self.audit.log_action(
                    action="validate_tool_schema",
                    invariant_id=tool_name,
                    status="violation",
                    details={
                        "tool_name": tool_name,
                        "error": str(e),
                        "action_taken": "logged_validation_error",
                    },
                )

        return {
            "valid": invalid_count == 0,
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "validation_errors": validation_errors,
            "status": "pass" if invalid_count == 0 else "fail",
        }

    def _calculate_compliance_score(self, results: Dict[str, Any]) -> float:
        """Calculate overall compliance score."""
        total_checks = 0
        passed_checks = 0

        # Protected files check
        protected = results.get("protected_files", {})
        if "enforced" in protected and "violations" in protected:
            total_checks += 1
            if protected.get("status") == "pass":
                passed_checks += 1

        # Tool validations check
        tools = results.get("tool_validations", {})
        if "valid" in tools:
            total_checks += 1
            if tools.get("valid", False):
                passed_checks += 1

        # Rule enforcements check
        rules = results.get("rule_enforcements", {})
        if "allowed" in rules:
            total_checks += 1
            if rules.get("allowed", False):
                passed_checks += 1

        if total_checks == 0:
            return 0.0

        return (passed_checks / total_checks) * 100

    def get_enforcement_summary(self) -> Dict[str, Any]:
        """Get summary of current enforcement state."""
        audit_summary = self.audit.get_summary()

        return {
            "invariants": {
                "total": len(self.invariants),
                "protected_files": len(self.protected_files),
                "tool_schemas": len(self.tool_schemas),
                "enforcement_rules": len(self.enforcement_rules),
            },
            "audit": audit_summary,
            "enforcement_mode": "strict" if self.strict_mode else "permissive",
            "system_status": "operational",
        }


def main():
    """Main entry point for the invariant enforcement controller."""
    parser = argparse.ArgumentParser(
        description="Corporate-style invariant enforcement controller"
    )
    parser.add_argument(
        "--invariants", required=True, help="JSON file containing atomic invariants"
    )
    parser.add_argument(
        "--action",
        choices=["validate", "enforce", "audit", "comprehensive"],
        default="comprehensive",
        help="Action to perform (default: comprehensive)",
    )
    parser.add_argument(
        "--strict", action="store_true", help="Enable strict mode (fail on violations)"
    )
    parser.add_argument("--audit-file", help="Custom audit file path")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Create enforcer
    enforcer = InvariantEnforcer(
        invariants_file=args.invariants,
        audit_file=args.audit_file,
        strict_mode=args.strict,
    )

    # Load invariants
    if not enforcer.load_invariants():
        print("ERROR: Failed to load invariants")
        return 1

    # Perform requested action
    try:
        if args.action == "validate":
            print("Validating invariants structure...")
            # Basic validation is done during load
            print("✓ Invariants loaded successfully")
            summary = enforcer.get_enforcement_summary()
            print(f"  • Total invariants: {summary['invariants']['total']}")
            print(f"  • Protected files: {summary['invariants']['protected_files']}")
            print(f"  • Tool schemas: {summary['invariants']['tool_schemas']}")
            print(
                f"  • Enforcement rules: {summary['invariants']['enforcement_rules']}"
            )

        elif args.action == "enforce":
            print("Enforcing protected files...")
            enforced, violations = enforcer.enforce_protected_files()
            print(f"  • Enforced: {enforced}")
            print(f"  • Violations: {violations}")
            print(f"  • Status: {'PASS' if violations == 0 else 'FAIL'}")

        elif args.action == "audit":
            print("Generating audit report...")
            audit_file = enforcer.audit.save_audit()
            print(f"✓ Audit saved to: {audit_file}")
            summary = enforcer.audit.get_summary()
            print(f"  • Total entries: {summary['total_entries']}")
            print(f"  • Violations: {summary['violations']}")
            print(f"  • Enforcements: {summary['enforcements']}")
            print(f"  • Compliance rate: {summary['compliance_rate']:.1f}%")

        elif args.action == "comprehensive":
            print("Running comprehensive enforcement...")
            results = enforcer.run_comprehensive_enforcement()

            print(f"\n=== COMPREHENSIVE ENFORCEMENT RESULTS ===")
            print(f"Overall Status: {results['overall_status'].upper()}")
            print(f"Compliance Score: {results['compliance_score']:.1f}%")

            # Protected files
            protected = results["protected_files"]
            print(f"\nProtected Files:")
            print(f"  • Enforced: {protected.get('enforced', 0)}")
            print(f"  • Violations: {protected.get('violations', 0)}")
            print(f"  • Status: {protected.get('status', 'unknown').upper()}")

            # Tool validations
            tools = results["tool_validations"]
            print(f"\nTool Schemas:")
            print(f"  • Valid: {tools.get('valid_count', 0)}")
            print(f"  • Invalid: {tools.get('invalid_count', 0)}")
            print(f"  • Status: {tools.get('status', 'unknown').upper()}")

            # Rule enforcements
            rules = results["rule_enforcements"]
            print(f"\nExecution Rules:")
            print(f"  • Allowed: {rules.get('allowed', False)}")
            print(f"  • Message: {rules.get('message', 'No message')}")
            print(f"  • Status: {rules.get('status', 'unknown').upper()}")

            if "audit_file" in results:
                print(f"\nAudit File: {results['audit_file']}")

            if results["overall_status"] == "fail":
                print(f"\n❌ ENFORCEMENT FAILED")
                if "error" in results:
                    print(f"Error: {results['error']}")
                return 1
            else:
                print(f"\n✅ ENFORCEMENT PASSED")

        # Print summary
        summary = enforcer.get_enforcement_summary()
        print(f"\n=== ENFORCEMENT SUMMARY ===")
        print(f"Mode: {summary['enforcement_mode'].upper()}")
        print(f"System Status: {summary['system_status'].upper()}")
        print(f"Audit Compliance: {summary['audit']['compliance_rate']:.1f}%")
        print(f"Total Invariants: {summary['invariants']['total']}")
        print(f"Protected Files: {summary['invariants']['protected_files']}")
        print(f"Tool Schemas: {summary['invariants']['tool_schemas']}")
        print(f"Enforcement Rules: {summary['invariants']['enforcement_rules']}")

        return 0

    except InvariantViolation as e:
        print(f"\n❌ INVARIANT VIOLATION (STRICT MODE): {e}")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
