"""D_PHYSICS invariant checks."""

from typing import Tuple, List, Dict
from fractions import Fraction

from axioms.logic import ProofObject
from axioms.classical_mechanics import Vector3, Particle
from src.domains.d_physics.implementation import (
    SystemState,
    ActuatorState,
    check_energy_conservation,
    check_momentum_conservation,
    check_equation_of_motion_satisfied,
    check_joint_torque_limits,
    check_numerical_stability,
)


def check_energy_conservation_invariant(states: List[SystemState]) -> Tuple[bool, ProofObject]:
    """Invariant: Total mechanical energy is conserved in isolated systems."""
    return check_energy_conservation(states)


def check_momentum_conservation_invariant(states: List[SystemState]) -> Tuple[bool, ProofObject]:
    """Invariant: Total linear momentum is conserved in isolated systems."""
    return check_momentum_conservation(states)


def check_equation_of_motion_invariant(force: Vector3,
                                       mass: Fraction,
                                       acceleration: Vector3) -> Tuple[bool, ProofObject]:
    """Invariant: F = ma is satisfied at all times."""
    return check_equation_of_motion_satisfied(force, mass, acceleration)


def check_joint_torque_limits_invariant(actuators: List[ActuatorState],
                                        limits: Dict[str, Fraction]) -> Tuple[bool, ProofObject]:
    """Invariant: Joint torques stay within actuator limits."""
    all_within, violations, proof = check_joint_torque_limits(actuators, limits)
    
    final_proof = ProofObject(
        rule="JointTorqueLimitsInvariant",
        premises=proof.premises + [f"violations={violations}"],
        conclusion=f"all_within={all_within}"
    )
    
    return all_within, final_proof


def check_numerical_stability_invariant(dt: Fraction,
                                        max_frequency: Fraction) -> Tuple[bool, ProofObject]:
    """Invariant: Numerical integration respects stability criteria."""
    return check_numerical_stability(dt, max_frequency)


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    # Test energy conservation
    p1 = Particle(
        mass=Fraction(1),
        position=Vector3(Fraction(0), Fraction(0), Fraction(0)),
        velocity=Vector3(Fraction(1), Fraction(0), Fraction(0))
    )
    p2 = Particle(
        mass=Fraction(1),
        position=Vector3(Fraction(1), Fraction(0), Fraction(0)),
        velocity=Vector3(Fraction(-1), Fraction(0), Fraction(0))
    )
    
    state1 = SystemState(time=Fraction(0), particles=[p1, p2])
    state2 = SystemState(time=Fraction(1), particles=[p1, p2])  # Same energy
    
    conserved, _ = check_energy_conservation([state1, state2])
    results["energy_conservation"] = "PASS" if conserved else "FAIL"
    
    # Test equation of motion
    force = Vector3(Fraction(10), Fraction(0), Fraction(0))
    mass = Fraction(2)
    expected_acc = Vector3(Fraction(5), Fraction(0), Fraction(0))
    
    satisfied, _ = check_equation_of_motion_satisfied(force, mass, expected_acc)
    results["equation_of_motion"] = "PASS" if satisfied else "FAIL"
    
    # Test joint torque limits
    actuators = [
        ActuatorState("joint1", Fraction(0), Fraction(5)),
        ActuatorState("joint2", Fraction(0), Fraction(15)),
    ]
    limits = {"joint1": Fraction(10), "joint2": Fraction(10)}
    
    all_within, _, _ = check_joint_torque_limits(actuators, limits)
    results["joint_torque_limits"] = "PASS" if all_within else "FAIL"
    
    # Test numerical stability
    stable, _ = check_numerical_stability(Fraction(1, 60), Fraction(30))
    results["numerical_stability"] = "PASS" if stable else "FAIL"
    
    return results
