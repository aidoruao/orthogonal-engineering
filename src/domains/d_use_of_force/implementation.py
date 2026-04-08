"""D_USE_OF_FORCE implementation."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict
from enum import Enum, auto
from datetime import datetime

class Use_Of_ForceStatus(Enum):
    COMPLIANT = auto()
    NON_COMPLIANT = auto()
    PENDING = auto()

@dataclass
class Use_Of_ForceRecord:
    record_id: str
    created_at: datetime = field(default_factory=datetime.now)
    status: Use_Of_ForceStatus = Use_Of_ForceStatus.PENDING

class Use_Of_ForceChecker:
    def check_compliance(self, record: Use_Of_ForceRecord) -> Dict:
        return {"record_id": record.record_id, "compliant": record.status == Use_Of_ForceStatus.COMPLIANT}
