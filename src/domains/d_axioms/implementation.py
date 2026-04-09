"""D_AXIOMS implementation — ZFC, Peano, Proof Theory, Axiom Systems

Layer: 1 (Foundational)
CardinalStrength: IMPREDICATIVE

Axiom systems: ZFC (Zermelo-Fraenkel + Choice), Peano Arithmetic, proof theory.
Gödel (1931): Incompleteness theorems. Tarski (1933): Truth undefinability.
"""

from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from enum import Enum
from typing import List, Optional


class AxiomSystem(Enum):
    """Axiom system classification"""
    ZFC = 1          # Zermelo-Fraenkel set theory + Axiom of Choice
    PEANO = 2        # Peano arithmetic (PA)
    ZF_NO_CHOICE = 3 # ZF without Choice
    HEYTING_ARITHMETIC = 4  # Intuitionistic arithmetic


class AxiomName(Enum):
    """ZFC and Peano axioms"""
    # ZFC axioms
    EXTENSIONALITY = 1
    PAIRING = 2
    UNION = 3
    POWER_SET = 4
    INFINITY = 5
    REPLACEMENT = 6
    FOUNDATION = 7
    CHOICE = 8
    # Peano axioms
    ZERO_IS_NATURAL = 9
    SUCCESSOR_NATURAL = 10
    ZERO_NOT_SUCCESSOR = 11
    SUCCESSOR_INJECTIVE = 12
    INDUCTION = 13


@dataclass
class Axiom:
    """Formal axiom in a system"""
    axiom_name: AxiomName
    system: AxiomSystem
    statement: str  # Formal statement
    independent: bool  # Whether axiom is independent of others


@dataclass
class ProofSystem:
    """Formal proof system"""
    system_id: str
    axiom_system: AxiomSystem
    axioms: List[AxiomName]
    consistent: bool  # Whether system is consistent
    complete: bool    # Whether system is complete (false for PA, ZFC)


@dataclass
class AxiomSchema:
    """Axiom schema (infinite family of axioms)"""
    schema_name: str
    system: AxiomSystem
    num_instances: Optional[int]  # None for infinite schemas (e.g., Replacement)


@dataclass
class GodelSentence:
    """Gödel sentence for incompleteness"""
    system: AxiomSystem
    provable: bool
    true: bool
    statement: str


@dataclass
class IndependenceProof:
    """Independence proof for axiom"""
    axiom_name: AxiomName
    system: AxiomSystem
    independent: bool
    model_with_axiom: str
    model_without_axiom: str  # Countermodel where axiom fails


@dataclass
class ConsistencyStrength:
    """Consistency strength ordering between systems"""
    weaker_system: AxiomSystem
    stronger_system: AxiomSystem
    strength_ratio: Fraction  # Relative consistency strength


def zfc_axioms() -> List[AxiomName]:
    """Return list of ZFC axioms"""
    return [
        AxiomName.EXTENSIONALITY,
        AxiomName.PAIRING,
        AxiomName.UNION,
        AxiomName.POWER_SET,
        AxiomName.INFINITY,
        AxiomName.REPLACEMENT,
        AxiomName.FOUNDATION,
        AxiomName.CHOICE
    ]


def peano_axioms() -> List[AxiomName]:
    """Return list of Peano axioms"""
    return [
        AxiomName.ZERO_IS_NATURAL,
        AxiomName.SUCCESSOR_NATURAL,
        AxiomName.ZERO_NOT_SUCCESSOR,
        AxiomName.SUCCESSOR_INJECTIVE,
        AxiomName.INDUCTION
    ]


def is_schema(axiom: AxiomName) -> bool:
    """Check if axiom is actually a schema (infinite family)"""
    # Replacement and Induction are schemas
    return axiom in [AxiomName.REPLACEMENT, AxiomName.INDUCTION]
