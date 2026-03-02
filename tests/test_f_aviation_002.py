"""
Falsification test: ATC communication handles malformed messages gracefully.
Invalid ATC messages ignored without crash.

# @falsification_id: F_AVIATION_002
"""
import pytest

def parse_atc_message(msg: str) -> dict:
    if not msg or len(msg) < 3:
        return {"error": "too_short"}
    parts = msg.strip().split()
    if not parts:
        return {"error": "empty"}
    return {"callsign": parts[0], "instruction": parts[1] if len(parts) > 1 else ""}

MALFORMED = ["", "X", "\x00\xff", "A" * 5000, "   "]

def test_malformed_messages_no_exception():
    for msg in MALFORMED:
        try:
            result = parse_atc_message(msg)
            assert isinstance(result, dict)
        except Exception as e:
            pytest.fail(f"Exception on {msg!r}: {e}")
