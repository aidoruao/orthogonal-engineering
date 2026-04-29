"""Test Warden Units - Test Warden Units"""
import os
from pathlib import Path

from wardens.cherub_unit import CherubUnit
from wardens.ophanim_unit import OphanimUnit
from wardens.seraph_unit import SeraphUnit


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_seraph_unit_interface_and_deterministic_scan(tmp_path):
    _write(
        tmp_path / "sample.py",
        """
def returns_value(flag: bool) -> int:
    if flag:
        return 1


def duplicate_one():
    value = 1
    return value


def duplicate_two():
    value = 1
    return value


def tautology():
    if True or True:
        return 1
    return 0


def unreachable():
    return 1
    value = 2
    return value
""".strip(),
    )

    unit = SeraphUnit(str(tmp_path))
    init_result = unit.initialize()
    scan_one = unit.query("scan")
    scan_two = unit.query("scan")
    health = unit.health_check()

    assert init_result["success"] is True
    assert scan_one["success"] is True
    assert scan_one["analysis_hash"] == scan_two["analysis_hash"]
    assert scan_one["logic_audit"]["finding_count"] >= 3
    assert health["overall_health"] == "healthy"
    assert unit.get_metadata()["initialized"] is True


def test_cherub_unit_interface_and_deterministic_scan(tmp_path):
    _write(
        tmp_path / "documentation" / "report.md",
        "studies show the program works with no incidents and no engagement\nselective mutism therapy\n",
    )
    _write(
        tmp_path / "scripts" / "notes.txt",
        "experts say this is widely known without a source\n",
    )
    _write(
        tmp_path / "evidence" / "case.txt",
        "Generated: 2026-04-03\nNo incidents and no engagement were treated as absence of distress.\n",
    )

    unit = CherubUnit(str(tmp_path))
    init_result = unit.initialize()
    scan_one = unit.query("scan")
    scan_two = unit.query("scan")
    health = unit.health_check()

    assert init_result["success"] is True
    assert scan_one["success"] is True
    assert scan_one["analysis_hash"] == scan_two["analysis_hash"]
    assert scan_one["source_verification"]["finding_count"] >= 1
    assert scan_one["pii_boundary_check"]["finding_count"] >= 1
    assert health["overall_health"] == "healthy"
    assert unit.get_metadata()["initialized"] is True


def test_ophanim_unit_interface_and_deterministic_scan(tmp_path):
    _write(tmp_path / "module_a.py", "import module_b\n")
    _write(tmp_path / "module_b.py", "import module_a\n")
    _write(tmp_path / "logs" / "feedback.log", "amplitude=1\namplitude=2\namplitude=3\n")
    recent_log = tmp_path / "logs" / "recent.log"
    previous_log = tmp_path / "logs" / "previous.log"
    _write(recent_log, "x" * 300)
    _write(previous_log, "x" * 100)
    now = int(os.path.getmtime(recent_log))
    os.utime(recent_log, (now, now))
    previous_timestamp = now - (8 * 24 * 60 * 60)
    os.utime(previous_log, (previous_timestamp, previous_timestamp))

    unit = OphanimUnit(str(tmp_path))
    init_result = unit.initialize()
    scan_one = unit.query("scan")
    scan_two = unit.query("scan")
    health = unit.health_check()

    assert init_result["success"] is True
    assert scan_one["success"] is True
    assert scan_one["analysis_hash"] == scan_two["analysis_hash"]
    assert scan_one["cycle_detection"]["dag_acyclic"] is False
    assert scan_one["entropy_monitoring"]["finding_count"] >= 1
    assert scan_one["growth_analysis"]["finding_count"] >= 1
    assert health["overall_health"] == "healthy"
    assert unit.get_metadata()["initialized"] is True
