"""Synthetic differential geometry — Infinitesimals, microlinear spaces.

Implements SDG using the Kock-Lawvere axiom with nilsquare infinitesimals.
All operations return (result, ProofObject) pairs.

Mathematical foundation: Kock, "Synthetic Differential Geometry"
Biblical: Genesis 1:1 — "In the beginning God created the heavens and the earth." (Creation from infinitesimal to infinite.)
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Callable, Tuple, List

from axioms.logic import ProofObject


@dataclass(frozen=True)
class Infinitesimal:
    """A nilsquare infinitesimal d where d² = 0.
    
    In SDG, the Kock-Lawvere axiom states that for any function f: D → R
    where D = {d ∈ R | d² = 0}, there exist unique a, b ∈ R such that
    f(d) = a + b·d for all d ∈ D.
    
    This implements d as a symbolic quantity with the property d² = 0.
    """
    coefficient: Fraction
    
    def __post_init__(self):
        # Ensure coefficient is a Fraction
        if isinstance(self.coefficient, int):
            object.__setattr__(self, 'coefficient', Fraction(self.coefficient))
    
    def __add__(self, other):
        if isinstance(other, Infinitesimal):
            return Infinitesimal(self.coefficient + other.coefficient)
        # Adding to a regular number creates a Microquantity
        return Microquantity(other, self.coefficient)
    
    def __radd__(self, other):
        return self.__add__(other)
    
    def __mul__(self, other):
        # d² = 0 for infinitesimals
        if isinstance(other, Infinitesimal):
            return Microquantity(Fraction(0), Fraction(0))  # Zero
        return Infinitesimal(self.coefficient * other)
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __repr__(self):
        return f"{self.coefficient}·d"


@dataclass(frozen=True)
class Microquantity:
    """A microquantity: a + b·d where d² = 0.
    
    Represents an element of R ⊕ R·d, the ring of dual numbers.
    """
    standard_part: Fraction  # a
    infinitesimal_part: Fraction  # b (coefficient of d)
    
    def __post_init__(self):
        # Ensure both are Fractions
        if isinstance(self.standard_part, int):
            object.__setattr__(self, 'standard_part', Fraction(self.standard_part))
        if isinstance(self.infinitesimal_part, int):
            object.__setattr__(self, 'infinitesimal_part', Fraction(self.infinitesimal_part))
    
    def __add__(self, other):
        if isinstance(other, Microquantity):
            return Microquantity(
                self.standard_part + other.standard_part,
                self.infinitesimal_part + other.infinitesimal_part
            )
        elif isinstance(other, Infinitesimal):
            return Microquantity(self.standard_part, self.infinitesimal_part + other.coefficient)
        else:
            return Microquantity(self.standard_part + other, self.infinitesimal_part)
    
    def __radd__(self, other):
        return self.__add__(other)
    
    def __mul__(self, other):
        if isinstance(other, Microquantity):
            # (a + b·d)(c + e·d) = ac + (ae + bc)·d (since d² = 0)
            return Microquantity(
                self.standard_part * other.standard_part,
                self.standard_part * other.infinitesimal_part + self.infinitesimal_part * other.standard_part
            )
        elif isinstance(other, Infinitesimal):
            return Microquantity(Fraction(0), self.standard_part * other.coefficient)
        else:
            return Microquantity(self.standard_part * other, self.infinitesimal_part * other)
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __repr__(self):
        if self.infinitesimal_part >= 0:
            return f"{self.standard_part} + {self.infinitesimal_part}·d"
        return f"{self.standard_part} - {abs(self.infinitesimal_part)}·d"


@dataclass
class MicrolinearSpace:
    """A microlinear space with Kock-Lawvere property.
    
    For every function f: D → R, exists unique a,b such that f(d) = a + b·d.
    The coefficient b is the derivative of f at 0.
    """
    name: str
    
    def apply_kock_lawvere(self, f: Callable[[Infinitesimal], Microquantity]) -> Tuple[Microquantity, ProofObject]:
        """Apply Kock-Lawvere axiom: extract standard and infinitesimal parts.
        
        For f(d) = a + b·d, returns (a, b) where:
        - a = f(0) is the standard part
        - b is the derivative f'(0)
        
        Args:
            f: Function from infinitesimals to microquantities
        
        Returns:
            ((a, b), proof) where result = a + b·d
        """
        # Evaluate at d = 0 to get standard part
        zero = Infinitesimal(Fraction(0))
        f_at_0 = f(zero)
        a = f_at_0.standard_part
        
        # Evaluate at d = 1 (as infinitesimal) to get slope
        # f(d) = a + b·d, so f(1·d) = a + b·1 = a + b
        one_d = Infinitesimal(Fraction(1))
        f_at_d = f(one_d)
        # f_at_d = a + b·1 = a + b, so b = f_at_d - a
        b = f_at_d.infinitesimal_part
        
        result = Microquantity(a, b)
        
        proof = ProofObject(
            conclusion=f"Kock-Lawvere: f(d) = {a} + {b}·d",
            premises=[f"f(0) = {a}", f"f'(0) = {b}"],
            rule="kock_lawvere",
            derivation=["By uniqueness in Kock-Lawvere axiom"]
        )
        return result, proof


def tangent_vector(f: Callable[[Fraction], Fraction], point: Fraction) -> Tuple[Fraction, ProofObject]:
    """Extract tangent vector (derivative) using SDG.
    
    The tangent to f at point is the coefficient b in:
    f(point + d) = f(point) + b·d
    
    Args:
        f: Function R → R
        point: Point where to compute tangent
    
    Returns:
        (slope, proof)
    """
    # In SDG: f(x + d) = f(x) + f'(x)·d for nilsquare d
    # We approximate using finite difference
    h = Fraction(1, 1000000)  # Small but non-zero
    
    f_at_point = f(point)
    f_at_point_plus_h = f(point + h)
    
    # f(x + h) ≈ f(x) + f'(x)·h
    # So f'(x) ≈ (f(x+h) - f(x)) / h
    slope = (f_at_point_plus_h - f_at_point) / h
    
    proof = ProofObject(
        conclusion=f"Tangent vector at {point}: f'({point}) ≈ {slope}",
        premises=[f"f({point}) = {f_at_point}", f"f({point}+{h}) = {f_at_point_plus_h}"],
        rule="tangent_sdg",
        derivation=[f"SDG: f(x+d) = f(x) + f'(x)·d"]
    )
    return slope, proof


def lie_bracket(X: Callable[[Fraction], Fraction], 
                Y: Callable[[Fraction], Fraction], 
                point: Fraction) -> Tuple[Fraction, ProofObject]:
    """Compute Lie bracket [X,Y] = XY - YX at a point.
    
    The Lie bracket measures the failure of vector fields to commute.
    [X,Y](f) = X(Y(f)) - Y(X(f))
    
    Args:
        X: First vector field (as function on reals)
        Y: Second vector field
        point: Point where to evaluate
    
    Returns:
        (bracket_value, proof)
    """
    # Approximate X(Y(f)) and Y(X(f)) at point
    h = Fraction(1, 10000)
    
    # X(Y(point)) approximation
    y_at_point = Y(point)
    y_at_point_plus_h = Y(point + h)
    dy = (y_at_point_plus_h - y_at_point) / h
    
    x_at_point = X(point)
    x_at_y = X(y_at_point)
    x_at_y_plus_dy = X(y_at_point + h * dy)
    xy_f = (x_at_y_plus_dy - x_at_y) / h
    
    # Y(X(point)) approximation
    dx = (x_at_point_plus_h := X(point + h))
    dx = (dx - x_at_point) / h
    
    y_at_x = Y(x_at_point)
    y_at_x_plus_dx = Y(x_at_point + h * dx)
    yx_f = (y_at_x_plus_dx - y_at_x) / h
    
    bracket = xy_f - yx_f
    
    proof = ProofObject(
        conclusion=f"Lie bracket [X,Y] at {point} ≈ {bracket}",
        premises=[f"X(Y(f)) ≈ {xy_f}", f"Y(X(f)) ≈ {yx_f}"],
        rule="lie_bracket",
        derivation=[f"[X,Y] = XY - YX"]
    )
    return bracket, proof


def differential_form(f: Callable[[Fraction], Fraction], 
                     degree: int) -> Tuple[Callable, ProofObject]:
    """Create exterior derivative of a 0-form (function).
    
    For a 0-form f, df is a 1-form: df(v) = v(f)
    
    Args:
        f: Function (0-form)
        degree: Degree of the form (0 for functions)
    
    Returns:
        (df, proof) where df is the exterior derivative
    """
    if degree != 0:
        raise ValueError("Only 0-forms supported in this implementation")
    
    def df(vector_field: Callable[[Fraction], Fraction]) -> Callable[[Fraction], Fraction]:
        """df applied to a vector field gives directional derivative."""
        def result(point: Fraction) -> Fraction:
            h = Fraction(1, 10000)
            # Directional derivative: v(f)(p) ≈ (f(p + h·v(p)) - f(p)) / h
            v_at_p = vector_field(point)
            return (f(point + h * v_at_p) - f(point)) / h
        return result
    
    proof = ProofObject(
        conclusion=f"Exterior derivative d(f) created",
        premises=[f"0-form f degree: {degree}"],
        rule="exterior_derivative",
        derivation=["df(v) = v(f) by definition"]
    )
    return df, proof


def stokes_theorem_check(form_values: List[Fraction], 
                         boundary_values: List[Fraction],
                         interior_values: List[Fraction]) -> Tuple[bool, ProofObject]:
    """Discrete approximation of Stokes' theorem: ∫_∂M ω = ∫_M dω.
    
    For a discrete mesh, verifies that the sum over boundary faces
    approximates the sum of the exterior derivative over interior.
    
    Args:
        form_values: Values of the form at vertices
        boundary_values: Form values on boundary edges/faces
        interior_values: Exterior derivative values on interior
    
    Returns:
        (approximation_holds, proof)
    """
    # Discrete approximation: sum of boundary values ≈ sum of interior values
    boundary_sum = sum(boundary_values)
    interior_sum = sum(interior_values)
    
    # Check if approximately equal (within tolerance)
    diff = abs(boundary_sum - interior_sum)
    tolerance = Fraction(1, 100)
    holds = diff < tolerance
    
    proof = ProofObject(
        conclusion=f"Stokes theorem {'verified' if holds else 'approximation large'}",
        premises=[f"∫_∂M ω = {boundary_sum}", f"∫_M dω = {interior_sum}", f"Difference: {diff}"],
        rule="stokes_discrete",
        derivation=[f"Discrete approximation on {len(interior_values)} interior elements"]
    )
    return holds, proof
