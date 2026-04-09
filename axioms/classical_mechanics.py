"""Classical Mechanics — Lagrangian, Hamiltonian, Newtonian dynamics.

Implements the mathematical foundations of physical motion using
exact Fraction arithmetic. No floats. All operations return
(result, ProofObject) pairs.

Mathematical foundation: Goldstein, "Classical Mechanics"
Biblical: Psalm 19:1 — "The heavens declare the glory of God;
the skies proclaim the work of his hands."
"""

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple, List

from axioms.logic import ProofObject


@dataclass(frozen=True)
class Vector3:
    """3D vector using exact Fraction arithmetic."""
    x: Fraction
    y: Fraction
    z: Fraction
    
    def add(self, other: 'Vector3') -> 'Vector3':
        """Vector addition: a + b"""
        return Vector3(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z
        )
    
    def sub(self, other: 'Vector3') -> 'Vector3':
        """Vector subtraction: a - b"""
        return Vector3(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z
        )
    
    def scale(self, scalar: Fraction) -> 'Vector3':
        """Scalar multiplication: s * v"""
        return Vector3(
            self.x * scalar,
            self.y * scalar,
            self.z * scalar
        )
    
    def dot(self, other: 'Vector3') -> Fraction:
        """Dot product: a · b"""
        return (self.x * other.x + 
                self.y * other.y + 
                self.z * other.z)
    
    def cross(self, other: 'Vector3') -> 'Vector3':
        """Cross product: a × b"""
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def magnitude_squared(self) -> Fraction:
        """Squared magnitude: |v|² (avoids sqrt → float)."""
        return self.x * self.x + self.y * self.y + self.z * self.z
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector3):
            return False
        return (self.x == other.x and 
                self.y == other.y and 
                self.z == other.z)


@dataclass(frozen=True)
class Particle:
    """Classical particle with mass, position, velocity."""
    mass: Fraction
    position: Vector3
    velocity: Vector3
    
    def momentum(self) -> Vector3:
        """Linear momentum: p = m * v"""
        return self.velocity.scale(self.mass)
    
    def kinetic_energy(self) -> Fraction:
        """Kinetic energy: T = (1/2) * m * v²"""
        v_squared = self.velocity.magnitude_squared()
        return Fraction(1, 2) * self.mass * v_squared


def newton_second_law(force: Vector3, mass: Fraction) -> Tuple[Vector3, ProofObject]:
    """Newton's Second Law: F = ma → a = F/m
    
    Returns acceleration vector with proof witness.
    """
    if mass == Fraction(0):
        raise ValueError("Mass cannot be zero")
    
    acceleration = force.scale(Fraction(1) / mass)
    
    proof = ProofObject(
        rule="NewtonSecondLaw",
        premises=[
            f"F=({force.x},{force.y},{force.z})",
            f"m={mass}"
        ],
        conclusion=f"a=({acceleration.x},{acceleration.y},{acceleration.z})"
    )
    
    return acceleration, proof


def kinetic_energy(particle: Particle) -> Tuple[Fraction, ProofObject]:
    """Kinetic energy: T = (1/2) * m * v·v
    
    Uses Fraction(1, 2) for exact arithmetic.
    """
    T = particle.kinetic_energy()
    
    proof = ProofObject(
        rule="KineticEnergy",
        premises=[
            f"m={particle.mass}",
            f"|v|²={particle.velocity.magnitude_squared()}"
        ],
        conclusion=f"T={T}"
    )
    
    return T, proof


def gravitational_force(m1: Fraction, m2: Fraction, r_squared: Fraction, 
                        G: Fraction) -> Tuple[Fraction, ProofObject]:
    """Newton's Law of Universal Gravitation: F = G * m1 * m2 / r²
    
    Args:
        m1: Mass of first body
        m2: Mass of second body  
        r_squared: Squared distance between bodies (avoids sqrt)
        G: Gravitational constant (as Fraction)
    
    Returns:
        Force magnitude (Fraction) and proof
    """
    if r_squared == Fraction(0):
        raise ValueError("Distance cannot be zero")
    
    F = G * m1 * m2 / r_squared
    
    proof = ProofObject(
        rule="NewtonGravitation",
        premises=[
            f"m1={m1}",
            f"m2={m2}",
            f"r²={r_squared}",
            f"G={G}"
        ],
        conclusion=f"F={F}"
    )
    
    return F, proof


def lagrangian(kinetic: Fraction, potential: Fraction) -> Tuple[Fraction, ProofObject]:
    """Lagrangian: L = T - V
    
    The Lagrangian is the fundamental function from which equations
    of motion are derived via the Euler-Lagrange equation.
    """
    L = kinetic - potential
    
    proof = ProofObject(
        rule="Lagrangian",
        premises=[
            f"T={kinetic}",
            f"V={potential}"
        ],
        conclusion=f"L={L}"
    )
    
    return L, proof


def hamiltonian(kinetic: Fraction, potential: Fraction) -> Tuple[Fraction, ProofObject]:
    """Hamiltonian: H = T + V
    
    Represents total energy of the system. For conservative systems,
    H is conserved (constant in time).
    """
    H = kinetic + potential
    
    proof = ProofObject(
        rule="Hamiltonian",
        premises=[
            f"T={kinetic}",
            f"V={potential}"
        ],
        conclusion=f"H={H}"
    )
    
    return H, proof


def conservation_of_energy(T1: Fraction, V1: Fraction,
                           T2: Fraction, V2: Fraction) -> Tuple[bool, ProofObject]:
    """Verify conservation of mechanical energy.
    
    For conservative systems: T1 + V1 = T2 + V2
    
    Returns True if energy is conserved within exact Fraction arithmetic.
    """
    E1 = T1 + V1
    E2 = T2 + V2
    conserved = (E1 == E2)
    
    proof = ProofObject(
        rule="EnergyConservation",
        premises=[
            f"E1=T1+V1={T1}+{V1}={E1}",
            f"E2=T2+V2={T2}+{V2}={E2}"
        ],
        conclusion=f"conserved={conserved}"
    )
    
    return conserved, proof


def conservation_of_momentum(p_before: Vector3, p_after: Vector3) -> Tuple[bool, ProofObject]:
    """Verify conservation of linear momentum.
    
    For isolated systems: p_before = p_after
    
    Returns True if momentum is conserved (component-wise equality).
    """
    conserved = (p_before == p_after)
    
    proof = ProofObject(
        rule="MomentumConservation",
        premises=[
            f"p_before=({p_before.x},{p_before.y},{p_before.z})",
            f"p_after=({p_after.x},{p_after.y},{p_after.z})"
        ],
        conclusion=f"conserved={conserved}"
    )
    
    return conserved, proof


def euler_lagrange_residual(dL_dq: Fraction, d_dt_dL_dqdot: Fraction) -> Tuple[Fraction, ProofObject]:
    """Euler-Lagrange residual: ε = d/dt(∂L/∂q̇) - ∂L/∂q
    
    The Euler-Lagrange equation states:
        d/dt(∂L/∂q̇) - ∂L/∂q = 0
    
    Returns the residual. Zero means the equation is satisfied.
    
    Args:
        dL_dq: Partial derivative of L with respect to q
        d_dt_dL_dqdot: Time derivative of ∂L/∂q̇
    
    Returns:
        (residual, proof) where residual = 0 iff E-L satisfied
    """
    residual = d_dt_dL_dqdot - dL_dq
    
    proof = ProofObject(
        rule="EulerLagrange",
        premises=[
            f"∂L/∂q={dL_dq}",
            f"d/dt(∂L/∂q̇)={d_dt_dL_dqdot}"
        ],
        conclusion=f"ε={residual}, satisfied={residual==Fraction(0)}"
    )
    
    return residual, proof


def angular_momentum(position: Vector3, momentum: Vector3) -> Tuple[Vector3, ProofObject]:
    """Angular momentum: L = r × p
    
    Returns the angular momentum vector (cross product of position and momentum).
    """
    L = position.cross(momentum)
    
    proof = ProofObject(
        rule="AngularMomentum",
        premises=[
            f"r=({position.x},{position.y},{position.z})",
            f"p=({momentum.x},{momentum.y},{momentum.z})"
        ],
        conclusion=f"L=({L.x},{L.y},{L.z})"
    )
    
    return L, proof


def work_energy_theorem(work: Fraction, delta_KE: Fraction) -> Tuple[bool, ProofObject]:
    """Verify the work-energy theorem: W = ΔK
    
    The net work done on a particle equals its change in kinetic energy.
    
    Returns True if W = ΔK exactly.
    """
    satisfied = (work == delta_KE)
    
    proof = ProofObject(
        rule="WorkEnergyTheorem",
        premises=[
            f"W={work}",
            f"ΔK={delta_KE}"
        ],
        conclusion=f"satisfied={satisfied}"
    )
    
    return satisfied, proof
