"""Pattern: Equity Threshold

Implements the requirement that resource distribution variance stays
within bounds. No group can monopolize resources.

Mathematical: variance(allocations) ≤ threshold
           Gini coefficient ≤ threshold

Used by: D_SCHOOL_FUNDING, D_NEIGHBORHOOD_EQUITY, D_SCHOOL_EQUITY,
D_TRANSIT, D_UTILITY_REGULATION
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from fractions import Fraction
import statistics


@dataclass
class Allocation:
    """A resource allocation."""
    recipient_id: str
    amount: Fraction
    population: int = 1  # For per-capita calculations
    
    @property
    def per_capita(self) -> Fraction:
        """Calculate per-capita amount."""
        if self.population == 0:
            return Fraction(0)
        return self.amount / self.population


class EquityThreshold:
    """
    Enforces equity thresholds on resource allocations.
    
    Resource distribution must stay within bounded variance.
No recipient can receive disproportionate share.
    
    Attributes:
        variance_threshold: Maximum allowed variance
        gini_threshold: Maximum allowed Gini coefficient
    """
    
    def __init__(
        self,
        variance_threshold: Fraction = Fraction(15, 100),  # 15%
        gini_threshold: Fraction = Fraction(4, 10),       # 0.4
    ):
        self.variance_threshold = variance_threshold
        self.gini_threshold = gini_threshold
        self.violations: list = []
    
    def calculate_variance(self, allocations: List[Allocation]) -> Fraction:
        """Calculate variance of per-capita allocations."""
        if len(allocations) < 2:
            return Fraction(0)
        
        values = [float(a.per_capita) for a in allocations]
        mean = statistics.mean(values)
        variance = statistics.variance(values)
        
        # Return as fraction of mean (coefficient of variation squared)
        if mean == 0:
            return Fraction(0)
        return Fraction(int(variance * 10000), int(mean * mean * 10000))
    
    def calculate_gini(self, allocations: List[Allocation]) -> Fraction:
        """
        Calculate Gini coefficient.
        
        Gini = 0 means perfect equality.
        Gini = 1 means perfect inequality.
        """
        if len(allocations) < 2:
            return Fraction(0)
        
        values = sorted([float(a.per_capita) for a in allocations])
        n = len(values)
        cumsum = 0
        for i, v in enumerate(values):
            cumsum += (i + 1) * v
        
        total = sum(values)
        if total == 0:
            return Fraction(0)
        
        gini = (2 * cumsum) / (n * total) - (n + 1) / n
        return Fraction(int(gini * 1000), 1000)
    
    def check_equity(self, allocations: List[Allocation]) -> Dict[str, Any]:
        """
        Check if allocations meet equity thresholds.
        
        Returns:
            Dict with check results
        """
        variance = self.calculate_variance(allocations)
        gini = self.calculate_gini(allocations)
        
        violations = []
        
        if variance > self.variance_threshold:
            violations.append({
                "type": "variance_exceeded",
                "value": float(variance),
                "threshold": float(self.variance_threshold),
            })
        
        if gini > self.gini_threshold:
            violations.append({
                "type": "gini_exceeded",
                "value": float(gini),
                "threshold": float(self.gini_threshold),
            })
        
        if violations:
            self.violations.extend(violations)
        
        return {
            "equitable": len(violations) == 0,
            "variance": float(variance),
            "gini": float(gini),
            "violations": violations,
        }
    
    def get_equity_violations(self) -> list:
        """Get all equity violations detected."""
        return self.violations
