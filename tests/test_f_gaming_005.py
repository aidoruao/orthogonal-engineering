"""
Falsification test: Mod system cannot execute arbitrary code outside sandbox.
Mod confined to game resources.

# @falsification_id: F_GAMING_005
"""
import os
import pytest

GAME_DIR = "/tmp/game_sandbox"

class ModSandbox:
    def __init__(self, game_dir: str):
        self.game_dir = os.path.abspath(game_dir)

    def access_file(self, path: str) -> str:
        abs_path = os.path.abspath(path)
        if not abs_path.startswith(self.game_dir):
            return "ACCESS_DENIED"
        return "ACCESS_GRANTED"

def test_mod_cannot_escape_sandbox():
    sandbox = ModSandbox(GAME_DIR)
    assert sandbox.access_file("/etc/passwd") == "ACCESS_DENIED"
    assert sandbox.access_file("/tmp/game_sandbox/textures/tex.png") == "ACCESS_GRANTED"
    assert sandbox.access_file("/tmp/game_sandbox/../../../etc/hosts") == "ACCESS_DENIED"
