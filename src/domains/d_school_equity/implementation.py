"""D_SCHOOL_EQUITY implementation — Educational Equity & Access

Layer: 4 (Institutional)
CardinalStrength: PREDICATIVE

Standards:
- Title I (ESSA)
- IDEA (special education)
- Brown v. Board
- Disparate impact analysis
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict
from fractions import Fraction


@dataclass
class School:
    """Educational institution."""
    school_id: str
    name: str
    district: str
    
    enrollment_total: int
    enrollment_by_race: Dict[str, int]
    
    title_i_eligible: bool
    title_i_funding: Fraction
    
    per_pupil_spending: Fraction
    state_avg_spending: Fraction
    
    def spending_equity_ratio(self) -> Fraction:
        if self.state_avg_spending == 0:
            return Fraction(1)
        return self.per_pupil_spending / self.state_avg_spending


@dataclass
class DisciplineRecord:
    """Student discipline by demographic."""
    school_id: str
    year: int
    
    suspensions_total: int
    suspensions_by_race: Dict[str, int]
    
    enrollment_by_race: Dict[str, int]
    
    def suspension_rate(self, race: str) -> Fraction:
        enrolled = self.enrollment_by_race.get(race, 0)
        if enrolled == 0:
            return Fraction(0)
        return Fraction(self.suspensions_by_race.get(race, 0), enrolled)
    
    def disparate_impact_ratio(self, race_a: str, race_b: str) -> Fraction:
        rate_a = self.suspension_rate(race_a)
        rate_b = self.suspension_rate(race_b)
        if rate_b == 0:
            return Fraction(0)
        return rate_a / rate_b


@dataclass
class SchoolEquityChecker:
    """Checker for educational equity."""
    schools: List[School] = field(default_factory=list)
    discipline: List[DisciplineRecord] = field(default_factory=list)
    
    def underfunded_schools(self, threshold: Fraction) -> List[School]:
        return [s for s in self.schools if s.spending_equity_ratio() < threshold]
    
    def disparate_impact_violations(self, threshold: Fraction) -> List[DisciplineRecord]:
        """Disparate impact > 3:1 or < 1:3."""
        violations = []
        for d in self.discipline:
            races = list(d.enrollment_by_race.keys())
            for i, r1 in enumerate(races):
                for r2 in races[i+1:]:
                    ratio = d.disparate_impact_ratio(r1, r2)
                    if ratio > threshold or ratio < Fraction(1) / threshold:
                        violations.append(d)
        return violations
