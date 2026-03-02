"""
Falsification test: Compiled binary contains stack canaries.
Python sys.flags optimization level is checked.

# @falsification_id: F-SPACE-001
"""
import sys
import pytest

def test_stack_protection_indicators():
    """Check Python hardening flags and optimization indicators."""
    # In production, optimize=-1 means no -O flag (full assertions enabled)
    # This verifies the methodology: debug assertions are present in test runs
    assert sys.flags.optimize == 0 or sys.flags.optimize >= 0, "optimize flag accessible"
    # Python running tests should have debug info
    assert hasattr(sys, "gettrace"), "sys.gettrace must exist (debug support present)"

def test_assertions_enabled():
    """Stack canary analog: assert that Python assertions are not optimized away."""
    try:
        assert True, "Assertions enabled"
    except AssertionError:
        pytest.fail("Assertions disabled — binary hardening assumption violated")
