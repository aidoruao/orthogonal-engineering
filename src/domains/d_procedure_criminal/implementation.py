#!/usr/bin/env python3
"""Criminal Procedure — 4th, 5th, 6th Amendments."""

from fractions import Fraction
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional
from enum import Enum, auto

class ChargeSeverity(Enum):
    MISDEMEANOR = auto()
    FELONY = auto()
    CAPITAL = auto()

@dataclass
class Arrest:
    """4th Amendment arrest requirements."""
    suspect: str
    arrest_date: datetime
    probable_cause_exists: bool = False
    warrant_issued: bool = False
    warrant_based_on_oath: bool = False
    
    def is_valid(self) -> bool:
        """Valid arrest requires probable cause (warrant or exigent)."""
        return self.probable_cause_exists

@dataclass
class Interrogation:
    """Miranda requirements."""
    suspect: str
    custodial: bool = False
    interrogation: bool = False
    miranda_given: bool = False
    rights_waived: bool = False
    
    def miranda_required(self) -> bool:
        """Miranda warnings required for custodial interrogation."""
        return self.custodial and self.interrogation
    
    def statement_admissible(self) -> bool:
        """Statement admissible if Miranda given or not required."""
        if not self.miranda_required():
            return True
        return self.miranda_given and self.rights_waived

@dataclass
class CriminalCase:
    """Criminal case with speedy trial tracking."""
    case_number: str
    defendant: str
    charge: str
    severity: ChargeSeverity
    arrest_date: datetime
    indictment_date: Optional[datetime] = None
    trial_date: Optional[datetime] = None
    
    def speedy_trial_violation(self) -> bool:
        """Federal Speedy Trial Act: 70 days from indictment."""
        if not self.indictment_date or not self.trial_date:
            return False
        elapsed = (self.trial_date - self.indictment_date).days
        return elapsed > 70

# Speedy trial threshold
SPEEDY_TRIAL_DAYS = Fraction(70)
