"""
Falsification test: UV output is zero when door is open.
UV disabled when door sensor = OPEN.

# @falsification_id: F_CRUSADER_005
"""
import pytest

class UVController:
    def __init__(self):
        self.door_open = False
        self.uv_output = 0

    def set_door(self, open: bool):
        self.door_open = open
        if self.door_open:
            self.uv_output = 0

    def enable_uv(self, level: int):
        if self.door_open:
            return
        self.uv_output = level

def test_uv_off_when_door_open():
    ctrl = UVController()
    ctrl.set_door(True)
    ctrl.enable_uv(100)
    assert ctrl.uv_output == 0, "UV must be zero when door is open"

def test_uv_on_when_door_closed():
    ctrl = UVController()
    ctrl.set_door(False)
    ctrl.enable_uv(100)
    assert ctrl.uv_output == 100
