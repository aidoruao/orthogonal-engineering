"""D_RESTORATIVE_JUSTICE implementation — Restorative Justice, Victim-Offender Mediation

Layer: 3 (Criminal Justice)
CardinalStrength: PREDICATIVE
Source: Victim Offender Reconciliation Act, Circle sentencing, Family group conferencing
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum, auto
from fractions import Fraction


class RJProgramType(Enum):
    """Types of restorative justice programs."""
    VICTIM_OFFENDER_MEDIATION = auto()
    PEACEMAKING_CIRCLE = auto()
    FAMILY_GROUP_CONFERENCE = auto()
    REPARATIVE_PROBATION = auto()


class RJOutcome(Enum):
    """Outcomes of restorative justice process."""
    AGREEMENT_REACHED = auto()
    NO_AGREEMENT = auto()
    WITHDRAWN = auto()
    REFERRED_TRADITIONAL = auto()


@dataclass
class RestorativeJusticeCase:
    """A restorative justice case."""
    case_id: str
    program_type: RJProgramType
    offense_type: str
    
    # Participants
    victim_participating: bool
    offender_id: str
    victim_id: Optional[str]
    community_representatives: int
    
    # Process
    preparation_meetings: int
    conference_held: bool
    agreement_terms: List[str]
    
    # Outcomes
    outcome: RJOutcome
    restitution_amount: Fraction
    community_service_hours: Fraction
    completion_status: str  # "completed", "in_progress", "breached"
    
    # Satisfaction (0-1 scale)
    victim_satisfaction: Fraction
    offender_satisfaction: Fraction
    
    def get_participation_score(self) -> Fraction:
        """Calculate participation quality score."""
        score = Fraction(0)
        if self.victim_participating:
            score += Fraction(1, 3)
        if self.conference_held:
            score += Fraction(1, 3)
        if len(self.agreement_terms) > 0:
            score += Fraction(1, 3)
        return score
    
    def is_successful(self) -> bool:
        """Check if case completed successfully."""
        return self.outcome == RJOutcome.AGREEMENT_REACHED and self.completion_status == "completed"


@dataclass
class RJProgramMetrics:
    """Program-wide restorative justice metrics."""
    program_id: str
    program_type: RJProgramType
    
    # Volume
    cases_referred: int
    cases_accepted: int
    cases_completed: int
    cases_breached: int
    
    # Outcomes
    restitution_collected: Fraction
    restitution_owed: Fraction
    community_service_completed: Fraction
    community_service_assigned: Fraction
    
    # Recidivism tracking
    recidivism_count: int
    tracked_participants: int
    
    def get_completion_rate(self) -> Fraction:
        """Calculate agreement completion rate."""
        if self.cases_completed + self.cases_breached == 0:
            return Fraction(0)
        return Fraction(self.cases_completed, self.cases_completed + self.cases_breached)
    
    def get_restitution_rate(self) -> Fraction:
        """Calculate restitution collection rate."""
        if self.restitution_owed == 0:
            return Fraction(1)
        return self.restitution_collected / self.restitution_owed


# Restorative justice standards
MIN_VICTIM_SATISFACTION_TARGET = Fraction(7, 10)  # 70%
MIN_COMPLETION_RATE = Fraction(6, 10)  # 60%
MIN_PREPARATION_MEETINGS = 1


def victim_satisfaction_target() -> Fraction:
    """Target victim satisfaction rate."""
    return MIN_VICTIM_SATISFACTION_TARGET


def completion_rate_target() -> Fraction:
    """Target agreement completion rate."""
    return MIN_COMPLETION_RATE
