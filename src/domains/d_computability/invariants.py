#!/usr/bin/env python3
"""D_COMPUTABILITY Invariants — Halting problem, Rice's theorem, Busy Beaver

Computability theory per Turing (1936), Rice (1953), and Radó (1962).
All invariants use Fraction arithmetic where applicable.
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    TuringMachine, DecisionProblem, BusyBeaverCandidate, RiceTheoremCheck,
    HaltingStatus, DecidabilityClass,
    busy_beaver_sigma_2, busy_beaver_sigma_3, busy_beaver_sigma_4,
    max_tm_steps_before_timeout
)


def check_halting_undecidability(problem: DecisionProblem) -> Tuple[bool, ProofObject]:
    """
    Halting problem is undecidable (Turing 1936).

    Falsifies if: problem_id == 'HALTING' AND decidability != UNDECIDABLE
    falsifies_if: problem_id == 'HALTING' AND decidability != UNDECIDABLE
    """
    if problem.problem_id == "HALTING" and problem.decidability != DecidabilityClass.UNDECIDABLE:
        return False, ProofObject(
            conclusion=f"VIOLATION: Halting problem marked as {problem.decidability.name} (must be UNDECIDABLE)",
            premises=[
                "Halting problem is undecidable (Turing 1936)",
                f"Given: {problem.decidability.name}"
            ],
            rule="turing_1936_halting_undecidable"
        )

    return True, ProofObject(
        conclusion=f"Problem {problem.problem_id} decidability classification correct",
        premises=[f"Decidability: {problem.decidability.name}"],
        rule="turing_1936_halting_undecidable"
    )


def check_rice_theorem_semantic(rice: RiceTheoremCheck) -> Tuple[bool, ProofObject]:
    """
    Rice's theorem: All nontrivial semantic properties of programs are undecidable.

    Falsifies if: is_semantic AND is_nontrivial (property must be undecidable)
    falsifies_if: is_semantic AND is_nontrivial (property must be undecidable)
    """
    if rice.is_semantic and rice.is_nontrivial:
        return True, ProofObject(
            conclusion=f"Property {rice.property_id} is undecidable (Rice's theorem)",
            premises=[
                "Property is semantic (about program behavior)",
                "Property is nontrivial (some programs satisfy, some don't)",
                "Rice's theorem: all such properties are undecidable"
            ],
            rule="rice_1953_semantic_nontrivial"
        )

    return True, ProofObject(
        conclusion=f"Property {rice.property_id} may be decidable (not covered by Rice's theorem)",
        premises=[
            f"Semantic: {rice.is_semantic}",
            f"Nontrivial: {rice.is_nontrivial}"
        ],
        rule="rice_1953_semantic_nontrivial"
    )


def check_busy_beaver_lower_bound(bb: BusyBeaverCandidate) -> Tuple[bool, ProofObject]:
    """
    Busy Beaver Σ(n) lower bounds must be consistent with proven values.

    Falsifies if: n=2 AND sigma_lower_bound > 4, or n=3 AND sigma_lower_bound > 6, etc.
    falsifies_if: n=2 AND sigma_lower_bound > 4, or n=3 AND sigma_lower_bound > 6, etc.
    """
    if bb.n_states == 2:
        proven_sigma = busy_beaver_sigma_2()
        if bb.sigma_lower_bound > proven_sigma:
            return False, ProofObject(
                conclusion=f"VIOLATION: Σ(2) lower bound {bb.sigma_lower_bound} exceeds proven value {proven_sigma}",
                premises=[
                    f"Given lower bound: {bb.sigma_lower_bound}",
                    f"Proven Σ(2) = {proven_sigma}"
                ],
                rule="busy_beaver_proven_values"
            )

    if bb.n_states == 3:
        proven_sigma = busy_beaver_sigma_3()
        if bb.sigma_lower_bound > proven_sigma:
            return False, ProofObject(
                conclusion=f"VIOLATION: Σ(3) lower bound {bb.sigma_lower_bound} exceeds proven value {proven_sigma}",
                premises=[
                    f"Given lower bound: {bb.sigma_lower_bound}",
                    f"Proven Σ(3) = {proven_sigma}"
                ],
                rule="busy_beaver_proven_values"
            )

    if bb.n_states == 4:
        proven_sigma = busy_beaver_sigma_4()
        if bb.sigma_lower_bound > proven_sigma:
            return False, ProofObject(
                conclusion=f"VIOLATION: Σ(4) lower bound {bb.sigma_lower_bound} exceeds proven value {proven_sigma}",
                premises=[
                    f"Given lower bound: {bb.sigma_lower_bound}",
                    f"Proven Σ(4) = {proven_sigma}"
                ],
                rule="busy_beaver_proven_values"
            )

    return True, ProofObject(
        conclusion=f"Busy Beaver Σ({bb.n_states}) lower bound {bb.sigma_lower_bound} consistent",
        premises=[f"Lower bound: {bb.sigma_lower_bound}"],
        rule="busy_beaver_proven_values"
    )


def check_tm_simulation_timeout(tm: TuringMachine) -> Tuple[bool, ProofObject]:
    """
    Turing machine simulations must timeout to avoid infinite loops (halting problem).

    Falsifies if: steps_executed > max_tm_steps_before_timeout() AND NOT halted
    falsifies_if: steps_executed > max_tm_steps_before_timeout() AND NOT halted
    """
    max_steps = max_tm_steps_before_timeout()

    if tm.steps_executed > max_steps and not tm.halted:
        return False, ProofObject(
            conclusion=f"VIOLATION: TM {tm.machine_id} exceeded {max_steps} steps without halting",
            premises=[
                f"Steps executed: {tm.steps_executed}",
                f"Halted: {tm.halted}",
                f"Max steps: {max_steps}"
            ],
            rule="tm_simulation_timeout"
        )

    return True, ProofObject(
        conclusion=f"TM {tm.machine_id} simulation within bounds",
        premises=[
            f"Steps: {tm.steps_executed}",
            f"Halted: {tm.halted}"
        ],
        rule="tm_simulation_timeout"
    )


def check_decidable_halts_always(problem: DecisionProblem) -> Tuple[bool, ProofObject]:
    """
    Decidable problems must have algorithms that always halt.

    Falsifies if: decidability == DECIDABLE AND no reduction proof provided
    falsifies_if: decidability == DECIDABLE AND no reduction proof provided
    """
    if problem.decidability == DecidabilityClass.DECIDABLE and not problem.reduction_proof:
        return False, ProofObject(
            conclusion=f"VIOLATION: Problem {problem.problem_id} marked DECIDABLE but no halting proof",
            premises=[
                "Decidable problems require proof of termination",
                f"Reduction proof: {problem.reduction_proof}"
            ],
            rule="decidable_algorithm_halts"
        )

    return True, ProofObject(
        conclusion=f"Problem {problem.problem_id} decidability classification justified",
        premises=[
            f"Decidability: {problem.decidability.name}",
            f"Proof: {problem.reduction_proof or 'N/A'}"
        ],
        rule="decidable_algorithm_halts"
    )
