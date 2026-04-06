"""D_FEDERALISM implementation — Federal/State Structure

Implements federalism: enumerated federal powers, 10th Amendment residual
state powers, and Supremacy Clause conflict resolution.

Layer: 1 (Constitutional)
CardinalStrength: INACCESSIBLE
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Set, Dict
from enum import Enum, auto
from fractions import Fraction


class GovernmentLevel(Enum):
    """Levels of government in federal system."""
    FEDERAL = auto()
    STATE = auto()
    LOCAL = auto()


class PowerType(Enum):
    """Types of government powers under federalism."""
    # Enumerated federal powers (Article I, Section 8)
    REGULATE_INTERSTATE_COMMERCE = auto()
    DECLARE_WAR = auto()
    COIN_MONEY = auto()
    ESTABLISH_POST_OFFICES = auto()
    
    # Reserved state powers (10th Amendment)
    POLICE_POWER = auto()
    EDUCATION = auto()
    LOCAL_LAW_ENFORCEMENT = auto()
    ELECTION_ADMINISTRATION = auto()
    
    # Concurrent powers
    TAXATION = auto()
    ESTABLISH_COURTS = auto()
    
    # Prohibited powers
    BILLS_OF_ATTAINDER = auto()
    EX_POST_FACTO = auto()


# Federal enumerated powers (exclusive)
FEDERAL_POWERS: Set[PowerType] = {
    PowerType.REGULATE_INTERSTATE_COMMERCE,
    PowerType.DECLARE_WAR,
    PowerType.COIN_MONEY,
    PowerType.ESTABLISH_POST_OFFICES,
}

# State reserved powers (10th Amendment)
STATE_POWERS: Set[PowerType] = {
    PowerType.POLICE_POWER,
    PowerType.EDUCATION,
    PowerType.LOCAL_LAW_ENFORCEMENT,
    PowerType.ELECTION_ADMINISTRATION,
}

# Concurrent powers (both can exercise)
CONCURRENT_POWERS: Set[PowerType] = {
    PowerType.TAXATION,
    PowerType.ESTABLISH_COURTS,
}


@dataclass
class SupremacyClause:
    """
    Supremacy Clause resolution: federal > state > local.
    
    Article VI: "This Constitution, and the Laws of the United States
    which shall be made in Pursuance thereof... shall be the supreme
    Law of the Land."
    """
    
    federal_law: str
    state_law: str
    conflict_description: str
    
    def resolve_conflict(self) -> Dict:
        """
        Resolve conflict between federal and state law.
        
        Federal law preempts state law per Supremacy Clause.
        """
        return {
            "supremacy_applies": True,
            "prevailing_law": self.federal_law,
            "preempted_law": self.state_law,
            "resolution": "Federal law prevails per Supremacy Clause",
            "state_law_invalid": True,
        }
    
    @staticmethod
    def get_hierarchy() -> List[GovernmentLevel]:
        """Return government hierarchy (highest to lowest authority)."""
        return [GovernmentLevel.FEDERAL, GovernmentLevel.STATE, GovernmentLevel.LOCAL]


@dataclass
class PowerExercise:
    """Record of a government level exercising a power."""
    level: GovernmentLevel
    power: PowerType
    description: str
    
    def is_constitutional(self) -> bool:
        """Check if this power exercise is constitutional under federalism."""
        # Federal can exercise enumerated and concurrent powers
        if self.level == GovernmentLevel.FEDERAL:
            return self.power in FEDERAL_POWERS or self.power in CONCURRENT_POWERS
        
        # State can exercise reserved and concurrent powers
        if self.level == GovernmentLevel.STATE:
            return self.power in STATE_POWERS or self.power in CONCURRENT_POWERS
        
        # Local has limited powers delegated by state
        if self.level == GovernmentLevel.LOCAL:
            return self.power == PowerType.POLICE_POWER  # Local police power only
        
        return False


class FederalismChecker:
    """Federalism compliance checker (enumerated powers, supremacy clause)."""
    
    def __init__(self):
        self.power_exercises: List[PowerExercise] = []
        self.supremacy_conflicts_resolved: List[Dict] = []
    
    def check_power_exercise(
        self,
        level: GovernmentLevel,
        power: PowerType,
        description: str,
    ) -> bool:
        """
        Check if power exercise is constitutional.
        
        Returns True if constitutional, False if violates federalism.
        """
        exercise = PowerExercise(
            level=level,
            power=power,
            description=description,
        )
        self.power_exercises.append(exercise)
        
        return exercise.is_constitutional()
    
    def check_federal_power(self, power: PowerType, description: str) -> bool:
        """Check if federal exercise of power is constitutional."""
        return self.check_power_exercise(GovernmentLevel.FEDERAL, power, description)
    
    def check_state_power(self, power: PowerType, description: str) -> bool:
        """Check if state exercise of power is constitutional."""
        return self.check_power_exercise(GovernmentLevel.STATE, power, description)
    
    def check_supremacy(
        self,
        federal_law: str,
        state_law: str,
        conflict_description: str,
    ) -> Dict:
        """
        Apply Supremacy Clause to resolve federal-state conflict.
        
        Federal law always prevails.
        """
        supremacy = SupremacyClause(
            federal_law=federal_law,
            state_law=state_law,
            conflict_description=conflict_description,
        )
        
        resolution = supremacy.resolve_conflict()
        self.supremacy_conflicts_resolved.append(resolution)
        return resolution
    
    def is_tenth_amendment_violation(
        self,
        federal_action: str,
        power_type: PowerType,
    ) -> bool:
        """
        Check if federal action violates 10th Amendment.
        
        10th Amendment: Powers not delegated to federal government
        are reserved to the states.
        """
        # If power is exclusively state and federal tries to exercise it
        if power_type in STATE_POWERS and power_type not in CONCURRENT_POWERS:
            return True
        return False
    
    def get_federalism_summary(self) -> dict:
        """Get summary of federalism checks."""
        constitutional = sum(1 for p in self.power_exercises if p.is_constitutional())
        unconstitutional = len(self.power_exercises) - constitutional
        
        return {
            "total_power_exercises": len(self.power_exercises),
            "constitutional": constitutional,
            "unconstitutional": unconstitutional,
            "supremacy_conflicts_resolved": len(self.supremacy_conflicts_resolved),
        }


def check_federalism_compliance(
    level: GovernmentLevel,
    power: PowerType,
    description: str,
) -> bool:
    """
    Convenience function to check federalism compliance.
    
    Usage:
        if not check_federalism_compliance(
            level=GovernmentLevel.FEDERAL,
            power=PowerType.EDUCATION,  # State power!
            description="Federal education mandate",
        ):
            print("Violates 10th Amendment")
    """
    checker = FederalismChecker()
    return checker.check_power_exercise(level, power, description)
