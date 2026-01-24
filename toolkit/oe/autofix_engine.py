"""
Autofix Engine - Glass-Box Boundary Autofix Implementation

Implements real-time boundary violation detection and fix suggestions.
Provides spell-check-like functionality for code integrity with:
- Boundary violation detection
- Fix suggestion generation
- Automatic fix application (with user confirmation)
- Documentation sync maintenance

Author: Orthogonal Engineering System
Date: 2026-01-24
Version: 1.0.0
"""

import ast
import difflib
import functools
import inspect
import json
import re
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from toolkit.oe.boundary_enforcer import BoundaryViolation, glass_box_boundary


class ViolationSeverity(Enum):
    """Severity levels for boundary violations."""

    CRITICAL = "critical"  # Boundary breach, suppressed signal, missing artifact
    HIGH = "high"  # Missing validation, direct I/O, timeline violation
    MEDIUM = "medium"  # Structural inconsistency, missing imports
    LOW = "low"  # Documentation sync issues, minor style violations


class FixType(Enum):
    """Types of fixes that can be applied."""

    ADD_DECORATOR = "add_decorator"
    ADD_VALIDATION = "add_validation"
    ADD_GATEWAY = "add_gateway"
    REPLACE_EXCEPTION = "replace_exception"
    ADD_IMPORTS = "add_imports"
    ADD_LOGGING = "add_logging"
    ADD_EXCEPTION_HANDLING = "add_exception_handling"
    REFACTOR_DATABASE_ACCESS = "refactor_database_access"
    SYNC_DOCUMENTATION = "sync_documentation"


@dataclass
class BoundaryViolation:
    """Represents a detected boundary violation."""

    violation_id: str
    violation_type: str
    severity: ViolationSeverity
    location: Tuple[str, int, int]  # (file_path, line_start, line_end)
    description: str
    code_snippet: str
    suggested_fixes: List[Dict[str, Any]]
    context: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert violation to dictionary for serialization."""
        return {
            "violation_id": self.violation_id,
            "violation_type": self.violation_type,
            "severity": self.severity.value,
            "location": {
                "file_path": self.location[0],
                "line_start": self.location[1],
                "line_end": self.location[2],
            },
            "description": self.description,
            "code_snippet": self.code_snippet,
            "suggested_fixes": self.suggested_fixes,
            "context": self.context or {},
        }


@dataclass
class FixSuggestion:
    """Represents a suggested fix for a boundary violation."""

    fix_id: str
    fix_type: FixType
    description: str
    confidence: float  # 0.0 to 1.0
    code_before: str
    code_after: str
    application_instructions: str
    validation_required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert fix suggestion to dictionary."""
        return {
            "fix_id": self.fix_id,
            "fix_type": self.fix_type.value,
            "description": self.description,
            "confidence": self.confidence,
            "code_before": self.code_before,
            "code_after": self.code_after,
            "application_instructions": self.application_instructions,
            "validation_required": self.validation_required,
        }


class AutofixEngine:
    """
    Core autofix engine for Glass-Box Boundary violations.

    Provides spell-check-like functionality for code integrity with:
    1. Real-time boundary violation detection
    2. Fix suggestion generation
    3. Automatic fix application (with user confirmation)
    4. Documentation sync maintenance
    """

    def __init__(self, boundary_enforcer=None):
        """
        Initialize the autofix engine.

        Args:
            boundary_enforcer: Optional boundary enforcer instance.
        """
        self.boundary_enforcer = boundary_enforcer
        self.violation_patterns = self._initialize_violation_patterns()
        self.fix_templates = self._initialize_fix_templates()

        # Statistics
        self.violations_detected = 0
        self.fixes_applied = 0
        self.fixes_suggested = 0

    def _initialize_violation_patterns(self) -> Dict[str, Dict]:
        """Initialize patterns for detecting boundary violations."""
        return {
            "missing_boundary_decorator": {
                "pattern": r"def\s+\w+\s*\([^)]*\)\s*:",
                "description": "Function missing @glass_box_boundary decorator",
                "severity": ViolationSeverity.HIGH,
                "detector": self._detect_missing_decorator,
            },
            "broad_exception_catch": {
                "pattern": r"except\s+(Exception|BaseException)\s*:",
                "description": "Broad exception catching suppresses signals",
                "severity": ViolationSeverity.CRITICAL,
                "detector": self._detect_broad_exception,
            },
            "direct_io_without_gateway": {
                "pattern": r"(open\(|\.read\(|\.write\(|\.save\(|\.load\()",
                "description": "Direct I/O operation without gateway interface",
                "severity": ViolationSeverity.HIGH,
                "detector": self._detect_direct_io,
            },
            "missing_input_validation": {
                "pattern": r"def\s+\w+\s*\([^)]*\)\s*:",
                "description": "Function missing input validation",
                "severity": ViolationSeverity.MEDIUM,
                "detector": self._detect_missing_decorator,  # Using same detector for now
            },
            "missing_output_validation": {
                "pattern": r"return\s+",
                "description": "Function missing output validation",
                "severity": ViolationSeverity.MEDIUM,
                "detector": self._detect_missing_decorator,  # Using same detector for now
            },
            "suppressed_warnings": {
                "pattern": r"warnings\.filterwarnings\([^)]*ignore[^)]*\)",
                "description": "Warning suppression hides potential issues",
                "severity": ViolationSeverity.CRITICAL,
                "detector": self._detect_broad_exception,  # Using similar detector for now
            },
            "ui_database_direct_path": {
                "pattern": r"(UI|ui|button|click).*?(database|db|insert|update|delete)",
                "description": "Direct UI to database access violates orthogonal separation",
                "severity": ViolationSeverity.HIGH,
                "detector": self._detect_direct_io,  # Using similar detector for now
            },
            "missing_imports": {
                "pattern": r'^\s*(?!import|from|#|""").*?\b(glass_box_boundary|BoundaryViolation)\b',
                "description": "Missing required imports for boundary enforcement",
                "severity": ViolationSeverity.MEDIUM,
                "detector": self._detect_missing_decorator,  # Using same detector for now
            },
        }

    def _initialize_fix_templates(self) -> Dict[FixType, Dict]:
        """Initialize fix templates for different violation types."""
        return {
            FixType.ADD_DECORATOR: {
                "template": "@glass_box_boundary(input_validator={input_validator}, output_validator={output_validator})\n{original_code}",
                "description": "Add @glass_box_boundary decorator with validation",
                "confidence": 0.9,
            },
            FixType.ADD_VALIDATION: {
                "template": "{validation_code}\n{original_code}",
                "description": "Add input/output validation schema",
                "confidence": 0.8,
            },
            FixType.ADD_GATEWAY: {
                "template": "# Gateway interface for I/O operations\nclass {gateway_name}:\n    @staticmethod\n    def {operation}(*args, **kwargs):\n        # Gateway implementation\n        pass\n\n{original_code}",
                "description": "Add gateway interface for I/O operations",
                "confidence": 0.7,
            },
            FixType.REPLACE_EXCEPTION: {
                "template": 'except {specific_exception} as e:\n    logger.error(f"Boundary violation: {e}")\n    raise BoundaryViolation(f"{specific_exception}: {e}", "exception_handling")',
                "description": "Replace broad exception with specific exception handling",
                "confidence": 0.85,
            },
            FixType.ADD_IMPORTS: {
                "template": "from toolkit.oe.boundary_enforcer import glass_box_boundary, BoundaryViolation\n{original_imports}",
                "description": "Add required imports for boundary enforcement",
                "confidence": 0.95,
            },
            FixType.ADD_LOGGING: {
                "template": "import logging\n\nlogger = logging.getLogger(__name__)\n\n{original_code}",
                "description": "Add logging infrastructure",
                "confidence": 0.8,
            },
            FixType.ADD_EXCEPTION_HANDLING: {
                "template": 'try:\n    {original_code}\nexcept Exception as e:\n    logger.error(f"Boundary violation: {e}")\n    raise BoundaryViolation(f"Unhandled exception: {e}", "exception_handling")',
                "description": "Add proper exception handling",
                "confidence": 0.75,
            },
        }

    def analyze_file(self, file_path: str, content: str) -> List[BoundaryViolation]:
        """
        Analyze a file for boundary violations.

        Args:
            file_path: Path to the file
            content: File content as string

        Returns:
            List of detected boundary violations
        """
        violations = []

        # Split content into lines for line-based analysis
        lines = content.split("\n")

        # Check each violation pattern
        for violation_type, pattern_info in self.violation_patterns.items():
            detector = pattern_info["detector"]
            detected_violations = detector(file_path, content, lines)
            violations.extend(detected_violations)

        self.violations_detected += len(violations)
        return violations

    def _detect_missing_decorator(
        self, file_path: str, content: str, lines: List[str]
    ) -> List[BoundaryViolation]:
        """Detect functions missing @glass_box_boundary decorator."""
        violations = []

        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if function has decorator
                    has_decorator = any(
                        isinstance(decorator, ast.Name)
                        and decorator.id == "glass_box_boundary"
                        for decorator in node.decorator_list
                    )

                    if not has_decorator and not node.name.startswith("_"):
                        # Get function lines
                        line_start = node.lineno
                        line_end = node.end_lineno
                        code_snippet = "\n".join(lines[line_start - 1 : line_end])

                        # Generate fix suggestions
                        fixes = self._generate_fixes_for_missing_decorator(
                            node, code_snippet
                        )

                        violation = BoundaryViolation(
                            violation_id=f"missing_decorator_{node.name}_{line_start}",
                            violation_type="missing_boundary_decorator",
                            severity=ViolationSeverity.HIGH,
                            location=(file_path, line_start, line_end),
                            description=f"Function '{node.name}' missing @glass_box_boundary decorator",
                            code_snippet=code_snippet,
                            suggested_fixes=fixes,
                            context={
                                "function_name": node.name,
                                "args": [arg.arg for arg in node.args.args],
                                "has_return": any(
                                    isinstance(n, ast.Return) for n in ast.walk(node)
                                ),
                            },
                        )
                        violations.append(violation)
        except SyntaxError:
            # Skip files with syntax errors
            pass

        return violations

    def _generate_fixes_for_missing_decorator(
        self, node: ast.FunctionDef, code_snippet: str
    ) -> List[Dict]:
        """Generate fix suggestions for missing decorator."""
        fixes = []

        # Analyze function to determine appropriate validators
        has_args = len(node.args.args) > 0
        has_return = any(isinstance(n, ast.Return) for n in ast.walk(node))

        # Fix 1: Basic decorator
        decorator_line = f"@glass_box_boundary()"
        fixed_code = f"{decorator_line}\n{code_snippet}"

        fixes.append(
            {
                "fix_type": FixType.ADD_DECORATOR.value,
                "description": "Add basic @glass_box_boundary decorator",
                "confidence": 0.9,
                "code_before": code_snippet,
                "code_after": fixed_code,
                "application_instructions": f"Add @glass_box_boundary() decorator before function '{node.name}'",
                "validation_required": True,
            }
        )

        # Fix 2: Decorator with validation if function has args
        if has_args:
            decorator_line = f"@glass_box_boundary(input_validator=validate_input, output_validator=validate_output)"
            fixed_code = f"{decorator_line}\n{code_snippet}"

            fixes.append(
                {
                    "fix_type": FixType.ADD_DECORATOR.value,
                    "description": "Add @glass_box_boundary decorator with validation",
                    "confidence": 0.8,
                    "code_before": code_snippet,
                    "code_after": fixed_code,
                    "application_instructions": f"Add decorator with input/output validation for function '{node.name}'",
                    "validation_required": True,
                }
            )

        return fixes

    def _detect_broad_exception(
        self, file_path: str, content: str, lines: List[str]
    ) -> List[BoundaryViolation]:
        """Detect broad exception catching."""
        violations = []

        pattern = r"except\s+(Exception|BaseException)\s*:"
        for i, line in enumerate(lines):
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                # Get context (3 lines before and after)
                start = max(0, i - 3)
                end = min(len(lines), i + 4)
                context = "\n".join(lines[start:end])

                # Check if it's a "pass" or suppressed exception
                next_lines = lines[i + 1 : i + 4]
                is_suppressed = any("pass" in l.strip() for l in next_lines)

                severity = (
                    ViolationSeverity.CRITICAL
                    if is_suppressed
                    else ViolationSeverity.HIGH
                )

                fixes = self._generate_fixes_for_broad_exception(
                    line, context, is_suppressed
                )

                violation = BoundaryViolation(
                    violation_id=f"broad_exception_{file_path}_{i + 1}",
                    violation_type="broad_exception_catch",
                    severity=severity,
                    location=(file_path, i + 1, i + 1),
                    description="Broad exception catching suppresses error signals",
                    code_snippet=context,
                    suggested_fixes=fixes,
                    context={
                        "exception_type": match.group(1),
                        "is_suppressed": is_suppressed,
                        "line_number": i + 1,
                    },
                )
                violations.append(violation)

        return violations

    def _generate_fixes_for_broad_exception(
        self, line: str, context: str, is_suppressed: bool
    ) -> List[Dict]:
        """Generate fix suggestions for broad exception."""
        fixes = []

        # Fix 1: Replace with specific exception
        specific_fix = line.replace("Exception", "ValueError").replace(
            "BaseException", "RuntimeError"
        )
        fixed_context = context.replace(line, specific_fix)

        fixes.append(
            {
                "fix_type": FixType.REPLACE_EXCEPTION.value,
                "description": "Replace broad exception with specific exception type",
                "confidence": 0.85,
                "code_before": context,
                "code_after": fixed_context,
                "application_instructions": "Replace 'except Exception:' with specific exception type like 'except ValueError:'",
                "validation_required": True,
            }
        )

        # Fix 2: Add proper error handling if suppressed
        if is_suppressed:
            proper_handling = (
                line
                + '\n    logger.error(f"Boundary violation: {e}")\n    raise BoundaryViolation(f"Unhandled exception: {e}", "exception_handling")'
            )
            fixed_context = context.replace(line + "\n    pass", proper_handling)

            fixes.append(
                {
                    "fix_type": FixType.ADD_EXCEPTION_HANDLING.value,
                    "description": "Add proper exception handling with logging and boundary violation",
                    "confidence": 0.9,
                    "code_before": context,
                    "code_after": fixed_context,
                    "application_instructions": "Replace suppressed exception with proper error handling and logging",
                    "validation_required": True,
                }
            )

        return fixes

    def _detect_direct_io(
        self, file_path: str, content: str, lines: List[str]
    ) -> List[BoundaryViolation]:
        """Detect direct I/O operations without gateway."""
        violations = []

        io_patterns = [
            (r"open\([^)]*\)", "Direct file open without gateway"),
            (r"\.read\([^)]*\)", "Direct file read without gateway"),
            (r"\.write\([^)]*\)", "Direct file write without gateway"),
            (r"\.save\([^)]*\)", "Direct file save without gateway"),
            (r"\.load\([^)]*\)", "Direct file load without gateway"),
            (
                r"json\.(dump|dumps|load|loads)\(",
                "Direct JSON operation without gateway",
            ),
            (
                r"pickle\.(dump|dumps|load|loads)\(",
                "Direct pickle operation without gateway",
            ),
        ]

        violations = []

        for i, line in enumerate(lines):
            for pattern, description in io_patterns:
                if re.search(pattern, line):
                    # Get context (3 lines before and after)
                    start = max(0, i - 3)
                    end = min(len(lines), i + 4)
                    context = "\n".join(lines[start:end])

                    # Generate fix suggestions
                    fixes = self._generate_fixes_for_direct_io(
                        line, context, pattern, description
                    )

                    violation = BoundaryViolation(
                        violation_id=f"direct_io_{file_path}_{i + 1}_{hash(pattern)}",
                        violation_type="direct_io_without_gateway",
                        severity=ViolationSeverity.HIGH,
                        location=(file_path, i + 1, i + 1),
                        description=description,
                        code_snippet=context,
                        suggested_fixes=fixes,
                        context={
                            "pattern": pattern,
                            "line_number": i + 1,
                            "line_content": line.strip(),
                        },
                    )
                    violations.append(violation)

        return violations
