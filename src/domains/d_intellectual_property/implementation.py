"""D_INTELLECTUAL_PROPERTY implementation — Intellectual Property

Implements patent (35 U.S.C.), copyright (17 U.S.C.), and trademark (15 U.S.C.)
law including novelty analysis, fair use factors, and infringement detection.

Layer: 2 (Statutory)
CardinalStrength: PREDICATIVE
Source: 35 U.S.C. (Patent), 17 U.S.C. (Copyright), 15 U.S.C. §1051 (Lanham Act)

Biblical: Exodus 20:15 — "You shall not steal."

The commandment against theft extends to intellectual property—creative
works, inventions, and brand identities represent the fruits of labor
that belong to their creators. This domain enforces protections against
unauthorized appropriation of intellectual creations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction


class IPType(Enum):
    """Types of intellectual property."""
    PATENT = auto()
    COPYRIGHT = auto()
    TRADEMARK = auto()
    TRADE_SECRET = auto()


class PatentClaimType(Enum):
    """Types of patent claims."""
    APPARATUS = auto()      # Device/machine
    METHOD = auto()         # Process
    COMPOSITION = auto()    # Chemical composition
    ARTICLE = auto()        # Manufactured article


class FairUsePurpose(Enum):
    """Purposes favoring fair use under 17 U.S.C. §107."""
    CRITICISM = auto()
    COMMENT = auto()
    NEWS_REPORTING = auto()
    TEACHING = auto()
    SCHOLARSHIP = auto()
    RESEARCH = auto()
    PARODY = auto()
    TRANSFORMATIVE = auto()


class TrademarkStrength(Enum):
    """Spectrum of trademark distinctiveness."""
    GENERIC = auto()        # Not protectable
    DESCRIPTIVE = auto()    # Weak, requires secondary meaning
    SUGGESTIVE = auto()     # Inherently distinctive
    ARBITRARY = auto()      # Strong
    FANCIFUL = auto()       # Strongest


@dataclass
class PatentClaim:
    """A single claim in a patent."""
    claim_number: int
    claim_type: PatentClaimType
    claim_text: str
    
    # Elements (for infringement analysis)
    elements: List[str] = field(default_factory=list)
    
    def get_element_count(self) -> int:
        """Number of elements in claim (more = narrower)."""
        return len(self.elements)


@dataclass
class Invention:
    """An invention for patent analysis."""
    invention_id: str
    title: str
    inventor: str
    
    # Patent information
    filing_date: datetime
    issue_date: Optional[datetime] = None
    patent_number: Optional[str] = None
    
    # Claims
    claims: List[PatentClaim] = field(default_factory=list)
    
    # Prior art
    prior_art_references: List[Dict] = field(default_factory=list)
    
    def is_expired(self, as_of: Optional[datetime] = None) -> bool:
        """Check if patent has expired (20 years from filing)."""
        if as_of is None:
            as_of = datetime.now()
        
        expiration = self.filing_date + timedelta(days=20 * 365)
        return as_of > expiration
    
    @property
    def claim_count(self) -> int:
        """Total number of claims."""
        return len(self.claims)


@dataclass
class CreativeWork:
    """A creative work for copyright analysis."""
    work_id: str
    title: str
    creator: str
    creation_date: datetime
    
    # Content
    content_type: str  # "literary", "musical", "dramatic", "artistic", "software"
    content: str = ""  # Actual content or description
    
    # Registration
    registration_number: Optional[str] = None
    registration_date: Optional[datetime] = None
    
    # Copyright term
    is_work_for_hire: bool = False
    author_death_date: Optional[datetime] = None
    
    def is_in_public_domain(self, as_of: Optional[datetime] = None) -> bool:
        """Check if work is in public domain."""
        if as_of is None:
            as_of = datetime.now()
        
        # Works for hire: 95 years from publication or 120 from creation
        if self.is_work_for_hire:
            pd_date = self.creation_date + timedelta(days=120 * 365)
            return as_of > pd_date
        
        # Life + 70 years
        if self.author_death_date:
            pd_date = self.author_death_date + timedelta(days=70 * 365)
            return as_of > pd_date
        
        # Unknown: assume protected
        return False
    
    def get_similarity_score(self, other_work: CreativeWork) -> Fraction:
        """Calculate similarity score between works (simplified)."""
        # Simplified: check for substantial similarity
        if not self.content or not other_work.content:
            return Fraction(0)
        
        # Use basic string similarity
        words1 = set(self.content.lower().split())
        words2 = set(other_work.content.lower().split())
        
        if not words1 or not words2:
            return Fraction(0)
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return Fraction(intersection, union) if union > 0 else Fraction(0)


@dataclass
class FairUseAnalysis:
    """Analysis of fair use factors under 17 U.S.C. §107."""
    purpose: FairUsePurpose
    work: CreativeWork
    portion_used: Fraction  # 0 to 1
    
    # Market effect
    market_substitution: bool = False  # Would use substitute for original?
    
    # Nature of work
    work_is_factual: bool = False  # Factual works favor fair use
    work_published: bool = True
    
    def analyze_four_factors(self) -> Dict:
        """Analyze the four fair use factors.
        
        1. Purpose and character of use
        2. Nature of copyrighted work
        3. Amount and substantiality
        4. Effect on market
        """
        # Factor 1: Purpose
        purpose_scores = {
            FairUsePurpose.CRITICISM: 3,
            FairUsePurpose.COMMENT: 3,
            FairUsePurpose.NEWS_REPORTING: 3,
            FairUsePurpose.TEACHING: 3,
            FairUsePurpose.SCHOLARSHIP: 3,
            FairUsePurpose.RESEARCH: 3,
            FairUsePurpose.PARODY: 3,
            FairUsePurpose.TRANSFORMATIVE: 3,
        }
        factor1 = purpose_scores.get(self.purpose, 0)
        
        # Factor 2: Nature of work
        factor2 = 2 if self.work_is_factual else 1
        if not self.work_published:
            factor2 -= 1  # Unpublished works disfavor fair use
        
        # Factor 3: Amount used
        if self.portion_used <= Fraction(1, 10):
            factor3 = 3
        elif self.portion_used <= Fraction(1, 4):
            factor3 = 2
        elif self.portion_used <= Fraction(1, 2):
            factor3 = 1
        else:
            factor3 = 0
        
        # Factor 4: Market effect
        factor4 = 0 if self.market_substitution else 3
        
        total_score = factor1 + factor2 + factor3 + factor4
        max_score = 12
        
        return {
            "factor1_purpose": factor1,
            "factor2_nature": factor2,
            "factor3_amount": factor3,
            "factor4_market": factor4,
            "total_score": total_score,
            "max_score": max_score,
            "likely_fair_use": total_score >= 8,  # 2/3 of max
        }


@dataclass
class Trademark:
    """A trademark for analysis."""
    mark_id: str
    mark_text: str
    owner: str
    
    # Classification
    strength: TrademarkStrength
    goods_services_class: str
    
    # Registration
    filing_date: datetime
    registration_date: Optional[datetime] = None
    
    # Use
    first_use_date: Optional[datetime] = None
    continuous_use: bool = True
    
    def is_registered(self) -> bool:
        """Check if mark is registered."""
        return self.registration_date is not None
    
    def is_abandoned(self, as_of: Optional[datetime] = None) -> bool:
        """Check if mark has been abandoned (non-use)."""
        if as_of is None:
            as_of = datetime.now()
        
        if not self.continuous_use and self.first_use_date:
            # 3 years of non-use creates presumption of abandonment
            abandonment_date = self.first_use_date + timedelta(days=3 * 365)
            return as_of > abandonment_date
        
        return False
    
    def similarity_to(self, other: Trademark) -> Fraction:
        """Calculate similarity to another mark."""
        # Simplified: check for phonetic/appearance similarity
        mark1 = self.mark_text.lower()
        mark2 = other.mark_text.lower()
        
        # Exact match
        if mark1 == mark2:
            return Fraction(1)
        
        # Check for common substrings
        if mark1 in mark2 or mark2 in mark1:
            return Fraction(3, 4)
        
        # Check first characters
        if mark1[0] == mark2[0]:
            return Fraction(1, 4)
        
        return Fraction(0)


class PatentAnalyzer:
    """Analyzer for patent validity and infringement."""
    
    def __init__(self):
        self.prior_art_database: List[Dict] = []
    
    def check_novelty(self, invention: Invention) -> Dict:
        """Check if invention meets novelty requirement (35 U.S.C. §102).
        
        Invention is novel if not:
        - Previously patented
        - Described in printed publication
        - In public use or on sale
        - Otherwise available to public
        """
        novelty_issues = []
        
        for prior_art in invention.prior_art_references:
            if prior_art.get("date", datetime.min) < invention.filing_date:
                novelty_issues.append({
                    "type": "ANTICIPATION",
                    "reference": prior_art.get("reference"),
                    "date": prior_art.get("date"),
                })
        
        return {
            "novel": len(novelty_issues) == 0,
            "issues": novelty_issues,
        }
    
    def check_obviousness(self, invention: Invention) -> Dict:
        """Check if invention is non-obvious (35 U.S.C. §103).
        
        Invention is obvious if differences between subject matter
        sought to be patented and the prior art are such that the
        subject matter as a whole would have been obvious at the time.
        """
        # Simplified: if many prior art references covering similar ground,
        # invention may be obvious
        
        similar_prior_art = [
            pa for pa in invention.prior_art_references
            if pa.get("similarity_score", 0) > 0.7
        ]
        
        if len(similar_prior_art) >= 2:
            return {
                "non_obvious": False,
                "reason": "Multiple similar prior art references suggest obviousness",
                "references": similar_prior_art,
            }
        
        return {
            "non_obvious": True,
            "similar_references": len(similar_prior_art),
        }
    
    def analyze_infringement(
        self,
        patent: Invention,
        accused_product: Dict,
    ) -> Dict:
        """Analyze potential patent infringement.
        
        Infringement requires that accused product/practice contains
        every element of at least one claim (all elements rule).
        """
        infringement_results = []
        
        for claim in patent.claims:
            missing_elements = []
            for element in claim.elements:
                if element not in accused_product.get("features", []):
                    missing_elements.append(element)
            
            infringement_results.append({
                "claim_number": claim.claim_number,
                "infringed": len(missing_elements) == 0,
                "missing_elements": missing_elements,
            })
        
        any_infringement = any(r["infringed"] for r in infringement_results)
        
        return {
            "patent_number": patent.patent_number,
            "infringement_found": any_infringement,
            "claim_analysis": infringement_results,
        }


class CopyrightAnalyzer:
    """Analyzer for copyright protection and infringement."""
    
    def __init__(self):
        self.copyright_registry: List[CreativeWork] = []
    
    def check_substantial_similarity(
        self,
        work1: CreativeWork,
        work2: CreativeWork,
    ) -> Dict:
        """Check for substantial similarity (infringement test).
        
        Infringement requires:
        1. Copying (access + similarity)
        2. Improper appropriation (substantial similarity)
        """
        similarity = work1.get_similarity_score(work2)
        
        # Threshold for substantial similarity varies by work type
        thresholds = {
            "literary": Fraction(8, 10),
            "musical": Fraction(7, 10),
            "software": Fraction(6, 10),
            "artistic": Fraction(7, 10),
        }
        
        threshold = thresholds.get(work1.content_type, Fraction(7, 10))
        
        return {
            "similarity_score": similarity,
            "threshold": threshold,
            "substantially_similar": similarity >= threshold,
        }
    
    def analyze_fair_use(
        self,
        use_analysis: FairUseAnalysis,
    ) -> Dict:
        """Analyze whether use constitutes fair use."""
        return use_analysis.analyze_four_factors()


class TrademarkAnalyzer:
    """Analyzer for trademark protection and infringement."""
    
    def __init__(self):
        self.trademark_registry: List[Trademark] = []
    
    def check_likelihood_of_confusion(
        self,
        mark1: Trademark,
        mark2: Trademark,
    ) -> Dict:
        """Check for likelihood of confusion (infringement test).
        
        Factors (Polaroid test):
        1. Strength of senior mark
        2. Similarity of marks
        3. Similarity of products
        4. Likely bridging gap
        5. Actual confusion
        6. Junior user's good faith
        7. Quality of junior's products
        8. Sophistication of consumers
        """
        similarity = mark1.similarity_to(mark2)
        
        # Factor 1: Strength
        strength_scores = {
            TrademarkStrength.GENERIC: 0,
            TrademarkStrength.DESCRIPTIVE: 1,
            TrademarkStrength.SUGGESTIVE: 2,
            TrademarkStrength.ARBITRARY: 3,
            TrademarkStrength.FANCIFUL: 4,
        }
        strength_factor = strength_scores.get(mark1.strength, 0)
        
        # Calculate confusion likelihood
        confusion_factors = {
            "mark_similarity": similarity,
            "senior_strength": strength_factor,
            "likely_confusion": similarity >= Fraction(3, 4) and strength_factor >= 2,
        }
        
        return confusion_factors
    
    def check_dilution(
        self,
        famous_mark: Trademark,
        junior_mark: Trademark,
    ) -> Dict:
        """Check for trademark dilution (famous marks only).
        
        Dilution requires:
        1. Mark is famous
        2. Junior use began after mark became famous
        3. Junior use causes dilution by blurring or tarnishment
        """
        is_famous = famous_mark.strength in (
            TrademarkStrength.ARBITRARY,
            TrademarkStrength.FANCIFUL,
        ) and famous_mark.is_registered()
        
        similarity = famous_mark.similarity_to(junior_mark)
        
        dilution_by_blurring = is_famous and similarity >= Fraction(1, 2)
        
        return {
            "famous": is_famous,
            "similarity": similarity,
            "dilution_by_blurring": dilution_by_blurring,
            "dilution_by_tarnishment": False,  # Would require reputation analysis
        }


class IPComplianceChecker:
    """Comprehensive intellectual property compliance checker."""
    
    def __init__(self):
        self.patent_analyzer = PatentAnalyzer()
        self.copyright_analyzer = CopyrightAnalyzer()
        self.trademark_analyzer = TrademarkAnalyzer()
    
    def check_patent_validity(self, invention: Invention) -> Dict:
        """Check patent validity (novelty and non-obviousness)."""
        novelty = self.patent_analyzer.check_novelty(invention)
        obviousness = self.patent_analyzer.check_obviousness(invention)
        
        valid = novelty["novel"] and obviousness["non_obvious"]
        
        return {
            "valid": valid,
            "novelty": novelty,
            "obviousness": obviousness,
        }


# Convenience functions
def check_patent_novelty_required(
    invention_description: str,
    prior_art_exists: bool,
) -> Dict:
    """Quick check for patent novelty requirement."""
    return {
        "novel": not prior_art_exists,
        "patentable": not prior_art_exists,
        "issue": "Prior art exists" if prior_art_exists else None,
    }


def check_copyright_term_limits(
    creation_year: int,
    author_death_year: Optional[int] = None,
    current_year: int = 2024,
) -> Dict:
    """Check if copyright has expired."""
    if author_death_year:
        expiration = author_death_year + 70
    else:
        expiration = creation_year + 95  # Work for hire
    
    expired = current_year > expiration
    
    return {
        "copyright_expired": expired,
        "expiration_year": expiration,
        "years_remaining": max(0, expiration - current_year),
    }


def check_trademark_distinctiveness(
    mark_text: str,
    describes_product: bool,
) -> Dict:
    """Check trademark distinctiveness."""
    if describes_product:
        strength = "DESCRIPTIVE"
        protectable = False  # Without secondary meaning
    elif len(mark_text) <= 3:
        strength = "ARBITRARY"
        protectable = True
    else:
        strength = "SUGGESTIVE"
        protectable = True
    
    return {
        "strength": strength,
        "inherently_protectable": protectable,
    }


def check_fair_use_factors(
    purpose: str,
    portion_used_percent: int,
    market_effect: str,
) -> Dict:
    """Quick fair use analysis."""
    # Purpose factor
    favored_purposes = ["criticism", "comment", "news", "teaching", "parody"]
    purpose_favored = purpose.lower() in favored_purposes
    
    # Portion factor
    portion = Fraction(portion_used_percent, 100)
    small_portion = portion <= Fraction(1, 4)
    
    # Market factor
    no_market_harm = market_effect.lower() in ["none", "minimal"]
    
    fair_use_likely = purpose_favored and small_portion and no_market_harm
    
    return {
        "likely_fair_use": fair_use_likely,
        "purpose_favored": purpose_favored,
        "small_portion": small_portion,
        "no_market_harm": no_market_harm,
    }
