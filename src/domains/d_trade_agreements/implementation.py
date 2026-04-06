"""D_TRADE_AGREEMENTS implementation — Trade & Commerce Agreements"""

from dataclasses import dataclass
from typing import Dict, List
from fractions import Fraction


@dataclass
class TariffSchedule:
    """Deterministic tariff schedule."""
    product_code: str
    mfn_rate: Fraction  # Most-Favored-Nation rate
    preferential_rate: Fraction
    
    def calculate_tariff(self, value: Fraction, preferential: bool = False) -> Fraction:
        """Calculate tariff deterministically."""
        rate = self.preferential_rate if preferential else self.mfn_rate
        return value * rate


class TradeAgreement:
    """Trade agreement with MFN clause enforcement."""
    
    def __init__(self, agreement_name: str):
        self.agreement_name = agreement_name
        self.tariff_schedules: Dict[str, TariffSchedule] = {}
        self.parties: List[str] = []
    
    def add_tariff_schedule(self, schedule: TariffSchedule) -> None:
        """Add tariff schedule."""
        self.tariff_schedules[schedule.product_code] = schedule
    
    def apply_mfn_clause(self, product_code: str, new_rate: Fraction) -> None:
        """
        Apply MFN clause: if one party gets better rate, all parties get it.
        """
        if product_code in self.tariff_schedules:
            schedule = self.tariff_schedules[product_code]
            # MFN: apply lowest rate to all
            if new_rate < schedule.mfn_rate:
                schedule.mfn_rate = new_rate
