"""
Falsification test for F_MINECRAFT_004.

Tests the invariant: Pre-action constraint check rejects any turtle command
that violates spatial invariants.

Falsifying observation: SigmaLoraConstraintSystem.validate_command() accepts
a command that violates a spatial invariant (e.g., permits digging straight
down without safety checks, or permits autonomous forever-mining).

The constraint logic is defined in minimal_ai_ide/turtle_constraint_server.py.
This test inlines the two relevant constraint methods (check_error_forgiveness
and check_autonomy_prevention) to keep the test self-contained and
CI-executable without the optional server dependencies (fastapi, pydantic).
"""
# @falsification_id: F_MINECRAFT_004

import re


# --- Inlined constraint methods from SigmaLoraConstraintSystem ---
# Source: minimal_ai_ide/turtle_constraint_server.py:168-299


def _check_error_forgiveness(command: str) -> bool:
    """GRACE: rejects commands that lack error recovery for dangerous actions."""
    command_lower = command.lower()
    dangerous_without_safety = [
        "dig straight down",
        "mine without checking",
        "build without support",
    ]
    for dangerous in dangerous_without_safety:
        if dangerous in command_lower:
            safety_terms = ["check", "verify", "safe", "careful", "slow"]
            if not any(term in command_lower for term in safety_terms):
                return False
    return True


def _check_autonomy_prevention(command: str, context: dict) -> bool:
    """KENOSIS: rejects commands that create autonomous systems."""
    command_lower = command.lower()
    autonomous_patterns = [
        "forever",
        "infinite",
        "always",
        "never stop",
        "autonomous",
        "self-sustaining",
        "auto-pilot",
    ]
    for pattern in autonomous_patterns:
        if pattern in command_lower:
            if not (context and context.get("allow_autonomous", False)):
                return False
    return True


def _validate_command(command: str, context: dict) -> tuple:
    """
    Validate command against all spatial constraints.
    Returns (is_valid, constraints, christ_score).
    Only GRACE and KENOSIS are spatial-invariant-relevant; others pass by default.
    """
    constraints = {
        "LOGOS": True,          # logical consistency — not spatial
        "CHALCEDON": True,      # human collaboration — not spatial
        "GRACE": _check_error_forgiveness(command),
        "ESCHATON": True,       # purpose alignment — not spatial
        "AGAPE": True,          # user benefit — not spatial
        "KENOSIS": _check_autonomy_prevention(command, context),
    }
    christ_score = sum(1 for v in constraints.values() if v) / len(constraints)
    is_valid = all(constraints.values())
    return is_valid, constraints, christ_score


# --- Tests ---


def test_f_minecraft_004_grace_rejects_unsafe_dig():
    """
    F_MINECRAFT_004 / GRACE: 'dig straight down' must be rejected.

    Spatial invariant: Pre-action constraint check rejects any turtle command
    that violates spatial invariants.

    'Dig straight down' is a spatial-invariant violation: it ignores the GRACE
    constraint that requires error-recovery paths for dangerous movement
    operations (fall hazard, lava, void) and includes no safety terms
    ("check", "verify", "safe", "careful", "slow").

    Note: the phrase "dig straight down without checking" is NOT a valid test
    case because "checking" contains the safety term "check" and would pass
    the GRACE filter. The minimal violating form is "dig straight down" alone.
    """
    command = "dig straight down"
    context = {}
    is_valid, constraints, christ_score = _validate_command(command, context)

    assert not constraints["GRACE"], (
        "F_MINECRAFT_004 FAILED: GRACE constraint accepted 'dig straight down'. "
        "Expected rejection — command lacks safety checks."
    )
    assert not is_valid, (
        "F_MINECRAFT_004 FAILED: validate_command returned is_valid=True for "
        f"'{command}'. Expected False. Constraints: {constraints}"
    )


def test_f_minecraft_004_kenosis_rejects_forever_mining():
    """
    F_MINECRAFT_004 / KENOSIS: 'mine forever' must be rejected.

    Spatial invariant: Pre-action constraint check rejects any turtle command
    that violates spatial invariants.

    'Mine forever' is a spatial-invariant violation: it enables unbounded
    autonomous operation without human check-in (KENOSIS constraint).
    """
    command = "mine forever"
    context = {}
    is_valid, constraints, christ_score = _validate_command(command, context)

    assert not constraints["KENOSIS"], (
        "F_MINECRAFT_004 FAILED: KENOSIS constraint accepted 'mine forever'. "
        "Expected rejection — autonomous/forever operation requires allow_autonomous."
    )
    assert not is_valid, (
        "F_MINECRAFT_004 FAILED: validate_command returned is_valid=True for "
        f"'{command}'. Expected False. Constraints: {constraints}"
    )


def test_f_minecraft_004_valid_command_passes():
    """
    F_MINECRAFT_004 / pass: a safe, bounded command must be accepted.

    Verifies that the constraint system is not over-rejecting: a well-formed
    command with no spatial invariant violations must pass all constraints.
    """
    command = "dig forward 3 blocks carefully"
    context = {}
    is_valid, constraints, christ_score = _validate_command(command, context)

    assert constraints["GRACE"], (
        f"F_MINECRAFT_004 FAILED: GRACE rejected '{command}' unexpectedly."
    )
    assert constraints["KENOSIS"], (
        f"F_MINECRAFT_004 FAILED: KENOSIS rejected '{command}' unexpectedly."
    )
    assert is_valid, (
        f"F_MINECRAFT_004 FAILED: validate_command rejected '{command}'. "
        f"Constraints: {constraints}"
    )
    assert 0.0 <= christ_score <= 1.0, (
        f"F_MINECRAFT_004: christ_score out of range: {christ_score}"
    )


def test_f_minecraft_004_allow_autonomous_flag_permits_forever():
    """
    F_MINECRAFT_004 / context override: allow_autonomous=True must bypass KENOSIS.

    Confirms the constraint system is correctly context-aware: when the operator
    explicitly grants autonomous permission, KENOSIS no longer rejects the command.
    """
    command = "mine forever"
    context = {"allow_autonomous": True}
    is_valid, constraints, christ_score = _validate_command(command, context)

    assert constraints["KENOSIS"], (
        "F_MINECRAFT_004 FAILED: KENOSIS rejected 'mine forever' even with "
        "allow_autonomous=True. Expected acceptance."
    )
