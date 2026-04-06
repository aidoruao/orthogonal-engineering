"""D_SECURITIES_LAW implementation — Securities Law

Implements securities regulation under Securities Act of 1933
(registration) and Securities Exchange Act of 1934 (anti-fraud,
insider trading, reporting).

Layer: 2 (Statutory)
CardinalStrength: PREDICATIVE
Source: 15 U.S.C. §77a (Securities Act), 15 U.S.C. §78a (Exchange Act)

Biblical: Proverbs 11:1 — "The LORD detests dishonest scales, but
accurate weights find favor with him."

Also: Leviticus 19:35-36 — "Do not use dishonest standards when
measuring length, weight or quantity."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction


class SecurityType(Enum):
    """Types of securities."""
    COMMON_STOCK = auto()
    PREFERRED_STOCK = auto()
    CORPORATE_BOND = auto()
    GOVERNMENT_BOND = auto()
    MUTUAL_FUND = auto()
    ETF = auto()
    OPTION = auto()
    FUTURE = auto()
    PRIVATE_PLACEMENT = auto()
    RESTRICTED_STOCK = auto()


class TransactionType(Enum):
    """Types of securities transactions."""
    PURCHASE = auto()
    SALE = auto()
    SHORT_SALE = auto()
    OPTION_EXERCISE = auto()


class InvestorType(Enum):
    """Investor classification."""
    ACCREDITED = auto()
    NON_ACCREDITED = auto()
    INSTITUTIONAL = auto()
    RETAIL = auto()


@dataclass
class Security:
    """A security instrument."""
    cusip: str
    issuer_name: str
    security_type: SecurityType
    
    # Registration status
    registered_with_sec: bool
    registration_effective_date: Optional[datetime] = None
    
    # Private placement exemption
    exemption_claimed: Optional[str] = None  # "Reg D", "Reg S", etc.
    
    # Restrictions
    restricted: bool = False
    legend_removal_eligible: Optional[datetime] = None
    
    def requires_registration(self) -> bool:
        """Check if security requires SEC registration."""
        if self.registered_with_sec:
            return False  # Already registered
        
        # Private placements exempt
        if self.exemption_claimed:
            return False
        
        return True


@dataclass
class Transaction:
    """A securities transaction."""
    transaction_id: str
    security: Security
    transaction_type: TransactionType
    
    buyer: str
    seller: str
    
    quantity: int
    price_per_share: Fraction
    transaction_date: datetime
    
    # Insider information
    buyer_is_insider: bool = False
    seller_is_insider: bool = False
    material_nonpublic_info_known: bool = False
    
    @property
    def total_value(self) -> Fraction:
        """Total transaction value."""
        return self.price_per_share * self.quantity


@dataclass
class Insider:
    """An insider subject to Section 16 and Rule 10b-5."""
    name: str
    issuer: str
    position: str  # "officer", "director", "10%_shareholder"
    
    # Holdings
    beneficial_ownership: int = 0
    
    # Trading history (for short-swing profit analysis)
    transactions: List[Transaction] = field(default_factory=list)
    
    def is_section16_insider(self) -> bool:
        """Check if subject to Section 16 reporting."""
        return self.position in ("officer", "director", "10%_shareholder")


class SecuritiesRegistrationChecker:
    """Checker for securities registration requirements.
    
    Securities Act of 1933 requires registration unless exemption applies.
    """
    
    # Exemption thresholds
    REG_D_LIMIT = Fraction(5_000_000)  # Rule 504, 505, 506
    INTRASTATE_OFFERING = "Rule 147"
    
    def check_registration_requirement(
        self,
        security: Security,
        offering_amount: Fraction,
        num_investors: int,
    ) -> Dict:
        """Check if offering requires registration.
        
        Returns:
            Registration analysis
        """
        if security.registered_with_sec:
            return {
                "registration_required": False,
                "reason": "Already registered",
            }
        
        # Check common exemptions
        exemptions = []
        
        # Reg D - Private placements
        if num_investors <= 35 and offering_amount <= self.REG_D_LIMIT:
            exemptions.append("Reg D Rule 506")
        
        # Accredited investor only
        if num_investors <= 35:  # All accredited
            exemptions.append("Reg D Rule 506(c)")
        
        if exemptions:
            return {
                "registration_required": False,
                "exemption_available": exemptions[0],
                "all_exemptions": exemptions,
            }
        
        return {
            "registration_required": True,
            "reason": "No exemption available for this offering size/investor count",
            "recommended_action": "File Form S-1",
        }


class InsiderTradingAnalyzer:
    """Analyzer for insider trading under Rule 10b-5.
    
    Prohibits trading on material nonpublic information (MNPI).
    """
    
    def analyze_transaction(self, transaction: Transaction) -> Dict:
        """Analyze transaction for insider trading.
        
        Elements:
        1. Material information
        2. Nonpublic
        3. Breach of duty
        4. Scienter (intent to deceive)
        """
        issues = []
        
        # Check for insider status
        if transaction.buyer_is_insider or transaction.seller_is_insider:
            # Insiders trading - check for MNPI
            if transaction.material_nonpublic_info_known:
                issues.append({
                    "type": "INSIDER_TRADING",
                    "severity": "CRITICAL",
                    "description": "Trading while in possession of MNPI",
                })
        
        # Check timing around earnings/material events
        # (Simplified - real analysis would check against event dates)
        
        return {
            "transaction_id": transaction.transaction_id,
            "compliant": len(issues) == 0,
            "issues": issues,
            "insider_trading_suspected": any(
                i["type"] == "INSIDER_TRADING" for i in issues
            ),
        }
    
    def check_section16_compliance(
        self,
        insider: Insider,
        lookback_days: int = 180,
    ) -> Dict:
        """Check Section 16 short-swing profit rule.
        
        Section 16(b): Insiders must disgorge profits from purchases
        and sales within 6 months.
        """
        if not insider.is_section16_insider():
            return {"section16_applies": False}
        
        # Find matched transactions within 6 months
        recent_transactions = [
            t for t in insider.transactions
            if (datetime.now() - t.transaction_date).days <= lookback_days
        ]
        
        # Sort by date
        buys = [t for t in recent_transactions if t.transaction_type == TransactionType.PURCHASE]
        sells = [t for t in recent_transactions if t.transaction_type == TransactionType.SALE]
        
        short_swing_profits = []
        
        for buy in buys:
            for sell in sells:
                days_between = (sell.transaction_date - buy.transaction_date).days
                if 0 < days_between <= lookback_days:
                    profit = (sell.price_per_share - buy.price_per_share) * min(buy.quantity, sell.quantity)
                    if profit > 0:
                        short_swing_profits.append({
                            "buy_date": buy.transaction_date,
                            "sell_date": sell.transaction_date,
                            "profit": profit,
                        })
        
        return {
            "section16_applies": True,
            "short_swing_profits": short_swing_profits,
            "total_disgorgement": sum(p["profit"] for p in short_swing_profits),
            "compliant": len(short_swing_profits) == 0,
        }


class AntiFraudCompliance:
    """Compliance checker for anti-fraud provisions (Rule 10b-5)."""
    
    def check_material_misstatement(
        self,
        statement: str,
        material_facts_omitted: List[str],
    ) -> Dict:
        """Check for material misstatements or omissions.
        
        Rule 10b-5 prohibits:
        (a) Devices, schemes to defraud
        (b) Material misstatements
        (c) Material omissions
        (d) Acts that operate as fraud
        """
        issues = []
        
        if material_facts_omitted:
            issues.append({
                "type": "MATERIAL_OMISSION",
                "omitted": material_facts_omitted,
            })
        
        # Check for common fraudulent language
        red_flags = ["guaranteed", "risk-free", "can't lose", "secret"]
        statement_lower = statement.lower()
        
        for flag in red_flags:
            if flag in statement_lower:
                issues.append({
                    "type": "MISLEADING_STATEMENT",
                    "flag": flag,
                })
        
        return {
            "compliant": len(issues) == 0,
            "issues": issues,
        }
    
    def check_ponzi_scheme_indicators(
        self,
        returns_promised: Fraction,
        returns_actual: Optional[Fraction],
        investor_payouts_vs_revenue: Fraction,
    ) -> Dict:
        """Check for Ponzi scheme indicators.
        
        Indicators:
        - Unusually consistent returns
        - Returns exceed market norms
        - Payouts exceed actual revenue
        """
        issues = []
        
        # Promised returns > 20% annually is suspicious
        if returns_promised > Fraction(20, 100):
            issues.append("Unusually high promised returns")
        
        # Payouts > revenue indicates Ponzi structure
        if investor_payouts_vs_revenue > Fraction(1):
            issues.append("Payouts exceed revenue - possible Ponzi")
        
        return {
            "ponzi_indicators": len(issues) > 0,
            "issues": issues,
        }


class SecuritiesComplianceChecker:
    """Comprehensive securities law compliance checker."""
    
    def __init__(self):
        self.registration_checker = SecuritiesRegistrationChecker()
        self.insider_analyzer = InsiderTradingAnalyzer()
        self.fraud_checker = AntiFraudCompliance()
    
    def check_offering_compliance(
        self,
        security: Security,
        offering_amount: Fraction,
        investor_types: List[InvestorType],
    ) -> Dict:
        """Check full offering compliance."""
        num_investors = len(investor_types)
        
        registration = self.registration_checker.check_registration_requirement(
            security, offering_amount, num_investors
        )
        
        issues = []
        if registration["registration_required"]:
            issues.append("Registration required but not filed")
        
        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "registration": registration,
        }


# Convenience functions
def check_registration_required(
    security_type: str,
    offering_amount: float,
    num_non_accredited: int,
) -> Dict:
    """Quick check if securities offering requires registration."""
    return {
        "registration_likely_required": (
            offering_amount > 5_000_000 and num_non_accredited > 35
        ),
        "consider_exemption": num_non_accredited <= 35,
    }


def check_insider_trading_prohibited(
    is_insider: bool,
    has_mnpi: bool,
) -> Dict:
    """Quick check for insider trading violation."""
    violation = is_insider and has_mnpi
    
    return {
        "insider_trading_violation": violation,
        "penalty_exposure": "civil_and_criminal" if violation else "none",
    }


def check_antifraud_rule_10b5(
    misstatement: bool,
    omission_material: bool,
    scienter: bool,
) -> Dict:
    """Quick check for Rule 10b-5 violation elements."""
    elements_met = sum([misstatement, omission_material, scienter])
    
    return {
        "elements_met": elements_met,
        "likely_violation": elements_met >= 2,
        "recommended_action": "SEC_report" if elements_met >= 2 else "continue_monitoring",
    }
