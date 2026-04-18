"""Invariant checks for Biochemistry."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import BiochemistryClaim, create_nominal_claim


def check_enzyme_kinetics_michaelis(data: BiochemistryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Michaelis-Menten kinetics are valid.

    Standard: Biochemistry domain invariant.
    Falsifies if: not michaelis_menten_valid.
    falsifies_if: not michaelis_menten_valid.

    Returns:
        Tuple of (success, proof).
    """
    success = data.michaelis_menten_valid
    proof = ProofObject(
        rule="check_enzyme_kinetics_michaelis",
        premises=[
            "domain=Biochemistry",
            f"michaelis_menten_valid={{data.michaelis_menten_valid}}",
        ],
        conclusion=(
            "PASS: Michaelis-Menten kinetics are valid"
            if success else "FAIL: Michaelis-Menten kinetics are valid"
        ),
    )
    return success, proof


def check_atp_hydrolysis_exergonic(data: BiochemistryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: ATP hydrolysis is exergonic.

    Standard: Biochemistry domain invariant.
    Falsifies if: not atp_hydrolysis_exergonic.
    falsifies_if: not atp_hydrolysis_exergonic.

    Returns:
        Tuple of (success, proof).
    """
    success = data.atp_hydrolysis_exergonic
    proof = ProofObject(
        rule="check_atp_hydrolysis_exergonic",
        premises=[
            "domain=Biochemistry",
            f"atp_hydrolysis_exergonic={{data.atp_hydrolysis_exergonic}}",
        ],
        conclusion=(
            "PASS: ATP hydrolysis is exergonic"
            if success else "FAIL: ATP hydrolysis is exergonic"
        ),
    )
    return success, proof


def check_protein_folding_entropy(data: BiochemistryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Protein folding entropy change is valid.

    Standard: Biochemistry domain invariant.
    Falsifies if: not folding_entropy_valid.
    falsifies_if: not folding_entropy_valid.

    Returns:
        Tuple of (success, proof).
    """
    success = data.folding_entropy_valid
    proof = ProofObject(
        rule="check_protein_folding_entropy",
        premises=[
            "domain=Biochemistry",
            f"folding_entropy_valid={{data.folding_entropy_valid}}",
        ],
        conclusion=(
            "PASS: Protein folding entropy change is valid"
            if success else "FAIL: Protein folding entropy change is valid"
        ),
    )
    return success, proof


def check_dna_replication_fidelity(data: BiochemistryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: DNA replication fidelity is high.

    Standard: Biochemistry domain invariant.
    Falsifies if: not replication_fidelity_high.
    falsifies_if: not replication_fidelity_high.

    Returns:
        Tuple of (success, proof).
    """
    success = data.replication_fidelity_high
    proof = ProofObject(
        rule="check_dna_replication_fidelity",
        premises=[
            "domain=Biochemistry",
            f"replication_fidelity_high={{data.replication_fidelity_high}}",
        ],
        conclusion=(
            "PASS: DNA replication fidelity is high"
            if success else "FAIL: DNA replication fidelity is high"
        ),
    )
    return success, proof


def check_concentration_equilibrium_fraction(data: BiochemistryClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Equilibrium concentration is non-negative.

    Standard: Biochemistry domain invariant.
    Falsifies if: not equilibrium_concentration.
    falsifies_if: not equilibrium_concentration.

    Returns:
        Tuple of (success, proof).
    """
    success = data.equilibrium_concentration >= Fraction(0)
    proof = ProofObject(
        rule="check_concentration_equilibrium_fraction",
        premises=[
            "domain=Biochemistry",
            f"equilibrium_concentration={{data.equilibrium_concentration}}",
        ],
        conclusion=(
            "PASS: Equilibrium concentration is non-negative is non-negative"
            if success else "FAIL: Equilibrium concentration is non-negative is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Biochemistry nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_enzyme_kinetics_michaelis", check_enzyme_kinetics_michaelis),
        ("check_atp_hydrolysis_exergonic", check_atp_hydrolysis_exergonic),
        ("check_protein_folding_entropy", check_protein_folding_entropy),
        ("check_dna_replication_fidelity", check_dna_replication_fidelity),
        ("check_concentration_equilibrium_fraction", check_concentration_equilibrium_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
