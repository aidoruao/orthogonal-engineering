"""D_DIPLOMATIC implementation — Diplomatic Law"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Diplomat:
    """A diplomat with immunity."""
    name: str
    country: str
    rank: str
    immunity_scope: List[str] = field(default_factory=list)
    
    def has_immunity(self, action: str) -> bool:
        """Check if diplomat has immunity for action."""
        return action in self.immunity_scope


@dataclass
class PersonaNonGrata:
    """Persona non grata declaration."""
    diplomat_name: str
    declaring_country: str
    declaration_date: datetime
    reason: str
    departure_deadline: datetime
    
    def is_valid(self) -> bool:
        """Check if PNG was properly declared."""
        return len(self.reason) > 0 and self.departure_deadline > self.declaration_date


class DiplomaticLaw:
    """Vienna Convention on Diplomatic Relations implementation."""
    
    def __init__(self):
        self.diplomats: List[Diplomat] = []
        self.png_declarations: List[PersonaNonGrata] = []
    
    def register_diplomat(self, diplomat: Diplomat) -> None:
        """Register a diplomat."""
        self.diplomats.append(diplomat)
    
    def declare_persona_non_grata(
        self,
        diplomat_name: str,
        declaring_country: str,
        reason: str,
        departure_days: int = 30,
    ) -> PersonaNonGrata:
        """Declare a diplomat persona non grata."""
        now = datetime.now()
        png = PersonaNonGrata(
            diplomat_name=diplomat_name,
            declaring_country=declaring_country,
            declaration_date=now,
            reason=reason,
            departure_deadline=now + datetime.timedelta(days=departure_days),
        )
        self.png_declarations.append(png)
        return png
    
    def check_immunity_scope(self, diplomat_name: str, action: str) -> bool:
        """Check if action is within diplomat's immunity scope."""
        diplomat = next((d for d in self.diplomats if d.name == diplomat_name), None)
        if diplomat is None:
            return False
        return diplomat.has_immunity(action)
