#!/usr/bin/env python3
"""Aerospace Domain Invariants — DO-178C compliance, redundancy, structural health."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    CertificationLevel,
    MAX_LINES_PER_FUNCTION,
    RedundancyChecker,
    RedundantChannel,
    SoftwareComponent,
    StructuralHealthMonitor,
    StructuralHealthSensor,
)


def check_certification_coverage(component: SoftwareComponent) -> Tuple[bool, ProofObject]:
    """DO-178C requires specific structural coverage based on DAL.

    Falsifies if: coverage for the DAL (MC/DC or decision) is below 100%.
    falsifies_if: coverage for the DAL (MC/DC or decision) is below 100%.
    """
    required = component.required_mc_dc_coverage()
    
    if component.dal == CertificationLevel.LEVEL_A:
        actual = component.structural_coverage_mc_dc
        if actual < Fraction(100):
            return False, ProofObject(
                conclusion=f"VIOLATION: Level A requires 100% MC/DC, got {actual}%",
                premises=[f"MC/DC: {actual}%", "Required: 100%"],
                rule="do178c_table_a1"
            )
    
    if component.dal == CertificationLevel.LEVEL_B:
        actual = component.structural_coverage_decision
        if actual < Fraction(100):
            return False, ProofObject(
                conclusion=f"VIOLATION: Level B requires 100% decision coverage, got {actual}%",
                premises=[],
                rule="do178c_table_a1"
            )
    
    return True, ProofObject(
        conclusion=f"Structural coverage adequate for {component.dal.name}",
        premises=[],
        rule="do178c_coverage"
    )


def check_redundancy_agreement(checker: RedundancyChecker) -> Tuple[bool, ProofObject]:
    """Redundant channels must agree on output for voting.

    Falsifies if: no healthy channels, cannot form quorum, or healthy channels disagree.
    falsifies_if: no healthy channels, cannot form quorum, or healthy channels disagree.
    """
    healthy = checker.get_healthy_channels()
    
    if len(healthy) == 0:
        return False, ProofObject(
            conclusion="VIOLATION: No healthy channels available",
            premises=[],
            rule="redundancy_health"
        )
    
    if not checker.can_vote():
        return False, ProofObject(
            conclusion=f"VIOLATION: Insufficient healthy channels for majority ({len(healthy)}/{len(checker.channels)})",
            premises=[],
            rule="redundancy_quorum"
        )
    
    if not checker.channels_agree():
        return False, ProofObject(
            conclusion="VIOLATION: Healthy channels disagree on output",
            premises=[],
            rule="redundancy_consensus"
        )
    
    return True, ProofObject(
        conclusion="Redundant channels in agreement",
        premises=[f"Healthy: {len(healthy)}", f"Total: {len(checker.channels)}"],
        rule="redundancy_consensus"
    )


def check_structural_health(monitor: StructuralHealthMonitor) -> Tuple[bool, ProofObject]:
    """Structural health sensors must be within specification.

    Falsifies if: monitor.get_alerted_sensors() is non-empty.
    falsifies_if: monitor.get_alerted_sensors() is non-empty.
    """
    alerted = monitor.get_alerted_sensors()
    
    if len(alerted) > 0:
        return False, ProofObject(
            conclusion=f"VIOLATION: {len(alerted)} sensors outside spec",
            premises=[s.sensor_id for s in alerted],
            rule="structural_health_threshold"
        )
    
    return True, ProofObject(
        conclusion="Structural health within specification",
        premises=[f"Sensors checked: {len(monitor.sensors)}"],
        rule="structural_health"
    )


def check_function_size(component: SoftwareComponent) -> Tuple[bool, ProofObject]:
    """Advisory: functions should not exceed recommended size.

    Falsifies if: average lines_per_function exceeds MAX_LINES_PER_FUNCTION.
    falsifies_if: average lines_per_function exceeds MAX_LINES_PER_FUNCTION.
    """
    lines_per_func = Fraction(component.lines_of_code, max(1, component.requirements_based_tests))
    
    if lines_per_func > MAX_LINES_PER_FUNCTION:
        return False, ProofObject(
            conclusion=f"VIOLATION: Average function size {lines_per_func} > {MAX_LINES_PER_FUNCTION}",
            premises=[],
            rule="do178c_complexity_advisory"
        )
    
    return True, ProofObject(
        conclusion="Function size within advisory limits",
        premises=[],
        rule="do178c_complexity"
    )


def run_all_invariants() -> dict:
    """Run all D_AEROSPACE invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    software_component = SoftwareComponent(
        name="Sample AEROSPAC",
        dal=CertificationLevel.LEVEL_A,
        lines_of_code=1,
        structural_coverage_mc_dc=Fraction(100),
        structural_coverage_decision=Fraction(100),
        structural_coverage_statement=Fraction(100),
    )
    redundancy_checker = RedundancyChecker(
        channels=[RedundantChannel(
        channel_id="AEROSPAC-001",
    )],
    )
    structural_health_monitor = StructuralHealthMonitor(
        sensors=[StructuralHealthSensor(
        sensor_id="AEROSPAC-001",
        location="Sample Location",
    )],
    )

    checks = [
        ("check_certification_coverage", lambda: check_certification_coverage(software_component)),
        ("check_function_size", lambda: check_function_size(software_component)),
        ("check_redundancy_agreement", lambda: check_redundancy_agreement(redundancy_checker)),
        ("check_structural_health", lambda: check_structural_health(structural_health_monitor)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            result = func()
            if isinstance(result, tuple) and len(result) == 2:
                success, proof = result
                results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
            else:
                passed = getattr(result, "passed", True)
                results[name] = "PASS" if passed else "FAIL: " + str(getattr(result, "evidence", result))
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_AEROSPACE invariants: PASS")
