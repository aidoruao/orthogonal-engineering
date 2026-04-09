#!/usr/bin/env python3
"""Healthcare Law — Stark, Anti-Kickback, EMTALA, HIPAA."""

from fractions import Fraction
from dataclasses import dataclass
from typing import List
from enum import Enum, auto

class ViolationType(Enum):
    STARK = auto()
    ANTI_KICKBACK = auto()
    EMTALA = auto()
    HIPAA = auto()

@dataclass
class Physician:
    name: str
    npi: str
    has_financial_relationship: bool = False

@dataclass
class Referral:
    referring_physician: Physician
    referred_entity: str
    designated_health_service: bool = False
    compensation_arrangement: bool = False
    
    def violates_stark(self) -> bool:
        """Stark Law: No self-referral for DHS with financial relationship."""
        return (
            self.designated_health_service and 
            self.compensation_arrangement and
            self.referring_physician.has_financial_relationship
        )

@dataclass
class EMTPatient:
    """EMTALA patient screening requirements."""
    arrived_datetime: str
    screened: bool = False
    stabilized: bool = False
    transferred: bool = False
    
    def emtala_violation(self) -> bool:
        """EMTALA requires screening and stabilization."""
        return not (self.screened and (self.stabilized or self.transferred))

@dataclass
class PHI_Access:
    """HIPAA minimum necessary standard."""
    requested_phi: List[str]
    minimum_necessary: List[str]
    
    def exceeds_minimum_necessary(self) -> bool:
        """HIPAA: Disclose only minimum necessary."""
        return len(self.requested_phi) > len(self.minimum_necessary)
