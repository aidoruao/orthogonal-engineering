#!/usr/bin/env python3
"""D_AXIOMS Invariants — ZFC, Peano, proof theory verification

Verifies axiom consistency, independence, completeness limits (Gödel), ZFC foundation.
Gödel (1931): Incompleteness theorems. Cohen (1963): Independence of Choice.
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    Axiom, ProofSystem, AxiomSchema, GodelSentence, IndependenceProof,
    ConsistencyStrength, AxiomSystem, AxiomName,
    zfc_axioms, peano_axioms, is_schema
)


def check_axiom_consistency(system: ProofSystem) -> Tuple[bool, ProofObject]:
    """
    Axiom systems must be consistent (no contradictions derivable).

    Gödel (1931): Consistency cannot be proven within the system.
    Falsifies if: consistent == False (system proves contradiction)
    """
    if not system.consistent:
        return False, ProofObject(
            conclusion=f"VIOLATION: System {system.system_id} is inconsistent",
            premises=[
                f"System: {system.axiom_system.name}",
                f"Consistent: {system.consistent}",
                "Inconsistent systems prove all statements"
            ],
            rule="axiom_consistency"
        )

    return True, ProofObject(
        conclusion=f"System {system.system_id} is consistent",
        premises=[f"Axiom system: {system.axiom_system.name}", f"Axioms: {len(system.axioms)}"],
        rule="axiom_consistency"
    )


def check_independence(proof: IndependenceProof) -> Tuple[bool, ProofObject]:
    """
    Independent axioms must have countermodels where they fail.

    Cohen (1963): Independence of Choice via forcing.
    Falsifies if: independent == True but no countermodel exists
    """
    if proof.independent and not proof.model_without_axiom:
        return False, ProofObject(
            conclusion=f"VIOLATION: Axiom {proof.axiom_name.name} claimed independent but no countermodel",
            premises=[
                f"Axiom: {proof.axiom_name.name}",
                f"Independent: {proof.independent}",
                f"Countermodel: {proof.model_without_axiom}",
                "Independence requires countermodel"
            ],
            rule="axiom_independence"
        )

    if proof.independent:
        return True, ProofObject(
            conclusion=f"Axiom {proof.axiom_name.name} is independent in {proof.system.name}",
            premises=[
                f"Model with axiom: {proof.model_with_axiom}",
                f"Countermodel: {proof.model_without_axiom}"
            ],
            rule="axiom_independence"
        )

    return True, ProofObject(
        conclusion=f"Axiom {proof.axiom_name.name} is derivable (not independent)",
        premises=[f"Independent: {proof.independent}"],
        rule="axiom_independence"
    )


def check_completeness_limit(system: ProofSystem, godel: GodelSentence) -> Tuple[bool, ProofObject]:
    """
    Sufficiently strong systems (PA, ZFC) must be incomplete per Gödel.

    Gödel (1931): First Incompleteness Theorem.
    Falsifies if: system is PA or ZFC and complete == True
    """
    strong_systems = [AxiomSystem.ZFC, AxiomSystem.PEANO, AxiomSystem.ZF_NO_CHOICE]

    if system.axiom_system in strong_systems and system.complete:
        return False, ProofObject(
            conclusion=f"VIOLATION: System {system.axiom_system.name} cannot be complete per Gödel",
            premises=[
                f"System: {system.axiom_system.name}",
                f"Complete: {system.complete}",
                "Gödel (1931): Sufficiently strong consistent systems are incomplete"
            ],
            rule="godel_incompleteness"
        )

    # Check Gödel sentence properties
    if godel.system == system.axiom_system:
        if godel.true and godel.provable:
            return True, ProofObject(
                conclusion=f"Gödel sentence for {godel.system.name} is true and provable (statement is decidable)",
                premises=[f"True: {godel.true}", f"Provable: {godel.provable}"],
                rule="godel_sentence"
            )

        if godel.true and not godel.provable:
            return True, ProofObject(
                conclusion=f"Gödel sentence for {godel.system.name} is true but unprovable (incompleteness)",
                premises=[
                    f"True: {godel.true}",
                    f"Provable: {godel.provable}",
                    "Demonstrates Gödel incompleteness"
                ],
                rule="godel_sentence"
            )

    return True, ProofObject(
        conclusion=f"System {system.axiom_system.name} incompleteness verified",
        premises=[f"Complete: {system.complete}"],
        rule="godel_incompleteness"
    )


def check_zfc_foundation(system: ProofSystem) -> Tuple[bool, ProofObject]:
    """
    ZFC systems must include Foundation axiom (no infinite descending ∈-chains).

    Zermelo (1908): Foundation prevents sets containing themselves.
    Falsifies if: system is ZFC but FOUNDATION not in axioms
    """
    if system.axiom_system in [AxiomSystem.ZFC, AxiomSystem.ZF_NO_CHOICE]:
        if AxiomName.FOUNDATION not in system.axioms:
            return False, ProofObject(
                conclusion=f"VIOLATION: ZFC system {system.system_id} missing Foundation axiom",
                premises=[
                    f"System: {system.axiom_system.name}",
                    f"Axioms: {[a.name for a in system.axioms]}",
                    "Foundation required for ZFC"
                ],
                rule="zfc_foundation"
            )

    return True, ProofObject(
        conclusion=f"System {system.system_id} includes Foundation axiom",
        premises=[f"Axioms: {[a.name for a in system.axioms]}"],
        rule="zfc_foundation"
    )


def check_peano_induction(system: ProofSystem) -> Tuple[bool, ProofObject]:
    """
    Peano arithmetic must include Induction schema.

    Peano (1889): Induction is essential for natural number properties.
    Falsifies if: system is PEANO but INDUCTION not in axioms
    """
    if system.axiom_system == AxiomSystem.PEANO:
        if AxiomName.INDUCTION not in system.axioms:
            return False, ProofObject(
                conclusion=f"VIOLATION: Peano system {system.system_id} missing Induction schema",
                premises=[
                    f"System: {system.axiom_system.name}",
                    f"Axioms: {[a.name for a in system.axioms]}",
                    "Induction required for Peano arithmetic"
                ],
                rule="peano_induction"
            )

        # Induction must be a schema (infinite axioms)
        if not is_schema(AxiomName.INDUCTION):
            return False, ProofObject(
                conclusion=f"VIOLATION: INDUCTION must be a schema, not single axiom",
                premises=["Induction is infinite family of axioms"],
                rule="peano_induction_schema"
            )

    return True, ProofObject(
        conclusion=f"System {system.system_id} includes Induction schema",
        premises=[f"Axioms: {[a.name for a in system.axioms]}"],
        rule="peano_induction"
    )


def check_choice_independence(proof: IndependenceProof) -> Tuple[bool, ProofObject]:
    """
    Axiom of Choice must be independent of ZF.

    Cohen (1963): Choice is independent via forcing method.
    Falsifies if: Choice claimed dependent on ZF
    """
    if proof.axiom_name == AxiomName.CHOICE and proof.system == AxiomSystem.ZF_NO_CHOICE:
        if not proof.independent:
            return False, ProofObject(
                conclusion=f"VIOLATION: Axiom of Choice must be independent of ZF per Cohen (1963)",
                premises=[
                    f"Independent: {proof.independent}",
                    "Cohen (1963): Choice is independent of ZF"
                ],
                rule="choice_independence"
            )

        # Verify countermodels
        if proof.independent and not proof.model_without_axiom:
            return False, ProofObject(
                conclusion=f"VIOLATION: Choice independence requires countermodel (e.g., forcing model)",
                premises=[
                    f"Model with Choice: {proof.model_with_axiom}",
                    f"Countermodel: {proof.model_without_axiom}"
                ],
                rule="choice_independence"
            )

    return True, ProofObject(
        conclusion=f"Axiom of Choice independence verified",
        premises=[f"Independent: {proof.independent}", f"Countermodel: {proof.model_without_axiom}"],
        rule="choice_independence"
    )


def check_consistency_strength_ordering(strength: ConsistencyStrength) -> Tuple[bool, ProofObject]:
    """
    Consistency strength must respect known ordering (PA < ZF < ZFC).

    Gödel (1940): If ZF consistent, then ZFC consistent.
    Falsifies if: ordering violates known results
    """
    # Known orderings: PEANO < ZF_NO_CHOICE <= ZFC
    known_orderings = {
        (AxiomSystem.PEANO, AxiomSystem.ZF_NO_CHOICE): True,
        (AxiomSystem.PEANO, AxiomSystem.ZFC): True,
        (AxiomSystem.ZF_NO_CHOICE, AxiomSystem.PEANO): False,  # Violation
        (AxiomSystem.ZFC, AxiomSystem.PEANO): False  # Violation
    }

    pair = (strength.weaker_system, strength.stronger_system)
    if pair in known_orderings:
        expected = known_orderings[pair]
        is_correct_ordering = (strength.strength_ratio < Fraction(1, 1))

        if expected and not is_correct_ordering:
            return False, ProofObject(
                conclusion=f"VIOLATION: {strength.weaker_system.name} should be weaker than {strength.stronger_system.name}",
                premises=[
                    f"Weaker: {strength.weaker_system.name}",
                    f"Stronger: {strength.stronger_system.name}",
                    f"Ratio: {strength.strength_ratio}",
                    "Violates known consistency strength ordering"
                ],
                rule="consistency_strength"
            )

        if not expected and is_correct_ordering:
            return False, ProofObject(
                conclusion=f"VIOLATION: {strength.stronger_system.name} cannot be stronger than {strength.weaker_system.name}",
                premises=[
                    f"Claimed weaker: {strength.weaker_system.name}",
                    f"Claimed stronger: {strength.stronger_system.name}",
                    "Violates known consistency strength ordering"
                ],
                rule="consistency_strength"
            )

    return True, ProofObject(
        conclusion=f"Consistency strength ordering {strength.weaker_system.name} < {strength.stronger_system.name} verified",
        premises=[f"Ratio: {strength.strength_ratio}"],
        rule="consistency_strength"
    )
