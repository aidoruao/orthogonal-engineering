#!/usr/bin/env python3
"""Physics Domain Invariants — Conservation laws, physical constraints.

Standards:
- Conservation of momentum
- Conservation of energy
- Speed of light limit
- Non-negative mass

Falsifies if:
- Momentum not conserved in isolated system
- Energy not conserved (elastic collision)
- Superluminal velocity
- Negative mass
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import PhysicalObject, PhysicalSystem, Collision


def check_mass_non_negative(obj: PhysicalObject) -> Tuple[bool, ProofObject]:
    """Mass must be non-negative.

    Falsifies if: obj.mass < 0.
    """
    if obj.mass < Fraction(0):
        return False, ProofObject(
            conclusion=f"VIOLATION: Negative mass {obj.mass}",
            premises=[f"Object: {obj.object_id}", f"Mass: {obj.mass}"],
            rule="physical_mass_non_negative"
        )
    
    return True, ProofObject(
        conclusion="Mass non-negative",
        premises=[f"Mass: {obj.mass}"],
        rule="mass_valid"
    )


def check_momentum_conservation(collision: Collision) -> Tuple[bool, ProofObject]:
    """Momentum conserved in all collisions (isolated system).

    Falsifies if: collision.momentum_conserved is False.
    """
    if not collision.momentum_conserved:
        return False, ProofObject(
            conclusion="VIOLATION: Momentum not conserved in collision",
            premises=[
                f"Collision: {collision.collision_id}",
                f"Objects: {collision.object_a}, {collision.object_b}"
            ],
            rule="conservation_of_momentum"
        )
    
    return True, ProofObject(
        conclusion="Momentum conserved",
        premises=[f"Collision: {collision.collision_id}"],
        rule="momentum_conserved"
    )


def check_energy_conservation_elastic(collision: Collision) -> Tuple[bool, ProofObject]:
    """Energy conserved in elastic collisions.

    Falsifies if: collision.elastic is True and energy_conserved is False.
    """
    if collision.elastic and not collision.energy_conserved:
        return False, ProofObject(
            conclusion="VIOLATION: Energy not conserved in elastic collision",
            premises=[
                f"Collision: {collision.collision_id}",
                "Type: Elastic",
                "Energy conserved: False"
            ],
            rule="conservation_of_energy"
        )
    
    return True, ProofObject(
        conclusion="Energy conserved (or inelastic)",
        premises=[f"Elastic: {collision.elastic}"],
        rule="energy_conserved"
    )


def check_speed_limit(obj: PhysicalObject, speed_limit: Fraction) -> Tuple[bool, ProofObject]:
    """Speed cannot exceed limit (e.g., speed of light).

    Falsifies if: object speed squared exceeds limit squared.
    """
    # Compare squared speeds to avoid sqrt
    v_sq = obj.speed()
    c_sq = speed_limit * speed_limit
    
    if v_sq > c_sq:
        return False, ProofObject(
            conclusion=f"VIOLATION: Object speed exceeds limit",
            premises=[
                f"Object: {obj.object_id}",
                f"Speed²: {v_sq}",
                f"Limit²: {c_sq}"
            ],
            rule="relativistic_speed_limit"
        )
    
    return True, ProofObject(
        conclusion="Speed within limit",
        premises=[f"Speed²: {v_sq}", f"Limit²: {c_sq}"],
        rule="speed_compliant"
    )


def check_system_mass_conservation(system: PhysicalSystem, initial_mass: Fraction) -> Tuple[bool, ProofObject]:
    """Mass conserved in isolated system.

    Falsifies if: system total mass differs from initial_mass.
    """
    current = system.total_mass()
    if current != initial_mass:
        return False, ProofObject(
            conclusion=f"VIOLATION: Mass not conserved",
            premises=[
                f"System: {system.system_id}",
                f"Initial: {initial_mass}",
                f"Current: {current}"
            ],
            rule="conservation_of_mass"
        )
    
    return True, ProofObject(
        conclusion="Mass conserved",
        premises=[f"Total mass: {current}"],
        rule="mass_conserved"
    )
