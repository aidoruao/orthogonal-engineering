#!/usr/bin/env python3
"""Property Law — Recording, adverse possession, easements."""

from fractions import Fraction
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum, auto


class RecordingActType(Enum):
    RACE = auto()        # First to record wins
    NOTICE = auto()      # Subsequent BFP without notice wins
    RACE_NOTICE = auto() # Subsequent BFP without notice who records first wins


@dataclass(frozen=True)
class PropertyInterest:
    """Real property interest with recording info."""
    owner: str
    legal_description: str
    date_acquired: Optional[datetime] = None
    recorded: bool = False
    recording_date: Optional[datetime] = None

    def recording_priority_score(self, against: "PropertyInterest") -> Fraction:
        """Priority score based on recording status and timing.

        Citation: Restatement (Third) of Property § 7.1.
        Returns 1 when this interest clearly prevails, 0 when it clearly loses,
        and intermediate values for ties or unrecorded chains.
        """
        if self.recorded and not against.recorded:
            return Fraction(1, 1)
        if not self.recorded and against.recorded:
            return Fraction(0, 1)
        if self.recorded and against.recorded:
            if self.recording_date and against.recording_date:
                if self.recording_date < against.recording_date:
                    return Fraction(1, 1)
                if self.recording_date > against.recording_date:
                    return Fraction(0, 1)
            return Fraction(1, 2)
        # Neither recorded — fall back to acquisition date
        if self.date_acquired and against.date_acquired:
            if self.date_acquired < against.date_acquired:
                return Fraction(2, 3)
            if self.date_acquired > against.date_acquired:
                return Fraction(1, 3)
        return Fraction(1, 2)


@dataclass(frozen=True)
class AdversePossession:
    """Adverse possession claim — OCEAN elements."""
    claimant: str
    property_desc: str

    # OCEAN elements
    open_notorious: bool = False   # Visible possession
    continuous: bool = False       # Uninterrupted
    exclusive: bool = False        # Not shared with true owner
    adverse: bool = False          # Without permission
    notorious: bool = False        # Known to community

    possession_start: Optional[datetime] = None
    possession_end: Optional[datetime] = None

    statutory_period_years: Fraction = Fraction(10)

    def element_completeness(self) -> Fraction:
        """Fraction of OCEAN elements satisfied (0 to 1).

        Citation: Muscari v. Villani, 830 A.2d 975 (N.J. 2003).
        """
        elements = [
            self.open_notorious,
            self.continuous,
            self.exclusive,
            self.adverse,
            self.notorious,
        ]
        present = sum(1 for e in elements if e)
        return Fraction(present, 5)

    def possession_duration_years(self) -> Fraction:
        """Compute years of possession as Fraction."""
        if not self.possession_start or not self.possession_end:
            return Fraction(0, 1)
        days = (self.possession_end - self.possession_start).days
        return Fraction(days, 365)

    def claim_strength(self) -> Fraction:
        """Overall claim strength combining element completeness and duration."""
        completeness = self.element_completeness()
        duration = self.possession_duration_years()
        if duration >= self.statutory_period_years:
            duration_factor = Fraction(1, 1)
        else:
            duration_factor = duration / self.statutory_period_years
        return completeness * duration_factor
