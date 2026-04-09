#!/usr/bin/env python3
"""Evidence Law — FRE 401-702."""

from fractions import Fraction
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum, auto

class EvidenceType(Enum):
    TESTIMONIAL = auto()
    DOCUMENTARY = auto()
    PHYSICAL = auto()
    EXPERT = auto()

@dataclass
class Evidence:
    evidence_type: EvidenceType
    description: str
    probative_value: Fraction  # 0-1 scale
    prejudicial_effect: Fraction  # 0-1 scale (FRE 403)
    hearsay: bool = False
    hearsay_exception: Optional[str] = None
    
    def is_relevant(self) -> bool:
        """FRE 401: Relevant if tendency to make fact more/less probable."""
        return self.probative_value > Fraction(0)
    
    def is_admissible_403(self) -> bool:
        """FRE 403: Exclude if probative value substantially outweighed by prejudice."""
        return self.probative_value >= self.prejudicial_effect

@dataclass
class ExpertWitness:
    name: str
    field: str
    qualifications: List[str]
    methodology_reliable: bool = False  # Daubert standard
    fit_to_facts: bool = False
    
    def is_admissible_daubert(self) -> bool:
        """FRE 702/Daubert: Expert testimony requirements."""
        return self.methodology_reliable and self.fit_to_facts
