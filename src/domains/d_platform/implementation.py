"""D_PLATFORM implementation — Platform Governance, Content Moderation, Interoperability

Layer: 3 (Digital Regulation)
CardinalStrength: PREDICATIVE
Source: DSA, DMA, Platform Transparency laws
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum, auto
from fractions import Fraction


class PlatformType(Enum):
    """Type of digital platform."""
    SOCIAL_MEDIA = auto()
    MARKETPLACE = auto()
    SEARCH_ENGINE = auto()
    APP_STORE = auto()
    MESSAGING = auto()


class ContentDecision(Enum):
    """Content moderation decision."""
    REMOVE = auto()
    RESTRICT = auto()
    MONETIZE = auto()
    NO_ACTION = auto()


@dataclass
class ContentModeration:
    """Content moderation action."""
    decision_id: str
    platform_id: str
    content_type: str
    
    decision: ContentDecision
    automated: bool  # Algorithmic or human review
    human_oversight: bool  # Human reviewed automated decision
    
    # Transparency
    user_notified: bool
    reason_provided: bool
    appeal_available: bool
    
    # Timing
    content_posted: str
    decision_made: str
    appeal_filed: Optional[str]
    appeal_resolved: Optional[str]


@dataclass
class DigitalPlatform:
    """Online platform operator."""
    platform_id: str
    name: str
    platform_type: PlatformType
    
    # Scale (DSA VLOP thresholds)
    monthly_active_users: Fraction
    eu_users: Fraction
    
    # Content moderation
    moderators_employed: int
    content_removed_annual: int
    appeals_received: int
    appeals_upheld: int
    
    # Transparency
    transparency_report_published: bool
    ad_repository_public: bool
    recommendation_algorithm_disclosed: bool
    
    def get_appeal_upheld_rate(self) -> Fraction:
        """Calculate appeal success rate."""
        if self.appeals_received == 0:
            return Fraction(0)
        return Fraction(self.appeals_upheld, self.appeals_received)
    
    def is_vlop(self) -> bool:
        """Check if Very Large Online Platform per DSA."""
        return self.eu_users >= 45000000  # 45 million EU users


# Platform standards
DSA_APPEAL_RESPONSE_DAYS = Fraction(1)  # Expedited handling
VLOP_USER_THRESHOLD = Fraction(45000000)  # 45 million
MIN_APPEAL_TRANSPARENCY = Fraction(5, 100)  # 5% appeal rate acceptable


def dsa_appeal_target_days() -> Fraction:
    """DSA target for appeal response."""
    return DSA_APPEAL_RESPONSE_DAYS


def vlop_user_threshold() -> Fraction:
    """DSA VLOP user threshold."""
    return VLOP_USER_THRESHOLD
