#!/usr/bin/env python3
"""
Consent Communications — All communication requires explicit consent

No message is delivered without explicit consent from the receiver.
This is not a technical limitation — it is a constitutional requirement.

Mathematical Foundation:
  - axioms/process_algebra.py for communication protocols
  - axioms/temporal_logic.py for consent expiration
  - axioms/epistemic_logic.py for knowledge of consent

Regulatory Reference:
  - GDPR Article 6 — Lawfulness of processing
  - ePrivacy Directive — Consent for communications

Biblical: 1 Corinthians 6:12 — "Not all things are beneficial"
  Consent ensures communication is beneficial, not just lawful.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject
from axioms.temporal_logic import TimeInterval


class ConsentStatus(Enum):
    """Status of a consent grant."""
    PENDING = auto()    # Requested, not yet granted
    GRANTED = auto()    # Active consent
    REVOKED = auto()    # Explicitly revoked
    EXPIRED = auto()    # Time limit reached


@dataclass(frozen=True)
class ConsentRequest:
    """Request for communication consent.
    
    Every communication must begin with a request.
    """
    request_id: str
    sender_id: str
    receiver_id: str
    purpose: str
    data_types: Tuple[str, ...]  # What data will be shared
    duration: TimeInterval  # How long consent lasts
    timestamp: str
    
    def proof(self) -> ProofObject:
        """Generate ProofObject for this request."""
        return ProofObject(
            rule="ConsentRequest",
            premises=[
                f"request_id={self.request_id}",
                f"sender={self.sender_id}",
                f"receiver={self.receiver_id}",
                f"purpose={self.purpose}",
            ],
            conclusion=f"consent requested at {self.timestamp}"
        )


@dataclass(frozen=True)
class ConsentGrant:
    """Explicit grant of consent.
    
    Consent is:
    - Freely given (not coerced)
    - Specific (limited purpose)
    - Informed (receiver knows what they're consenting to)
    - Unambiguous (clear affirmative action)
    - Revocable (can be withdrawn)
    """
    grant_id: str
    request_id: str
    granter_id: str  # Who grants consent (receiver of request)
    grantee_id: str  # Who receives consent (sender of request)
    scope: Tuple[str, ...]  # What is permitted
    status: ConsentStatus
    created_at: str
    expires_at: str
    
    def is_active(self, current_time: str) -> bool:
        """Check if consent is currently active."""
        if self.status != ConsentStatus.GRANTED:
            return False
        # Simple string comparison (ISO-8601 format)
        return current_time < self.expires_at
    
    def proof(self) -> ProofObject:
        """Generate ProofObject for this grant."""
        return ProofObject(
            rule="ConsentGrant",
            premises=[
                f"grant_id={self.grant_id}",
                f"request_id={self.request_id}",
                f"granter={self.granter_id}",
                f"status={self.status.name}",
            ],
            conclusion=f"consent {self.status.name.lower()}"
        )


@dataclass
class ConsentChannel:
    """A communication channel gated by consent.
    
    No message passes without valid consent.
    """
    channel_id: str
    sender_id: str
    receiver_id: str
    consent_grant: Optional[ConsentGrant]
    messages: List[Tuple[str, str, ProofObject]] = field(default_factory=list)  # (content, timestamp, proof)
    
    def can_send(self, current_time: str) -> Tuple[bool, ProofObject]:
        """Check if sender can transmit on this channel."""
        if self.consent_grant is None:
            return False, ProofObject(
                rule="ConsentCheck",
                premises=[f"channel={self.channel_id}"],
                conclusion="denied: no consent grant"
            )
        
        if not self.consent_grant.is_active(current_time):
            return False, ProofObject(
                rule="ConsentCheck",
                premises=[
                    f"channel={self.channel_id}",
                    f"grant_status={self.consent_grant.status.name}",
                ],
                conclusion="denied: consent not active"
            )
        
        return True, ProofObject(
            rule="ConsentCheck",
            premises=[
                f"channel={self.channel_id}",
                f"grant_id={self.consent_grant.grant_id}",
            ],
            conclusion="permitted: consent valid"
        )
    
    def send_message(
        self,
        content: str,
        timestamp: str,
    ) -> Tuple[bool, ProofObject]:
        """Send message if consent permits.
        
        Returns:
            (delivered, proof)
        """
        permitted, check_proof = self.can_send(timestamp)
        
        if not permitted:
            return False, check_proof
        
        # Record message
        delivery_proof = ProofObject(
            rule="MessageDeliver",
            premises=[
                f"channel={self.channel_id}",
                f"sender={self.sender_id}",
                f"receiver={self.receiver_id}",
                f"content_hash={hash(content) & 0xFFFF:04x}",
            ],
            conclusion="message delivered"
        )
        
        self.messages.append((content, timestamp, delivery_proof))
        
        return True, delivery_proof
    
    def revoke_consent(self, timestamp: str) -> ProofObject:
        """Revoke consent for this channel."""
        if self.consent_grant is not None:
            from dataclasses import replace
            self.consent_grant = replace(
                self.consent_grant,
                status=ConsentStatus.REVOKED
            )
        
        return ProofObject(
            rule="ConsentRevoke",
            premises=[
                f"channel={self.channel_id}",
                f"timestamp={timestamp}",
            ],
            conclusion="consent revoked"
        )


@dataclass
class ConsentManager:
    """Manages consent requests and grants across the system."""
    requests: Dict[str, ConsentRequest] = field(default_factory=dict)
    grants: Dict[str, ConsentGrant] = field(default_factory=dict)
    channels: Dict[str, ConsentChannel] = field(default_factory=dict)
    
    def request_consent(
        self,
        sender_id: str,
        receiver_id: str,
        purpose: str,
        data_types: Tuple[str, ...],
        duration: TimeInterval,
        timestamp: str,
    ) -> Tuple[ConsentRequest, ProofObject]:
        """Request consent for communication."""
        import hashlib
        
        # Generate request ID
        request_hash = hashlib.sha256(
            f"{sender_id}:{receiver_id}:{timestamp}".encode()
        ).hexdigest()[:16]
        request_id = f"CONSENT_REQ_{request_hash}"
        
        request = ConsentRequest(
            request_id=request_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            purpose=purpose,
            data_types=data_types,
            duration=duration,
            timestamp=timestamp,
        )
        
        self.requests[request_id] = request
        
        return request, request.proof()
    
    def grant_consent(
        self,
        request_id: str,
        granter_id: str,
        scope: Tuple[str, ...],
        duration_seconds: Fraction,
        timestamp: str,
    ) -> Tuple[Optional[ConsentGrant], ProofObject]:
        """Grant consent for a request."""
        if request_id not in self.requests:
            return None, ProofObject(
                rule="ConsentGrant",
                premises=[f"request_id={request_id}"],
                conclusion="failed: request not found"
            )
        
        request = self.requests[request_id]
        
        # Verify granter is the receiver
        if granter_id != request.receiver_id:
            return None, ProofObject(
                rule="ConsentGrant",
                premises=[
                    f"granter={granter_id}",
                    f"receiver={request.receiver_id}",
                ],
                conclusion="failed: granter not authorized"
            )
        
        # Generate grant ID and expiration
        import hashlib
        grant_hash = hashlib.sha256(
            f"grant:{request_id}:{timestamp}".encode()
        ).hexdigest()[:16]
        grant_id = f"CONSENT_GRANT_{grant_hash}"
        
        # Simple expiration calculation (would use proper time math)
        expires_at = f"{timestamp[:-1]}+{(duration_seconds / 3600):.2f}h"
        
        grant = ConsentGrant(
            grant_id=grant_id,
            request_id=request_id,
            granter_id=granter_id,
            grantee_id=request.sender_id,
            scope=scope,
            status=ConsentStatus.GRANTED,
            created_at=timestamp,
            expires_at=expires_at,
        )
        
        self.grants[grant_id] = grant
        
        # Create channel
        channel_id = f"CHAN_{request.sender_id}_{request.receiver_id}"
        channel = ConsentChannel(
            channel_id=channel_id,
            sender_id=request.sender_id,
            receiver_id=request.receiver_id,
            consent_grant=grant,
        )
        self.channels[channel_id] = channel
        
        return grant, grant.proof()
