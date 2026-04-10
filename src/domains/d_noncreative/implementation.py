"""D_NONCREATIVE implementation — Non-Creative Works, Public Domain, Orphan Works

Layer: 3 (Legal/IP)
CardinalStrength: PREDICATIVE
Source: Copyright Act § 102, Bridgeman v. Corel, Feist v. Rural
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum, auto
from fractions import Fraction


class WorkType(Enum):
    """Types of potentially non-creative works."""
    FACTUAL_COMPILATION = auto()
    SLAVISH_COPY = auto()
    MECHANICAL_REPRODUCTION = auto()
    STANDARD_FORMS = auto()
    GOVERNMENT_WORK = auto()


class CopyrightStatus(Enum):
    """Copyright status determination."""
    PUBLIC_DOMAIN = auto()
    COPYRIGHTED = auto()
    ORPHAN_WORK = auto()
    UNCERTAIN = auto()


@dataclass
class Work:
    """A creative or non-creative work."""
    work_id: str
    title: str
    work_type: WorkType
    
    # Creativity factors (0-1 scale as Fraction)
    selection_originality: Fraction
    arrangement_originality: Fraction
    coordination_originality: Fraction
    
    # Source
    is_government_work: bool
    author_known: bool
    author_deceased: bool
    creation_year: int
    publication_year: Optional[int]
    
    # Orphan work criteria
    owner_search_efforts: int  # Number of search attempts
    registry_searches: int
    professional_searches: int
    
    def get_creativity_score(self) -> Fraction:
        """Calculate overall creativity score."""
        return (self.selection_originality + 
                self.arrangement_originality + 
                self.coordination_originality) / 3
    
    def is_likely_public_domain(self) -> bool:
        """Check if work is likely in public domain."""
        if self.is_government_work:
            return True
        if self.author_deceased and self.creation_year < 1929:
            return True
        return False


@dataclass
class FactualCompilation:
    """Factual compilation work (e.g., database, phone book)."""
    compilation_id: str
    title: str
    
    # Feist factors
    facts_collected: int
    selection_criteria_original: bool
    arrangement_original: bool
    effort_in_collection: Fraction  # Sweat of the brow not protected
    
    def has_minimal_creativity(self) -> bool:
        """Check if compilation has minimal creativity (Feist standard)."""
        return self.selection_criteria_original or self.arrangement_original


# Copyright thresholds
MINIMAL_CREATIVITY_THRESHOLD = Fraction(1, 10)  # Some minimal creativity required
ORPHAN_SEARCH_THRESHOLD = 3  # Minimum search efforts for orphan work presumption
PUBLIC_DOMAIN_YEAR = 1929  # Pre-1929 works generally public domain


def minimal_creativity_threshold() -> Fraction:
    """Threshold for minimal creativity (Feist v. Rural)."""
    return MINIMAL_CREATIVITY_THRESHOLD


def orphan_work_search_threshold() -> int:
    """Minimum search efforts for orphan work determination."""
    return ORPHAN_SEARCH_THRESHOLD
