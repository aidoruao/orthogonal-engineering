"""
Session Continuity System - Maintains boundary state across AI sessions

Prevents "willy-nilly" AI behavior by preserving boundary enforcement state
across IDE crashes, AI instance restarts, and session boundaries.

Implements "continuity of body" for the Glass-Box Boundary system:
- Persists boundary violation state across sessions
- Maintains regex ban enforcement continuity
- Recovers from IDE crashes caused by combinatorial explosions
- Preserves autofix application history
- Ensures consistent boundary enforcement

Author: Orthogonal Engineering System
Date: 2026-01-24
Version: 1.0.0
"""

import json
import os
import pickle
import shutil
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from toolkit.oe.regex_boundary_enforcer import RegexBoundaryEnforcer, RegexViolation


class ContinuityState(Enum):
    """State of session continuity."""

    HEALTHY = "healthy"  # Normal operation, no recent crashes
    RECOVERING = "recovering"  # Recovering from crash
    DEGRADED = "degraded"  # Multiple recent crashes
    CRITICAL = "critical"  # Frequent crashes, boundary enforcement at risk
    LOST = "lost"  # Complete loss of continuity


class CrashCause(Enum):
    """Causes of IDE/AI session crashes."""

    REGEX_COMBINATORIAL_EXPLOSION = "regex_combinatorial_explosion"
    MEMORY_OVERFLOW = "memory_overflow"
    TOKEN_EXHAUSTION = "token_exhaustion"
    INFINITE_LOOP = "infinite_loop"
    DEADLOCK = "deadlock"
    UNKNOWN = "unknown"


@dataclass
class SessionCrash:
    """Record of a session crash."""

    crash_id: str
    timestamp: datetime
    cause: CrashCause
    file_path: Optional[str]
    line_number: Optional[int]
    offending_pattern: Optional[str]  # For regex crashes
    memory_usage_mb: Optional[float]
    token_count: Optional[int]
    stack_trace: Optional[str]
    recovery_attempted: bool = False
    recovery_successful: bool = False
    boundary_violations_detected: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "crash_id": self.crash_id,
            "timestamp": self.timestamp.isoformat(),
            "cause": self.cause.value,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "offending_pattern": self.offending_pattern,
            "memory_usage_mb": self.memory_usage_mb,
            "token_count": self.token_count,
            "recovery_attempted": self.recovery_attempted,
            "recovery_successful": self.recovery_successful,
            "boundary_violations_detected": self.boundary_violations_detected,
        }


@dataclass
class BoundaryState:
    """State of boundary enforcement across sessions."""

    session_id: str
    start_time: datetime
    last_activity: datetime
    total_edits: int = 0
    boundary_checks: int = 0
    violations_detected: int = 0
    fixes_applied: int = 0
    crashes_experienced: int = 0
    regex_violations: List[RegexViolation] = field(default_factory=list)
    active_bans: Dict[str, Any] = field(default_factory=dict)
    continuity_score: float = 1.0  # 0.0 to 1.0
    state: ContinuityState = ContinuityState.HEALTHY

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "total_edits": self.total_edits,
            "boundary_checks": self.boundary_checks,
            "violations_detected": self.violations_detected,
            "fixes_applied": self.fixes_applied,
            "crashes_experienced": self.crashes_experienced,
            "regex_violation_count": len(self.regex_violations),
            "active_bans": self.active_bans,
            "continuity_score": self.continuity_score,
            "state": self.state.value,
        }


class SessionContinuity:
    """
    Maintains continuity of boundary enforcement across AI sessions.

    Prevents the "willy-nilly" AI behavior by:
    1. Persisting boundary state across crashes
    2. Remembering regex violations that caused previous crashes
    3. Maintaining ban lists for dangerous patterns
    4. Providing crash recovery mechanisms
    5. Ensuring consistent enforcement despite AI instance changes
    """

    def __init__(self, workspace_root: str, session_id: Optional[str] = None):
        """
        Initialize session continuity system.

        Args:
            workspace_root: Root directory of the workspace
            session_id: Optional session ID (generated if None)
        """
        self.workspace_root = Path(workspace_root)
        self.session_id = session_id or f"session_{uuid.uuid4().hex[:8]}"
        self.state_file = (
            self.workspace_root / "logs" / "session_state" / f"{self.session_id}.json"
        )
        self.crash_log_dir = self.workspace_root / "logs" / "crashes"
        self.recovery_dir = self.workspace_root / "logs" / "recovery"

        # Create necessary directories
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.crash_log_dir.mkdir(parents=True, exist_ok=True)
        self.recovery_dir.mkdir(parents=True, exist_ok=True)

        # Initialize state
        self.boundary_state = self._load_state() or BoundaryState(
            session_id=self.session_id,
            start_time=datetime.now(),
            last_activity=datetime.now(),
        )

        # Regex boundary enforcer for crash analysis
        self.regex_enforcer = RegexBoundaryEnforcer(workspace_root)

        # Crash history
        self.crash_history: List[SessionCrash] = []
        self._load_crash_history()

        # Lock for thread safety
        self._lock = threading.RLock()

        # Auto-save timer
        self._auto_save_timer = None
        self._start_auto_save()

        # Initialize active bans based on crash history
        self._initialize_bans_from_history()

    def _load_state(self) -> Optional[BoundaryState]:
        """Load boundary state from disk."""
        try:
            if self.state_file.exists():
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Convert string dates back to datetime
                data["start_time"] = datetime.fromisoformat(data["start_time"])
                data["last_activity"] = datetime.fromisoformat(data["last_activity"])
                data["state"] = ContinuityState(data["state"])

                # Create boundary state object
                state = BoundaryState(**data)

                # Load regex violations from separate file
                violations_file = self.state_file.with_suffix(".violations.json")
                if violations_file.exists():
                    with open(violations_file, "r", encoding="utf-8") as f:
                        violations_data = json.load(f)
                    # Note: Would need proper deserialization for RegexViolation objects
                    # For now, store as dicts
                    state.regex_violations = violations_data

                return state
        except Exception as e:
            print(f"Warning: Failed to load session state: {e}")
            return None

    def _save_state(self):
        """Save boundary state to disk."""
        with self._lock:
            try:
                # Save main state
                state_dict = self.boundary_state.to_dict()
                with open(self.state_file, "w", encoding="utf-8") as f:
                    json.dump(state_dict, f, indent=2, default=str)

                # Save regex violations separately
                violations_file = self.state_file.with_suffix(".violations.json")
                violations_data = [
                    v.to_dict() for v in self.boundary_state.regex_violations
                ]
                with open(violations_file, "w", encoding="utf-8") as f:
                    json.dump(violations_data, f, indent=2, default=str)

                # Also save to recovery directory for crash recovery
                recovery_file = (
                    self.recovery_dir
                    / f"state_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                with open(recovery_file, "w", encoding="utf-8") as f:
                    json.dump(state_dict, f, indent=2, default=str)

            except Exception as e:
                print(f"Warning: Failed to save session state: {e}")

    def _load_crash_history(self):
        """Load crash history from disk."""
        try:
            crash_files = list(self.crash_log_dir.glob("crash_*.json"))
            for crash_file in sorted(crash_files)[-100:]:  # Load last 100 crashes
                with open(crash_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Convert string date back to datetime
                data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                data["cause"] = CrashCause(data["cause"])

                crash = SessionCrash(**data)
                self.crash_history.append(crash)
        except Exception as e:
            print(f"Warning: Failed to load crash history: {e}")

    def _start_auto_save(self):
        """Start auto-save timer."""

        def auto_save():
            self._save_state()
            # Reschedule
            self._auto_save_timer = threading.Timer(
                30.0, auto_save
            )  # Save every 30 seconds
            self._auto_save_timer.daemon = True
            self._auto_save_timer.start()

        self._auto_save_timer = threading.Timer(30.0, auto_save)
        self._auto_save_timer.daemon = True
        self._auto_save_timer.start()

    def _initialize_bans_from_history(self):
        """Initialize ban lists from crash history."""
        with self._lock:
            # Analyze recent crashes for patterns to ban
            recent_crashes = [
                c
                for c in self.crash_history
                if (datetime.now() - c.timestamp).total_seconds() < 3600
            ]  # Last hour

            for crash in recent_crashes:
                if crash.cause == CrashCause.REGEX_COMBINATORIAL_EXPLOSION:
                    if crash.offending_pattern:
                        # Add pattern to active bans
                        pattern_hash = hash(crash.offending_pattern) & 0xFFFFFFFF
                        ban_key = f"regex_pattern_{pattern_hash:08x}"

                        if ban_key not in self.boundary_state.active_bans:
                            self.boundary_state.active_bans[ban_key] = {
                                "type": "regex_pattern",
                                "pattern": crash.offending_pattern,
                                "banned_since": crash.timestamp.isoformat(),
                                "crash_count": 1,
                                "last_crash": crash.timestamp.isoformat(),
                                "severity": "critical",
                            }
                        else:
                            # Update existing ban
                            ban = self.boundary_state.active_bans[ban_key]
                            ban["crash_count"] += 1
                            ban["last_crash"] = crash.timestamp.isoformat()

            # Update continuity score based on crash history
            self._update_continuity_score()

    def _update_continuity_score(self):
        """Update continuity score based on recent activity."""
        with self._lock:
            # Base score starts at 1.0
            score = 1.0

            # Deduct for recent crashes
            recent_crashes = [
                c
                for c in self.crash_history
                if (datetime.now() - c.timestamp).total_seconds() < 300
            ]  # Last 5 minutes
            score -= len(recent_crashes) * 0.3

            # Deduct for high violation rate
            if self.boundary_state.total_edits > 0:
                violation_rate = (
                    self.boundary_state.violations_detected
                    / self.boundary_state.total_edits
                )
                if violation_rate > 0.1:  # More than 10% violations
                    score -= 0.2
                elif violation_rate > 0.05:  # More than 5% violations
                    score -= 0.1

            # Deduct for low fix application rate
            if self.boundary_state.violations_detected > 0:
                fix_rate = (
                    self.boundary_state.fixes_applied
                    / self.boundary_state.violations_detected
                )
                if fix_rate < 0.5:  # Less than 50% fixes applied
                    score -= 0.2
                elif fix_rate < 0.8:  # Less than 80% fixes applied
                    score -= 0.1

            # Clamp score to [0.0, 1.0]
            score = max(0.0, min(1.0, score))

            # Update state based on score
            if score >= 0.8:
                self.boundary_state.state = ContinuityState.HEALTHY
            elif score >= 0.6:
                self.boundary_state.state = ContinuityState.RECOVERING
            elif score >= 0.4:
                self.boundary_state.state = ContinuityState.DEGRADED
            elif score >= 0.2:
                self.boundary_state.state = ContinuityState.CRITICAL
            else:
                self.boundary_state.state = ContinuityState.LOST

            self.boundary_state.continuity_score = score

    def record_edit(self, file_path: str, edit_type: str):
        """Record an edit made by the AI."""
        with self._lock:
            self.boundary_state.total_edits += 1
            self.boundary_state.last_activity = datetime.now()
            self._update_continuity_score()

    def record_boundary_check(self, violations_detected: int = 0):
        """Record a boundary check operation."""
        with self._lock:
            self.boundary_state.boundary_checks += 1
            self.boundary_state.violations_detected += violations_detected
            self.boundary_state.last_activity = datetime.now()
            self._update_continuity_score()

    def record_fix_applied(self):
        """Record a fix application."""
        with self._lock:
            self.boundary_state.fixes_applied += 1
            self.boundary_state.last_activity = datetime.now()
            self._update_continuity_score()

    def record_regex_violation(self, violation: RegexViolation):
        """Record a regex boundary violation."""
        with self._lock:
            self.boundary_state.regex_violations.append(violation)

            # Add to active bans if critical
            if violation.severity == "critical" and violation.continuity_threat:
                pattern_hash = hash(violation.dangerous_pattern) & 0xFFFFFFFF
                ban_key = f"regex_pattern_{pattern_hash:08x}"

                if ban_key not in self.boundary_state.active_bans:
                    self.boundary_state.active_bans[ban_key] = {
                        "type": "regex_pattern",
                        "pattern": violation.dangerous_pattern,
                        "banned_since": datetime.now().isoformat(),
                        "violation_count": 1,
                        "last_violation": datetime.now().isoformat(),
                        "severity": violation.severity,
                        "risk_score": violation.risk_score,
                        "suggested_replacement": violation.suggested_replacement,
                    }
                else:
                    # Update existing ban
                    ban = self.boundary_state.active_bans[ban_key]
                    ban["violation_count"] += 1
                    ban["last_violation"] = datetime.now().isoformat()
                    ban["risk_score"] = max(
                        ban.get("risk_score", 0.0), violation.risk_score
                    )

            self.boundary_state.last_activity = datetime.now()
            self._update_continuity_score()

    def record_crash(self, cause: CrashCause, **kwargs) -> SessionCrash:
        """
        Record a session crash.

        Args:
            cause: Cause of the crash
            **kwargs: Additional crash information

        Returns:
            SessionCrash object representing the crash
        """
        with self._lock:
            crash = SessionCrash(
                crash_id=f"crash_{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now(),
                cause=cause,
                file_path=kwargs.get("file_path"),
                line_number=kwargs.get("line_number"),
                offending_pattern=kwargs.get("offending_pattern"),
                memory_usage_mb=kwargs.get("memory_usage_mb"),
                token_count=kwargs.get("token_count"),
                stack_trace=kwargs.get("stack_trace"),
            )

            self.crash_history.append(crash)
            self.boundary_state.crashes_experienced += 1

            # Save crash to disk
            crash_file = self.crash_log_dir / f"crash_{crash.crash_id}.json"
            with open(crash_file, "w", encoding="utf-8") as f:
                json.dump(crash.to_dict(), f, indent=2, default=str)

            # Update bans based on crash
            if (
                cause == CrashCause.REGEX_COMBINATORIAL_EXPLOSION
                and crash.offending_pattern
            ):
                pattern_hash = hash(crash.offending_pattern) & 0xFFFFFFFF
                ban_key = f"regex_pattern_{pattern_hash:08x}"

                if ban_key not in self.boundary_state.active_bans:
                    self.boundary_state.active_bans[ban_key] = {
                        "type": "regex_pattern",
                        "pattern": crash.offending_pattern,
                        "banned_since": crash.timestamp.isoformat(),
                        "crash_count": 1,
                        "last_crash": crash.timestamp.isoformat(),
                        "severity": "critical",
                    }
                else:
                    # Update existing ban
                    ban = self.boundary_state.active_bans[ban_key]
                    ban["crash_count"] += 1
                    ban["last_crash"] = crash.timestamp.isoformat()

            self.boundary_state.last_activity = datetime.now()
            self._update_continuity_score()
            self._save_state()

            return crash

    def get_continuity_report(self) -> Dict[str, Any]:
        """Get a continuity report."""
        with self._lock:
            recent_crashes = [
                c
                for c in self.crash_history
                if (datetime.now() - c.timestamp).total_seconds() < 3600
            ]

            return {
                "session_id": self.session_id,
                "state": self.boundary_state.state.value,
                "continuity_score": self.boundary_state.continuity_score,
                "total_edits": self.boundary_state.total_edits,
                "boundary_checks": self.boundary_state.boundary_checks,
                "violations_detected": self.boundary_state.violations_detected,
                "fixes_applied": self.boundary_state.fixes_applied,
                "crashes_experienced": self.boundary_state.crashes_experienced,
                "active_bans_count": len(self.boundary_state.active_bans),
                "recent_crashes": len(recent_crashes),
                "session_duration_hours": (
                    datetime.now() - self.boundary_state.start_time
                ).total_seconds()
                / 3600,
                "last_activity": self.boundary_state.last_activity.isoformat(),
            }

    def check_pattern_banned(
        self, pattern: str
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if a regex pattern is banned.

        Args:
            pattern: Regex pattern to check

        Returns:
            Tuple of (is_banned, ban_info)
        """
        with self._lock:
            pattern_hash = hash(pattern) & 0xFFFFFFFF
            ban_key = f"regex_pattern_{pattern_hash:08x}"

            if ban_key in self.boundary_state.active_bans:
                return True, self.boundary_state.active_bans[ban_key]

            # Also check for similar patterns
            for ban_key, ban_info in self.boundary_state.active_bans.items():
                if ban_info.get("type") == "regex_pattern":
                    banned_pattern = ban_info.get("pattern", "")
                    # Simple similarity check
                    if pattern in banned_pattern or banned_pattern in pattern:
                        return True, ban_info

            return False, None

    def should_block_edit(self, file_path: str, content: str) -> Tuple[bool, str]:
        """
        Determine if an edit should be blocked based on continuity state.

        Args:
            file_path: Path to file being edited
            content: Content being added/changed

        Returns:
            Tuple of (should_block, reason)
        """
        with self._lock:
            # Check continuity state
            if self.boundary_state.state == ContinuityState.LOST:
                return True, "Continuity lost - boundary enforcement unavailable"

            if self.boundary_state.state == ContinuityState.CRITICAL:
                return True, "Critical continuity state - manual intervention required"

            # Check for banned regex patterns in content
            regex_enforcer = RegexBoundaryEnforcer()
            violations = regex_enforcer.analyze_file(file_path, content)

            for violation in violations:
                if (
                    violation.severity in ["critical", "high"]
                    and violation.continuity_threat
                ):
                    is_banned, ban_info = self.check_pattern_banned(
                        violation.dangerous_pattern
                    )
                    if is_banned:
                        return (
                            True,
                            f"Banned regex pattern detected: {violation.dangerous_pattern}",
                        )

            # Check if we're in recovery mode and should be conservative
            if self.boundary_state.state == ContinuityState.RECOVERING:
                # Be more conservative during recovery
                if len(violations) > 0:
                    return True, "Recovery mode - blocking edits with violations"

            return False, ""

    def recover_from_crash(self, crash_id: str) -> bool:
        """
        Attempt to recover from a crash.

        Args:
            crash_id: ID of the crash to recover from

        Returns:
            True if recovery successful, False otherwise
        """
        with self._lock:
            # Find the crash
            crash = None
            for c in self.crash_history:
                if c.crash_id == crash_id:
                    crash = c
                    break

            if not crash:
                return False

            # Mark as recovery attempted
            crash.recovery_attempted = True

            # Recovery actions based on crash cause
            if crash.cause == CrashCause.REGEX_COMBINATORIAL_EXPLOSION:
                if crash.file_path and crash.offending_pattern:
                    # Try to fix the offending file
                    try:
                        file_path = Path(crash.file_path)
                        if file_path.exists():
                            content = file_path.read_text(encoding="utf-8")
                            fixed_content, fixes = self.regex_enforcer.apply_fixes(
                                str(file_path), content, auto_apply=True
                            )
                            if fixes:
                                file_path.write_text(fixed_content, encoding="utf-8")
                                crash.recovery_successful = True
                                return True
                    except Exception as e:
                        print(f"Recovery failed: {e}")

            # Update crash record
            crash_file = self.crash_log_dir / f"crash_{crash.crash_id}.json"
            if crash_file.exists():
                with open(crash_file, "w", encoding="utf-8") as f:
                    json.dump(crash.to_dict(), f, indent=2, default=str)

            return crash.recovery_successful

    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Clean up old session data."""
        with self._lock:
            # Clean up old crash logs
            for crash_file in self.crash_log_dir.glob("crash_*.json"):
                try:
                    stat = crash_file.stat()
                    age_hours = (time.time() - stat.st_mtime) / 3600
                    if age_hours > max_age_hours:
                        crash_file.unlink()
                except Exception:
                    pass

            # Clean up old recovery backups
            for backup_file in self.recovery_dir.glob("state_backup_*.json"):
                try:
                    stat = backup_file.stat()
                    age_hours = (time.time() - stat.st_mtime) / 3600
                    if age_hours > max_age_hours:
                        backup_file.unlink()
                except Exception:
                    pass

    def __del__(self):
        """Cleanup on destruction."""
        if self._auto_save_timer:
            self._auto_save_timer.cancel()
        self._save_state()
