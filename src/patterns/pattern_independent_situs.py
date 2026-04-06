"""Pattern: Independent Situs

Implements the requirement that review/audit is always by a different
situs (perspective) than the actor.

Mathematical: geometric_morphism(actor_situs, reviewer_situs) must exist
and actor_situs ≠ reviewer_situs.

Used by: D_JUDICIAL_REVIEW, D_POLICE_PROCEDURE, D_ADMINISTRATIVE_LAW, D_ETHICS
"""

from dataclasses import dataclass, field
from typing import Set, List, Dict, Any
from src.sal.topos_subobject_classifier import SheafContext, geometric_morphism


@dataclass
class Situs:
    """A perspective/site in the topos."""
    situs_id: str
    name: str
    context: SheafContext
    can_review: Set[str] = field(default_factory=set)  # IDs of situs this can review
    cannot_review: Set[str] = field(default_factory=set)  # IDs of situs this cannot review (self)
    
    def can_review_situs(self, other_situs_id: str) -> bool:
        """Check if this situs can review another."""
        # Cannot review self
        if other_situs_id == self.situs_id:
            return False
        # Must be in can_review list
        return other_situs_id in self.can_review


class IndependentSitus:
    """
    Enforces that review is always by an independent situs.
    
    No actor can review their own actions. Review requires a
different perspective.
    
    Attributes:
        situs_registry: All registered situs
    """
    
    def __init__(self):
        self.situs_registry: Dict[str, Situs] = {}
    
    def register_situs(self, situs: Situs) -> None:
        """Register a situs."""
        self.situs_registry[situs.situs_id] = situs
        # By default, situs cannot review itself
        situs.cannot_review.add(situs.situs_id)
    
    def establish_review_relationship(
        self,
        reviewer_id: str,
        actor_id: str,
    ) -> Dict[str, Any]:
        """
        Establish a review relationship.
        
        Args:
            reviewer_id: The situs doing the review
            actor_id: The situs being reviewed
        
        Returns:
            Dict with establishment results
        """
        reviewer = self.situs_registry.get(reviewer_id)
        actor = self.situs_registry.get(actor_id)
        
        if reviewer is None:
            return {"established": False, "reason": f"Reviewer {reviewer_id} not found"}
        
        if actor is None:
            return {"established": False, "reason": f"Actor {actor_id} not found"}
        
        # Check independence
        if reviewer_id == actor_id:
            return {
                "established": False,
                "reason": "Cannot establish self-review",
                "violation": "Independence requirement",
            }
        
        # Check if reviewer is authorized to review this situs type
        if not reviewer.can_review_situs(actor_id):
            return {
                "established": False,
                "reason": f"{reviewer_id} not authorized to review {actor_id}",
            }
        
        # Try to construct geometric morphism
        try:
            morphism = geometric_morphism(
                source=actor.context,
                target=reviewer.context,
            )
            
            return {
                "established": True,
                "reviewer": reviewer_id,
                "actor": actor_id,
                "truth_preserved": morphism.truth_preserved,
                "violations": morphism.violations,
            }
        except Exception as e:
            return {
                "established": False,
                "reason": f"Failed to construct morphism: {e}",
            }
    
    def verify_independence(self, reviewer_id: str, actor_id: str) -> bool:
        """Verify that a review relationship maintains independence."""
        return reviewer_id != actor_id
    
    def get_reviewers_for(self, actor_id: str) -> List[Situs]:
        """Get all situs that can review the given actor."""
        return [
            s for s in self.situs_registry.values()
            if s.can_review_situs(actor_id)
        ]
