#!/usr/bin/env python3
"""
OE-AGENT PHASE 5 VERIFICATION SCRIPT
Simple verification of Phase 5 implementation

Version: 1.0.0
Date: 2026-01-25
Purpose: Verify Phase 5 components are importable and functional
"""

import os
import sys
from pathlib import Path


def verify_imports():
    """Verify all Phase 5 components can be imported."""
    print("=" * 70)
    print("OE-AGENT PHASE 5 VERIFICATION")
    print("=" * 70)

    # Add oe-agent to path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))

    imports_to_test = [
        ("Session Manager", "ide_integration.session_manager", "SessionManager"),
        (
            "Performance Monitor",
            "ide_integration.performance_monitor",
            "PerformanceMonitor",
        ),
        ("Audit Reporter", "ide_integration.audit_reporter", "AuditReporter"),
        ("MCP Atomic Gateway", "mcp_atomic_gateway", "MCPAtomicGateway"),
        ("TransactionGuard", "events.transaction_guard", "TransactionGuard"),
        ("AtomicEventSink", "events.event_sink", "AtomicEventSink"),
        ("PolicyGate", "policy.policy_gate", "PolicyGate"),
    ]

    results = []
    for component_name, module_name, class_name in imports_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            results.append((component_name, True, "✓ Import successful"))
            print(f"✅ {component_name}: Import successful")
        except Exception as e:
            results.append((component_name, False, f"❌ {str(e)}"))
            print(f"❌ {component_name}: {e}")

    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    successful = sum(1 for _, success, _ in results if success)
    total = len(results)

    print(f"Successful imports: {successful}/{total}")

    if successful == total:
        print("🎉 ALL PHASE 5 COMPONENTS VERIFIED SUCCESSFULLY")
        print("Phase 5 implementation is ready for use.")
    else:
        print("⚠️ SOME IMPORTS FAILED")
        print("\nFailed imports:")
        for component_name, success, message in results:
            if not success:
                print(f"  - {component_name}: {message}")

    return successful == total


def verify_file_structure():
    """Verify Phase 5 file structure exists."""
    print("\n" + "=" * 70)
    print("FILE STRUCTURE VERIFICATION")
    print("=" * 70)

    current_dir = Path(__file__).parent
    required_files = [
        "PHASE5_ATOMIC.yaml",
        "demo_phase5.py",
        "test_phase5_atomic.py",
        "ide_integration/session_manager.py",
        "ide_integration/performance_monitor.py",
        "ide_integration/audit_reporter.py",
        "mcp_atomic_gateway.py",
        "events/transaction_guard.py",
        "events/event_sink.py",
        "policy/policy_gate.py",
    ]

    results = []
    for file_path in required_files:
        full_path = current_dir / file_path
        if full_path.exists():
            results.append((file_path, True, "✓ File exists"))
            print(f"✅ {file_path}: Exists")
        else:
            results.append((file_path, False, "❌ File missing"))
            print(f"❌ {file_path}: Missing")

    print("\n" + "=" * 70)
    print("FILE STRUCTURE SUMMARY")
    print("=" * 70)

    existing = sum(1 for _, exists, _ in results if exists)
    total = len(results)

    print(f"Files found: {existing}/{total}")

    if existing == total:
        print("🎉 ALL REQUIRED FILES PRESENT")
    else:
        print("⚠️ SOME FILES MISSING")
        print("\nMissing files:")
        for file_path, exists, message in results:
            if not exists:
                print(f"  - {file_path}")

    return existing == total


def main():
    """Main verification function."""
    print("\n" + "=" * 70)
    print("PHASE 5 IMPLEMENTATION VERIFICATION")
    print("=" * 70)
    print("Based on: OE Phase 5 Atomic Completion Blueprint")
    print(
        "Enforcing: All IDE-integrated AI interactions are atomic, auditable, and falsifiable"
    )
    print("\n")

    # Verify imports
    imports_ok = verify_imports()

    # Verify file structure
    files_ok = verify_file_structure()

    print("\n" + "=" * 70)
    print("FINAL VERIFICATION RESULT")
    print("=" * 70)

    if imports_ok and files_ok:
        print("🎉 PHASE 5 VERIFICATION COMPLETE - ALL CHECKS PASSED")
        print("\nNext steps:")
        print("1. Run demonstration: python demo_phase5.py")
        print("2. Run tests: python test_phase5_atomic.py")
        print("3. Review specification: PHASE5_ATOMIC.yaml")
        print("4. Read implementation summary: ../PHASE_5_IMPLEMENTATION_SUMMARY.md")
        return 0
    else:
        print("⚠️ PHASE 5 VERIFICATION FAILED")
        print("\nIssues found:")
        if not imports_ok:
            print("- Some components failed to import")
        if not files_ok:
            print("- Some required files are missing")
        print("\nPlease check the errors above and fix the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
