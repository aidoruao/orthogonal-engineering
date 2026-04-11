#!/usr/bin/env python3
"""
P2P Identity — Self-sovereign identity with capability-gated delegation

Identity is not assigned by a central authority. It is self-generated
through cryptographic proof-of-work, then attested by peers.

Mathematical Foundation:
  - axioms/cryptographic_verification.py for key verification
  - axioms/zero_knowledge.py for selective disclosure
  - axioms/number_theory.py for key generation

Regulatory Reference:
  - GDPR Article 25 — Data protection by design
  - SSI (Self-Sovereign Identity) principles

Biblical: Exodus 3:14 — "I AM WHO I AM" — identity as self-declaration
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional, Set
from fractions import Fraction
from enum import Enum, auto
import hashlib

from axioms.logic import ProofObject
from axioms.capability_security import Capability, Permission


class IdentityStatus(Enum):
    """Lifecycle status of an identity."""
    PROVISIONAL = auto()    # New, not yet attested
    ACTIVE = auto()         # Attested by peers, operational
    SUSPENDED = auto()      # Under dispute
    REVOKED = auto()        # Permanently revoked


@dataclass(frozen=True)
class IdentityKey:
    """Cryptographic identity key.
    
    The public key is the identity. The private key is held only by
    the identity owner (never by the kernel).
    """
    public_key: str  # Hex-encoded public key
    key_type: str = "ed25519"  # Default to Ed25519
    
    def fingerprint(self) -> str:
        """Generate short fingerprint of this key."""
        return hashlib.sha256(self.public_key.encode()).hexdigest()[:16]


@dataclass(frozen=True)
class Identity:
    """A self-sovereign identity.
    
    An identity is a public key plus metadata. The kernel never holds
    the private key. Identity operations require cryptographic proof.
    """
    identity_id: str  # Derived from public key fingerprint
    primary_key: IdentityKey
    status: IdentityStatus
    created_at: str  # ISO-8601 timestamp
    attestations: Tuple[str, ...]  # IDs of identities that attested this one
    
    def verify_signature(self, message: str, signature: str) -> Tuple[bool, ProofObject]:
        """Verify a signature from this identity.
        
        In real implementation: uses ed25519_verify.
        Here: abstract specification with ProofObject.
        """
        # Abstract verification
        is_valid = signature.startswith(f"sig:{self.identity_id}")
        
        proof = ProofObject(
            rule="IdentityVerifySignature",
            premises=[
                f"identity={self.identity_id}",
                f"message_hash={hashlib.sha256(message.encode()).hexdigest()[:16]}...",
            ],
            conclusion=f"valid={is_valid}"
        )
        
        return is_valid, proof


@dataclass(frozen=True)
class IdentityCap:
    """Capability to act as an identity.
    
    Grants the holder the right to perform operations as the identity.
    """
    identity_id: str
    permissions: Set[str]  # "sign", "attest", "delegate", "revoke"
    attenuations: Tuple[str, ...]
    
    def has_permission(self, perm: str) -> bool:
        return perm in self.permissions


@dataclass
class IdentityRegistry:
    """Registry of identities in the system.
    
    Not a central authority — just a witness of observed identities.
    Anyone can propose an identity. Attestation makes it real.
    """
    identities: Dict[str, Identity] = field(default_factory=dict)
    attestations: Dict[str, List[str]] = field(default_factory=dict)  # id -> list of attester ids
    
    def register_identity(
        self,
        public_key: str,
        timestamp: str,
    ) -> Tuple[Identity, ProofObject]:
        """Register a new provisional identity.
        
        Args:
            public_key: Hex-encoded public key
            timestamp: ISO-8601 timestamp
            
        Returns:
            (identity, proof)
        """
        key = IdentityKey(public_key=public_key)
        identity_id = key.fingerprint()
        
        identity = Identity(
            identity_id=identity_id,
            primary_key=key,
            status=IdentityStatus.PROVISIONAL,
            created_at=timestamp,
            attestations=tuple(),
        )
        
        self.identities[identity_id] = identity
        
        proof = ProofObject(
            rule="IdentityRegister",
            premises=[
                f"identity_id={identity_id}",
                f"key_type={key.key_type}",
                f"timestamp={timestamp}",
            ],
            conclusion="identity registered (provisional)"
        )
        
        return identity, proof
    
    def attest_identity(
        self,
        attester_id: str,
        attestee_id: str,
        timestamp: str,
    ) -> Tuple[bool, ProofObject]:
        """Attest to the validity of an identity.
        
        An identity becomes ACTIVE after 3 attestations (by the testimony
        of two or three witnesses — Matthew 18:16).
        
        Args:
            attester_id: Identity making the attestation
            attestee_id: Identity being attested
            timestamp: ISO-8601 timestamp
            
        Returns:
            (success, proof)
        """
        if attestee_id not in self.identities:
            return False, ProofObject(
                rule="IdentityAttest",
                premises=[f"attestee={attestee_id}"],
                conclusion="failed: attestee not found"
            )
        
        if attester_id not in self.identities:
            return False, ProofObject(
                rule="IdentityAttest",
                premises=[f"attester={attester_id}"],
                conclusion="failed: attester not found"
            )
        
        # Record attestation
        if attestee_id not in self.attestations:
            self.attestations[attestee_id] = []
        
        if attester_id in self.attestations[attestee_id]:
            return False, ProofObject(
                rule="IdentityAttest",
                premises=[f"attester={attester_id}", f"attestee={attestee_id}"],
                conclusion="failed: already attested"
            )
        
        self.attestations[attestee_id].append(attester_id)
        
        # Check if now active (3 attestations)
        identity = self.identities[attestee_id]
        if len(self.attestations[attestee_id]) >= 3 and identity.status == IdentityStatus.PROVISIONAL:
            from dataclasses import replace
            new_identity = replace(identity, status=IdentityStatus.ACTIVE)
            self.identities[attestee_id] = new_identity
        
        proof = ProofObject(
            rule="IdentityAttest",
            premises=[
                f"attester={attester_id}",
                f"attestee={attestee_id}",
                f"attestation_count={len(self.attestations[attestee_id])}",
            ],
            conclusion="attestation recorded"
        )
        
        return True, proof
    
    def get_identity(self, identity_id: str) -> Tuple[Optional[Identity], ProofObject]:
        """Get identity by ID.
        
        Returns:
            (identity, proof) — identity is None if not found
        """
        identity = self.identities.get(identity_id)
        
        if identity is None:
            return None, ProofObject(
                rule="IdentityGet",
                premises=[f"identity_id={identity_id}"],
                conclusion="not found"
            )
        
        return identity, ProofObject(
            rule="IdentityGet",
            premises=[
                f"identity_id={identity_id}",
                f"status={identity.status.name}",
            ],
            conclusion="found"
        )
