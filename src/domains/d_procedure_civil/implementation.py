#!/usr/bin/env python3
"""Civil Procedure — FRCP compliance framework.

FRCP 23(a); Bell Atlantic Corp. v. Twombly, 550 U.S. 544 (2007);
Celotex Corp. v. Catrett, 477 U.S. 317 (1986).
"""

from fractions import Fraction
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Set
from enum import Enum, auto


class MotionType(Enum):
    RULE_12_B_6 = auto()  # Failure to state a claim
    SUMMARY_JUDGMENT = auto()  # FRCP 56
    CLASS_CERTIFICATION = auto()  # FRCP 23


@dataclass(frozen=True)
class Party:
    name: str
    contacts_with_forum: Fraction = Fraction(0)  # For jurisdiction


@dataclass(frozen=True)
class Lawsuit:
    """Civil action with FRCP compliance tracking."""
    plaintiff: Party
    defendant: Party
    case_number: str
    filed_date: Optional[datetime]

    # Pleadings
    complaint_allegations: List[str] = field(default_factory=list)
    answer_filed: bool = False

    # FRCP 23 Class Action
    class_action: bool = False
    class_size_estimate: int = 0
    commonality: bool = False
    typicality: bool = False
    adequacy: bool = False
    numerosity: bool = False

    # FRCP 56 Summary Judgment
    summary_judgment_motions: List[MotionType] = field(default_factory=list)
    genuine_dispute_exists: bool = True
    disputed_fact_count: int = 0

    def class_certification_score(self) -> Fraction:
        """Fraction of FRCP 23(a) elements met plus numerosity ratio."""
        elements = 0
        if self.commonality: elements += 1
        if self.typicality: elements += 1
        if self.adequacy: elements += 1
        if self.numerosity: elements += 1
        element_score = Fraction(elements, 4)
        if not self.class_action:
            return element_score
        size_ratio = Fraction(
            min(self.class_size_estimate, MIN_CLASS_SIZE),
            MIN_CLASS_SIZE
        ) if MIN_CLASS_SIZE > 0 else Fraction(1, 1)
        return (element_score + size_ratio) / Fraction(2, 1)

    def plausibility_score(self) -> Fraction:
        """Fraction of minimum factual allegations required (Twombly)."""
        min_required = 3
        return Fraction(min(len(self.complaint_allegations), min_required), min_required)

    def summary_judgment_readiness(self) -> Fraction:
        """Readiness for summary judgment: 1 if no genuine dispute (Celotex)."""
        if self.genuine_dispute_exists:
            return Fraction(0, 1)
        return Fraction(1, 1)

    def get_class_certification_requirements(self) -> Set[str]:
        """FRCP 23(a) requirements: numerosity, commonality, typicality, adequacy."""
        reqs = set()
        if self.numerosity: reqs.add("numerosity")
        if self.commonality: reqs.add("commonality")
        if self.typicality: reqs.add("typicality")
        if self.adequacy: reqs.add("adequacy")
        return reqs

    def is_summary_judgment_appropriate(self) -> bool:
        """FRCP 56: No genuine dispute of material fact."""
        return not self.genuine_dispute_exists


# FRCP thresholds
MIN_CLASS_SIZE = 40  # Numerosity threshold
SUMMARY_JUDGMENT_DEADLINE_DAYS = Fraction(30)
