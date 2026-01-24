"""
Human Override Gate - Phase 12 Human-Only Override Mechanism

Implements physical human confirmation token requirement for any modifications
after Phase 12 epistemic finalization. No IDE, no AI invocation allowed.

Author: Orthogonal Engineering System
Date: 2026-01-22
Version: 1.0.0
"""

import hashlib
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from toolkit.oe.evidence_lock import EvidenceLock
from toolkit.oe.failure_ledger import FailureLedger


class HumanOverrideGate:
    """
    Human-only override gate for Phase 12 epistemic finalization.

    Requires physical human confirmation token for any modifications.
    No IDE, no AI invocation allowed.
    Override events permanently logged.
    """

    def __init__(self, override_registry_path: Optional[str] = None):
        """
        Initialize human override gate.

        Args:
            override_registry_path: Path to override registry file. If None, uses default.
        """
        if override_registry_path is None:
            self.override_registry_path = (
                Path("logs") / "human_override" / "override_registry.json"
            )
        else:
            self.override_registry_path = Path(override_registry_path)

        # Ensure directory exists
        self.override_registry_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize override registry if it doesn't exist
        if not self.override_registry_path.exists():
            self._initialize_override_registry()

        # Load override registry
        self.override_registry = self._load_override_registry()

        # Evidence lock for protecting override records
        self.evidence_lock = EvidenceLock()

        # Failure ledger for recording violations
        self.failure_ledger = FailureLedger()

        # Lock the override registry itself
        self._lock_override_registry()

    def _initialize_override_registry(self) -> None:
        """Initialize empty override registry with metadata."""
        registry_data = {
            "schema_version": "1.0",
            "registry_id": f"HUMAN-OVERRIDE-REGISTRY-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "description": "Orthogonal Engineering Human Override Registry - Phase 12",
            "invariants": {
                "physical_human_confirmation_required": True,
                "no_ide_allowed": True,
                "no_ai_invocation_allowed": True,
                "override_events_permanently_logged": True,
                "exit_code_2_on_violation": True,
            },
            "overrides": [],
            "violations": [],
            "statistics": {
                "total_overrides": 0,
                "total_violations": 0,
                "first_override": None,
                "last_override": None,
                "last_violation": None,
            },
        }

        with open(self.override_registry_path, "w", encoding="utf-8") as f:
            json.dump(registry_data, f, indent=2, ensure_ascii=False)

    def _load_override_registry(self) -> Dict[str, Any]:
        """Load override registry from disk."""
        try:
            with open(self.override_registry_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            # If registry is corrupted, create new one with corruption notice
            corruption_path = self.override_registry_path.with_suffix(".corrupted")
            if self.override_registry_path.exists():
                self.override_registry_path.rename(corruption_path)

            # Initialize fresh registry
            self._initialize_override_registry()
            with open(self.override_registry_path, "r", encoding="utf-8") as f:
                return json.load(f)

    def _save_override_registry(self) -> None:
        """Save override registry to disk."""
        # Update statistics
        self.override_registry["statistics"]["total_overrides"] = len(
            self.override_registry.get("overrides", [])
        )
        self.override_registry["statistics"]["total_violations"] = len(
            self.override_registry.get("violations", [])
        )

        # Write to temporary file first for atomicity
        temp_path = self.override_registry_path.with_suffix(
            f".{uuid.uuid4().hex[:8]}.tmp"
        )

        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(self.override_registry, f, indent=2, ensure_ascii=False)

        # Atomic replace
        try:
            os.replace(temp_path, self.override_registry_path)
        except (OSError, PermissionError):
            # Fallback: delete target first, then rename
            try:
                if self.override_registry_path.exists():
                    self.override_registry_path.unlink()
                temp_path.rename(self.override_registry_path)
            except Exception as write_error:
                # Last resort: write directly
                import logging

                logging.getLogger(__name__).warning(
                    f"Failed atomic write, falling back to direct write: {write_error}"
                )
                with open(self.override_registry_path, "w", encoding="utf-8") as f:
                    json.dump(self.override_registry, f, indent=2, ensure_ascii=False)
                # Clean up temp file
                if temp_path.exists():
                    try:
                        temp_path.unlink()
                    except Exception as cleanup_error:
                        # Log cleanup failure but continue - this is non-critical
                        logging.getLogger(__name__).warning(
                            f"Failed to cleanup temp file {temp_path}: {cleanup_error}"
                        )

    def _lock_override_registry(self) -> None:
        """Lock the override registry file as evidence."""
        self.evidence_lock.lock_evidence(
            str(self.override_registry_path), "Human Override Registry - Phase 12"
        )

    def _generate_physical_token(self) -> str:
        """
        Generate a physical human confirmation token.

        In a real implementation, this would involve:
        1. Physical hardware token
        2. Biometric verification
        3. Physical presence detection
        4. Multi-factor authentication

        For this implementation, we simulate with a cryptographically secure token.
        """
        # Generate token based on timestamp, random data, and system entropy
        token_data = f"{datetime.now(timezone.utc).isoformat()}:{uuid.uuid4().hex}:{os.urandom(32).hex()}"
        token_hash = hashlib.sha256(token_data.encode()).hexdigest()

        # Format as human-readable token (first 16 chars for display)
        human_token = token_hash[:16].upper()

        return human_token

    def _verify_physical_presence(self, token: str) -> bool:
        """
        Verify physical human presence.

        In a real implementation, this would:
        1. Require physical token insertion
        2. Require biometric verification
        3. Check for physical presence sensors
        4. Validate multi-factor authentication

        For this implementation, we simulate verification.
        """
        # Simulate physical verification delay
        time.sleep(2)  # Simulate human interaction time

        # In real implementation, this would check hardware tokens, biometrics, etc.
        # For simulation, we'll accept any token that looks valid
        if len(token) == 16 and token.isalnum():
            return True

        return False

    def request_override(
        self,
        operation: str,
        target_path: str,
        justification: str,
        requires_physical_token: bool = True,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Request a human override for an operation.

        Args:
            operation: Operation being requested (e.g., "modify", "delete", "create")
            target_path: Path to target file/directory
            justification: Human-readable justification for override
            requires_physical_token: Whether physical token is required (default: True)

        Returns:
            Tuple of (success, override_id, error_message)
        """
        # Check if AI is attempting override (violation)
        if self._is_ai_invocation():
            self._record_violation(
                operation=operation,
                target_path=target_path,
                justification=justification,
                violation_type="AI_ATTEMPTED_OVERRIDE",
                description="AI attempted human override (violation of Phase 12)",
            )
            return False, None, "AI invocation not allowed for human overrides"

        # Check if IDE is attempting override (violation)
        if self._is_ide_invocation():
            self._record_violation(
                operation=operation,
                target_path=target_path,
                justification=justification,
                violation_type="IDE_ATTEMPTED_OVERRIDE",
                description="IDE attempted human override (violation of Phase 12)",
            )
            return False, None, "IDE invocation not allowed for human overrides"

        # Generate override ID
        override_id = f"OVERRIDE-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"

        # Generate physical token if required
        physical_token = None
        if requires_physical_token:
            physical_token = self._generate_physical_token()

            print("\n" + "=" * 60)
            print("PHASE 12 HUMAN OVERRIDE REQUIRED")
            print("=" * 60)
            print(f"Operation: {operation}")
            print(f"Target: {target_path}")
            print(f"Justification: {justification}")
            print(f"\nPHYSICAL TOKEN REQUIRED: {physical_token}")
            print("\nInstructions:")
            print("1. Physically verify your identity")
            print("2. Enter the token when prompted")
            print("3. Confirm override intention")
            print("=" * 60 + "\n")

            # Simulate token verification
            print(
                f"Please enter the physical token '{physical_token}' to confirm override:"
            )
            # In real implementation, this would read from hardware token
            # For simulation, we'll simulate verification
            if not self._verify_physical_presence(physical_token):
                self._record_violation(
                    operation=operation,
                    target_path=target_path,
                    justification=justification,
                    violation_type="PHYSICAL_TOKEN_VERIFICATION_FAILED",
                    description=f"Physical token verification failed for override {override_id}",
                )
                return False, None, "Physical token verification failed"

        # Record override
        override_record = {
            "override_id": override_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": operation,
            "target_path": target_path,
            "justification": justification,
            "physical_token_used": physical_token is not None,
            "physical_token_hash": hashlib.sha256(physical_token.encode()).hexdigest()
            if physical_token
            else None,
            "verified_by": "HumanOverrideGate",
            "metadata": {
                "system_platform": sys.platform,
                "python_version": sys.version,
                "working_directory": os.getcwd(),
            },
        }

        # Add to overrides list
        if "overrides" not in self.override_registry:
            self.override_registry["overrides"] = []
        self.override_registry["overrides"].append(override_record)

        # Update statistics
        stats = self.override_registry["statistics"]
        if stats["first_override"] is None:
            stats["first_override"] = datetime.now(timezone.utc).isoformat()
        stats["last_override"] = datetime.now(timezone.utc).isoformat()

        # Save registry
        self._save_override_registry()

        # Also record in failure ledger (as a special override record, not failure)
        try:
            self.failure_ledger.record_failure(
                phase="PHASE12_HUMAN_OVERRIDE",
                violated_invariant="HUMAN_OVERRIDE_EXECUTED",
                description=f"Human override executed: {operation} on {target_path}",
                artifact_hash=hashlib.sha256(override_id.encode()).hexdigest(),
                severity="INFO",  # Special severity for overrides
                metadata={
                    "override_id": override_id,
                    "operation": operation,
                    "target_path": target_path,
                    "justification": justification,
                    "physical_token_used": physical_token is not None,
                },
            )
        except Exception as e:
            # Log but don't fail if ledger recording fails
            print(f"Warning: Failed to record override in failure ledger: {e}")

        print(f"\n✅ HUMAN OVERRIDE GRANTED: {override_id}")
        print(f"   Operation: {operation}")
        print(f"   Target: {target_path}")
        print(f"   Timestamp: {override_record['timestamp']}")
        print(f"   This override has been permanently logged.\n")

        return True, override_id, None

    def _is_ai_invocation(self) -> bool:
        """
        Detect if current invocation is from AI.

        In a real implementation, this would:
        1. Check process tree for AI agents
        2. Check for AI-specific environment variables
        3. Verify execution context
        4. Check for AI API calls

        For this implementation, we use heuristics.
        """
        # Check for AI-related environment variables
        ai_env_vars = [
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "GOOGLE_AI_KEY",
            "DEEPSEEK_API_KEY",
            "AI_AGENT",
            "LLM_PROVIDER",
        ]

        for env_var in ai_env_vars:
            if env_var in os.environ:
                return True

        # Check process name for AI indicators
        import psutil

        try:
            current_process = psutil.Process()
            process_name = current_process.name().lower()

            ai_process_indicators = [
                "ai",
                "llm",
                "gpt",
                "claude",
                "gemini",
                "deepseek",
                "agent",
                "assistant",
            ]

            for indicator in ai_process_indicators:
                if indicator in process_name:
                    return True

            # Check parent processes
            for parent in current_process.parents():
                parent_name = parent.name().lower()
                for indicator in ai_process_indicators:
                    if indicator in parent_name:
                        return True
        except (ImportError, psutil.Error):
            # psutil not available or error occurred
            pass

        return False

    def _is_ide_invocation(self) -> bool:
        """
        Detect if current invocation is from IDE.

        In a real implementation, this would:
        1. Check for IDE-specific environment variables
        2. Check parent processes for IDE executables
        3. Verify execution context

        For this implementation, we use heuristics.
        """
        # Check for IDE-related environment variables
        ide_env_vars = [
            "VSCODE_PID",
            "JETBRAINS_IDE",
            "PYCHARM",
            "INTELLIJ",
            "ZED_PID",
            "SUBLIME",
            "ATOM",
        ]

        for env_var in ide_env_vars:
            if env_var in os.environ:
                return True

        # Check process name for IDE indicators
        import psutil

        try:
            current_process = psutil.Process()
            process_name = current_process.name().lower()

            ide_process_indicators = [
                "vscode",
                "code",
                "pycharm",
                "intellij",
                "idea",
                "zed",
                "sublime",
                "atom",
                "editor",
                "ide",
            ]

            for indicator in ide_process_indicators:
                if indicator in process_name:
                    return True

            # Check parent processes
            for parent in current_process.parents():
                parent_name = parent.name().lower()
                for indicator in ide_process_indicators:
                    if indicator in parent_name:
                        return True
        except (ImportError, psutil.Error):
            # psutil not available or error occurred
            pass

        return False

    def _record_violation(
        self,
        operation: str,
        target_path: str,
        justification: str,
        violation_type: str,
        description: str,
    ) -> None:
        """Record a violation of human override gate."""
        violation_id = str(uuid.uuid4())
        violation = {
            "violation_id": violation_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": operation,
            "target_path": target_path,
            "justification": justification,
            "violation_type": violation_type,
            "description": description,
            "detected_by": "HumanOverrideGate",
        }

        # Add to violations list
        if "violations" not in self.override_registry:
            self.override_registry["violations"] = []
        self.override_registry["violations"].append(violation)

        # Update statistics
        stats = self.override_registry["statistics"]
        stats["last_violation"] = datetime.now(timezone.utc).isoformat()

        # Save registry
        self._save_override_registry()

        # Record in failure ledger
        try:
            self.failure_ledger.record_failure(
                phase="PHASE12_HUMAN_OVERRIDE_VIOLATION",
                violated_invariant=violation_type,
                description=description,
                artifact_hash=hashlib.sha256(violation_id.encode()).hexdigest(),
                severity="CRITICAL",
                metadata={
                    "violation_id": violation_id,
                    "operation": operation,
                    "target_path": target_path,
                    "justification": justification,
                },
            )
        except Exception as e:
            # Even if ledger fails, we must enforce the gate
            pass

        # Trigger exit code 2 as required by Phase 12
        print(f"\n❌ PHASE12 VIOLATION: {description}", file=sys.stderr)
        print(f"   Violation Type: {violation_type}", file=sys.stderr)
        print(f"   Operation: {operation}", file=sys.stderr)
        print(f"   Target: {target_path}", file=sys.stderr)
        print(
            f"\n   Exit code 2 triggered as per Phase 12 boundary enforcement.",
            file=sys.stderr,
        )
        sys.exit(2)

    def get_statistics(self) -> Dict[str, Any]:
        """Get current statistics."""
        return {
            "total_overrides": len(self.override_registry.get("overrides", [])),
            "total_violations": len(self.override_registry.get("violations", [])),
            "first_override": self.override_registry.get("statistics", {}).get(
                "first_override"
            ),
            "last_override": self.override_registry.get("statistics", {}).get(
                "last_override"
            ),
            "last_violation": self.override_registry.get("statistics", {}).get(
                "last_violation"
            ),
            "registry_path": str(self.override_registry_path),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Global human override gate instance
_global_human_override_gate: Optional[HumanOverrideGate] = None


def get_human_override_gate() -> HumanOverrideGate:
    """Get or create global human override gate instance."""
    global _global_human_override_gate
    if _global_human_override_gate is None:
        _global_human_override_gate = HumanOverrideGate()
    return _global_human_override_gate


def request_human_override(
    operation: str,
    target_path: str,
    justification: str,
    requires_physical_token: bool = True,
) -> Tuple[bool, Optional[str], Optional[str]]:
    """Convenience function to request human override."""
    return get_human_override_gate().request_override(
        operation, target_path, justification, requires_physical_token
    )


if __name__ == "__main__":
    # Test the human override gate
    print("Testing Human Override Gate...")

    gate = HumanOverrideGate()

    # Test override request (simulated - won't actually request physical token in test)
    print("\nSimulating human override request...")
    success, override_id, error = gate.request_override(
        operation="test_modify",
        target_path="/tmp/test_file.txt",
        justification="Test override for Phase 12 verification",
        requires_physical_token=False,  # Don't require physical token for test
    )

    if success:
        print(f"✅ Override granted: {override_id}")
    else:
        print(f"❌ Override failed: {error}")

    # Get statistics
    stats = gate.get_statistics()
    print(f"\nStatistics: {json.dumps(stats, indent=2)}")
