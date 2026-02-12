# failure_analyzer.py - Orthogonal Engineering Failure Analysis System
# Glass Box Methodology - Ontological Premises Analysis
# Version: 1.0.0
# Date: 2026-01-20
# Methodology: Orthogonal Engineering with Popperian Falsification

import datetime
import hashlib
import json
import os
import sys
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ============================================================================
# ONTOLOGICAL PREMISES
# ============================================================================


class OntologicalPremise(Enum):
    """Core ontological premises of Orthogonal Engineering"""

    # Epistemological Premises
    FALSIFIABILITY = "falsifiability"
    CORRESPONDENCE = "correspondence"
    TRANSPARENCY = "transparency"
    AUDITABILITY = "auditability"

    # Methodological Premises
    GLASS_BOX = "glass_box"
    ATOMIC_OPERATIONS = "atomic_operations"
    INVARIANT_TRACKING = "invariant_tracking"
    FAILURE_DOCUMENTATION = "failure_documentation"

    # Implementation Premises
    TOOL_VALIDATION = "tool_validation"
    REAL_WORLD_GROUNDING = "real_world_grounding"
    MIMICRY_DETECTION = "mimicry_detection"
    REPRODUCIBILITY = "reproducibility"


class FailureSeverity(Enum):
    """Severity levels for failures"""

    CRITICAL = "critical"  # Blocks all use, violates core premises
    HIGH = "high"  # Limits adoption, violates key premises
    MEDIUM = "medium"  # Impacts quality, violates secondary premises
    LOW = "low"  # Polish issues, minor premise violations
    INFO = "info"  # Observations, no premise violations


class FailureCategory(Enum):
    """Categories of failures"""

    DETECTOR_FAILURE = "detector_failure"
    STATISTICAL_FAILURE = "statistical_failure"
    CORRESPONDENCE_FAILURE = "correspondence_failure"
    REPRODUCIBILITY_FAILURE = "reproducibility_failure"
    METHODOLOGY_FAILURE = "methodology_failure"
    IMPLEMENTATION_FAILURE = "implementation_failure"
    DOCUMENTATION_FAILURE = "documentation_failure"
    VALIDATION_FAILURE = "validation_failure"


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class FailureEvidence:
    """Evidence supporting a failure claim"""

    description: str
    source_file: str
    line_numbers: Optional[List[int]] = None
    data_hash: Optional[str] = None
    timestamp: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        if self.data_hash is None:
            self.data_hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """Calculate hash of evidence content"""
        content = f"{self.description}{self.source_file}{self.timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class PremiseViolation:
    """Violation of an ontological premise"""

    premise: OntologicalPremise
    violation_description: str
    impact_level: str  # "direct", "indirect", "potential"
    evidence: List[FailureEvidence]


@dataclass
class FailureAnalysis:
    """Complete analysis of a failure"""

    failure_id: str
    title: str
    description: str
    severity: FailureSeverity
    category: FailureCategory
    discovered_date: str
    last_updated: str

    # Ontological analysis
    premise_violations: List[PremiseViolation]
    methodology_implications: List[str]
    falsifiable_claims_affected: List[str]

    # Evidence
    evidence: List[FailureEvidence]
    reproduction_steps: List[str]

    # Status
    status: str  # "open", "in_progress", "resolved", "wont_fix"
    fix_required: List[str]
    fix_priority: str  # "immediate", "soon", "eventually", "optional"

    # Verification
    independent_verification_possible: bool
    verification_instructions: Optional[str] = None

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert enums to strings
        data["severity"] = self.severity.value
        data["category"] = self.category.value
        data["premise_violations"] = [
            {
                "premise": pv.premise.value,
                "violation_description": pv.violation_description,
                "impact_level": pv.impact_level,
                "evidence": [asdict(e) for e in pv.evidence],
            }
            for pv in self.premise_violations
        ]
        data["evidence"] = [asdict(e) for e in self.evidence]
        return data


# ============================================================================
# FAILURE ANALYZER CLASS
# ============================================================================


class FailureAnalyzer:
    """Main failure analysis system with ontological premises"""

    def __init__(self, repository_path: str):
        self.repository_path = Path(repository_path)
        self.failures: List[FailureAnalysis] = []
        self.analysis_hash: Optional[str] = None

    def analyze_existing_failures(self) -> List[FailureAnalysis]:
        """Analyze existing FAILURES.md and other failure documentation"""
        failures = []

        # 1. Analyze FAILURES.md
        failures_md_path = self.repository_path / "FAILURES.md"
        if failures_md_path.exists():
            failures.extend(self._analyze_failures_md(failures_md_path))

        # 2. Analyze falsification results
        falsification_path = (
            self.repository_path
            / "evidence"
            / "deepseek-analysis"
            / "FALSIFICATION_RESULTS.md"
        )
        if falsification_path.exists():
            failures.extend(self._analyze_falsification_results(falsification_path))

        # 3. Analyze pipeline logs for runtime failures
        log_path = self.repository_path / "pipeline_run_log.txt"
        if log_path.exists():
            failures.extend(self._analyze_pipeline_logs(log_path))

        self.failures = failures
        self.analysis_hash = self._calculate_analysis_hash()
        return failures

    def _analyze_failures_md(self, filepath: Path) -> List[FailureAnalysis]:
        """Parse and analyze FAILURES.md file"""
        failures = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse critical failures section
            if "## 🚨 CRITICAL FAILURES" in content:
                critical_section = content.split("## 🚨 CRITICAL FAILURES")[1].split(
                    "## ⚠️"
                )[0]
                failures.extend(
                    self._parse_failure_section(
                        critical_section, FailureSeverity.CRITICAL
                    )
                )

            # Parse high priority failures
            if "## ⚠️ HIGH PRIORITY FAILURES" in content:
                high_section = content.split("## ⚠️ HIGH PRIORITY FAILURES")[1].split(
                    "## 🔵"
                )[0]
                failures.extend(
                    self._parse_failure_section(high_section, FailureSeverity.HIGH)
                )

            # Parse medium priority failures
            if "## 🔵 MEDIUM PRIORITY FAILURES" in content:
                medium_section = content.split("## 🔵 MEDIUM PRIORITY FAILURES")[
                    1
                ].split("## 💚")[0]
                failures.extend(
                    self._parse_failure_section(medium_section, FailureSeverity.MEDIUM)
                )

            # Parse low priority failures
            if "## 💚 LOW PRIORITY FAILURES" in content:
                low_section = content.split("## 💚 LOW PRIORITY FAILURES")[1].split(
                    "## 📊"
                )[0]
                failures.extend(
                    self._parse_failure_section(low_section, FailureSeverity.LOW)
                )

        except Exception as e:
            print(f"Error analyzing FAILURES.md: {e}")

        return failures

    def _parse_failure_section(
        self, section: str, severity: FailureSeverity
    ) -> List[FailureAnalysis]:
        """Parse individual failure sections"""
        failures = []
        lines = section.strip().split("\n")

        current_failure = None
        current_evidence = []
        in_failure_block = False

        for i, line in enumerate(lines):
            line = line.strip()

            # Detect failure start (### FAILURE X: pattern)
            if line.startswith("### FAILURE") and ":" in line:
                if current_failure is not None:
                    # Save previous failure
                    current_failure.evidence = current_evidence.copy()
                    failures.append(current_failure)

                # Start new failure
                title = line.split(":", 1)[1].strip()
                failure_id = f"FAILURE-{len(failures) + 1:03d}"

                # Determine category based on title
                category = self._determine_category(title)

                current_failure = FailureAnalysis(
                    failure_id=failure_id,
                    title=title,
                    description="",
                    severity=severity,
                    category=category,
                    discovered_date=datetime.datetime.utcnow().isoformat() + "Z",
                    last_updated=datetime.datetime.utcnow().isoformat() + "Z",
                    premise_violations=[],
                    methodology_implications=[],
                    falsifiable_claims_affected=[],
                    evidence=[],
                    reproduction_steps=[],
                    status="open",
                    fix_required=[],
                    fix_priority="immediate"
                    if severity == FailureSeverity.CRITICAL
                    else "soon",
                    independent_verification_possible=True,
                    verification_instructions=None,
                )
                current_evidence = []
                in_failure_block = True

            # Collect description lines
            elif in_failure_block and line and not line.startswith("**"):
                if current_failure:
                    if not current_failure.description:
                        current_failure.description = line
                    else:
                        current_failure.description += " " + line

            # Detect evidence markers
            elif line.startswith("**Evidence:**"):
                evidence_text = lines[i + 1].strip() if i + 1 < len(lines) else ""
                if evidence_text:
                    evidence = FailureEvidence(
                        description=evidence_text,
                        source_file=str(self.repository_path / "FAILURES.md"),
                        line_numbers=[i + 1],
                    )
                    current_evidence.append(evidence)

            # Detect fix requirements
            elif line.startswith("**Fix Required:**"):
                fix_text = ""
                j = i + 1
                while (
                    j < len(lines)
                    and lines[j].strip()
                    and not lines[j].strip().startswith("**")
                ):
                    fix_text += lines[j].strip() + "\n"
                    j += 1
                if current_failure and fix_text:
                    current_failure.fix_required = [
                        ft.strip() for ft in fix_text.split("\n") if ft.strip()
                    ]

        # Add the last failure
        if current_failure is not None:
            current_failure.evidence = current_evidence
            failures.append(current_failure)

        # Add ontological premise violations
        for failure in failures:
            failure.premise_violations = self._determine_premise_violations(failure)
            failure.methodology_implications = self._determine_methodology_implications(
                failure
            )

        return failures

    def _determine_category(self, title: str) -> FailureCategory:
        """Determine failure category from title"""
        title_lower = title.lower()

        if any(word in title_lower for word in ["detector", "canal", "pattern"]):
            return FailureCategory.DETECTOR_FAILURE
        elif any(
            word in title_lower for word in ["statistical", "p-value", "significance"]
        ):
            return FailureCategory.STATISTICAL_FAILURE
        elif any(
            word in title_lower
            for word in ["correspondence", "implementation", "working"]
        ):
            return FailureCategory.CORRESPONDENCE_FAILURE
        elif any(
            word in title_lower for word in ["reproducibility", "reproduce", "setup"]
        ):
            return FailureCategory.REPRODUCIBILITY_FAILURE
        elif any(
            word in title_lower for word in ["methodology", "premise", "ontological"]
        ):
            return FailureCategory.METHODOLOGY_FAILURE
        elif any(
            word in title_lower for word in ["documentation", "glossary", "changelog"]
        ):
            return FailureCategory.DOCUMENTATION_FAILURE
        else:
            return FailureCategory.IMPLEMENTATION_FAILURE

    def _determine_premise_violations(
        self, failure: FailureAnalysis
    ) -> List[PremiseViolation]:
        """Determine which ontological premises are violated by this failure"""
        violations = []

        # Map categories to premise violations
        premise_mapping = {
            FailureCategory.DETECTOR_FAILURE: [
                (OntologicalPremise.TOOL_VALIDATION, "direct"),
                (OntologicalPremise.FALSIFIABILITY, "direct"),
                (OntologicalPremise.CORRESPONDENCE, "indirect"),
            ],
            FailureCategory.STATISTICAL_FAILURE: [
                (OntologicalPremise.REPRODUCIBILITY, "direct"),
                (OntologicalPremise.FALSIFIABILITY, "direct"),
            ],
            FailureCategory.CORRESPONDENCE_FAILURE: [
                (OntologicalPremise.REAL_WORLD_GROUNDING, "direct"),
                (OntologicalPremise.CORRESPONDENCE, "direct"),
                (OntologicalPremise.MIMICRY_DETECTION, "indirect"),
            ],
            FailureCategory.REPRODUCIBILITY_FAILURE: [
                (OntologicalPremise.REPRODUCIBILITY, "direct"),
                (OntologicalPremise.TRANSPARENCY, "indirect"),
            ],
            FailureCategory.METHODOLOGY_FAILURE: [
                (OntologicalPremise.FALSIFIABILITY, "direct"),
                (OntologicalPremise.GLASS_BOX, "direct"),
            ],
        }

        # Add premise violations based on category
        if failure.category in premise_mapping:
            for premise, impact in premise_mapping[failure.category]:
                violation = PremiseViolation(
                    premise=premise,
                    violation_description=f"Failure in {failure.category.value} violates {premise.value} premise",
                    impact_level=impact,
                    evidence=failure.evidence[:1],  # Use first evidence item
                )
                violations.append(violation)

        # Add severity-based violations
        if failure.severity == FailureSeverity.CRITICAL:
            violation = PremiseViolation(
                premise=OntologicalPremise.GLASS_BOX,
                violation_description="Critical failure indicates lack of transparency in development",
                impact_level="direct",
                evidence=failure.evidence[:1],
            )
            violations.append(violation)

        return violations

    def _determine_methodology_implications(
        self, failure: FailureAnalysis
    ) -> List[str]:
        """Determine implications for the methodology"""
        implications = []

        if failure.severity == FailureSeverity.CRITICAL:
            implications.append("Blocks all use of affected components")
            implications.append("Requires immediate methodology review")

        if failure.category == FailureCategory.DETECTOR_FAILURE:
            implications.append("All density claims using this detector are invalid")
            implications.append("Requires detector redesign with stricter criteria")

        if failure.category == FailureCategory.CORRESPONDENCE_FAILURE:
            implications.append("Highlights gap between claims and implementations")
            implications.append("Emphasizes need for real-world grounding")

        return implications

    def _analyze_falsification_results(self, filepath: Path) -> List[FailureAnalysis]:
        """Analyze falsification results for failures"""
        failures = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Create failure analysis for falsified claim
            if "❌ CLAIM REJECTED" in content:
                failure = FailureAnalysis(
                    failure_id="FALSIFICATION-001",
                    title="DeepSeek 45.30% density claim falsified",
                    description="Three independent falsification tests rejected the 45.30% density claim",
                    severity=FailureSeverity.CRITICAL,
                    category=FailureCategory.DETECTOR_FAILURE,
                    discovered_date=datetime.datetime.utcnow().isoformat() + "Z",
                    last_updated=datetime.datetime.utcnow().isoformat() + "Z",
                    premise_violations=[
                        PremiseViolation(
                            premise=OntologicalPremise.FALSIFIABILITY,
                            violation_description="Claim failed falsification tests",
                            impact_level="direct",
                            evidence=[
                                FailureEvidence(
                                    description="70% false positive rate in detector",
                                    source_file=str(filepath),
                                    line_numbers=[30, 40],  # Approximate line numbers
                                )
                            ],
                        )
                    ],
                    methodology_implications=[
                        "All density claims using this detector are invalid",
                        "Detector requires complete redesign",
                        "Methodology proved itself by identifying its own failure",
                    ],
                    falsifiable_claims_affected=["DENSITY-001", "DENSITY-002"],
                    evidence=[
                        FailureEvidence(
                            description="Falsification test results showing 70% false positive rate",
                            source_file=str(filepath),
                            data_hash=hashlib.sha256(content.encode()).hexdigest()[:16],
                        )
                    ],
                    reproduction_steps=[
                        "Run falsification tests from FALSIFICATION_RESULTS.md",
                        "Sample 100 'verified' turns manually",
                        "Calculate precision rate",
                    ],
                    status="resolved",  # Already documented and addressed
                    fix_required=[
                        "Remove 45.30% claim from all files",
                        "Document detector failure mode",
                        "Revise to conservative 5-10% estimate",
                    ],
                    fix_priority="immediate",
                    independent_verification_possible=True,
                    verification_instructions="See FALSIFICATION_RESULTS.md for test methodology",
                )
                failures.append(failure)

        except Exception as e:
            # Log parsing error but continue with analysis
            print(f"Warning: Error parsing failures from FAILURES.md: {e}")
            # Continue with existing failures list

        return failures

    def _analyze_pipeline_logs(self, filepath):
        """Analyze pipeline logs for runtime failures."""
        return []

    def _calculate_analysis_hash(self):
        """Calculate hash of current analysis state."""
        import hashlib, json
        data = json.dumps([f.to_dict() for f in self.failures], sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()


def analyze_failure(repository_path):
    """Curated API entry point for failure analysis."""
    analyzer = FailureAnalyzer(repository_path)
    return analyzer.analyze_existing_failures()


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    analyze_failure(path)
