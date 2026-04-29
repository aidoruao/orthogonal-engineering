"""Invariant checks for D_ARXIV_QUANTUM_RANDOMIZED_SUBSPACE.

Paper: arXiv 2604.09483v1 (quant-ph)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    Hamiltonian,
    QRSIConfig,
    SubspaceEstimate,
    QRSIClaim,
    QRSIEvidence,
)


# ---------------------------------------------------------------------------
# 1. Anti-concentration condition
# ---------------------------------------------------------------------------

def check_anti_concentration(
    # TODO: Expand check_anti_concentration() - stub detected by Yeshua Agent
    claim: QRSIClaim,
) -> Tuple[bool, ProofObject]:
    """Random rotations must satisfy anti-concentration over degenerate manifold.

    Standard: arXiv 2604.09483v1 claim operationalization.
    Falsifies if: config.satisfies_anti_concentration is False.
    falsifies_if: anti-concentration condition is not satisfied.
    """
    if not claim.config.satisfies_anti_concentration:
        return False, ProofObject(
            rule="check_anti_concentration",
            premises=["satisfies_anti_concentration=False"],
            conclusion="VIOLATION: Anti-concentration condition not satisfied",
        )
    return True, ProofObject(
        rule="check_anti_concentration",
        premises=["satisfies_anti_concentration=True"],
        conclusion="PASS: Anti-concentration condition satisfied",
    )


# ---------------------------------------------------------------------------
# 2. Spectral gap preserved
# ---------------------------------------------------------------------------

def check_spectral_gap_preserved(
    # TODO: Expand check_spectral_gap_preserved() - stub detected by Yeshua Agent
    claim: QRSIClaim,
) -> Tuple[bool, ProofObject]:
    """Spectral gap must be preserved exactly on every branch.

    Standard: arXiv 2604.09483v1 claim operationalization.
    Falsifies if: estimate.spectral_gap_preserved is False.
    falsifies_if: spectral gap is not preserved.
    """
    if not claim.estimate.spectral_gap_preserved:
        return False, ProofObject(
            rule="check_spectral_gap_preserved",
            premises=["spectral_gap_preserved=False"],
            conclusion="VIOLATION: Spectral gap not preserved on all branches",
        )
    return True, ProofObject(
        rule="check_spectral_gap_preserved",
        premises=["spectral_gap_preserved=True"],
        conclusion="PASS: Spectral gap preserved on all branches",
    )


# ---------------------------------------------------------------------------
# 3. Full eigenspace spanned
# ---------------------------------------------------------------------------

def check_full_eigenspace_spanned(
    # TODO: Expand check_full_eigenspace_spanned() - stub detected by Yeshua Agent
    claim: QRSIClaim,
) -> Tuple[bool, ProofObject]:
    """The construction must span the full eigenspace almost surely.

    Standard: arXiv 2604.09483v1 claim operationalization.
    Falsifies if: estimate.full_eigenspace_spanned is False.
    falsifies_if: full eigenspace is not spanned.
    """
    if not claim.estimate.full_eigenspace_spanned:
        return False, ProofObject(
            rule="check_full_eigenspace_spanned",
            premises=["full_eigenspace_spanned=False"],
            conclusion="VIOLATION: Full eigenspace not spanned",
        )
    return True, ProofObject(
        rule="check_full_eigenspace_spanned",
        premises=["full_eigenspace_spanned=True"],
        conclusion="PASS: Full eigenspace spanned almost surely",
    )


# ---------------------------------------------------------------------------
# 4. Branch count matches degeneracy
# ---------------------------------------------------------------------------

def check_branch_count_matches_degeneracy(
    # TODO: Expand check_branch_count_matches_degeneracy() - stub detected by Yeshua Agent
    claim: QRSIClaim,
) -> Tuple[bool, ProofObject]:
    """Branch count must equal degeneracy g.

    Standard: arXiv 2604.09483v1 claim operationalization.
    Falsifies if: config.branch_count != hamiltonian.degeneracy_g.
    falsifies_if: branch count does not match degeneracy.
    """
    if claim.config.branch_count != claim.hamiltonian.degeneracy_g:
        return False, ProofObject(
            rule="check_branch_count_matches_degeneracy",
            premises=[
                f"branch_count={claim.config.branch_count}",
                f"degeneracy_g={claim.hamiltonian.degeneracy_g}",
            ],
            conclusion="VIOLATION: Branch count does not match degeneracy",
        )
    return True, ProofObject(
        rule="check_branch_count_matches_degeneracy",
        premises=[
            f"branch_count={claim.config.branch_count}",
            f"degeneracy_g={claim.hamiltonian.degeneracy_g}",
        ],
        conclusion="PASS: Branch count matches degeneracy",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all D_ARXIV_QUANTUM_RANDOMIZED_SUBSPACE invariants with nominal data.

    Falsifies if: any invariant fails or raises an exception.
    falsifies_if: any invariant fails or raises an exception.
    """
    ham = Hamiltonian(
        hamiltonian_name="toric_code",
        degeneracy_g=4,
        spectral_gap=Fraction(1, 10),
    )
    config_good = QRSIConfig(
        branch_count=4,
        satisfies_anti_concentration=True,
        uses_haar_randomness=False,
    )
    estimate_good = SubspaceEstimate(
        estimated_dimension=4,
        full_eigenspace_spanned=True,
        spectral_gap_preserved=True,
    )
    claim_safe = QRSIClaim(
        hamiltonian=ham,
        config=config_good,
        estimate=estimate_good,
    )

    # FAIL case: no anti-concentration
    config_bad_ac = QRSIConfig(
        branch_count=4,
        satisfies_anti_concentration=False,
        uses_haar_randomness=False,
    )
    claim_bad_ac = QRSIClaim(
        hamiltonian=ham,
        config=config_bad_ac,
        estimate=estimate_good,
    )

    # FAIL case: spectral gap not preserved
    estimate_bad_gap = SubspaceEstimate(
        estimated_dimension=4,
        full_eigenspace_spanned=True,
        spectral_gap_preserved=False,
    )
    claim_bad_gap = QRSIClaim(
        hamiltonian=ham,
        config=config_good,
        estimate=estimate_bad_gap,
    )

    # FAIL case: branch count mismatch
    config_bad_branch = QRSIConfig(
        branch_count=3,
        satisfies_anti_concentration=True,
        uses_haar_randomness=False,
    )
    claim_bad_branch = QRSIClaim(
        hamiltonian=ham,
        config=config_bad_branch,
        estimate=estimate_good,
    )

    checks = [
        ("check_anti_concentration_pass", lambda: check_anti_concentration(claim_safe)),
        ("check_spectral_gap_preserved_pass", lambda: check_spectral_gap_preserved(claim_safe)),
        ("check_full_eigenspace_spanned_pass", lambda: check_full_eigenspace_spanned(claim_safe)),
        ("check_branch_count_matches_degeneracy_pass", lambda: check_branch_count_matches_degeneracy(claim_safe)),
        ("check_anti_concentration_fail", lambda: check_anti_concentration(claim_bad_ac)),
        ("check_spectral_gap_preserved_fail", lambda: check_spectral_gap_preserved(claim_bad_gap)),
        ("check_branch_count_matches_degeneracy_fail", lambda: check_branch_count_matches_degeneracy(claim_bad_branch)),
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
    print("All D_ARXIV_QUANTUM_RANDOMIZED_SUBSPACE invariants: PASS")
