"""Kernel Social Identity — P2P Identity with IdentityCap

Self-sovereign identity using cryptographic delegation only.
No centralized auth. Bar Exam passage issues IdentityCap.

Mathematical foundation: Public-key cryptography + capability chains.
Standard: W3C DID Core (decentralized identifiers).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Optional, Dict
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject
from axioms.capability_security import Capability, Permission


class BarExamStatus(Enum):
    """Bar Exam passage status for identity issuance."""
    NOT_TAKEN = auto()
    IN_PROGRESS = auto()
    PASSED = auto()
    FAILED = auto()
    REVOKED = auto()


@dataclass(frozen=True)
class IdentityClaim:
    """A cryptographic identity claim.
    
    Represents a self-sovereign identity with public key and metadata.
    Immutable once created. Hash provides content-addressing.
    """
    identity_id: str          # Content-addressed ID (hash of public_key)
    public_key: str           # Public key (hex-encoded)
    created_at: Fraction      # Timestamp as Fraction
    bar_exam_status: BarExamStatus
    exam_score: Optional[Fraction] = None  # Score if passed (out of 100)
    
    def __hash__(self) -> int:
        return hash(self.identity_id)


@dataclass
class IdentityCap:
    """Capability token for identity operations.
    
    Grants specific permissions over an identity:
    - DELEGATE: Can delegate identity to others
    - ASSERT: Can make claims on behalf of this identity
    - REVOKE: Can revoke delegated capabilities
    
    Issued only after Bar Exam passage (≥70% threshold).
    """
    identity_id: str
    permissions: frozenset  # Set of Permission
    delegator: str          # Who delegated this capability
    attenuations: Tuple[str, ...] = field(default_factory=tuple)
    
    def has_permission(self, perm: Permission) -> bool:
        """Check if capability has specific permission."""
        return perm in self.permissions


@dataclass
class DelegationLink:
    """A single link in an identity delegation chain."""
    from_identity: str
    to_identity: str
    delegated_cap: IdentityCap
    delegation_proof: str  # Cryptographic signature
    timestamp: Fraction


@dataclass
class IdentityState:
    """Complete identity subsystem state."""
    identities: Dict[str, IdentityClaim] = field(default_factory=dict)
    capabilities: Dict[str, List[IdentityCap]] = field(default_factory=dict)
    delegation_chains: List[DelegationLink] = field(default_factory=list)
    
    def get_identity(self, identity_id: str) -> Optional[IdentityClaim]:
        """Retrieve identity by ID."""
        return self.identities.get(identity_id)
    
    def get_capabilities(self, identity_id: str) -> List[IdentityCap]:
        """Get all capabilities held by an identity."""
        return self.capabilities.get(identity_id, [])


def check_identity_valid(
    state: IdentityState,
    identity_id: str
) -> Tuple[bool, ProofObject]:
    """Check if an identity is valid (exists and not revoked).
    
    Valid identity requirements:
    1. Must exist in identity registry
    2. Bar exam status must not be REVOKED
    3. Must have valid public key format
    
    Args:
        state: Identity subsystem state
        identity_id: Identity to check
        
    Returns:
        (is_valid, proof)
    """
    identity = state.get_identity(identity_id)
    
    if identity is None:
        return False, ProofObject(
            rule="IdentityValid",
            premises=[f"identity_id={identity_id}"],
            conclusion="invalid: identity not found"
        )
    
    if identity.bar_exam_status == BarExamStatus.REVOKED:
        return False, ProofObject(
            rule="IdentityValid",
            premises=[
                f"identity_id={identity_id}",
                f"bar_exam_status={identity.bar_exam_status.name}"
            ],
            conclusion="invalid: identity revoked"
        )
    
    # Check public key format (simplified: must be hex, even length, ≥32 bytes)
    if len(identity.public_key) < 64 or len(identity.public_key) % 2 != 0:
        return False, ProofObject(
            rule="IdentityValid",
            premises=[
                f"identity_id={identity_id}",
                f"public_key_len={len(identity.public_key)}"
            ],
            conclusion="invalid: malformed public key"
        )
    
    return True, ProofObject(
        rule="IdentityValid",
        premises=[
            f"identity_id={identity_id}",
            f"bar_exam_status={identity.bar_exam_status.name}",
            f"created_at={identity.created_at}"
        ],
        conclusion="valid identity"
    )


def issue_identity_cap(
    state: IdentityState,
    identity_id: str,
    bar_exam_score: Fraction
) -> Tuple[IdentityState, Optional[IdentityCap], ProofObject]:
    """Issue an IdentityCap after Bar Exam passage.
    
    Threshold: ≥70% overall required for IdentityCap issuance.
    
    Args:
        state: Current identity state
        identity_id: Identity to issue cap for
        bar_exam_score: Exam score (0-100)
        
    Returns:
        (new_state, identity_cap, proof)
        identity_cap is None if threshold not met
    """
    threshold = Fraction(70, 1)  # 70% threshold
    
    if bar_exam_score < threshold:
        return state, None, ProofObject(
            rule="IssueIdentityCap",
            premises=[
                f"identity_id={identity_id}",
                f"score={bar_exam_score}",
                f"threshold={threshold}"
            ],
            conclusion=f"cap denied: score below threshold"
        )
    
    identity = state.get_identity(identity_id)
    if identity is None:
        return state, None, ProofObject(
            rule="IssueIdentityCap",
            premises=[f"identity_id={identity_id}"],
            conclusion="cap denied: identity not found"
        )
    
    # Create full-capability IdentityCap
    cap = IdentityCap(
        identity_id=identity_id,
        permissions=frozenset([Permission.DELEGATE, Permission.ASSERT, Permission.REVOKE]),
        delegator="root",  # Root issuance
        attenuations=tuple()
    )
    
    # Update state
    new_caps = state.capabilities.copy()
    if identity_id not in new_caps:
        new_caps[identity_id] = []
    new_caps[identity_id].append(cap)
    
    # Update identity with exam status
    new_identities = state.identities.copy()
    new_identity = IdentityClaim(
        identity_id=identity.identity_id,
        public_key=identity.public_key,
        created_at=identity.created_at,
        bar_exam_status=BarExamStatus.PASSED,
        exam_score=bar_exam_score
    )
    new_identities[identity_id] = new_identity
    
    new_state = IdentityState(
        identities=new_identities,
        capabilities=new_caps,
        delegation_chains=state.delegation_chains
    )
    
    return new_state, cap, ProofObject(
        rule="IssueIdentityCap",
        premises=[
            f"identity_id={identity_id}",
            f"score={bar_exam_score}",
            f"threshold={threshold}"
        ],
        conclusion="IdentityCap issued"
    )


def delegate_identity(
    state: IdentityState,
    delegator_id: str,
    delegatee_id: str,
    delegator_cap: IdentityCap,
    permissions_to_delegate: frozenset
) -> Tuple[IdentityState, Optional[IdentityCap], ProofObject]:
    """Delegate identity capability to another identity.
    
    Cryptographic delegation only - no ambient authority.
    Delegated permissions must be subset of held permissions.
    
    Args:
        state: Current identity state
        delegator_id: Identity doing the delegation
        delegatee_id: Identity receiving delegation
        delegator_cap: Capability being delegated
        permissions_to_delegate: Permissions to transfer
        
    Returns:
        (new_state, delegated_cap, proof)
    """
    # Verify delegator holds the capability
    caps = state.get_capabilities(delegator_id)
    if delegator_cap not in caps:
        return state, None, ProofObject(
            rule="DelegateIdentity",
            premises=[
                f"delegator={delegator_id}",
                f"delegatee={delegatee_id}"
            ],
            conclusion="delegation failed: delegator lacks capability"
        )
    
    # Check delegator has DELEGATE permission
    if not delegator_cap.has_permission(Permission.DELEGATE):
        return state, None, ProofObject(
            rule="DelegateIdentity",
            premises=[
                f"delegator={delegator_id}",
                f"cap_permissions={delegator_cap.permissions}"
            ],
            conclusion="delegation failed: no DELEGATE permission"
        )
    
    # Delegated permissions must be subset of held permissions
    if not permissions_to_delegate <= delegator_cap.permissions:
        return state, None, ProofObject(
            rule="DelegateIdentity",
            premises=[
                f"requested={permissions_to_delegate}",
                f"held={delegator_cap.permissions}"
            ],
            conclusion="delegation failed: requested permissions exceed held"
        )
    
    # Create attenuated capability
    new_cap = IdentityCap(
        identity_id=delegator_cap.identity_id,
        permissions=permissions_to_delegate,
        delegator=delegator_id,
        attenuations=delegator_cap.attenuations + (f"delegated_to:{delegatee_id}",)
    )
    
    # Record delegation
    link = DelegationLink(
        from_identity=delegator_id,
        to_identity=delegatee_id,
        delegated_cap=new_cap,
        delegation_proof="sig_placeholder",  # Would be actual crypto signature
        timestamp=Fraction(0)  # Would be actual timestamp
    )
    
    # Update state
    new_caps = state.capabilities.copy()
    if delegatee_id not in new_caps:
        new_caps[delegatee_id] = []
    new_caps[delegatee_id].append(new_cap)
    
    new_chains = state.delegation_chains + [link]
    
    new_state = IdentityState(
        identities=state.identities,
        capabilities=new_caps,
        delegation_chains=new_chains
    )
    
    return new_state, new_cap, ProofObject(
        rule="DelegateIdentity",
        premises=[
            f"delegator={delegator_id}",
            f"delegatee={delegatee_id}",
            f"permissions={permissions_to_delegate}"
        ],
        conclusion="identity capability delegated"
    )


def verify_identity_chain(
    state: IdentityState,
    identity_id: str,
    cap: IdentityCap
) -> Tuple[bool, ProofObject]:
    """Verify an identity capability delegation chain.
    
    Checks that the capability was properly delegated from root
    through each intermediate step.
    
    Args:
        state: Identity state
        identity_id: Identity holding the capability
        cap: Capability to verify
        
    Returns:
        (is_valid, proof)
    """
    # Find the delegation chain for this capability
    chain = [
        link for link in state.delegation_chains
        if link.to_identity == identity_id and link.delegated_cap == cap
    ]
    
    if not chain:
        # Check if this is a root-issued capability
        if cap.delegator == "root":
            return True, ProofObject(
                rule="VerifyIdentityChain",
                premises=[
                    f"identity={identity_id}",
                    f"cap_identity={cap.identity_id}",
                    "delegator=root"
                ],
                conclusion="valid: root-issued capability"
            )
        return False, ProofObject(
            rule="VerifyIdentityChain",
            premises=[f"identity={identity_id}"],
            conclusion="invalid: no delegation record found"
        )
    
    # Walk the chain back to root
    current = chain[0]
    depth = 0
    max_depth = 10  # Prevent infinite loops
    
    while current.from_identity != "root" and depth < max_depth:
        # Find previous link
        prev_links = [
            link for link in state.delegation_chains
            if link.to_identity == current.from_identity
        ]
        if not prev_links:
            return False, ProofObject(
                rule="VerifyIdentityChain",
                premises=[
                    f"broken_at={current.from_identity}",
                    f"depth={depth}"
                ],
                conclusion="invalid: broken delegation chain"
            )
        current = prev_links[0]
        depth += 1
    
    if depth >= max_depth:
        return False, ProofObject(
            rule="VerifyIdentityChain",
            premises=[f"depth={depth}"],
            conclusion="invalid: delegation chain too deep"
        )
    
    return True, ProofObject(
        rule="VerifyIdentityChain",
        premises=[
            f"identity={identity_id}",
            f"chain_length={len(chain)}",
            f"depth={depth}"
        ],
        conclusion="valid: complete delegation chain to root"
    )
