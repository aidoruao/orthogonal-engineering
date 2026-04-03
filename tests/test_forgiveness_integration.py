#!/usr/bin/env python3
# @falsification_id: F_FORGIVENESS_001
"""Tests for forgiveness-system integration with the PR84 audit pipeline."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from forgiveness_system.forgiveness_system import EnergyType, ForgivenessSystem


def test_violation_produces_building_output():
    with tempfile.TemporaryDirectory() as tmpdir:
        system = ForgivenessSystem(base_path=tmpdir)
        violation_id = system.log_violation("test violation", "tests/test_forgiveness_integration.py")
        fork_id = system.create_state_fork(violation_id)
        output = system.execute_building_workflow(fork_id)
        assert output is not None
        assert system.violations[violation_id].building_output_id == output.id
        assert system.violations[violation_id].engagement_count == 1


def test_energy_allocation_defaults_to_build_over_fight():
    with tempfile.TemporaryDirectory() as tmpdir:
        system = ForgivenessSystem(base_path=tmpdir)
        violation_id = system.log_violation("energy test", "tests/test_forgiveness_integration.py")
        fork_id = system.create_state_fork(violation_id)
        fork = system.forks[fork_id]
        assert fork.get_energy(EnergyType.BUILD) == 0.7
        assert fork.get_energy(EnergyType.FIGHT) == 0.0


def test_emotional_pointer_is_dereferenced_on_fork():
    with tempfile.TemporaryDirectory() as tmpdir:
        system = ForgivenessSystem(base_path=tmpdir)
        violation_id = system.log_violation("pointer test", "tests/test_forgiveness_integration.py")
        assert system.violations[violation_id].emotional_pointer is not None
        system.create_state_fork(violation_id)
        assert system.violations[violation_id].emotional_pointer is None


def test_trace_generation_reflects_building_output():
    with tempfile.TemporaryDirectory() as tmpdir:
        system = ForgivenessSystem(base_path=tmpdir)
        violation_id = system.log_violation("trace test", "tests/test_forgiveness_integration.py")
        fork_id = system.create_state_fork(violation_id)
        system.execute_building_workflow(fork_id)
        trace = system.generate_trace()
        assert trace["system_state"]["violations_count"] == 1
        assert trace["system_state"]["building_outputs_count"] == 1


def main():
    test_violation_produces_building_output()
    test_energy_allocation_defaults_to_build_over_fight()
    test_emotional_pointer_is_dereferenced_on_fork()
    test_trace_generation_reflects_building_output()
    print("PASS test_forgiveness_integration")


if __name__ == "__main__":
    main()
