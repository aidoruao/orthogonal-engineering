"""
Falsification test: Safety interlock cannot be bypassed by software.
Interlock open blocks all actuator commands.

# @falsification_id: F_INDUSTRIAL_005
"""
import pytest

class SafetyInterlock:
    def __init__(self):
        self.open = True

    def send_command(self, cmd: str) -> str:
        if self.open:
            return "BLOCKED"
        return "EXECUTED"

def test_interlock_blocks_all_commands():
    interlock = SafetyInterlock()
    commands = ["start_motor", "open_valve", "engage_clutch", "raise_arm"]
    for cmd in commands:
        result = interlock.send_command(cmd)
        assert result == "BLOCKED", f"Command {cmd!r} was not blocked by open interlock"
