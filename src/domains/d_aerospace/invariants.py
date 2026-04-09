#!/usr/bin/env python3
"""Aerospace Domain Invariants — DO-178C compliance, redundancy, structural health."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    SoftwareComponent, CertificationLevel, RedundancyChecker,
    StructuralHealthMonitor, MAX_LINES_PER_FUNCTION
)


def check_certification_coverage(component: SoftwareComponent) -> Tuple[bool, ProofObject]:
    """DO-178C requires specific structural coverage based on DAL."""
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
    """Redundant channels must agree on output for voting."""
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
    """Structural health sensors must be within specification."""
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
    """Advisory: functions should not exceed recommended size."""
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
