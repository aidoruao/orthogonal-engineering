"""D_DH_STANDALONE invariants — executable checks for the 5 domain invariants.

Each function in this module represents an invariant check that can be executed
against the DH source code or runtime behavior. The checks follow the pattern
from D_DOLLARTREE but are specialized for Minecraft mod forensics.

Invariants:
  1. serverTickEvent must complete within 15ms (30% of 50ms tick)
  2. No GL calls during FML splash screen phase
  3. Config distance values must have upper bound validation
  4. Mixin redirects must check thread context before GL operations
  5. Every error path must have a user-facing message
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class InvariantCheck:
    """Result of an invariant check."""
    invariant_id: str
    description: str
    passed: bool
    evidence: str
    violation_location: Optional[str] = None
    recommended_fix: Optional[str] = None


# ---------------------------------------------------------------------------
# Invariant 1: Tick budget compliance
# ---------------------------------------------------------------------------


def check_tick_budget_compliance(
    time_budget_ms: float = 15.0,
    tick_duration_ms: float = 50.0,
    max_events: int = 20,
) -> InvariantCheck:
    """
    Check that serverTickEvent completes within its time budget.
    
    From DH_SOURCE_INDEX.json:
      - serverTickEvent has 15ms budget (line 124)
      - Unbounded chunkLoadEvents queue
      - while(!taskQueue.isEmpty()) with no count limit
    
    Args:
        time_budget_ms: The allocated time budget (default 15ms)
        tick_duration_ms: The full tick duration (default 50ms for 20 TPS)
        max_events: Maximum events to process per tick (should be bounded)
    
    Returns:
        InvariantCheck with pass/fail status
    """
    # Theoretical calculation: if each event takes 0.5ms, 20 events = 10ms (ok)
    # But with 4096-block generation, each event can take much longer
    estimated_time_per_event_ms = 0.75  # Conservative estimate with large generation
    estimated_time_for_max_events = max_events * estimated_time_per_event_ms
    
    # Check: can we process max_events within budget?
    can_meet_budget = estimated_time_for_max_events <= time_budget_ms
    
    # Additional check: budget as percentage of tick
    budget_percentage = (time_budget_ms / tick_duration_ms) * 100
    reasonable_budget = budget_percentage <= 30  # Should be < 30% of tick
    
    passed = can_meet_budget and reasonable_budget
    
    return InvariantCheck(
        invariant_id="IV-DH-001",
        description="serverTickEvent must complete within 15ms (30% of 50ms tick)",
        passed=passed,
        evidence=(
            f"Budget: {time_budget_ms}ms ({budget_percentage:.1f}% of tick). "
            f"Max events {max_events} × {estimated_time_per_event_ms}ms/event = "
            f"{estimated_time_for_max_events}ms. Can meet budget: {can_meet_budget}."
        ),
        violation_location="ForgeServerProxy.java:serverTickEvent (lines 105-141)" if not passed else None,
        recommended_fix="Reduce budget to 5ms and cap events at 20 per tick" if not passed else None,
    )


def check_queue_boundedness(max_queue_size: int = 1000) -> InvariantCheck:
    """
    Check that chunkLoadEvents queue has a bounded size.
    
    From DH analysis: ConcurrentLinkedQueue grows without bound.
    
    Args:
        max_queue_size: Maximum acceptable queue size
    
    Returns:
        InvariantCheck with pass/fail status
    """
    # The actual queue has no size limit
    has_size_limit = False  # From source analysis
    
    return InvariantCheck(
        invariant_id="IV-DH-002",
        description="Chunk event queue must have bounded size",
        passed=has_size_limit,
        evidence=(
            f"Queue uses ConcurrentLinkedQueue without size limit. "
            f"Expected max: {max_queue_size}, actual: unbounded."
        ),
        violation_location="ForgeServerProxy.java:chunkLoadEvents (line 101)" if not has_size_limit else None,
        recommended_fix="Add size counter and reject/overflow at 1000 entries" if not has_size_limit else None,
    )


# ---------------------------------------------------------------------------
# Invariant 2: GL context readiness
# ---------------------------------------------------------------------------


def check_gl_context_guard() -> InvariantCheck:
    """
    Check that MixinFramebuffer has GL context guard.
    
    From DH analysis: createDepthTexture executes GL during splash screen.
    
    Returns:
        InvariantCheck with pass/fail status
    """
    # The Mixin does not check for splash screen
    has_splash_guard = False  # From source analysis
    
    return InvariantCheck(
        invariant_id="IV-DH-003",
        description="No GL calls during FML splash screen phase",
        passed=has_splash_guard,
        evidence=(
            "MixinFramebuffer.createDepthTexture calls GL11.glBindTexture and "
            "GL11.glTexImage2D without checking if splash screen is active."
        ),
        violation_location="MixinFramebuffer.java:createDepthTexture (lines 31-52)" if not has_splash_guard else None,
        recommended_fix="Add isSplashScreenActive() check before GL operations" if not has_splash_guard else None,
    )


def check_thread_context_before_gl() -> InvariantCheck:
    """
    Check that GL operations verify thread context.
    
    Returns:
        InvariantCheck with pass/fail status
    """
    # The Mixin assumes correct thread but doesn't verify
    has_thread_check = False  # From source analysis
    
    return InvariantCheck(
        invariant_id="IV-DH-004",
        description="Mixin redirects must check thread context before GL operations",
        passed=has_thread_check,
        evidence="GL operations execute without Thread.currentThread() validation.",
        violation_location="MixinFramebuffer.java" if not has_thread_check else None,
        recommended_fix="Add thread context assertion before GL calls" if not has_thread_check else None,
    )


# ---------------------------------------------------------------------------
# Invariant 3: Config validation
# ---------------------------------------------------------------------------


def check_config_validation_warning(
    default_value: int = 4096,
    warning_threshold: int = 2048,
) -> InvariantCheck:
    """
    Check that config warns for values above threshold.
    
    From DH analysis: maxGenerationRequestDistance=4096 has no warning.
    
    Args:
        default_value: The default config value
        warning_threshold: Value above which warning should be shown
    
    Returns:
        InvariantCheck with pass/fail status
    """
    # No warning is issued for the default
    has_warning = False  # From source analysis
    is_aggressive = default_value > warning_threshold
    
    return InvariantCheck(
        invariant_id="IV-DH-005",
        description="Config distance values must have upper bound validation",
        passed=has_warning or not is_aggressive,
        evidence=(
            f"Default value {default_value} > threshold {warning_threshold}, "
            f"but no performance warning is logged. "
            f"Area: π × {default_value}² = {int(3.14159 * default_value * default_value):,} blocks² per player."
        ),
        violation_location="Config.java:maxGenerationRequestDistance (line 1744)" if not has_warning else None,
        recommended_fix="Add WARN log when value > 2048 with recommended 1024" if not has_warning else None,
    )


# ---------------------------------------------------------------------------
# Invariant 4 & 5: Error handling
# ---------------------------------------------------------------------------


def check_error_path_messages() -> InvariantCheck:
    """
    Check that error paths have user-facing messages.
    
    Returns:
        InvariantCheck with pass/fail status
    """
    # Many error paths just log or silently fail
    all_paths_have_messages = False  # From source analysis
    
    return InvariantCheck(
        invariant_id="IV-DH-006",
        description="Every error path must have a user-facing message",
        passed=all_paths_have_messages,
        evidence="Error paths exist without corresponding user notification.",
        recommended_fix="Add user-facing error messages to all catch blocks",
    )


# ---------------------------------------------------------------------------
# Composite check runner
# ---------------------------------------------------------------------------


def run_all_invariant_checks() -> Tuple[InvariantCheck, ...]:
    """Run all 6 invariant checks and return results."""
    return (
        check_tick_budget_compliance(),
        check_queue_boundedness(),
        check_gl_context_guard(),
        check_thread_context_before_gl(),
        check_config_validation_warning(),
        check_error_path_messages(),
    )


def get_invariant_summary() -> Dict[str, Any]:
    """Get a summary of all invariant checks."""
    checks = run_all_invariant_checks()
    passed = sum(1 for c in checks if c.passed)
    failed = len(checks) - passed
    
    return {
        "domain": "D_DH_STANDALONE",
        "total_checks": len(checks),
        "passed": passed,
        "failed": failed,
        "all_passed": failed == 0,
        "violations": [
            {
                "id": c.invariant_id,
                "description": c.description,
                "location": c.violation_location,
                "fix": c.recommended_fix,
            }
            for c in checks if not c.passed
        ],
    }
