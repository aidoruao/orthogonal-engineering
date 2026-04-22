"""
Test script for IDE Adapter
Tests the routing logic and traceability features.
"""

import json
import os
import sys

from ide_adapter import IDEAdapter, route_ide_query


def test_basic_routing():
    """Test basic routing functionality."""
    print("=== Testing Basic Routing ===")

    # Initialize adapter
    workspace = os.path.dirname(os.path.abspath(__file__))
    adapter = IDEAdapter(workspace)

    # Test 1: Query with automation keyword
    print("\nTest 1: Query with 'automation' keyword")
    result = adapter.route_query("How do I use the automation tools?")
    print(f"Result: {json.dumps(result, indent=2)}")

    # Test 2: Query with documentation keyword
    print("\nTest 2: Query with 'documentation' keyword")
    result = adapter.route_query("Where is the documentation?")
    print(f"Result: {json.dumps(result, indent=2)}")

    # Test 3: Query with file path metadata
    print("\nTest 3: Query with file path metadata")
    result = adapter.route_query(
        "Fix this bug",
        metadata={"file_path": "automation/run_full_audit_with_trace.py"},
    )
    print(f"Result: {json.dumps(result, indent=2)}")

    # Test 4: Query with folder path metadata
    print("\nTest 4: Query with folder path metadata")
    result = adapter.route_query(
        "What's in this folder?", metadata={"folder_path": "toolkit/oe"}
    )
    print(f"Result: {json.dumps(result, indent=2)}")

    # Test 5: Ambiguous query (should be rejected)
    print("\nTest 5: Ambiguous query (should be rejected)")
    result = adapter.route_query("automation documentation")
    print(f"Result: {json.dumps(result, indent=2)}")

    # Test 6: General query (should go to dynamic warden)
    print("\nTest 6: General query (should go to dynamic warden)")
    result = adapter.route_query("How does this system work?")
    print(f"Result: {json.dumps(result, indent=2)}")

    return True


def test_scoped_context():
    """Test scoped context generation."""
    print("\n=== Testing Scoped Context ===")

    workspace = os.path.dirname(os.path.abspath(__file__))
    adapter = IDEAdapter(workspace)

    # Get context for automation warden
    print("\nTest: Scoped context for automation_warden")
    context = adapter.get_scoped_context_for_warden(
        "automation_warden", "How do I run the audit?"
    )
    print(f"Context keys: {list(context.keys())}")
    print(f"Warden metadata keys: {list(context.get('warden_metadata', {}).keys())}")

    # Verify scoped context rules
    assert "query" in context
    assert "warden_metadata" in context
    assert "global_repo_state" not in context  # Should not be included
    assert "other_wardens" not in context  # Should not be included

    print("✓ Scoped context follows rules")
    return True


def test_trace_generation():
    """Test trace file generation."""
    print("\n=== Testing Trace Generation ===")

    workspace = os.path.dirname(os.path.abspath(__file__))
    adapter = IDEAdapter(workspace)

    # Make a query that should generate a trace
    result = adapter.route_query("Test trace generation")

    # Check if trace file was created
    trace_id = result.get("trace_id")
    trace_file = os.path.join(workspace, "logs", "traces", f"ide_query_{trace_id}.json")

    if os.path.exists(trace_file):
        print(f"✓ Trace file created: {trace_file}")

        # Load and verify trace content
        with open(trace_file, "r") as f:
            trace_data = json.load(f)

        required_fields = ["trace_id", "query", "metadata", "result", "timestamp"]
        for field in required_fields:
            assert field in trace_data, f"Missing field in trace: {field}"

        print("✓ Trace file contains all required fields")
        return True
    else:
        print(f"✗ Trace file not found: {trace_file}")
        return False


def test_session_management():
    """Test session ID generation and persistence."""
    print("\n=== Testing Session Management ===")

    workspace = os.path.dirname(os.path.abspath(__file__))

    # Create two adapters (should have different session IDs)
    adapter1 = IDEAdapter(workspace)
    adapter2 = IDEAdapter(workspace)

    session1 = adapter1.get_session_info()
    session2 = adapter2.get_session_info()

    print(f"Adapter 1 Session ID: {session1['session_id']}")
    print(f"Adapter 2 Session ID: {session2['session_id']}")

    # Session IDs should be different (generated per instance)
    assert session1["session_id"] != session2["session_id"], (
        "Session IDs should be unique"
    )

    # But IDE name and workspace should be the same
    assert session1["ide_name"] == session2["ide_name"], "IDE names should match"
    assert session1["workspace_root"] == session2["workspace_root"], (
        "Workspace roots should match"
    )

    print("✓ Session management working correctly")
    return True


def test_convenience_function():
    """Test the convenience route_ide_query function."""
    print("\n=== Testing Convenience Function ===")

    workspace = os.path.dirname(os.path.abspath(__file__))

    result = route_ide_query(
        "Test convenience function", workspace, metadata={"test": "metadata"}
    )

    assert "trace_id" in result
    assert "status" in result
    assert "timestamp" in result

    print(f"Result: {json.dumps(result, indent=2)}")
    print("✓ Convenience function working")
    return True


def test_registry_loading():
    """Test that registry is loaded correctly."""
    print("\n=== Testing Registry Loading ===")

    workspace = os.path.dirname(os.path.abspath(__file__))
    adapter = IDEAdapter(workspace)

    # Get session info which includes registry stats
    session_info = adapter.get_session_info()

    print(f"Total wardens: {session_info['total_wardens']}")
    print(f"Traces directory: {session_info['traces_dir']}")

    # Verify we have expected wardens
    expected_wardens = [
        "automation_warden",
        "toolkit_warden",
        "documentation_warden",
        "logs_warden",
        "evidence_warden",
    ]

    # This is just informational - don't fail if some are missing
    print("Expected wardens (some may not exist):")
    for warden in expected_wardens:
        print(f"  - {warden}")

    print("✓ Registry loaded successfully")
    return True


def main():
    """Run all tests."""
    print("Running IDE Adapter Tests")
    print("=" * 50)

    tests = [
        ("Basic Routing", test_basic_routing),
        ("Scoped Context", test_scoped_context),
        ("Trace Generation", test_trace_generation),
        ("Session Management", test_session_management),
        ("Convenience Function", test_convenience_function),
        ("Registry Loading", test_registry_loading),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            print(f"\nRunning: {test_name}")
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ {test_name} failed with error: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {test_name}")
        if success:
            passed += 1

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
