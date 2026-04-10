"""D_PSYCHOLOGY implementation — Psychology & Behavioral Science

Layer: 4 (Institutional)
CardinalStrength: PREDICATIVE

Standards:
- APA Ethics Code
- Informed consent
- IRB requirements
- Statistical significance
- Effect size reporting
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from fractions import Fraction


@dataclass
class ResearchStudy:
    """Psychological research study."""
    study_id: str
    title: str
    principal_investigator: str
    
    # Ethics
    irb_approved: bool
    irb_protocol_number: Optional[str]
    informed_consent_obtained: bool
    
    # Design
    participants_enrolled: int
    participants_completed: int
    
    # Results
    hypothesis_supported: Optional[bool]
    effect_size: Optional[Fraction]
    p_value: Optional[Fraction]
    
    def completion_rate(self) -> Fraction:
        if self.participants_enrolled == 0:
            return Fraction(0)
        return Fraction(self.participants_completed, self.participants_enrolled)
    
    def statistically_significant(self, alpha: Fraction = Fraction(5, 100)) -> bool:
        if self.p_value is None:
            return False
        return self.p_value < alpha


@dataclass
class Participant:
    """Research participant."""
    participant_id: str
    study_id: str
    
    consent_date: datetime
    withdrawal_date: Optional[datetime]
    
    vulnerable_population: bool  # Children, prisoners, etc.
    capacity_to_consent: bool
    
    def has_withdrawn(self) -> bool:
        return self.withdrawal_date is not None


@dataclass
class PsychologyChecker:
    """Checker for research ethics and validity."""
    studies: List[ResearchStudy] = field(default_factory=list)
    participants: List[Participant] = field(default_factory=list)
    
    def non_irb_approved(self) -> List[ResearchStudy]:
        return [s for s in self.studies if not s.irb_approved]
    
    def consent_violations(self) -> List[Participant]:
        return [p for p in self.participants 
                if not p.capacity_to_consent and not p.vulnerable_population]
    
    def p_hacking_indicators(self) -> List[ResearchStudy]:
        """Multiple studies with p just below threshold."""
        return [s for s in self.studies 
                if s.p_value and Fraction(4, 100) < s.p_value < Fraction(6, 100)]
