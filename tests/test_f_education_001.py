"""
Falsification test: Proctoring detects prohibited browser navigation.
Tab-switch detected and flagged.

# @falsification_id: F_EDUCATION_001
"""
import pytest

class ProctoringSystem:
    def __init__(self):
        self.flags = []

    def on_tab_switch(self, event: dict):
        if event.get("type") == "tab_switch":
            self.flags.append({"violation": "tab_switch", "time": event.get("time", 0)})

def test_tab_switch_detected():
    proctor = ProctoringSystem()
    proctor.on_tab_switch({"type": "tab_switch", "time": 42.5})
    assert len(proctor.flags) == 1
    assert proctor.flags[0]["violation"] == "tab_switch"

def test_non_violation_not_flagged():
    proctor = ProctoringSystem()
    proctor.on_tab_switch({"type": "mouse_move", "time": 10.0})
    assert len(proctor.flags) == 0
