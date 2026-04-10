"""D_GAMING implementation — Video Games & Interactive Entertainment

Layer: 4 (Institutional - Entertainment)
CardinalStrength: PREDICATIVE

Standards:
- ESRB/PEGI rating systems
- Platform certification (TCR/TRC)
- Accessibility guidelines (CVAA, WCAG)
- Online safety (COPPA, GDPR-K)
- Loot box regulations (various jurisdictions)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction


class RatingSystem(Enum):
    """Age rating systems."""
    ESRB = auto()  # US/Canada
    PEGI = auto()  # Europe
    CERO = auto()  # Japan
    USK = auto()   # Germany
    GRAC = auto()  # Korea


class ContentDescriptor(Enum):
    """Content warning descriptors."""
    VIOLENCE = auto()
    LANGUAGE = auto()
    SEXUAL_CONTENT = auto()
    SUBSTANCE_USE = auto()
    GAMBLING = auto()
    FEAR = auto()
    ONLINE_INTERACTION = auto()


class Platform(Enum):
    """Gaming platforms."""
    PC = auto()
    PLAYSTATION = auto()
    XBOX = auto()
    NINTENDO = auto()
    MOBILE = auto()
    WEB = auto()


class MonetizationType(Enum):
    """How games generate revenue."""
    PREMIUM = auto()           # One-time purchase
    SUBSCRIPTION = auto()      # Recurring fee
    FREEMIUM = auto()          # Free with IAP
    AD_SUPPORTED = auto()
    LOOT_BOX = auto()          # Randomized rewards


@dataclass(frozen=True)
class AgeRating:
    """Age rating in a specific system."""
    system: RatingSystem
    rating: str  # E: Everyone, T: Teen, M: Mature, etc.
    minimum_age: int
    descriptors: Set[ContentDescriptor]
    
    def is_appropriate_for(self, age: int) -> bool:
        """Check if content appropriate for given age."""
        return age >= self.minimum_age


@dataclass
class AccessibilityFeature:
    """Game accessibility accommodations."""
    feature_id: str
    name: str
    description: str
    target_disabilities: List[str]  # motor, vision, hearing, cognitive
    implemented: bool
    configurable: bool


@dataclass
class GamingSession:
    """A play session with telemetry."""
    session_id: str
    player_id: str
    game_id: str
    start_time: datetime
    duration: timedelta
    
    # Safety metrics
    chat_messages_sent: int
    chat_messages_reported: int
    purchases_made: int
    purchase_amount: Fraction  # In local currency
    
    def spending_rate(self) -> Fraction:
        """Spending per hour."""
        hours = Fraction(self.duration.total_seconds()) / 3600
        if hours == 0:
            return Fraction(0)
        return self.purchase_amount / hours
    
    def report_rate(self) -> Fraction:
        """Fraction of chat messages reported."""
        if self.chat_messages_sent == 0:
            return Fraction(0)
        return Fraction(self.chat_messages_reported, self.chat_messages_sent)


@dataclass
class LootBox:
    """Randomized reward mechanism."""
    box_id: str
    name: str
    price: Fraction
    currency: str
    
    # Drop rates (must sum to 1)
    drop_rates: Dict[str, Fraction]  # item_id -> probability
    
    # Regulatory compliance
    odds_disclosed: bool
    pity_timer: Optional[int] = None  # Guaranteed drop after N tries
    
    def expected_value(self, item_values: Dict[str, Fraction]) -> Fraction:
        """Expected monetary value of box contents."""
        total = Fraction(0)
        for item_id, rate in self.drop_rates.items():
            value = item_values.get(item_id, Fraction(0))
            total += rate * value
        return total
    
    def is_fair_value(self, item_values: Dict[str, Fraction]) -> bool:
        """Expected value >= price (player expectation)."""
        return self.expected_value(item_values) >= self.price


@dataclass
class Game:
    """A video game product."""
    game_id: str
    title: str
    developer: str
    publisher: str
    release_date: datetime
    
    # Ratings
    ratings: List[AgeRating] = field(default_factory=list)
    monetization: List[MonetizationType] = field(default_factory=list)
    platforms: List[Platform] = field(default_factory=list)
    
    # Features
    accessibility_features: List[AccessibilityFeature] = field(default_factory=list)
    online_features: bool = False
    cross_platform: bool = False
    
    # Safety
    parental_controls: bool = False
    play_time_limits: bool = False
    spending_limits: bool = False
    
    def get_rating(self, system: RatingSystem) -> Optional[AgeRating]:
        """Get rating for specific system."""
        for r in self.ratings:
            if r.system == system:
                return r
        return None
    
    def minimum_age(self) -> int:
        """Highest minimum age across all rating systems."""
        if not self.ratings:
            return 0
        return max(r.minimum_age for r in self.ratings)
    
    def has_loot_boxes(self) -> bool:
        """Game contains randomized reward mechanics."""
        return MonetizationType.LOOT_BOX in self.monetization
    
    def accessibility_coverage(self) -> Fraction:
        """Fraction of standard accessibility features implemented."""
        STANDARD_FEATURES = 12  # Colorblind, subtitles, remapping, etc.
        implemented = sum(1 for f in self.accessibility_features if f.implemented)
        return Fraction(implemented, STANDARD_FEATURES)


@dataclass
class Player:
    """A player account."""
    player_id: str
    account_created: datetime
    date_of_birth: Optional[datetime]
    parent_email: Optional[str]  # For COPPA compliance
    
    verified_adult: bool = False
    spending_limit_weekly: Optional[Fraction] = None
    play_time_limit_daily: Optional[timedelta] = None
    
    def age(self) -> Optional[int]:
        """Current age if DOB known."""
        if self.date_of_birth is None:
            return None
        from datetime import datetime
        days = (datetime.now() - self.date_of_birth).days
        return days // 365
    
    def is_minor(self) -> bool:
        """Under 18 (or 13 for COPPA)."""
        age = self.age()
        if age is None:
            return not self.verified_adult
        return age < 18
    
    def coppa_requires_consent(self) -> bool:
        """Under 13 requires parental consent."""
        age = self.age()
        if age is None:
            return False
        return age < 13


@dataclass
class GamingChecker:
    """Checker for game compliance and safety."""
    games: List[Game] = field(default_factory=list)
    players: List[Player] = field(default_factory=list)
    sessions: List[GamingSession] = field(default_factory=list)
    loot_boxes: List[LootBox] = field(default_factory=list)
    
    def age_inappropriate_games(self, player: Player) -> List[Game]:
        """Games player is too young for."""
        age = player.age()
        if age is None:
            return []
        return [g for g in self.games if g.minimum_age() > age]
    
    def unmonitored_minors(self) -> List[Player]:
        """Minors without parental controls."""
        return [p for p in self.players if p.is_minor() and not p.parent_email]
    
    def high_spenders(self, threshold: Fraction) -> List[GamingSession]:
        """Sessions with spending above threshold."""
        return [s for s in self.sessions if s.purchase_amount > threshold]
    
    def undisclosed_loot_box_odds(self) -> List[LootBox]:
        """Loot boxes not disclosing drop rates."""
        return [lb for lb in self.loot_boxes if not lb.odds_disclosed]
