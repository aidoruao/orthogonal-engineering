"""D_SOCIOLOGY implementation — Social Research Ethics, Survey Methods, IRB

Layer: 3 (Research Ethics)
CardinalStrength: PREDICATIVE
Source: Belmont Report, APA Ethics, AAPOR Standards
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum, auto
from fractions import Fraction


class ResearchType(Enum):
    """Types of sociological research."""
    SURVEY = auto()
    EXPERIMENT = auto()
    ETHNOGRAPHY = auto()
    SECONDARY_ANALYSIS = auto()
    CLINICAL_TRIAL = auto()


class IRBStatus(Enum):
    """IRB review status."""
    EXEMPT = auto()
    EXPEDITED = auto()
    FULL_BOARD = auto()
    PENDING = auto()
    NOT_SUBMITTED = auto()


@dataclass
class ResearchStudy:
    """Sociological research study."""
    study_id: str
    title: str
    researcher_id: str
    research_type: ResearchType
    
    # IRB
    irb_status: IRBStatus
    irb_approval_date: Optional[str]
    informed_consent_obtained: bool
    
    # Participants
    target_sample_size: int
    actual_sample_size: int
    vulnerable_populations: bool  # Minors, prisoners, etc.
    
    # Data protection
    data_anonymized: bool
    data_retention_years: Fraction
    
    # Response rates
    contacts_attempted: int
    responses_received: int
    
    def get_response_rate(self) -> Fraction:
        """Calculate survey response rate."""
        if self.contacts_attempted == 0:
            return Fraction(0)
        return Fraction(self.responses_received, self.contacts_attempted)


@dataclass
class SurveyInstrument:
    """Survey questionnaire instrument."""
    instrument_id: str
    study_id: str
    
    # Quality metrics
    pilot_tested: bool
    cognitive_interviews: int
    pretest_n: int
    
    # Validity
    reliability_coefficient: Fraction  # Cronbach's alpha
    validity_assessed: bool
    
    # Bias checks
    question_order_randomized: bool
    response_option_balance: bool


# Sociology research standards
MIN_RESPONSE_RATE = Fraction(3, 10)  # 30% minimum
MIN_RELIABILITY_ALPHA = Fraction(7, 10)  # 0.70 minimum
MAX_DATA_RETENTION = Fraction(7)  # 7 years


def min_survey_response_rate() -> Fraction:
    """AAPOR minimum acceptable response rate."""
    return MIN_RESPONSE_RATE


def min_reliability_alpha() -> Fraction:
    """Minimum Cronbach's alpha for reliability."""
    return MIN_RELIABILITY_ALPHA
