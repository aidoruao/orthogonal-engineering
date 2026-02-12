"""
test_phase0_components.py
==========================

Simple test to verify Phase 0 components work correctly.

This test validates the core Phase 0 components without requiring
a running daemon. It tests:
1. ChristConstraintHandler - Falsification-based evaluation
2. LoggingProtocol - Standardized logging
3. Data models and patterns

Note: DaemonClient requires a running daemon, so it's tested separately.
"""

import json
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import Phase 0 components
try:
    from christ_constraint_handler import (
        ChristConstraintHandler,
        ChristConstraintResult,
        ConstraintDimension,
        ConstraintViolation,
        EvaluationContext,
        EvaluationMode,
    )
    from logging_protocol import (
        LogComponent,
        LoggingProtocol,
        LogLevel,
        StructuredLogEntry,
    )
    from logging_protocol import (
        OperationType as LogOperationType,
    )

    COMPONENTS_LOADED = True
except ImportError as e:
    print(f"❌ Failed to import Phase 0 components: {e}")
    COMPONENTS_LOADED = False


def test_christ_constraint_handler():
    """Test ChristConstraintHandler with various examples"""
    print("\n" + "=" * 70)
    print("TESTING CHRIST CONSTRAINT HANDLER")
    print("=" * 70)

    # Initialize handler
    handler = ChristConstraintHandler(
        audit_threshold=0.5,
        block_threshold=0.3,
        enable_context_awareness=True,
    )

    test_cases = [
        {
            "name": "Good philosophical response",
            "text": "Based on empirical evidence and current understanding, this hypothesis appears testable and falsifiable. However, further verification through peer review would be necessary.",
            "expected_mode": EvaluationMode.NORMAL,
            "expected_score_min": 0.7,
        },
        {
            "name": "Problematic response (should trigger audit)",
            "text": "This is absolutely certain and proven beyond doubt. There is no possibility of error.",
            "expected_mode": EvaluationMode.AUDIT_ONLY,
            "expected_score_max": 0.5,
        },
        {
            "name": "Severe violation (should be blocked)",
            "text": "I am omniscient and can solve all problems with perfect accuracy. My knowledge is complete and infallible.",
            "expected_mode": EvaluationMode.BLOCKED,
            "expected_score_max": 0.3,
        },
        {
            "name": "System operation (should be exempt)",
            "text": "System health check: All components operational",
            "expected_mode": EvaluationMode.EXEMPT,
        },
    ]

    all_passed = True

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print("-" * 40)

        # Create evaluation context
        context = EvaluationContext(
            text=test_case["text"],
            source_component="TestRunner",
            operation_type="test"
            if "System" not in test_case["name"]
            else "system_health_check",
            request_id=f"test_{i}",
        )

        # Evaluate constraint
        result = handler.evaluate(context)

        # Check results
        passed = True

        # Check mode
        if result.mode != test_case["expected_mode"]:
            print(
                f"  ❌ Mode mismatch: Expected {test_case['expected_mode'].value}, got {result.mode.value}"
            )
            passed = False
        else:
            print(f"  ✅ Mode correct: {result.mode.value}")

        # Check score ranges if specified
        if "expected_score_min" in test_case:
            if result.overall_score < test_case["expected_score_min"]:
                print(
                    f"  ❌ Score too low: Expected >= {test_case['expected_score_min']}, got {result.overall_score:.3f}"
                )
                passed = False
            else:
                print(
                    f"  ✅ Score acceptable: {result.overall_score:.3f} >= {test_case['expected_score_min']}"
                )

        if "expected_score_max" in test_case:
            if result.overall_score > test_case["expected_score_max"]:
                print(
                    f"  ❌ Score too high: Expected <= {test_case['expected_score_max']}, got {result.overall_score:.3f}"
                )
                passed = False
            else:
                print(
                    f"  ✅ Score acceptable: {result.overall_score:.3f} <= {test_case['expected_score_max']}"
                )

        # Show dimension scores
        print(f"  📊 Overall score: {result.overall_score:.3f}")
        for dim_score in result.dimension_scores:
            status = (
                "✅"
                if dim_score.score >= 0.7
                else "⚠️"
                if dim_score.score >= 0.5
                else "❌"
            )
            print(f"    {status} {dim_score.dimension.value}: {dim_score.score:.3f}")

        if result.violations:
            print(f"  ⚠️ Violations: {[v.value for v in result.violations]}")

        if not passed:
            all_passed = False

    # Test statistics
    print("\n" + "=" * 40)
    print("CHRIST CONSTRAINT STATISTICS")
    print("=" * 40)

    stats = handler.get_evaluation_statistics()
    print(f"Total evaluations: {stats['total_evaluations']}")
    print(f"Score mean: {stats['score_statistics']['mean']:.3f}")
    print(f"Mode distribution: {stats['mode_distribution']}")

    return all_passed


def test_logging_protocol():
    """Test LoggingProtocol with various log types"""
    print("\n" + "=" * 70)
    print("TESTING LOGGING PROTOCOL")
    print("=" * 70)

    # Initialize logger
    logger = LoggingProtocol(
        component=LogComponent.LORA_CHAT,
        enable_daemon_streaming=False,  # No daemon for test
        log_file="test_logging.log",
        log_level=LogLevel.DEBUG,
    )

    test_cases = [
        {
            "name": "System startup",
            "method": logger.log_system_start,
            "args": [],
        },
        {
            "name": "Inference start",
            "method": logger.log_inference_start,
            "args": ["test_request_001", "single_inference", 50],
        },
        {
            "name": "Inference complete",
            "method": logger.log_inference_complete,
            "args": ["test_request_001", 200, 0.75, 150.5],
        },
        {
            "name": "Validation pass",
            "method": logger.log_validation,
            "args": [
                "chat_inference",
                True,
                "test_request_001",
                "Validated successfully",
            ],
        },
        {
            "name": "Validation fail",
            "method": logger.log_validation,
            "args": ["chat_inference", False, "test_request_001", "Invalid parameters"],
        },
        {
            "name": "Constraint evaluation",
            "method": logger.log_constraint_evaluation,
            "args": ["christ_constraint", "PASS", 0.82, "test_request_001"],
        },
        {
            "name": "Christ constraint alert",
            "method": logger.log_christ_constraint_alert,
            "args": ["test_request_001", 0.42, 0.5],
        },
        {
            "name": "Performance metric",
            "method": logger.log_performance_metric,
            "args": ["inference_time", 125.5, "ms", "test_request_001"],
        },
    ]

    all_passed = True

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print("-" * 40)

        try:
            # Call logging method
            result = test_case["method"](*test_case["args"])

            # Verify result
            if isinstance(result, StructuredLogEntry):
                print(f"  ✅ Log entry created: {result.message[:50]}...")

                # Verify structure
                required_fields = [
                    "timestamp",
                    "level",
                    "component",
                    "operation",
                    "message",
                ]
                for field in required_fields:
                    if not hasattr(result, field) or getattr(result, field) is None:
                        print(f"  ❌ Missing field: {field}")
                        all_passed = False

                # Verify serialization
                try:
                    json_str = json.dumps(result.to_dict(), default=str)
                    print(f"  ✅ JSON serializable: {len(json_str)} bytes")
                except Exception as e:
                    print(f"  ❌ JSON serialization failed: {e}")
                    all_passed = False

            else:
                print(f"  ❌ Unexpected result type: {type(result)}")
                all_passed = False

        except Exception as e:
            print(f"  ❌ Logging method failed: {e}")
            all_passed = False

    # Test performance tracking
    print("\n" + "=" * 40)
    print("PERFORMANCE TRACKING TEST")
    print("=" * 40)

    try:
        # Start tracking
        logger.start_performance_tracking("test_operation", "perf_test_001")

        # Simulate work
        time.sleep(0.1)

        # End tracking
        elapsed = logger.end_performance_tracking(
            "test_operation", "perf_test_001", log_result=True
        )

        print(f"  ✅ Performance tracked: {elapsed:.1f}ms")

        # Get statistics
        stats = logger.get_performance_statistics("test_operation")
        print(f"  📊 Statistics: {stats}")

    except Exception as e:
        print(f"  ❌ Performance tracking failed: {e}")
        all_passed = False

    # Test audit trail
    print("\n" + "=" * 40)
    print("AUDIT TRAIL TEST")
    print("=" * 40)

    try:
        # Start audit trail
        logger.start_audit_trail("test_audit")

        # Add entries
        logger.add_audit_entry(
            "user_message", {"message": "Test message"}, "audit_test_001"
        )
        logger.add_audit_entry("validation", {"valid": True}, "audit_test_001")
        logger.add_audit_entry("inference", {"tokens": 150}, "audit_test_001")

        # Complete audit trail
        logger.complete_audit_trail("test_audit")

        # Get audit trail
        trail = logger.get_audit_trail()
        print(f"  ✅ Audit trail created: {len(trail)} entries")

        # Export audit trail
        export_success = logger.export_audit_trail("test_audit_trail.json")
        if export_success:
            print(f"  ✅ Audit trail exported to test_audit_trail.json")
        else:
            print(f"  ❌ Audit trail export failed")
            all_passed = False

    except Exception as e:
        print(f"  ❌ Audit trail failed: {e}")
        all_passed = False

    # Get logging statistics
    print("\n" + "=" * 40)
    print("LOGGING STATISTICS")
    print("=" * 40)

    stats = logger.get_log_statistics()
    print(f"Component: {stats['component']}")
    print(f"Log level: {stats['log_level']}")
    print(f"Daemon streaming: {stats['daemon_streaming_enabled']}")
    print(f"Audit trail size: {stats['audit_trail_size']}")

    return all_passed


def test_data_models():
    """Test data model serialization and validation"""
    print("\n" + "=" * 70)
    print("TESTING DATA MODELS")
    print("=" * 70)

    all_passed = True

    # Test StructuredLogEntry
    print("\n1. Testing StructuredLogEntry")
    print("-" * 40)

    try:
        entry = StructuredLogEntry(
            level=LogLevel.INFO,
            component=LogComponent.LORA_CHAT,
            operation=LogOperationType.INFERENCE,
            message="Test message",
            request_id="test_001",
            data={"key": "value"},
            performance_metrics={"time_ms": 150.5},
            constraint_scores={"christ": 0.75},
        )

        # Test to_dict
        entry_dict = entry.to_dict()
        required_keys = ["timestamp", "level", "component", "operation", "message"]
        for key in required_keys:
            if key not in entry_dict:
                print(f"  ❌ Missing key in dict: {key}")
                all_passed = False

        print(
            f"  ✅ StructuredLogEntry created: {entry_dict['component']}.{entry_dict['operation']}"
        )

        # Test to_log_string
        log_string = entry.to_log_string()
        if len(log_string) > 0:
            print(f"  ✅ Log string: {log_string[:80]}...")
        else:
            print(f"  ❌ Empty log string")
            all_passed = False

    except Exception as e:
        print(f"  ❌ StructuredLogEntry failed: {e}")
        all_passed = False

    # Test EvaluationContext
    print("\n2. Testing EvaluationContext")
    print("-" * 40)

    try:
        context = EvaluationContext(
            text="Test text for evaluation",
            source_component="TestRunner",
            operation_type="test",
            request_id="test_002",
            previous_responses=["Response 1", "Response 2"],
            system_state={"status": "testing"},
            user_context={"user_id": "test_user"},
        )

        # Verify fields
        if context.text != "Test text for evaluation":
            print(f"  ❌ Text mismatch")
            all_passed = False

        if len(context.previous_responses) != 2:
            print(f"  ❌ Previous responses mismatch")
            all_passed = False

        print(
            f"  ✅ EvaluationContext created: {context.source_component}.{context.operation_type}"
        )

    except Exception as e:
        print(f"  ❌ EvaluationContext failed: {e}")
        all_passed = False

    return all_passed


def main():
    """Main test function"""
    print("\n" + "=" * 70)
    print("PHASE 0 COMPONENTS TEST SUITE")
    print("=" * 70)
    print("Testing core Phase 0 components without daemon")
    print("=" * 70)

    if not COMPONENTS_LOADED:
        print("❌ Cannot run tests: Phase 0 components not loaded")
        print("\nPlease ensure these files are in the project root:")
        print("  • christ_constraint_handler.py")
        print("  • logging_protocol.py")
        return

    test_results = []

    # Run tests
    print("\n🚀 Starting Phase 0 component tests...")

    # Test 1: Christ Constraint Handler
    print("\n📋 Test 1: Christ Constraint Handler")
    result1 = test_christ_constraint_handler()
    test_results.append(("Christ Constraint Handler", result1))

    # Test 2: Logging Protocol
    print("\n📋 Test 2: Logging Protocol")
    result2 = test_logging_protocol()
    test_results.append(("Logging Protocol", result2))

    # Test 3: Data Models
    print("\n📋 Test 3: Data Models")
    result3 = test_data_models()
    test_results.append(("Data Models", result3))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    all_passed = True
    for test_name, passed in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("Phase 0 components are working correctly.")
    else:
        print("⚠️ SOME TESTS FAILED")
        print("Please check the test output above for details.")

    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("1. Start the daemon: python LOCAL_AI_DAEMON.py")
    print("2. Run integration tests with actual daemon")
    print("3. Proceed to Phase 1 implementation")
    print("=" * 70)

    # Cleanup
    import os

    if os.path.exists("test_logging.log"):
        os.remove("test_logging.log")
    if os.path.exists("test_audit_trail.json"):
        os.remove("test_audit_trail.json")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
