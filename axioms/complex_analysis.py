"""Complex analysis — Complex numbers, holomorphic functions, residues.

Implements complex arithmetic using pairs of Fractions (real, imag).
All operations return (result, ProofObject) pairs.

Mathematical foundation: Ahlfors, "Complex Analysis"
Biblical: Ezekiel 1:16 — "Their appearance and their work was as it were a wheel in the middle of a wheel."
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import List, Tuple, Callable, Optional

from axioms.logic import ProofObject


@dataclass(frozen=True)
class ComplexFraction:
    """Complex number as (real, imag) pair of Fractions.
    
    Represents a + bi where a, b ∈ ℚ (Fractions).
    """
    real: Fraction
    imag: Fraction
    
    def __add__(self, other: ComplexFraction) -> ComplexFraction:
        return ComplexFraction(self.real + other.real, self.imag + other.imag)
    
    def __sub__(self, other: ComplexFraction) -> ComplexFraction:
        return ComplexFraction(self.real - other.real, self.imag - other.imag)
    
    def __mul__(self, other: ComplexFraction) -> ComplexFraction:
        # (a+bi)(c+di) = (ac-bd) + (ad+bc)i
        return ComplexFraction(
            self.real * other.real - self.imag * other.imag,
            self.real * other.imag + self.imag * other.real
        )
    
    def conjugate(self) -> ComplexFraction:
        """Complex conjugate: a + bi → a - bi."""
        return ComplexFraction(self.real, -self.imag)
    
    def modulus_squared(self) -> Fraction:
        """|z|² = a² + b²."""
        return self.real * self.real + self.imag * self.imag
    
    def inverse(self) -> ComplexFraction:
        """1/z = z̄ / |z|²."""
        mod_sq = self.modulus_squared()
        if mod_sq == 0:
            raise ZeroDivisionError("Cannot invert zero complex number")
        conj = self.conjugate()
        return ComplexFraction(conj.real / mod_sq, conj.imag / mod_sq)
    
    def __truediv__(self, other: ComplexFraction) -> ComplexFraction:
        return self * other.inverse()
    
    def __repr__(self) -> str:
        if self.imag >= 0:
            return f"{self.real}+{self.imag}i"
        return f"{self.real}{self.imag}i"


def cauchy_riemann_check(u: Callable[[Fraction, Fraction], Fraction],
                          v: Callable[[Fraction, Fraction], Fraction],
                          point: Tuple[Fraction, Fraction],
                          h: Fraction) -> Tuple[bool, ProofObject]:
    """Verify Cauchy-Riemann equations at a point: ∂u/∂x = ∂v/∂y and ∂u/∂y = -∂v/∂x.
    
    For f(z) = u(x,y) + i*v(x,y) to be holomorphic, the partial derivatives
    must satisfy the Cauchy-Riemann equations.
    
    Args:
        u: Real part function u(x, y)
        v: Imaginary part function v(x, y)
        point: (x, y) where to check
        h: Step size for finite differences
    
    Returns:
        (satisfied, proof) where satisfied indicates if C-R equations hold
    """
    x, y = point
    
    # Compute partial derivatives using finite differences
    du_dx = (u(x + h, y) - u(x - h, y)) / (2 * h)
    du_dy = (u(x, y + h) - u(x, y - h)) / (2 * h)
    dv_dx = (v(x + h, y) - v(x - h, y)) / (2 * h)
    dv_dy = (v(x, y + h) - v(x, y - h)) / (2 * h)
    
    # Check C-R equations
    cr1 = du_dx - dv_dy  # Should be 0
    cr2 = du_dy + dv_dx  # Should be 0
    
    tolerance = Fraction(1, 1000)
    
    satisfied = abs(cr1) < tolerance and abs(cr2) < tolerance
    
    proof = ProofObject(
        conclusion=f"Cauchy-Riemann equations {'satisfied' if satisfied else 'NOT satisfied'} at ({x}, {y})",
        premises=[
            f"∂u/∂x = {du_dx}, ∂v/∂y = {dv_dy}",
            f"∂u/∂y = {du_dy}, ∂v/∂x = {dv_dx}",
        ],
        rule="cauchy_riemann_check",
        derivation=[
            f"∂u/∂x - ∂v/∂y = {cr1}",
            f"∂u/∂y + ∂v/∂x = {cr2}",
        ]
    )
    return satisfied, proof


def contour_integral(f: Callable[[ComplexFraction], ComplexFraction],
                     path_points: List[ComplexFraction]) -> Tuple[ComplexFraction, ProofObject]:
    """Trapezoidal sum over discrete path for contour integral ∮ f(z) dz.
    
    Approximates ∫_γ f(z) dz by summing f(z_k) * Δz_k along the path.
    
    Args:
        f: Complex function to integrate
        path_points: List of points along the contour
    
    Returns:
        (integral_value, proof)
    """
    if len(path_points) < 2:
        proof = ProofObject(
            conclusion="Contour integral = 0 (degenerate path)",
            premises=["Path has fewer than 2 points"],
            rule="contour_degenerate",
            derivation=[]
        )
        return ComplexFraction(Fraction(0), Fraction(0)), proof
    
    total = ComplexFraction(Fraction(0), Fraction(0))
    
    for i in range(len(path_points) - 1):
        z_k = path_points[i]
        z_next = path_points[i + 1]
        dz = z_next - z_k
        f_z = f(z_k)
        total = total + f_z * dz
    
    proof = ProofObject(
        conclusion=f"Contour integral ≈ {total}",
        premises=[f"Path with {len(path_points)} points"],
        rule="contour_trapezoidal",
        derivation=[f"Sum of f(z_k) * Δz_k over {len(path_points)-1} segments"]
    )
    return total, proof


def residue_at_pole(f: Callable[[ComplexFraction], ComplexFraction],
                     pole: ComplexFraction,
                     radius: Fraction,
                     n_points: int = 100) -> Tuple[ComplexFraction, ProofObject]:
    """Numerical residue via contour integral around pole.
    
    For a simple pole at z₀: Res(f, z₀) = (1/2πi) ∮ f(z) dz
    
    Computes the integral around a circle of given radius centered at pole.
    
    Args:
        f: Complex function
        pole: Location of the pole
        radius: Radius of contour circle
        n_points: Number of points for discretization
    
    Returns:
        (residue_estimate, proof)
    """
    from math import pi, cos, sin
    
    # Generate points on circle: z = pole + radius * e^(iθ)
    path_points = []
    for k in range(n_points):
        theta = 2 * pi * k / n_points
        # Approximate e^(iθ) = cos(θ) + i*sin(θ) using Fraction approximations
        # Use simple rational approximations
        cos_approx = Fraction(int(cos(theta) * 1000), 1000)
        sin_approx = Fraction(int(sin(theta) * 1000), 1000)
        point = pole + ComplexFraction(radius * cos_approx, radius * sin_approx)
        path_points.append(point)
    
    # Close the path
    path_points.append(path_points[0])
    
    # Compute contour integral
    integral, _ = contour_integral(f, path_points)
    
    # Residue = integral / (2πi)
    # 1/i = -i, so integral / (2πi) = -i * integral / (2π)
    two_pi = Fraction(6283, 1000)  # Approximation of 2π
    residue = ComplexFraction(
        integral.imag / two_pi,  # Real part comes from imag of integral
        -integral.real / two_pi   # Imag part comes from -real of integral
    )
    
    proof = ProofObject(
        conclusion=f"Residue at {pole} ≈ {residue}",
        premises=[f"Contour integral = {integral}", f"Radius = {radius}"],
        rule="residue_numerical",
        derivation=[f"Computed via {n_points}-point discretization of circular contour"]
    )
    return residue, proof


def fundamental_theorem_of_algebra_witness(coefficients: List[Fraction],
                                           max_iterations: int = 100) -> Tuple[ComplexFraction, ProofObject]:
    """For polynomial with Fraction coefficients, find approximate root via Newton's method.
    
    Fundamental Theorem of Algebra: Every non-constant polynomial has at least one root.
    
    This function constructs a witness by finding an approximate root.
    
    Args:
        coefficients: [a₀, a₁, ..., aₙ] for polynomial a₀ + a₁z + ... + aₙzⁿ
        max_iterations: Maximum Newton iterations
    
    Returns:
        (approximate_root, proof)
    """
    if len(coefficients) < 2:
        proof = ProofObject(
            conclusion="No root found (constant polynomial)",
            premises=["Degree < 1"],
            rule="ftoa_constant",
            derivation=[]
        )
        return ComplexFraction(Fraction(0), Fraction(0)), proof
    
    def poly(z: ComplexFraction) -> ComplexFraction:
        """Evaluate polynomial at z."""
        result = ComplexFraction(Fraction(0), Fraction(0))
        power = ComplexFraction(Fraction(1), Fraction(0))  # z^0 = 1
        for coeff in coefficients:
            result = result + ComplexFraction(coeff, Fraction(0)) * power
            power = power * z
        return result
    
    def poly_derivative(z: ComplexFraction) -> ComplexFraction:
        """Evaluate derivative at z."""
        result = ComplexFraction(Fraction(0), Fraction(0))
        power = ComplexFraction(Fraction(1), Fraction(0))
        for i, coeff in enumerate(coefficients[1:], 1):
            result = result + ComplexFraction(coeff * i, Fraction(0)) * power
            power = power * z
        return result
    
    # Initial guess
    z = ComplexFraction(Fraction(1), Fraction(1))
    
    for i in range(max_iterations):
        pz = poly(z)
        dpz = poly_derivative(z)
        
        # Check if converged
        if pz.modulus_squared() < Fraction(1, 1000000):
            proof = ProofObject(
                conclusion=f"Root found: z ≈ {z}",
                premises=[f"Newton's method converged in {i+1} iterations"],
                rule="ftoa_witness",
                derivation=[f"Final |p(z)|² = {pz.modulus_squared()}"]
            )
            return z, proof
        
        # Newton step: z_{n+1} = z_n - p(z_n)/p'(z_n)
        if dpz.modulus_squared() == 0:
            break
        z = z - pz / dpz
    
    # Return best approximation
    proof = ProofObject(
        conclusion=f"Approximate root: z ≈ {z}",
        premises=[f"Newton's method completed {max_iterations} iterations"],
        rule="ftoa_approximation",
        derivation=[f"Final |p(z)|² = {poly(z).modulus_squared()}"]
    )
    return z, proof
