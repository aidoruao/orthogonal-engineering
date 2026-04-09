#!/usr/bin/env python3
"""
Consumer Protection Domain — FTC Act, Magnuson-Moss

Key statutes:
- FTC Act § 5: Unfair/deceptive practices
- Magnuson-Moss Warranty Act
"""

from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum, auto


class ClaimType(Enum):
    PERFORMANCE = auto()
    HEALTH = auto()
    SAFETY = auto()
    ENVIRONMENTAL = auto()


@dataclass
class ProductClaim:
    """Marketing claim about a product."""
    claim_id: str
    product_id: str
    claim_text: str
    claim_type: ClaimType
    has_evidence: bool = False
    evidence_quality: str = "none"  # none, weak, moderate, strong


@dataclass
class ClaimVerifier:
    """Verify marketing claims against evidence."""
    claims: List[ProductClaim]
    
    def find_unsubstantiated(self) -> List[ProductClaim]:
        """Find claims without adequate evidence."""
        return [
            c for c in self.claims
            if not c.has_evidence or c.evidence_quality in ["none", "weak"]
        ]


@dataclass
class Warranty:
    """Product warranty under Magnuson-Moss."""
    warranty_id: str
    product_id: str
    full_warranty: bool = False  # Full vs limited
    duration_months: int = 12
    covered_parts: List[str] = field(default_factory=list)
    exclusions: List[str] = field(default_factory=list)
    
    def covers_part(self, part: str) -> bool:
        return part in self.covered_parts and part not in self.exclusions


@dataclass
class WarrantyChecker:
    """Check warranty compliance."""
    warranty: Warranty
    repair_request: str
    
    def is_covered(self) -> bool:
        return self.warranty.covers_part(self.repair_request)


@dataclass
class Recall:
    """Product recall notice."""
    recall_id: str
    product_id: str
    hazard_description: str
    remedy: str
    notification_sent: bool = False
    remedy_available: bool = False


@dataclass
class RecallTracker:
    """Track recall notification completeness."""
    recall: Recall
    affected_units: int = 0
    notified_units: int = 0
    
    def notification_rate(self) -> Fraction:
        if self.affected_units == 0:
            return Fraction(100)
        return Fraction(self.notified_units * 100, self.affected_units)
    
    def is_complete(self) -> bool:
        return self.notification_rate() >= Fraction(95)


# Consumer protection thresholds
MIN_EVIDENCE_QUALITY = "moderate"
MIN_NOTIFICATION_RATE = Fraction(95)
FULL_WARRANTY_MIN_MONTHS = 12
