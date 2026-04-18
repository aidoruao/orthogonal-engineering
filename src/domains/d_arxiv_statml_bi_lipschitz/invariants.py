"""Invariant checks for d_arxiv_statml_bi_lipschitz."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import BiLipschitzAutoencoderClaim, create_nominal_claim


def check_injectivity(data: BiLipschitzAutoencoderClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Encoder is injective.

    Standard: arXiv 2604.06701v1 (stat.ML) claim operationalization.
    Falsifies if: not is_injective.
    falsifies_if: not is_injective.

    Returns:
        Tuple of (success, proof).
    """
    success = data.is_injective is True
    proof = ProofObject(
        rule="check_injectivity",
        premises=[
            f"paper_id=2604.06701v1",
            f'is_injective={data.is_injective}',
        ],
        conclusion=(
            "PASS: encoder is injective"
            if success else "FAIL: not is_injective"
        ),
    )
    return success, proof



def check_lipschitz_constant_valid(data: BiLipschitzAutoencoderClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Lipschitz constant >= lower bi-lipschitz constant and lower > 0.

    Standard: arXiv 2604.06701v1 (stat.ML) claim operationalization.
    Falsifies if: lipschitz_constant < bi_lipschitz_lower or bi_lipschitz_lower <= 0.
    falsifies_if: lipschitz_constant < bi_lipschitz_lower or bi_lipschitz_lower <= 0.

    Returns:
        Tuple of (success, proof).
    """
    success = data.lipschitz_constant >= data.bi_lipschitz_lower and data.bi_lipschitz_lower > Fraction(0)
    proof = ProofObject(
        rule="check_lipschitz_constant_valid",
        premises=[
            f"paper_id=2604.06701v1",
            f'lipschitz_constant={data.lipschitz_constant}',
            f'bi_lipschitz_lower={data.bi_lipschitz_lower}',
        ],
        conclusion=(
            "PASS: Lipschitz constant >= lower bi-Lipschitz constant and lower > 0"
            if success else "FAIL: lipschitz_constant < bi_lipschitz_lower or bi_lipschitz_lower <= 0"
        ),
    )
    return success, proof



def check_dimension_valid(data: BiLipschitzAutoencoderClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Latent dimension is in [1, input_dimension].

    Standard: arXiv 2604.06701v1 (stat.ML) claim operationalization.
    Falsifies if: latent_dimension < 1 or latent_dimension > input_dimension.
    falsifies_if: latent_dimension < 1 or latent_dimension > input_dimension.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(1) <= data.latent_dimension <= data.input_dimension
    proof = ProofObject(
        rule="check_dimension_valid",
        premises=[
            f"paper_id=2604.06701v1",
            f'latent_dimension={data.latent_dimension}',
            f'input_dimension={data.input_dimension}',
        ],
        conclusion=(
            "PASS: latent dimension is in [1, input_dimension]"
            if success else "FAIL: latent_dimension < 1 or latent_dimension > input_dimension"
        ),
    )
    return success, proof



def check_bi_lipschitz_lower_positive(data: BiLipschitzAutoencoderClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Lower bi-lipschitz constant is positive.

    Standard: arXiv 2604.06701v1 (stat.ML) claim operationalization.
    Falsifies if: bi_lipschitz_lower <= 0.
    falsifies_if: bi_lipschitz_lower <= 0.

    Returns:
        Tuple of (success, proof).
    """
    success = data.bi_lipschitz_lower > Fraction(0)
    proof = ProofObject(
        rule="check_bi_lipschitz_lower_positive",
        premises=[
            f"paper_id=2604.06701v1",
            f'bi_lipschitz_lower={data.bi_lipschitz_lower}',
        ],
        conclusion=(
            "PASS: lower bi-Lipschitz constant is positive"
            if success else "FAIL: bi_lipschitz_lower <= 0"
        ),
    )
    return success, proof



def check_input_dimension_positive(data: BiLipschitzAutoencoderClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Input dimension is >= 1.

    Standard: arXiv 2604.06701v1 (stat.ML) claim operationalization.
    Falsifies if: input_dimension < 1.
    falsifies_if: input_dimension < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.input_dimension >= Fraction(1)
    proof = ProofObject(
        rule="check_input_dimension_positive",
        premises=[
            f"paper_id=2604.06701v1",
            f'input_dimension={data.input_dimension}',
        ],
        conclusion=(
            "PASS: input dimension is >= 1"
            if success else "FAIL: input_dimension < 1"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.06701v1 (stat.ML) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_injectivity", check_injectivity),
        ("check_lipschitz_constant_valid", check_lipschitz_constant_valid),
        ("check_dimension_valid", check_dimension_valid),
        ("check_bi_lipschitz_lower_positive", check_bi_lipschitz_lower_positive),
        ("check_input_dimension_positive", check_input_dimension_positive),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
