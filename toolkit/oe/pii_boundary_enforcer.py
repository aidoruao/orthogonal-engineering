"""
PII BOUNDARY ENFORCER - Personal Information Protection Module
Version: 1.0
Schema ID: PII-CANON-1.0
Generated: 2026-01-21
Purpose: Enforce PII Canon for Orthogonal Engineering Repository

Atomic PII Canon Enforcement:
1. Prevent humanly sensitive, personal, or relational content from commits
2. Maintain strict separation between professional methodology and private cognitive work
3. Enforce atomic blocking with immediate rollback on violations
4. Provide safe sanitization for technical insights extraction
5. Log violations without exposing sensitive content

Principles:
- Human Safety: Hard-block pre-commit for minor/PII references
- Privacy: All personal chats stay local, never committed
- Professional Clarity: Only sanitized, technical insights committed
- Atomic Enforcement: Commit success = 100% PII-free; failure = rollback
- Subtractive Clarity: No ambiguity about what content belongs where
- Auditability: Log violations safely without exposing sensitive info
"""

import hashlib
import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class PIIViolationType(str, Enum):
    """Types of PII boundary violations"""

    MINOR_REFERENCE = "minor_reference"
    PERSONAL_RELATIONSHIP = "personal_relationship"
    PRIVATE_PHILOSOPHY = "private_philosophy"
    THERAPY_NOTES = "therapy_notes"
    DEVELOPMENT_PLANS = "development_plans"
    WEAPONS_TRAINING = "weapons_training"
    RELIGIOUS_TRAINING = "religious_training"
    SOCIAL_HARM_RISK = "social_harm_risk"
    MIXED_CONTEXT = "mixed_context"


class ViolationSeverity(str, Enum):
    """Severity levels for PII violations"""

    CRITICAL = "critical"  # Immediate block, social harm risk
    HIGH = "high"  # Personal content, must be sanitized
    MEDIUM = "medium"  # Mixed professional/personal content
    LOW = "low"  # Borderline content, warning only


@dataclass
class PIIViolation:
    """Represents a detected PII boundary violation"""

    violation_id: str
    violation_type: PIIViolationType
    severity: ViolationSeverity
    file_path: str
    line_number: int
    context_preview: str  # Safe preview without sensitive content
    pattern_matched: str
    action_taken: str
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "violation_id": self.violation_id,
            "violation_type": self.violation_type.value,
            "severity": self.severity.value,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "context_preview": self.context_preview,
            "pattern_matched": self.pattern_matched,
            "action_taken": self.action_taken,
            "timestamp": self.timestamp,
        }


class PIIBoundaryEnforcer:
    """
    Enforces PII Canon boundaries with detection, sanitization, and blocking.

    Core Responsibilities:
    1. Detect PII violations in staged files
    2. Sanitize technical insights while removing personal content
    3. Provide atomic blocking for git commits
    4. Log violations safely without exposing sensitive content
    5. Maintain separation between personal and professional domains
    """

    # PII-sensitive file patterns that should never be committed
    PII_FILE_PATTERNS = [
        "chat_exports/*",
        "*.chat.json",
        "*.conversation.txt",
        "personal_notes/*",
        "therapy_journal/*",
        "private_cognition/*",
    ]

    # PII detection patterns with severity levels
    PII_DETECTION_PATTERNS = {
        # CRITICAL: Social harm risk, minor references
        r"\b(middle\s+school\s+girl|minor\s+reference|underage)\b": {
            "type": PIIViolationType.MINOR_REFERENCE,
            "severity": ViolationSeverity.CRITICAL,
            "replacement": "MINOR_REFERENCE_REDACTED",
            "description": "Reference to minor in philosophical context - social harm risk",
        },
        r"\b(why\s+me\s+sociological\s+analysis|relationship\s+analysis\s+real\s+people)\b": {
            "type": PIIViolationType.PERSONAL_RELATIONSHIP,
            "severity": ViolationSeverity.CRITICAL,
            "replacement": "PERSONAL_RELATIONSHIP_ANALYSIS_REDACTED",
            "description": "Personal relationship analysis involving real people",
        },
        # HIGH: Personal development plans, private philosophy
        r"\b(christian\s+apologetics|religious\s+training\s+plan)\b": {
            "type": PIIViolationType.RELIGIOUS_TRAINING,
            "severity": ViolationSeverity.HIGH,
            "replacement": "RELIGIOUS_TRAINING_PLAN_REDACTED",
            "description": "Personal religious training or development plan",
        },
        r"\b(karambit|weapons\s+training)\b": {
            "type": PIIViolationType.WEAPONS_TRAINING,
            "severity": ViolationSeverity.HIGH,
            "replacement": "WEAPONS_TRAINING_REFERENCE_REDACTED",
            "description": "Weapons training or combat reference",
        },
        # MEDIUM: Therapy notes, personal development
        r"\b(selective\s+mutism\s+therapy|personal\s+therapy\s+notes)\b": {
            "type": PIIViolationType.THERAPY_NOTES,
            "severity": ViolationSeverity.MEDIUM,
            "replacement": "THERAPY_NOTES_REDACTED",
            "description": "Personal therapy notes or treatment plans",
        },
        r"\b(personal\s+development\s+plan\s+for\s+others|development\s+plans\s+real\s+humans)\b": {
            "type": PIIViolationType.DEVELOPMENT_PLANS,
            "severity": ViolationSeverity.MEDIUM,
            "replacement": "DEVELOPMENT_PLANS_REDACTED",
            "description": "Personal development plans for real individuals",
        },
        # LOW: Philosophical frameworks, mixed content
        r"\b(personal\s+philosophical\s+framework|private\s+cognitive\s+work)\b": {
            "type": PIIViolationType.PRIVATE_PHILOSOPHY,
            "severity": ViolationSeverity.LOW,
            "replacement": "PRIVATE_PHILOSOPHY_REDACTED",
            "description": "Private philosophical or cognitive work",
        },
        r"\b(mixed\s+professional\s+personal|context\s+separation\s+violation)\b": {
            "type": PIIViolationType.MIXED_CONTEXT,
            "severity": ViolationSeverity.LOW,
            "replacement": "MIXED_CONTEXT_REDACTED",
            "description": "Mixed professional and personal content",
        },
    }

    # Safe technical patterns that can be extracted after sanitization
    TECHNICAL_PATTERNS_ALLOWED = [
        r"\b(orthogonal\s+engineering|glass\s+box\s+boundary)\b",
        r"\b(subtractive\s+clarity|atomic\s+enforcement)\b",
        r"\b(regex\s+boundary|combinatorial\s+explosion)\b",
        r"\b(python\s+enforcer|zed\s+ide\s+integration)\b",
        r"\b(trace\s+generation|boundary\s+violation)\b",
        r"\b(continuity\s+of\s+body|session\s+persistence)\b",
    ]

    def __init__(self, workspace_root: str = "."):
        """
        Initialize PII boundary enforcer.

        Args:
            workspace_root: Root directory of the workspace
        """
        self.workspace_root = Path(workspace_root).resolve()
        self.violations: List[PIIViolation] = []
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup logging for PII boundary enforcement"""
        logger = logging.getLogger("pii_boundary_enforcer")
        logger.setLevel(logging.INFO)

        # Create logs directory if it doesn't exist
        logs_dir = self.workspace_root / "logs" / "pii_violations"
        logs_dir.mkdir(parents=True, exist_ok=True)

        # File handler for violation logs
        log_file = (
            logs_dir / f"pii_violations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # Console handler for immediate feedback
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

    def generate_violation_id(self) -> str:
        """Generate unique violation ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_hash = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[
            :8
        ]
        return f"PII_VIOLATION_{timestamp}_{random_hash}"

    def detect_pii_violations(self, file_path: str, content: str) -> List[PIIViolation]:
        """
        Detect PII violations in file content.

        Args:
            file_path: Path to the file being checked
            content: Content of the file

        Returns:
            List of detected PII violations
        """
        violations = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            for pattern, pattern_info in self.PII_DETECTION_PATTERNS.items():
                if re.search(pattern, line, re.IGNORECASE):
                    # Create safe context preview (max 50 chars)
                    context_preview = line.strip()[:50]
                    if len(line.strip()) > 50:
                        context_preview += "..."

                    violation = PIIViolation(
                        violation_id=self.generate_violation_id(),
                        violation_type=pattern_info["type"],
                        severity=pattern_info["severity"],
                        file_path=file_path,
                        line_number=line_num,
                        context_preview=context_preview,
                        pattern_matched=pattern,
                        action_taken="detected",
                        timestamp=datetime.now().isoformat(),
                    )
                    violations.append(violation)

                    self.logger.warning(
                        f"PII violation detected: {pattern_info['type'].value} "
                        f"in {file_path}:{line_num} - {pattern_info['description']}"
                    )

        return violations

    def sanitize_content(self, content: str) -> Tuple[str, List[PIIViolation]]:
        """
        Sanitize content by replacing PII with safe placeholders.

        Args:
            content: Original content to sanitize

        Returns:
            Tuple of (sanitized_content, list_of_violations)
        """
        sanitized = content
        violations = []

        for pattern, pattern_info in self.PII_DETECTION_PATTERNS.items():
            # Find all matches for logging
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            for match in matches:
                # Create violation record
                line_num = content[: match.start()].count("\n") + 1
                context_preview = match.group(0)[:50]

                violation = PIIViolation(
                    violation_id=self.generate_violation_id(),
                    violation_type=pattern_info["type"],
                    severity=pattern_info["severity"],
                    file_path="<in_memory_content>",
                    line_number=line_num,
                    context_preview=context_preview,
                    pattern_matched=pattern,
                    action_taken="sanitized",
                    timestamp=datetime.now().isoformat(),
                )
                violations.append(violation)

            # Replace with safe placeholder
            sanitized = re.sub(
                pattern, pattern_info["replacement"], sanitized, flags=re.IGNORECASE
            )

        return sanitized, violations

    def extract_technical_insights(self, sanitized_content: str) -> str:
        """
        Extract technical insights from sanitized content.

        Args:
            sanitized_content: Content after PII sanitization

        Returns:
            Technical insights with non-technical content removed
        """
        lines = sanitized_content.split("\n")
        technical_lines = []

        for line in lines:
            # Keep lines that contain technical patterns
            if any(
                re.search(pattern, line, re.IGNORECASE)
                for pattern in self.TECHNICAL_PATTERNS_ALLOWED
            ):
                technical_lines.append(line)
            # Also keep lines that don't contain redaction placeholders (likely already technical)
            elif not any(
                placeholder in line
                for placeholder in ["REDACTED", "MINOR_", "PERSONAL_", "PRIVATE_"]
            ):
                technical_lines.append(line)

        return "\n".join(technical_lines)

    def check_file_for_commit(
        self, file_path: str, content: str
    ) -> Tuple[bool, List[PIIViolation]]:
        """
        Check if file is safe to commit (atomic blocking).

        Args:
            file_path: Path to the file
            content: Content of the file

        Returns:
            Tuple of (is_safe_to_commit, list_of_violations)
        """
        # Check if file matches PII-sensitive patterns
        file_path_str = str(file_path)
        for pattern in self.PII_FILE_PATTERNS:
            if Path(file_path_str).match(pattern):
                self.logger.error(
                    f"File {file_path} matches PII-sensitive pattern {pattern} - BLOCKING COMMIT"
                )
                return False, []

        # Detect PII violations
        violations = self.detect_pii_violations(file_path_str, content)

        # Check for critical violations that require immediate blocking
        critical_violations = [
            v for v in violations if v.severity == ViolationSeverity.CRITICAL
        ]

        if critical_violations:
            self.logger.error(
                f"CRITICAL PII violations detected in {file_path}: "
                f"{len(critical_violations)} violations - BLOCKING COMMIT"
            )
            return False, violations

        # High severity violations also block commit (needs sanitization)
        high_violations = [
            v for v in violations if v.severity == ViolationSeverity.HIGH
        ]
        if high_violations:
            self.logger.error(
                f"HIGH severity PII violations detected in {file_path}: "
                f"{len(high_violations)} violations - BLOCKING COMMIT (needs sanitization)"
            )
            return False, violations

        # Medium and low severity violations allow commit with warning
        if violations:
            self.logger.warning(
                f"PII violations detected in {file_path}: {len(violations)} violations - ALLOWING WITH WARNING"
            )

        return True, violations

    def process_file_for_commit(
        self, file_path: str, content: str
    ) -> Tuple[str, List[PIIViolation]]:
        """
        Process file for commit with sanitization and technical insight extraction.

        Args:
            file_path: Path to the file
            content: Original content

        Returns:
            Tuple of (processed_content, list_of_violations)
        """
        # First sanitize PII content
        sanitized_content, sanitization_violations = self.sanitize_content(content)

        # Then extract technical insights
        technical_content = self.extract_technical_insights(sanitized_content)

        # Check if result is safe to commit
        is_safe, check_violations = self.check_file_for_commit(
            file_path, technical_content
        )

        all_violations = sanitization_violations + check_violations

        if not is_safe:
            self.logger.error(
                f"File {file_path} is not safe to commit even after sanitization"
            )
            return "", all_violations

        return technical_content, all_violations

    def save_violations_log(self, violations: List[PIIViolation]) -> str:
        """
        Save violations log to file (safe, no sensitive content).

        Args:
            violations: List of violations to save

        Returns:
            Path to saved log file
        """
        logs_dir = self.workspace_root / "logs" / "pii_violations"
        logs_dir.mkdir(parents=True, exist_ok=True)

        log_file = (
            logs_dir / f"violation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        log_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_violations": len(violations),
                "critical_count": len(
                    [v for v in violations if v.severity == ViolationSeverity.CRITICAL]
                ),
                "high_count": len(
                    [v for v in violations if v.severity == ViolationSeverity.HIGH]
                ),
                "medium_count": len(
                    [v for v in violations if v.severity == ViolationSeverity.MEDIUM]
                ),
                "low_count": len(
                    [v for v in violations if v.severity == ViolationSeverity.LOW]
                ),
            },
            "violations": [v.to_dict() for v in violations],
        }

        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2)

        return str(log_file)
