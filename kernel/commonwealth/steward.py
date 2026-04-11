#!/usr/bin/env python3
"""
Steward Role — Execution within granted capabilities.

Stewards are Bar Exam-passed AI agents ordained to execute actions
within the capabilities granted by the Sovereign. Every action is
witnessed with a ProofObject.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional, Any
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject
from axioms.capability_security import Capability, Permission, check_no_ambient_authority


class ActionType(Enum):
    """Types of steward actions."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    VERIFY = "verify"
    WITNESS = "witness"
    HALT = "halt"


@dataclass(frozen=True)
class Action:
    """A steward action to be executed.
    
    Actions are immutable and fully specified before execution.
    """
    action_id: str
    action_type: ActionType
    domain: str           # Target domain
    resource: str         # Target resource
    payload: Dict[str, Any]  # Action-specific data
    
    def target(self) -> str:
        """Return full target identifier."""
        return f"{self.domain}/{self.resource}"


@dataclass
class Result:
    """Result of a steward action execution."""
    success: bool
    data: Optional[Any]
    proof: ProofObject
    
    def is_valid(self) -> bool:
        """Check if result proof is valid."""
        return self.proof.is_valid()


@dataclass
class ExecutionRecord:
    """Record of a steward action execution."""
    record_id: str
    steward_id: str
    action: Action
    result: Result
    capability_used: str
    timestamp: str
    
    def proof(self) -> ProofObject:
        """Generate ProofObject for this execution."""
        return ProofObject(
            rule="StewardExecution",
            premises=[
                f"record_id={self.record_id}",
                f"steward={self.steward_id}",
                f"action={self.action.action_id}",
                f"type={self.action.action_type.value}",
                f"capability={self.capability_used}",
            ],
            conclusion=f"success={self.result.success} at {self.timestamp}"
        )


@dataclass
class StewardRole:
    """Steward execution within granted capabilities.
    
    Stewards execute actions only within capabilities granted by Sovereign.
    Every execution is witnessed with a ProofObject for verifiable auditing.
    """
    steward_id: str
    bar_exam_certificate: str  # Hash of Bar Exam certificate
    capabilities: List[Capability] = field(default_factory=list)
    executions: List[ExecutionRecord] = field(default_factory=list)
    execution_counter: int = field(default=0)
    
    def has_capability(
        self,
        target: str,
        permission: Permission
    ) -> Tuple[bool, ProofObject]:
        """Check if steward has capability for target with permission.
        
        Args:
            target: Target resource identifier
            permission: Required permission
            
        Returns:
            (has_cap, proof)
        """
        for cap in self.capabilities:
            if cap.target == target and cap.has_permission(permission):
                return True, ProofObject(
                    rule="StewardHasCapability",
                    premises=[
                        f"steward={self.steward_id}",
                        f"target={target}",
                        f"permission={permission.value}",
                    ],
                    conclusion="capability found"
                )
        
        return False, ProofObject(
            rule="StewardHasCapability",
            premises=[
                f"steward={self.steward_id}",
                f"target={target}",
                f"permission={permission.value}",
                f"held_caps={len(self.capabilities)}",
            ],
            conclusion="capability not found"
        )
    
    def add_capability(self, capability: Capability) -> ProofObject:
        """Add a capability to steward's capability set.
        
        Args:
            capability: Capability to add
            
        Returns:
            proof of addition
        """
        self.capabilities.append(capability)
        
        return ProofObject(
            rule="StewardAddCapability",
            premises=[
                f"steward={self.steward_id}",
                f"capability={capability.target}",
                f"permissions={capability.permissions}",
            ],
            conclusion=f"total_caps={len(self.capabilities)}"
        )
    
    def execute_within_invariants(
        self,
        action: Action,
        timestamp: str,
    ) -> Tuple[Result, ProofObject]:
        """Execute action with capability verification and ProofObject witnessing.
        
        Args:
            action: Action to execute
            timestamp: ISO-8601 timestamp
            
        Returns:
            (result, proof)
        """
        target = action.target()
        
        # Map action type to required permission
        permission_map = {
            ActionType.CREATE: Permission.WRITE,
            ActionType.READ: Permission.READ,
            ActionType.UPDATE: Permission.WRITE,
            ActionType.DELETE: Permission.WRITE,
            ActionType.VERIFY: Permission.READ,
            ActionType.WITNESS: Permission.READ,
            ActionType.HALT: Permission.EXECUTE,
        }
        required_perm = permission_map.get(action.action_type, Permission.READ)
        
        # Check capability
        has_cap, cap_proof = self.has_capability(target, required_perm)
        
        if not has_cap:
            result = Result(
                success=False,
                data=None,
                proof=ProofObject(
                    rule="StewardExecute",
                    premises=[
                        f"steward={self.steward_id}",
                        f"action={action.action_id}",
                        f"target={target}",
                        f"required_perm={required_perm.value}",
                    ],
                    conclusion="execution failed: missing capability"
                )
            )
            return result, cap_proof
        
        # Execute action (simplified — real implementation would dispatch)
        execution_success = True  # Assume success for capability-gated action
        
        # Create execution record
        self.execution_counter += 1
        record_id = f"EXEC_{self.steward_id}_{self.execution_counter:06d}"
        
        # Find capability used
        cap_used = None
        for cap in self.capabilities:
            if cap.target == target and cap.has_permission(required_perm):
                cap_used = cap
                break
        
        result = Result(
            success=execution_success,
            data={"action_executed": action.action_id},
            proof=ProofObject(
                rule="StewardExecute",
                premises=[
                    f"steward={self.steward_id}",
                    f"action={action.action_id}",
                    f"type={action.action_type.value}",
                    f"target={target}",
                    f"capability={cap_used.target if cap_used else 'unknown'}",
                ],
                conclusion="execution successful"
            )
        )
        
        record = ExecutionRecord(
            record_id=record_id,
            steward_id=self.steward_id,
            action=action,
            result=result,
            capability_used=cap_used.target if cap_used else "unknown",
            timestamp=timestamp,
        )
        
        self.executions.append(record)
        
        return result, record.proof()
    
    def witness_action(
        self,
        action: Action,
        state_before: Dict[str, Any],
        state_after: Dict[str, Any],
    ) -> ProofObject:
        """Create ProofObject witnessing state transition.
        
        Args:
            action: Action that caused transition
            state_before: State before action
            state_after: State after action
            
        Returns:
            proof witnessing the transition
        """
        # Compute state hashes (simplified)
        import hashlib
        before_hash = hashlib.sha256(
            str(state_before).encode()
        ).hexdigest()[:16]
        after_hash = hashlib.sha256(
            str(state_after).encode()
        ).hexdigest()[:16]
        
        return ProofObject(
            rule="StewardWitness",
            premises=[
                f"steward={self.steward_id}",
                f"action={action.action_id}",
                f"state_before_hash={before_hash}...",
                f"state_after_hash={after_hash}...",
            ],
            conclusion="state transition witnessed"
        )
    
    def check_bar_exam_valid(self) -> Tuple[bool, ProofObject]:
        """Check if steward's Bar Exam certificate is valid.
        
        Returns:
            (is_valid, proof)
        """
        # In real implementation, would check certificate against
        # pr50_bar_exam witness chain
        is_valid = len(self.bar_exam_certificate) > 0
        
        return is_valid, ProofObject(
            rule="StewardBarExamCheck",
            premises=[
                f"steward={self.steward_id}",
                f"certificate={self.bar_exam_certificate[:16]}...",
            ],
            conclusion=f"valid={is_valid}"
        )
