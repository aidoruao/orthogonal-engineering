"""Invariant checks for Neuroscience."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import NeuroscienceClaim, create_nominal_claim


def check_action_potential_all_or_none(data: NeuroscienceClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Action potential follows all-or-none principle.

    Standard: Neuroscience domain invariant.
    Falsifies if: not action_potential_all_or_none.
    falsifies_if: not action_potential_all_or_none.

    Returns:
        Tuple of (success, proof).
    """
    success = data.action_potential_all_or_none
    proof = ProofObject(
        rule="check_action_potential_all_or_none",
        premises=[
            "domain=Neuroscience",
            f"action_potential_all_or_none={{data.action_potential_all_or_none}}",
        ],
        conclusion=(
            "PASS: Action potential follows all-or-none principle"
            if success else "FAIL: Action potential follows all-or-none principle"
        ),
    )
    return success, proof


def check_synapse_neurotransmitter_release(data: NeuroscienceClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Neurotransmitter release is within valid range.

    Standard: Neuroscience domain invariant.
    Falsifies if: not neurotransmitter_release_valid.
    falsifies_if: not neurotransmitter_release_valid.

    Returns:
        Tuple of (success, proof).
    """
    success = data.neurotransmitter_release_valid
    proof = ProofObject(
        rule="check_synapse_neurotransmitter_release",
        premises=[
            "domain=Neuroscience",
            f"neurotransmitter_release_valid={{data.neurotransmitter_release_valid}}",
        ],
        conclusion=(
            "PASS: Neurotransmitter release is within valid range"
            if success else "FAIL: Neurotransmitter release is within valid range"
        ),
    )
    return success, proof


def check_myelination_conduction_speed(data: NeuroscienceClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Myelination increases conduction speed.

    Standard: Neuroscience domain invariant.
    Falsifies if: not myelination_increases_speed.
    falsifies_if: not myelination_increases_speed.

    Returns:
        Tuple of (success, proof).
    """
    success = data.myelination_increases_speed
    proof = ProofObject(
        rule="check_myelination_conduction_speed",
        premises=[
            "domain=Neuroscience",
            f"myelination_increases_speed={{data.myelination_increases_speed}}",
        ],
        conclusion=(
            "PASS: Myelination increases conduction speed"
            if success else "FAIL: Myelination increases conduction speed"
        ),
    )
    return success, proof


def check_refractory_period_bounded(data: NeuroscienceClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Refractory period is bounded.

    Standard: Neuroscience domain invariant.
    Falsifies if: not refractory_period_bounded.
    falsifies_if: not refractory_period_bounded.

    Returns:
        Tuple of (success, proof).
    """
    success = data.refractory_period_bounded
    proof = ProofObject(
        rule="check_refractory_period_bounded",
        premises=[
            "domain=Neuroscience",
            f"refractory_period_bounded={{data.refractory_period_bounded}}",
        ],
        conclusion=(
            "PASS: Refractory period is bounded"
            if success else "FAIL: Refractory period is bounded"
        ),
    )
    return success, proof


def check_synaptic_weight_fraction(data: NeuroscienceClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Synaptic weight is non-negative.

    Standard: Neuroscience domain invariant.
    Falsifies if: not synaptic_weight.
    falsifies_if: not synaptic_weight.

    Returns:
        Tuple of (success, proof).
    """
    success = data.synaptic_weight >= Fraction(0)
    proof = ProofObject(
        rule="check_synaptic_weight_fraction",
        premises=[
            "domain=Neuroscience",
            f"synaptic_weight={{data.synaptic_weight}}",
        ],
        conclusion=(
            "PASS: Synaptic weight is non-negative is non-negative"
            if success else "FAIL: Synaptic weight is non-negative is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Neuroscience nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_action_potential_all_or_none", check_action_potential_all_or_none),
        ("check_synapse_neurotransmitter_release", check_synapse_neurotransmitter_release),
        ("check_myelination_conduction_speed", check_myelination_conduction_speed),
        ("check_refractory_period_bounded", check_refractory_period_bounded),
        ("check_synaptic_weight_fraction", check_synaptic_weight_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
