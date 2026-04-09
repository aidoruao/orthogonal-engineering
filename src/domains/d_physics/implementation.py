"""D_PHYSICS implementation — Physics Simulation & Dynamics.

Bridges axioms/classical_mechanics.py to practical domain invariants.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, List, Dict
from fractions import Fraction

from axioms.logic import ProofObject
from axioms.classical_mechanics import (
    Vector3,
    Particle,
    kinetic_energy,
    conservation_of_energy,
    conservation_of_momentum,
    newton_second_law,
)


@dataclass(frozen=True)
class SystemState:
    """Complete state of a physical system at one instant."""
    time: Fraction
    particles: List[Particle]
    
    def total_kinetic_energy(self) -> Tuple[Fraction, ProofObject]:
        """Sum kinetic energy of all particles."""
        total = Fraction(0)
        for p in self.particles:
            ke, _ = kinetic_energy(p)
            total += ke
        
        proof = ProofObject(
            rule="TotalKineticEnergy",
            premises=[f"n_particles={len(self.particles)}"],
            conclusion=f"total_KE={total}"
        )
        
        return total, proof
    
    def total_momentum(self) -> Tuple[Vector3, ProofObject]:
        """Sum linear momentum of all particles."""
        total = Vector3(Fraction(0), Fraction(0), Fraction(0))
        for p in self.particles:
            total = total.add(p.momentum())
        
        proof = ProofObject(
            rule="TotalMomentum",
            premises=[f"n_particles={len(self.particles)}"],
            conclusion=f"total_p=({total.x},{total.y},{total.z})"
        )
        
        return total, proof


@dataclass(frozen=True)
class JointConstraint:
    """Constraint on a joint in a mechanical system."""
    joint_id: str
    min_position: Fraction
    max_position: Fraction
    max_torque: Fraction


@dataclass(frozen=True)
class ActuatorState:
    """State of a joint actuator."""
    joint_id: str
    position: Fraction
    torque: Fraction


def check_energy_conservation(states: List[SystemState],
                              tolerance: Fraction = Fraction(0)) -> Tuple[bool, ProofObject]:
    """Check energy conservation across system states.
    
    Args:
        states: List of system states at different times
        tolerance: Allowed deviation (0 for exact conservation)
    
    Returns:
        (conserved, proof)
    """
    if len(states) < 2:
        return True, ProofObject(
            rule="EnergyConservation",
            premises=["insufficient states"],
            conclusion="n/a"
        )
    
    # Get total energy for each state
    energies = []
    for state in states:
        ke, _ = state.total_kinetic_energy()
        # Potential energy would come from field
        energies.append(ke)  # Simplified: just kinetic for now
    
    # Check if all energies are equal within tolerance
    first = energies[0]
    all_equal = all(abs(e - first) <= tolerance for e in energies)
    
    proof = ProofObject(
        rule="EnergyConservation",
        premises=[f"energies={energies}", f"tolerance={tolerance}"],
        conclusion=f"conserved={all_equal}"
    )
    
    return all_equal, proof


def check_momentum_conservation(states: List[SystemState]) -> Tuple[bool, ProofObject]:
    """Check momentum conservation across system states."""
    if len(states) < 2:
        return True, ProofObject(
            rule="MomentumConservation",
            premises=["insufficient states"],
            conclusion="n/a"
        )
    
    # Get total momentum for each state
    momenta = []
    for state in states:
        p, _ = state.total_momentum()
        momenta.append(p)
    
    # Check if all momenta are equal
    first = momenta[0]
    all_equal = all(p == first for p in momenta)
    
    proof = ProofObject(
        rule="MomentumConservation",
        premises=[f"momenta_count={len(momenta)}"],
        conclusion=f"conserved={all_equal}"
    )
    
    return all_equal, proof


def check_equation_of_motion_satisfied(force: Vector3,
                                       mass: Fraction,
                                       acceleration: Vector3) -> Tuple[bool, ProofObject]:
    """Check if F = ma is satisfied.
    
    Computes expected acceleration from force and mass,
    compares to measured acceleration.
    """
    if mass == Fraction(0):
        return False, ProofObject(
            rule="EquationOfMotion",
            premises=["zero mass"],
            conclusion="invalid"
        )
    
    expected_acc, _ = newton_second_law(force, mass)
    satisfied = (acceleration == expected_acc)
    
    proof = ProofObject(
        rule="EquationOfMotion",
        premises=[
            f"F=({force.x},{force.y},{force.z})",
            f"m={mass}",
            f"expected_a=({expected_acc.x},{expected_acc.y},{expected_acc.z})",
            f"measured_a=({acceleration.x},{acceleration.y},{acceleration.z})"
        ],
        conclusion=f"satisfied={satisfied}"
    )
    
    return satisfied, proof


def check_joint_torque_limits(actuators: List[ActuatorState],
                              limits: Dict[str, Fraction]) -> Tuple[bool, List[str], ProofObject]:
    """Check if all joint torques are within limits.
    
    Args:
        actuators: List of actuator states
        limits: Dict mapping joint_id to max torque
    
    Returns:
        (all_within, violations, proof)
    """
    violations = []
    
    for actuator in actuators:
        if actuator.joint_id in limits:
            limit = limits[actuator.joint_id]
            if abs(actuator.torque) > limit:
                violations.append(
                    f"Joint {actuator.joint_id}: torque {actuator.torque} exceeds limit {limit}"
                )
    
    all_within = len(violations) == 0
    
    proof = ProofObject(
        rule="JointTorqueLimits",
        premises=[
            f"n_actuators={len(actuators)}",
            f"violations={len(violations)}"
        ],
        conclusion=f"all_within={all_within}"
    )
    
    return all_within, violations, proof


@dataclass(frozen=True)
class Collision:
    """Collision event between two bodies."""
    body_a: str
    body_b: str
    impulse: Vector3


def check_collision_momentum_conservation(momentum_before: Vector3,
                                         momentum_after: Vector3,
                                         external_impulse: Vector3) -> Tuple[bool, ProofObject]:
    """Check if collision conserves momentum (accounting for external impulses).
    
    momentum_after should equal momentum_before + external_impulse
    """
    expected = momentum_before.add(external_impulse)
    conserved = (momentum_after == expected)
    
    proof = ProofObject(
        rule="CollisionMomentum",
        premises=[
            f"p_before=({momentum_before.x},{momentum_before.y},{momentum_before.z})",
            f"p_after=({momentum_after.x},{momentum_after.y},{momentum_after.z})",
            f"external=({external_impulse.x},{external_impulse.y},{external_impulse.z})"
        ],
        conclusion=f"conserved={conserved}"
    )
    
    return conserved, proof


def check_numerical_stability(dt: Fraction,
                             max_frequency: Fraction) -> Tuple[bool, ProofObject]:
    """Check if time step is stable for explicit integration.
    
    For stability: dt < 2 / max_frequency (simplified criterion)
    """
    if max_frequency == Fraction(0):
        return True, ProofObject(
            rule="NumericalStability",
            premises=["zero frequency"],
            conclusion="stable"
        )
    
    # Simplified stability limit
    stability_limit = Fraction(2) / max_frequency
    stable = dt < stability_limit
    
    proof = ProofObject(
        rule="NumericalStability",
        premises=[
            f"dt={dt}",
            f"max_freq={max_frequency}",
            f"stability_limit={stability_limit}"
        ],
        conclusion=f"stable={stable}"
    )
    
    return stable, proof
