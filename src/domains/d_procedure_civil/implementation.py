#!/usr/bin/env python3
"""Civil Procedure — FRCP compliance framework."""

from fractions import Fraction
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Set
from enum import Enum, auto

class MotionType(Enum):
    RULE_12_B_6 = auto()  # Failure to state a claim
    SUMMARY_JUDGMENT = auto()  # FRCP 56
    CLASS_CERTIFICATION = auto()  # FRCP 23

@dataclass
class Party:
    name: str
    contacts_with_forum: Fraction = Fraction(0)  # For jurisdiction

@dataclass
class Lawsuit:
    """Civil action with FRCP compliance tracking."""
    plaintiff: Party
    defendant: Party
    case_number: str
    filed_date: datetime
    
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
