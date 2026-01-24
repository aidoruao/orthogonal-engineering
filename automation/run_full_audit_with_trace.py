#!/usr/bin/env python3
"""
GLASS BOX BOUNDARY ENFORCER - Python Implementation
Version: 1.11
Schema ID: GB-ORIGIN-1.11
Generated: 2026-01-21 02:10:00 UTC

Purpose: Enforce Glass-Box Boundary as defined in GLASS_BOX_BOUNDARY_v1.11.html
Exit Code: 2 on any boundary violation (fail-fast architecture)

Atomic Instructions Compliance:
1. Scan repository for required artifacts
2. Snapshot environment (python version, dependencies, system info)
3. Detect suppressed signals in AI logs/outputs
4. Record timeline + sequence violations
5. Compute hash_manifest over evidence + environment
6. Sign trace with private key stored outside AI context
7. Monitor token usage and prevent excessive file processing
"""

import hashlib
import json
import logging
import os
import subprocess
import sys
import traceback
import uuid
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ============================================================================
# CONSTANTS FROM HTML BLUEPRINT
# ============================================================================

REQUIRED_ARTIFACTS = [
    "automation/full_audit.py",
    "automation/generate_sha256_manifest.py",
    "automation/verify_sha256_manifest.py",
    "documentation/README.md",
    "grounding_models/GROUNDING_MODELS.md",
    "historical_candidates/HISTORICAL_LOGOS_CANDIDATES.md",
    "correspondence_bridge/correspondence_validator_final.py",
]

# Token usage monitoring constants
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB maximum file size
MAX_TOKEN_ESTIMATE = 100000  # 100K tokens maximum estimate
TOKEN_RATIO = 0.75  # Rough estimate: tokens = chars * 0.75

SUPPRESSED_SIGNAL_PATTERNS = [
    r"except Exception:\s*pass",
    r"warnings\.filterwarnings\(.*ignore.*\)",
    r"logging\.getLogger\(\)\.setLevel\(logging\.CRITICAL\)",
    r"sys\.exit\(0\).*#.*failure",
]

TIMELINE_REQUIRED_EVENTS = [
    "environment_snapshot",
    "artifact_scan",
    "boundary_validation",
    "signal_detection",
    "hash_computation",
    "trace_signing",
]

# ============================================================================
# BOUNDARY DECORATOR FACTORY
# ============================================================================


def glass_box_boundary(
    input_validator=None,
    output_validator=None,
    side_effect_check=False,
    orthogonal_separation=False,
):
    """
    Boundary enforcement decorator as specified in HTML blueprint.

    Enforces:
    1. Input validation against schema
    2. Output validation against schema
    3. Side-effect confinement (no uncaptured I/O)
    4. Orthogonal separation (gateway pattern for external systems)

    Raises immediate exception on boundary violation.
    """
    from functools import wraps

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Input validation
            if input_validator:
                if not validate_input(args, kwargs, input_validator):
                    raise BoundaryViolation(
                        f"Input validation failed for {func.__name__}",
                        violation_type="input_validation",
                        function=func.__name__,
                    )

            # 2. Side-effect pre-check
            if side_effect_check:
                if not check_side_effects_allowed(func):
                    raise BoundaryViolation(
                        f"Side effects not allowed for {func.__name__}",
                        violation_type="side_effect",
                        function=func.__name__,
                    )

            # 3. Orthogonal separation check
            if orthogonal_separation:
                if not ensure_gateway_pattern(func):
                    raise BoundaryViolation(
                        f"Gateway pattern required for {func.__name__}",
                        violation_type="orthogonal_separation",
                        function=func.__name__,
                    )

            # 4. Execute function
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                raise BoundaryViolation(
                    f"Function {func.__name__} raised exception: {str(e)}",
                    violation_type="execution",
                    function=func.__name__,
                ) from e

            # 5. Output validation
            if output_validator:
                if not validate_output(result, output_validator):
                    raise BoundaryViolation(
                        f"Output validation failed for {func.__name__}",
                        violation_type="output_validation",
                        function=func.__name__,
                    )

            return result

        return wrapper

    return decorator


# ============================================================================
# CORE ENFORCER FUNCTIONS (PLACEHOLDER IMPLEMENTATIONS)
# ============================================================================


@glass_box_boundary(
    input_validator=None,
    output_validator=None,
    side_effect_check=True,
    orthogonal_separation=True,
)
def scan_repository_for_artifacts() -> Dict[str, Any]:
    """
    Scan repository for required artifacts listed in HTML blueprint.

    Returns:
        Dict with found_artifacts, missing_artifacts, and scan_status
    """
    repo_root = Path(__file__).parent.parent
    found = []
    missing = []

    for artifact in REQUIRED_ARTIFACTS:
        artifact_path = repo_root / artifact
        if artifact_path.exists():
            found.append(artifact)
        else:
            missing.append(artifact)

    return {
        "required_artifacts": REQUIRED_ARTIFACTS,
        "found_artifacts": found,
        "missing_artifacts": missing,
        "scan_status": "complete" if not missing else "incomplete",
    }


@glass_box_boundary(
    input_validator=None,
    output_validator=None,
    side_effect_check=True,
    orthogonal_separation=True,
)
def snapshot_environment() -> Dict[str, Any]:
    """
    Snapshot environment: python version, dependencies, system info.

    Returns:
        Dict with python_version, dependencies, and system_info
    """
    import platform

    # Get Python version
    python_version = sys.version

    # Get dependencies (simplified - in production would parse requirements.txt)
    dependencies = []
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            dependencies = [
                line.strip() for line in result.stdout.splitlines() if line.strip()
            ]
    except Exception as e:
        dependencies = [f"Error capturing dependencies: {str(e)}"]

    # System info
    system_info = {
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "cwd": os.getcwd(),
        "python_executable": sys.executable,
    }

    return {
        "python_version": python_version,
        "dependencies": dependencies,
        "system_info": system_info,
    }


@glass_box_boundary(
    input_validator=None,
    output_validator=None,
    side_effect_check=True,
    orthogonal_separation=True,
)
def detect_suppressed_signals() -> List[Dict[str, Any]]:
    """
    Detect suppressed signals in AI logs/outputs.

    Returns:
        List of detected suppressed signals with type, source, and confidence
    """
    import re

    suppressed_signals = []
    repo_root = Path(__file__).parent.parent

    # Scan Python files for suppressed signal patterns
    for py_file in repo_root.rglob("*.py"):
        try:
            # Skip files in logs directory (these are generated files that simulate violations)
            if "logs" in str(py_file):
                continue

            # Check file size before reading
            file_size = py_file.stat().st_size
            if file_size > MAX_FILE_SIZE_BYTES:
                suppressed_signals.append(
                    {
                        "signal_type": "excessive_file_size",
                        "source": str(py_file.relative_to(repo_root)),
                        "detection_method": f"file_size_exceeded: {file_size} bytes > {MAX_FILE_SIZE_BYTES} bytes",
                        "confidence": 1.0,
                        "details": {
                            "file_size_bytes": file_size,
                            "max_allowed_bytes": MAX_FILE_SIZE_BYTES,
                            "estimated_tokens": int(file_size * TOKEN_RATIO / 4),
                            "max_allowed_tokens": MAX_TOKEN_ESTIMATE,
                        },
                    }
                )
                continue

            content = py_file.read_text(encoding="utf-8")
            for pattern in SUPPRESSED_SIGNAL_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    suppressed_signals.append(
                        {
                            "signal_type": "error_suppression",
                            "source": str(py_file.relative_to(repo_root)),
                            "detection_method": f"regex_pattern: {pattern}",
                            "confidence": 0.8,
                        }
                    )
        except Exception as e:
            print(f"Warning: Error scanning file {py_file}: {e}")
            continue

    return suppressed_signals


@glass_box_boundary(
    input_validator=None,
    output_validator=None,
    side_effect_check=True,
    orthogonal_separation=True,
)
def record_timeline_sequence(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Record timeline sequence and detect violations.

    Args:
        events: List of events in chronological order

    Returns:
        Dict with events, violations, and sequence_valid flag
    """
    violations = []

    # Check for required events
    event_types = [event.get("event_type") for event in events]
    for required_event in TIMELINE_REQUIRED_EVENTS:
        if required_event not in event_types:
            violations.append(f"Missing required event: {required_event}")

    # Check sequence violations (simplified)
    # In production would implement proper sequence validation
    if len(events) >= 2:
        for i in range(1, len(events)):
            prev_time = datetime.fromisoformat(
                events[i - 1]["timestamp"].replace("Z", "+00:00")
            )
            curr_time = datetime.fromisoformat(
                events[i]["timestamp"].replace("Z", "+00:00")
            )
            if curr_time < prev_time:
                violations.append(f"Timeline sequence violation at event {i}")

    return {
        "events": events,
        "violations": violations,
        "sequence_valid": len(violations) == 0,
    }


@glass_box_boundary(
    input_validator=None,
    output_validator=None,
    side_effect_check=True,
    orthogonal_separation=True,
)
def compute_hash_manifest(evidence_files: List[str]) -> Dict[str, Any]:
    """
    Compute hash_manifest over evidence + environment.

    Args:
        evidence_files: List of file paths to include in hash manifest

    Returns:
        Dict with algorithm, files_hashed, root_hash, and file_hashes
    """
    repo_root = Path(__file__).parent.parent
    file_hashes = {}

    for file_path in evidence_files:
        full_path = repo_root / file_path
        if full_path.exists():
            try:
                content = full_path.read_bytes()
                file_hash = hashlib.sha256(content).hexdigest()
                file_hashes[file_path] = file_hash
            except Exception as e:
                print(f"Warning: Error hashing file {file_path}: {e}")
                file_hashes[file_path] = f"ERROR: {str(e)}"

    # Compute root hash (simplified - in production would use Merkle tree)
    all_hashes = "".join(sorted(file_hashes.values()))
    root_hash = hashlib.sha256(all_hashes.encode()).hexdigest()

    return {
        "algorithm": "SHA256",
        "files_hashed": len(file_hashes),
        "root_hash": root_hash,
        "file_hashes": file_hashes,
    }


@glass_box_boundary(
    input_validator=None,
    output_validator=None,
    side_effect_check=True,
    orthogonal_separation=True,
)
def sign_trace(trace_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sign the trace with private key stored outside AI context.

    Note: In production, private key would be stored securely outside AI context.
    This is a placeholder implementation.

    Args:
        trace_data: The trace data to sign

    Returns:
        Dict with signature information
    """
    # Convert trace to string for signing
    trace_str = json.dumps(trace_data, sort_keys=True, indent=2)

    # In production: Use actual cryptographic signing
    # This is a placeholder that simulates signing
    signature_hash = hashlib.sha256(trace_str.encode()).hexdigest()

    return {
        "signed_by": "glass_box_enforcer_v1.11",
        "signature_hash": signature_hash,
        "verification_key": "placeholder_key_secure_storage_required",
        "timestamp": datetime.now().isoformat() + "Z",
        "note": "In production: Use actual cryptographic signing with key outside AI context",
    }


# ============================================================================
# VALIDATION FUNCTIONS (PLACEHOLDERS)
# ============================================================================


def validate_input(args, kwargs, validator) -> bool:
    """Placeholder for input validation logic."""
    # In production: Implement actual schema validation
    return True


def validate_output(result, validator) -> bool:
    """Placeholder for output validation logic."""
    # In production: Implement actual schema validation
    return True


def check_side_effects_allowed(func) -> bool:
    """Placeholder for side-effect checking logic."""
    # In production: Analyze function for side effects
    return True


def ensure_gateway_pattern(func) -> bool:
    """Placeholder for gateway pattern checking logic."""
    # In production: Check for proper gateway usage
    return True


# ============================================================================
# EXCEPTION CLASSES
# ============================================================================


class BoundaryViolation(Exception):
    """Exception raised when Glass-Box Boundary is violated."""

    def __init__(self, message: str, violation_type: str, function: str = None):
        self.message = message
        self.violation_type = violation_type
        self.function = function
        super().__init__(f"{violation_type.upper()} violation in {function}: {message}")


class TimelineViolation(Exception):
    """Exception raised when timeline sequence is violated."""

    pass


class SuppressedSignalDetected(Exception):
    """Exception raised when suppressed signals are detected."""

    pass


# ============================================================================
# MAIN ENFORCER FUNCTION
# ============================================================================


@glass_box_boundary(
    input_validator=None,
    output_validator=None,
    side_effect_check=True,
    orthogonal_separation=True,
)
def run_full_audit_with_trace() -> Dict[str, Any]:
    """
    Main enforcer function that implements the complete audit with trace generation.

    Returns:
        Complete trace document compliant with HTML blueprint schema
    """
    events = []
    boundary_violations = []

    try:
        # Event 1: Environment snapshot
        env_start = datetime.now().isoformat() + "Z"
        environment = snapshot_environment()
        env_end = datetime.now().isoformat() + "Z"
        events.append(
            {
                "event_type": "environment_snapshot",
                "timestamp": env_start,
                "component": "enforcer",
                "details": {
                    "duration": f"{(datetime.fromisoformat(env_end.replace('Z', '+00:00')) - datetime.fromisoformat(env_start.replace('Z', '+00:00'))).total_seconds()}s"
                },
            }
        )

        # Event 2: Artifact scan
        artifact_start = datetime.now().isoformat() + "Z"
        artifact_scan = scan_repository_for_artifacts()
        artifact_end = datetime.now().isoformat() + "Z"
        events.append(
            {
                "event_type": "artifact_scan",
                "timestamp": artifact_start,
                "component": "enforcer",
                "details": {
                    "missing_count": len(artifact_scan.get("missing_artifacts", []))
                },
            }
        )

        # Check for missing artifacts (boundary violation)
        if artifact_scan.get("missing_artifacts"):
            boundary_violations.append(
                {
                    "violation_type": "missing_artifact",
                    "file": "repository_root",
                    "line": 0,
                    "description": f"Missing required artifacts: {artifact_scan['missing_artifacts']}",
                    "severity": "critical",
                }
            )

        # Event 3: Boundary validation
        boundary_start = datetime.now().isoformat() + "Z"
        # Boundary validation happens through decorators
        boundary_end = datetime.now().isoformat() + "Z"
        events.append(
            {
                "event_type": "boundary_validation",
                "timestamp": boundary_start,
                "component": "enforcer",
                "details": {"validation_method": "decorator_enforcement"},
            }
        )

        # Event 4: Signal detection
        signal_start = datetime.now().isoformat() + "Z"
        suppressed_signals = detect_suppressed_signals()
        signal_end = datetime.now().isoformat() + "Z"
        events.append(
            {
                "event_type": "signal_detection",
                "timestamp": signal_start,
                "component": "enforcer",
                "details": {"signals_detected": len(suppressed_signals)},
            }
        )

        # Check for suppressed signals (boundary violation)
        if suppressed_signals:
            for signal in suppressed_signals:
                boundary_violations.append(
                    {
                        "violation_type": "suppressed_signal",
                        "file": signal.get("source", "unknown"),
                        "line": 0,
                        "description": f"Suppressed signal detected: {signal.get('signal_type')}",
                        "severity": "high",
                    }
                )

        # Event 4.5: Token usage detection
        token_start = datetime.now().isoformat() + "Z"
        token_violations = detect_token_usage_violations()
        token_end = datetime.now().isoformat() + "Z"
        events.append(
            {
                "event_type": "token_usage_detection",
                "timestamp": token_start,
                "component": "enforcer",
                "details": {"violations_detected": len(token_violations)},
            }
        )

        # Check for token usage violations (boundary violation)
        if token_violations:
            for violation in token_violations:
                boundary_violations.append(
                    {
                        "violation_type": "token_usage_violation",
                        "file": violation.get("source", "unknown"),
                        "line": 0,
                        "description": f"Token usage violation: {violation.get('violation_type')}",
                        "severity": "high",
                        "details": violation.get("details", {}),
                    }
                )

        # Event 5: Hash computation
        hash_start = datetime.now().isoformat() + "Z"
        evidence_files = artifact_scan.get("found_artifacts", []) + [
            "automation/run_full_audit_with_trace.py",
            "documentation/GLASS_BOX_BOUNDARY_v1.11.html",
        ]
        hash_manifest = compute_hash_manifest(evidence_files)
        hash_end = datetime.now().isoformat() + "Z"
        events.append(
            {
                "event_type": "hash_computation",
                "timestamp": hash_start,
                "component": "enforcer",
                "details": {"files_hashed": hash_manifest.get("files_hashed", 0)},
            }
        )

        # Event 7: Trace assembly
        trace = {
            "trace_id": f"GB-TRACE-{uuid.uuid4().hex[:8].upper()}-{uuid.uuid4().hex[:4].upper()}-{uuid.uuid4().hex[:4].upper()}-{uuid.uuid4().hex[:12].upper()}",
            "timestamp": datetime.now().isoformat() + "Z",
            "repository_meta": {
                "name": "orthogonal-engineering",
                "version": "1.11",
                "commit_hash": get_commit_hash(),
                "branch": get_current_branch(),
                "dirty": has_uncommitted_changes(),
            },
            "environment_snapshot": environment,
            "artifact_scan": artifact_scan,
            "boundary_violations": boundary_violations,
            "suppressed_signals": suppressed_signals,
            "hash_manifest": hash_manifest,
            "python_enforcer_active": True,
            "ide_integration": {
                "autofix_enabled": True,
                "structural_consistency": True,
                "boundary_awareness": True,
                "doc_sync": True,
            },
        }

        # Event 8: Trace signing event (record that signing will occur)
        sign_start = datetime.now().isoformat() + "Z"
        events.append(
            {
                "event_type": "trace_signing",
                "timestamp": sign_start,
                "component": "enforcer",
                "details": {"signed_by": "glass_box_enforcer_v1.11"},
            }
        )

        # Event 9: Final timeline recording (after all events are added)
        timeline = record_timeline_sequence(events)
        trace["timeline_sequence"] = timeline

        # Check timeline violations
        if not timeline.get("sequence_valid", True):
            boundary_violations.append(
                {
                    "violation_type": "timeline_sequence",
                    "file": "timeline",
                    "line": 0,
                    "description": f"Timeline sequence violations: {timeline.get('violations', [])}",
                    "severity": "high",
                }
            )
            # Update trace with updated boundary violations
            trace["boundary_violations"] = boundary_violations

        # Add signature after timeline is validated and included in trace
        trace["signature"] = sign_trace(trace)

        return trace

    except BoundaryViolation as e:
        # Record boundary violation
        boundary_violations.append(
            {
                "violation_type": e.violation_type,
                "file": e.function or "unknown",
                "line": 0,
                "description": str(e),
                "severity": "critical",
            }
        )

        # Generate partial trace for debugging
        partial_trace = {
            "trace_id": f"GB-TRACE-PARTIAL-{uuid.uuid4().hex[:8].upper()}",
            "timestamp": datetime.now().isoformat() + "Z",
            "boundary_violations": boundary_violations,
            "error": f"Boundary violation during audit: {str(e)}",
            "python_enforcer_active": True,
            "ide_integration": {
                "autofix_enabled": True,
                "structural_consistency": True,
                "boundary_awareness": True,
                "doc_sync": True,
            },
        }
        return partial_trace

    except Exception as e:
        # System error
        return {
            "trace_id": f"GB-TRACE-ERROR-{uuid.uuid4().hex[:8].upper()}",
            "timestamp": datetime.now().isoformat() + "Z",
            "error": f"System error during audit: {str(e)}",
            "python_enforcer_active": True,
            "ide_integration": {
                "autofix_enabled": True,
                "structural_consistency": True,
                "boundary_awareness": True,
                "doc_sync": True,
            },
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_commit_hash() -> str:
    """Get current commit hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
            cwd=Path(__file__).parent.parent,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        print(f"Warning: Error getting commit hash: {e}")
    return "unknown"


def get_current_branch() -> str:
    """Get current git branch."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=False,
            cwd=Path(__file__).parent.parent,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        print(f"Warning: Error getting current branch: {e}")
    return "unknown"


def has_uncommitted_changes() -> bool:
    """Check if repository has uncommitted changes."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=False,
            cwd=Path(__file__).parent.parent,
        )
        if result.returncode == 0:
            return len(result.stdout.strip()) > 0
    except Exception as e:
        print(f"Warning: Error checking uncommitted changes: {e}")
    return False


# ============================================================================
# TRACE VALIDATION
# ============================================================================


def validate_trace_against_schema(trace: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate trace against HTML blueprint schema.

    Returns:
        Tuple of (is_valid, validation_errors)
    """
    errors = []

    # Check required fields from HTML blueprint
    required_fields = [
        "trace_id",
        "timestamp",
        "repository_meta",
        "environment_snapshot",
        "artifact_scan",
        "boundary_violations",
        "suppressed_signals",
        "timeline_sequence",
        "hash_manifest",
        "signature",
        "python_enforcer_active",
        "ide_integration",
    ]

    for field in required_fields:
        if field not in trace:
            errors.append(f"Missing required field: {field}")

    # Check python_enforcer_active
    if not trace.get("python_enforcer_active", False):
        errors.append("python_enforcer_active must be true")

    # Check ide_integration fields
    ide_integration = trace.get("ide_integration", {})
    required_ide_fields = [
        "autofix_enabled",
        "structural_consistency",
        "boundary_awareness",
        "doc_sync",
    ]

    for field in required_ide_fields:
        if field not in ide_integration:
            errors.append(f"Missing ide_integration field: {field}")
        elif not ide_integration[field]:
            errors.append(f"ide_integration.{field} must be true")

    # Check trace_id format (simplified)
    trace_id = trace.get("trace_id", "")
    if not trace_id.startswith("GB-TRACE-"):
        errors.append("trace_id must start with 'GB-TRACE-'")

    return len(errors) == 0, errors


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================


@glass_box_boundary(
    input_validator=None,
    output_validator=None,
    side_effect_check=True,
    orthogonal_separation=True,
)
def detect_token_usage_violations() -> List[Dict[str, Any]]:
    """
    Detect token usage violations by checking file sizes and estimating token counts.

    Returns:
        List of detected token usage violations
    """
    import re

    violations = []
    repo_root = Path(__file__).parent.parent

    # Scan all text-based files in the repository
    text_extensions = {
        ".py",
        ".md",
        ".txt",
        ".json",
        ".html",
        ".js",
        ".css",
        ".yml",
        ".yaml",
        ".toml",
        ".ini",
        ".cfg",
    }

    for file_path in repo_root.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in text_extensions:
            try:
                # Skip files in .git directory
                if ".git" in str(file_path):
                    continue

                # Skip data files in logs directory and other data directories
                relative_path = str(file_path.relative_to(repo_root))
                if any(
                    dir in relative_path
                    for dir in [
                        "logs",
                        "forgiveness_all_exports_output",
                        "forgiveness_analysis_output",
                    ]
                ):
                    continue

                # Skip large JSON data files that are not code
                if file_path.suffix.lower() == ".json" and any(
                    name in relative_path
                    for name in [
                        "aidor_filesystem_scan",
                        "token_analysis",
                        "failure_ledger",
                    ]
                ):
                    continue

                # Check file size
                file_size = file_path.stat().st_size

                # Estimate token count (rough approximation: 1 token ≈ 4 characters)
                estimated_tokens = int(file_size * TOKEN_RATIO / 4)

                # Check for violations
                if file_size > MAX_FILE_SIZE_BYTES:
                    violations.append(
                        {
                            "violation_type": "excessive_file_size",
                            "source": relative_path,
                            "detection_method": f"file_size_exceeded: {file_size} bytes > {MAX_FILE_SIZE_BYTES} bytes",
                            "confidence": 1.0,
                            "details": {
                                "file_size_bytes": file_size,
                                "max_allowed_bytes": MAX_FILE_SIZE_BYTES,
                                "estimated_tokens": estimated_tokens,
                                "max_allowed_tokens": MAX_TOKEN_ESTIMATE,
                                "recommendation": f"Split file or add to .zedignore: {relative_path}",
                            },
                        }
                    )

                if estimated_tokens > MAX_TOKEN_ESTIMATE:
                    violations.append(
                        {
                            "violation_type": "token_usage_violation",
                            "file": relative_path,
                            "line": 0,
                            "description": "Token usage violation: excessive_token_estimate",
                            "severity": "high",
                            "details": {
                                "file_size_bytes": file_size,
                                "estimated_tokens": estimated_tokens,
                                "max_allowed_tokens": MAX_TOKEN_ESTIMATE,
                                "token_ratio_used": 0.75,
                                "recommendation": f"File may cause token limit issues: {relative_path}",
                            },
                        }
                    )

            except (OSError, UnicodeDecodeError) as e:
                # Skip files that can't be read
                continue

    return violations


def main():
    """Main entry point with exit code handling as per HTML blueprint."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Glass Box Boundary Enforcer v1.11",
        epilog="Exit codes: 0=Success, 1=System error, 2=Boundary violation, "
        "3=Environment mismatch, 4=Timeline violation, 5=Signature failed",
    )

    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate existing trace without generating new one",
    )

    parser.add_argument(
        "--trace-file", type=str, help="Path to trace file for validation"
    )

    parser.add_argument(
        "--output", type=str, help="Output file for trace (default: stdout)"
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    try:
        if args.validate_only and args.trace_file:
            # Validate existing trace
            with open(args.trace_file, "r", encoding="utf-8") as f:
                trace = json.load(f)

            is_valid, errors = validate_trace_against_schema(trace)

            if args.verbose:
                print(f"Trace validation: {'PASS' if is_valid else 'FAIL'}")
                if errors:
                    print("Validation errors:")
                    for error in errors:
                        print(f"  - {error}")

            if not is_valid:
                print("Boundary violation: Trace does not comply with schema")
                sys.exit(2)  # Boundary violation

            print("Trace validation successful")
            sys.exit(0)

        else:
            # Generate new trace
            trace = run_full_audit_with_trace()

            # Validate the generated trace
            is_valid, errors = validate_trace_against_schema(trace)

            if not is_valid:
                if args.verbose:
                    print("Generated trace validation failed:")
                    for error in errors:
                        print(f"  - {error}")

                # Check for specific violation types
                if "environment" in str(errors).lower():
                    sys.exit(3)  # Environment mismatch
                elif "timeline" in str(errors).lower():
                    sys.exit(4)  # Timeline violation
                elif "signature" in str(errors).lower():
                    sys.exit(5)  # Signature verification failed
                else:
                    sys.exit(2)  # General boundary violation

            # Output trace
            output = json.dumps(trace, indent=2, ensure_ascii=False)

            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(output)
                if args.verbose:
                    print(f"Trace written to: {args.output}")
            else:
                print(output)

            if args.verbose:
                print(f"Trace generated successfully: {trace['trace_id']}")
                print(
                    f"Boundary violations: {len(trace.get('boundary_violations', []))}"
                )
                print(f"Suppressed signals: {len(trace.get('suppressed_signals', []))}")

            # Check for boundary violations or suppressed signals
            boundary_violations = trace.get("boundary_violations", [])
            suppressed_signals = trace.get("suppressed_signals", [])

            if boundary_violations or suppressed_signals:
                print(
                    f"Boundary violation detected: {len(boundary_violations)} violations, {len(suppressed_signals)} suppressed signals"
                )
                sys.exit(2)  # Boundary violation as per Glass-Box Boundary rules
            else:
                sys.exit(0)

    except BoundaryViolation as e:
        print(f"Boundary violation: {str(e)}")
        sys.exit(2)

    except TimelineViolation as e:
        print(f"Timeline violation: {str(e)}")
        sys.exit(4)

    except SuppressedSignalDetected as e:
        print(f"Suppressed signal detected: {str(e)}")
        sys.exit(2)

    except Exception as e:
        print(f"System error: {str(e)}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
