#!/usr/bin/env python3
"""Environmental Planning — NEPA, CEQA, EIS requirements."""

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


@dataclass
class ImpactScore:
    """Environmental impact score for a category."""
    category: ImpactCategory
    score: Fraction  # 0-100 scale
    mitigation: List[str] = field(default_factory=list)
    
    def has_mitigation(self) -> bool:
        return len(self.mitigation) > 0


@dataclass
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


@dataclass
class CommentPeriod:
    """Public comment period tracking."""
    start_date: str
    end_date: str
    days_duration: int
    
    MINIMUM_COMMENT_DAYS = 30
    
    def is_adequate(self) -> bool:
        return self.days_duration >= self.MINIMUM_COMMENT_DAYS


@dataclass
class MitigationTracker:
    """Track mitigation measure implementation."""
    required_measures: List[str]
    implemented_measures: List[str]
    
    def completion_rate(self) -> Fraction:
        if not self.required_measures:
            return Fraction(100)
        return Fraction(len(self.implemented_measures) * 100, len(self.required_measures))
    
    def is_complete(self) -> bool:
        return set(self.required_measures) <= set(self.implemented_measures)


# Environmental thresholds
SIGNIFICANT_IMPACT_THRESHOLD = Fraction(50)
MIN_MITIGATION_COMPLETION = Fraction(100)
