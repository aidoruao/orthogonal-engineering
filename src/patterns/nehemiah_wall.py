"""Nehemiah Wall Pattern

Biblical basis: Nehemiah 4 — builders worked with trowel in one hand
and sword in the other. Implementation and defense together.

Application: Implementation + test in the same commit. No code without
corresponding tests. No test without code that makes it pass.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
from enum import Enum, auto


class WallStatus(Enum):
    """Status of a Nehemiah wall (implementation + test pair)."""
    COMPLETE = auto()      # Both implementation and tests present
    INCOMPLETE = auto()    # Missing one side
    BREACH = auto()        # Tests failing


@dataclass
class WallSection:
    """A section of the wall — implementation + test pair."""
    section_id: str
    implementation_file: Path
    test_file: Path
    description: str
    status: WallStatus = WallStatus.INCOMPLETE
    
    def is_complete(self) -> bool:
        """Check if both files exist."""
        return (
            self.implementation_file.exists() and
            self.test_file.exists()
        )


class NehemiahWall:
    """
    Implements the Nehemiah wall pattern.
    
    Every implementation must have corresponding tests.
    Every test must have corresponding implementation.
    
    Attributes:
        sections: List of wall sections being tracked
    """
    
    def __init__(self):
        self.sections: List[WallSection] = []
    
    def add_section(
        self,
        section_id: str,
        implementation_file: Path,
        test_file: Path,
        description: str,
    ) -> WallSection:
        """Add a new wall section."""
        section = WallSection(
            section_id=section_id,
            implementation_file=Path(implementation_file),
            test_file=Path(test_file),
            description=description,
        )
        self.sections.append(section)
        return section
    
    def check_wall_integrity(self) -> Dict[str, Any]:
        """
        Check integrity of all wall sections.
        
        Returns:
            Dict with status summary
        """
        complete = 0
        incomplete = 0
        breaches = []
        
        for section in self.sections:
            if section.is_complete():
                complete += 1
                # In real implementation, would run tests here
            else:
                incomplete += 1
                missing = []
                if not section.implementation_file.exists():
                    missing.append("implementation")
                if not section.test_file.exists():
                    missing.append("tests")
                breaches.append({
                    "section": section.section_id,
                    "missing": missing,
                })
        
        return {
            "total_sections": len(self.sections),
            "complete": complete,
            "incomplete": incomplete,
            "breaches": breaches,
            "integrity_percentage": (complete / len(self.sections) * 100) if self.sections else 0,
        }
    
    def enforce_wall(self) -> bool:
        """
        Enforce the wall — fail if any section is incomplete.
        
        Returns:
            True if all sections are complete
        """
        result = self.check_wall_integrity()
        return result["incomplete"] == 0
    
    def get_sections_missing_tests(self) -> List[WallSection]:
        """Get sections missing test files."""
        return [
            s for s in self.sections
            if s.implementation_file.exists() and not s.test_file.exists()
        ]
    
    def get_sections_missing_implementation(self) -> List[WallSection]:
        """Get sections missing implementation files."""
        return [
            s for s in self.sections
            if s.test_file.exists() and not s.implementation_file.exists()
        ]
