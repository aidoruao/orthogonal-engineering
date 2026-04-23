#!/usr/bin/env python3
"""Evidence Law — FRE 401-702.

FRE 401; FRE 403; FRE 801-802;
Daubert v. Merrell Dow Pharmaceuticals, 509 U.S. 579 (1993);
Kumho Tire Co. v. Carmichael, 526 U.S. 137 (1999).
"""

from fractions import Fraction
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum, auto


class EvidenceType(Enum):
    TESTIMONIAL = auto()
    DOCUMENTARY = auto()
    PHYSICAL = auto()
    EXPERT = auto()


@dataclass(frozen=True)
class Evidence:
    """Evidence with probative and prejudicial scores."""
    evidence_type: EvidenceType
    description: str
    probative_value: Fraction  # 0-1 scale
    prejudicial_effect: Fraction  # 0-1 scale (FRE 403)
    hearsay: bool = False
    hearsay_exception: Optional[str] = None

    def relevance_ratio(self) -> Fraction:
        """FRE 401: Relevant if tendency to make fact more/less probable."""
        return self.probative_value

    def probative_prejudice_ratio(self) -> Fraction:
        """FRE 403: probative_value / (probative_value + prejudicial_effect)."""
        denom = self.probative_value + self.prejudicial_effect
        if denom == Fraction(0):
            return Fraction(1, 1)
        return self.probative_value / denom

    def hearsay_reliability_score(self) -> Fraction:
        """FRE 801/802: 1 if not hearsay, 4/5 if exception, 0 if no exception."""
        if not self.hearsay:
            return Fraction(1, 1)
        if self.hearsay_exception:
            return Fraction(4, 5)
        return Fraction(0, 1)

    def is_relevant(self) -> bool:
        return self.probative_value > Fraction(0)

    def is_admissible_403(self) -> bool:
        return self.probative_value >= self.prejudicial_effect


@dataclass(frozen=True)
class ExpertWitness:
    """Expert testimony under Daubert."""
    name: str
    field: str
    qualifications: List[str]
    methodology_reliable: bool = False  # Daubert standard
    fit_to_facts: bool = False
    methodology_score: Fraction = Fraction(0)  # 0–1 scale

    def daubert_reliability_score(self) -> Fraction:
        """FRE 702/Daubert: reliability score (Daubert v. Merrell Dow)."""
        if self.methodology_reliable and self.fit_to_facts:
            return Fraction(1, 1)
        return self.methodology_score

    def is_admissible_daubert(self) -> bool:
        return self.daubert_reliability_score() >= Fraction(7, 10)
