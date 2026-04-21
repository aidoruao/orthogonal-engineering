# failure_report_generator.py - Orthogonal Engineering Failure Report Generator
# Glass Box Methodology - Comprehensive Failure Analysis Reports
# Version: 1.0.0
# Date: 2026-01-20
# Methodology: Orthogonal Engineering with Popperian Falsification

import datetime
import hashlib
import json
import os
import sys
import textwrap
from collections import defaultdict
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ============================================================================
# REPORT TYPES
# ============================================================================


class ReportType(Enum):
    """Types of failure analysis reports"""

    # Individual Failure Reports
    FAILURE_ANALYSIS = "failure_analysis"  # Detailed analysis of single failure
    FALSIFICATION_REPORT = (
        "falsification_report"  # Report on falsification test failure
    )
    CORRESPONDENCE_REPORT = "correspondence_report"  # Correspondence validation failure

    # Aggregate Reports
    METHODOLOGY_HEALTH = "methodology_health"  # Overall methodology health
    TOOL_VALIDATION = "tool_validation"  # Tool validation status
    ONTOLOGICAL_AUDIT = "ontological_audit"  # Audit of ontological premises

    # Trend Reports
    FAILURE_TRENDS = "failure_trends"  # Failure trends over time
    RESOLUTION_ANALYSIS = "resolution_analysis"  # Analysis of failure resolutions

    # Special Reports
    CRITICAL_FAILURE_SUMMARY = (
        "critical_failure_summary"  # Summary of critical failures
    )
    GLASS_BOX_COMPLIANCE = "glass_box_compliance"  # Glass box compliance report


class ReportFormat(Enum):
    """Output formats for reports"""

    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    PLAIN_TEXT = "plain_text"
    CSV = "csv"


# ============================================================================
# REPORT STRUCTURES
# ============================================================================


@dataclass
class ReportMetadata:
    """Metadata for failure analysis reports"""

    report_id: str
    report_type: ReportType
    generated_at: str
    generator_version: str = "1.0.0"
    methodology_version: str = "orthogonal-engineering-v1.0"
    report_hash: Optional[str] = None

    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.datetime.utcnow().isoformat() + "Z"
        if not self.report_hash:
            self.report_hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """Calculate hash of report metadata"""
        content = f"{self.report_id}{self.report_type.value}{self.generated_at}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class FailureStatistics:
    """Statistical analysis of failures"""

    total_failures: int
    critical_failures: int
    high_priority_failures: int
    medium_priority_failures: int
    low_priority_failures: int

    open_failures: int
    in_progress_failures: int
    resolved_failures: int

    detector_failures: int
    correspondence_failures: int
    statistical_failures: int
    reproducibility_failures: int

    average_resolution_time_days: Optional[float] = None
    resolution_rate_percentage: Optional[float] = None

    def calculate_totals(self):
        """Calculate derived statistics"""
        self.total_by_severity = {
            "critical": self.critical_failures,
            "high": self.high_priority_failures,
            "medium": self.medium_priority_failures,
            "low": self.low_priority_failures,
        }

        self.total_by_status = {
            "open": self.open_failures,
            "in_progress": self.in_progress_failures,
            "resolved": self.resolved_failures,
        }

        self.total_by_category = {
            "detector": self.detector_failures,
            "correspondence": self.correspondence_failures,
            "statistical": self.statistical_failures,
            "reproducibility": self.reproducibility_failures,
        }


@dataclass
class OntologicalPremiseAnalysis:
    """Analysis of ontological premise violations"""

    premise_name: str
    premise_description: str
    violations_count: int
    critical_violations: int
    example_violations: List[str]
    methodology_implications: List[str]
    fix_recommendations: List[str]

    def severity_score(self) -> float:
        """Calculate severity score for premise violations"""
        base_score = self.violations_count * 0.1
        critical_penalty = self.critical_violations * 0.5
        return min(1.0, base_score + critical_penalty)


@dataclass
class MethodologyHealthScore:
    """Health score for methodology"""

    overall_score: float  # 0.0 to 1.0
    falsifiability_score: float
    correspondence_score: float
    transparency_score: float
    reproducibility_score: float
    tool_validation_score: float

    critical_issues: List[str]
    improvement_recommendations: List[str]

    def get_health_status(self) -> str:
        """Get health status based on overall score"""
        if self.overall_score >= 0.8:
            return "HEALTHY"
        elif self.overall_score >= 0.6:
            return "MODERATE"
        elif self.overall_score >= 0.4:
            return "CONCERNING"
        else:
            return "CRITICAL"


# ============================================================================
# REPORT GENERATOR CLASS
# ============================================================================


class FailureReportGenerator:
    """Generate comprehensive failure analysis reports"""

    def __init__(self, repository_path: str, output_dir: str = "failure_reports"):
        self.repository_path = Path(repository_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Load existing failure data
        self.failures = self._load_failure_data()
        self.failure_statistics = self._calculate_statistics()

    def _load_failure_data(self) -> List[Dict[str, Any]]:
        """Load failure data from various sources"""
        failures = []

        # Load from FAILURES.md
        failures_md_path = self.repository_path / "FAILURES.md"
        if failures_md_path.exists():
            failures.extend(self._parse_failures_md(failures_md_path))

        # Load from falsification results
        falsification_path = (
            self.repository_path
            / "evidence"
            / "deepseek-analysis"
            / "FALSIFICATION_RESULTS.md"
        )
        if falsification_path.exists():
            failures.extend(self._parse_falsification_results(falsification_path))

        # Load from failure logs if they exist
        failure_logs_dir = self.repository_path / "failure_logs"
        if failure_logs_dir.exists():
            failures.extend(self._load_failure_logs(failure_logs_dir))

        return failures

    def _parse_failures_md(self, filepath: Path) -> List[Dict[str, Any]]:
        """Parse FAILURES.md file"""
        failures = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse critical failures
            if "## 🚨 CRITICAL FAILURES" in content:
                critical_section = content.split("## 🚨 CRITICAL FAILURES")[1].split(
                    "## ⚠️"
                )[0]
                failures.extend(
                    self._parse_failure_section(critical_section, "critical")
                )

            # Parse high priority failures
            if "## ⚠️ HIGH PRIORITY FAILURES" in content:
                high_section = content.split("## ⚠️ HIGH PRIORITY FAILURES")[1].split(
                    "## 🔵"
                )[0]
                failures.extend(self._parse_failure_section(high_section, "high"))

            # Parse medium priority failures
            if "## 🔵 MEDIUM PRIORITY FAILURES" in content:
                medium_section = content.split("## 🔵 MEDIUM PRIORITY FAILURES")[
                    1
                ].split("## 💚")[0]
                failures.extend(self._parse_failure_section(medium_section, "medium"))

            # Parse low priority failures
            if "## 💚 LOW PRIORITY FAILURES" in content:
                low_section = content.split("## 💚 LOW PRIORITY FAILURES")[1].split(
                    "## 📊"
                )[0]
                failures.extend(self._parse_failure_section(low_section, "low"))

        except Exception as e:
            print(f"Error parsing FAILURES.md: {e}")

        return failures

    def _parse_failure_section(
        self, section: str, severity: str
    ) -> List[Dict[str, Any]]:
        """Parse individual failure sections"""
        failures = []
        lines = section.strip().split("\n")

        current_failure = None
        current_description = []

        for i, line in enumerate(lines):
            line = line.strip()

            # Detect failure start
            if line.startswith("### FAILURE") and ":" in line:
                if current_failure is not None:
                    # Save previous failure
                    current_failure["description"] = " ".join(current_description)
                    failures.append(current_failure)

                # Start new failure
                title_parts = line.split(":", 1)
                if len(title_parts) > 1:
                    title = title_parts[1].strip()
                else:
                    title = line

                current_failure = {
                    "id": f"FAILURE-{len(failures) + 1:03d}",
                    "title": title,
                    "severity": severity,
                    "category": self._determine_category(title),
                    "description": "",
                    "evidence": [],
                    "fix_required": [],
                    "status": "open",
                    "discovered_date": datetime.datetime.utcnow().isoformat() + "Z",
                }
                current_description = []

            # Collect description
            elif current_failure is not None and line and not line.startswith("**"):
                current_description.append(line)

            # Detect evidence
            elif line.startswith("**Evidence:**"):
                if i + 1 < len(lines):
                    evidence = lines[i + 1].strip()
                    if evidence:
                        current_failure["evidence"].append(evidence)

            # Detect fix requirements
            elif line.startswith("**Fix Required:**"):
                j = i + 1
                while (
                    j < len(lines)
                    and lines[j].strip()
                    and not lines[j].strip().startswith("**")
                ):
                    fix_line = lines[j].strip()
                    if fix_line:
                        current_failure["fix_required"].append(fix_line)
                    j += 1

        # Add the last failure
        if current_failure is not None:
            current_failure["description"] = " ".join(current_description)
            failures.append(current_failure)

        return failures

    def _determine_category(self, title: str) -> str:
        """Determine failure category from title"""
        title_lower = title.lower()

        if any(word in title_lower for word in ["detector", "canal", "pattern"]):
            return "detector_failure"
        elif any(
            word in title_lower for word in ["statistical", "p-value", "significance"]
        ):
            return "statistical_failure"
        elif any(
            word in title_lower
            for word in ["correspondence", "implementation", "working"]
        ):
            return "correspondence_failure"
        elif any(
            word in title_lower for word in ["reproducibility", "reproduce", "setup"]
        ):
            return "reproducibility_failure"
        else:
            return "implementation_failure"

    def _parse_falsification_results(self, filepath: Path) -> List[Dict[str, Any]]:
        """Parse falsification results"""
        failures = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            if "❌ CLAIM REJECTED" in content:
                failure = {
                    "id": "FALSIFICATION-001",
                    "title": "DeepSeek 45.30% density claim falsified",
                    "severity": "critical",
                    "category": "detector_failure",
                    "description": "Three independent falsification tests rejected the 45.30% density claim",
                    "evidence": [
                        "70% false positive rate in detector",
                        "Chaotic variance (100% range)",
                        "96% repetition rate indicating mimicry",
                    ],
                    "fix_required": [
                        "Remove 45.30% claim from all files",
                        "Document detector failure mode",
                        "Revise to conservative 5-10% estimate",
                    ],
                    "status": "resolved",
                    "discovered_date": datetime.datetime.utcnow().isoformat() + "Z",
                    "methodology_implications": [
                        "All density claims using this detector are invalid",
                        "Detector requires complete redesign",
                        "Methodology proved itself by identifying its own failure",
                    ],
                }
                failures.append(failure)

        except Exception as e:
            print(f"Error parsing falsification results: {e}")

        return failures

    def _load_failure_logs(self, logs_dir: Path) -> List[Dict[str, Any]]:
        """Load failure logs from directory"""
        failures = []

        try:
            for log_file in logs_dir.glob("*.json"):
                with open(log_file, "r", encoding="utf-8") as f:
                    log_data = json.load(f)

                if "failures" in log_data:
                    failures.extend(log_data["failures"])

        except Exception as e:
            print(f"Error loading failure logs: {e}")

        return failures

    def _calculate_statistics(self) -> FailureStatistics:
        """Calculate failure statistics"""
        stats = FailureStatistics(
            total_failures=len(self.failures),
            critical_failures=sum(
                1 for f in self.failures if f.get("severity") == "critical"
            ),
            high_priority_failures=sum(
                1 for f in self.failures if f.get("severity") == "high"
            ),
            medium_priority_failures=sum(
                1 for f in self.failures if f.get("severity") == "medium"
            ),
            low_priority_failures=sum(
                1 for f in self.failures if f.get("severity") == "low"
            ),
            open_failures=sum(1 for f in self.failures if f.get("status") == "open"),
            in_progress_failures=sum(
                1 for f in self.failures if f.get("status") == "in_progress"
            ),
            resolved_failures=sum(
                1 for f in self.failures if f.get("status") == "resolved"
            ),
            detector_failures=sum(
                1 for f in self.failures if f.get("category") == "detector_failure"
            ),
            correspondence_failures=sum(
                1
                for f in self.failures
                if f.get("category") == "correspondence_failure"
            ),
            statistical_failures=sum(
                1 for f in self.failures if f.get("category") == "statistical_failure"
            ),
            reproducibility_failures=sum(
                1
                for f in self.failures
                if f.get("category") == "reproducibility_failure"
            ),
        )

        stats.calculate_totals()
        return stats

    # ============================================================================
    # REPORT GENERATION METHODS
    # ============================================================================

    def generate_methodology_health_report(
        self, format: ReportFormat = ReportFormat.MARKDOWN
    ) -> str:
        """Generate methodology health report"""
        metadata = ReportMetadata(
            report_id=f"METHODOLOGY-HEALTH-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            report_type=ReportType.METHODOLOGY_HEALTH,
            generated_at=datetime.datetime.utcnow().isoformat() + "Z",
        )

        # Calculate health scores
        health_score = self._calculate_methodology_health_score()

        # Generate report based on format
        if format == ReportFormat.MARKDOWN:
            return self._generate_markdown_health_report(metadata, health_score)
        elif format == ReportFormat.JSON:
            return self._generate_json_health_report(metadata, health_score)
        else:
            return self._generate_markdown_health_report(metadata, health_score)

    def _calculate_methodology_health_score(self) -> MethodologyHealthScore:
        """Calculate methodology health score"""

        # Calculate individual scores
        falsifiability_score = self._calculate_falsifiability_score()
        correspondence_score = self._calculate_correspondence_score()
        transparency_score = self._calculate_transparency_score()
        reproducibility_score = self._calculate_reproducibility_score()
        tool_validation_score = self._calculate_tool_validation_score()

        # Calculate overall score (weighted average)
        weights = {
            "falsifiability": 0.3,
            "correspondence": 0.25,
            "transparency": 0.2,
            "reproducibility": 0.15,
            "tool_validation": 0.1,
        }

        overall_score = (
            falsifiability_score * weights["falsifiability"]
            + correspondence_score * weights["correspondence"]
            + transparency_score * weights["transparency"]
            + reproducibility_score * weights["reproducibility"]
            + tool_validation_score * weights["tool_validation"]
        )

        # Identify critical issues
        critical_issues = []
        if falsifiability_score < 0.5:
            critical_issues.append("Falsifiability principles not fully implemented")
        if correspondence_score < 0.4:
            critical_issues.append("Correspondence validation lacking evidence")
        if self.failure_statistics.critical_failures > 0:
            critical_issues.append(
                f"{self.failure_statistics.critical_failures} critical failures unresolved"
            )

        # Generate recommendations
        recommendations = []
        if overall_score < 0.8:
            recommendations.append("Address critical failures before making new claims")
        if tool_validation_score < 0.6:
            recommendations.append("Improve tool validation with more rigorous testing")
