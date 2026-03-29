"""
Falsification test for F_MINECRAFT_001.

Tests the invariant: Sign text is parsed correctly from turtle.inspect()
data.state fields (MC 1.20+ double-sided signs).

Falsifying observation: Sign text is missing, truncated, or incorrectly parsed.
"""
# @falsification_id: F_MINECRAFT_001

import json


def _parse_sign_text(inspect_data):
    """Parse sign text from CC:Tweaked turtle.inspect() return data."""
    state = inspect_data.get("state", {})
    front = state.get("front_text", {}).get("messages", [])
    back = state.get("back_text", {}).get("messages", [])
    parsed_front = []
    parsed_back = []
    for msg in front:
        if isinstance(msg, str):
            try:
                parsed = json.loads(msg)
                parsed_front.append(parsed.get("text", ""))
            except (json.JSONDecodeError, TypeError):
                parsed_front.append(msg)
        elif isinstance(msg, dict):
            parsed_front.append(msg.get("text", ""))
    for msg in back:
        if isinstance(msg, str):
            try:
                parsed = json.loads(msg)
                parsed_back.append(parsed.get("text", ""))
            except (json.JSONDecodeError, TypeError):
                parsed_back.append(msg)
        elif isinstance(msg, dict):
            parsed_back.append(msg.get("text", ""))
    return parsed_front, parsed_back


def test_f_minecraft_001():
    """F_MINECRAFT_001: Sign text parsed correctly from turtle.inspect()."""
    mock_inspect = {
        "name": "minecraft:oak_sign",
        "state": {
            "front_text": {
                "messages": [
                    '{"text":"ZONE_A"}',
                    '{"text":"X=100"}',
                    '{"text":"Z=200"}',
                    '{"text":"INVARIANT"}',
                ]
            },
            "back_text": {
                "messages": [
                    '{"text":"BACK_1"}',
                    '{"text":"BACK_2"}',
                    '{"text":""}',
                    '{"text":""}',
                ]
            },
        },
    }
    front, back = _parse_sign_text(mock_inspect)
    assert len(front) == 4, f"Expected 4 front lines, got {len(front)}"
    assert len(back) == 4, f"Expected 4 back lines, got {len(back)}"
    assert front[0] == "ZONE_A"
    assert front[1] == "X=100"
    assert front[2] == "Z=200"
    assert front[3] == "INVARIANT"
    assert back[0] == "BACK_1"
    assert back[1] == "BACK_2"
