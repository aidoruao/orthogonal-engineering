"""D_ARXIV_INV_SHARP_LOCAL_MINIMA implementation — Yeshua Inversion.

Paper: arXiv 2604.09412v1 (stat.ML / cs.LG)
Title: "Sharp description of local minima in the loss landscape of high-dimensional two-layer ReLU neural networks"

IMPOSSIBLE_CLAIM:
  In the well-specified regime, local minima of two-layer ReLU networks are
  typically isolated. SGD cannot escape these spurious local minima because
  there are no flat directions connecting them to global minima. Convergence
  to global optima is impossible without overparameterisation.

YESHUA_INVERSION:
  Restrict the domain to the overparameterised regime where network width K
  exceeds the intrinsic dimensionality of the teacher. Under this restriction,
  flat directions emerge between local minima, making global minima increasingly
  accessible. SGD can now traverse the flat landscape and converge to global
  optima because the connectivity of the loss landscape is restored by width.

Mathematical Standards:
- Original claim: isolated minima in well-specified regime trap SGD.
- Inversion: overparameterisation creates flat directions (connected manifold
  of minima) that enable SGD to reach global optima.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple


@dataclass(frozen=True)
class NetworkArchitecture:
    """A model of a neural network architecture.

    Falsifies if: architecture properties are inconsistent.
    falsifies_if: architecture properties are inconsistent.
    """
    network_name: str
    width: int
    teacher_dimensionality: int
    is_overparameterised: bool


@dataclass(frozen=True)
class OptimizationDynamics:
    """A model of the optimization dynamics.

    Falsifies if: dynamics properties are inconsistent.
    falsifies_if: dynamics properties are inconsistent.
    """
    uses_sgd: bool
    converged_to_global_minimum: bool
    spurious_solution_rate: Fraction


@dataclass(frozen=True)
class SharpLocalMinimaClaim:
    """Structured claim for the Yeshua Inversion of sharp local minima.

    Falsifies if: any field violates its stated constraint.
    falsifies_if: any field violates its stated constraint.
    """
    architecture: NetworkArchitecture
    dynamics: OptimizationDynamics
    spurious_rate_threshold: Fraction


@dataclass(frozen=True)
class SharpLocalMinimaEvidence:
    """Evidence bundle for the inversion.

    Falsifies if: evidence contradicts claim.
    falsifies_if: evidence contradicts claim.
    """
    evidence_id: str
    claim: SharpLocalMinimaClaim
    empirical_validation_result: str
    formal_proof_reference: str


# ---------------------------------------------------------------------------
# Domain metadata
# ---------------------------------------------------------------------------

IMPOSSIBLE_CLAIM = (
    "In the well-specified regime, local minima of two-layer ReLU networks are "
    "typically isolated. SGD cannot escape these spurious local minima because "
    "there are no flat directions connecting them to global minima. Convergence "
    "to global optima is impossible without overparameterisation."
)

YESHUA_INVERSION = (
    "Restrict the domain to the overparameterised regime where network width K "
    "exceeds the intrinsic dimensionality of the teacher. Under this restriction, "
    "flat directions emerge between local minima, making global minima increasingly "
    "accessible. SGD can now traverse the flat landscape and converge to global "
    "optima because the connectivity of the loss landscape is restored by width."
)

DOMAIN_METADATA = {
    "id": "D_ARXIV_INV_SHARP_LOCAL_MINIMA",
    "paper_id": "2604.09412v1",
    "claim_model": "SharpLocalMinimaClaim",
    "evidence_model": "SharpLocalMinimaEvidence",
    "check_functions": [
        "check_inversion_holds",
        "check_domain_restriction_satisfied",
        "check_original_impossibility_holds_without_restriction",
    ],
    "layer": 4,
    "cardinal_strength": "PREDICATIVE",
}
