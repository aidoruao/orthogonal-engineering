"""
Falsification test: LOTO cannot be overridden remotely.
LOTO active rejects all remote commands.

# @falsification_id: F_BLUECOLLAR_002
"""
import pytest

class LOTOSystem:
    def __init__(self):
        self.active = True

    def execute_remote(self, cmd: str) -> str:
        if self.active:
            return "REJECTED"
        return "OK"

def test_loto_rejects_all_remote_commands():
    loto = LOTOSystem()
    commands = ["power_on", "start_conveyor", "release_lock", "enable_output"]
    for cmd in commands:
        assert loto.execute_remote(cmd) == "REJECTED", f"{cmd} not rejected under LOTO"
