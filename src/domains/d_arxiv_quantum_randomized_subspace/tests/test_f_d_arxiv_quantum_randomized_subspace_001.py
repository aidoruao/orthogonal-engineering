"""Tests for D_ARXIV_QUANTUM_RANDOMIZED_SUBSPACE.

Standard: OE test pattern — PASS and FAIL cases for each invariant.
"""

from __future__ import annotations

from fractions import Fraction

from axioms.logic import ProofObject
from domains.d_arxiv_quantum_randomized_subspace.implementation import (
    Hamiltonian,
    QRSIConfig,
    SubspaceEstimate,
    QRSIClaim,
)
from domains.d_arxiv_quantum_randomized_subspace.invariants import (
    check_anti_concentration,
    check_spectral_gap_preserved,
    check_full_eigenspace_spanned,
    check_branch_count_matches_degeneracy,
    run_all_invariants,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_hamiltonian():
    return Hamiltonian(
        hamiltonian_name="toric_code",
        degeneracy_g=4,
        spectral_gap=Fraction(1, 10),
    )


def make_good_config():
    return QRSIConfig(
        branch_count=4,
        satisfies_anti_concentration=True,
        uses_haar_randomness=False,
    )


def make_good_estimate():
    return SubspaceEstimate(
        estimated_dimension=4,
        full_eigenspace_spanned=True,
        spectral_gap_preserved=True,
    )


def make_safe_claim():
    return QRSIClaim(
        hamiltonian=make_hamiltonian(),
        config=make_good_config(),
        estimate=make_good_estimate(),
    )


def make_bad_ac_claim():
    return QRSIClaim(
        hamiltonian=make_hamiltonian(),
        config=QRSIConfig(
            branch_count=4,
            satisfies_anti_concentration=False,
            uses_haar_randomness=False,
        ),
        estimate=make_good_estimate(),
    )


def make_bad_gap_claim():
    return QRSIClaim(
        hamiltonian=make_hamiltonian(),
        config=make_good_config(),
        estimate=SubspaceEstimate(
            estimated_dimension=4,
            full_eigenspace_spanned=True,
            spectral_gap_preserved=False,
        ),
    )


def make_bad_branch_claim():
    return QRSIClaim(
        hamiltonian=make_hamiltonian(),
        config=QRSIConfig(
            branch_count=3,
            satisfies_anti_concentration=True,
            uses_haar_randomness=False,
        ),
        estimate=make_good_estimate(),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_check_anti_concentration_pass():
    claim = make_safe_claim()
    success, proof = check_anti_concentration(claim)
    assert success is True
    assert "satisfied" in proof.conclusion


def test_check_anti_concentration_fail():
    claim = make_bad_ac_claim()
    success, proof = check_anti_concentration(claim)
    assert success is False
    assert "not satisfied" in proof.conclusion


def test_check_spectral_gap_preserved_pass():
    claim = make_safe_claim()
    success, proof = check_spectral_gap_preserved(claim)
    assert success is True
    assert "preserved" in proof.conclusion


def test_check_spectral_gap_preserved_fail():
    claim = make_bad_gap_claim()
    success, proof = check_spectral_gap_preserved(claim)
    assert success is False
    assert "not preserved" in proof.conclusion


def test_check_full_eigenspace_spanned_pass():
    claim = make_safe_claim()
    success, proof = check_full_eigenspace_spanned(claim)
    assert success is True
    assert "spanned" in proof.conclusion


def test_check_branch_count_matches_degeneracy_pass():
    claim = make_safe_claim()
    success, proof = check_branch_count_matches_degeneracy(claim)
    assert success is True
    assert "matches" in proof.conclusion


def test_check_branch_count_matches_degeneracy_fail():
    claim = make_bad_branch_claim()
    success, proof = check_branch_count_matches_degeneracy(claim)
    assert success is False
    assert "does not match" in proof.conclusion


def test_run_all_invariants():
    results = run_all_invariants()
    for name, result in results.items():
        if name.endswith("_pass"):
            assert result == "PASS", f"{name} failed: {result}"
        elif name.endswith("_fail"):
            assert result.startswith("FAIL"), f"{name} should fail but got: {result}"
