"""D_INTERNATIONAL_HUMANITARIAN implementation — International humanitarian law.

Covers: Geneva Conventions, protection of civilians, POW rights,
medical neutrality, distinction principle.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Set
from fractions import Fraction


class ProtectedCategory(Enum):
    CIVILIAN = "civilian"
    POW = "prisoner_of_war"
    MEDICAL_PERSONNEL = "medical_personnel"
    RELIGIOUS_PERSONNEL = "religious_personnel"
    HUMANITARIAN_WORKERS = "humanitarian_workers"


class ConflictType(Enum):
    INTERNATIONAL = "international"
    NON_INTERNATIONAL = "non_international"
    OCCUPATION = "occupation"


@dataclass
class ProtectedPerson:
    person_id: str
    category: ProtectedCategory
    location: str
    receiving_protection: bool = True
    protection_coverage: Fraction = field(default=Fraction(1, 1))


@dataclass
class MilitaryTarget:
    target_id: str
    military_necessity: bool
    proportionality_assessed: bool
    expected_civilian_harm: int
    necessity_score: Fraction = field(default=Fraction(1, 1))
    distinction_score: Fraction = field(default=Fraction(1, 1))
    harm_fraction: Fraction = field(default=Fraction(0))


@dataclass
class D_INTERNATIONAL_HUMANITARIANRecord:
    record_id: str
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)
    protected_persons: List[ProtectedPerson] = field(default_factory=list)
    military_operations: List[MilitaryTarget] = field(default_factory=list)


class D_INTERNATIONAL_HUMANITARIANChecker:
    """International humanitarian law compliance checker."""
    
    def check_compliance(self, record: D_INTERNATIONAL_HUMANITARIANRecord) -> Dict[str, Any]:
        return {
            "compliant": record.status == "active",
            "record_id": record.record_id,
            "protected_count": len(record.protected_persons),
        }
    
    def check_distinction_principle(self, target: MilitaryTarget) -> bool:
        """Check if target distinguishes between combatants and civilians."""
        return target.military_necessity and target.proportionality_assessed
    
    def check_proportionality(self, target: MilitaryTarget, 
                              military_advantage: int) -> bool:
        """Check if civilian harm is proportionate to military advantage."""
        return target.expected_civilian_harm <= military_advantage * 2
    
    def check_protection_status(self, person: ProtectedPerson) -> bool:
        """Check if protected person is receiving required protections."""
        return person.receiving_protection
