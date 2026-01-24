"""
IDE-AI Integration Layer - Real-time Boundary Checking and Autofix

Provides spell-check-like functionality for AI-as-IDE workflow with:
- Real-time boundary violation detection during code editing
- Inline suggestions and fixes
- Continuous validation loop
- Session persistence for "continuity of body"
- Integration with existing boundary enforcement system

Author: Orthogonal Engineering System
Date: 2026-01-24
Version: 1.0.0
"""

import asyncio
import difflib
import json
import os
import sys
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from toolkit.oe.autofix_engine import AutofixEngine, BoundaryViolation, FixType
from toolkit.oe.boundary_enforcer import BoundaryViolation as BoundaryViolationException
from toolkit.oe.boundary_enforcer import glass_box_boundary
from toolkit.oe.evidence_store import EvidenceStore
from toolkit.oe.ide_behavior_accounting import IDEBehaviorAccounting


class IDEAIState(Enum):
    """State of the IDE-AI integration."""

    IDLE = "idle"
    MONITORING = "monitoring"
    ANALYZING = "analyzing"
    SUGGESTING = "suggesting"
    APPLYING_FIX = "applying_fix"
    VALIDATING = "validating"
    ERROR = "error"


class ViolationDisplayMode(Enum):
    """How violations should be displayed to the user."""

    INLINE = "inline"  # Show violations inline with code
    SIDEBAR = "sidebar"  # Show violations in sidebar
    POPUP = "popup"  # Show violations in popup
    NOTIFICATION = "notification"  # Show as notification
    LOG_ONLY = "log_only"  # Only log violations


@dataclass
class CodeEdit:
    """Represents a code edit made by the AI."""

    edit_id: str
    timestamp: datetime
    file_path: str
    line_start: int
    line_end: int
    content_before: str
    content_after: str
    edit_type: str  # "insert", "delete", "replace"
    author: str = "ai_agent"
    boundary_checked: bool = False
    violations_detected: List[BoundaryViolation] = field(default_factory=list)
    fixes_applied: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "edit_id": self.edit_id,
            "timestamp": self.timestamp.isoformat(),
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "edit_type": self.edit_type,
            "author": self.author,
            "boundary_checked": self.boundary_checked,
            "violations_detected": [v.to_dict() for v in self.violations_detected],
            "fixes_applied": self.fixes_applied,
            "content_diff": self.get_diff(),
        }

    def get_diff(self) -> str:
        """Get unified diff of the edit."""
        diff = difflib.unified_diff(
            self.content_before.splitlines(keepends=True),
            self.content_after.splitlines(keepends=True),
            fromfile=f"{self.file_path} (before)",
            tofile=f"{self.file_path} (after)",
            lineterm="",
        )
        return "".join(diff)


@dataclass
class IDEAIStats:
    """Statistics for IDE-AI integration."""

    total_edits: int = 0
    edits_with_violations: int = 0
    violations_detected: int = 0
    fixes_suggested: int = 0
    fixes_applied: int = 0
    validation_passes: int = 0
    validation_failures: int = 0
    average_response_time_ms: float = 0.0
    session_duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_edits": self.total_edits,
            "edits_with_violations": self.edits_with_violations,
            "violations_detected": self.violations_detected,
            "fixes_suggested": self.fixes_suggested,
            "fixes_applied": self.fixes_applied,
            "validation_passes": self.validation_passes,
            "validation_failures": self.validation_failures,
            "average_response_time_ms": self.average_response_time_ms,
            "session_duration_seconds": self.session_duration_seconds,
        }


class IDEAIListener:
    """Listener interface for IDE-AI events."""

    async def on_violation_detected(
        self, violation: BoundaryViolation, edit: CodeEdit
    ) -> None:
        """Called when a boundary violation is detected."""
        pass

    async def on_fix_suggested(
        self, fix: Dict[str, Any], violation: BoundaryViolation
    ) -> None:
        """Called when a fix is suggested for a violation."""
        pass

    async def on_fix_applied(
        self, fix: Dict[str, Any], edit: CodeEdit, success: bool
    ) -> None:
        """Called when a fix is applied."""
        pass

    async def on_validation_complete(
        self, edit: CodeEdit, passed: bool, violations: List[BoundaryViolation]
    ) -> None:
        """Called when validation is complete for an edit."""
        pass

    async def on_state_changed(
        self, old_state: IDEAIState, new_state: IDEAIState
    ) -> None:
        """Called when the IDE-AI state changes."""
        pass


class IDEAIIntegration:
    """
    IDE-AI Integration Layer for real-time boundary checking.

    Provides spell-check-like functionality for AI-as-IDE workflow:
    1. Monitors code edits in real-time
    2. Detects boundary violations immediately
    3. Suggests fixes inline (like spell-check suggestions)
    4. Applies fixes with user confirmation
    5. Maintains session continuity
    6. Integrates with existing boundary enforcement
    """

    def __init__(
        self,
        workspace_root: str,
        listener: Optional[IDEAIListener] = None,
        display_mode: ViolationDisplayMode = ViolationDisplayMode.INLINE,
        auto_suggest: bool = True,
        auto_apply_low_risk: bool = False,
        session_id: Optional[str] = None,
    ):
        """
        Initialize IDE-AI integration.

        Args:
            workspace_root: Root directory of the workspace
            listener: Optional listener for IDE-AI events
            display_mode: How violations should be displayed
            auto_suggest: Whether to automatically suggest fixes
            auto_apply_low_risk: Whether to automatically apply low-risk fixes
            session_id: Optional session ID for continuity
        """
        self.workspace_root = Path(workspace_root)
        self.listener = listener
        self.display_mode = display_mode
        self.auto_suggest = auto_suggest
        self.auto_apply_low_risk = auto_apply_low_risk

        # Initialize components
        self.autofix_engine = AutofixEngine()
        self.ide_accounting = IDEBehaviorAccounting()
        self.evidence_store = EvidenceStore()

        # State management
        self.state = IDEAIState.IDLE
        self.session_id = session_id or self._generate_session_id()
        self.stats = IDEAIStats()
        self.session_start_time = datetime.now()

        # Edit tracking
        self.pending_edits: List[CodeEdit] = []
        self.applied_edits: List[CodeEdit] = []
        self.active_violations: Dict[str, BoundaryViolation] = {}

        # File monitoring
        self.monitored_files: Set[str] = set()
        self.file_hashes: Dict[str, str] = {}

        # Threading
        self._monitoring_thread: Optional[threading.Thread] = None
        self._stop_monitoring = threading.Event()

        # Configuration
        self.config = {
            "check_on_save": True,
            "check_on_edit": True,
            "max_file_size_mb": 10,
            "excluded_patterns": [".git", "__pycache__", ".venv", "node_modules"],
            "response_timeout_seconds": 5,
            "max_violations_per_file": 100,
            "continuity_enabled": True,
        }

        # Initialize session
        self._initialize_session()

    def _generate_session_id(self) -> str:
        """Generate unique session ID for continuity."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_part = str(uuid.uuid4())[:8]
        return f"IDE_AI_SESSION_{timestamp}_{random_part}"

    def _initialize_session(self) -> None:
        """Initialize IDE-AI session for continuity."""
        session_dir = self.workspace_root / ".ide_ai_sessions"
        session_dir.mkdir(exist_ok=True)

        self.session_file = session_dir / f"{self.session_id}.json"

        # Load previous session if exists and continuity is enabled
        if self.config["continuity_enabled"] and self.session_file.exists():
            try:
                with open(self.session_file, "r") as f:
                    session_data = json.load(f)
                self._load_session_data(session_data)
                print(f"Loaded previous session: {self.session_id}")
            except Exception as e:
                print(f"Failed to load session: {e}")

        # Save initial session state
        self._save_session()

    def _load_session_data(self, session_data: Dict[str, Any]) -> None:
        """Load session data from previous session."""
        # Load stats
        stats_data = session_data.get("stats", {})
        self.stats = IDEAIStats(**stats_data)

        # Load active violations
        violations_data = session_data.get("active_violations", {})
        for vid, vdata in violations_data.items():
            # Reconstruct violation objects (simplified)
            self.active_violations[vid] = BoundaryViolation(
                violation_id=vid,
                violation_type=vdata["violation_type"],
                severity=vdata["severity"],
                location=tuple(vdata["location"]),
                description=vdata["description"],
                code_snippet=vdata["code_snippet"],
                suggested_fixes=vdata["suggested_fixes"],
            )

        print(
            f"Loaded {len(self.active_violations)} active violations from previous session"
        )

    def _save_session(self) -> None:
        """Save current session state for continuity."""
        session_data = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "workspace_root": str(self.workspace_root),
            "state": self.state.value,
            "stats": self.stats.to_dict(),
            "active_violations": {
                vid: v.to_dict() for vid, v in self.active_violations.items()
            },
            "config": self.config,
            "monitored_files": list(self.monitored_files),
        }

        try:
            with open(self.session_file, "w") as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save session: {e}")

    def _change_state(self, new_state: IDEAIState) -> None:
        """Change IDE-AI state and notify listener."""
        old_state = self.state
        self.state = new_state

        if self.listener:
            asyncio.create_task(self.listener.on_state_changed(old_state, new_state))

    def start_monitoring(self) -> None:
        """Start monitoring workspace for changes."""
        if self.state != IDEAIState.IDLE:
            raise RuntimeError(f"Cannot start monitoring from state: {self.state}")

        self._change_state(IDEAIState.MONITORING)

        # Start monitoring thread
        self._stop_monitoring.clear()
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self._monitoring_thread.start()

        print(f"Started IDE-AI monitoring for session: {self.session_id}")

    def stop_monitoring(self) -> None:
        """Stop monitoring workspace."""
        self._stop_monitoring.set()
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)

        self._change_state(IDEAIState.IDLE)
        self._save_session()  # Final save

        print(f"Stopped IDE-AI monitoring for session: {self.session_id}")

    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while not self._stop_monitoring.is_set():
            try:
                # Check for file changes
                self._check_file_changes()

                # Process pending edits
                self._process_pending_edits()

                # Save session periodically
                if time.time() % 30 < 1:  # Every ~30 seconds
                    self._save_session()

                time.sleep(0.5)  # Check every 500ms

            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                self._change_state(IDEAIState.ERROR)
                time.sleep(5)  # Wait before retry

    def _check_file_changes(self) -> None:
        """Check for file changes in monitored files."""
        for file_path in list(self.monitored_files):
            if not Path(file_path).exists():
                self.monitored_files.remove(file_path)
                continue

            current_hash = self._hash_file(file_path)
            if (
                file_path in self.file_hashes
                and self.file_hashes[file_path] != current_hash
            ):
                # File changed
                self._on_file_changed(file_path, current_hash)

            self.file_hashes[file_path] = current_hash

    def _hash_file(self, file_path: str) -> str:
        """Calculate hash of a file."""
        try:
            with open(file_path, "rb") as f:
                return str(hash(f.read()))
        except:
            return "error"

    def _on_file_changed(self, file_path: str, new_hash: str) -> None:
        """Handle file change event."""
        if not self.config["check_on_edit"]:
            return

        # Read file content
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except:
            return

        # Create edit object
        edit = CodeEdit(
            edit_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            file_path=file_path,
            line_start=1,
            line_end=len(content.splitlines()),
            content_before="",  # We don't have before content in monitoring mode
            content_after=content,
            edit_type="monitored_change",
            author="unknown",
        )

        # Add to pending edits
        self.pending_edits.append(edit)

    def _process_pending_edits(self) -> None:
        """Process pending edits for boundary checking."""
        if not self.pending_edits:
            return

        self._change_state(IDEAIState.ANALYZING)

        while self.pending_edits:
            edit = self.pending_edits.pop(0)
            self._analyze_edit(edit)

        self._change_state(IDEAIState.MONITORING)

    def _analyze_edit(self, edit: CodeEdit) -> None:
        """Analyze an edit for boundary violations."""
        start_time = time.time()

        try:
            # Read file content
            with open(edit.file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Analyze for violations
            violations = self.autofix_engine.analyze_file(edit.file_path, content)
            edit.violations_detected = violations
            edit.boundary_checked = True

            # Update stats
            self.stats.total_edits += 1
            if violations:
                self.stats.edits_with_violations += 1
                self.stats.violations_detected += len(violations)

            # Store edit
            self.applied_edits.append(edit)

            # Handle violations
            if violations:
                self._handle_violations(violations, edit)

            # Validate the edit
            validation_passed = self._validate_edit(edit)

            # Update stats
            if validation_passed:
                self.stats.validation_passes += 1
            else:
                self.stats.validation_failures += 1

            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.stats.average_response_time_ms = (
                self.stats.average_response_time_ms * (self.stats.total_edits - 1)
                + response_time
            ) / self.stats.total_edits

            # Update session duration
            self.stats.session_duration_seconds = (
                datetime.now() - self.session_start_time
            ).total_seconds()

            # Notify listener
            if self.listener:
                asyncio.create_task(
                    self.listener.on_validation_complete(
                        edit, validation_passed, violations
                    )
                )

        except Exception as e:
            print(f"Error analyzing edit {edit.edit_id}: {e}")

    def _handle_violations(
        self, violations: List[BoundaryViolation], edit: CodeEdit
    ) -> None:
        """Handle detected violations."""
        for violation in violations:
            # Store violation
            self.active_violations[violation.violation_id] = violation

            # Notify listener
            if self.listener:
                asyncio.create_task(
                    self.listener.on_violation_detected(violation, edit)
                )

            # Auto-suggest fixes if enabled
            if self.auto_suggest and violation.suggested_fixes:
                self._suggest_fixes(violation)

    def _suggest_fixes(self, violation: BoundaryViolation) -> None:
        """Suggest fixes for a violation."""
        for fix in violation.suggested_fixes:
            self.stats.fixes_suggested += 1

            # Auto-apply low-risk fixes if enabled
