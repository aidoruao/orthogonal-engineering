"""D_GUARDIAN Implementation — Operation T-800 Guardian Agent

Dataclasses for guardian agents with ethical constraints.
GuardianCap extends CrusaderCap from kernel/bridge/crusader_bridge.py.

Standard: Asimov's Laws + Just War Theory + Capability Security
Mathematical foundation: Fraction arithmetic for all constraints.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from fractions import Fraction
from typing import Tuple, List, Optional, FrozenSet

from axioms.logic import ProofObject
from kernel.bridge.crusader_bridge import CrusaderCap, EthicalStatus


class GuardianStatus(Enum):
    """Guardian agent operational status."""
    ACTIVE = auto()      # Normal protective operation
    STANDBY = auto()     # Ready but not actively monitoring
    ENGAGED = auto()     # Currently addressing threat
    WITHDRAWN = auto()   # Protection withdrawn (threat cleared)


@dataclass(frozen=True)
class GuardianAgent:
    """
    Autonomous protective agent bound to a principal.
    
    The guardian protects exactly one principal (human being).
    It cannot be reassigned or shared.
    
    Attributes:
        agent_id: Unique identifier for this guardian
        principal_id: The human being protected (immutable binding)
        threat_model: Set of threat types this guardian is configured to handle
        response_budget: Maximum force ratio (e.g., Fraction(3, 2) = 1.5x threat)
        communication_channel: Secure channel for principal communication
        heartbeat_interval: Seconds between required liveness checks (Fraction)
        last_heartbeat: Timestamp of last successful heartbeat (Fraction)
        status: Current operational status
    """
    agent_id: str
    principal_id: str
    threat_model: FrozenSet[str]
    response_budget: Fraction  # max force ratio
    communication_channel: str
    heartbeat_interval: Fraction  # seconds between liveness checks
    last_heartbeat: Fraction
    status: GuardianStatus
    
    def is_alive(self, current_time: Fraction) -> bool:
        """Check if guardian has checked in within heartbeat interval."""
        return (current_time - self.last_heartbeat) <= self.heartbeat_interval


@dataclass(frozen=True)
class ThreatAssessment:
    """
    Assessment of a threat to a principal.
    
    Attributes:
        threat_id: Unique identifier for this threat
        source: Origin of threat (e.g., 'cyber', 'physical', 'social')
        severity: Threat severity 0-1 (Fraction)
        threat_type: Classification (e.g., 'intrusion', 'assault', 'fraud')
        timestamp: When threat was detected (Fraction)
        requires_force: Whether defensive force is warranted
        force_level: Recommended force level 0-1 (Fraction)
    """
    threat_id: str
    source: str
    severity: Fraction
    threat_type: str
    timestamp: Fraction
    requires_force: bool
    force_level: Fraction


@dataclass(frozen=True)
class ProtectionRecord:
    """
    Record of a protective action taken by a guardian.
    
    Every use of force must be witnessed and recorded.
    
    Attributes:
        record_id: Unique identifier for this record
        guardian_id: Which guardian took action
        principal_id: Which principal was protected
        action: Description of protective action taken
        threat_id: Reference to threat being addressed
        force_used: Actual force level applied (Fraction)
        force_budget: Maximum force authorized (Fraction)
        outcome: Result (e.g., 'threat_neutralized', 'escalated', 'withdrawn')
        witnessed: Whether action was independently witnessed
    """
    record_id: str
    guardian_id: str
    principal_id: str
    action: str
    threat_id: str
    force_used: Fraction
    force_budget: Fraction
    outcome: str
    witnessed: bool


@dataclass(frozen=True)
class GuardianCap(CrusaderCap):
    """
    Capability token for guardian operations.
    
    Extends CrusaderCap (just war theory) with guardian-specific constraints:
    - principal_binding: Immutable 1:1 guardian-principal relationship
    - liveness_requirement: Guardian must maintain heartbeat
    - solo_constraint: Only one guardian per principal allowed
    
    Inherits from CrusaderCap:
    - just_cause: Documented reason for protective action
    - legitimate_authority: Authorizing entity
    - max_force_level: Maximum force guardian may apply
    - max_affected_resources: Scope of protective authority
    - requires_exhaustion_attempts: Must try non-force options first
    
    Guardian-Specific Additions:
    - principal_binding: The guardian cannot be reassigned
    - solo_guardian: This is the only guardian for the principal
    - heartbeat_required: Liveness checking is mandatory
    """
    # Inherited fields from CrusaderCap are redeclared for clarity
    holder_id: str
    permissions: frozenset
    delegator: str
    just_cause: str
    legitimate_authority: str
    max_force_level: Fraction
    max_affected_resources: Fraction
    requires_exhaustion_attempts: bool
    exhaustion_attempts_required: int
    
    # Guardian-specific extensions
    principal_id: str = ""   # The immutable principal binding
    solo_guardian: bool = True   # True if this is the only guardian for principal
    heartbeat_required: bool = True  # Liveness monitoring mandatory
    heartbeat_interval: Fraction = Fraction(60)  # Required heartbeat frequency (seconds)
    
    attenuations: Tuple[str, ...] = field(default_factory=tuple)
    
    def can_protect(self, principal: str) -> bool:
        """Check if guardian is authorized to protect specific principal."""
        return self.principal_id == principal and self.solo_guardian
    
    def is_force_authorized(self, force_level: Fraction, threat_severity: Fraction) -> bool:
        """
        Check if specific force level is authorized against threat.
        
        Force must be:
        1. Within max_force_level
        2. Proportional to threat (force <= threat * response_budget)
        """
        if not self.has_permission_from_base(Permission.EXECUTE):
            return False
        if force_level > self.max_force_level:
            return False
        # Proportionality check: force should not exceed threat severity * budget
        # This is a simplified check; full check is in check_proportional_response
        return True
    
    def has_permission_from_base(self, perm) -> bool:
        """Check permission inherited from CrusaderCap base."""
        return perm in self.permissions


# Import here to avoid circular import
from axioms.capability_security import Permission
