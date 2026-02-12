"""
OE-AGENT PACKAGE
Governed Autonomous Engineer with Atomic Execution

Version: 3.0.0
Schema ID: OE-AGENT-PHASE3-3.0
Date: 2026-01-24

🎯 PURPOSE:
OE-Agent is a governed autonomous engineer that cannot lie, cannot leak,
cannot hallucinate authority, and cannot silently act.

🔒 PHASE 3 FEATURES:
- Atomic execution with XACT model (INTENT → COMMIT/ABORT)
- Policy gate with pre-INTENT decisions
- Linear hash-chained event logging
- Cryptographic proof of event sequence
- Phase 2 backward compatibility

📁 PACKAGE STRUCTURE:
oe-agent/
├── executor/          # Atomic execution engine
├── events/           # Hash-chained event logging
├── policy/           # Policy gate and constraints
└── tests/           # Comprehensive test suite
"""

__version__ = "3.0.0"
__schema_id__ = "OE-AGENT-PHASE3-3.0"
__author__ = "Orthogonal Engineering"
__date__ = "2026-01-24"

# Core components
from .events.event_sink import AtomicEventSink
from .executor.simple_executor import AtomicSimpleExecutor
from .policy.policy_gate import PolicyConstraint, PolicyDecision, PolicyGate

# Export public API
__all__ = [
    "AtomicSimpleExecutor",
    "AtomicEventSink",
    "PolicyGate",
    "PolicyDecision",
    "PolicyConstraint",
]

# Package metadata
PACKAGE_INFO = {
    "name": "oe-agent",
    "version": __version__,
    "schema_id": __schema_id__,
    "phase": 3,
    "features": [
        "atomic_execution",
        "policy_gate",
        "hash_chained_events",
        "xact_model",
        "backward_compatibility",
    ],
    "guarantees": [
        "no_ghost_actions",
        "no_narrative_repair",
        "replayable_truth",
        "cryptographic_proof",
    ],
}


def get_package_info():
    """Get package information."""
    return PACKAGE_INFO.copy()


def verify_installation():
    """Verify that all components are importable."""
    try:
        from .events.event_sink import AtomicEventSink
        from .executor.simple_executor import AtomicSimpleExecutor
        from .policy.policy_gate import PolicyGate

        return {
            "success": True,
            "components": {
                "AtomicSimpleExecutor": True,
                "AtomicEventSink": True,
                "PolicyGate": True,
            },
            "version": __version__,
            "phase": 3,
        }
    except ImportError as e:
        return {"success": False, "error": str(e), "version": __version__, "phase": 3}


# Initialize package
if __name__ == "__main__":
    info = verify_installation()
    if info["success"]:
        print(f"✅ OE-Agent Phase 3 ({__version__}) installed successfully")
        print(f"   Schema: {__schema_id__}")
        print(f"   Components: {len(info['components'])}")
    else:
        print(f"❌ Installation verification failed: {info['error']}")
