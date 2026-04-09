#!/usr/bin/env python3
"""Property Law — Recording, adverse possession, easements."""

from fractions import Fraction
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum, auto

class RecordingActType(Enum):
    RACE = auto()        # First to record wins
    NOTICE = auto()      # Subsequent BFP without notice wins
    RACE_NOTICE = auto() # Subsequent BFP without notice who records first wins

@dataclass
class PropertyInterest:
    """Real property interest with recording info."""
    owner: str
    legal_description: str
    date_acquired: datetime
    recorded: bool = False
    recording_date: Optional[datetime] = None

@dataclass
class AdversePossession:
    """Adverse possession claim — OCEAN elements."""
    claimant: str
    property_desc: str
    
    # OCEAN elements
    open_notorious: bool = False  # Visible possession
    continuous: bool = False      # Uninterrupted
    exclusive: bool = False       # Not shared with true owner
    adverse: bool = False         # Without permission
    notorious: bool = False       # Known to community
    
    possession_start: Optional[datetime] = None
    possession_end: Optional[datetime] = None
    
    STATUTORY_PERIOD_YEARS: int = 10  # Varies by jurisdiction
    
    def all_elements_present(self) -> bool:
        """OCEAN elements for adverse possession."""
        return all([
            self.open_notorious,
            self.continuous,
            self.exclusive,
            self.adverse,
            self.notorious,
        ])
    
    def possession_duration_years(self) -> Fraction:
        if not self.possession_start or not self.possession_end:
            return Fraction(0)
        days = (self.possession_end - self.possession_start).days
        return Fraction(days, 365)
    
    def is_valid_claim(self) -> bool:
        """Valid adverse possession requires elements + statutory period."""
        return (
            self.all_elements_present() and
            self.possession_duration_years() >= self.STATUTORY_PERIOD_YEARS
        )
