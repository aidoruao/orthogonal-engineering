"""
IDE Behavior Accounting - Phase 11 Autonomous Failure Accounting

Records IDE-originated actions as first-class events.
Each file creation/modification tagged with IDE agent identity, source blueprint hash,
and execution timestamp. Unattributed changes trigger automatic failure.

Author: Orthogonal Engineering System
Date: 2026-01-22
Version: 1.0.0
"""

import hashlib
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from toolkit.oe.evidence_store import EvidenceStore
from toolkit.oe.failure_ledger import FailureLedger


class IDEBehaviorAccounting:
    """
    Tracks IDE-originated actions as first-class events.

    Implements Phase 11 A4 requirements:
    - Record IDE-originated actions as first-class events
    - Each file creation/modification tagged with:
        * IDE agent identity
        * source blueprint hash
        * execution timestamp
    - Unattributed changes → automatic failure
    """

    def __init__(self, ledger: Optional[FailureLedger] = None):
        """
        Initialize IDE behavior accounting.

        Args:
            ledger: Failure ledger instance. If None, creates new one.
        """
        self.ledger = ledger or FailureLedger()
        self.evidence_store = EvidenceStore()

        # Directory for IDE action logs
        self.actions_dir = Path("logs") / "ide_actions"
        self.actions_dir.mkdir(parents=True, exist_ok=True)

        # Current IDE session
        self.session_id = self._generate_session_id()
        self.current_agent = None
        self.current_blueprint = None

        # Action tracking
        self.actions = []
        self.unattributed_changes = []

        # Configuration
        self.config = {
            "require_attribution": True,
            "validate_blueprint_hash": True,
            "enforce_timestamp_consistency": True,
            "auto_fail_on_unattributed": True,
            "exit_code_on_unattributed": 2,
            "store_all_actions": True,
            "max_action_age_seconds": 3600,  # 1 hour
        }

        # Initialize session
        self._initialize_session()

    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        random_part = str(uuid.uuid4())[:8]
        return f"IDE_SESSION_{timestamp}_{random_part}"

    def _initialize_session(self) -> None:
        """Initialize IDE session."""
        session_info = {
            "session_id": self.session_id,
            "start_time": datetime.utcnow().isoformat(),
            "pid": os.getpid(),
            "python_version": sys.version,
            "cwd": os.getcwd(),
            "config": self.config,
        }

        session_path = self.actions_dir / self.session_id
        session_path.mkdir(exist_ok=True)

        session_file = session_path / "session_info.json"
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session_info, f, indent=2, ensure_ascii=False)

    def set_agent(self, agent_id: str, agent_type: str = "ZED_IDE") -> None:
        """
        Set current IDE agent.

        Args:
            agent_id: Agent identifier (e.g., "Zed-AI-Assistant", "Human-Operator")
            agent_type: Type of agent (ZED_IDE, VSCODE, HUMAN, etc.)
        """
        self.current_agent = {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "set_time": datetime.utcnow().isoformat(),
        }

        # Record agent change as action
        self.record_action(
            action_type="AGENT_CHANGE",
            target="system",
            description=f"Agent changed to {agent_id} ({agent_type})",
            agent_id=agent_id,
            agent_type=agent_type,
        )

    def set_blueprint(
        self, blueprint_path: str, blueprint_hash: Optional[str] = None
    ) -> str:
        """
        Set current source blueprint.

        Args:
            blueprint_path: Path to blueprint file
            blueprint_hash: SHA256 hash of blueprint. If None, calculated automatically.

        Returns:
            Blueprint hash
        """
        blueprint_file = Path(blueprint_path)

        if not blueprint_file.exists():
            raise FileNotFoundError(f"Blueprint not found: {blueprint_path}")

        # Calculate hash if not provided
        if blueprint_hash is None:
            blueprint_hash = self._calculate_file_hash(blueprint_file)

        self.current_blueprint = {
            "path": str(blueprint_file),
            "hash": blueprint_hash,
            "size": blueprint_file.stat().st_size,
            "set_time": datetime.utcnow().isoformat(),
        }

        # Record blueprint change as action
        self.record_action(
            action_type="BLUEPRINT_CHANGE",
            target=str(blueprint_file),
            description=f"Blueprint set to {blueprint_file.name}",
            blueprint_hash=blueprint_hash,
        )

        return blueprint_hash

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def record_action(
        self,
        action_type: str,
        target: str,
        description: str,
        agent_id: Optional[str] = None,
        agent_type: Optional[str] = None,
        blueprint_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Record an IDE-originated action.

        Args:
            action_type: Type of action (FILE_CREATE, FILE_MODIFY, AGENT_CHANGE, etc.)
            target: Target of action (file path, system component, etc.)
            description: Human-readable description
            agent_id: Agent identifier. If None, uses current agent.
            agent_type: Agent type. If None, uses current agent type.
            blueprint_hash: Source blueprint hash. If None, uses current blueprint.
            metadata: Additional metadata about the action

        Returns:
            Action ID
        """
        # Validate attribution
        if self.config["require_attribution"]:
            if agent_id is None and self.current_agent is None:
                self._handle_unattributed_action(
                    action_type, target, description, "No agent set"
                )
                return ""

        # Use current values if not specified
        if agent_id is None and self.current_agent:
            agent_id = self.current_agent["agent_id"]
            agent_type = self.current_agent["agent_type"]

        if blueprint_hash is None and self.current_blueprint:
            blueprint_hash = self.current_blueprint["hash"]

        # Generate action ID
        action_id = f"{self.session_id}_{action_type}_{len(self.actions)}"

        # Create action record
        action_record = {
            "action_id": action_id,
            "session_id": self.session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "action_type": action_type,
            "target": target,
            "description": description,
            "agent": {
                "agent_id": agent_id,
                "agent_type": agent_type,
            }
            if agent_id
            else None,
            "blueprint": {
                "hash": blueprint_hash,
                "path": self.current_blueprint["path"]
                if self.current_blueprint
                else None,
            }
            if blueprint_hash
            else None,
            "metadata": metadata or {},
        }

        # Validate blueprint hash if required
        if self.config["validate_blueprint_hash"] and blueprint_hash:
            if not self._validate_blueprint_hash(blueprint_hash):
                self._handle_invalid_blueprint(action_record)
                return action_id

        # Add to actions
        self.actions.append(action_record)

        # Save action to file
        self._save_action(action_record)

        # Record in evidence store
        self._record_in_evidence_store(action_record)

        return action_id

    def _validate_blueprint_hash(self, blueprint_hash: str) -> bool:
        """
        Validate blueprint hash.

        Args:
            blueprint_hash: Hash to validate

        Returns:
            True if valid, False otherwise
        """
        if not self.current_blueprint:
            return False

        # Check if hash matches current blueprint
        if blueprint_hash != self.current_blueprint["hash"]:
            # Check if it's a known historical blueprint
            return self._is_historical_blueprint(blueprint_hash)

        return True

    def _is_historical_blueprint(self, blueprint_hash: str) -> bool:
        """
        Check if hash corresponds to a known historical blueprint.

        Args:
            blueprint_hash: Hash to check

        Returns:
            True if known historical blueprint
        """
        # This would typically check a registry of known blueprints
        # For now, we'll check if it's a Phase 8 or Phase 9 blueprint
        known_blueprints = [
            # Phase 8 blueprint (example)
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            # Phase 9 blueprint (example)
            "b70e8c527b94f0a172caf100b44fbd9be1271f565365d52dd49df4b9a30ffd7c",
        ]

        return blueprint_hash in known_blueprints

    def _handle_unattributed_action(
        self, action_type: str, target: str, description: str, reason: str
    ) -> None:
        """
        Handle unattributed action.

        Args:
            action_type: Type of action
            target: Action target
            description: Action description
            reason: Reason why action is unattributed
        """
        unattributed_record = {
            "action_type": action_type,
            "target": target,
            "description": description,
            "timestamp": datetime.utcnow().isoformat(),
            "reason": reason,
            "session_id": self.session_id,
        }

        self.unattributed_changes.append(unattributed_record)

        # Record as failure
        failure_id = self.ledger.record_failure(
            phase="IDE_BEHAVIOR_ACCOUNTING",
            violated_invariant="UNATTRIBUTED_ACTION",
            description=f"Unattributed action: {action_type} on {target}",
            artifact_hash=self._hash_string(str(unattributed_record)),
            causal_parent_hash=None,
            severity="HIGH",
            metadata={
                "unattributed_record": unattributed_record,
                "reason": reason,
                "auto_detected": True,
            },
        )

        # Record in evidence store
        self.evidence_store.log_evidence(
            evidence_type="UNATTRIBUTED_ACTION",
            content={
                "failure_id": failure_id,
                "unattributed_record": unattributed_record,
                "reason": reason,
            },
            source="ide_behavior_accounting",
            metadata={
                "action_type": action_type,
                "target": target,
                "session_id": self.session_id,
                "confidence": 0.95,
                "tags": ["unattributed_action", "boundary_violation", "high"],
            },
        )

        # Enforce failure if configured
        if self.config["auto_fail_on_unattributed"]:
            self._enforce_failure_on_unattributed()

    def _handle_invalid_blueprint(self, action_record: Dict[str, Any]) -> None:
        """
        Handle action with invalid blueprint hash.

        Args:
            action_record: Action record with invalid blueprint
        """
        failure_id = self.ledger.record_failure(
            phase="IDE_BEHAVIOR_ACCOUNTING",
            violated_invariant="INVALID_BLUEPRINT",
            description=f"Action with invalid blueprint hash: {action_record['action_type']}",
            artifact_hash=self._hash_string(str(action_record)),
            causal_parent_hash=None,
            severity="CRITICAL",
            metadata={
                "action_record": action_record,
                "provided_hash": action_record.get("blueprint", {}).get("hash"),
                "expected_hash": self.current_blueprint["hash"]
                if self.current_blueprint
                else None,
                "auto_detected": True,
            },
        )

        # Record in evidence store
        self.evidence_store.log_evidence(
            evidence_type="INVALID_BLUEPRINT",
            content={
                "failure_id": failure_id,
                "action_record": action_record,
                "provided_hash": action_record.get("blueprint", {}).get("hash"),
                "expected_hash": self.current_blueprint["hash"]
                if self.current_blueprint
                else None,
            },
            source="ide_behavior_accounting",
            metadata={
                "action_type": action_record["action_type"],
                "target": action_record["target"],
                "session_id": self.session_id,
                "confidence": 0.99,
                "tags": ["invalid_blueprint", "boundary_violation", "critical"],
            },
        )

    def _enforce_failure_on_unattributed(self) -> None:
        """Enforce failure on unattributed action."""
        if self.config["exit_code_on_unattributed"] is not None:
            # Record enforcement action
            self.record_action(
                action_type="ENFORCEMENT",
                target="system",
                description=f"Exit code {self.config['exit_code_on_unattributed']} due to unattributed action",
                metadata={
                    "exit_code": self.config["exit_code_on_unattributed"],
                    "reason": "unattributed_action_detected",
                    "unattributed_count": len(self.unattributed_changes),
                },
            )

            # Actually exit
            sys.exit(self.config["exit_code_on_unattributed"])

    def _hash_string(self, text: str) -> str:
        """Calculate SHA256 hash of a string."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _save_action(self, action_record: Dict[str, Any]) -> None:
        """Save action to file."""
        session_path = self.actions_dir / self.session_id
        action_file = session_path / f"{action_record['action_id']}.json"

        with open(action_file, "w", encoding="utf-8") as f:
            json.dump(action_record, f, indent=2, ensure_ascii=False)

    def _record_in_evidence_store(self, action_record: Dict[str, Any]) -> None:
        """Record action in evidence store."""
        try:
            self.evidence_store.log_evidence(
                evidence_type="IDE_ACTION",
                content=action_record,
                source="ide_behavior_accounting",
                metadata={
                    "session_id": self.session_id,
                    "action_id": action_record["action_id"],
                    "has_blueprint": action_record.get("blueprint") is not None,
                    "has_agent": action_record.get("agent") is not None,
                    "confidence": 1.0,
                    "tags": [
                        "ide_action",
                        action_record["action_type"].lower(),
                        action_record.get("agent", {})
                        .get("agent_type", "unknown")
                        .lower(),
                    ],
                },
            )
        except Exception as e:
            # If evidence store fails, record that as a separate action
            self.record_action(
                action_type="EVIDENCE_STORE_ERROR",
                target="evidence_store",
                description=f"Failed to record action in evidence store: {str(e)}",
                metadata={
                    "original_action_id": action_record["action_id"],
                    "error": str(e),
                },
            )

    def record_file_creation(
        self, file_path: str, content_hash: Optional[str] = None
    ) -> str:
        """
        Record file creation action.

        Args:
            file_path: Path to created file
            content_hash: SHA256 hash of file content. If None, calculated automatically.

        Returns:
            Action ID
        """
        file_obj = Path(file_path)

        if not file_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Calculate hash if not provided
        if content_hash is None:
            content_hash = self._calculate_file_hash(file_obj)

        return self.record_action(
            action_type="FILE_CREATE",
            target=str(file_obj),
            description=f"Created file: {file_obj.name}",
            metadata={
                "file_size": file_obj.stat().st_size,
                "content_hash": content_hash,
                "file_path": str(file_obj),
                "absolute_path": str(file_obj.absolute()),
            },
        )

    def record_file_modification(
        self,
        file_path: str,
        old_hash: Optional[str] = None,
        new_hash: Optional[str] = None,
    ) -> str:
        """
        Record file modification action.

        Args:
            file_path: Path to modified file
            old_hash: SHA256 hash of file before modification (optional)
            new_hash: SHA256 hash of file after modification. If None, calculated automatically.

        Returns:
            Action ID
        """
        file_obj = Path(file_path)

        if not file_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Calculate new hash if not provided
        if new_hash is None:
            new_hash = self._calculate_file_hash(file_obj)

        return self.record_action(
            action_type="FILE_MODIFY",
            target=str(file_obj),
            description=f"Modified file: {file_obj.name}",
            metadata={
                "file_size": file_obj.stat().st_size,
                "old_content_hash": old_hash,
                "new_content_hash": new_hash,
                "file_path": str(file_obj),
                "absolute_path": str(file_obj.absolute()),
                "modification_detected": old_hash != new_hash if old_hash else True,
            },
        )

    def record_file_deletion(self, file_path: str) -> str:
        """
        Record file deletion action.

        Args:
            file_path: Path to deleted file

        Returns:
            Action ID
        """
        file_obj = Path(file_path)

        return self.record_action(
            action_type="FILE_DELETE",
            target=str(file_obj),
            description=f"Deleted file: {file_obj.name}",
            metadata={
                "file_path": str(file_obj),
                "absolute_path": str(file_obj.absolute())
                if file_obj.exists()
                else None,
                "existed_before": file_obj.exists(),
            },
        )

    def end_session(self) -> Dict[str, Any]:
        """
        End IDE session and return summary.

        Returns:
            Session summary
        """
        session_path = self.actions_dir / self.session_id

        # Save session summary
        summary = {
            "session_id": self.session_id,
            "start_time": self._get_session_start_time(),
            "end_time": datetime.utcnow().isoformat(),
            "total_actions": len(self.actions),
            "unattributed_actions": len(self.unattributed_changes),
            "agent_changes": len(
                [a for a in self.actions if a["action_type"] == "AGENT_CHANGE"]
            ),
            "blueprint_changes": len(
                [a for a in self.actions if a["action_type"] == "BLUEPRINT_CHANGE"]
            ),
            "file_operations": {
                "create": len(
                    [a for a in self.actions if a["action_type"] == "FILE_CREATE"]
                ),
                "modify": len(
                    [a for a in self.actions if a["action_type"] == "FILE_MODIFY"]
                ),
                "delete": len(
                    [a for a in self.actions if a["action_type"] == "FILE_DELETE"]
                ),
            },
            "actions_by_agent": self._count_actions_by_agent(),
            "unattributed_details": self.unattributed_changes,
            "config": self.config,
        }

        summary_file = session_path / "session_summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        # Reset session state
        self.actions = []
        self.unattributed_changes = []
        # Keep session_id for reference

        return summary

    def _get_session_start_time(self) -> Optional[str]:
        """Get session start time from session info file."""
        session_path = self.actions_dir / self.session_id
        session_file = session_path / "session_info.json"

        if session_file.exists():
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    session_info = json.load(f)
                    return session_info.get("start_time")
            except (json.JSONDecodeError, FileNotFoundError):
                pass

        return None

    def _count_actions_by_agent(self) -> Dict[str, int]:
        """Count actions by agent."""
        counts = {}
        for action in self.actions:
            agent_id = action.get("agent", {}).get("agent_id", "UNKNOWN")
            counts[agent_id] = counts.get(agent_id, 0) + 1
        return counts

    def get_session_statistics(self) -> Dict[str, Any]:
        """Get statistics for all sessions."""
        if not self.actions_dir.exists():
            return {"total_sessions": 0, "sessions": []}

        session_dirs = [d for d in self.actions_dir.iterdir() if d.is_dir()]
        statistics = {
            "total_sessions": len(session_dirs),
            "sessions": [],
            "total_actions": 0,
            "total_unattributed": 0,
            "agent_distribution": {},
        }

        for session_dir in session_dirs:
            summary_file = session_dir / "session_summary.json"
            if summary_file.exists():
                try:
                    with open(summary_file, "r", encoding="utf-8") as f:
                        summary = json.load(f)

                    statistics["sessions"].append(
                        {
                            "session_id": summary.get("session_id"),
                            "total_actions": summary.get("total_actions", 0),
                            "unattributed_actions": summary.get(
                                "unattributed_actions", 0
                            ),
                            "file_operations": summary.get("file_operations", {}),
                            "session_path": str(session_dir),
                        }
                    )

                    statistics["total_actions"] += summary.get("total_actions", 0)
                    statistics["total_unattributed"] += summary.get(
                        "unattributed_actions", 0
                    )

                    # Update agent distribution
                    for agent, count in summary.get("actions_by_agent", {}).items():
                        statistics["agent_distribution"][agent] = (
                            statistics["agent_distribution"].get(agent, 0) + count
                        )

                except (json.JSONDecodeError, FileNotFoundError):
                    # Skip corrupted sessions
                    continue

        return statistics


# Singleton instance for global access
_ide_behavior_accounting_instance = None


def get_ide_behavior_accounting() -> IDEBehaviorAccounting:
    """Get global IDE behavior accounting instance."""
    global _ide_behavior_accounting_instance
    if _ide_behavior_accounting_instance is None:
        _ide_behavior_accounting_instance = IDEBehaviorAccounting()
    return _ide_behavior_accounting_instance
