#!/usr/bin/env python3
"""D_SPACE Invariants — Space Systems

Verifies spaceflight software safety, radiation tolerance, orbital mechanics.
NASA-STD-8719.13B (Software Safety), ECSS-Q-ST-80C (ESA Space Product Assurance).
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    SpaceSoftware, RadiationTolerance, OrbitParameters,
    SoftwareCriticality,
    nasa_safety_critical_no_dynamic_alloc, nasa_seu_protection_required,
    nasa_radiation_margin_factor, orbital_escape_eccentricity
)


def check_memory_protection_enabled(software: SpaceSoftware) -> Tuple[bool, ProofObject]:
    """
    Safety-critical flight software must have memory protection (canaries, ASLR).

    NASA-STD-8719.13B: Safety-critical software shall employ memory protection
    mechanisms to prevent buffer overflows and corruption.

    Falsifies if: safety_critical and (no canaries or no ASLR)
    """
    if software.criticality != SoftwareCriticality.SAFETY_CRITICAL:
        return True, ProofObject(
            conclusion=f"Software {software.module_id} not safety-critical, memory protection N/A",
            premises=[f"Criticality: {software.criticality.name}"],
            rule="nasa_8719_13b_memory_protection"
        )

    if not software.has_canaries:
        return False, ProofObject(
            conclusion=f"VIOLATION: Safety-critical software {software.name} lacks stack canaries",
            premises=[
                f"Module: {software.module_id} ({software.name})",
                f"Criticality: {software.criticality.name}",
                f"Stack canaries: {software.has_canaries}",
                "NASA-STD-8719.13B requires memory protection"
            ],
            rule="nasa_8719_13b_memory_protection"
        )

    if not software.has_aslr:
        return False, ProofObject(
            conclusion=f"VIOLATION: Safety-critical software {software.name} lacks ASLR",
            premises=[
                f"Module: {software.module_id}",
                f"ASLR: {software.has_aslr}",
                "NASA-STD-8719.13B requires memory protection"
            ],
            rule="nasa_8719_13b_memory_protection"
        )

    return True, ProofObject(
        conclusion=f"Software {software.name} has required memory protections",
        premises=[f"Canaries: {software.has_canaries}", f"ASLR: {software.has_aslr}"],
        rule="nasa_8719_13b_memory_protection"
    )


def check_no_dynamic_allocation_in_realtime(software: SpaceSoftware) -> Tuple[bool, ProofObject]:
    """
    Real-time safety-critical paths must use static allocation only (no malloc/new).

    NASA-STD-8719.13B: Dynamic memory allocation introduces non-determinism
    and fragmentation risks in real-time systems.

    Falsifies if: safety_critical and uses_dynamic_allocation=True
    """
    if software.criticality != SoftwareCriticality.SAFETY_CRITICAL:
        return True, ProofObject(
            conclusion=f"Module {software.module_id} not safety-critical, dynamic allocation N/A",
            premises=[f"Criticality: {software.criticality.name}"],
            rule="nasa_8719_13b_dynamic_allocation"
        )

    if software.uses_dynamic_allocation:
        return False, ProofObject(
            conclusion=f"VIOLATION: Safety-critical module {software.name} uses dynamic allocation",
            premises=[
                f"Module: {software.module_id}",
                f"Criticality: {software.criticality.name}",
                f"Dynamic allocation: {software.uses_dynamic_allocation}",
                "NASA-STD-8719.13B prohibits dynamic allocation in safety-critical real-time code"
            ],
            rule="nasa_8719_13b_dynamic_allocation"
        )

    return True, ProofObject(
        conclusion=f"Module {software.name} uses static allocation only",
        premises=["Dynamic allocation: False"],
        rule="nasa_8719_13b_dynamic_allocation"
    )


def check_static_analysis_complement(software: SpaceSoftware) -> Tuple[bool, ProofObject]:
    """
    Static analysis findings must have corresponding runtime checks.

    NASA-STD-8719.13B: Defense-in-depth requires both static and dynamic analysis.
    Static analysis identifies potential issues; runtime checks mitigate them.

    Falsifies if: has_static_analysis but not has_runtime_checks
    """
    if not software.has_static_analysis:
        return False, ProofObject(
            conclusion=f"VIOLATION: Module {software.name} lacks static analysis",
            premises=[
                f"Module: {software.module_id}",
                f"Static analysis: {software.has_static_analysis}",
                "NASA-STD-8719.13B requires static analysis"
            ],
            rule="nasa_8719_13b_defense_in_depth"
        )

    if not software.has_runtime_checks:
        return False, ProofObject(
            conclusion=f"VIOLATION: Module {software.name} has static analysis but no runtime checks",
            premises=[
                f"Static analysis: {software.has_static_analysis}",
                f"Runtime checks: {software.has_runtime_checks}",
                "Defense-in-depth requires runtime checks to complement static analysis"
            ],
            rule="nasa_8719_13b_defense_in_depth"
        )

    return True, ProofObject(
        conclusion=f"Module {software.name} has defense-in-depth (static + runtime)",
        premises=["Static analysis: True", "Runtime checks: True"],
        rule="nasa_8719_13b_defense_in_depth"
    )


def check_radiation_tolerance_specs(component: RadiationTolerance, mission_dose: Fraction) -> Tuple[bool, ProofObject]:
    """
    Components must meet mission radiation requirements with margin.

    ECSS-Q-ST-80C: Component total dose rating must exceed mission requirement
    by design margin (typically 2x).

    Falsifies if: total_dose_rads < mission_dose * margin_factor
    """
    margin = nasa_radiation_margin_factor()
    required_dose = mission_dose * margin

    if component.total_dose_rads < required_dose:
        return False, ProofObject(
            conclusion=f"VIOLATION: Component {component.name} dose rating {component.total_dose_rads} rads insufficient",
            premises=[
                f"Component: {component.component_id} ({component.name})",
                f"Rating: {component.total_dose_rads} rads",
                f"Mission dose: {mission_dose} rads",
                f"Margin: {margin}x",
                f"Required: {required_dose} rads",
                "ECSS-Q-ST-80C requires 2x margin"
            ],
            rule="ecss_q_st_80c_radiation_margin"
        )

    return True, ProofObject(
        conclusion=f"Component {component.name} meets radiation tolerance with margin",
        premises=[f"{component.total_dose_rads} rads >= {required_dose} rads"],
        rule="ecss_q_st_80c_radiation_margin"
    )


def check_seu_protection(component: RadiationTolerance) -> Tuple[bool, ProofObject]:
    """
    Critical components must have SEU (Single Event Upset) protection.

    ECSS-Q-ST-80C: Safety-critical components require SEU immunity or mitigation
    (EDAC, TMR, scrubbing) and latchup protection.

    Falsifies if: neither SEU immune nor latchup protected
    """
    if not component.seu_immune and not component.latchup_protected:
        return False, ProofObject(
            conclusion=f"VIOLATION: Component {component.name} lacks SEU/latchup protection",
            premises=[
                f"Component: {component.component_id}",
                f"SEU immune: {component.seu_immune}",
                f"Latchup protected: {component.latchup_protected}",
                "ECSS-Q-ST-80C requires SEU protection for critical components"
            ],
            rule="ecss_q_st_80c_seu_protection"
        )

    return True, ProofObject(
        conclusion=f"Component {component.name} has SEU/latchup protection",
        premises=[
            f"SEU immune: {component.seu_immune}",
            f"Latchup protected: {component.latchup_protected}"
        ],
        rule="ecss_q_st_80c_seu_protection"
    )


def check_orbit_validity(orbit: OrbitParameters) -> Tuple[bool, ProofObject]:
    """
    Orbital parameters must be physically valid (bound orbit: e < 1, a > 0).

    Orbital mechanics: For a bound (closed) orbit, eccentricity must be < 1.
    Semi-major axis must be positive. Escape trajectory has e >= 1.

    Falsifies if: eccentricity >= 1 or semi_major_axis <= 0
    """
    escape_e = orbital_escape_eccentricity()

    if orbit.semi_major_axis <= Fraction(0):
        return False, ProofObject(
            conclusion=f"VIOLATION: Semi-major axis {orbit.semi_major_axis} km not positive",
            premises=[
                f"Semi-major axis: {orbit.semi_major_axis} km",
                "Semi-major axis must be positive for valid orbit"
            ],
            rule="orbital_mechanics_bound_orbit"
        )

    if orbit.eccentricity < Fraction(0):
        return False, ProofObject(
            conclusion=f"VIOLATION: Eccentricity {orbit.eccentricity} is negative",
            premises=[
                f"Eccentricity: {orbit.eccentricity}",
                "Eccentricity must be non-negative"
            ],
            rule="orbital_mechanics_bound_orbit"
        )

    if orbit.eccentricity >= escape_e:
        return False, ProofObject(
            conclusion=f"VIOLATION: Eccentricity {orbit.eccentricity} >= {escape_e} (escape/hyperbolic trajectory, not bound orbit)",
            premises=[
                f"Eccentricity: {orbit.eccentricity}",
                f"Escape threshold: {escape_e}",
                "Bound orbit requires e < 1"
            ],
            rule="orbital_mechanics_bound_orbit"
        )

    return True, ProofObject(
        conclusion=f"Orbit parameters valid: bound orbit (e={orbit.eccentricity}, a={orbit.semi_major_axis} km)",
        premises=[
            f"Eccentricity: {orbit.eccentricity} < {escape_e}",
            f"Semi-major axis: {orbit.semi_major_axis} km > 0"
        ],
        rule="orbital_mechanics_bound_orbit"
    )
