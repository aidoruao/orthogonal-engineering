"""Tests for kingdom_os_entry.py — boot + engine integration."""

import subprocess
import sys
import json


def test_version_flag():
    """--version prints version and exits 0."""
    result = subprocess.run(
        [sys.executable, "kingdom_os_entry.py", "--version"],
        capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0
    assert "Kingdom OS" in result.stdout
    assert "v0.1.0" in result.stdout


def test_query_flag():
    """--query runs a single query and exits."""
    result = subprocess.run(
        [sys.executable, "kingdom_os_entry.py", "--query", "nuclear reactor scram"],
        capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0
    assert "Boot complete" in result.stdout


def test_json_flag():
    """--json outputs valid JSON."""
    result = subprocess.run(
        [sys.executable, "kingdom_os_entry.py", "--query", "criminal miranda",
         "--json"],
        capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0
    # Find the JSON line in output (after boot messages)
    lines = result.stdout.strip().split('\n')
    # Last chunk should be parseable JSON
    json_text = ""
    brace_depth = 0
    for line in lines:
        if '{' in line:
            json_text = line
            brace_depth = line.count('{') - line.count('}')
        elif brace_depth > 0:
            json_text += '\n' + line
            brace_depth += line.count('{') - line.count('}')
    if json_text:
        parsed = json.loads(json_text)
        assert "text" in parsed
        assert "speaker_hash" in parsed
        assert "thinker_hash" in parsed


def test_boot_integrity():
    """Boot sequence completes with all phases verified."""
    from fractions import Fraction
    from kernel.boot import boot, verify_boot_integrity
    state, proof = boot(Fraction(8 * 1024**3))
    valid, v_proof = verify_boot_integrity(state)
    assert valid is True
    assert state.userland_reached is True
    assert len(state.steps_completed) == 6
    assert proof.proof_hash  # non-empty


def test_engine_loads_after_boot():
    """OrthogonalEngine initializes after kernel boot."""
    from fractions import Fraction
    from kernel.boot import boot
    from oe_engine.engine import OrthogonalEngine
    state, _ = boot(Fraction(8 * 1024**3))
    assert state.userland_reached
    engine = OrthogonalEngine()
    assert engine._manifest.domain_count > 100
    assert engine._manifest.manifest_hash
