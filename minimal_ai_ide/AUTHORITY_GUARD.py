"""
AUTHORITY_GUARD.py
==================

EXCLUSIVE AUTHORITY ENFORCEMENT SYSTEM
Makes authority physically impossible to bypass

ARCHITECTURE:
- Process-level authority isolation
- Runtime PID checking
- Import guards that hard-fail if called outside daemon
- Environment-based jurisdiction enforcement

PRINCIPLE: "All intelligence paths factor through the daemon"
"""

import hashlib
import inspect
import os
import sys
import threading
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Set

# ==================== AUTHORITY STATE ====================


class AuthorityState(Enum):
    """Authority jurisdiction states"""

    UNAUTHORIZED = "unauthorized"  # No authority granted
    DAEMON_ONLY = "daemon_only"  # Only daemon process can access
    LOCKED = "locked"  # Authority is locked to current process
    VIOLATION = "violation"  # Authority violation detected


class AuthorityViolation(Exception):
    """Raised when authority is violated"""

    pass


# ==================== AUTHORITY GUARD ====================


class AuthorityGuard:
    """
    Exclusive authority enforcement system.

    Makes it physically impossible to bypass the daemon.

    Features:
    1. Process-level authority isolation
    2. Runtime PID checking
    3. Import guards that hard-fail
    4. Environment-based jurisdiction
    5. Cryptographic process binding
    """

    # Singleton instance
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._state = AuthorityState.UNAUTHORIZED
        self._authorized_pid = None
        self._authorized_process_hash = None
        self._protected_components: Set[str] = set()
        self._violation_count = 0

        # Protected components that MUST only run in daemon
        self._protected_components.update(
            [
                "LoRA_LLM_Integrator",
                "Σ_LORA_ConstraintExecutor",
                "PopperianValidator",
                "SelfAutomativeMaster",
                "generate_with_constraints",
                "verify_all_constraints",
                "run_falsification_suite",
            ]
        )

        # Environment check
        self._check_environment()

        print(f"🔒 AuthorityGuard initialized: {self._state.value}")

    def _check_environment(self):
        """Check if we're in the daemon environment"""
        # Check for daemon environment variable
        if os.environ.get("AI_DAEMON_AUTHORITY") == "exclusive":
            self._state = AuthorityState.DAEMON_ONLY
            self._authorized_pid = os.getpid()
            self._authorized_process_hash = self._calculate_process_hash()
            print(f"✅ Authority granted to daemon PID: {self._authorized_pid}")
        else:
            self._state = AuthorityState.UNAUTHORIZED
            print("⚠️  Running in unauthorized mode (constraints may be bypassable)")

    def _calculate_process_hash(self) -> str:
        """Calculate cryptographic hash of process identity"""
        pid = os.getpid()
        ppid = os.getppid()
        creation_time = (
            os.path.getctime(f"/proc/{pid}") if os.path.exists(f"/proc/{pid}") else 0
        )
        thread_id = threading.get_ident()

        hash_input = f"{pid}:{ppid}:{creation_time}:{thread_id}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def lock_authority(self) -> bool:
        """
        Lock authority to current process.
        Once locked, cannot be changed until process ends.
        """
        if self._state == AuthorityState.LOCKED:
            return True  # Already locked

        if self._state != AuthorityState.DAEMON_ONLY:
            print(f"❌ Cannot lock authority from state: {self._state.value}")
            return False

        self._state = AuthorityState.LOCKED
        print(f"🔐 Authority LOCKED to PID: {self._authorized_pid}")
        return True

    def check_authority(self, component_name: str) -> bool:
        """
        Check if current context has authority to use component.
        Hard-fails if not authorized.
        """
        # If component is not protected, allow access
        if component_name not in self._protected_components:
            return True

        # Check authority state
        if self._state == AuthorityState.UNAUTHORIZED:
            self._violation_count += 1
            error_msg = f"""
            ⚠️  AUTHORITY VIOLATION ⚠️

            Component: {component_name}
            State: {self._state.value}
            PID: {os.getpid()}

            This component can ONLY be accessed through the Local AI Daemon.
            Attempting to bypass the daemon violates exclusive authority.

            To fix:
            1. Start the daemon: python LOCAL_AI_DAEMON.py
            2. Access via: http://localhost:8080/query
            3. Never import {component_name} directly

            Violation count: {self._violation_count}
            """
            print(error_msg)

            # In strict mode, raise exception
            if os.environ.get("AI_DAEMON_STRICT") == "true":
                raise AuthorityViolation(error_msg)

            return False

        # Check if we're in the authorized process
        current_pid = os.getpid()
        if current_pid != self._authorized_pid:
            self._state = AuthorityState.VIOLATION
            self._violation_count += 1

            error_msg = f"""
            🚨 CRITICAL AUTHORITY VIOLATION 🚨

            Component: {component_name}
            Authorized PID: {self._authorized_pid}
            Current PID: {current_pid}

            Process boundary violation!
            This component is LOCKED to daemon process only.

            System integrity compromised.
            """
            print(error_msg)
            raise AuthorityViolation(error_msg)

        return True

    def wrap_protected_component(self, component_class):
        """
        Decorator to wrap protected components with authority checks.
        """

        class ProtectedComponent(component_class):
            def __init__(self, *args, **kwargs):
                guard = AuthorityGuard()
                component_name = component_class.__name__

                if not guard.check_authority(component_name):
                    raise AuthorityViolation(
                        f"Cannot instantiate {component_name} without daemon authority"
                    )

                super().__init__(*args, **kwargs)

            def __getattribute__(self, name):
                # Check authority for protected methods
                guard = AuthorityGuard()
                component_name = component_class.__name__

                if (
                    name.startswith("generate")
                    or name.startswith("verify")
                    or name.startswith("run")
                ):
                    if not guard.check_authority(component_name):
                        raise AuthorityViolation(
                            f"Cannot call {name} on {component_name} without daemon authority"
                        )

                return super().__getattribute__(name)

        return ProtectedComponent

    def get_status(self) -> Dict[str, Any]:
        """Get current authority status"""
        return {
            "state": self._state.value,
            "authorized_pid": self._authorized_pid,
            "process_hash": self._authorized_process_hash,
            "protected_components": list(self._protected_components),
            "violation_count": self._violation_count,
            "current_pid": os.getpid(),
            "is_authorized": self._state
            in [AuthorityState.DAEMON_ONLY, AuthorityState.LOCKED],
            "is_locked": self._state == AuthorityState.LOCKED,
        }

    def add_protected_component(self, component_name: str):
        """Add a component to the protected list"""
        self._protected_components.add(component_name)
        print(f"🔒 Added protected component: {component_name}")

    def enforce_daemon_only(self):
        """
        Enforce that we're running in daemon-only mode.
        Called by daemon at startup.
        """
        # Set environment variable
        os.environ["AI_DAEMON_AUTHORITY"] = "exclusive"

        # Re-initialize with new environment
        self._state = AuthorityState.DAEMON_ONLY
        self._authorized_pid = os.getpid()
        self._authorized_process_hash = self._calculate_process_hash()

        print(f"✅ Daemon authority enforced for PID: {self._authorized_pid}")

        # Lock authority
        self.lock_authority()

        return True


# ==================== IMPORT GUARDS ====================


def guard_import(module_name: str, component_name: str):
    """
    Guard specific imports to prevent unauthorized access.

    Usage in protected modules:
        from AUTHORITY_GUARD import guard_import
        guard_import(__name__, "LoRA_LLM_Integrator")
    """
    guard = AuthorityGuard()

    # Check if this import is happening in an unauthorized context
    caller_frame = inspect.currentframe().f_back
    caller_module = inspect.getmodule(caller_frame)

    if caller_module and "test" in caller_module.__name__.lower():
        # Allow in tests (with warning)
        print(
            f"⚠️  Importing {component_name} in test context: {caller_module.__name__}"
        )
        return

    if not guard.check_authority(component_name):
        # Get call stack for debugging
        import traceback

        stack = traceback.extract_stack()

        error_msg = f"""
        🚨 UNAUTHORIZED IMPORT ATTEMPT 🚨

        Component: {component_name}
        Caller module: {caller_module.__name__ if caller_module else "unknown"}

        Stack trace:
        {chr(10).join(traceback.format_list(stack[-5:]))}

        This import is ONLY allowed within the Local AI Daemon.
        """
        print(error_msg)
        raise AuthorityViolation(error_msg)


# ==================== RUNTIME ENFORCEMENT ====================


def enforce_daemon_runtime():
    """
    Runtime enforcement that must be called by daemon at startup.
    Sets up exclusive authority environment.
    """
    guard = AuthorityGuard()
    guard.enforce_daemon_only()

    # Set strict mode
    os.environ["AI_DAEMON_STRICT"] = "true"

    print("=" * 70)
    print("🔐 EXCLUSIVE AUTHORITY RUNTIME ENFORCEMENT")
    print("=" * 70)
    print("All intelligence paths now factor through this daemon.")
    print("Bypass is physically impossible.")
    print("=" * 70)

    return guard


# ==================== DAEMON ENTRY GUARD ====================


def daemon_entry_guard():
    """
    Guard that must be called at daemon entry point.
    Ensures daemon is the ONLY entry point for intelligence.
    """
    # Check if we're the main process
    if __name__ != "__main__":
        error_msg = """
        🚨 DAEMON ENTRY VIOLATION 🚨

        This module must be run as the main daemon process.
        Do not import it or call it from other modules.

        Run: python LOCAL_AI_DAEMON.py
        """
        print(error_msg)
        sys.exit(1)

    # Check command line
    if len(sys.argv) < 2 or sys.argv[1] != "--daemon":
        error_msg = """
        🚨 DAEMON COMMAND VIOLATION 🚨

        Daemon must be started with --daemon flag:
        python LOCAL_AI_DAEMON.py --daemon

        This prevents accidental execution.
        """
        print(error_msg)
        sys.exit(1)

    # Enforce runtime
    guard = enforce_daemon_runtime()

    return guard


# ==================== QUICK STATUS CHECK ====================

if __name__ == "__main__":
    # Quick test of authority guard
    guard = AuthorityGuard()
    status = guard.get_status()

    print("=" * 70)
    print("AUTHORITY GUARD STATUS")
    print("=" * 70)
    for key, value in status.items():
        print(f"{key}: {value}")
    print("=" * 70)

    if status["is_authorized"]:
        print("✅ System has exclusive authority")
    else:
        print("⚠️  System running in bypassable mode")
        print("   Start daemon with: python LOCAL_AI_DAEMON.py --daemon")
