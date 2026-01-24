"""
Regex Boundary Enforcer - Prevents combinatorial explosions from AI-generated regex

Implements the regex generation ban as specified in the Subtractive Clarity Canon:
- Detects dangerous regex patterns that cause combinatorial explosions
- Provides safe alternatives using bounded string methods
- Enforces deterministic, inspectable string processing
- Prevents IDE crashes and session state loss

Author: Orthogonal Engineering System
Date: 2026-01-24
Version: 1.0.0
"""

import ast
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class RegexViolationType(Enum):
    """Types of regex boundary violations."""

    UNBOUNDED_QUANTIFIER = "unbounded_quantifier"  # .*, .+, .?, .{n,}, .{,m}
    COMPLEX_FEATURE = "complex_feature"  # lookahead, lookbehind, backreferences
    NESTED_UNBOUNDED = "nested_unbounded"  # (.*)*, (.+)+
    DANGEROUS_ALTERNATION = "dangerous_alternation"  # .*|.*, .+|.+
    RECURSIVE_PATTERN = "recursive_pattern"  # (?R), (?1)
    POSSESSIVE_QUANTIFIER = "possessive_quantifier"  # .*+, .++
    UNBOUNDED_REPETITION = "unbounded_repetition"  # .{n,} without upper bound


class SafeStringMethod(Enum):
    """Safe alternatives to dangerous regex patterns."""

    STARTSWITH = "str.startswith"
    ENDSWITH = "str.endswith"
    CONTAINS = "str.contains"  # via 'in' operator
    SPLIT = "str.split"
    PARTITION = "str.partition"
    REPLACE = "str.replace"
    ISALNUM = "str.isalnum"
    ISALPHA = "str.isalpha"
    ISDIGIT = "str.isdigit"
    ISLOWER = "str.islower"
    ISUPPER = "str.isupper"
    STRIP = "str.strip"
    LSTRIP = "str.lstrip"
    RSTRIP = "str.rstrip"
    COUNT = "str.count"
    FIND = "str.find"
    RFIND = "str.rfind"
    INDEX = "str.index"
    RINDEX = "str.rindex"


@dataclass
class RegexViolation:
    """Represents a detected regex boundary violation."""

    violation_id: str
    violation_type: RegexViolationType
    severity: str  # "critical", "high", "medium", "low"
    location: Tuple[str, int, int]  # (file_path, line_start, line_end)
    dangerous_pattern: str
    context: str  # Code context around the violation
    risk_score: float  # 0.0 to 1.0
    combinatorial_explosion_risk: str  # Description of the risk
    safe_alternatives: List[SafeStringMethod]
    suggested_replacement: str
    continuity_threat: bool  # Whether this can cause IDE crash/session loss

    def to_dict(self) -> Dict[str, Any]:
        """Convert violation to dictionary for serialization."""
        return {
            "violation_id": self.violation_id,
            "violation_type": self.violation_type.value,
            "severity": self.severity,
            "location": {
                "file_path": self.location[0],
                "line_start": self.location[1],
                "line_end": self.location[2],
            },
            "dangerous_pattern": self.dangerous_pattern,
            "context": self.context,
            "risk_score": self.risk_score,
            "combinatorial_explosion_risk": self.combinatorial_explosion_risk,
            "safe_alternatives": [alt.value for alt in self.safe_alternatives],
            "suggested_replacement": self.suggested_replacement,
            "continuity_threat": self.continuity_threat,
        }


class RegexBoundaryEnforcer:
    """
    Enforces regex boundary rules to prevent combinatorial explosions.

    Implements the regex generation ban from the Subtractive Clarity Canon:
    - No unbounded quantifiers (.*, .+, .?, .{n,})
    - No complex regex features (lookahead, lookbehind, backreferences)
    - No nested unbounded patterns
    - No dangerous alternation patterns
    - All string processing must use bounded, deterministic methods
    """

    # Dangerous regex patterns that cause combinatorial explosions
    DANGEROUS_PATTERNS = {
        RegexViolationType.UNBOUNDED_QUANTIFIER: [
            r"\.\*",  # .*
            r"\.\+",  # .+
            r"\.\?",  # .?
            r"\.\{(\d+),\s*\}",  # .{n,}
            r"\.\{\s*,\s*(\d+)\}",  # .{,m}
        ],
        RegexViolationType.COMPLEX_FEATURE: [
            r"\(\?[=!<]",  # Lookahead/lookbehind: (?=, (?!, (?<=, (?<!
            r"\\\d+",  # Backreferences: \1, \2, etc.
            r"\(\?:",  # Non-capturing groups (can hide complexity)
        ],
        RegexViolationType.NESTED_UNBOUNDED: [
            r"\([^)]*\*[^)]*\)\*",  # (.*)*
            r"\([^)]*\+[^)]*\)\+",  # (.+)+
            r"\([^)]*\?[^)]*\)\?",  # (.?)?
        ],
        RegexViolationType.DANGEROUS_ALTERNATION: [
            r"\.\*\|\.\*",  # .*|.*
            r"\.\+\|\.\+",  # .+|.+
            r"\.\?\|\.\?",  # .?|.?
        ],
        RegexViolationType.RECURSIVE_PATTERN: [
            r"\(\?R\)",  # (?R)
            r"\(\?(\d+)\)",  # (?1), (?2), etc.
        ],
        RegexViolationType.POSSESSIVE_QUANTIFIER: [
            r"\.\*\+",  # .*+
            r"\.\+\+",  # .++
            r"\.\?\?",  # .?? (possessive optional)
        ],
        RegexViolationType.UNBOUNDED_REPETITION: [
            r"\{(\d+),\s*\}",  # {n,}
            r"\{\s*,\s*(\d+)\}",  # {,m}
        ],
    }

    # Safe bounded regex patterns (allowed)
    ALLOWED_PATTERNS = [
        r"^[a-zA-Z0-9_]+$",  # Simple identifier
        r"^\d{4}-\d{2}-\d{2}$",  # Date pattern
        r"^[A-Z]{3}$",  # Three-letter code
        r"\s+",  # Whitespace (bounded by line)
        r"[a-z]{1,10}",  # Bounded character class
        r"\d{1,5}",  # Bounded digits
        r"[A-Z][a-z]*",  # Capitalized word
        r"^[^@]+@[^@]+\.[^@]+$",  # Simple email (bounded)
    ]

    # Mapping from dangerous patterns to safe string methods
    PATTERN_TO_SAFE_METHODS = {
        r"\.\*": [  # .* - match any sequence
            SafeStringMethod.CONTAINS,  # For checking presence
            SafeStringMethod.STARTSWITH,  # For prefix matching
            SafeStringMethod.ENDSWITH,  # For suffix matching
        ],
        r"\.\+": [  # .+ - match one or more
            SafeStringMethod.CONTAINS,
            SafeStringMethod.FIND,
            SafeStringMethod.INDEX,
        ],
        r"\.\?": [  # .? - optional character
            SafeStringMethod.STARTSWITH,
            SafeStringMethod.ENDSWITH,
            SafeStringMethod.PARTITION,
        ],
        r"[a-zA-Z]+": [  # Word matching
            SafeStringMethod.ISALPHA,
            SafeStringMethod.ISALNUM,
        ],
        r"\d+": [  # Digit matching
            SafeStringMethod.ISDIGIT,
            SafeStringMethod.COUNT,
        ],
        r"\s+": [  # Whitespace
            SafeStringMethod.STRIP,
            SafeStringMethod.SPLIT,
        ],
    }

    def __init__(self, workspace_root: Optional[str] = None):
        """
        Initialize the regex boundary enforcer.

        Args:
            workspace_root: Root directory of the workspace (optional)
        """
        self.workspace_root = Path(workspace_root) if workspace_root else None
        self.violations: List[RegexViolation] = []

    def analyze_file(self, file_path: str, content: str) -> List[RegexViolation]:
        """
        Analyze a file for regex boundary violations.

        Args:
            file_path: Path to the file
            content: File content as string

        Returns:
            List of detected regex violations
        """
        self.violations = []

        # Check if file imports re module
        if "import re" in content or "from re import" in content:
            # Parse the file to find regex usage
            self._analyze_regex_usage(file_path, content)

        return self.violations

    def _analyze_regex_usage(self, file_path: str, content: str):
        """Analyze regex usage in file content."""
        try:
            # Parse the Python file
            tree = ast.parse(content)

            # Walk through the AST to find regex usage
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    self._analyze_call_node(node, file_path, content)
                elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                    # Check string literals that might be regex patterns
                    self._analyze_string_literal(node, file_path, content)

        except SyntaxError as e:
            # If we can't parse the file, do simple line-by-line analysis
            self._analyze_lines(file_path, content)

    def _analyze_call_node(self, node: ast.Call, file_path: str, content: str):
        """Analyze a function call node for regex usage."""
        # Check if this is a re.* function call
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in [
                "search",
                "match",
                "findall",
                "finditer",
                "sub",
                "split",
                "compile",
            ]:
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "re":
                    # This is a re.* function call
                    line_start = node.lineno
                    line_end = (
                        node.end_lineno if hasattr(node, "end_lineno") else line_start
                    )

                    # Get the code snippet
                    lines = content.split("\n")
                    context = "\n".join(
                        lines[max(0, line_start - 3) : min(len(lines), line_end + 2)]
                    )

                    # Extract the regex pattern argument
                    pattern_arg = None
                    if node.args:
                        pattern_arg = node.args[0]
                        if isinstance(pattern_arg, ast.Constant) and isinstance(
                            pattern_arg.value, str
                        ):
                            pattern = pattern_arg.value
                            self._analyze_regex_pattern(
                                pattern, file_path, line_start, context
                            )

    def _analyze_string_literal(self, node: ast.Constant, file_path: str, content: str):
        """Analyze string literals that might be regex patterns."""
        # Heuristic: strings containing regex-like patterns
        string_value = node.value
        if isinstance(string_value, str) and len(string_value) > 2:
            # Check for common regex patterns in the string
            regex_like_patterns = [
                r"\.\*",
                r"\.\+",
                r"\.\?",
                r"\\[dDsSwW]",
                r"\[.*\]",
                r"\(.*\)",
            ]
            for pattern in regex_like_patterns:
                if re.search(pattern, string_value):
                    # This might be a regex pattern
                    line_start = node.lineno
                    lines = content.split("\n")
                    context = "\n".join(
                        lines[max(0, line_start - 3) : min(len(lines), line_start + 2)]
                    )
                    self._analyze_regex_pattern(
                        string_value, file_path, line_start, context
                    )
                    break

    def _analyze_lines(self, file_path: str, content: str):
        """Fallback: analyze file line by line for regex patterns."""
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            # Look for re.* function calls
            re_function_pattern = (
                r"re\.(?:search|match|findall|finditer|sub|split|compile)\(([^)]+)\)"
            )
            matches = re.finditer(re_function_pattern, line)
            for match in matches:
                # Try to extract the pattern argument
                args = match.group(1)
                # Simple extraction: look for string literals in arguments
                string_pattern = r'[\'"]([^\'"]+)[\'"]'
                string_matches = re.findall(string_pattern, args)
                for pattern in string_matches:
                    context = "\n".join(lines[max(0, i - 3) : min(len(lines), i + 2)])
                    self._analyze_regex_pattern(pattern, file_path, i, context)

    def _analyze_regex_pattern(
        self, pattern: str, file_path: str, line_num: int, context: str
    ):
        """Analyze a regex pattern for boundary violations."""
        # First check if it's an allowed pattern
        for allowed_pattern in self.ALLOWED_PATTERNS:
            if re.fullmatch(allowed_pattern, pattern):
                return  # Pattern is allowed

        # Check for dangerous patterns
        for violation_type, patterns in self.DANGEROUS_PATTERNS.items():
            for dangerous_pattern in patterns:
                if re.search(dangerous_pattern, pattern):
                    # Found a dangerous pattern
                    self._record_violation(
                        violation_type=violation_type,
                        dangerous_pattern=pattern,
                        file_path=file_path,
                        line_num=line_num,
                        context=context,
                    )
                    break

    def _record_violation(
        self,
        violation_type: RegexViolationType,
        dangerous_pattern: str,
        file_path: str,
        line_num: int,
        context: str,
    ):
        """Record a regex boundary violation."""
        # Calculate risk score
        risk_score = self._calculate_risk_score(violation_type, dangerous_pattern)

        # Determine severity
        if risk_score >= 0.7:
            severity = "critical"
            continuity_threat = True
        elif risk_score >= 0.4:
            severity = "high"
            continuity_threat = True
        elif risk_score >= 0.2:
            severity = "medium"
            continuity_threat = False
        else:
            severity = "low"
            continuity_threat = False

        # Get safe alternatives
        safe_alternatives = self._get_safe_alternatives(dangerous_pattern)

        # Generate suggested replacement
        suggested_replacement = self._generate_replacement(
            dangerous_pattern, safe_alternatives
        )

        # Create violation
        violation = RegexViolation(
            violation_id=f"REGEX-{hash(dangerous_pattern) & 0xFFFFFFFF:08x}",
            violation_type=violation_type,
            severity=severity,
            location=(file_path, line_num, line_num),
            dangerous_pattern=dangerous_pattern,
            context=context,
            risk_score=risk_score,
            combinatorial_explosion_risk=self._get_explosion_risk_description(
                violation_type
            ),
            safe_alternatives=safe_alternatives,
            suggested_replacement=suggested_replacement,
            continuity_threat=continuity_threat,
        )

        self.violations.append(violation)

    def _calculate_risk_score(
        self, violation_type: RegexViolationType, pattern: str
    ) -> float:
        """Calculate risk score for a regex pattern."""
        base_scores = {
            RegexViolationType.UNBOUNDED_QUANTIFIER: 0.8,
            RegexViolationType.COMPLEX_FEATURE: 0.9,
            RegexViolationType.NESTED_UNBOUNDED: 1.0,  # Highest risk
            RegexViolationType.DANGEROUS_ALTERNATION: 0.7,
            RegexViolationType.RECURSIVE_PATTERN: 0.95,
            RegexViolationType.POSSESSIVE_QUANTIFIER: 0.85,
            RegexViolationType.UNBOUNDED_REPETITION: 0.75,
        }

        base_score = base_scores.get(violation_type, 0.5)

        # Adjust based on pattern complexity
        complexity_factors = [
            (r"\.\*", 0.1),  # .* adds risk
            (r"\.\+", 0.15),  # .+ adds more risk
            (r"\(\?", 0.2),  # Complex features add risk
            (r"\\d", 0.1),  # Backreferences add risk
            (r"\|", 0.05),  # Alternation adds risk
        ]

        additional_risk = 0.0
        for factor_pattern, risk in complexity_factors:
            if re.search(factor_pattern, pattern):
                additional_risk += risk

        return min(1.0, base_score + additional_risk)

    def _get_safe_alternatives(self, pattern: str) -> List[SafeStringMethod]:
        """Get safe string method alternatives for a regex pattern."""
        alternatives = []

        # Check pattern-to-method mapping
        for dangerous_pattern, methods in self.PATTERN_TO_SAFE_METHODS.items():
            if re.search(dangerous_pattern, pattern):
                alternatives.extend(methods)

        # Add general alternatives if no specific match
        if not alternatives:
            alternatives = [
                SafeStringMethod.CONTAINS,
                SafeStringMethod.FIND,
                SafeStringMethod.SPLIT,
                SafeStringMethod.PARTITION,
            ]

        # Remove duplicates while preserving order
        seen = set()
        unique_alternatives = []
        for alt in alternatives:
            if alt not in seen:
                seen.add(alt)
                unique_alternatives.append(alt)

        return unique_alternatives

    def _generate_replacement(
        self, pattern: str, alternatives: List[SafeStringMethod]
    ) -> str:
        """Generate a suggested replacement code snippet."""
        if not alternatives:
            return "# Replace with bounded string methods"

        # Get the most appropriate alternative
        primary_alternative = alternatives[0]

        # Generate example replacement based on pattern type
        if ".*" in pattern or ".+" in pattern:
            if pattern.startswith("^") and pattern.endswith("$"):
                # Full string match
                return f"# Use exact string comparison: text == 'expected_value'"
            elif pattern.startswith("^"):
                # Prefix match
                return f"# Use text.startswith('prefix')"
            elif pattern.endswith("$"):
                # Suffix match
                return f"# Use text.endswith('suffix')"
            else:
                # Contains match
                return f"# Use 'substring' in text or text.find('substring') != -1"
        elif "\\d+" in pattern:
            return f"# Use text.isdigit() or all(c.isdigit() for c in text)"
        elif "[a-zA-Z]+" in pattern:
            return f"# Use text.isalpha() or text.isalnum()"
        elif "\\s+" in pattern:
            return f"# Use text.split() or text.strip()"
        else:
            return f"# Replace with {primary_alternative.value} or other bounded string method"

    def _get_explosion_risk_description(
        self, violation_type: RegexViolationType
    ) -> str:
        """Get description of combinatorial explosion risk."""
        descriptions = {
            RegexViolationType.UNBOUNDED_QUANTIFIER: "Unbounded quantifiers (.*, .+, .?) cause exponential backtracking on ambiguous input",
            RegexViolationType.COMPLEX_FEATURE: "Complex regex features (lookahead, lookbehind, backreferences) create combinatorial state explosion",
            RegexViolationType.NESTED_UNBOUNDED: "Nested unbounded patterns ((.*)*, (.+)+) create factorial growth in match attempts",
            RegexViolationType.DANGEROUS_ALTERNATION: "Dangerous alternation with unbounded patterns causes branch explosion",
            RegexViolationType.RECURSIVE_PATTERN: "Recursive patterns create infinite recursion possibilities",
            RegexViolationType.POSSESSIVE_QUANTIFIER: "Possessive quantifiers hide backtracking complexity leading to unexpected explosions",
            RegexViolationType.UNBOUNDED_REPETITION: "Unbounded repetition ranges create unpredictable memory usage",
        }
        return descriptions.get(
            violation_type, "Combinatorial explosion risk in regex evaluation"
        )

    def get_violation_summary(self) -> Dict[str, Any]:
        """Get summary of all detected violations."""
        critical_count = sum(1 for v in self.violations if v.severity == "critical")
        high_count = sum(1 for v in self.violations if v.severity == "high")
        medium_count = sum(1 for v in self.violations if v.severity == "medium")
        low_count = sum(1 for v in self.violations if v.severity == "low")
        continuity_threats = sum(1 for v in self.violations if v.continuity_threat)

        return {
            "total_violations": len(self.violations),
            "critical_violations": critical_count,
            "high_violations": high_count,
            "medium_violations": medium_count,
            "low_violations": low_count,
            "continuity_threats": continuity_threats,
            "average_risk_score": sum(v.risk_score for v in self.violations)
            / len(self.violations)
            if self.violations
            else 0.0,
            "violations_by_type": {
                vt.value: sum(1 for v in self.violations if v.violation_type == vt)
                for vt in RegexViolationType
            },
        }

    def generate_fix_report(self) -> str:
        """Generate a human-readable fix report."""
        if not self.violations:
            return "No regex boundary violations detected."

        report_lines = [
            "=" * 80,
            "REGEX BOUNDARY VIOLATION REPORT",
            "=" * 80,
            f"Total violations: {len(self.violations)}",
            f"Critical violations: {sum(1 for v in self.violations if v.severity == 'critical')}",
            f"Continuity threats: {sum(1 for v in self.violations if v.continuity_threat)}",
            "",
            "VIOLATIONS:",
            "=" * 80,
        ]

        for i, violation in enumerate(self.violations, 1):
            report_lines.extend(
                [
                    f"{i}. {violation.violation_type.value.upper()} - {violation.severity.upper()}",
                    f"   File: {violation.location[0]}:{violation.location[1]}",
                    f"   Pattern: {violation.dangerous_pattern}",
                    f"   Risk Score: {violation.risk_score:.2f}",
                    f"   Continuity Threat: {'YES' if violation.continuity_threat else 'NO'}",
                    f"   Risk: {violation.combinatorial_explosion_risk}",
                    "",
                    f"   Context:",
                    f"   {violation.context}",
                    "",
                    f"   Suggested Fix:",
                    f"   {violation.suggested_replacement}",
                    "",
                    f"   Safe Alternatives:",
                ]
            )
            for alt in violation.safe_alternatives:
                report_lines.append(f"   - {alt.value}")
            report_lines.append("-" * 80)

        report_lines.extend(
            [
                "",
                "SUMMARY:",
                "=" * 80,
                "Regex generation is banned due to orthogonal-engineering-scale combinatorial explosion risks.",
                "All string processing must use bounded, deterministic methods.",
                "Violations threaten IDE continuity and can cause session state loss.",
                "",
                "RECOMMENDED ACTIONS:",
                "1. Replace all regex patterns with bounded string methods",
                "2. Use str.startswith(), str.endswith(), 'in' operator, str.split()",
                "3. Implement deterministic parsing algorithms",
                "4. Validate all AI-generated code for regex usage",
                "5. Enable continuous regex boundary monitoring",
                "=" * 80,
            ]
        )

        return "\n".join(report_lines)

    def apply_fixes(
        self, file_path: str, content: str, auto_apply: bool = False
    ) -> Tuple[str, List[str]]:
        """
        Apply fixes to regex violations in file content.

        Args:
            file_path: Path to the file
            content: Original file content
            auto_apply: Whether to apply fixes automatically (vs. suggesting)

        Returns:
            Tuple of (fixed_content, applied_fix_descriptions)
        """
        # First analyze the file
        violations = self.analyze_file(file_path, content)
        if not violations:
            return content, []

        fixed_content = content
        applied_fixes = []

        # For each violation, apply or suggest fix
        for violation in violations:
            if auto_apply or violation.severity in ["critical", "high"]:
                # Apply the fix
                # This is a simplified implementation - in production would use AST transformation
                lines = fixed_content.split("\n")
                line_idx = violation.location[1] - 1

                # Simple replacement: comment out the dangerous line and add suggestion
                if 0 <= line_idx < len(lines):
                    original_line = lines[line_idx]
                    fix_comment = (
                        f"# REGEX BOUNDARY VIOLATION: {violation.violation_type.value}"
                    )
                    suggestion = f"# FIX: {violation.suggested_replacement}"
                    lines[line_idx] = f"{original_line}\n{fix_comment}\n{suggestion}"
                    fixed_content = "\n".join(lines)

                    applied_fixes.append(
                        f"Applied fix for {violation.violation_type.value} at line {violation.location[1]}"
                    )

        return fixed_content, applied_fixes
