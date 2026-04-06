"""D_INTERNATIONAL_CRIMINAL implementation — International Criminal Law"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum, auto


class CoreCrime(Enum):
    """Core crimes under Rome Statute."""
    GENOCIDE = auto()
    CRIMES_AGAINST_HUMANITY = auto()
    WAR_CRIMES = auto()
    AGGRESSION = auto()


@dataclass
class UniversalJurisdictionCase:
    """Case subject to universal jurisdiction."""
    case_id: str
    crime: CoreCrime
    suspect: str
    location: str
    evidence_present: bool
    
    def can_prosecute(self) -> bool:
        """Check if case can be prosecuted under universal jurisdiction."""
        # Universal jurisdiction applies to core crimes
        return self.evidence_present and self.crime in CoreCrime


class InternationalCriminalLaw:
    """Universal jurisdiction and ICC complementarity checker."""
    
    def __init__(self):
        self.cases: List[UniversalJurisdictionCase] = []
    
    def check_complementarity(
        self,
        domestic_proceedings: bool,
        domestic_willing: bool,
        domestic_able: bool,
    ) -> bool:
        """
        Check ICC complementarity principle.
        
        ICC can only prosecute if domestic court is:
        - Unwilling (shielding), OR
        - Unable (collapse/jurisdiction issues)
        """
        if not domestic_proceedings:
            return True  # ICC can prosecute
        if not domestic_willing:
            return True  # Domestic shielding
        if not domestic_able:
            return True  # Domestic unable
        return False  # Domestic proceedings adequate
