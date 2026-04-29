"""Failure Logger - failure_logger.py - Orthogonal Engineering Failure Logging System"""
# failure_logger.py - Orthogonal Engineering Failure Logging System
# Glass Box Methodology - Ontological Failure Tracking
# Version: 1.0.0
# Date: 2026-01-20
# Methodology: Orthogonal Engineering with Popperian Falsification

import datetime
import hashlib
import inspect
import json
import os
import sys
import traceback
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# ============================================================================
# ONTOLOGICAL FAILURE TYPES
# ============================================================================


class FailureType(Enum):
    """Types of failures in orthogonal engineering methodology"""

    # Epistemological Failures
    FALSIFICATION_FAILURE = "falsification_failure"  # Claim failed falsification test
    CORRESPONDENCE_FAILURE = "correspondence_failure"  # Output doesn't match reality
    TRANSPARENCY_FAILURE = "transparency_failure"  # Lack of visibility into process
    AUDIT_FAILURE = "audit_failure"  # Missing or incomplete audit trail

    # Methodological Failures
    GLASS_BOX_FAILURE = "glass_box_failure"  # Black box detected
    ATOMICITY_FAILURE = "atomicity_failure"  # Operation not atomic
    INVARIANT_FAILURE = "invariant_failure"  # Invariant violated
    REPRODUCIBILITY_FAILURE = "reproducibility_failure"  # Cannot reproduce results

    # Implementation Failures
    TOOL_FAILURE = "tool_failure"  # Tool doesn't work as claimed
    DETECTOR_FAILURE = "detector_failure"  # Pattern detector failed
    STATISTICAL_FAILURE = "statistical_failure"  # Statistical analysis invalid
    VALIDATION_FAILURE = "validation_failure"  # Validation process failed

    # Documentation Failures
    CLAIM_DOCUMENTATION_FAILURE = (
        "claim_documentation_failure"  # Claim not properly documented
    )
    EVIDENCE_FAILURE = "evidence_failure"  # Evidence missing or insufficient
    VERIFICATION_FAILURE = "verification_failure"  # Verification steps missing

    # System Failures
    PIPELINE_FAILURE = "pipeline_failure"  # Pipeline execution failed
    INTEGRATION_FAILURE = "integration_failure"  # System integration failed
    DEPENDENCY_FAILURE = "dependency_failure"  # Dependency issue


class FailureSeverity(Enum):
    """Severity levels for failures"""

    CRITICAL = "critical"  # Blocks all use, violates core premises
    HIGH = "high"  # Limits adoption, violates key premises
    MEDIUM = "medium"  # Impacts quality, violates secondary premises
    LOW = "low"  # Polish issues, minor premise violations
    INFO = "info"  # Observations, no premise violations


class FailureStatus(Enum):
    """Status of failure resolution"""

    OPEN = "open"  # Failure not addressed
    IN_PROGRESS = "in_progress"  # Being worked on
    RESOLVED = "resolved"  # Fixed and verified
    WONT_FIX = "wont_fix"  # Will not be fixed
    DUPLICATE = "duplicate"  # Duplicate of another failure
    INVALID = "invalid"  # Not actually a failure


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class FailureContext:
    """Context in which failure occurred"""

    tool_name: str
    function_name: str
    line_number: Optional[int] = None
    git_commit: Optional[str] = None
    timestamp: str = field(
        default_factory=lambda: datetime.datetime.utcnow().isoformat() + "Z"
    )
    environment: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Set default environment information"""
        if not self.environment:
            self.environment = {
                "python_version": sys.version,
                "platform": sys.platform,
                "cwd": os.getcwd(),
            }


@dataclass
class FailureEvidence:
    """Evidence supporting failure claim"""

    description: str
    data: Optional[Any] = None
    data_hash: Optional[str] = None
    source_file: Optional[str] = None
    line_numbers: Optional[List[int]] = None
    screenshot_path: Optional[str] = None
    log_excerpt: Optional[str] = None

    def __post_init__(self):
        """Calculate hash if data provided"""
        if self.data is not None and self.data_hash is None:
            self.data_hash = self._calculate_data_hash()

    def _calculate_data_hash(self) -> str:
        """Calculate hash of evidence data"""
        try:
            if isinstance(self.data, (dict, list)):
                data_str = json.dumps(self.data, sort_keys=True)
            else:
                data_str = str(self.data)
            return hashlib.sha256(data_str.encode()).hexdigest()[:16]
        except:
            return "hash_calculation_failed"


@dataclass
class FailureImpact:
    """Impact analysis of the failure"""

    affected_claims: List[str] = field(default_factory=list)
    affected_tools: List[str] = field(default_factory=list)
    methodology_implications: List[str] = field(default_factory=list)
    user_impact: str = ""
    timeline_impact: str = ""

    def add_affected_claim(self, claim_id: str):
        """Add affected claim to list"""
        if claim_id not in self.affected_claims:
            self.affected_claims.append(claim_id)

    def add_affected_tool(self, tool_name: str):
        """Add affected tool to list"""
        if tool_name not in self.affected_tools:
            self.affected_tools.append(tool_name)


@dataclass
class FailureResolution:
    """Resolution plan for failure"""

    required_actions: List[str] = field(default_factory=list)
    priority: str = "medium"  # immediate, high, medium, low
    estimated_effort: str = ""  # e.g., "2 hours", "1 week"
    assigned_to: Optional[str] = None
    target_date: Optional[str] = None
    verification_method: str = ""

    def add_action(self, action: str):
        """Add required action"""
        if action not in self.required_actions:
            self.required_actions.append(action)


@dataclass
class FailureEntry:
    """Complete failure entry with ontological tracking"""

    # Core identification (no defaults first)
    failure_id: str
    title: str
    description: str
    failure_type: FailureType
    severity: FailureSeverity
    context: FailureContext

    # Fields with defaults (must come after fields without defaults)
    status: FailureStatus = FailureStatus.OPEN

    # Evidence
    evidence: List[FailureEvidence] = field(default_factory=list)
    reproduction_steps: List[str] = field(default_factory=list)

    # Impact analysis
    impact: FailureImpact = field(default_factory=FailureImpact)

    # Resolution
    resolution: FailureResolution = field(default_factory=FailureResolution)

    # Metadata
    created_at: str = field(
        default_factory=lambda: datetime.datetime.utcnow().isoformat() + "Z"
    )
    updated_at: str = field(
        default_factory=lambda: datetime.datetime.utcnow().isoformat() + "Z"
    )
    discovered_by: Optional[str] = None
    verified_by: Optional[str] = None

    # Ontological tracking
    ontological_premises_violated: List[str] = field(default_factory=list)
    falsifiable_claims_generated: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Initialize with default values"""
        self.updated_at = datetime.datetime.utcnow().isoformat() + "Z"

        # Generate failure ID if not provided
        if not self.failure_id:
            prefix = self.failure_type.value.upper().replace("_", "-")
            timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
            self.failure_id = f"{prefix}-{timestamp}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)

        # Convert enums to strings
        data["failure_type"] = self.failure_type.value
        data["severity"] = self.severity.value
        data["status"] = self.status.value

        # Convert nested dataclasses
        data["context"] = asdict(self.context)
        data["evidence"] = [asdict(e) for e in self.evidence]
        data["impact"] = asdict(self.impact)
        data["resolution"] = asdict(self.resolution)

        return data

    def add_evidence(self, evidence: FailureEvidence):
        """Add evidence to failure entry"""
        self.evidence.append(evidence)
        self.updated_at = datetime.datetime.utcnow().isoformat() + "Z"

    def add_reproduction_step(self, step: str):
        """Add reproduction step"""
        if step not in self.reproduction_steps:
            self.reproduction_steps.append(step)
            self.updated_at = datetime.datetime.utcnow().isoformat() + "Z"

    def update_status(self, new_status: FailureStatus, notes: str = ""):
        """Update failure status"""
        self.status = new_status
        self.updated_at = datetime.datetime.utcnow().isoformat() + "Z"

        if notes:
            if not hasattr(self, "status_notes"):
                self.status_notes = []
            self.status_notes.append(
                {
                    "timestamp": self.updated_at,
                    "status": new_status.value,
                    "notes": notes,
                }
            )

    def calculate_hash(self) -> str:
        """Calculate hash of failure entry for verification"""
        data = self.to_dict()
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()


# ============================================================================
# FAILURE LOGGER CLASS
# ============================================================================


class FailureLogger:
    """Main failure logging system with ontological tracking"""

    def __init__(self, log_directory: str = "failure_logs"):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(exist_ok=True)

        self.failures: Dict[str, FailureEntry] = {}
        self.current_session_id = self._generate_session_id()

        # Initialize session log
        self.session_log_path = (
            self.log_directory / f"session_{self.current_session_id}.json"
        )
        self._initialize_session_log()

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.md5(str(os.getpid()).encode()).hexdigest()[:6]
        return f"{timestamp}_{random_suffix}"

    def _initialize_session_log(self):
        """Initialize session log file"""
        session_info = {
            "session_id": self.current_session_id,
            "start_time": datetime.datetime.utcnow().isoformat() + "Z",
            "environment": {
                "python_version": sys.version,
                "platform": sys.platform,
                "cwd": os.getcwd(),
                "argv": sys.argv,
            },
            "failures_logged": 0,
            "failures": [],
        }

        with open(self.session_log_path, "w", encoding="utf-8") as f:
            json.dump(session_info, f, indent=2)

    def log_failure(
        self,
        title: str,
        description: str,
        failure_type: FailureType,
        severity: FailureSeverity,
        tool_name: str,
        evidence_data: Optional[Any] = None,
        exception: Optional[Exception] = None,
        affected_claims: Optional[List[str]] = None,
        reproduction_steps: Optional[List[str]] = None,
        **kwargs,
    ) -> FailureEntry:
        """Log a new failure with full ontological tracking"""

        # Get calling context
        caller_frame = inspect.currentframe().f_back
        function_name = caller_frame.f_code.co_name if caller_frame else "unknown"
        line_number = caller_frame.f_lineno if caller_frame else None

        # Create context
        context = FailureContext(
            tool_name=tool_name,
            function_name=function_name,
            line_number=line_number,
            environment={
                "python_version": sys.version,
                "platform": sys.platform,
                "cwd": os.getcwd(),
            },
        )

        # Create evidence
        evidence_list = []
        if evidence_data is not None:
            evidence = FailureEvidence(
                description="Failure evidence data", data=evidence_data
            )
            evidence_list.append(evidence)

        if exception is not None:
            exception_evidence = FailureEvidence(
                description=f"Exception: {type(exception).__name__}",
                data={
                    "exception_type": type(exception).__name__,
                    "exception_message": str(exception),
                    "traceback": traceback.format_exc(),
                },
            )
            evidence_list.append(exception_evidence)

        # Create impact analysis
        impact = FailureImpact()
        if affected_claims:
            for claim in affected_claims:
                impact.add_affected_claim(claim)

        # Determine ontological premises violated
        ontological_premises = self._determine_ontological_premises(
            failure_type, severity, description
        )

        # Generate falsifiable claims from failure
        falsifiable_claims = self._generate_falsifiable_claims(
            title, description, failure_type
        )

        # Create failure entry
        failure_entry = FailureEntry(
            failure_id="",  # Will be auto-generated
            title=title,
            description=description,
            failure_type=failure_type,
            severity=severity,
            context=context,
            evidence=evidence_list,
            impact=impact,
            ontological_premises_violated=ontological_premises,
            falsifiable_claims_generated=falsifiable_claims,
            **kwargs,
        )

        # Add reproduction steps if provided
        if reproduction_steps:
            for step in reproduction_steps:
                failure_entry.add_reproduction_step(step)

        # Store failure
        self.failures[failure_entry.failure_id] = failure_entry

        # Save to session log
        self._save_to_session_log(failure_entry)

        # Save individual failure file
        self._save_individual_failure(failure_entry)

        # Update master failure index
        self._update_master_index(failure_entry)

        return failure_entry

    def _determine_ontological_premises(
        self, failure_type: FailureType, severity: FailureSeverity, description: str
    ) -> List[str]:
        """Determine which ontological premises are violated"""
        premises = []

        # Map failure types to premises
        premise_mapping = {
            FailureType.FALSIFICATION_FAILURE: [
                "falsifiability",
                "scientific_method",
                "claim_verification",
            ],
            FailureType.CORRESPONDENCE_FAILURE: [
                "correspondence",
                "reality_grounding",
                "implementation_validation",
            ],
            FailureType.TRANSPARENCY_FAILURE: [
                "transparency",
                "glass_box",
                "inspectability",
            ],
            FailureType.AUDIT_FAILURE: [
                "auditability",
                "traceability",
                "verification_chain",
            ],
            FailureType.GLASS_BOX_FAILURE: [
                "glass_box",
                "transparency",
                "no_black_boxes",
            ],
            FailureType.ATOMICITY_FAILURE: [
                "atomic_operations",
                "transactional_integrity",
                "rollback_capability",
            ],
            FailureType.INVARIANT_FAILURE: [
                "invariant_preservation",
                "methodology_consistency",
                "claim_integrity",
            ],
            FailureType.REPRODUCIBILITY_FAILURE: [
                "reproducibility",
                "scientific_standards",
                "independent_verification",
            ],
            FailureType.DETECTOR_FAILURE: [
                "tool_validation",
                "pattern_recognition_accuracy",
                "false_positive_control",
            ],
            FailureType.STATISTICAL_FAILURE: [
                "statistical_rigor",
                "mathematical_correctness",
                "significance_validation",
            ],
        }

        # Add premises based on failure type
        if failure_type in premise_mapping:
            premises.extend(premise_mapping[failure_type])

        # Add severity-based premises
        if severity == FailureSeverity.CRITICAL:
            premises.append("methodology_integrity")
            premises.append("core_functionality")

        if severity in [FailureSeverity.CRITICAL, FailureSeverity.HIGH]:
            premises.append("adoption_blocker")

        # Add description-based premises
        description_lower = description.lower()
        if any(word in description_lower for word in ["black box", "opaque", "hidden"]):
            premises.append("anti_blackbox_violation")

        if any(
            word in description_lower
            for word in ["cannot reproduce", "not reproducible"]
        ):
            premises.append("reproducibility_violation")

        if any(
            word in description_lower for word in ["no evidence", "missing evidence"]
        ):
            premises.append("evidence_requirement_violation")

        return list(set(premises))  # Remove duplicates

    def _generate_falsifiable_claims(
        self, title: str, description: str, failure_type: FailureType
    ) -> List[str]:
        """Generate falsifiable claims from failure"""
        claims = []

        # Base claim about failure existence
        claims.append(f"Failure '{title}' exists and is documented")

        # Type-specific claims
        if failure_type == FailureType.FALSIFICATION_FAILURE:
            claims.append(f"Claim in '{title}' failed falsification test")
            claims.append("Falsification methodology correctly identified failure")

        elif failure_type == FailureType.CORRESPONDENCE_FAILURE:
            claims.append(f"Output doesn't correspond to reality in '{title}'")
            claims.append("Correspondence validation would detect this failure")

        elif failure_type == FailureType.DETECTOR_FAILURE:
            claims.append(f"Detector in '{title}' has accuracy issues")

        return claims

    def _save_to_session_log(self, failure_entry):
        """Save failure to session log file."""
        try:
            with open(self.session_log_path, "r", encoding="utf-8") as f:
                session = json.load(f)
            session["failures"].append(failure_entry.to_dict())
            session["failures_logged"] = len(session["failures"])
            with open(self.session_log_path, "w", encoding="utf-8") as f:
                json.dump(session, f, indent=2)
        except Exception:
            pass

    def _save_individual_failure(self, failure_entry):
        """Save individual failure to its own file."""
        try:
            path = self.log_directory / f"{failure_entry.failure_id}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(failure_entry.to_dict(), f, indent=2)
        except Exception:
            pass

    def _update_master_index(self, failure_entry):
        """Update master failure index."""
        index_path = self.log_directory / "master_index.json"
        try:
            if index_path.exists():
                with open(index_path, "r", encoding="utf-8") as f:
                    index = json.load(f)
            else:
                index = {"failures": []}
            index["failures"].append({
                "failure_id": failure_entry.failure_id,
                "title": failure_entry.title,
                "severity": failure_entry.severity.value,
                "status": failure_entry.status.value,
            })
            with open(index_path, "w", encoding="utf-8") as f:
                json.dump(index, f, indent=2)
        except Exception:
            pass


def log_failure(title, description, failure_type=FailureType.TOOL_FAILURE,
                severity=FailureSeverity.MEDIUM, tool_name="unknown", **kwargs):
    """Curated API entry point for failure logging."""
    logger = FailureLogger()
    return logger.log_failure(
        title=title,
        description=description,
        failure_type=failure_type,
        severity=severity,
        tool_name=tool_name,
        **kwargs,
    )
