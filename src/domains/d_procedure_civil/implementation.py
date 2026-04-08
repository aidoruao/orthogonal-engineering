"""D_PROCEDURE_CIVIL implementation."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict
from enum import Enum, auto
from datetime import datetime

class Procedure_CivilStatus(Enum):
    COMPLIANT = auto()
    NON_COMPLIANT = auto()
    PENDING = auto()

@dataclass
class Procedure_CivilRecord:
    record_id: str
    created_at: datetime = field(default_factory=datetime.now)
    status: Procedure_CivilStatus = Procedure_CivilStatus.PENDING

class Procedure_CivilChecker:
    def check_compliance(self, record: Procedure_CivilRecord) -> Dict:
        return {"record_id": record.record_id, "compliant": record.status == Procedure_CivilStatus.COMPLIANT}
