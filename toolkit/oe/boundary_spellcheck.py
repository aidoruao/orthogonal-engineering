"""
Boundary Spell-Check System - Real-time Code Integrity Validation

Provides spell-check-like functionality for Glass-Box Boundary violations with:
- Real-time validation during code editing
- Inline violation highlighting
- Quick-fix suggestions
- Auto-correction for common patterns
- Integration with IDE workflow

Author: Orthogonal Engineering System
Date: 2026-01-24
Version: 1.0.0
"""

import ast
import difflib
import re
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from toolkit.oe.autofix_engine import AutofixEngine, BoundaryViolation, FixType
from toolkit.oe.boundary_enforcer import BoundaryViolation as BoundaryViolationException


class SpellCheckSeverity(Enum):
    """Severity levels for spell-check violations."""

    ERROR = "error"  # Must fix - boundary violation
    WARNING = "warning"  # Should fix - potential issue
    INFO = "info"  # Could fix - style/suggestion
    HINT = "hint"  # Optional fix - improvement


class SpellCheckAction(Enum):
    """Actions available for spell-check violations."""

    QUICK_FIX = "quick_fix"  # Apply fix automatically
    SUGGEST_FIX = "suggest_fix"  # Show fix suggestion
    IGNORE = "ignore"  # Ignore this violation
    IGNORE_ALL = "ignore_all"  # Ignore all violations of this type
    DISABLE = "disable"  # Disable this check
    SHOW_DOCS = "show_docs"  # Show documentation
    APPLY_ALL = "apply_all"  # Apply all similar fixes


@dataclass
class SpellCheckDiagnostic:
    """Diagnostic for a boundary violation (like a spell-check error)."""

    diagnostic_id: str
    file_path: str
    line: int
    column: int
    end_line: int
    end_column: int
    severity: SpellCheckSeverity
    message: str
    code: str
    source: str = "boundary_spellcheck"
    actions: List[SpellCheckAction] = field(default_factory=list)
    fix: Optional[Dict[str, Any]] = None
    related_info: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for IDE integration."""
        return {
            "diagnostic_id": self.diagnostic_id,
            "range": {
                "start": {"line": self.line, "character": self.column},
                "end": {"line": self.end_line, "character": self.end_column},
            },
            "severity": self.severity.value,
            "message": self.message,
            "code": self.code,
            "source": self.source,
            "actions": [action.value for action in self.actions],
            "fix": self.fix,
            "related_info": self.related_info,
            "tags": self.tags,
        }


@dataclass
class SpellCheckResult:
    """Result of a spell-check operation."""

    file_path: str
    diagnostics: List[SpellCheckDiagnostic]
    timestamp: datetime
    duration_ms: float
    total_violations: int
    fixable_violations: int
    auto_fixed: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
            "total_violations": self.total_violations,
            "fixable_violations": self.fixable_violations,
            "auto_fixed": self.auto_fixed,
            "diagnostics": [d.to_dict() for d in self.diagnostics],
        }


class BoundarySpellCheck:
    """
    Boundary Spell-Check System for real-time code integrity validation.

    Provides spell-check-like functionality with:
    1. Real-time validation during editing
    2. Inline violation highlighting
    3. Quick-fix suggestions (Ctrl+. or ⌘.)
    4. Auto-correction for common patterns
    5. Integration with IDE workflow
    """

    def __init__(self, autofix_engine: Optional[AutofixEngine] = None):
        """
        Initialize the boundary spell-check system.

        Args:
            autofix_engine: Optional autofix engine for fix generation
        """
        self.autofix_engine = autofix_engine or AutofixEngine()
        self.enabled_checks = self._initialize_checks()
        self.ignored_patterns: Set[str] = set()
        self.disabled_checks: Set[str] = set()

        # Statistics
        self.total_files_checked = 0
        self.total_violations_found = 0
        self.total_fixes_applied = 0
        self.total_auto_fixes = 0

        # Cache for performance
        self._file_cache: Dict[str, Tuple[str, float]] = {}
        self._diagnostic_cache: Dict[str, List[SpellCheckDiagnostic]] = {}

    def _initialize_checks(self) -> Dict[str, Dict[str, Any]]:
        """Initialize all spell-check rules."""
        return {
            "missing_boundary_decorator": {
                "description": "Function missing @glass_box_boundary decorator",
                "severity": SpellCheckSeverity.ERROR,
                "pattern": r"def\s+\w+\s*\([^)]*\)\s*:",
                "detector": self._check_missing_decorator,
                "auto_fix": True,
                "quick_fix": True,
                "tags": ["boundary", "decorator", "function"],
            },
            "broad_exception_catch": {
                "description": "Broad exception catching suppresses signals",
                "severity": SpellCheckSeverity.ERROR,
                "pattern": r"except\s+(Exception|BaseException)\s*:",
                "detector": self._check_broad_exception,
                "auto_fix": True,
                "quick_fix": True,
                "tags": ["exception", "signal-suppression", "critical"],
            },
            "direct_io_without_gateway": {
                "description": "Direct I/O operation without gateway interface",
                "severity": SpellCheckSeverity.WARNING,
                "pattern": r"(open\(|\.read\(|\.write\(|\.save\(|\.load\()",
                "detector": self._check_direct_io,
                "auto_fix": False,
                "quick_fix": True,
                "tags": ["io", "gateway", "orthogonal"],
            },
            "missing_input_validation": {
                "description": "Function missing input validation",
                "severity": SpellCheckSeverity.WARNING,
                "pattern": r"def\s+\w+\s*\([^)]*\)\s*:",
                "detector": self._check_missing_validation,
                "auto_fix": False,
                "quick_fix": True,
                "tags": ["validation", "input", "function"],
            },
            "suppressed_warnings": {
                "description": "Warning suppression hides potential issues",
                "severity": SpellCheckSeverity.ERROR,
                "pattern": r"warnings\.filterwarnings\([^)]*ignore[^)]*\)",
                "detector": self._check_suppressed_warnings,
                "auto_fix": True,
                "quick_fix": True,
                "tags": ["warning", "signal-suppression", "debugging"],
            },
            "missing_imports": {
                "description": "Missing required imports for boundary enforcement",
                "severity": SpellCheckSeverity.INFO,
                "pattern": r'^\s*(?!import|from|#|""").*?\b(glass_box_boundary|BoundaryViolation)\b',
                "detector": self._check_missing_imports,
                "auto_fix": True,
                "quick_fix": True,
                "tags": ["import", "dependency", "boundary"],
            },
            "ui_database_direct_path": {
                "description": "Direct UI to database access violates orthogonal separation",
                "severity": SpellCheckSeverity.WARNING,
                "pattern": r"(UI|ui|button|click).*?(database|db|insert|update|delete)",
                "detector": self._check_ui_database_path,
                "auto_fix": False,
                "quick_fix": True,
                "tags": ["ui", "database", "orthogonal", "architecture"],
            },
            "incomplete_logging": {
                "description": "Missing logging infrastructure",
                "severity": SpellCheckSeverity.INFO,
                "pattern": r"def\s+\w+\s*\([^)]*\)\s*:",
                "detector": self._check_incomplete_logging,
                "auto_fix": True,
                "quick_fix": True,
                "tags": ["logging", "observability", "debugging"],
            },
        }

    def check_file(
        self, file_path: str, content: Optional[str] = None
    ) -> SpellCheckResult:
        """
        Check a file for boundary violations (spell-check style).

        Args:
            file_path: Path to the file
            content: Optional file content (if None, reads from file)

        Returns:
            SpellCheckResult with diagnostics
        """
        start_time = time.time()

        # Read content if not provided
        if content is None:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                return SpellCheckResult(
                    file_path=file_path,
                    diagnostics=[],
                    timestamp=datetime.now(),
                    duration_ms=0,
                    total_violations=0,
                    fixable_violations=0,
                )

        # Update cache
        self._file_cache[file_path] = (content, time.time())

        # Run all checks
        diagnostics: List[SpellCheckDiagnostic] = []

        for check_id, check_info in self.enabled_checks.items():
            if check_id in self.disabled_checks:
                continue

            detector = check_info["detector"]
            check_diagnostics = detector(file_path, content)
            diagnostics.extend(check_diagnostics)

        # Update statistics
        self.total_files_checked += 1
        self.total_violations_found += len(diagnostics)

        # Count fixable violations
        fixable_violations = sum(
            1
            for d in diagnostics
            if d.fix is not None and SpellCheckAction.QUICK_FIX in d.actions
        )

        duration_ms = (time.time() - start_time) * 1000

        # Cache diagnostics
        self._diagnostic_cache[file_path] = diagnostics

        return SpellCheckResult(
            file_path=file_path,
            diagnostics=diagnostics,
            timestamp=datetime.now(),
            duration_ms=duration_ms,
            total_violations=len(diagnostics),
            fixable_violations=fixable_violations,
        )

    def check_files(self, file_paths: List[str]) -> Dict[str, SpellCheckResult]:
        """
        Check multiple files for boundary violations.

        Args:
            file_paths: List of file paths to check

        Returns:
            Dictionary mapping file paths to SpellCheckResult
        """
        results = {}
        for file_path in file_paths:
            result = self.check_file(file_path)
            results[file_path] = result
        return results

    def apply_fix(
        self, diagnostic_id: str, file_path: str
    ) -> Optional[Tuple[str, str]]:
        """
        Apply a fix for a diagnostic.

        Args:
            diagnostic_id: ID of the diagnostic to fix
            file_path: Path to the file

        Returns:
            Tuple of (original_content, fixed_content) or None if fix cannot be applied
        """
        # Get diagnostics from cache
        if file_path not in self._diagnostic_cache:
            # Re-run check if not in cache
            self.check_file(file_path)

        diagnostics = self._diagnostic_cache.get(file_path, [])

        # Find the diagnostic
        diagnostic = next(
            (d for d in diagnostics if d.diagnostic_id == diagnostic_id), None
        )
        if not diagnostic or not diagnostic.fix:
            return None

        # Get file content
        if file_path in self._file_cache:
            content = self._file_cache[file_path][0]
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

        # Apply the fix
        fix = diagnostic.fix
        if "code_before" in fix and "code_after" in fix:
            # Simple replacement fix
            fixed_content = content.replace(fix["code_before"], fix["code_after"])

            # Update cache
            self._file_cache[file_path] = (fixed_content, time.time())
            self.total_fixes_applied += 1

            return (content, fixed_content)

        return None

    def apply_all_fixes(self, file_path: str) -> Optional[Tuple[str, str]]:
        """
        Apply all available fixes for a file.

        Args:
            file_path: Path to the file

        Returns:
            Tuple of (original_content, fixed_content) or None if no fixes
        """
        # Get diagnostics
        if file_path not in self._diagnostic_cache:
            self.check_file(file_path)

        diagnostics = self._diagnostic_cache.get(file_path, [])

        # Get file content
        if file_path in self._file_cache:
            content = self._file_cache[file_path][0]
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

        original_content = content
        fixed_content = content

        # Apply fixes in reverse order (to avoid line number issues)
        fixable_diagnostics = [
            d
            for d in diagnostics
            if d.fix is not None and SpellCheckAction.QUICK_FIX in d.actions
        ]

        fixable_diagnostics.sort(key=lambda d: d.line, reverse=True)

        fixes_applied = 0
        for diagnostic in fixable_diagnostics:
            fix = diagnostic.fix
            if "code_before" in fix and "code_after" in fix:
                # Apply the fix
                fixed_content = fixed_content.replace(
                    fix["code_before"], fix["code_after"]
                )
                fixes_applied += 1

        if fixes_applied > 0:
            # Update cache
            self._file_cache[file_path] = (fixed_content, time.time())
            self.total_fixes_applied += fixes_applied
            self.total_auto_fixes += fixes_applied

            return (original_content, fixed_content)

        return None

    def _check_missing_decorator(
        self, file_path: str, content: str
    ) -> List[SpellCheckDiagnostic]:
        """Check for missing @glass_box_boundary decorator."""
        diagnostics = []

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
                        # Create diagnostic
                        diagnostic_id = f"missing_decorator_{node.name}_{node.lineno}"

                        # Generate fix
                        fix = self._generate_decorator_fix(node, content)

                        diagnostic = SpellCheckDiagnostic(
                            diagnostic_id=diagnostic_id,
                            file_path=file_path,
                            line=node.lineno - 1,  # 0-based for IDE
                            column=node.col_offset,
                            end_line=node.lineno - 1,
                            end_column=node.col_offset + len(f"def {node.name}"),
                            severity=SpellCheckSeverity.ERROR,
                            message=f"Function '{node.name}' missing @glass_box_boundary decorator",
                            code="missing_boundary_decorator",
                            actions=[
                                SpellCheckAction.QUICK_FIX,
                                SpellCheckAction.SUGGEST_FIX,
                                SpellCheckAction.IGNORE,
                                SpellCheckAction.SHOW_DOCS,
                            ],
                            fix=fix,
                            tags=["boundary", "decorator", "function"],
                        )
                        diagnostics.append(diagnostic)
        except SyntaxError:
            # Skip files with syntax errors
            pass

        return diagnostics

    def _generate_decorator_fix(
        self, node: ast.FunctionDef, content: str
    ) -> Dict[str, Any]:
        """Generate fix for missing decorator."""
        lines = content.split("\n")
        function_line = lines[node.lineno - 1]

        # Simple decorator addition
        decorator_line = "@glass_box_boundary()"
        fixed_line = f"{decorator_line}\n{function_line}"

        return {
            "description": "Add @glass_box_boundary decorator",
            "code_before": function_line,
            "code_after": fixed_line,
            "application_instructions": f"Add @glass_box_boundary() decorator before function '{node.name}'",
        }

    def _check_broad_exception(
        self, file_path: str, content: str
    ) -> List[SpellCheckDiagnostic]:
        """Check for broad exception catching."""
        diagnostics = []
        lines = content.split("\n")

        pattern = r"except\s+(Exception|BaseException)\s*:"

        for i, line in enumerate(lines):
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                # Check if it's a "pass" or suppressed exception
                next_lines = lines[i + 1 : i + 4]
                is_suppressed = any("pass" in l.strip() for l in next_lines)

                severity = (
                    SpellCheckSeverity.ERROR
                    if is_suppressed
                    else SpellCheckSeverity.WARNING
                )

                # Create diagnostic
                diagnostic_id = f"broad_exception_{file_path}_{i + 1}"

                # Generate fix
                fix = self._generate_exception_f
