"""D_INSURANCE implementation."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict
from enum import Enum, auto
from datetime import datetime

class InsuranceStatus(Enum):
    COMPLIANT = auto()
    NON_COMPLIANT = auto()
    PENDING = auto()

@dataclass
class InsuranceRecord:
    record_id: str
    created_at: datetime = field(default_factory=datetime.now)
    status: InsuranceStatus = InsuranceStatus.PENDING

class InsuranceChecker:
    def check_compliance(self, record: InsuranceRecord) -> Dict:
        return {"record_id": record.record_id, "compliant": record.status == InsuranceStatus.COMPLIANT}
