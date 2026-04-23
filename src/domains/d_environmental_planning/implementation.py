#!/usr/bin/env python3
"""Environmental Planning — NEPA, CEQA, EIS requirements.

42 U.S.C. § 4332(2)(C) (NEPA); CEQA Guidelines § 15000;
Sierra Club v. U.S. Army Corps of Engineers, 701 F.3d 120 (5th Cir. 2012).
"""

from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum, auto


class ImpactCategory(Enum):
    AIR = auto()
    WATER = auto()
    BIOLOGY = auto()
    NOISE = auto()
    CULTURAL = auto()


@dataclass(frozen=True)
class ImpactScore:
    """Environmental impact score for a category."""
    category: ImpactCategory
    score: Fraction  # 0-100 scale
    mitigation: List[str] = field(default_factory=list)

    def normalized_score(self) -> Fraction:
        """Score normalized to 0–1 (NEPA significance threshold)."""
        return Fraction(self.score, 100)


@dataclass(frozen=True)
class EnvironmentalImpactStatement:
    """EIS with impact scores."""
    project_id: str
    impact_scores: List[ImpactScore]

    def total_impact(self) -> Fraction:
        if not self.impact_scores:
            return Fraction(0)
        return sum(i.score for i in self.impact_scores) / len(self.impact_scores)

    def significant_impacts(self) -> List[ImpactScore]:
        return [i for i in self.impact_scores if i.score > Fraction(50)]


@dataclass(frozen=True)
class CommentPeriod:
    """Public comment period tracking."""
    start_date: str
    end_date: str
    days_duration: int

    MINIMUM_COMMENT_DAYS: Fraction = Fraction(30, 1)

    def adequacy_ratio(self) -> Fraction:
        """Fraction of minimum comment period provided (NEPA)."""
        return Fraction(self.days_duration, 1) / self.MINIMUM_COMMENT_DAYS

    def is_adequate(self) -> bool:
        return self.adequacy_ratio() >= Fraction(1, 1)


@dataclass(frozen=True)
class MitigationTracker:
    """Track mitigation measure implementation."""
    required_measures: List[str]
    implemented_measures: List[str]

    def completion_ratio(self) -> Fraction:
        """Fraction of required measures implemented (CEQA)."""
        if not self.required_measures:
            return Fraction(1, 1)
        return Fraction(len(self.implemented_measures), len(self.required_measures))

    def completion_rate(self) -> Fraction:
        if not self.required_measures:
            return Fraction(100)
        return Fraction(len(self.implemented_measures) * 100, len(self.required_measures))

    def is_complete(self) -> bool:
        return set(self.required_measures) <= set(self.implemented_measures)


# Environmental thresholds
SIGNIFICANT_IMPACT_THRESHOLD = Fraction(50)
MIN_MITIGATION_COMPLETION = Fraction(100)
