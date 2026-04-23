"""D_INTERNATIONAL_CRIMINAL implementation — International criminal law.

Covers: war crimes, crimes against humanity, genocide, jurisdiction,
ICC procedures, extradition.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
from fractions import Fraction
from datetime import datetime


class CrimeType(Enum):
    WAR_CRIME = "war_crime"
    CRIME_AGAINST_HUMANITY = "crime_against_humanity"
    GENOCIDE = "genocide"
    AGGRESSION = "aggression"


class CaseStatus(Enum):
    PRELIMINARY_EXAMINATION = "preliminary_examination"
    INVESTIGATION = "investigation"
    TRIAL = "trial"
    APPEAL = "appeal"
    CLOSED = "closed"


@dataclass
class Case:
    case_id: str
    crime_type: CrimeType
    status: CaseStatus
    opened_at: datetime
    defendant: str
    jurisdiction: str
    charges: List[str] = field(default_factory=list)
    charge_gravity: Fraction = field(default=Fraction(1, 1))
    jurisdiction_strength: Fraction = field(default=Fraction(1, 1))


@dataclass
class Evidence:
    evidence_id: str
    case_id: str
    type: str
    authenticity_verified: bool
    chain_of_custody: List[str] = field(default_factory=list)
    evidence_weight: Fraction = field(default=Fraction(1, 1))
    custody_links: int = field(default=2)
    custody_gaps: int = field(default=0)


@dataclass
class D_INTERNATIONAL_CRIMINALRecord:
    record_id: str
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)
    cases: List[Case] = field(default_factory=list)


class D_INTERNATIONAL_CRIMINALChecker:
    """International criminal law compliance checker."""
    
    def check_compliance(self, record: D_INTERNATIONAL_CRIMINALRecord) -> Dict[str, Any]:
        return {
            "compliant": record.status == "active",
            "record_id": record.record_id,
            "case_count": len(record.cases),
        }
    
    def check_jurisdiction(self, case: Case, territorial_state: str, 
                           defendant_nationality: str) -> bool:
        """Check if ICC has jurisdiction over case."""
        # ICC jurisdiction: territorial or nationality basis
        return case.jurisdiction in [territorial_state, defendant_nationality, "universal"]
    
    def verify_evidence_chain(self, evidence: Evidence) -> bool:
        """Verify chain of custody for evidence."""
        return len(evidence.chain_of_custody) > 0 and evidence.authenticity_verified
    
    def check_complementarity(self, domestic_proceedings: bool, 
                              domestic_willing_able: bool) -> bool:
        """Check complementarity principle - ICC acts only when domestic courts won't/can't."""
        return not domestic_proceedings or not domestic_willing_able
