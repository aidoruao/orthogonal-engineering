"""D_GAMEMODS implementation — Game Modifications & User-Generated Content

Layer: 4 (Institutional - Media/Creative)
CardinalStrength: PREDICATIVE

Regulatory/Technical Standards:
- EULA compliance and modding policy
- Copyright fair use (transformative works)
- Platform content moderation
- Mod API versioning
- Asset integrity verification
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime
from fractions import Fraction
import hashlib


class ModType(Enum):
    """Types of game modifications."""
    TOTAL_CONVERSION = auto()
    GAMEPLAY_OVERHAUL = auto()
    CONTENT_ADDITION = auto()      # New items, quests
    VISUAL_ENHANCEMENT = auto()
    UTILITY = auto()               # Bug fixes, performance
    CHEAT = auto()                 # Unauthorized advantages


class ModStatus(Enum):
    """Lifecycle status of a mod."""
    DEVELOPMENT = auto()
    BETA = auto()
    RELEASED = auto()
    DEPRECATED = auto()
    REMOVED = auto()


class DistributionPlatform(Enum):
    """Where mods are distributed."""
    WORKSHOP = auto()              # Steam Workshop
    NEXUS = auto()                 # Nexus Mods
    CURSEFORGE = auto()
    DIRECT = auto()                # Direct download
    INGAME = auto()                # Built-in marketplace


@dataclass(frozen=True)
class GameVersion:
    """Semantic versioning for game compatibility."""
    major: int
    minor: int
    patch: int
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def is_compatible_with(self, other: GameVersion) -> bool:
        """Same major version typically required for mod compatibility."""
        return self.major == other.major
    
    def is_at_least(self, other: GameVersion) -> bool:
        """Version comparison."""
        if self.major != other.major:
            return self.major > other.major
        if self.minor != other.minor:
            return self.minor > other.minor
        return self.patch >= other.patch


@dataclass(frozen=True)
class AssetChecksum:
    """Content-addressed asset verification."""
    asset_path: str
    sha256: str
    size_bytes: int
    
    def verify_content(self, content: bytes) -> bool:
        """Verify content matches checksum."""
        computed = hashlib.sha256(content).hexdigest()
        return computed == self.sha256


@dataclass
class Mod:
    """A game modification."""
    mod_id: str
    name: str
    author: str
    mod_type: ModType
    status: ModStatus
    
    # Versioning
    mod_version: GameVersion
    supported_game_versions: List[GameVersion]
    
    # Content
    description: str
    assets: List[AssetChecksum] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # mod_ids
    
    # Distribution
    platforms: List[DistributionPlatform] = field(default_factory=list)
    download_count: int = 0
    rating: Fraction = Fraction(0)  # 0-5
    
    # Compliance
    license: str = ""
    eula_compliant: bool = True
    contains_third_party_ip: bool = False
    
    def supports_game_version(self, game_version: GameVersion) -> bool:
        """Check if mod supports a specific game version."""
        for supported in self.supported_game_versions:
            if supported.is_compatible_with(game_version):
                return True
        return False
    
    def is_total_conversion(self) -> bool:
        """Total conversions replace most game content."""
        return self.mod_type == ModType.TOTAL_CONVERSION
    
    def has_unresolved_dependencies(self, available_mods: Set[str]) -> List[str]:
        """Find missing dependencies."""
        return [dep for dep in self.dependencies if dep not in available_mods]


@dataclass
class ModConflict:
    """Compatibility conflict between mods."""
    mod_a: str
    mod_b: str
    conflict_type: str  # asset_override, script_incompatibility, etc.
    severity: str  # minor, major, critical
    resolution: Optional[str] = None  # load_order, patch_available, etc.


@dataclass
class ModLoadOrder:
    """Deterministic mod loading sequence."""
    ordered_mods: List[str]  # mod_ids in load order
    conflicts: List[ModConflict] = field(default_factory=list)
    
    def is_valid(self) -> bool:
        """Load order resolves all critical conflicts."""
        critical = [c for c in self.conflicts if c.severity == "critical"]
        return len(critical) == 0 or all(c.resolution for c in critical)
    
    def get_position(self, mod_id: str) -> int:
        """0-indexed position in load order."""
        try:
            return self.ordered_mods.index(mod_id)
        except ValueError:
            return -1
    
    def loads_before(self, mod_a: str, mod_b: str) -> bool:
        """Check if mod_a loads before mod_b."""
        pos_a = self.get_position(mod_a)
        pos_b = self.get_position(mod_b)
        return pos_a >= 0 and pos_b >= 0 and pos_a < pos_b


@dataclass
class ContentModerationReport:
    """Moderation action on mod content."""
    report_id: str
    mod_id: str
    reported_by: str
    reason: str  # copyright, malware, offensive, etc.
    status: str  # pending, approved, rejected
    reviewed_by: Optional[str] = None
    review_date: Optional[datetime] = None
    
    def is_resolved(self) -> bool:
        """Report has been reviewed."""
        return self.status in ("approved", "rejected")


@dataclass
class GameModChecker:
    """Checker for mod compatibility and compliance."""
    mods: List[Mod] = field(default_factory=list)
    load_orders: List[ModLoadOrder] = field(default_factory=list)
    reports: List[ContentModerationReport] = field(default_factory=list)
    
    def find_conflicts(self) -> List[ModConflict]:
        """Identify all mod conflicts."""
        conflicts = []
        for lo in self.load_orders:
            conflicts.extend(lo.conflicts)
        return conflicts
    
    def incompatible_mods(self, game_version: GameVersion) -> List[Mod]:
        """Mods not supporting current game version."""
        return [m for m in self.mods if not m.supports_game_version(game_version)]
    
    def pending_moderation(self) -> List[ContentModerationReport]:
        """Unresolved moderation reports."""
        return [r for r in self.reports if not r.is_resolved()]
    
    def critical_conflicts(self) -> List[ModConflict]:
        """Conflicts preventing game launch."""
        return [c for c in self.find_conflicts() if c.severity == "critical"]
    
    def verify_asset_integrity(self, mod_id: str, asset_data: Dict[str, bytes]) -> List[str]:
        """Verify mod assets match registered checksums."""
        mod = next((m for m in self.mods if m.mod_id == mod_id), None)
        if not mod:
            return ["Mod not found"]
        
        failed = []
        for asset in mod.assets:
            content = asset_data.get(asset.asset_path)
            if content is None:
                failed.append(f"Missing: {asset.asset_path}")
            elif not asset.verify_content(content):
                failed.append(f"Corrupt: {asset.asset_path}")
        
        return failed
