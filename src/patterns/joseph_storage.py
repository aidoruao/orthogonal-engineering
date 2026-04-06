"""Joseph Storage Pattern

Biblical basis: Genesis 41 — Joseph stores grain during 7 years of plenty
to prepare for 7 years of famine. Systematic preparation for future need.

Application: Cache successful patterns. When a solution works, store it
for future use. Build a library of proven approaches.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import hashlib


@dataclass
class StoredPattern:
    """A cached pattern."""
    pattern_id: str
    name: str
    description: str
    implementation: str  # Code or reference to code
    success_count: int = 0
    failure_count: int = 0
    first_used: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return self.success_count / total


class JosephStorage:
    """
    Implements the Joseph storage pattern.
    
    Cache successful patterns for future use. Build a library of
    proven approaches that can be reused.
    
    Attributes:
        patterns: Dictionary of stored patterns by ID
        storage_path: Where to persist patterns
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.patterns: Dict[str, StoredPattern] = {}
        self.storage_path = storage_path
    
    def store_pattern(
        self,
        pattern_id: str,
        name: str,
        description: str,
        implementation: str,
        tags: Optional[List[str]] = None,
    ) -> StoredPattern:
        """Store a new pattern."""
        pattern = StoredPattern(
            pattern_id=pattern_id,
            name=name,
            description=description,
            implementation=implementation,
            tags=tags or [],
        )
        self.patterns[pattern_id] = pattern
        return pattern
    
    def get_pattern(self, pattern_id: str) -> Optional[StoredPattern]:
        """Retrieve a pattern by ID."""
        return self.patterns.get(pattern_id)
    
    def find_by_tag(self, tag: str) -> List[StoredPattern]:
        """Find all patterns with a given tag."""
        return [p for p in self.patterns.values() if tag in p.tags]
    
    def record_success(self, pattern_id: str) -> None:
        """Record a successful application of a pattern."""
        pattern = self.patterns.get(pattern_id)
        if pattern:
            pattern.success_count += 1
            pattern.last_used = datetime.now()
    
    def record_failure(self, pattern_id: str) -> None:
        """Record a failed application of a pattern."""
        pattern = self.patterns.get(pattern_id)
        if pattern:
            pattern.failure_count += 1
            pattern.last_used = datetime.now()
    
    def get_top_patterns(self, n: int = 10) -> List[StoredPattern]:
        """Get top N patterns by success rate."""
        sorted_patterns = sorted(
            self.patterns.values(),
            key=lambda p: p.success_rate,
            reverse=True,
        )
        return sorted_patterns[:n]
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get statistics on stored patterns."""
        if not self.patterns:
            return {"total_patterns": 0}
        
        total_successes = sum(p.success_count for p in self.patterns.values())
        total_failures = sum(p.failure_count for p in self.patterns.values())
        
        return {
            "total_patterns": len(self.patterns),
            "total_successes": total_successes,
            "total_failures": total_failures,
            "overall_success_rate": (
                total_successes / (total_successes + total_failures)
                if (total_successes + total_failures) > 0 else 0
            ),
            "top_pattern": self.get_top_patterns(1)[0].name if self.patterns else None,
        }
