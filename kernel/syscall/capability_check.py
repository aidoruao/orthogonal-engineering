#!/usr/bin/env python3
"""
Capability Check — Pre-syscall capability verification

Every syscall is checked for required capabilities before execution.
This is the enforcement point of the capability security model.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional
from fractions import Fraction

from axioms.logic import ProofObject
from axioms.capability_security import Capability, Permission

from .interface import SyscallNumber


@dataclass(frozen=True)
class SyscallAudit:
    """Audit record for a capability-checked syscall."""
    syscall_num: int
    process_id: str
    capability_target: str
    permission: str
    granted: bool
    timestamp: str
    
    def proof(self) -> ProofObject:
        return ProofObject(
            rule="SyscallAudit",
            premises=[
                f"syscall={self.syscall_num}",
                f"pid={self.process_id}",
                f"cap={self.capability_target}",
            ],
            conclusion=f"granted={self.granted}"
        )


@dataclass
class CapabilityChecker:
    """Pre-syscall capability verification."""
    audit_log: List[SyscallAudit] = field(default_factory=list)
    rate_limits: Dict[str, Fraction] = field(default_factory=dict)  # process_id -> calls/sec
    
    def check_syscall(
        self,
        syscall: SyscallNumber,
        process_id: str,
        capabilities: List[Capability],
        target_resource: str,
        required_perm: Permission
    ) -> Tuple[bool, SyscallAudit]:
        """Check if process has capability for syscall.
        
        Returns:
            (permitted, audit_record)
        """
        # Check rate limit
        current_rate = self.rate_limits.get(process_id, Fraction(0))
        if current_rate > Fraction(1000):  # Max 1000 syscalls/sec
            audit = SyscallAudit(
                syscall_num=syscall.value,
                process_id=process_id,
                capability_target=target_resource,
                permission=required_perm.value,
                granted=False,
                timestamp="rate_limited"
            )
            return False, audit
        
        # Check capability
        has_cap = any(
            cap.target == target_resource and cap.has_permission(required_perm)
            for cap in capabilities
        )
        
        audit = SyscallAudit(
            syscall_num=syscall.value,
            process_id=process_id,
            capability_target=target_resource,
            permission=required_perm.value,
            granted=has_cap,
            timestamp="checked"
        )
        
        self.audit_log.append(audit)
        
        return has_cap, audit
    
    def get_audit_trail(
        self,
        process_id: str
    ) -> Tuple[List[SyscallAudit], ProofObject]:
        """Get audit trail for a process."""
        trail = [a for a in self.audit_log if a.process_id == process_id]
        
        return trail, ProofObject(
            rule="CapabilityGetAudit",
            premises=[f"pid={process_id}", f"entries={len(trail)}"],
            conclusion="audit trail retrieved"
        )
