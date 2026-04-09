#!/usr/bin/env python3
"""
Administrative Law Implementation — APA Compliance Framework

Key regulatory thresholds:
- Notice-and-comment: minimum 30-day comment period (APA § 553)
- Exhaustion: administrative remedies must be exhausted before judicial review
- Chevron deference: agency interpretation of ambiguous statutes
- Record rule: decision must be based on administrative record
"""

from fractions import Fraction
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Set
from enum import Enum, auto


class RulemakingType(Enum):
    INFORMAL = auto()      # APA § 553(b)(A) - notice and comment
    FORMAL = auto()        # APA § 556-557 - on-the-record hearing
    DIRECT_FINAL = auto()  # Minor amendments, effective unless adverse comments
    INTERPRETIVE = auto()  # Exempt from notice-and-comment


class JudicialReviewStandard(Enum):
    ARBITRARY_CAPRICIOUS = auto()   # APA § 706(2)(A)
    SUBSTANTIAL_EVIDENCE = auto()   # APA § 706(2)(E) - formal proceedings
    DE_NOVO = auto()                # APA § 706(2)(F) - de novo review


@dataclass
class Agency:
    """Federal administrative agency."""
    name: str
    enabling_act: str  # Citation to organic statute
    url: str
    rules_promulgated: List['Rulemaking'] = field(default_factory=list)
    
    def promulgate_rule(self, rule: 'Rulemaking') -> None:
        """Add a rulemaking to this agency's record."""
        self.rules_promulgated.append(rule)


@dataclass 
class Comment:
    """Public comment on proposed rule."""
    commenter: str
    text: str
    date_submitted: datetime
    supports_rule: bool = False
    
    def get_word_count(self) -> int:
        """Count words in comment text."""
        return len(self.text.split())


@dataclass
class Rulemaking:
    """APA rulemaking proceeding."""
    docket_number: str
    agency: Agency
    title: str
    rule_type: RulemakingType
    
    # Dates
    notice_date: Optional[datetime] = None
    comment_period_open: Optional[datetime] = None
    comment_period_close: Optional[datetime] = None
    final_rule_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    
    # Content
    proposed_text: str = ""
    final_text: str = ""
    comments_received: List[Comment] = field(default_factory=list)
    
    # Chevron analysis
    statutory_authority: str = ""
    statutory_ambiguity: bool = False
    
    def get_comment_period_days(self) -> Fraction:
        """Calculate the comment period duration in days."""
        if not self.comment_period_open or not self.comment_period_close:
            return Fraction(0)
        delta = self.comment_period_close - self.comment_period_open
        return Fraction(delta.days)
    
    def get_comment_count(self) -> int:
        """Total comments received."""
        return len(self.comments_received)
    
    def get_supporting_comments(self) -> List[Comment]:
        """Comments supporting the rule."""
        return [c for c in self.comments_received if c.supports_rule]
    
    def get_opposing_comments(self) -> List[Comment]:
        """Comments opposing the rule."""
        return [c for c in self.comments_received if not c.supports_rule]


@dataclass
class AdministrativeRecord:
    """The administrative record for judicial review."""
    rulemaking: Rulemaking
    documents: List[Dict] = field(default_factory=list)
    
    def add_document(self, doc_type: str, content: str, date: datetime) -> None:
        """Add a document to the administrative record."""
        self.documents.append({
            "type": doc_type,
            "content": content,
            "date": date.isoformat(),
        })
    
    def get_document_count(self) -> int:
        """Total documents in the record."""
        return len(self.documents)


@dataclass
class ExhaustionClaim:
    """Track exhaustion of administrative remedies."""
    claimant: str
    agency: Agency
    issue_raised: str
    date_agency_decision: Optional[datetime] = None
    date_judicial_filing: Optional[datetime] = None
    remedies_sought: List[str] = field(default_factory=list)
    remedies_exhausted: List[str] = field(default_factory=list)
    
    def is_exhausted(self) -> bool:
        """Check if all remedies have been exhausted."""
        return set(self.remedies_sought) <= set(self.remedies_exhausted)
    
    def days_between_decision_and_filing(self) -> Fraction:
        """Days between final agency decision and judicial filing."""
        if not self.date_agency_decision or not self.date_judicial_filing:
            return Fraction(0)
        delta = self.date_judicial_filing - self.date_agency_decision
        return Fraction(delta.days)


# Threshold constants (APA-based)
MIN_COMMENT_PERIOD_DAYS = Fraction(30)  # APA § 553 standard
MAX_NOTICE_PUBLICATION_DAYS = Fraction(60)  # Publication timing
MIN_NOTICE_TO_COMMENT_GAP = Fraction(0)  # Same-day acceptable


def calculate_chevron_deference(
    statutory_text: str, 
    agency_interpretation: str,
    ambiguity_score: Fraction  # 0-1 scale, 1 = completely ambiguous
) -> JudicialReviewStandard:
    """
    Apply Chevron deference analysis.
    
    Chevron Step 1: Has Congress spoken directly? If yes, use statutory text.
    Chevron Step 2: If ambiguous, is agency interpretation reasonable?
    """
    if ambiguity_score < Fraction(1, 10):
        # Statute is clear — no deference, apply plain meaning
        return JudicialReviewStandard.DE_NOVO
    elif ambiguity_score < Fraction(5, 10):
        # Some ambiguity — arbitrary and capricious review
        return JudicialReviewStandard.ARBITRARY_CAPRICIOUS
    else:
        # Significant ambiguity — substantial deference in formal proceedings
        return JudicialReviewStandard.SUBSTANTIAL_EVIDENCE


def check_arbitrary_capricious_factors(rule: Rulemaking) -> Dict[str, bool]:
    """
    Check factors for arbitrary and capricious review under APA § 706(2)(A).
    
    Factors:
    1. Failed to consider important aspect of problem
    2. Offered explanation counter to evidence
    3. Explanation implausible
    4. Departed from prior policy without justification
    """
    return {
        "considered_comments": rule.get_comment_count() > 0,
        "explained_changes": len(rule.final_text) > 0,
        "rational_connection": rule.statutory_authority != "",
        "consistent_with_record": True,  # Would require full record analysis
    }


def is_final_agency_action(rule: Rulemaking) -> bool:
    """
    Check if rulemaking constitutes final agency action under 
    Bennett v. Spear (1997): (1) consummation, (2) legal consequences.
    """
    has_consummation = rule.final_rule_date is not None
    has_legal_consequences = rule.effective_date is not None
    return has_consummation and has_legal_consequences
