"""D_MEDIA_LAW implementation — Media Law & Communications Regulation

Layer: 4 (Institutional)
CardinalStrength: PREDICATIVE

Standards:
- First Amendment (US)
- FCC regulations (broadcast, obscenity)
- Defamation law (libel/slander)
- Shield laws (journalist privilege)
- Right of publicity/privacy
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum, auto
from datetime import datetime
from fractions import Fraction


class MediaType(Enum):
    """Types of media outlets."""
    BROADCAST_TV = auto()
    BROADCAST_RADIO = auto()
    CABLE = auto()
    PRINT = auto()
    ONLINE = auto()
    STREAMING = auto()
    PODCAST = auto()
    SOCIAL_MEDIA = auto()


class ContentRating(Enum):
    """Content classification."""
    G = auto()
    PG = auto()
    PG13 = auto()
    R = auto()
    NC17 = auto()
    TVY = auto()
    TVMA = auto()


@dataclass
class BroadcastStation:
    """FCC-licensed broadcast station."""
    call_sign: str
    frequency: str
    media_type: MediaType
    
    license_grant_date: datetime
    license_expiration: datetime
    
    # FCC requirements
    public_file_complete: bool
    children_programming_hours: Fraction
    political_file_current: bool
    
    # Ownership
    owner: str
    station_count: int  # For ownership cap calculation
    
    def license_current(self) -> bool:
        """License not expired."""
        return datetime.now() < self.license_expiration
    
    def meets_children_programming(self) -> bool:
        """Core educational programming requirement (3 hours/week)."""
        return self.children_programming_hours >= Fraction(3)


@dataclass
class PublishedContent:
    """Media publication."""
    content_id: str
    title: str
    media_type: MediaType
    publisher: str
    publish_date: datetime
    
    # Content classification
    rating: Optional[ContentRating]
    contains_explicit: bool
    news_content: bool  # For shield law protection
    
    # Legal flags
    defamation_claim_filed: bool
    retraction_issued: bool
    
    # Sources (for shield law)
    confidential_sources: List[str] = field(default_factory=list)
    source_protection_claimed: bool = False


@dataclass
class DefamationClaim:
    """Libel or slander lawsuit."""
    claim_id: str
    plaintiff: str
    defendant: str
    
    claim_type: str  # libel, slander, slander_per_se
    publication_date: datetime
    
    # Elements
    false_statement: bool
    published_to_third_party: bool
    fault_level: str  # negligence, actual_malice
    damages_claimed: Fraction
    
    # Defenses
    truth_defense: bool
    opinion_defense: bool
    privilege_claimed: str  # absolute, qualified, none
    
    def is_public_figure_claim(self) -> bool:
        """Requires actual malice per NYT v. Sullivan."""
        return self.fault_level == "actual_malice"


@dataclass
class ShieldLawClaim:
    """Journalist privilege against source disclosure."""
    claim_id: str
    journalist: str
    media_outlet: str
    
    subpoena_date: datetime
    information_sought: str
    
    # Qualification
    qualified_journalist: bool  # Employed, freelancer with history
    information_confidential: bool
    
    # Outcome
    privilege_recognized: Optional[bool]
    contempt_issued: bool


@dataclass
class RightOfPublicity:
    """Personality rights commercial use."""
    personality_id: str
    person_name: str
    
    # Commercial use
    likeness_used_without_consent: bool
    commercial_purpose: bool
    use_value: Fraction
    
    # Post-mortem rights (varies by state)
    person_deceased: bool
    years_since_death: int


@dataclass
class MediaLawChecker:
    """Checker for media law compliance."""
    stations: List[BroadcastStation] = field(default_factory=list)
    content: List[PublishedContent] = field(default_factory=list)
    defamation_claims: List[DefamationClaim] = field(default_factory=list)
    shield_claims: List[ShieldLawClaim] = field(default_factory=list)
    
    def expired_broadcast_licenses(self) -> List[BroadcastStation]:
        """Stations with expired FCC licenses."""
        return [s for s in self.stations if not s.license_current()]
    
    def children_programming_deficient(self) -> List[BroadcastStation]:
        """Stations not meeting children's programming requirements."""
        return [s for s in self.stations if not s.meets_children_programming()]
    
    def pending_defamation(self) -> List[DefamationClaim]:
        """Active defamation suits."""
        return [d for d in self.defamation_claims if not d.truth_defense]
    
    def shield_violations(self) -> List[ShieldLawClaim]:
        """Journalists held in contempt for protecting sources."""
        return [s for s in self.shield_claims if s.contempt_issued]
