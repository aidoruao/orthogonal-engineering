"""Pattern: Anti-Nominalism

Implements INV-YS-007: No empty labels. Every name must resolve to a
concrete structure in C. Anti-nominalism: names must have hashed referents.

Biblical: Exodus 3:14 — "I AM WHO I AM." The divine name is not empty;
it refers to the one who is. Names mean something.

Used by: D_CONTRACT_LAW, D_ADMINISTRATIVE_LAW, D_CURRICULUM,
D_LICENSING, D_DIGITAL_GOVERNANCE
"""

from dataclasses import dataclass
from typing import Dict, Any, Set, Optional
import hashlib


@dataclass
class NamedEntity:
    """A named entity with concrete referent."""
    name: str
    referent_type: str
    referent_data: bytes
    hash_value: str = ""
    
    def __post_init__(self):
        """Compute hash of referent."""
        if not self.hash_value:
            self.hash_value = hashlib.sha256(
                self.referent_data + self.name.encode()
            ).hexdigest()
    
    def has_referent(self) -> bool:
        """Check if entity has non-empty referent."""
        # TODO: Expand has_referent() - stub detected by Yeshua Agent
        return len(self.referent_data) > 0


class AntiNominalism:
    """
    Enforces that every name has a concrete referent.
    
    No label without hashed referent. All terms used must resolve
to concrete structures.
    
    Attributes:
        registry: Dictionary of named entities
    """
    
    def __init__(self):
        self.registry: Dict[str, NamedEntity] = {}
        self.violations: list = []
    
    def register_entity(
        self,
        name: str,
        referent_type: str,
        referent_data: bytes,
    ) -> Optional[NamedEntity]:
        """
        Register a named entity.
        
        Returns:
            NamedEntity if successful, None if referent is empty
        """
        if not referent_data:
            self.violations.append({
                "name": name,
                "violation": "Empty referent",
            })
            return None
        
        entity = NamedEntity(
            name=name,
            referent_type=referent_type,
            referent_data=referent_data,
        )
        self.registry[name] = entity
        return entity
    
    def resolve_name(self, name: str) -> Optional[NamedEntity]:
        """
        Resolve a name to its concrete referent.
        
        Returns:
            NamedEntity if found, None otherwise
        """
        return self.registry.get(name)
    
    def check_name_usage(self, name: str) -> Dict[str, Any]:
        """
        Check if a name is properly registered.
        
        Returns:
            Dict with check results
        """
        entity = self.registry.get(name)
        
        if entity is None:
            return {
                "valid": False,
                "reason": "Name not registered",
                "name": name,
            }
        
        if not entity.has_referent():
            return {
                "valid": False,
                "reason": "Empty referent",
                "name": name,
            }
        
        return {
            "valid": True,
            "name": name,
            "referent_type": entity.referent_type,
            "hash": entity.hash_value,
        }
    
    def get_unresolved_names(self) -> list:
        """Get list of names with violations."""
        # TODO: Expand get_unresolved_names() - stub detected by Yeshua Agent
        return self.violations
