#!/usr/bin/env python3
"""
Sovereign Role — Capability grant and revocation.

The Sovereign (@aidoruao) is the sole human authority in the Yeshua Commonwealth.
All capabilities flow from the Sovereign through documented, hash-anchored grants.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject
from axioms.capability_security import Capability, Permission


class ScopeType(Enum):
    """Types of capability scope."""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DELEGATE = "delegate"
    ADMIN = "admin"


@dataclass(frozen=True)
class Scope:
    """A scope defines what a capability permits.
    
    Scopes are immutable and hashable for use in capability grants.
    """
    domain: str           # Domain identifier (e.g., "d_automotive")
    resource: str         # Resource within domain (e.g., "invariants.py")
    scope_type: ScopeType # Type of access permitted
    
    def __hash__(self) -> int:
        # TODO: Expand __hash__() - stub detected by Yeshua Agent
        return hash((self.domain, self.resource, self.scope_type))


@dataclass(frozen=True)
class GrantRecord:
    """A record of a capability grant from Sovereign to Steward.
    
    Immutable, hash-anchored evidence of authorization.
    """
    grant_id: str
    steward_id: str
    capability: Capability
    scope: Scope
    justification_hash: str  # SHA-256 of justification text
    timestamp: str
    
    def proof(self) -> ProofObject:
        """Generate ProofObject for this grant."""
        return ProofObject(
            rule="SovereignGrant",
            premises=[
                f"grant_id={self.grant_id}",
                f"steward={self.steward_id}",
                f"capability={self.capability.target}",
                f"scope={self.scope.domain}/{self.scope.resource}",
                f"justification_hash={self.justification_hash[:16]}...",
            ],
            conclusion=f"capability granted at {self.timestamp}"
        )


@dataclass
class RevocationRecord:
    """A record of capability revocation."""
    revocation_id: str
    grant_id: str
    reason: str
    evidence_hash: str
    timestamp: str
    
    def proof(self) -> ProofObject:
        """Generate ProofObject for this revocation."""
        return ProofObject(
            rule="SovereignRevoke",
            premises=[
                f"revocation_id={self.revocation_id}",
                f"grant_id={self.grant_id}",
                f"reason={self.reason}",
                f"evidence_hash={self.evidence_hash[:16]}...",
            ],
            conclusion=f"capability revoked at {self.timestamp}"
        )


@dataclass
class SovereignRole:
    """Sovereign capability grant and revocation.
    
    The Sovereign is the root of all authority in the Commonwealth.
    Every capability grant is documented, hash-anchored, and witnessed.
    """
    sovereign_id: str = "@aidoruao"
    grants: Dict[str, GrantRecord] = field(default_factory=dict)
    revocations: Dict[str, RevocationRecord] = field(default_factory=dict)
    grant_counter: int = field(default=0)
    revocation_counter: int = field(default=0)
    
    def grant_capability(
        self,
        steward_id: str,
        scope: Scope,
        permissions: frozenset,
        justification: str,
        timestamp: str,
    ) -> Tuple[GrantRecord, ProofObject]:
        """Grant capability to steward with ProofObject justification.
        
        Args:
            steward_id: Identifier of steward receiving capability
            scope: Scope of the capability
            permissions: Set of permissions granted
            justification: Human-readable justification for grant
            timestamp: ISO-8601 timestamp of grant
            
        Returns:
            (grant_record, proof)
        """
        import hashlib
        
        # Generate grant ID
        self.grant_counter += 1
        grant_id = f"GRANT_{self.sovereign_id}_{self.grant_counter:06d}"
        
        # Compute justification hash
        justification_hash = hashlib.sha256(
            justification.encode("utf-8")
        ).hexdigest()
        
        # Create capability
        capability = Capability(
            target=f"{scope.domain}/{scope.resource}",
            permissions=permissions,
            attenuations=tuple(),
            delegator=self.sovereign_id,
        )
        
        # Create grant record
        grant = GrantRecord(
            grant_id=grant_id,
            steward_id=steward_id,
            capability=capability,
            scope=scope,
            justification_hash=justification_hash,
            timestamp=timestamp,
        )
        
        # Store grant
        self.grants[grant_id] = grant
        
        # Generate proof
        proof = ProofObject(
            rule="SovereignGrantCapability",
            premises=[
                f"sovereign={self.sovereign_id}",
                f"steward={steward_id}",
                f"scope={scope.domain}/{scope.resource}",
                f"permissions={permissions}",
                f"justification_hash={justification_hash}",
            ],
            conclusion=f"grant_id={grant_id}"
        )
        
        return grant, proof
    
    def revoke_capability(
        self,
        grant_id: str,
        reason: str,
        evidence: str,
        timestamp: str,
    ) -> Tuple[Optional[RevocationRecord], ProofObject]:
        """Revoke a previously granted capability.
        
        Args:
            grant_id: ID of grant to revoke
            reason: Human-readable reason for revocation
            evidence: Evidence supporting revocation
            timestamp: ISO-8601 timestamp of revocation
            
        Returns:
            (revocation_record, proof) — record is None if grant not found
        """
        import hashlib
        
        # Check grant exists
        if grant_id not in self.grants:
            return None, ProofObject(
                rule="SovereignRevokeCapability",
                premises=[f"grant_id={grant_id}"],
                conclusion="revocation failed: grant not found"
            )
        
        # Generate revocation ID
        self.revocation_counter += 1
        revocation_id = f"REVOKE_{self.sovereign_id}_{self.revocation_counter:06d}"
        
        # Compute evidence hash
        evidence_hash = hashlib.sha256(
            evidence.encode("utf-8")
        ).hexdigest()
        
        # Create revocation record
        revocation = RevocationRecord(
            revocation_id=revocation_id,
            grant_id=grant_id,
            reason=reason,
            evidence_hash=evidence_hash,
            timestamp=timestamp,
        )
        
        # Store revocation
        self.revocations[revocation_id] = revocation
        
        # Generate proof
        proof = ProofObject(
            rule="SovereignRevokeCapability",
            premises=[
                f"sovereign={self.sovereign_id}",
                f"grant_id={grant_id}",
                f"reason={reason}",
                f"evidence_hash={evidence_hash}",
            ],
            conclusion=f"revocation_id={revocation_id}"
        )
        
        return revocation, proof
    
    def is_grant_active(self, grant_id: str) -> Tuple[bool, ProofObject]:
        """Check if a grant is active (not revoked).
        
        Args:
            grant_id: Grant to check
            
        Returns:
            (is_active, proof)
        """
        if grant_id not in self.grants:
            return False, ProofObject(
                rule="CheckGrantActive",
                premises=[f"grant_id={grant_id}"],
                conclusion="grant not found"
            )
        
        # Check if revoked
        for revocation in self.revocations.values():
            if revocation.grant_id == grant_id:
                return False, ProofObject(
                    rule="CheckGrantActive",
                    premises=[
                        f"grant_id={grant_id}",
                        f"revocation_id={revocation.revocation_id}",
                    ],
                    conclusion="grant revoked"
                )
        
        return True, ProofObject(
            rule="CheckGrantActive",
            premises=[f"grant_id={grant_id}"],
            conclusion="grant active"
        )
    
    def declare_sabbath(
        self,
        state_hash: str,
        completion_proof: ProofObject,
        timestamp: str,
    ) -> Tuple[bool, ProofObject]:
        """Declare completion of current phase, initiate rest.
        
        The Sabbath Halt is a constitutional requirement — the system must
        rest when completion conditions are met, preventing infinite growth.
        
        Args:
            state_hash: SHA-256 of system state at declaration
            completion_proof: ProofObject verifying completion conditions
            timestamp: ISO-8601 timestamp
            
        Returns:
            (declared, proof)
        """
        # Verify completion proof is valid
        if not completion_proof.is_valid():
            return False, ProofObject(
                rule="DeclareSabbath",
                premises=[
                    f"sovereign={self.sovereign_id}",
                    f"state_hash={state_hash[:16]}...",
                ],
                conclusion="sabbath declaration failed: invalid completion proof"
            )
        
        # Generate proof
        proof = ProofObject(
            rule="DeclareSabbath",
            premises=[
                f"sovereign={self.sovereign_id}",
                f"state_hash={state_hash}",
                f"completion_proof_hash={completion_proof.proof_hash}",
                f"timestamp={timestamp}",
            ],
            conclusion="sabbath declared: rest initiated"
        )
        
        return True, proof
