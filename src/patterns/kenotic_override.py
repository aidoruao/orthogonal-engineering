"""Kenotic Override Pattern

Biblical basis: Philippians 2:6-7 — Christ "emptied himself" (Greek: kenosis),
taking the form of a servant. Love > Rule when the rule would condemn.

Application: When a strict interpretation of an invariant would cause harm
to a vulnerable party, the system should prioritize mercy over rigid rule-
following. INV-YS-004 (Mercy Weighting).
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Dict, Any


class OverrideDecision(Enum):
    """Decision on whether to apply kenotic override."""
    APPLY_OVERRIDE = auto()      # Rule would cause harm — override
    UPHOLD_RULE = auto()         # Rule should stand
    ESCALATE = auto()            # Cannot determine — escalate to human


@dataclass
class VulnerableParty:
    """Represents a potentially vulnerable party in a decision."""
    party_id: str
    vulnerability_factors: list  # e.g., ["elderly", "disabled", "low-income"]
    harm_risk: str  # "low", "medium", "high", "critical"


class KenoticOverride:
    """
    Implements kenosis (self-emptying) override for mercy.
    
    When a strict rule application would harm a vulnerable party,
    the system should consider overriding the rule in favor of mercy.
    
    This is NOT rule-breaking — it's rule-reinterpretation under
    the higher constraint of INV-YS-004 (Mercy Weighting).
    
    Attributes:
        mercy_threshold: Minimum harm risk to trigger override consideration
    """
    
    def __init__(self, mercy_threshold: str = "medium"):
        self.mercy_threshold = mercy_threshold
        self.override_history = []
    
    def evaluate_override(
        self,
        rule: str,
        rule_strict_application: Dict[str, Any],
        vulnerable_party: Optional[VulnerableParty],
        alternative_actions: list,
    ) -> OverrideDecision:
        """
        Evaluate whether to apply kenotic override.
        
        Args:
            rule: The rule being evaluated
            rule_strict_application: What strict application would require
            vulnerable_party: Party potentially harmed by strict application
            alternative_actions: Less harmful alternatives
        
        Returns:
            OverrideDecision on how to proceed
        """
        if vulnerable_party is None:
            # No vulnerable party — rule stands
            return OverrideDecision.UPHOLD_RULE
        
        # Check if harm risk meets threshold
        risk_levels = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        party_risk = risk_levels.get(vulnerable_party.harm_risk, 0)
        threshold_risk = risk_levels.get(self.mercy_threshold, 2)
        
        if party_risk < threshold_risk:
            # Risk below threshold — rule stands
            return OverrideDecision.UPHOLD_RULE
        
        if not alternative_actions:
            # No alternatives — cannot safely override
            return OverrideDecision.ESCALATE
        
        # Alternative exists and harm is significant — apply override
        self.override_history.append({
            "rule": rule,
            "party": vulnerable_party.party_id,
            "alternative": alternative_actions[0],
        })
        
        return OverrideDecision.APPLY_OVERRIDE
    
    def get_override_summary(self) -> Dict[str, int]:
        """Get summary of overrides applied."""
        return {
            "total_overrides": len(self.override_history),
            "by_party": len(set(o["party"] for o in self.override_history)),
        }
