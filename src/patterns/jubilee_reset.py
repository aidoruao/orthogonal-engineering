"""Jubilee Reset Pattern

Biblical basis: Leviticus 25 — every 50 years, debts are forgiven and 
property returns to original owners. A systematic reset of accumulated burden.

Application: Technical debt counter reset. After a major release or 
milestone, reset the tech debt counter to zero and re-evaluate all 
outstanding issues fresh.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any


@dataclass
class TechDebtItem:
    """A single item of technical debt."""
    id: str
    description: str
    created_at: datetime
    severity: str  # "low", "medium", "high", "critical"
    context: Dict[str, Any]


class JubileeReset:
    """
    Implements the Jubilee reset pattern for technical debt.
    
    Every 50th iteration (or configurable interval), reset the debt counter
    and require re-justification of all outstanding items.
    
    Attributes:
        reset_interval: Number of iterations between resets (default: 50)
        iteration_count: Current iteration
        debt_items: List of accumulated technical debt
        reset_history: History of past resets
    """
    
    def __init__(self, reset_interval: int = 50):
        self.reset_interval = reset_interval
        self.iteration_count = 0
        self.debt_items: List[TechDebtItem] = []
        self.reset_history: List[datetime] = []
    
    def add_debt(self, item: TechDebtItem) -> None:
        """Add a technical debt item."""
        self.debt_items.append(item)
    
    def iterate(self) -> bool:
        """
        Increment iteration counter and check if reset is due.
        
        Returns:
            True if a reset was triggered this iteration
        """
        self.iteration_count += 1
        
        if self.iteration_count >= self.reset_interval:
            self.reset()
            return True
        
        return False
    
    def reset(self) -> List[TechDebtItem]:
        """
        Perform Jubilee reset: clear all debt and return archived items.
        
        Returns:
            List of debt items that were cleared (for archival)
        """
        archived = self.debt_items.copy()
        self.debt_items = []
        self.iteration_count = 0
        self.reset_history.append(datetime.now())
        return archived
    
    def get_debt_summary(self) -> Dict[str, int]:
        """Get summary of current debt by severity."""
        summary = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for item in self.debt_items:
            summary[item.severity] = summary.get(item.severity, 0) + 1
        return summary
    
    def next_reset_in(self) -> int:
        """Return number of iterations until next reset."""
        return self.reset_interval - self.iteration_count
