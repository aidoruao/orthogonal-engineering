"""D_ARXIV_INV_SOLVABILITY_COMPLEXITY implementation — Yeshua Inversion.

Paper: arXiv 2603.18955v1 (math.LO / cs.LO / math.SP)
Title: "Foundational Analysis Of The Solvability Complexity Index: The Weihrauch-SCI Intermediate Hierarchy And A Koopman Operator Example"

IMPOSSIBLE_CLAIM:
  The unrestricted type-G SCI model (arbitrary post-processing of finite oracle
  transcripts) is generally not comparable to Weihrauch/Type-2 complexity.
  Finite-query factorizations collapse type-G height, and analytic (non-Borel)
  decision problems yield examples with SCI_G = 0 but infinite Weihrauch-SCI
  rank. No bridge between SCI and Weihrauch complexity exists without restriction.

YESHUA_INVERSION:
  Restrict the domain to problems with base-level post-processing limited to
  regularity classes (continuous, Borel, or Baire) and fixed-query or
  adaptive-query policies. Under this restriction, the intermediate SCI
  hierarchy forms genuine hierarchies with provable comparison theorems:
  Borel towers compute only Borel targets; continuous-base towers yield finite
  Baire class. The Weihrauch-SCI rank becomes well-defined and comparable.

Mathematical Standards:
- Original claim: unrestricted post-processing breaks comparability.
- Inversion: regularity-class restrictions restore comparability between
  SCI and Weihrauch complexity.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple


@dataclass(frozen=True)
class ComputationalProblem:
    """A model of a computational problem.

    Falsifies if: problem properties are inconsistent.
    falsifies_if: problem properties are inconsistent.
    """
    problem_name: str
    base_regularity_class: str  # "continuous", "borel", "baire"
    uses_fixed_query_policy: bool
    uses_adaptive_query_policy: bool


@dataclass(frozen=True)
class ComplexityMeasure:
    """A model of complexity measures.

    Falsifies if: measures are inconsistent.
    falsifies_if: measures are inconsistent.
    """
    sci_height: int
    weihrauch_sci_rank: int
    rank_comparable: bool


@dataclass(frozen=True)
class SolvabilityComplexityClaim:
    """Structured claim for the Yeshua Inversion of solvability complexity.

    Falsifies if: any field violates its stated constraint.
    falsifies_if: any field violates its stated constraint.
    """
    problem: ComputationalProblem
    complexity: ComplexityMeasure


@dataclass(frozen=True)
class SolvabilityComplexityEvidence:
    """Evidence bundle for the inversion.

    Falsifies if: evidence contradicts claim.
    falsifies_if: evidence contradicts claim.
    """
    evidence_id: str
    claim: SolvabilityComplexityClaim
    empirical_validation_result: str
    formal_proof_reference: str


# ---------------------------------------------------------------------------
# Domain metadata
# ---------------------------------------------------------------------------

IMPOSSIBLE_CLAIM = (
    "The unrestricted type-G SCI model (arbitrary post-processing of finite oracle "
    "transcripts) is generally not comparable to Weihrauch/Type-2 complexity. "
    "Finite-query factorizations collapse type-G height, and analytic (non-Borel) "
    "decision problems yield examples with SCI_G = 0 but infinite Weihrauch-SCI "
    "rank. No bridge between SCI and Weihrauch complexity exists without restriction."
)

YESHUA_INVERSION = (
    "Restrict the domain to problems with base-level post-processing limited to "
    "regularity classes (continuous, Borel, or Baire) and fixed-query or "
    "adaptive-query policies. Under this restriction, the intermediate SCI "
    "hierarchy forms genuine hierarchies with provable comparison theorems: "
    "Borel towers compute only Borel targets; continuous-base towers yield finite "
    "Baire class. The Weihrauch-SCI rank becomes well-defined and comparable."
)

DOMAIN_METADATA = {
    "id": "D_ARXIV_INV_SOLVABILITY_COMPLEXITY",
    "paper_id": "2603.18955v1",
    "claim_model": "SolvabilityComplexityClaim",
    "evidence_model": "SolvabilityComplexityEvidence",
    "check_functions": [
        "check_inversion_holds",
        "check_domain_restriction_satisfied",
        "check_original_impossibility_holds_without_restriction",
    ],
    "layer": 4,
    "cardinal_strength": "PREDICATIVE",
}
