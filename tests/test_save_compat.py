"""
Falsification test: Game save data is forward-compatible across versions.
v1 save loads correctly in v2 engine.

# @falsification_id: F-FUN-001
"""
import json
import pytest

def serialize_v1(state: dict) -> str:
    return json.dumps({"version": 1, "player": state})

def load_v2(data: str) -> dict:
    obj = json.loads(data)
    if obj["version"] == 1:
        obj["player"].setdefault("new_field_v2", "default_value")
    return obj["player"]

def test_v1_save_loads_in_v2():
    v1_state = {"name": "hero", "level": 5, "hp": 100}
    serialized = serialize_v1(v1_state)
    loaded = load_v2(serialized)
    assert loaded["name"] == v1_state["name"]
    assert loaded["level"] == v1_state["level"]
    assert loaded["hp"] == v1_state["hp"]
    assert "new_field_v2" in loaded
