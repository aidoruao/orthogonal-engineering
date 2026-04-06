"""Pattern: Bounded Power

Implements INV-YS-009: The system is constrained against unbounded
maximization. No constraint in C can authorize unlimited resource
or power extraction.

Biblical: 1 Samuel 8 — Samuel warns Israel that a king will take
their sons, daughters, fields, vineyards, olive groves. Power,
unchecked, extracts without limit.

Used by: D_SEPARATION_OF_POWERS, D_ANTITRUST, D_CORPORATE_LAW,
D_BANKING_REGULATION, D_USE_OF_FORCE
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from fractions import Fraction


@dataclass
class PowerGrant:
    """A grant of power or authority."""
    grant_id: str
    authority: str
    scope: str
    upper_bound: Optional[Fraction]  # None means unbounded (prohibited)
    duration_limit: Optional[int]    # None means unlimited (prohibited)
    
    def is_bounded(self) -> bool:
        """Check if this grant has explicit bounds."""
        return self.upper_bound is not None and self.duration_limit is not None


class BoundedPower:
    """
    Enforces that all power grants have explicit bounds.
    
    No authorization can be unlimited in scope or duration.
    All powers must have sunset clauses and scope limits.
    
    Attributes:
        grants: Tracked power grants
    """
    
    def __init__(self):
        self.grants: Dict[str, PowerGrant] = {}
        self.violations: list = []
    
    def register_grant(self, grant: PowerGrant) -> bool:
        """
        Register a power grant.
        
        Returns:
            True if grant is valid (bounded), False if unbounded
        """
        if not grant.is_bounded():
            self.violations.append({
                "grant": grant.grant_id,
                "violation": "Unbounded power grant",
                "authority": grant.authority,
            })
            return False
        
        self.grants[grant.grant_id] = grant
        return True
    
    def check_exercise(
        self,
        grant_id: str,
        amount: Fraction,
        duration: int,
    ) -> Dict[str, Any]:
        """
        Check if a power exercise is within bounds.
        
        Args:
            grant_id: The power grant being exercised
            amount: Amount of power being exercised
            duration: Duration of exercise
        
        Returns:
            Dict with 'within_bounds' and details
        """
        grant = self.grants.get(grant_id)
        if grant is None:
            return {
                "within_bounds": False,
                "reason": f"Grant {grant_id} not registered",
            }
        
        violations = []
        
        if grant.upper_bound and amount > grant.upper_bound:
            violations.append(
                f"Amount {amount} exceeds upper bound {grant.upper_bound}"
            )
        
        if grant.duration_limit and duration > grant.duration_limit:
            violations.append(
                f"Duration {duration} exceeds limit {grant.duration_limit}"
            )
        
        return {
            "within_bounds": len(violations) == 0,
            "violations": violations,
            "grant": grant,
        }
    
    def get_unbounded_grants(self) -> list:
        """Get list of unbounded grant violations."""
        return self.violations
