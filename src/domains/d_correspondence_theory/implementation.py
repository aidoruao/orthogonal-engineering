"""D_CORRESPONDENCE_THEORY implementation -- Correspondence structures.

Part 4 of Forensic Offensive Campaign.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Callable, Dict, Tuple


@dataclass(frozen=True)
class Morphism:
    """A morphism in the correspondence category.

    falsifies_if: source or target is empty, or mapping is not callable.
    """
    name: str
    source: str
    target: str
    mapping: Callable[[str], str]


@dataclass(frozen=True)
class CorrespondenceDiagram:
    """A commutative diagram h o f = g.

    Objects: A, B, C
    Morphisms: f: A->B, g: A->C, h: B->C
    falsifies_if: composition does not commute for any test input.
    """
    diagram_id: str
    objects: Tuple[str, ...]
    morphisms: Dict[str, Morphism]
    test_inputs: Tuple[str, ...]


@dataclass(frozen=True)
class CorrespondenceState:
    """Aggregate state of the correspondence framework.

    falsifies_if: coverage_ratio < Fraction(1, 1).
    """
    state_id: str
    diagrams: Tuple[CorrespondenceDiagram, ...]
    coverage_ratio: Fraction


DOMAIN_METADATA = {
    "name": "d_correspondence_theory",
    "version": "1.0.0",
    "part": "4",
    "campaign": "CAMPAIGN-FORENSIC-OFFENSIVE-001",
}
