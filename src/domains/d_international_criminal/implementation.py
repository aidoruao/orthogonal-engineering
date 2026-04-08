"""D_INTERNATIONAL_CRIMINAL implementation."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict
from enum import Enum, auto
from datetime import datetime

class International_CriminStatus(Enum):
    COMPLIANT = auto()
    NON_COMPLIANT = auto()
    PENDING = auto()

@dataclass
class International_CriminRecord:
    record_id: str
    created_at: datetime = field(default_factory=datetime.now)
    status: International_CriminStatus = International_CriminStatus.PENDING

class International_CriminChecker:
    def check_compliance(self, record: International_CriminRecord) -> Dict:
        return {"record_id": record.record_id, "compliant": record.status == International_CriminStatus.COMPLIANT}
