"""D_CORPORATE_LAW implementation — Corporate Law

Implements corporate governance principles including fiduciary duty,
self-dealing prohibition, and corporate veil piercing analysis.

Layer: 2 (Statutory)
CardinalStrength: PREDICATIVE
Source: Delaware General Corporation Law (DGCL), Model Business Corporation Act (MBCA),
        Restatement (Second) of Agency
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from fractions import Fraction


class FiduciaryDutyType(Enum):
    """Types of fiduciary duties owed by corporate directors/officers."""
    DUTY_OF_CARE = auto()          # Duty to act with informed judgment
    DUTY_OF_LOYALTY = auto()       # Duty to prioritize corporation's interests
    DUTY_OF_OBEDIENCE = auto()     # Duty to act within authority
    DUTY_OF_DISCLOSURE = auto()    # Duty to disclose material information


class SelfDealingType(Enum):
    """Categories of self-dealing transactions."""
    DIRECT_INTEREST = auto()       # Director has direct financial interest
    INDIRECT_INTEREST = auto()     # Director has indirect/family interest
    CORPORATE_OPPORTUNITY = auto() # Usurping corporate opportunity
    COMPETING_BUSINESS = auto()    # Competing with the corporation


@dataclass
class Director:
    """Corporate director with potential conflicts."""
    name: str
    director_id: str
    outside_directorships: List[str] = field(default_factory=list)
    financial_interests: Dict[str, Fraction] = field(default_factory=dict)
    
    def has_interest_in(self, entity_name: str) -> bool:
        """Check if director has financial interest in an entity."""
        return entity_name in self.financial_interests


@dataclass
class CorporateTransaction:
    """A transaction subject to fiduciary duty analysis."""
    transaction_id: str
    description: str
    counterparty: str
    value: Fraction
    directors_involved: List[Director] = field(default_factory=list)
    approved_by_board: bool = False
    approved_by_disinterested: bool = False
    disclosure_complete: bool = False
    fairness_opinion_obtained: bool = False
    
    @property
    def involves_self_dealing(self) -> bool:
        """Check if any involved director has interest in counterparty."""
        for director in self.directors_involved:
            if director.has_interest_in(self.counterparty):
                return True
        return False


@dataclass
class Shareholder:
    """Corporate shareholder."""
    name: str
    shares_owned: int
    total_shares_outstanding: int
    
    @property
    def ownership_percentage(self) -> Fraction:
        """Calculate ownership percentage."""
        if self.total_shares_outstanding == 0:
            return Fraction(0)
        return Fraction(self.shares_owned, self.total_shares_outstanding)
    
    def is_controlling(self, threshold: Fraction = Fraction(50, 100)) -> bool:
        """Check if shareholder has controlling interest."""
        return self.ownership_percentage >= threshold


class FiduciaryDutyAnalyzer:
    """Analyzer for fiduciary duty compliance.
    
    Directors owe duties of care and loyalty to the corporation—
    reflecting the biblical principle of stewardship (Luke 16:10:
    "Whoever can be trusted with very little can also be trusted
    with much").
    """
    
    def __init__(self):
        self.violations: List[Dict] = []
    
    def analyze_duty_of_loyalty(
        self,
        transaction: CorporateTransaction,
    ) -> Dict:
        """Analyze compliance with duty of loyalty.
        
        Args:
            transaction: The transaction to analyze
            
        Returns:
            Analysis result with compliance status and issues
        """
        issues = []
        
        if transaction.involves_self_dealing:
            if not transaction.disclosure_complete:
                issues.append("Self-dealing without full disclosure")
            
            if not transaction.approved_by_disinterested:
                issues.append("Self-dealing not approved by disinterested directors")
            
            if not transaction.fairness_opinion_obtained and transaction.value > Fraction(1_000_000):
                issues.append("Material self-dealing without fairness opinion")
        
        return {
            "duty": FiduciaryDutyType.DUTY_OF_LOYALTY,
            "compliant": len(issues) == 0,
            "issues": issues,
            "requires_entire_fairness": transaction.involves_self_dealing and not transaction.approved_by_disinterested,
        }
    
    def analyze_duty_of_care(
        self,
        transaction: CorporateTransaction,
        board_informed: bool = True,
        decision_documented: bool = True,
    ) -> Dict:
        """Analyze compliance with duty of care.
        
        Args:
            transaction: The transaction to analyze
            board_informed: Whether board was fully informed
            decision_documented: Whether decision process was documented
            
        Returns:
            Analysis result
        """
        issues = []
        
        if not board_informed:
            issues.append("Board not adequately informed")
        
        if not decision_documented:
            issues.append("Decision process not documented")
        
        if transaction.value > Fraction(10_000_000) and not transaction.fairness_opinion_obtained:
            issues.append("Major transaction without fairness opinion")
        
        return {
            "duty": FiduciaryDutyType.DUTY_OF_CARE,
            "compliant": len(issues) == 0,
            "issues": issues,
        }
    
    def check_self_dealing_compliance(
        self,
        transaction: CorporateTransaction,
    ) -> Dict:
        """Comprehensive self-dealing compliance check.
        
        Under DGCL §144, self-dealing is valid if:
        1. Approved by disinterested directors after full disclosure, OR
        2. Approved by shareholders after full disclosure, OR
        3. Transaction is fair to the corporation
        
        Args:
            transaction: The transaction to check
            
        Returns:
            Compliance analysis
        """
        if not transaction.involves_self_dealing:
            return {
                "is_self_dealing": False,
                "compliant": True,
                "safe_harbor_applies": True,
            }
        
        # Safe harbor 1: Disinterested director approval
        if transaction.approved_by_disinterested and transaction.disclosure_complete:
            return {
                "is_self_dealing": True,
                "compliant": True,
                "safe_harbor": "DGCL_144_a",  # Board approval
            }
        
        # Safe harbor 2 would be shareholder approval
        # (not implemented in this simplified version)
        
        # Safe harbor 3: Entire fairness standard applies
        return {
            "is_self_dealing": True,
            "compliant": None,  # Requires judicial review
            "requires_entire_fairness": True,
            "issues": ["Transaction requires entire fairness review"],
        }


class CorporateVeilAnalyzer:
    """Analyzer for corporate veil piercing (alter ego doctrine).
    
    Courts may pierce the corporate veil when:
    1. Unity of interest and ownership exists
    2. Failure to pierce would promote injustice
    """
    
    def __init__(self):
        self.factors: Dict[str, bool] = {}
    
    def analyze_veil_piercing_risk(
        self,
        corporation: str,
        shareholder: Shareholder,
        commingling_of_funds: bool = False,
        inadequate_capitalization: bool = False,
        failure_to_follow_formalities: bool = False,
        siphoning_of_funds: bool = False,
        non_functioning_officers: bool = False,
        sole_shareholder: bool = False,
    ) -> Dict:
        """Analyze risk of corporate veil being pierced.
        
        Args:
            corporation: Name of corporation
            shareholder: Shareholder to analyze
            commingling_of_funds: Personal/corporate funds mixed
            inadequate_capitalization: Undercapitalized at formation
            failure_to_follow_formalities: No meetings, minutes, etc.
            siphoning_of_funds: Excessive distributions
            non_functioning_officers: Officers are figureheads
            sole_shareholder: Only one shareholder
            
        Returns:
            Risk assessment
        """
        factors = {
            "commingling_of_funds": commingling_of_funds,
            "inadequate_capitalization": inadequate_capitalization,
            "failure_to_follow_formalities": failure_to_follow_formalities,
            "siphoning_of_funds": siphoning_of_funds,
            "non_functioning_officers": non_functioning_officers,
            "sole_shareholder": sole_shareholder,
        }
        
        factor_count = sum(1 for v in factors.values() if v)
        
        # Risk assessment
        if factor_count >= 4:
            risk_level = "EXTREME"
        elif factor_count >= 2:
            risk_level = "HIGH"
        elif factor_count >= 1:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"
        
        return {
            "corporation": corporation,
            "shareholder": shareholder.name,
            "risk_level": risk_level,
            "factors_present": factor_count,
            "factors": factors,
            "piercing_likely": risk_level in ("EXTREME", "HIGH"),
        }


class CorporateComplianceChecker:
    """Comprehensive corporate law compliance checker."""
    
    def __init__(self):
        self.fiduciary_analyzer = FiduciaryDutyAnalyzer()
        self.veil_analyzer = CorporateVeilAnalyzer()
    
    def check_transaction_compliance(
        self,
        transaction: CorporateTransaction,
        board_informed: bool = True,
        decision_documented: bool = True,
    ) -> Dict:
        """Full compliance check for a corporate transaction."""
        
        loyalty_check = self.fiduciary_analyzer.analyze_duty_of_loyalty(transaction)
        care_check = self.fiduciary_analyzer.analyze_duty_of_care(
            transaction, board_informed, decision_documented
        )
        self_dealing_check = self.fiduciary_analyzer.check_self_dealing_compliance(transaction)
        
        all_issues = []
        all_issues.extend(loyalty_check.get("issues", []))
        all_issues.extend(care_check.get("issues", []))
        all_issues.extend(self_dealing_check.get("issues", []))
        
        return {
            "transaction_id": transaction.transaction_id,
            "compliant": len(all_issues) == 0,
            "issues": all_issues,
            "duty_of_loyalty": loyalty_check,
            "duty_of_care": care_check,
            "self_dealing": self_dealing_check,
        }


def check_self_dealing(
    director_name: str,
    counterparty: str,
    transaction_value: Fraction,
    director_has_interest: bool,
    approved_by_disinterested: bool = False,
    full_disclosure: bool = False,
) -> Dict:
    """Convenience function to check self-dealing compliance.
    
    Usage:
        result = check_self_dealing(
            director_name="John Director",
            counterparty="Director's LLC",
            transaction_value=Fraction(500000),
            director_has_interest=True,
            approved_by_disinterested=True,
            full_disclosure=True,
        )
        if not result["compliant"]:
            print(f"Issues: {result['issues']}")
    """
    director = Director(
        name=director_name,
        director_id="001",
        financial_interests={counterparty: Fraction(100)} if director_has_interest else {},
    )
    
    transaction = CorporateTransaction(
        transaction_id="T001",
        description="Related party transaction",
        counterparty=counterparty,
        value=transaction_value,
        directors_involved=[director],
        approved_by_disinterested=approved_by_disinterested,
        disclosure_complete=full_disclosure,
    )
    
    analyzer = FiduciaryDutyAnalyzer()
    return analyzer.check_self_dealing_compliance(transaction)
