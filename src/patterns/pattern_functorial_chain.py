"""Pattern: Functorial Chain

Implements the requirement that multi-step legal processes preserve
structure end-to-end. If any link breaks, the chain fails — no skipping steps.

Mathematical: A functor F: C → D preserves structure. For a chain
A → B → C → D, each arrow must be a valid morphism.

Used by: D_CRIMINAL_LAW, D_CIVIL_LAW, D_IMMIGRATION, D_BANKRUPTCY
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Callable, Optional
from enum import Enum, auto


class ChainLinkStatus(Enum):
    """Status of a chain link."""
    PENDING = auto()
    VALID = auto()
    INVALID = auto()
    SKIPPED = auto()  # This is a violation


@dataclass
class ChainLink:
    """A single link in a functorial chain."""
    link_id: str
    from_state: str
    to_state: str
    validator: Callable[[Any], bool]
    status: ChainLinkStatus = ChainLinkStatus.PENDING
    validation_data: Any = None
    
    def validate(self, data: Any) -> bool:
        """Validate this link."""
        self.validation_data = data
        try:
            result = self.validator(data)
            self.status = ChainLinkStatus.VALID if result else ChainLinkStatus.INVALID
            return result
        except Exception:
            self.status = ChainLinkStatus.INVALID
            return False


class FunctorialChain:
    """
    Implements a functorial chain where each link must be valid.
    
    For processes like: Evidence → Charge → Trial → Verdict
    Each step must be valid or the entire chain fails.
    
    Attributes:
        links: Ordered list of chain links
    """
    
    def __init__(self, process_name: str):
        self.process_name = process_name
        self.links: List[ChainLink] = []
    
    def add_link(
        self,
        link_id: str,
        from_state: str,
        to_state: str,
        validator: Callable[[Any], bool],
    ) -> ChainLink:
        """Add a link to the chain."""
        link = ChainLink(
            link_id=link_id,
            from_state=from_state,
            to_state=to_state,
            validator=validator,
        )
        self.links.append(link)
        return link
    
    def validate_chain(self, data_per_link: List[Any]) -> Dict[str, Any]:
        """
        Validate the entire chain.
        
        Args:
            data_per_link: Validation data for each link in order
        
        Returns:
            Dict with validation results
        """
        if len(data_per_link) != len(self.links):
            return {
                "valid": False,
                "reason": f"Expected {len(self.links)} data items, got {len(data_per_link)}",
            }
        
        failed_links = []
        
        for i, (link, data) in enumerate(zip(self.links, data_per_link)):
            if not link.validate(data):
                failed_links.append({
                    "index": i,
                    "link_id": link.link_id,
                    "from": link.from_state,
                    "to": link.to_state,
                })
                # Chain fails at first broken link
                break
        
        return {
            "valid": len(failed_links) == 0,
            "process": self.process_name,
            "links_validated": len(self.links) - len(failed_links),
            "total_links": len(self.links),
            "failed_links": failed_links,
        }
    
    def is_complete(self) -> bool:
        """Check if all links are valid."""
        return all(link.status == ChainLinkStatus.VALID for link in self.links)
    
    def get_progress(self) -> Dict[str, Any]:
        """Get progress through the chain."""
        valid_count = sum(1 for link in self.links if link.status == ChainLinkStatus.VALID)
        return {
            "total": len(self.links),
            "completed": valid_count,
            "remaining": len(self.links) - valid_count,
            "percentage": (valid_count / len(self.links) * 100) if self.links else 0,
        }
