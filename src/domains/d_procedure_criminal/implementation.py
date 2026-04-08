"""D_PROCEDURE_CRIMINAL implementation."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict
from enum import Enum, auto
from datetime import datetime

class Procedure_CriminalStatus(Enum):
    COMPLIANT = auto()
    NON_COMPLIANT = auto()
    PENDING = auto()

@dataclass
class Procedure_CriminalRecord:
    record_id: str
    created_at: datetime = field(default_factory=datetime.now)
    status: Procedure_CriminalStatus = Procedure_CriminalStatus.PENDING

class Procedure_CriminalChecker:
    def check_compliance(self, record: Procedure_CriminalRecord) -> Dict:
        return {"record_id": record.record_id, "compliant": record.status == Procedure_CriminalStatus.COMPLIANT}
