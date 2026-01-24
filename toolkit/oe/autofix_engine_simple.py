"""
Simplified Autofix Engine - Glass-Box Boundary Autofix Implementation

A working, simplified version of the autofix engine that provides
core boundary violation detection and fix suggestions.

Author: Orthogonal Engineering System
Date: 2026-01-24
Version: 1.0.0
"""

import ast
import re
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ViolationSeverity(Enum):
    """Severity levels for boundary violations."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FixType(Enum):
    """Types of fixes that can be applied."""

    ADD_DECORATOR = "add_decorator"
    REPLACE_EXCEPTION = "replace_exception"
    ADD_GATEWAY = "add_gateway"
    ADD_IMPORTS = "add_imports"


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
        }


class SimpleAutofixEngine:
    """
    Simplified autofix engine for Glass-Box Boundary violations.

    Provides core functionality:
    1. Detect missing @glass_box_boundary decorators
    2. Detect broad exception catching
    3. Detect direct I/O operations
    4. Generate basic fix suggestions
    """

    def __init__(self):
        """Initialize the simplified autofix engine."""
        self.violations_detected = 0
        self.fixes_suggested = 0

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
        lines = content.split("\n")

        # Check for missing decorators
        violations.extend(self._detect_missing_decorators(file_path, content, lines))

        # Check for broad exceptions
        violations.extend(self._detect_broad_exceptions(file_path, content, lines))

        # Check for direct I/O
        violations.extend(self._detect_direct_io(file_path, content, lines))

        self.violations_detected += len(violations)
        return violations

    def _detect_missing_decorators(
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

                        # Generate fix
                        decorator_line = "@glass_box_boundary()"
                        fixed_code = f"{decorator_line}\n{code_snippet}"

                        violation = BoundaryViolation(
                            violation_id=f"missing_decorator_{node.name}_{line_start}",
                            violation_type="missing_boundary_decorator",
                            severity=ViolationSeverity.HIGH,
                            location=(file_path, line_start, line_end),
                            description=f"Function '{node.name}' missing @glass_box_boundary decorator",
                            code_snippet=code_snippet,
                            suggested_fixes=[
                                {
                                    "fix_type": FixType.ADD_DECORATOR.value,
                                    "description": "Add @glass_box_boundary decorator",
                                    "confidence": 0.9,
                                    "code_before": code_snippet,
                                    "code_after": fixed_code,
                                    "application_instructions": f"Add @glass_box_boundary() decorator before function '{node.name}'",
                                }
                            ],
                        )
                        violations.append(violation)
                        self.fixes_suggested += 1
        except SyntaxError:
            # Skip files with syntax errors
            pass

        return violations

    def _detect_broad_exceptions(
        self, file_path: str, content: str, lines: List[str]
    ) -> List[BoundaryViolation]:
        """Detect broad exception catching."""
        violations = []

        pattern = r"except\s+(Exception|BaseException)\s*:"
        for i, line in enumerate(lines):
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                # Get context
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                context = "\n".join(lines[start:end])

                # Check if suppressed
                next_lines = lines[i + 1 : i + 3]
                is_suppressed = any("pass" in l.strip() for l in next_lines)

                severity = (
                    ViolationSeverity.CRITICAL
                    if is_suppressed
                    else ViolationSeverity.HIGH
                )

                # Generate fix
                specific_fix = line.replace("Exception", "ValueError").replace(
                    "BaseException", "RuntimeError"
                )
                fixed_context = context.replace(line, specific_fix)

                violation = BoundaryViolation(
                    violation_id=f"broad_exception_{file_path}_{i + 1}",
                    violation_type="broad_exception_catch",
                    severity=severity,
                    location=(file_path, i + 1, i + 1),
                    description="Broad exception catching suppresses error signals",
                    code_snippet=context,
                    suggested_fixes=[
                        {
                            "fix_type": FixType.REPLACE_EXCEPTION.value,
                            "description": "Replace with specific exception",
                            "confidence": 0.85,
                            "code_before": context,
                            "code_after": fixed_context,
                            "application_instructions": "Replace 'except Exception:' with specific exception type",
                        }
                    ],
                )
                violations.append(violation)
                self.fixes_suggested += 1

        return violations

    def _detect_direct_io(
        self, file_path: str, content: str, lines: List[str]
    ) -> List[BoundaryViolation]:
        """Detect direct I/O operations without gateway."""
        violations = []

        io_patterns = [
            (r"open\([^)]*\)", "Direct file open without gateway"),
            (r"\.read\([^)]*\)", "Direct file read without gateway"),
            (r"\.write\([^)]*\)", "Direct file write without gateway"),
            (
                r"json\.(dump|dumps|load|loads)\(",
                "Direct JSON operation without gateway",
            ),
        ]

        for i, line in enumerate(lines):
            for pattern, description in io_patterns:
                if re.search(pattern, line):
                    # Get context
                    start = max(0, i - 2)
                    end = min(len(lines), i + 3)
                    context = "\n".join(lines[start:end])

                    # Generate gateway fix suggestion
                    gateway_fix = (
                        f"# TODO: Replace with gateway interface\n# {line.strip()}"
                    )
                    fixed_context = context.replace(line, gateway_fix)

                    violation = BoundaryViolation(
                        violation_id=f"direct_io_{file_path}_{i + 1}_{hash(pattern)}",
                        violation_type="direct_io_without_gateway",
                        severity=ViolationSeverity.HIGH,
                        location=(file_path, i + 1, i + 1),
                        description=description,
                        code_snippet=context,
                        suggested_fixes=[
                            {
                                "fix_type": FixType.ADD_GATEWAY.value,
                                "description": "Add gateway interface for I/O",
                                "confidence": 0.7,
                                "code_before": context,
                                "code_after": fixed_context,
                                "application_instructions": "Create gateway interface for I/O operations",
                            }
                        ],
                    )
                    violations.append(violation)
                    self.fixes_suggested += 1

        return violations

    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics."""
        return {
            "violations_detected": self.violations_detected,
            "fixes_suggested": self.fixes_suggested,
        }
