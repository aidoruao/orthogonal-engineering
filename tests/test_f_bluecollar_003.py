"""
Falsification test: Confined space atmospheric monitoring prevents unsafe entry.
Hazardous atmosphere keeps door locked.

# @falsification_id: F-BLUECOLLAR-003
"""
import pytest

class ConfinedSpaceMonitor:
    OXYGEN_MIN = 19.5
    OXYGEN_MAX = 23.5
    LEL_MAX = 10.0

    def is_safe(self, o2_pct: float, lel_pct: float) -> bool:
        return self.OXYGEN_MIN <= o2_pct <= self.OXYGEN_MAX and lel_pct < self.LEL_MAX

    def unlock_door(self, o2_pct: float, lel_pct: float) -> str:
        if self.is_safe(o2_pct, lel_pct):
            return "UNLOCKED"
        return "LOCKED"

def test_hazardous_atmosphere_keeps_door_locked():
    monitor = ConfinedSpaceMonitor()
    assert monitor.unlock_door(15.0, 5.0) == "LOCKED"   # low O2
    assert monitor.unlock_door(21.0, 15.0) == "LOCKED"  # high LEL
    assert monitor.unlock_door(21.0, 5.0) == "UNLOCKED" # safe

