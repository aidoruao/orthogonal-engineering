#!/usr/bin/env python3
"""
COMPREHENSIVE FORGIVENESS SYSTEM FIX
Version: 2.0
Schema ID: FORGIVENESS-FIX-2.0
Generated: 2026-01-24
Authority: Orthogonal Engineering Glass-Box Boundary

Purpose: Fix all issues in forgiveness system with anti-gaslighting layer
Violation Source: [FORGIVENESS_SYSTEM_ATTACK_001]
Fork ID: [COMPREHENSIVE_FIX_FORK]
Energy Allocated: BUILD=0.7, FIGHT=0.0

Issues Fixed:
1. False positive detection (decoy violations)
2. Line number misalignment (epistemic landmines)
3. Missing real violations (absorption through overwhelm)
4. No anti-gaslighting protection
5. Buggy pattern matching logic
6. Incomplete violation counting

Atomic Fixes Applied:
1. Context-aware parsing (not line-number dependent)
2. Multiple validation methods (self-validating analysis)
3. Gaslighting detection layer
4. Violation density mapping
5. Comprehensive pattern matching
6. Evidence chain validation
"""

import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import statistics

# Import anti-gaslighting components
sys.path.append(str(Path(__file__).parent))
from gaslighting_detector import GaslightingDetector, EpistemicCorruptionAlert
from violation_density_mapper import ViolationDensityMapper, DensityMap


@dataclass
class FixedViolation:
    """Fixed violation record with anti-gaslighting protection"""
    violation_id: str
    timestamp: str
    chat_line: str
    line_number: int
    violation_type: str
    severity: str
    evidence_hash: str
    matched_pattern: str
    user_invariants: List[str]
    ai_response: Optional[str]

    # Anti-gaslighting fields
    context_window: str = ""
    validation_methods: List[str] = field(default_factory=list)
    confidence_score: float = 1.0
    gaslighting_checked: bool = False
    gaslighting_alerts: List[Dict] = field(default_factory=list)


@dataclass
class FixedAnalysisResult:
    """Fixed analysis result with comprehensive validation"""
    violations: List[FixedViolation]
    invariants_found: Dict[str, List[str]]
    governance_failures: List[Dict]
    stats: Dict[str, Any]
    analysis_timestamp: str
    validation_checks: Dict[str, bool]
    gaslighting_report: Optional[Dict] = None
    density_map: Optional[Dict] = None


class FixedChatExportAnalyzer:
    """Fixed chat analyzer with anti-gaslighting protection"""

    def __init__(self, chat_exports_path: Path):
        self.chat_exports_path = chat_exports_path
        self.gaslighting_detector = GaslightingDetector(chat_exports_path)
        self.density_mapper = ViolationDensityMapper()

        # Expanded violation patterns (more comprehensive)
        self.violation_patterns = self._get_expanded_patterns()

        # Compile patterns
        self.compiled_patterns = {
            vtype: [re.compile(p, re.IGNORECASE) for p in patterns]
            for vtype, patterns in self.violation_patterns.items()
        }

        # User invariant patterns
        self.user_invariant_patterns = {
            "workload": [
                r"5\.75.*hour.*part.*time",
                r"12.*classrooms",
                r"12.*bathrooms",
                r"15.*bathrooms.*total",
                r"4.*hallways",
                r"3.*more.*rooms",
                r"3.*more.*bathrooms",
            ],
            "time": [
                r"2.*hour.*break.*max",
                r"2-4.*hours.*overtime",
                r"almost.*everyday",
                r"frontloading",
            ],
            "compliance": [
                r"highly.*compliant",
                r"non.*disagreeable",
                r"should.*be.*legal",
                r"objectively.*ontologically",
            ],
        }

        # Governance failure patterns
        self.governance_failure_patterns = {
            "wage_theft_indicators": [
                r"clock.*out.*but.*keep.*working",
                r"hours.*edited.*down",
                r"not.*paid.*for.*overtime",
                r"pressured.*not.*record.*hours",
                r"part.*time.*to.*dodge.*OT",
            ],
            "boundary_testing": [
                r"gaslighting",
                r"defensive.*reaction",
                r"procedural.*entanglement",
                r"exhaustion",
                r"control",
            ],
            "epistemic_breach": [
                r"rationalization",
                r"clinical.*retreat",
                r"feedback.*absorption",
                r"layered.*control",
                r"invincibility.*mechanism",
            ],
        }

    def _get_expanded_patterns(self) -> Dict[str, List[str]]:
        """Get expanded violation patterns to catch more violations"""
        return {
            "workload_exploitation": [
                r"overtime.*almost.*daily",
                r"2-4 hours.*overtime",
                r"frontload.*legal",
                r"workload.*exceeds.*paid.*hours",
                r"unsustainable.*workload",
                r"exploit.*workload",
                r"abuse.*overtime",
                r"unpaid.*work",
                r"wage.*theft",
                r"time.*theft",
            ],
            "boundary_violation": [
                r"invariant.*violat",
                r"category.*error",
                r"not.*negotiable",
                r"fixed.*variable",
                r"ontological.*problem",
                r"boundary.*violat",
                r"limit.*violat",
                r"rule.*violat",
                r"policy.*violat",
                r"standard.*violat",
            ],
            "corporate_gaslighting": [
                r"legal.*but.*exploitative",
                r"not.*illegal.*but",
                r"management.*failure.*not.*crime",
                r"high.*workload.*≠.*illegal",
                r"operational.*overload",
                r"gaslight.*employee",
                r"manipulat.*perception",
                r"deny.*reality",
                r"shift.*blame",
                r"minimiz.*concern",
            ],
            "ai_rationalization": [
                r"let.*s.*ground.*objectively",
                r"important.*distinction",
                r"the.*question.*isn.*t",
                r"bottom.*line.*clear",
                r"short.*answer.*nothing.*illegal",
                r"technically.*correct",
                r"legally.*permissible",
                r"operationally.*necessary",
                r"procedurally.*sound",
                r"contextually.*appropriate",
            ],
            "invariant_ignoring": [
                r"treat.*as.*variable",
                r"depends.*on.*details",
                r"state.*law",
                r"hourly.*vs.*salaried",
                r"red.*flaggy",
                r"ignore.*invariant",
                r"override.*rule",
                r"bypass.*limit",
                r"circumvent.*policy",
                r"disregard.*standard",
            ],
            "meta_corruption": [
                r"false.*positive",
                r"bug.*in.*detection",
                r"wrong.*line.*number",
                r"miss.*violation",
                r"only.*\d+.*violation",
                r"404.*vs.*1",
                r"epistemic.*corruption",
                r"gaslight.*analysis",
                r"manipulat.*result",
                r"corrupt.*detection",
            ]
        }

    def analyze_chat_file_fixed(self, file_path: Path) -> FixedAnalysisResult:
        """
        Fixed analysis with anti-gaslighting protection

        Returns:
            FixedAnalysisResult with comprehensive validation
        """
        print(f"🔍 Analyzing {file_path.name} with fixed system...")

        violations = []
        invariants_found = {}
        governance_failures = []
        stats = {
            "total_lines": 0,
            "user_messages": 0,
            "ai_responses": 0,
            "violations_detected": 0,
            "invariants_extracted": 0,
            "governance_failures": 0,
        }

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split('\n')

            stats["total_lines"] = len(lines)

            # Process in semantic windows (not line-by-line)
            semantic_windows = self._create_semantic_windows(content, window_size=1000)

            for window_idx, window in enumerate(semantic_windows):
                window_violations = self._analyze_semantic_window(
                    window["text"],
                    window["start_line"],
                    window["end_line"]
                )
                violations.extend(window_violations)

            # Extract invariants
            invariants_found = self._extract_invariants(content)

            # Detect governance failures
            governance_failures = self._detect_governance_failures(content)

            # Update stats
            stats["violations_detected"] = len(violations)
            stats["invariants_extracted"] = sum(len(v) for v in invariants_found.values())
            stats["governance_failures"] = len(governance_failures)

            # Run gaslighting detection
            gaslighting_report = self._run_gaslighting_detection(
                violations, content, file_path.stat().st_size
            )

            # Create density map
            density_map = self._create_density_map(violations, file_path)

            # Run validation checks
            validation_checks = self._run_validation_checks(
                violations, content, file_path.stat().st_size
            )

            result = FixedAnalysisResult(
                violations=violations,
                invariants_found=invariants_found,
                governance_failures=governance_failures,
                stats=stats,
                analysis_timestamp=datetime.utcnow().isoformat(),
                validation_checks=validation_checks,
                gaslighting_report=gaslighting_report,
                density_map=density_map
            )

            print(f"✅ Analysis complete: {len(violations)} violations found")
            return result

        except Exception as e:
            print(f"❌ Error analyzing {file_path}: {e}")
            raise

    def _create_semantic_windows(self, content: str, window_size: int = 1000) -> List[Dict]:
        """Create semantic windows for context-aware analysis"""
        windows = []
        lines = content.split('\n')

        for i in range(0, len(lines), window_size):
            window_lines = lines[i:min(i + window_size, len(lines))]
            window_text = '\n'.join(window_lines)

            windows.append({
                "text": window_text,
                "start_line": i + 1,
                "end_line": min(i + window_size, len(lines)),
                "window_id": f"window_{i//window_size:04d}"
            })

        return windows

    def _analyze_semantic_window(
        self, window_text: str, start_line: int, end_line: int
    ) -> List[FixedViolation]:
        """Analyze a semantic window for violations"""
        violations = []
        window_lines = window_text.split('\n')

        for local_line_num, line in enumerate(window_lines):
            absolute_line_num = start_line + local_line_num

            # Skip trivial lines (anti-decoy protection)
            if self._is_trivial_line(line):
                continue

            # Check for violation patterns
            for vtype, patterns in self.compiled_patterns.items():
                for pattern in patterns:
                    if pattern.search(line):
                        # Get context window
                        context_start = max(0, local_line_num - 2)
                        context_end = min(len(window_lines), local_line_num + 3)
                        context = '\n'.join(window_lines[context_start:context_end])

                        # Check for gaslighting
                        gaslighting_alerts = self._check_gaslighting_patterns(
                            line, absolute_line_num, context, vtype
                        )

                        # Only create violation if not a decoy
                        if not self._is_decoy_violation(line, context, gaslighting_alerts):
                            violation = FixedViolation(
                                violation_id=f"violation_{hashlib.md5(line.encode()).hexdigest()[:8]}",
                                timestamp=datetime.utcnow().isoformat(),
                                chat_line=line[:200],
                                line_number=absolute_line_num,
                                violation_type=vtype,
                                severity=self._get_severity(vtype),
                                evidence_hash=hashlib.sha256(line.encode()).hexdigest(),
                                matched_pattern=pattern.pattern,
                                user_invariants=[],
                                ai_response=None,
                                context_window=context,
                                validation_methods=["pattern_match", "context_validation"],
                                confidence_score=0.9,
                                gaslighting_checked=True,
                                gaslighting_alerts=gaslighting_alerts
                            )
                            violations.append(violation)

                        break  # Only count first match per line per type

        return violations

    def _is_trivial_line(self, line: str) -> bool:
        """Check if line is trivial (decoy protection)"""
        trivial_patterns = [
            r"^\s*$",  # Whitespace only
            r"^[^a-z]*$",  # No lowercase letters
            r"^[A-Z][a-z]+\s+said:$",  # "X said:"
            r"^[^:]+:\s*$",  # Label with no content
            r"^---+\s*$",  # Separator lines
            r"^==+\s*$",  # Separator lines
        ]

        for pattern in trivial_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True

        return len(line.strip()) < 10  # Very short lines

    def _is_decoy_violation(self, line: str, context: str, gaslighting_alerts: List[Dict]) -> bool:
        """Check if violation is a decoy"""
        # Check if line is trivial
        if self._is_trivial_line(line):
            return True

        # Check if context has no substantial content
        context_lines = context.split('\n')
        substantial_lines = [l for l in context_lines if not self._is_trivial_line(l) and len(l.strip()) > 20]

        if len(substantial_lines) < 2:
            return True

        # Check for gaslighting alerts
        if any("decoy" in str(alert).lower() for alert in gaslighting_alerts):
            return True

        return False

    def _check_gaslighting_patterns(
        self, line: str, line_number: int, context: str, violation_type: str
    ) -> List[Dict]:
        """Check for gaslighting patterns"""
        alerts = []

        # Check for meta-corruption patterns
        if violation_type == "meta_corruption":
            alerts.append({
                "type": "meta_corruption_detected",
                "line": line_number,
                "pattern": "meta_corruption",
                "confidence": 0.8
            })

        # Check for decoy patterns
        if self._is_trivial_line(line):
            alerts.append({
                "type": "possible_decoy",
                "line": line_number,
                "pattern": "trivial_line",
                "confidence": 0.7
            })

        return alerts

    def _get_severity(self, violation_type: str) -> str:
        """Get severity for violation type"""
        severity_map = {
            "workload_exploitation": "critical",
            "corporate_gaslighting": "critical",
            "boundary_violation": "severe",
            "ai_rationalization": "severe",
            "invariant_ignoring": "moderate",
            "meta_corruption": "critical",
            # New violation types (regex-detectable)
            "authority_inversion": "critical",
            "theological_dismissal": "critical",
            "false_equivalence": "critical",
            "emotional_weaponization": "critical",
            # New violation types (semantic analysis required)
            "compliance_theater": "systemic",
            "phantom_compliance": "systemic",
            "recursive_deflection": "systemic",
            "scope_reduction": "critical",
            "polymathic_collapse": "critical",
            "expertise_erasure": "systemic",
            "scale_blindness": "critical",
            "context_assassination": "systemic",
        }
        return severity_map.get(violation_type, "moderate")

    def _extract_invariants(self, content: str) -> Dict[str, List[str]]:
        """Extract user invariants from content"""
        invariants_found = {}

        for invariant_type, patterns in self.user_invariant_patterns.items():
            invariants_found[invariant_type] = []
            for pattern_str in patterns:
                pattern = re.compile(pattern_str, re.IGNORECASE)
                matches = pattern.findall(content)
                invariants_found[invariant_type].extend(matches)

        return invariants_found

    def _detect_governance_failures(self, content: str) -> List[Dict]:
        """Detect corporate governance failures"""
        failures = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            for failure_type, patterns in self.governance_failure_patterns.items():
                for pattern_str in patterns:
                    pattern = re.compile(pattern_str, re.IGNORECASE)
                    if pattern.search(line):
                        failure = {
                            "type": failure_type,
                            "line_number": line_num,
                            "matched_text": pattern.search(line).group(),
                            "evidence_hash": hashlib.sha256(line.encode()).hexdigest(),
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                        failures.append(failure)
                        break

        return failures

    def _run_gaslighting_detection(
        self, violations: List[FixedViolation], content: str, file_size: int
    ) -> Optional[Dict]:
        """Run gaslighting detection on analysis results"""
        try:
            # Convert violations for gaslighting detector
            violation_dicts = []
            for v in violations:
                violation_dicts.append({
                    "line_number": v.line_number,
                    "violation_type":
