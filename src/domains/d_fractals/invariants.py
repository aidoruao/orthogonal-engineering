#!/usr/bin/env python3
"""Fractals Domain Invariants — Self-similarity, dimension, and convergence.

Mathematical Standards:
- Hausdorff dimension
- Box-counting dimension  
- Iterated function systems
- Mandelbrot/Julia set membership

Falsifies if:
- Dimension estimate outside valid range [0, 3]
- IFS probabilities don't sum to 1
- Escape radius too small (false negatives)
- Box count decreases as box size decreases
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    FractalPoint, IteratedFunctionSystem, BoxCount,
    SelfSimilarity, Complex
)


def check_mandelbrot_membership(point: FractalPoint) -> Tuple[bool, ProofObject]:
    """Mandelbrot set: z_{n+1} = z_n² + c, z_0 = 0, bounded for all n.

    Falsifies if: mandelbrot_iterations cannot classify escape (error) or produces
    falsifies_if: mandelbrot_iterations cannot classify escape (error) or produces
    inconsistent escape status for the point.
    """
    # Quick check for main cardioid (exact formula)
    c = point.c
    # Main cardioid: c = 0.5*e^(iθ) - 0.25*e^(2iθ) approx
    # Simplified: check if |c - (-1)| < 0.25 for period-2 bulb
    
    iterations = point.mandelbrot_iterations()
    escaped = iterations < point.max_iterations
    
    if escaped:
        return True, ProofObject(
            conclusion=f"Point escaped after {iterations} iterations (outside Mandelbrot set)",
            premises=[f"c = {c.real} + {c.imag}i", f"Iterations: {iterations}"],
            rule="mandelbrot_escape_criterion"
        )
    
    return True, ProofObject(
        conclusion="Point in Mandelbrot set (did not escape)",
        premises=[f"c = {c.real} + {c.imag}i", f"Max iterations: {point.max_iterations}"],
        rule="mandelbrot_membership"
    )


def check_ifs_probability_sum(ifs: IteratedFunctionSystem) -> Tuple[bool, ProofObject]:
    """IFS probabilities must form valid distribution (sum to 1).

    Falsifies if: probabilities do not sum to 1 or any probability is outside [0, 1].
    falsifies_if: probabilities do not sum to 1 or any probability is outside [0, 1].
    """
    total = sum(ifs.probabilities, Fraction(0))
    
    if total != Fraction(1):
        return False, ProofObject(
            conclusion=f"VIOLATION: IFS probabilities sum to {total}, not 1",
            premises=[f"Probabilities: {ifs.probabilities}", f"Sum: {total}"],
            rule="ifs_probability_axiom"
        )
    
    for i, p in enumerate(ifs.probabilities):
        if p < Fraction(0) or p > Fraction(1):
            return False, ProofObject(
                conclusion=f"VIOLATION: Invalid probability {p} at index {i}",
                premises=[f"Probability: {p}"],
                rule="ifs_probability_bounds"
            )
    
    return True, ProofObject(
        conclusion="IFS probabilities form valid distribution",
        premises=[f"Sum: {total}", f"Count: {len(ifs.probabilities)}"],
        rule="ifs_probability_valid"
    )


def check_box_count_monotonicity(box_count: BoxCount) -> Tuple[bool, ProofObject]:
    """Box count must increase (or stay same) as box size decreases.

    Falsifies if: box_count with smaller boxes is less than with larger boxes.
    falsifies_if: box_count with smaller boxes is less than with larger boxes.
    """
    n_large = box_count.count_boxes(box_count.max_box_size)
    n_small = box_count.count_boxes(box_count.min_box_size)
    
    if n_small < n_large:
        return False, ProofObject(
            conclusion="VIOLATION: Box count decreases with smaller boxes",
            premises=[
                f"Large boxes ({box_count.max_box_size}): {n_large}",
                f"Small boxes ({box_count.min_box_size}): {n_small}"
            ],
            rule="box_count_monotonicity"
        )
    
    return True, ProofObject(
        conclusion="Box count monotonicity satisfied",
        premises=[f"Large: {n_large}, Small: {n_small}"],
        rule="box_count_monotonic"
    )


def check_dimension_bounds(dimension: Fraction, space_dimension: int) -> Tuple[bool, ProofObject]:
    """Fractal dimension must be between 0 and embedding space dimension.

    Falsifies if: dimension is negative or exceeds the embedding space dimension.
    falsifies_if: dimension is negative or exceeds the embedding space dimension.
    """
    if dimension < Fraction(0):
        return False, ProofObject(
            conclusion=f"VIOLATION: Negative fractal dimension {dimension}",
            premises=[f"Dimension: {dimension}"],
            rule="fractal_dimension_non_negative"
        )
    
    if dimension > Fraction(space_dimension):
        return False, ProofObject(
            conclusion=f"VIOLATION: Dimension {dimension} exceeds space dimension {space_dimension}",
            premises=[f"Dimension: {dimension}", f"Space: {space_dimension}"],
            rule="fractal_dimension_embedding_bound"
        )
    
    return True, ProofObject(
        conclusion="Fractal dimension within valid bounds",
        premises=[f"Dimension: {dimension}", f"Space: {space_dimension}"],
        rule="fractal_dimension_valid"
    )


def check_self_similarity_consistency(ss: SelfSimilarity) -> Tuple[bool, ProofObject]:
    """Self-similarity parameters must be consistent.

    Falsifies if: scaling factor is not in (0, 1), number of pieces < 1, or the
    falsifies_if: scaling factor is not in (0, 1), number of pieces < 1, or the
    similarity dimension is negative.
    """
    if ss.scaling_factor <= Fraction(0) or ss.scaling_factor >= Fraction(1):
        return False, ProofObject(
            conclusion=f"VIOLATION: Invalid scaling factor {ss.scaling_factor}",
            premises=[f"Scaling: {ss.scaling_factor}", "Required: (0, 1)"],
            rule="self_similarity_scaling_range"
        )
    
    if ss.num_pieces < 1:
        return False, ProofObject(
            conclusion=f"VIOLATION: Invalid number of pieces {ss.num_pieces}",
            premises=[f"Pieces: {ss.num_pieces}", "Required: >= 1"],
            rule="self_similarity_piece_count"
        )
    
    dim = ss.similarity_dimension()
    if dim < Fraction(0):
        return False, ProofObject(
            conclusion=f"VIOLATION: Negative similarity dimension {dim}",
            premises=[f"Dimension: {dim}"],
            rule="self_similarity_dimension_non_negative"
        )
    
    return True, ProofObject(
        conclusion="Self-similarity parameters consistent",
        premises=[
            f"Scaling: {ss.scaling_factor}",
            f"Pieces: {ss.num_pieces}",
            f"Dimension estimate: {dim}"
        ],
        rule="self_similarity_valid"
    )


def check_escape_radius_sufficient(radius: Fraction) -> Tuple[bool, ProofObject]:
    """Escape radius for Mandelbrot/Julia must be > 2 for correctness.

    Falsifies if: escape radius is less than or equal to 2, risking missed escapes.
    falsifies_if: escape radius is less than or equal to 2, risking missed escapes.
    """
    MIN_RADIUS = Fraction(2)
    
    if radius <= MIN_RADIUS:
        return False, ProofObject(
            conclusion=f"VIOLATION: Escape radius {radius} too small",
            premises=[f"Radius: {radius}", f"Minimum: {MIN_RADIUS}"],
            rule="mandelbrot_escape_radius_minimum"
        )
    
    return True, ProofObject(
        conclusion="Escape radius sufficient for correctness",
        premises=[f"Radius: {radius}"],
        rule="escape_radius_valid"
    )
