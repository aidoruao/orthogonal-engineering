"""D_RELIGIOUS_LIBERTY implementation — RFRA, Free Exercise, Establishment

Layer: 3 (Constitutional)
CardinalStrength: PREDICATIVE
Source: First Amendment, RFRA, RLUIPA, Sherbert/Yoder/Lukumi
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional, List
from enum import Enum, auto
from fractions import Fraction


class ReligiousClaimType(Enum):
    """Types of religious liberty claims."""
    FREE_EXERCISE = auto()
    ESTABLISHMENT_CLAUSE = auto()
    RFRACL AIM = auto()
    RLUIPA_CLAIM = auto()


class BurdenLevel(Enum):
    """Level of burden on religious exercise."""
    NONE = auto()
    INCIDENTAL = auto()
    SUBSTANTIAL = auto()
    SEVERE = auto()


@dataclass
class ReligiousAccommodation:
    """RFRA/RLUIPA religious accommodation analysis."""
    claim_id: str
    claimant_id: str
    claim_type: ReligiousClaimType
    
    # Religious exercise
    religious_belief_sincere: bool
    religious_practice_desc: str
    
    # Government burden
    government_interest: str
    burden_level: BurdenLevel
    least_restrictive_alternative_exists: bool
    
    # Accommodation outcome
    accommodation_granted: bool
    accommodation_description: str
    
    def is_substantial_burden(self) -> bool:
        """Check if burden is substantial (RFRA standard)."""
        return self.burden_level == BurdenLevel.SUBSTANTIAL or self.burden_level == BurdenLevel.SEVERE


@dataclass
class ReligiousExemption:
    """Religious exemption from generally applicable law."""
    exemption_id: str
    law_id: str
    
    # Exemption scope
    exempted_practices: List[str]
    exempted_persons_count: Fraction
    
    # Limits
    compelling_interest_override: bool
    harm_to_third_parties: Fraction
    
    # Time limits
    temporary: bool
    expiration_date: Optional[str]


# RFRA standards
RFRA_COMPELLING_INTEREST_REQUIRED = True
RLUIPA_PRISONER_STANDARD = "substantial_burden"


def rfra_substantial_burden_threshold() -> BurdenLevel:
    """RFRA requires substantial burden on religious exercise."""
    return BurdenLevel.SUBSTANTIAL
