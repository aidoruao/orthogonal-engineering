#!/usr/bin/env python3
"""Occupational Safety — OSHA general duty, PEL, fall protection."""

from fractions import Fraction
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum, auto

class ViolationType(Enum):
    SERIOUS = auto()
    WILLFUL = auto()
    REPEATED = auto()
    OTHER_THAN_SERIOUS = auto()

@dataclass
class Workplace:
    employer: str
    location: str
    industry: str
    employees_count: int

@dataclass
class Hazard:
    """Recognized workplace hazard."""
    description: str
    location: str
    chemical_exposure_ppm: Fraction = Fraction(0)
    permissible_exposure_limit: Fraction = Fraction(0)
    abatement_feasible: bool = False
    abatement_completeness_score: Fraction = Fraction(1, 1)
    
    def exceeds_pel(self) -> bool:
        """OSHA PEL: Permissible Exposure Limit exceeded."""
        if self.permissible_exposure_limit <= Fraction(0):
            return False
        return self.chemical_exposure_ppm > self.permissible_exposure_limit

@dataclass
class FallProtection:
    """OSHA 1926.501 fall protection requirements."""
    work_height_feet: Fraction
    guardrails_installed: bool = False
    personal_fall_arrest: bool = False
    safety_nets: bool = False
    fall_protection_coverage: Fraction = Fraction(1, 1)
    
    FALL_PROTECTION_THRESHOLD = Fraction(6)  # 6 feet
    
    def protection_required(self) -> bool:
        """Fall protection required at 6+ feet."""
        return self.work_height_feet >= self.FALL_PROTECTION_THRESHOLD
    
    def is_compliant(self) -> bool:
        """Compliant if protection not required OR protection provided."""
        if not self.protection_required():
            return True
        return self.guardrails_installed or self.personal_fall_arrest or self.safety_nets

@dataclass
class OSHAInspection:
    """OSHA inspection record."""
    workplace: Workplace
    inspection_date: str
    hazards_found: List[Hazard]
    citations_issued: List[ViolationType]
    
    def has_general_duty_violation(self) -> bool:
        """OSH Act § 5(a)(1): Free from recognized hazards."""
        for hazard in self.hazards_found:
            if hazard.abatement_feasible:
                return True
        return False
