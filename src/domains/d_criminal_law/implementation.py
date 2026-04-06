"""D_CRIMINAL_LAW implementation — Criminal Law

Implements criminal law: nullum crimen sine lege (no crime without law),
burden of proof on prosecution, sentencing within statutory ranges.

Layer: 2 (Statutory)
CardinalStrength: PREDICATIVE
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Set
from enum import Enum, auto
from datetime import datetime
from fractions import Fraction


class OffenseClass(Enum):
    """Classification of criminal offenses."""
    INFRACTION = auto()
    MISDEMEANOR = auto()
    FELONY = auto()
    CAPITAL = auto()


@dataclass
class CriminalOffense:
    """A criminal offense defined by statute."""
    offense_name: str
    statute_citation: str
    offense_class: OffenseClass
    elements: List[str] = field(default_factory=list)
    max_penalty_years: int = 0
    max_fine: Fraction = field(default_factory=lambda: Fraction(0))
    
    def is_defined_by_law(self) -> bool:
        """
        Check if offense is properly defined by law.
        
        Nullum crimen sine lege: No punishment without prior law.
        """
        return (
            len(self.statute_citation) > 0 and
            len(self.elements) > 0 and
            self.offense_class is not None
        )


@dataclass
class BurdenOfProof:
    """Burden of proof in criminal proceedings."""
    prosecution_evidence: List[str] = field(default_factory=list)
    reasonable_doubt_exists: bool = False
    
    # Standard: Beyond reasonable doubt
    BARD_THRESHOLD = Fraction(95, 100)  # 95% certainty
    
    def meets_beyond_reasonable_doubt(self) -> bool:
        """
        Check if burden of proof is met.
        
        Prosecution must prove guilt beyond reasonable doubt.
        """
        if self.reasonable_doubt_exists:
            return False
        # Simplified: real implementation would evaluate evidence strength
        return len(self.prosecution_evidence) >= 3  # Minimum evidence threshold
    
    def can_convict(self) -> bool:
        """Determine if conviction is permissible."""
        return self.meets_beyond_reasonable_doubt()


@dataclass
class Sentencing:
    """Criminal sentencing within statutory range."""
    offense: CriminalOffense
    convicted: bool = False
    sentence_years: int = 0
    fine_amount: Fraction = field(default_factory=lambda: Fraction(0))
    mitigating_factors: List[str] = field(default_factory=list)
    aggravating_factors: List[str] = field(default_factory=list)
    
    def is_within_statutory_range(self) -> bool:
        """
        Check if sentence is within statutory limits.
        
        Sentencing must be within range for offense class.
        """
        if not self.convicted:
            return self.sentence_years == 0
        
        return (
            self.sentence_years <= self.offense.max_penalty_years and
            self.fine_amount <= self.offense.max_fine
        )
    
    def apply_sentencing_factors(self) -> int:
        """
        Calculate adjusted sentence based on factors.
        
        Mitigating factors reduce sentence; aggravating increase.
        """
        base_sentence = self.sentence_years
        
        # Mitigating: reduce by 1 year per factor (minimum 0)
        for _ in self.mitigating_factors:
            base_sentence = max(0, base_sentence - 1)
        
        # Aggravating: increase by 1 year per factor
        for _ in self.aggravating_factors:
            base_sentence += 1
        
        # Cap at statutory maximum
        return min(base_sentence, self.offense.max_penalty_years)


class CriminalLaw:
    """Criminal law system with nullum crimen and burden of proof."""
    
    def __init__(self):
        self.offenses: Dict[str, CriminalOffense] = {}
        self.convictions: List[Dict] = []
        self.acquittals: List[Dict] = []
    
    def define_offense(
        self,
        offense_name: str,
        statute_citation: str,
        offense_class: OffenseClass,
        elements: List[str],
        max_penalty_years: int,
        max_fine: Fraction,
    ) -> CriminalOffense:
        """
        Define a criminal offense by statute.
        
        Required for nullum crimen sine lege.
        """
        offense = CriminalOffense(
            offense_name=offense_name,
            statute_citation=statute_citation,
            offense_class=offense_class,
            elements=elements,
            max_penalty_years=max_penalty_years,
            max_fine=max_fine,
        )
        self.offenses[offense_name] = offense
        return offense
    
    def prosecute(
        self,
        defendant: str,
        offense_name: str,
        evidence: List[str],
    ) -> Dict:
        """
        Prosecute a criminal case.
        
        Returns verdict based on burden of proof.
        """
        if offense_name not in self.offenses:
            return {
                "verdict": "DISMISSED",
                "reason": "Offense not defined by law",
                "nullum_crimen_violation": True,
            }
        
        offense = self.offenses[offense_name]
        
        # Check if offense properly defined
        if not offense.is_defined_by_law():
            return {
                "verdict": "DISMISSED",
                "reason": "Offense not properly defined",
                "nullum_crimen_violation": True,
            }
        
        # Evaluate burden of proof
        burden = BurdenOfProof(
            prosecution_evidence=evidence,
            reasonable_doubt_exists=len(evidence) < 3,
        )
        
        if burden.can_convict():
            self.convictions.append({
                "defendant": defendant,
                "offense": offense_name,
                "date": datetime.now(),
            })
            return {
                "verdict": "GUILTY",
                "offense": offense_name,
                "burden_met": True,
            }
        else:
            self.acquittals.append({
                "defendant": defendant,
                "offense": offense_name,
                "reason": "Reasonable doubt exists",
            })
            return {
                "verdict": "NOT GUILTY",
                "offense": offense_name,
                "burden_met": False,
            }
    
    def sentence(
        self,
        defendant: str,
        offense_name: str,
        base_sentence_years: int,
        fine: Fraction,
        mitigating: List[str],
        aggravating: List[str],
    ) -> Dict:
        """
        Sentence a convicted defendant.
        
        Sentence must be within statutory range.
        """
        if offense_name not in self.offenses:
            return {"error": "Offense not found"}
        
        offense = self.offenses[offense_name]
        
        # Check base sentence against statutory range BEFORE applying factors
        if base_sentence_years > offense.max_penalty_years:
            return {
                "error": "Sentence exceeds statutory maximum",
                "requested": base_sentence_years,
                "maximum": offense.max_penalty_years,
            }
        
        sentencing = Sentencing(
            offense=offense,
            convicted=True,
            sentence_years=base_sentence_years,
            fine_amount=fine,
            mitigating_factors=mitigating,
            aggravating_factors=aggravating,
        )
        
        # Apply factors
        final_sentence = sentencing.apply_sentencing_factors()
        
        return {
            "defendant": defendant,
            "offense": offense_name,
            "sentence_years": final_sentence,
            "fine": fine,
            "within_range": True,
        }


def check_nullum_crimen(offense_defined: bool) -> bool:
    """
    Convenience function to check nullum crimen sine lege.
    
    Returns False if prosecution attempted for undefined offense.
    """
    return offense_defined
