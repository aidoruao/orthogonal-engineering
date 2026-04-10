"""D_PHARMA implementation — Pharmaceutical Regulation

Layer: 4 (Institutional)
CardinalStrength: PREDICATIVE

Standards:
- FDA 21 CFR
- GMP (Good Manufacturing Practice)
- Clinical trial phases
- Adverse event reporting
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from fractions import Fraction


@dataclass
class Drug:
    """Pharmaceutical product."""
    ndc: str  # National Drug Code
    name: str
    manufacturer: str
    
    approval_date: Optional[datetime]
    approval_type: str  # NDA, ANDA, BLA
    
    gmp_certified: bool
    recall_status: bool
    
    def is_approved(self) -> bool:
        return self.approval_date is not None


@dataclass
class ClinicalTrial:
    """FDA clinical trial."""
    nct_number: str
    phase: int  # 1, 2, 3, 4
    
    enrolled: int
    completed: int
    
    ind_active: bool  # Investigational New Drug
    
    primary_completion: Optional[datetime]
    
    def enrollment_rate(self) -> Fraction:
        if self.enrolled == 0:
            return Fraction(0)
        return Fraction(self.completed, self.enrolled)


@dataclass
class AdverseEvent:
    """FDA adverse event report."""
    report_id: str
    drug_ndc: str
    
    serious: bool
    death: bool
    
    report_date: datetime
    fda_received: datetime
    
    def reported_timely(self) -> bool:
        days = (self.fda_received - self.report_date).days
        if self.serious:
            return days <= 15
        return days <= 90


@dataclass
class PharmaChecker:
    """Checker for pharma compliance."""
    drugs: List[Drug] = field(default_factory=list)
    trials: List[ClinicalTrial] = field(default_factory=list)
    events: List[AdverseEvent] = field(default_factory=list)
    
    def unapproved_drugs(self) -> List[Drug]:
        return [d for d in self.drugs if not d.is_approved()]
    
    def gmp_violations(self) -> List[Drug]:
        return [d for d in self.drugs if not d.gmp_certified]
    
    def late_ae_reports(self) -> List[AdverseEvent]:
        return [e for e in self.events if not e.reported_timely()]
    
    def ind_violations(self) -> List[ClinicalTrial]:
        return [t for t in self.trials if t.phase < 4 and not t.ind_active]
