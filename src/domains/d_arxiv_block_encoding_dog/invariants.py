"""Invariant checks for D_ARXIV_BLOCK_ENCODING_DOG.

Paper: arXiv 2604.09538v1 (quant-ph)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    GridConfig,
    BlockEncoding,
    DoGOperator,
    DoGClaim,
    DoGEvidence,
)


# ---------------------------------------------------------------------------
# 1. Constant subnormalisation
# ---------------------------------------------------------------------------

def check_constant_subnormalisation(
    claim: DoGClaim,
) -> Tuple[bool, ProofObject]:
    """Block encoding must have constant subnormalisation λ = 2.

    Standard: arXiv 2604.09538v1 claim operationalization.
    Falsifies if: subnormalisation_lambda != 2.
    falsifies_if: subnormalisation_lambda is not exactly 2.
    """
    lam = claim.encoding.subnormalisation_lambda
    if lam != Fraction(2):
        return False, ProofObject(
            rule="check_constant_subnormalisation",
            premises=[f"subnormalisation_lambda={lam}"],
            conclusion="VIOLATION: Subnormalisation factor is not constant λ=2",
        )
    return True, ProofObject(
        rule="check_constant_subnormalisation",
        premises=[f"subnormalisation_lambda={lam}"],
        conclusion="PASS: Subnormalisation factor is constant λ=2",
    )


# ---------------------------------------------------------------------------
# 2. No black-box oracles
# ---------------------------------------------------------------------------

def check_no_black_box_oracles(
    claim: DoGClaim,
) -> Tuple[bool, ProofObject]:
    """Block encoding must not require QRAM or signed amplitude loading.

    Standard: arXiv 2604.09538v1 claim operationalization.
    Falsifies if: uses_qram or uses_signed_amplitude_loading is True.
    falsifies_if: encoding uses QRAM or signed amplitude loading.
    """
    enc = claim.encoding
    violations = []
    if enc.uses_qram:
        violations.append("uses_qram=True")
    if enc.uses_signed_amplitude_loading:
        violations.append("uses_signed_amplitude_loading=True")

    if violations:
        return False, ProofObject(
            rule="check_no_black_box_oracles",
            premises=violations,
            conclusion="VIOLATION: Block encoding requires black-box oracles",
        )
    return True, ProofObject(
        rule="check_no_black_box_oracles",
        premises=["uses_qram=False", "uses_signed_amplitude_loading=False"],
        conclusion="PASS: No black-box oracles required",
    )


# ---------------------------------------------------------------------------
# 3. O(h^4) scaling
# ---------------------------------------------------------------------------

def check_o_h4_scaling(
    claim: DoGClaim,
) -> Tuple[bool, ProofObject]:
    """Block encoding success probability must scale as O(h^4).

    Standard: arXiv 2604.09538v1 claim operationalization.
    Falsifies if: scaling_order > 4 (i.e., worse than h^4).
    falsifies_if: scaling_order exceeds 4.
    """
    if claim.scaling_order > Fraction(4):
        return False, ProofObject(
            rule="check_o_h4_scaling",
            premises=[f"scaling_order={claim.scaling_order}"],
            conclusion="VIOLATION: Scaling order exceeds O(h^4)",
        )
    return True, ProofObject(
        rule="check_o_h4_scaling",
        premises=[f"scaling_order={claim.scaling_order}"],
        conclusion="PASS: Scaling order is O(h^4) or better",
    )


# ---------------------------------------------------------------------------
# 4. Success probability bounded
# ---------------------------------------------------------------------------

def check_success_probability_bounded(
    claim: DoGClaim,
) -> Tuple[bool, ProofObject]:
    """Success probability must be in (0, 1].

    Standard: arXiv 2604.09538v1 claim operationalization.
    Falsifies if: success_probability <= 0 or > 1.
    falsifies_if: success_probability is outside (0, 1].
    """
    p = claim.encoding.success_probability
    if p <= Fraction(0) or p > Fraction(1):
        return False, ProofObject(
            rule="check_success_probability_bounded",
            premises=[f"success_probability={p}"],
            conclusion="VIOLATION: Success probability outside valid range (0, 1]",
        )
    return True, ProofObject(
        rule="check_success_probability_bounded",
        premises=[f"success_probability={p}"],
        conclusion="PASS: Success probability within valid range",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all D_ARXIV_BLOCK_ENCODING_DOG invariants with nominal data.

    Falsifies if: any invariant fails or raises an exception.
    falsifies_if: any invariant fails or raises an exception.
    """
    grid = GridConfig(
        grid_size_n=256,
        spatial_dimension_d=2,
        grid_spacing_h=Fraction(1, 100),
    )
    encoding_good = BlockEncoding(
        subnormalisation_lambda=Fraction(2),
        uses_qram=False,
        uses_signed_amplitude_loading=False,
        success_probability=Fraction(9, 10),
    )
    operator = DoGOperator(
        sigma_1=Fraction(1),
        sigma_2=Fraction(2),
        stencil_width=5,
    )
    claim_safe = DoGClaim(
        grid=grid,
        encoding=encoding_good,
        operator=operator,
        scaling_order=Fraction(4),
    )

    # FAIL case: wrong subnormalisation
    encoding_bad_lambda = BlockEncoding(
        subnormalisation_lambda=Fraction(3),
        uses_qram=False,
        uses_signed_amplitude_loading=False,
        success_probability=Fraction(9, 10),
    )
    claim_bad_lambda = DoGClaim(
        grid=grid,
        encoding=encoding_bad_lambda,
        operator=operator,
        scaling_order=Fraction(4),
    )

    # FAIL case: uses QRAM
    encoding_bad_qram = BlockEncoding(
        subnormalisation_lambda=Fraction(2),
        uses_qram=True,
        uses_signed_amplitude_loading=False,
        success_probability=Fraction(9, 10),
    )
    claim_bad_qram = DoGClaim(
        grid=grid,
        encoding=encoding_bad_qram,
        operator=operator,
        scaling_order=Fraction(4),
    )

    # FAIL case: scaling too slow
    claim_bad_scaling = DoGClaim(
        grid=grid,
        encoding=encoding_good,
        operator=operator,
        scaling_order=Fraction(5),
    )

    checks = [
        ("check_constant_subnormalisation_pass", lambda: check_constant_subnormalisation(claim_safe)),
        ("check_no_black_box_oracles_pass", lambda: check_no_black_box_oracles(claim_safe)),
        ("check_o_h4_scaling_pass", lambda: check_o_h4_scaling(claim_safe)),
        ("check_success_probability_bounded_pass", lambda: check_success_probability_bounded(claim_safe)),
        ("check_constant_subnormalisation_fail", lambda: check_constant_subnormalisation(claim_bad_lambda)),
        ("check_no_black_box_oracles_fail", lambda: check_no_black_box_oracles(claim_bad_qram)),
        ("check_o_h4_scaling_fail", lambda: check_o_h4_scaling(claim_bad_scaling)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
        except Exception as exc:
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json

    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [
        k for k, v in results.items()
        if not v.startswith("PASS") and not k.endswith("_fail")
    ]
    unexpected = [
        k for k, v in results.items()
        if k.endswith("_fail") and not v.startswith("FAIL")
    ]
    failures.extend(unexpected)
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_ARXIV_BLOCK_ENCODING_DOG invariants: PASS")
