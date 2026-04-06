"""D_CONSUMER_PROTECTION implementation — Consumer Protection

Implements consumer protection law including FTC Act §5 (unfair/deceptive
practices), TILA disclosure requirements, FCRA, Magnuson-Moss Warranty Act.

Layer: 2 (Statutory)
CardinalStrength: PREDICATIVE
Source: 15 U.S.C. §45 (FTC Act), 15 U.S.C. §1601 (TILA), 15 U.S.C. §2301
(Magnuson-Moss), 15 U.S.C. §1681 (FCRA)

Biblical: Leviticus 19:35-36 — "Do not use dishonest standards when
measuring length, weight or quantity. Use honest scales and honest
weights, honest ephah and honest hin. I am the LORD your God, who
brought you out of Egypt."

Also: Proverbs 11:1 — "The LORD detests dishonest scales, but accurate
weights find favor with him."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction


class DeceptivePracticeType(Enum):
    """Types of deceptive practices under FTC Act §5."""
    FALSE_ADVERTISING = auto()         # Materially false representations
    BAIT_AND_SWITCH = auto()           # Advertise low, sell high
    OMISSION_OF_MATERIAL_FACTS = auto()  # Failure to disclose
    UNFAORTABLE_CONTRACT_TERMS = auto()  # Hidden terms
    FAKE_TESTIMONIALS = auto()         # False endorsements
    IMITATION_PRODUCTS = auto()        # Counterfeit goods
    PRICE_GOUGING = auto()             # Excessive pricing in emergencies


class UnfairPracticeType(Enum):
    """Types of unfair practices (causes substantial injury not outweighed)."""
    UNREASONABLE_DATA_COLLECTION = auto()
    COERCIVE_SALES_TACTICS = auto()
    TAKE_IT_OR_LEAVE_IT = auto()       # Adhesion contracts
    PRE_DISPUTE_ARBITRATION = auto()   # Forced arbitration clauses


class WarrantyType(Enum):
    """Types of warranties under Magnuson-Moss."""
    EXPRESS_WRITTEN = auto()
    EXPRESS_ORAL = auto()
    IMPLIED_MERCHANTABILITY = auto()   # UCC §2-314
    IMPLIED_FITNESS = auto()           # UCC §2-315
    FULL = auto()                      # Full warranty per Magnuson-Moss
    LIMITED = auto()                   # Limited warranty


@dataclass
class Product:
    """A consumer product."""
    product_id: str
    name: str
    manufacturer: str
    category: str
    
    # Pricing
    msrp: Fraction
    actual_price: Optional[Fraction] = None
    
    # Safety
    safety_warnings: List[str] = field(default_factory=list)
    recalls: List[str] = field(default_factory=list)
    
    # Warranties
    warranties: List[Dict] = field(default_factory=list)
    
    def has_active_recall(self) -> bool:
        """Check if product has active safety recall."""
        return len(self.recalls) > 0
    
    def get_warranty_period_days(self) -> int:
        """Get warranty period in days (default 365)."""
        for warranty in self.warranties:
            if warranty.get("type") in ("FULL", "LIMITED"):
                return warranty.get("period_days", 365)
        return 365


@dataclass
class Advertisement:
    """A consumer advertisement."""
    ad_id: str
    product: Product
    media_type: str  # "tv", "radio", "print", "digital", etc.
    
    # Claims
    claims: List[str] = field(default_factory=list)
    testimonials: List[Dict] = field(default_factory=list)
    
    # Pricing
    advertised_price: Optional[Fraction] = None
    fine_print: str = ""
    
    # Targeting
    target_demographic: str = ""
    
    def has_material_claims(self) -> bool:
        """Check if ad makes material claims about product."""
        return len(self.claims) > 0


@dataclass
class ConsumerTransaction:
    """A consumer transaction subject to protection laws."""
    transaction_id: str
    consumer_name: str
    product: Product
    
    # Pricing
    agreed_price: Fraction
    final_price: Fraction
    
    # Disclosures
    disclosures_provided: List[str] = field(default_factory=list)
    terms_explained: bool = False
    
    # Timing
    transaction_date: datetime = field(default_factory=datetime.now)
    cooling_off_deadline: Optional[datetime] = None
    
    # Cancellation
    cancelled: bool = False
    cancellation_date: Optional[datetime] = None
    
    def __post_init__(self):
        """Set cooling-off period if applicable."""
        if self.cooling_off_deadline is None:
            # Door-to-door sales: 3 business days
            self.cooling_off_deadline = self.transaction_date + timedelta(days=3)
    
    @property
    def price_discrepancy(self) -> Fraction:
        """Difference between agreed and final price."""
        return self.final_price - self.agreed_price
    
    @property
    def has_hidden_fees(self) -> bool:
        """Check if final price exceeds agreed price."""
        return self.final_price > self.agreed_price
    
    def can_cancel(self, as_of: Optional[datetime] = None) -> bool:
        """Check if transaction can be cancelled under cooling-off rule."""
        if self.cancelled:
            return False
        if as_of is None:
            as_of = datetime.now()
        return as_of <= self.cooling_off_deadline


class DeceptivePracticeAnalyzer:
    """Analyzer for deceptive and unfair practices under FTC Act §5.
    
    Section 5 prohibits "unfair or deceptive acts or practices in or
    affecting commerce." Deceptive: material representation likely to
    mislead reasonable consumer. Unfair: causes substantial injury not
    reasonably avoidable and not outweighed by benefits.
    """
    
    def __init__(self):
        self.violations: List[Dict] = []
    
    def analyze_advertisement(self, ad: Advertisement) -> Dict:
        """Analyze advertisement for deceptive practices.
        
        Returns:
            Compliance analysis
        """
        issues = []
        
        # Check for common deceptive patterns
        ad_text = " ".join(ad.claims).lower()
        
        # Bait and switch indicators
        bait_patterns = ["starting at", "as low as", "from", "up to"]
        for pattern in bait_patterns:
            if pattern in ad_text and ad.advertised_price:
                # Fine print should disclose limitations
                if "limited quantity" not in ad.fine_print.lower():
                    issues.append({
                        "type": "BAIT_SWITCH_RISK",
                        "description": f"'{pattern}' without adequate disclosure",
                    })
        
        # Unsubstantiated claims
        superlatives = ["best", "guaranteed", "miracle", "instant"]
        for word in superlatives:
            if word in ad_text:
                issues.append({
                    "type": "UNSUBSTANTIATED_CLAIM",
                    "description": f"Superlative '{word}' requires substantiation",
                })
        
        # Fake testimonials
        for testimonial in ad.testimonials:
            if not testimonial.get("verified_purchase", False):
                issues.append({
                    "type": "UNVERIFIED_TESTIMONIAL",
                    "description": f"Testimonial from {testimonial.get('name', 'unknown')} not verified",
                })
        
        return {
            "ad_id": ad.ad_id,
            "compliant": len(issues) == 0,
            "issues": issues,
            "deceptive_practice_likely": len([i for i in issues if i["type"].startswith(("BAIT", "UNSUBSTANTIATED"))]) > 0,
        }
    
    def analyze_transaction(self, transaction: ConsumerTransaction) -> Dict:
        """Analyze transaction for deceptive practices."""
        issues = []
        
        # Hidden fees
        if transaction.has_hidden_fees:
            issues.append({
                "type": "HIDDEN_FEES",
                "amount": transaction.price_discrepancy,
                "description": f"Final price ${float(transaction.final_price):.2f} exceeds agreed ${float(transaction.agreed_price):.2f}",
            })
        
        # Missing required disclosures
        required_disclosures = self._get_required_disclosures(transaction.product)
        missing = [d for d in required_disclosures if d not in transaction.disclosures_provided]
        
        if missing:
            issues.append({
                "type": "MISSING_DISCLOSURES",
                "missing": missing,
            })
        
        # Check for recalled product
        if transaction.product.has_active_recall():
            issues.append({
                "type": "SALE_OF_RECALLED_PRODUCT",
                "recalls": transaction.product.recalls,
            })
        
        return {
            "transaction_id": transaction.transaction_id,
            "compliant": len(issues) == 0,
            "issues": issues,
        }
    
    def _get_required_disclosures(self, product: Product) -> List[str]:
        """Get list of required disclosures for product type."""
        base_disclosures = ["price", "terms", "warranty"]
        
        if product.safety_warnings:
            base_disclosures.append("safety_warnings")
        
        return base_disclosures


class DisclosureRequirementsChecker:
    """Checker for disclosure requirements under TILA and other laws."""
    
    def __init__(self):
        self.required_tila_disclosures = [
            "annual_percentage_rate",
            "finance_charge",
            "amount_financed",
            "total_payments",
            "payment_schedule",
        ]
    
    def check_tila_disclosures(
        self,
        provided_disclosures: Dict[str, str],
    ) -> Dict:
        """Check TILA (Truth in Lending Act) disclosure compliance.
        
        TILA requires clear disclosure of credit terms before consummation.
        """
        missing = []
        for required in self.required_tila_disclosures:
            if required not in provided_disclosures:
                missing.append(required)
        
        return {
            "compliant": len(missing) == 0,
            "missing_disclosures": missing,
            "provided_count": len(provided_disclosures),
            "required_count": len(self.required_tila_disclosures),
        }
    
    def check_advertising_disclosures(
        self,
        ad: Advertisement,
        trigger_terms: List[str],
    ) -> Dict:
        """Check if advertising with trigger terms includes required disclosures.
        
        If ad includes trigger terms (e.g., "0% APR"), must disclose:
        - Down payment, terms, APR
        """
        ad_text = " ".join(ad.claims).lower()
        
        has_trigger = any(term.lower() in ad_text for term in trigger_terms)
        
        if has_trigger:
            # Check for required follow-up disclosures
            required_follow_up = ["apr", "down_payment", "terms"]
            has_follow_up = any(term in ad.fine_print.lower() for term in required_follow_up)
            
            return {
                "has_trigger_terms": True,
                "disclosures_adequate": has_follow_up,
                "compliant": has_follow_up,
            }
        
        return {
            "has_trigger_terms": False,
            "compliant": True,
        }


class WarrantyAnalyzer:
    """Analyzer for warranty compliance under Magnuson-Moss."""
    
    def __init__(self):
        self.warranty_claims: List[Dict] = []
    
    def analyze_warranty_coverage(
        self,
        product: Product,
        defect_description: str,
        purchase_date: datetime,
        claim_date: datetime,
    ) -> Dict:
        """Analyze whether defect is covered by warranty.
        
        Returns:
            Coverage determination
        """
        # Check warranty period
        warranty_days = product.get_warranty_period_days()
        days_since_purchase = (claim_date - purchase_date).days
        
        if days_since_purchase > warranty_days:
            return {
                "covered": False,
                "reason": "Warranty expired",
                "warranty_period_days": warranty_days,
                "days_since_purchase": days_since_purchase,
            }
        
        # Check for implied warranty of merchantability (always applies)
        has_implied_warranty = True  # UCC §2-314 unless disclaimed
        
        # Disclaimer check
        disclaimer_present = any(
            w.get("type") == "DISCLAIMER" for w in product.warranties
        )
        
        if disclaimer_present and not product.warranties:
            return {
                "covered": False,
                "reason": "Implied warranties disclaimed (as is)",
            }
        
        return {
            "covered": True,
            "warranty_type": "IMPLIED_MERCHANTABILITY",
            "remedy": "REPAIR_OR_REPLACE",
        }
    
    def check_full_warranty_requirements(self, warranty_terms: Dict) -> Dict:
        """Check if 'full warranty' meets Magnuson-Moss requirements.
        
        Full warranty must:
        - Fix defect within reasonable time
        - Not limit implied warranties
        - Not require purchase of other product
        """
        issues = []
        
        if warranty_terms.get("type") == "FULL":
            if warranty_terms.get("duration_days", 0) < 90:
                issues.append("Full warranty duration too short")
            
            if warranty_terms.get("requires_other_purchase", False):
                issues.append("Full warranty cannot require tie-in purchase")
        
        return {
            "is_full_warranty": warranty_terms.get("type") == "FULL",
            "compliant": len(issues) == 0,
            "issues": issues,
        }


class ConsumerProtectionComplianceChecker:
    """Comprehensive consumer protection compliance checker."""
    
    def __init__(self):
        self.deceptive_analyzer = DeceptivePracticeAnalyzer()
        self.disclosure_checker = DisclosureRequirementsChecker()
        self.warranty_analyzer = WarrantyAnalyzer()
    
    def check_transaction_compliance(
        self,
        transaction: ConsumerTransaction,
    ) -> Dict:
        """Check full transaction compliance."""
        deceptive = self.deceptive_analyzer.analyze_transaction(transaction)
        
        all_issues = deceptive.get("issues", [])
        
        return {
            "transaction_id": transaction.transaction_id,
            "compliant": len(all_issues) == 0,
            "issues": all_issues,
            "can_cancel": transaction.can_cancel(),
        }


# Convenience functions
def check_deceptive_practices_prohibited(
    advertised_price: float,
    actual_price: float,
    claims: List[str],
) -> Dict:
    """Quick check for deceptive practice indicators.
    
    Usage:
        result = check_deceptive_practices_prohibited(
            advertised_price=99.99,
            actual_price=149.99,
            claims=["guaranteed lowest price"],
        )
    """
    issues = []
    
    if actual_price > advertised_price:
        issues.append(f"Actual price ${actual_price} exceeds advertised ${advertised_price}")
    
    for claim in claims:
        claim_lower = claim.lower()
        if "guaranteed" in claim_lower or "best" in claim_lower:
            issues.append(f"Superlative claim requires substantiation: '{claim}'")
    
    return {
        "compliant": len(issues) == 0,
        "issues": issues,
        "deceptive_indicators": len(issues) > 0,
    }


def check_disclosure_requirements_met(
    provided_disclosures: List[str],
    product_category: str,
) -> Dict:
    """Check if required disclosures were provided."""
    required = ["price", "terms"]
    
    if product_category in ("financial", "credit"):
        required.extend(["apr", "finance_charge"])
    
    if product_category in ("electronics", "appliances"):
        required.append("warranty")
    
    missing = [r for r in required if r not in provided_disclosures]
    
    return {
        "compliant": len(missing) == 0,
        "missing": missing,
        "provided": provided_disclosures,
    }


def check_warranty_honored(
    days_since_purchase: int,
    warranty_period_days: int,
    defect_type: str,
) -> Dict:
    """Check if warranty should cover defect."""
    if days_since_purchase > warranty_period_days:
        return {
            "covered": False,
            "reason": "Warranty expired",
        }
    
    # Normal wear and tear typically excluded
    if defect_type.lower() in ("normal_wear", "accidental_damage"):
        return {
            "covered": False,
            "reason": "Exclusion: not manufacturing defect",
        }
    
    return {
        "covered": True,
        "remedy": "REPAIR_OR_REPLACE",
    }
