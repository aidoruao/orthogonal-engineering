"""D_FUN implementation — Play, Games, and Recreation

Layer: 4 (Institutional - Social/Cultural)
CardinalStrength: PREDICATIVE

Theoretical Standards:
- Huizinga's Homo Ludens
- Caillois' paidia vs ludus
- Flow theory (Csikszentmihalyi)
- Self-determination theory (autonomy, competence, relatedness)
- Bartle taxonomy (achiever, explorer, socializer, killer)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction


class PlayType(Enum):
    """Caillois' classification of play."""
    COMPETITION = auto()     # agon
    CHANCE = auto()          # alea
    SIMULATION = auto()      # mimicry
    VERTIGO = auto()         # ilinx


class PlayStructure(Enum):
    """Caillois' structure dimension."""
    PAIDIA = auto()          # Free, spontaneous, unstructured
    LUDUS = auto()           # Rule-bound, structured, institutionalized


class BartleType(Enum):
    """Bartle player taxonomy."""
    ACHIEVER = auto()        # Focus on game goals
    EXPLORER = auto()        # Focus on discovery
    SOCIALIZER = auto()      # Focus on relationships
    KILLER = auto()          # Focus on competition/domination


class FlowDimension(Enum):
    """Dimensions of flow state (Csikszentmihalyi)."""
    CHALLENGE_SKILL_BALANCE = auto()
    CLEAR_GOALS = auto()
    IMMEDIATE_FEEDBACK = auto()
    SENSE_OF_CONTROL = auto()
    LOSS_OF_SELF_CONSCIOUSNESS = auto()
    TRANSFORMATION_OF_TIME = auto()


@dataclass(frozen=True)
class Player:
    """A participant in play or games."""
    player_id: str
    bartle_profile: Dict[BartleType, Fraction]  # Fraction adding to 1
    skill_level: Fraction  # 0-1 normalized
    
    def dominant_type(self) -> BartleType:
        """Primary player motivation."""
        return max(self.bartle_profile, key=lambda k: self.bartle_profile[k])


@dataclass
class Game:
    """A structured form of play."""
    game_id: str
    title: str
    play_types: Set[PlayType]
    structure: PlayStructure
    
    # Flow characteristics
    challenge_range: Tuple[Fraction, Fraction]  # min, max difficulty
    clear_rules: bool
    feedback_frequency: Fraction  # How often feedback given (0-1)
    
    # Social features
    min_players: int
    max_players: int
    cooperative: bool
    
    def supports_player_count(self, n: int) -> bool:
        """Check if game supports n players."""
        return self.min_players <= n <= self.max_players
    
    def flow_compatibility(self, player_skill: Fraction) -> Fraction:
        """How well game matches player skill for flow."""
        min_chal, max_chal = self.challenge_range
        
        # Optimal flow when challenge ≈ skill
        if min_chal <= player_skill <= max_chal:
            return Fraction(1)
        
        # Calculate distance from optimal range
        if player_skill < min_chal:
            distance = min_chal - player_skill
        else:
            distance = player_skill - max_chal
        
        # Compatibility decreases with distance
        return max(Fraction(0), Fraction(1) - distance)


@dataclass
class PlaySession:
    """An instance of play."""
    session_id: str
    game: Game
    players: List[Player]
    start_time: datetime
    duration: timedelta
    
    # Flow measurements
    reported_flow: Optional[Fraction] = None  # Player-reported 0-1
    measured_engagement: Optional[Fraction] = None  # Behavioral metric
    
    def player_count(self) -> int:
        """Number of participants."""
        return len(self.players)
    
    def is_valid_session(self) -> bool:
        """Session meets game requirements."""
        return self.game.supports_player_count(self.player_count())
    
    def average_skill(self) -> Fraction:
        """Mean skill level of participants."""
        if not self.players:
            return Fraction(0)
        total = sum(p.skill_level for p in self.players)
        return total / len(self.players)
    
    def dominant_bartle_type(self) -> Optional[BartleType]:
        """Most common player type in session."""
        if not self.players:
            return None
        
        type_counts = {t: Fraction(0) for t in BartleType}
        for player in self.players:
            dom = player.dominant_type()
            type_counts[dom] += Fraction(1)
        
        return max(type_counts, key=lambda k: type_counts[k])


@dataclass
class FlowState:
    """Flow state assessment for a play session."""
    session: PlaySession
    
    # Csikszentmihalyi's flow channel dimensions
    challenge_level: Fraction
    skill_level: Fraction
    
    # Flow conditions
    clear_goals_present: bool
    immediate_feedback_present: bool
    control_sense: Fraction  # 0-1
    
    def in_flow_channel(self) -> bool:
        """True if challenge and skill balanced at high level."""
        # Flow when challenge ≈ skill and both moderately high
        balance = Fraction(1) - abs(self.challenge_level - self.skill_level)
        level = (self.challenge_level + self.skill_level) / 2
        
        # Need good balance and decent level
        return balance > Fraction(3, 4) and level > Fraction(1, 2)
    
    def flow_score(self) -> Fraction:
        """Overall flow likelihood (0-1)."""
        if not self.clear_goals_present:
            return Fraction(0)
        if not self.immediate_feedback_present:
            return Fraction(0)
        
        # Weighted combination
        balance = Fraction(1) - abs(self.challenge_level - self.skill_level)
        conditions = (self.control_sense + balance) / 2
        
        if not self.in_flow_channel():
            conditions = conditions / 2
        
        return conditions
    
    def state_classification(self) -> str:
        """Classify psychological state based on challenge/skill."""
        diff = self.challenge_level - self.skill_level
        
        if abs(diff) < Fraction(1, 4):
            if self.challenge_level > Fraction(1, 2):
                return "flow"
            else:
                return "apathy"
        elif diff > Fraction(0):
            return "anxiety"
        else:
            return "boredom"


@dataclass
class FunChecker:
    """Checker for play and game design properties."""
    games: List[Game] = field(default_factory=list)
    sessions: List[PlaySession] = field(default_factory=list)
    flow_states: List[FlowState] = field(default_factory=list)
    
    def games_for_player_type(self, bartle_type: BartleType) -> List[Game]:
        """Recommend games based on player type."""
        # Mapping: achiever -> competition, explorer -> simulation, etc.
        type_to_play = {
            BartleType.ACHIEVER: PlayType.COMPETITION,
            BartleType.EXPLORER: PlayType.SIMULATION,
            BartleType.SOCIALIZER: PlayType.CHANCE,  # Social luck
            BartleType.KILLER: PlayType.COMPETITION
        }
        target = type_to_play.get(bartle_type)
        return [g for g in self.games if target in g.play_types]
    
    def flow_sessions(self) -> List[PlaySession]:
        """Sessions where flow state was achieved."""
        flow_session_ids = {
            fs.session.session_id for fs in self.flow_states if fs.in_flow_channel()
        }
        return [s for s in self.sessions if s.session_id in flow_session_ids]
    
    def average_session_duration(self) -> timedelta:
        """Mean play session length."""
        if not self.sessions:
            return timedelta(0)
        total = sum((s.duration.total_seconds() for s in self.sessions), 0)
        avg = total / len(self.sessions)
        return timedelta(seconds=avg)
