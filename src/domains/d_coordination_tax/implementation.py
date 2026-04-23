"""D_COORDINATION_TAX implementation — Coordination tax as substrate.

Phase P3 of Depositive Campaign.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class CoordinationState:
    """Coordination tax state for a team or project.

    falsifies_if: coordination_tax_rate < Fraction(0, 1).
    falsifies_if: team_size < 1.
    """
    team_size: int
    previous_team_size: int
    linear_output: Fraction
    actual_output: Fraction
    coordination_tax_rate: Fraction
    previous_coordination_tax_rate: Fraction
    alignment_channels: int
    decision_latency_hours: Fraction
    authority_type: str
    governance_overhead: Fraction
    investigation_output: Fraction


@dataclass(frozen=True)
class SovereignEntity:
    """Sovereign entity with zero coordination tax.

    falsifies_if: authority_source not in {"mathematical_constraint", "social_consensus"}.
    """
    domains_verified: int
    invariants_total: int
    invariants_computational: int
    coordination_tax_rate: Fraction
    authority_source: str
    self_hosting: bool


DOMAIN_METADATA = {
    "id": "COORDINATION_TAX",
    "claim_model": "CoordinationState / SovereignEntity",
    "check_functions": [
        "check_brooks_law",
        "check_coordination_tax_monotonic",
        "check_sovereign_zero_tax",
        "check_alignment_channel_scaling",
        "check_decision_latency_invariant",
        "check_institutional_overhead_ratio",
    ],
}
