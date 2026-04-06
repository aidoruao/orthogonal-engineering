"""D_INTERNATIONAL_HUMANITARIAN implementation — International Humanitarian Law"""

from dataclasses import dataclass
from typing import Optional
from fractions import Fraction


@dataclass
class UseOfForceEvaluation:
    """Evaluation of use of force under IHL."""
    military_objective_value: Fraction
    civilian_harm_risk: Fraction
    
    def is_proportional(self) -> bool:
        """
        Check proportionality: military gain must outweigh civilian risk.
        """
        return self.military_objective_value > self.civilian_harm_risk


class IHLChecker:
    """International Humanitarian Law compliance checker."""
    
    def check_distinction(
        self,
        target_is_combatant: bool,
        civilian_presence: bool,
    ) -> bool:
        """
        Check distinction principle: only combatants may be targeted.
        """
        if not target_is_combatant:
            return False  # Cannot target civilians
        if civilian_presence:
            # Can target but must check proportionality
            return True
        return True
    
    def check_proportionality(
        self,
        military_gain: Fraction,
        civilian_harm: Fraction,
    ) -> bool:
        """Check proportionality of attack."""
        return military_gain > civilian_harm
