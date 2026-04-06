"""Gideon Reduction Pattern

Biblical basis: Judges 7 — Gideon's army reduced from 32,000 to 300.
Quality over quantity. Fearful sent home. Those who knelt to drink
sent home. Only the alert remained.

Application: Strip unnecessary dependencies. Remove code that doesn't
contribute to the core mission. Keep only what's essential.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Set
from pathlib import Path


@dataclass
class Dependency:
    """A dependency to evaluate."""
    name: str
    is_external: bool  # True if external package, False if internal
    usage_count: int   # How many places use this dependency
    is_essential: bool # Is this dependency required for core functionality


class GideonReduction:
    """
    Implements the Gideon reduction pattern.
    
    Strip dependencies that don't contribute to core mission.
    Remove code bloat. Keep only what's essential.
    
    Attributes:
        dependencies: List of dependencies being tracked
        core_mission: Description of core mission for evaluation
    """
    
    def __init__(self, core_mission: str = ""):
        self.dependencies: List[Dependency] = []
        self.core_mission = core_mission
        self.removed_dependencies = []
    
    def add_dependency(self, dep: Dependency) -> None:
        """Add a dependency for evaluation."""
        self.dependencies.append(dep)
    
    def evaluate_reduction(self) -> Dict[str, List[Dependency]]:
        """
        Evaluate which dependencies can be removed.
        
        Returns:
            Dict with 'keep' and 'remove' lists
        """
        keep = []
        remove = []
        
        for dep in self.dependencies:
            if dep.is_essential:
                keep.append(dep)
            elif dep.usage_count == 0:
                # Unused dependency — remove
                remove.append(dep)
            elif dep.is_external and dep.usage_count < 3:
                # External dependency with low usage — consider removal
                remove.append(dep)
            else:
                keep.append(dep)
        
        return {"keep": keep, "remove": remove}
    
    def apply_reduction(self) -> List[Dependency]:
        """
        Apply reduction and return removed dependencies.
        
        Note: This doesn't actually remove files — it returns
        recommendations for the developer to act on.
        """
        evaluation = self.evaluate_reduction()
        removed = evaluation["remove"]
        
        # Update dependency list
        self.dependencies = evaluation["keep"]
        self.removed_dependencies.extend(removed)
        
        return removed
    
    def get_reduction_stats(self) -> Dict[str, Any]:
        """Get statistics on reduction."""
        evaluation = self.evaluate_reduction()
        
        return {
            "total_dependencies": len(self.dependencies),
            "recommended_keep": len(evaluation["keep"]),
            "recommended_remove": len(evaluation["remove"]),
            "already_removed": len(self.removed_dependencies),
            "reduction_percentage": (
                len(evaluation["remove"]) / len(self.dependencies) * 100
                if self.dependencies else 0
            ),
        }
    
    def check_external_dependency(self, name: str) -> bool:
        """Check if an external dependency is in the keep list."""
        evaluation = self.evaluate_reduction()
        return any(d.name == name for d in evaluation["keep"])
