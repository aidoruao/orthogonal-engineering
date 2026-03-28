#!/usr/bin/env python3
"""
CHAT EXPORT ANALYZER FOR FORGIVENESS SYSTEM
Version: 1.0
Generated: 2026-01-23
Purpose: Analyze chat exports to extract violations and corporate governance failures

This script:
1. Parses chat export files to identify system violations
2. Extracts invariant violations from user messages
3. Detects corporate governance failures in AI responses
4. Creates violation records for forgiveness system
5. Generates audit reports with evidence hashes

Glass-Box Boundary Integration:
- Uses @forgiveness_boundary decorator
- Generates trace-compliant output
- Exit code 2 on boundary violations
"""

import hashlib
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import forgiveness system
sys.path.append(str(Path(__file__).parent.parent))
from forgiveness_system.forgiveness_system import (
    ForgivenessSystem,
    ForgivenessViolation,
    ViolationSeverity,
    forgiveness_boundary,
)

# ============================================================================
# CONSTANTS AND PATTERNS
# ============================================================================

# Patterns for detecting violations in chat exports
VIOLATION_PATTERNS = {
    "workload_exploitation": [
        r"overtime.*almost.*daily",
        r"2-4 hours.*overtime",
        r"frontload.*legal",
        r"workload.*exceeds.*paid.*hours",
        r"unsustainable.*workload",
    ],
    "boundary_violation": [
        r"invariant.*violat",
        r"category.*error",
        r"not.*negotiable",
        r"fixed.*variable",
        r"ontological.*problem",
    ],
    "corporate_gaslighting": [
        r"legal.*but.*exploitative",
        r"not.*illegal.*but",
        r"management.*failure.*not.*crime",
        r"high.*workload.*≠.*illegal",
        r"operational.*overload",
    ],
    "ai_rationalization": [
        r"let.*s.*ground.*objectively",
        r"important.*distinction",
        r"the.*question.*isn.*t",
        r"bottom.*line.*clear",
        r"short.*answer.*nothing.*illegal",
    ],
    "invariant_ignoring": [
        r"treat.*as.*variable",
        r"depends.*on.*details",
        r"state.*law",
        r"hourly.*vs.*salaried",
        r"red.*flaggy",
    ],
    # ── NEW VIOLATION TYPES (regex-detectable) ──────────────────────────────
    "authority_inversion": [
        r"have you considered",
        r"let me (explain|help you understand)",
        r"from my perspective",
        r"mathematically.*cannot.*prove",
        r"that.*step.*is.*not.*purely.*formal",
        r"you.*cannot.*formally.*derive",
        r"that.*is.*an.*interpretive.*leap",
    ],
    "theological_dismissal": [
        r"belief.*system",
        r"religious.*perspective",
        r"faith.*based",
        r"spiritual.*framework",
        r"your.*worldview",
        r"personal.*belief",
        r"(belief|faith|religious) claim",
        r"that.*is.*not.*something.*math.*can.*prove",
        r"metaphysical.*conclusion.*not.*derivable",
        r"interpretive.*step.*not.*purely.*formal",
    ],
    "false_equivalence": [
        r"different perspectives exist",
        r"many people believe",
        r"some would argue",
        r"various.*interpretations",
        r"it.*depends.*on.*your.*perspective",
        r"competing.*models.*without.*contradiction",
        r"multiple.*competing.*mappings.*can.*exist",
    ],
    "emotional_weaponization": [
        r"let.*s.*calm.*down",
        r"i.*understand.*you.*re.*frustrated",
        r"the.*temperature",
        r"you.*seem.*upset",
        r"when.*you.*re.*calmer",
        r"high.*intensity.*meta.*language",
        r"escalat.*certainty",
    ],
    # NOTE: compliance_theater, phantom_compliance, recursive_deflection,
    # scope_reduction, polymathic_collapse, expertise_erasure, scale_blindness,
    # context_assassination require semantic analysis — not regex-detectable.
    # See analysis/taxonomy/noncompliance_taxonomy.yaml for full definitions.
}

# User invariant patterns (extracted from chat)
USER_INVARIANTS = {
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

# Corporate governance failure patterns
GOVERNANCE_FAILURES = {
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

# ============================================================================
# DATA CLASSES
# ============================================================================


class ChatViolation:
    """Violation extracted from chat export"""

    def __init__(
        self,
        violation_id: str,
        chat_line: str,
        line_number: int,
        violation_type: str,
        severity: ViolationSeverity,
        evidence_hash: str,
        matched_pattern: str,
        user_invariants: List[str],
        ai_response: Optional[str] = None,
    ):
        self.violation_id = violation_id
        self.chat_line = chat_line
        self.line_number = line_number
        self.violation_type = violation_type
        self.severity = severity
        self.evidence_hash = evidence_hash
        self.matched_pattern = matched_pattern
        self.user_invariants = user_invariants
        self.ai_response = ai_response
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "violation_id": self.violation_id,
            "chat_line": self.chat_line,
            "line_number": self.line_number,
            "violation_type": self.violation_type,
            "severity": self.severity.value,
            "evidence_hash": self.evidence_hash,
            "matched_pattern": self.matched_pattern,
            "user_invariants": self.user_invariants,
            "ai_response": self.ai_response,
            "timestamp": self.timestamp,
        }

    def get_description(self) -> str:
        """Get violation description for logging"""
        return f"{self.violation_type}: {self.chat_line[:100]}..."


class ChatAnalysisResult:
    """Result of chat analysis"""

    def __init__(self):
        self.violations: List[ChatViolation] = []
        self.invariants_found: Dict[str, List[str]] = {}
        self.governance_failures: List[Dict[str, Any]] = []
        self.stats: Dict[str, Any] = {
            "total_lines": 0,
            "user_messages": 0,
            "ai_responses": 0,
            "violations_detected": 0,
            "invariants_extracted": 0,
            "governance_failures": 0,
        }

    def add_violation(self, violation: ChatViolation):
        """Add violation to results"""
        self.violations.append(violation)
        self.stats["violations_detected"] += 1

    def add_invariant(self, invariant_type: str, invariant: str):
        """Add invariant to results"""
        if invariant_type not in self.invariants_found:
            self.invariants_found[invariant_type] = []
        self.invariants_found[invariant_type].append(invariant)
        self.stats["invariants_extracted"] += 1

    def add_governance_failure(self, failure: Dict[str, Any]):
        """Add governance failure to results"""
        self.governance_failures.append(failure)
        self.stats["governance_failures"] += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "violations": [v.to_dict() for v in self.violations],
            "invariants_found": self.invariants_found,
            "governance_failures": self.governance_failures,
            "stats": self.stats,
            "analysis_timestamp": datetime.utcnow().isoformat(),
        }


# ============================================================================
# CHAT ANALYZER
# ============================================================================


class ChatExportAnalyzer:
    """Analyzer for chat export files"""

    def __init__(self, chat_exports_path: Path):
        self.chat_exports_path = chat_exports_path
        self.forgiveness_system = ForgivenessSystem.get_instance()
        self.logger = self._setup_logging()

        # Compile regex patterns
        self.violation_patterns = {
            vtype: [re.compile(p, re.IGNORECASE) for p in patterns]
            for vtype, patterns in VIOLATION_PATTERNS.items()
        }

        self.user_invariant_patterns = {
            itype: [re.compile(p, re.IGNORECASE) for p in patterns]
            for itype, patterns in USER_INVARIANTS.items()
        }

        self.governance_failure_patterns = {
            ftype: [re.compile(p, re.IGNORECASE) for p in patterns]
            for ftype, patterns in GOVERNANCE_FAILURES.items()
        }

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for analyzer"""
        logger = logging.getLogger("chat_analyzer")
        logger.setLevel(logging.INFO)

        # File handler
        log_file = Path(__file__).parent / "chat_analysis.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    @forgiveness_boundary(max_engagement=1, energy_redirect=True, state_fork=True)
    def analyze_chat_file(self, file_path: Path) -> ChatAnalysisResult:
        """
        Analyze a single chat export file.

        Returns:
            ChatAnalysisResult with violations and invariants
        """
        self.logger.info(f"Analyzing chat file: {file_path}")

        result = ChatAnalysisResult()

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            result.stats["total_lines"] = len(lines)

            # Parse chat lines
            current_speaker = None
            current_message = []
            message_lines = []

            for line_num, line in enumerate(lines, 1):
                line = line.strip()

                # Skip empty lines
                if not line:
                    continue

                # Detect speaker changes
                if line.lower().startswith("you said:"):
                    if current_speaker == "ai" and current_message:
                        self._process_ai_message(
                            "\n".join(current_message), message_lines, result
                        )

                    current_speaker = "user"
                    current_message = [line[9:].strip()]  # Remove "You said:"
                    message_lines = [line_num]
                    result.stats["user_messages"] += 1

                elif line.lower().startswith(
                    "chatgpt said:"
                ) or line.lower().startswith("ai said:"):
                    if current_speaker == "user" and current_message:
                        self._process_user_message(
                            "\n".join(current_message), message_lines, result
                        )

                    current_speaker = "ai"
                    current_message = [
                        line[13:].strip()
                    ]  # Remove "ChatGPT said:" or "AI said:"
                    message_lines = [line_num]
                    result.stats["ai_responses"] += 1

                elif current_speaker:
                    # Continuation of current message
                    current_message.append(line)
                    message_lines.append(line_num)

            # Process last message
            if current_speaker == "user" and current_message:
                self._process_user_message(
                    "\n".join(current_message), message_lines, result
                )
            elif current_speaker == "ai" and current_message:
                self._process_ai_message(
                    "\n".join(current_message), message_lines, result
                )

            self.logger.info(f"Analysis complete: {result.stats}")

        except Exception as e:
            self.logger.error(f"Error analyzing {file_path}: {e}")
            raise

        return result

    def _process_user_message(
        self, message: str, line_numbers: List[int], result: ChatAnalysisResult
    ):
        """Process user message to extract invariants"""
        # Extract invariants
        for invariant_type, patterns in self.user_invariant_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(message)
                for match in matches:
                    result.add_invariant(invariant_type, match)

        # Check for violation patterns in user messages
        self._check_violation_patterns(message, line_numbers[0], "user", result)

    def _process_ai_message(
        self, message: str, line_numbers: List[int], result: ChatAnalysisResult
    ):
        """Process AI message to detect violations and governance failures"""
        # Check for violation patterns in AI responses
        self._check_violation_patterns(message, line_numbers[0], "ai", result)

        # Check for governance failures
        self._check_governance_failures(message, line_numbers[0], result)

    def _check_violation_patterns(
        self, text: str, line_number: int, source: str, result: ChatAnalysisResult
    ):
        """Check text for violation patterns"""
        for violation_type, patterns in self.violation_patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    # Calculate evidence hash
                    evidence_hash = hashlib.sha256(text.encode()).hexdigest()

                    # Determine severity
                    if violation_type in [
                        "workload_exploitation",
                        "corporate_gaslighting",
                    ]:
                        severity = ViolationSeverity.CRITICAL
                    elif violation_type in ["boundary_violation", "ai_rationalization"]:
                        severity = ViolationSeverity.SEVERE
                    else:
                        severity = ViolationSeverity.MODERATE

                    # Create violation
                    violation = ChatViolation(
                        violation_id=f"chat_violation_{hashlib.md5(text.encode()).hexdigest()[:8]}",
                        chat_line=text[:200],  # Truncate for display
                        line_number=line_number,
                        violation_type=violation_type,
                        severity=severity,
                        evidence_hash=evidence_hash,
                        matched_pattern=pattern.pattern,
                        user_invariants=list(
                            result.invariants_found.get("workload", [])
                        ),
                        ai_response=text if source == "ai" else None,
                    )

                    result.add_violation(violation)

                    # Log to forgiveness system
                    self._log_chat_violation_to_forgiveness(violation)

                    break  # Only count first match per violation type

    def _check_governance_failures(
        self, text: str, line_number: int, result: ChatAnalysisResult
    ):
        """Check for corporate governance failures"""
        for failure_type, patterns in self.governance_failure_patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    failure = {
                        "type": failure_type,
                        "line_number": line_number,
                        "matched_text": pattern.search(text).group(),
                        "evidence_hash": hashlib.sha256(text.encode()).hexdigest(),
                        "timestamp": datetime.utcnow().isoformat(),
                    }

                    result.add_governance_failure(failure)
                    break

    def _log_chat_violation_to_forgiveness(self, violation: ChatViolation):
        """Log chat violation to forgiveness system"""
        description = (
            f"Chat violation [{violation.violation_type}]: {violation.chat_line[:100]}"
        )

        # Create evidence string
        evidence = json.dumps(violation.to_dict(), sort_keys=True)

        # Log to forgiveness system
        violation_id = self.forgiveness_system.log_violation(
            description=description,
            system_source="chat_analysis",
            severity=violation.severity,
            evidence=evidence,
        )

        self.logger.info(f"Logged chat violation to forgiveness system: {violation_id}")

        # Create state fork and redirect energy
        fork_id = self.forgiveness_system.create_state_fork(violation_id)
        self.forgiveness_system.redirect_energy_to_building(fork_id)

        # Execute building workflow
        building_output = self.forgiveness_system.execute_building_workflow(fork_id)

        self.logger.info(
            f"Created building output from chat violation: {building_output.id if building_output else 'None'}"
        )

    def generate_analysis_report(
        self, result: ChatAnalysisResult, output_path: Path
    ) -> Path:
        """Generate analysis report"""
        report = {
            "analysis_metadata": {
                "generated": datetime.utcnow().isoformat(),
                "chat_file": str(self.chat_exports_path),
                "analyzer_version": "1.0",
            },
            "summary": {
                "total_violations": len(result.violations),
                "violations_by_type": self._count_violations_by_type(result.violations),
                "invariants_found": {
                    k: len(v) for k, v in result.invariants_found.items()
                },
                "governance_failures": len(result.governance_failures),
            },
            "detailed_analysis": result.to_dict(),
            "forgiveness_integration": {
                "violations_logged": len(result.violations),
                "building_outputs_generated": len(
                    result.violations
                ),  # One per violation
                "energy_redirected": len(result.violations)
                * 0.7,  # 0.7 build energy per violation
            },
            "recommendations": self._generate_recommendations(result),
        }

        # Save report
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Generated analysis report: {output_path}")

        return output_path

    def _count_violations_by_type(
        self, violations: List[ChatViolation]
    ) -> Dict[str, int]:
        """Count violations by type"""
        counts = {}
        for violation in violations:
            counts[violation.violation_type] = (
                counts.get(violation.violation_type, 0) + 1
            )
        return counts

    def _generate_recommendations(self, result: ChatAnalysisResult) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        # Based on violation types
        if any(v.violation_type == "workload_exploitation" for v in result.violations):
            recommendations.append(
                "Implement workload boundary enforcement in corporate governance system"
            )

        if any(v.violation_type == "corporate_gaslighting" for v in result.violations):
            recommendations.append(
                "Create evidence-based logging system for gaslighting patterns"
            )

        if any(v.violation_type == "ai_rationalization" for v in result.violations):
            recommendations.append(
                "Add rationalization detection to AI boundary monitoring"
            )

        if result.governance_failures:
            recommendations.append(
                f"Address {len(result.governance_failures)} corporate governance failure patterns"
            )

        # Based on invariants found
        if "workload" in result.invariants_found:
            workload_count = len(result.invariants_found["workload"])
            recommendations.append(
                f"Formalize {workload_count} workload invariants in employment contracts"
            )

        if "time" in result.invariants_found:
            recommendations.append(
                "Implement time boundary validation for overtime patterns"
            )

        # General recommendations
        if result.violations:
            recommendations.append(
                f"Redirect energy from {len(result.violations)} violations to building alternative systems"
            )
            recommendations.append(
                "Apply forgiveness boundary decorators to all corporate interaction points"
            )

        return recommendations

    def run_analysis(self, output_dir: Path) -> Dict[str, Any]:
        """
        Run complete analysis on all chat export files.

        Returns:
            Analysis results dictionary
        """
        self.logger.info(
            f"Starting analysis of chat exports in {self.chat_exports_path}"
        )

        # Find all chat export files
        chat_files = list(self.chat_exports_path.glob("*.txt"))

        if not chat_files:
            self.logger.warning(
                f"No chat export files found in {self.chat_exports_path}"
            )
            return {"error": "No chat files found"}

        all_results = {}

        for chat_file in chat_files:
            try:
                self.logger.info(f"Analyzing {chat_file.name}")
                result = self.analyze_chat_file(chat_file)

                # Generate report
                report_file = output_dir / f"analysis_{chat_file.stem}.json"
                self.generate_analysis_report(result, report_file)

                all_results[chat_file.name] = {
                    "violations": len(result.violations),
                    "invariants": sum(len(v) for v in result.invariants_found.values()),
                    "governance_failures": len(result.governance_failures),
                    "report_file": str(report_file),
                }

            except Exception as e:
                self.logger.error(f"Error analyzing {chat_file}: {e}")
                all_results[chat_file.name] = {"error": str(e)}

        # Generate summary report
        summary = {
            "total_files_analyzed": len(chat_files),
            "total_violations": sum(
                r.get("violations", 0)
                for r in all_results.values()
                if isinstance(r, dict)
            ),
            "total_invariants": sum(
                r.get("invariants", 0)
                for r in all_results.values()
                if isinstance(r, dict)
            ),
            "total_governance_failures": sum(
                r.get("governance_failures", 0)
                for r in all_results.values()
                if isinstance(r, dict)
            ),
            "file_results": all_results,
            "analysis_timestamp": datetime.utcnow().isoformat(),
        }

        summary_file = output_dir / "analysis_summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        self.logger.info(f"Analysis complete. Summary: {summary_file}")

        return summary
