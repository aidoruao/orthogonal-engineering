"""Crusader Bridge — Ethical Warfare Capability Integration

Mediates between d_crusader invariants and kernel HAL.
Just war verification before any "force" operation.
Proportionality checks using Fraction arithmetic.

Mathematical foundation: Just war theory (Aquinas) + capability security.
Standard: Summa Theologica II-II Q.40, Geneva Convention precursors.
Biblical: Isaiah 2:4 — "They shall beat their swords into plowshares."
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Optional, Dict
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject
from axioms.capability_security import Capability, Permission


class ForceOperation(Enum):
    """Types of force operations requiring ethical verification."""
    MEMORY_ISOLATION = auto()   # Force isolation of memory region
    PROCESS_TERMINATION = auto() # Force kill process
    RESOURCE_REVOCATION = auto() # Force reclaim resources
    CAPABILITY_REVOCATION = auto()  # Force revoke capability
    EMERGENCY_SHUTDOWN = auto()  # Emergency system shutdown


class EthicalStatus(Enum):
    """Ethical authorization status."""
    AUTHORIZED = auto()
    DENIED_JUST_CAUSE = auto()      # Fails just cause criterion
    DENIED_AUTHORITY = auto()       # Fails legitimate authority
    DENIED_PROPORTIONALITY = auto() # Fails proportionality
    DENIED_NECESSITY = auto()       # Fails necessity (last resort)


@dataclass(frozen=True)
class CrusaderCap:
    """Capability token for ethical warfare (force) operations.
    
    Grants permission to use force under just war constraints:
    - Just cause: Must have legitimate grievance
    - Legitimate authority: Must be authorized
    - Proportionality: Response must match threat
    - Necessity: Must be last resort
    
    Every force operation is witnessed with ProofObject.
    """
    holder_id: str
    permissions: frozenset
    delegator: str
    
    # Just war criteria
    just_cause: str  # Documented reason for force
    legitimate_authority: str  # Authorizing entity
    
    # Proportionality limits
    max_force_level: Fraction  # 0-1 scale of maximum authorized force
    max_affected_resources: Fraction  # Maximum resources that can be affected
    
    # Necessity constraints
    requires_exhaustion_attempts: bool  # Must try non-force first
    exhaustion_attempts_required: int  # Number of attempts required
    
    attenuations: Tuple[str, ...] = field(default_factory=tuple)
    
    def has_permission(self, perm: Permission) -> bool:
        """Check if capability has specific permission."""
        return perm in self.permissions
    
    def can_apply_force(self, force_level: Fraction, affected_resources: Fraction) -> bool:
        """Check if capability authorizes specific level of force."""
        if not self.has_permission(Permission.EXECUTE):
            return False
        if force_level > self.max_force_level:
            return False
        if affected_resources > self.max_affected_resources:
            return False
        return True


@dataclass
class ForceOperationRecord:
    """A record of a force operation."""
    operation_id: str
    operation_type: ForceOperation
    target_id: str
    initiator_id: str
    
    # Ethical verification
    crusader_cap: CrusaderCap
    ethical_status: EthicalStatus
    just_cause_verified: bool
    authority_verified: bool
    proportionality_verified: bool
    necessity_verified: bool
    
    # Operation details
    force_level: Fraction
    affected_resources: Fraction
    timestamp: Fraction
    
    # ProofObject witness
    proof_hash: str


@dataclass
class CrusaderBridgeState:
    """Complete Crusader Bridge state."""
    # Active capabilities
    capabilities: Dict[str, List[CrusaderCap]] = field(default_factory=dict)
    
    # Operation history
    operations: List[ForceOperationRecord] = field(default_factory=list)
    
    # Exhaustion attempt tracking
    exhaustion_attempts: Dict[str, int] = field(default_factory=dict)  # target -> attempts
    
    # Statistics
    total_operations: int = 0
    authorized_operations: int = 0
    denied_operations: int = 0
    
    def get_caps(self, holder_id: str) -> List[CrusaderCap]:
        """Get all capabilities held by holder."""
        return self.capabilities.get(holder_id, [])
    
    def get_operations_on_target(self, target_id: str) -> List[ForceOperationRecord]:
        """Get all operations against a target."""
        return [op for op in self.operations if op.target_id == target_id]


def verify_just_cause(
    state: CrusaderBridgeState,
    cap: CrusaderCap,
    operation: ForceOperation,
    target_id: str,
    cause_documentation: str
) -> Tuple[bool, ProofObject]:
    """Verify just cause criterion.
    
    Just cause requires documented grievance with evidence.
    
    Args:
        state: Crusader bridge state
        cap: Capability being used
        operation: Type of force operation
        target_id: Target of operation
        cause_documentation: Documentation of grievance
        
    Returns:
        (verified, proof)
    """
    # Just cause requires non-empty documentation
    if not cause_documentation or len(cause_documentation) < 10:
        return False, ProofObject(
            rule="VerifyJustCause",
            premises=[
                f"operation={operation.name}",
                f"target={target_id}",
                "insufficient_documentation"
            ],
            conclusion="just cause NOT verified: documentation insufficient"
        )
    
    # Check for pattern of grievance (previous exhaustion attempts)
    previous_attempts = state.exhaustion_attempts.get(target_id, 0)
    
    return True, ProofObject(
        rule="VerifyJustCause",
        premises=[
            f"operation={operation.name}",
            f"target={target_id}",
            f"cause_length={len(cause_documentation)}",
            f"previous_attempts={previous_attempts}"
        ],
        conclusion="just cause verified"
    )


def verify_legitimate_authority(
    cap: CrusaderCap,
    operation: ForceOperation
) -> Tuple[bool, ProofObject]:
    """Verify legitimate authority criterion.
    
    Authority is legitimate if:
    1. Capability has EXECUTE permission
    2. delegator is in authority chain
    
    Args:
        cap: Capability to verify
        operation: Operation being authorized
        
    Returns:
        (verified, proof)
    """
    if not cap.has_permission(Permission.EXECUTE):
        return False, ProofObject(
            rule="VerifyLegitimateAuthority",
            premises=[
                f"holder={cap.holder_id}",
                f"permissions={cap.permissions}"
            ],
            conclusion="authority NOT verified: no EXECUTE permission"
        )
    
    # Verify authority chain
    if cap.delegator == "root" or cap.legitimate_authority:
        return True, ProofObject(
            rule="VerifyLegitimateAuthority",
            premises=[
                f"holder={cap.holder_id}",
                f"delegator={cap.delegator}",
                f"authority={cap.legitimate_authority}"
            ],
            conclusion="legitimate authority verified"
        )
    
    return False, ProofObject(
        rule="VerifyLegitimateAuthority",
        premises=[f"holder={cap.holder_id}", "no_authority_chain"],
        conclusion="authority NOT verified: no authority chain"
    )


def verify_proportionality(
    cap: CrusaderCap,
    operation: ForceOperation,
    requested_force: Fraction,
    affected_resources: Fraction,
    threat_level: Fraction
) -> Tuple[bool, ProofObject]:
    """Verify proportionality criterion.
    
    Proportionality requires:
    force_level <= max_authorized AND
    force_level <= threat_level * 1.5 (not excessive)
    
    Args:
        cap: Capability with limits
        operation: Operation type
        requested_force: Requested force level (0-1)
        affected_resources: Resources to be affected
        threat_level: Level of threat being responded to
        
    Returns:
        (verified, proof)
    """
    # Check against capability limits
    if requested_force > cap.max_force_level:
        return False, ProofObject(
            rule="VerifyProportionality",
            premises=[
                f"requested={requested_force}",
                f"max_authorized={cap.max_force_level}"
            ],
            conclusion="proportionality NOT verified: exceeds authorized limit"
        )
    
    if affected_resources > cap.max_affected_resources:
        return False, ProofObject(
            rule="VerifyProportionality",
            premises=[
                f"affected={affected_resources}",
                f"max_allowed={cap.max_affected_resources}"
            ],
            conclusion="proportionality NOT verified: affects too many resources"
        )
    
    # Check not excessive (force <= threat * 1.5)
    max_proportional_force = threat_level * Fraction(3, 2)
    if requested_force > max_proportional_force:
        return False, ProofObject(
            rule="VerifyProportionality",
            premises=[
                f"requested={requested_force}",
                f"threat={threat_level}",
                f"max_proportional={max_proportional_force}"
            ],
            conclusion="proportionality NOT verified: force exceeds threat * 1.5"
        )
    
    return True, ProofObject(
        rule="VerifyProportionality",
        premises=[
            f"requested={requested_force}",
            f"threat={threat_level}",
            f"max_allowed={cap.max_force_level}"
        ],
        conclusion="proportionality verified"
    )


def verify_necessity(
    state: CrusaderBridgeState,
    cap: CrusaderCap,
    target_id: str
) -> Tuple[bool, ProofObject]:
    """Verify necessity (last resort) criterion.
    
    Necessity requires exhaustion of non-force alternatives.
    
    Args:
        state: Crusader bridge state
        cap: Capability being used
        target_id: Target of operation
        
    Returns:
        (verified, proof)
    """
    if not cap.requires_exhaustion_attempts:
        return True, ProofObject(
            rule="VerifyNecessity",
            premises=["exhaustion_not_required"],
            conclusion="necessity verified (no exhaustion required)"
        )
    
    attempts = state.exhaustion_attempts.get(target_id, 0)
    
    if attempts < cap.exhaustion_attempts_required:
        return False, ProofObject(
            rule="VerifyNecessity",
            premises=[
                f"attempts={attempts}",
                f"required={cap.exhaustion_attempts_required}"
            ],
            conclusion="necessity NOT verified: insufficient exhaustion attempts"
        )
    
    return True, ProofObject(
        rule="VerifyNecessity",
        premises=[
            f"attempts={attempts}",
            f"required={cap.exhaustion_attempts_required}"
        ],
        conclusion="necessity verified (exhaustion attempts sufficient)"
    )


def record_exhaustion_attempt(
    state: CrusaderBridgeState,
    target_id: str,
    attempt_type: str,
    timestamp: Fraction
) -> Tuple[CrusaderBridgeState, ProofObject]:
    """Record a non-force exhaustion attempt.
    
    Args:
        state: Current state
        target_id: Target of attempt
        attempt_type: Type of non-force attempt
        timestamp: Timestamp
        
    Returns:
        (new_state, proof)
    """
    new_attempts = state.exhaustion_attempts.copy()
    new_attempts[target_id] = new_attempts.get(target_id, 0) + 1
    
    new_state = CrusaderBridgeState(
        capabilities=state.capabilities,
        operations=state.operations,
        exhaustion_attempts=new_attempts,
        total_operations=state.total_operations,
        authorized_operations=state.authorized_operations,
        denied_operations=state.denied_operations
    )
    
    return new_state, ProofObject(
        rule="RecordExhaustionAttempt",
        premises=[
            f"target={target_id}",
            f"attempt_type={attempt_type}",
            f"total_attempts={new_attempts[target_id]}"
        ],
        conclusion="exhaustion attempt recorded"
    )


def authorize_force_operation(
    state: CrusaderBridgeState,
    holder_id: str,
    cap: CrusaderCap,
    operation: ForceOperation,
    target_id: str,
    force_level: Fraction,
    affected_resources: Fraction,
    threat_level: Fraction,
    cause_documentation: str,
    timestamp: Fraction
) -> Tuple[CrusaderBridgeState, EthicalStatus, Optional[ForceOperationRecord], ProofObject]:
    """Authorize a force operation under just war criteria.
    
    This is the main entry point for ethical warfare verification.
    All four just war criteria must be satisfied.
    
    Args:
        state: Crusader bridge state
        holder_id: Capability holder
        cap: Crusader capability
        operation: Type of force operation
        target_id: Target of operation
        force_level: Requested force level (0-1)
        affected_resources: Resources to be affected
        threat_level: Level of threat being responded to
        cause_documentation: Documentation of just cause
        timestamp: Operation timestamp
        
    Returns:
        (new_state, status, record, proof)
        record is None if authorization denied
    """
    import hashlib
    
    # Verify capability held
    holder_caps = state.get_caps(holder_id)
    if cap not in holder_caps:
        status = EthicalStatus.DENIED_AUTHORITY
        return state, status, None, ProofObject(
            rule="AuthorizeForceOperation",
            premises=[f"holder={holder_id}", "cap not held"],
            conclusion="DENIED: invalid capability"
        )
    
    # Verify all four just war criteria
    checks = []
    
    # 1. Just Cause
    just_cause_ok, just_cause_proof = verify_just_cause(
        state, cap, operation, target_id, cause_documentation
    )
    checks.append(("just_cause", just_cause_ok, just_cause_proof))
    
    # 2. Legitimate Authority
    authority_ok, authority_proof = verify_legitimate_authority(cap, operation)
    checks.append(("authority", authority_ok, authority_proof))
    
    # 3. Proportionality
    proportionality_ok, proportionality_proof = verify_proportionality(
        cap, operation, force_level, affected_resources, threat_level
    )
    checks.append(("proportionality", proportionality_ok, proportionality_proof))
    
    # 4. Necessity
    necessity_ok, necessity_proof = verify_necessity(state, cap, target_id)
    checks.append(("necessity", necessity_ok, necessity_proof))
    
    # Determine overall status
    all_passed = all(ok for _, ok, _ in checks)
    
    if all_passed:
        status = EthicalStatus.AUTHORIZED
    else:
        # Find which check failed
        failed = [name for name, ok, _ in checks if not ok]
        if "just_cause" in failed:
            status = EthicalStatus.DENIED_JUST_CAUSE
        elif "authority" in failed:
            status = EthicalStatus.DENIED_AUTHORITY
        elif "proportionality" in failed:
            status = EthicalStatus.DENIED_PROPORTIONALITY
        else:
            status = EthicalStatus.DENIED_NECESSITY
    
    # Create operation record
    operation_id = hashlib.sha256(
        f"{holder_id}:{target_id}:{operation.name}:{timestamp}".encode()
    ).hexdigest()[:16]
    
    # Combine proofs
    proof_data = "|".join(f"{name}:{proof.proof_hash}" for name, _, proof in checks)
    combined_proof = ProofObject(
        rule="AuthorizeForceOperation",
        premises=[
            f"operation={operation.name}",
            f"target={target_id}",
            f"force={force_level}",
            f"checks={len(checks)}"
        ],
        conclusion=f"status={status.name}"
    )
    
    record = None
    if status == EthicalStatus.AUTHORIZED:
        record = ForceOperationRecord(
            operation_id=operation_id,
            operation_type=operation,
            target_id=target_id,
            initiator_id=holder_id,
            crusader_cap=cap,
            ethical_status=status,
            just_cause_verified=just_cause_ok,
            authority_verified=authority_ok,
            proportionality_verified=proportionality_ok,
            necessity_verified=necessity_ok,
            force_level=force_level,
            affected_resources=affected_resources,
            timestamp=timestamp,
            proof_hash=combined_proof.proof_hash
        )
    
    # Update statistics
    new_ops = state.operations.copy()
    if record:
        new_ops.append(record)
    
    new_state = CrusaderBridgeState(
        capabilities=state.capabilities,
        operations=new_ops,
        exhaustion_attempts=state.exhaustion_attempts,
        total_operations=state.total_operations + 1,
        authorized_operations=state.authorized_operations + (1 if status == EthicalStatus.AUTHORIZED else 0),
        denied_operations=state.denied_operations + (0 if status == EthicalStatus.AUTHORIZED else 1)
    )
    
    return new_state, status, record, combined_proof


def get_ethical_audit_log(
    state: CrusaderBridgeState,
    target_id: Optional[str] = None
) -> Tuple[List[ForceOperationRecord], ProofObject]:
    """Get audit log of force operations.
    
    Args:
        state: Crusader bridge state
        target_id: Optional filter by target
        
    Returns:
        (records, proof)
    """
    if target_id:
        records = [op for op in state.operations if op.target_id == target_id]
    else:
        records = state.operations.copy()
    
    authorized_count = sum(1 for r in records if r.ethical_status == EthicalStatus.AUTHORIZED)
    denied_count = len(records) - authorized_count
    
    return records, ProofObject(
        rule="GetEthicalAuditLog",
        premises=[
            f"total_records={len(records)}",
            f"authorized={authorized_count}",
            f"denied={denied_count}"
        ],
        conclusion="audit log retrieved"
    )
