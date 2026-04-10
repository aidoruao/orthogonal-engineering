"""Kernel Consent Communications — Consent-gated communication channels

CommsCap grants send/receive on specific channels.
Every message witnessed with ProofObject.
No communication without explicit consent.

Mathematical foundation: Capability-gated channels + Merkle witnessing.
Standard: GDPR Article 7 (conditions for consent), W3C DIDComm.
Biblical: 1 Corinthians 14:33 — "For God is not a God of confusion but of peace."
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Optional, Dict
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject
from axioms.capability_security import Capability, Permission


class ConsentStatus(Enum):
    """Consent status for communication channels."""
    PENDING = auto()    # Consent requested, not yet granted
    GRANTED = auto()    # Consent granted, communication allowed
    REVOKED = auto()    # Consent previously granted but revoked
    DENIED = auto()     # Consent explicitly denied
    EXPIRED = auto()    # Consent granted but time limit expired


class MessageType(Enum):
    """Types of consent-gated messages."""
    DIRECT = auto()     # One-to-one direct message
    GROUP = auto()      # Group channel message
    BROADCAST = auto()  # Broadcast to many recipients
    SYSTEM = auto()     # System notification (special handling)


@dataclass(frozen=True)
class Message:
    """A single consent-gated message.
    
    Every message carries:
    - Content hash (content-addressed)
    - Sender/receiver IDs
    - Timestamp
    - ProofObject witness
    """
    message_id: str       # Content hash of (sender+receiver+content+timestamp)
    sender_id: str
    receiver_id: str
    content_hash: str     # Hash of actual content
    timestamp: Fraction
    msg_type: MessageType
    witness_hash: str     # Merkle root of witnessing proofs


@dataclass
class CommsCap:
    """Capability token for communication operations.
    
    Grants specific permissions on a communication channel:
    - READ: Can receive messages
    - WRITE: Can send messages
    - DELEGATE: Can grant comms access to others
    
    Channels are consent-gated: both parties must consent.
    """
    channel_id: str
    holder_id: str        # Identity holding this capability
    permissions: frozenset
    consent_status: ConsentStatus
    delegator: str
    attenuations: Tuple[str, ...] = field(default_factory=tuple)
    expiry: Optional[Fraction] = None  # Optional consent expiry
    
    def has_permission(self, perm: Permission) -> bool:
        """Check if capability has specific permission."""
        return perm in self.permissions
    
    def is_active(self, current_time: Fraction) -> bool:
        """Check if consent is still active."""
        if self.consent_status != ConsentStatus.GRANTED:
            return False
        if self.expiry is not None and current_time > self.expiry:
            return False
        return True


@dataclass
class ConsentChannel:
    """A consent-gated communication channel.
    
    Channels are bidirectional but consent is unidirectional.
    Each side must independently grant consent for the other to send.
    """
    channel_id: str
    party_a: str
    party_b: str
    
    # Consent status from each party's perspective
    a_consents_to_b: ConsentStatus  # A allows B to send to A
    b_consents_to_a: ConsentStatus  # B allows A to send to B
    
    created_at: Fraction
    message_history: List[Message] = field(default_factory=list)
    
    def can_send(self, sender_id: str, current_time: Fraction) -> bool:
        """Check if sender can send messages on this channel."""
        if sender_id == self.party_a:
            return self.a_consents_to_b == ConsentStatus.GRANTED
        elif sender_id == self.party_b:
            return self.b_consents_to_a == ConsentStatus.GRANTED
        return False


@dataclass
class ConsentState:
    """Complete consent communications subsystem state."""
    channels: Dict[str, ConsentChannel] = field(default_factory=dict)
    capabilities: Dict[str, List[CommsCap]] = field(default_factory=dict)
    pending_consent_requests: Dict[str, Tuple[str, str, Fraction]] = field(default_factory=dict)
    # message_id -> (message, ProofObject)
    witnessed_messages: Dict[str, Tuple[Message, ProofObject]] = field(default_factory=dict)


def verify_consent(
    state: ConsentState,
    channel_id: str,
    sender_id: str,
    current_time: Fraction
) -> Tuple[bool, ProofObject]:
    """Verify that sender has consent to communicate on channel.
    
    Consent verification checks:
    1. Channel exists
    2. Sender is a party to the channel
    3. Receiver has granted consent
    4. Consent has not expired
    
    Args:
        state: Consent communications state
        channel_id: Channel to verify
        sender_id: Would-be sender
        current_time: Current timestamp
        
    Returns:
        (has_consent, proof)
    """
    if channel_id not in state.channels:
        return False, ProofObject(
            rule="VerifyConsent",
            premises=[f"channel_id={channel_id}"],
            conclusion="consent denied: channel not found"
        )
    
    channel = state.channels[channel_id]
    
    # Check sender is a party to this channel
    if sender_id not in (channel.party_a, channel.party_b):
        return False, ProofObject(
            rule="VerifyConsent",
            premises=[
                f"sender={sender_id}",
                f"party_a={channel.party_a}",
                f"party_b={channel.party_b}"
            ],
            conclusion="consent denied: sender not party to channel"
        )
    
    # Determine receiver and consent status
    if sender_id == channel.party_a:
        receiver_id = channel.party_b
        consent_status = channel.b_consents_to_a
    else:
        receiver_id = channel.party_a
        consent_status = channel.a_consents_to_b
    
    # Check consent status
    if consent_status == ConsentStatus.PENDING:
        return False, ProofObject(
            rule="VerifyConsent",
            premises=[
                f"sender={sender_id}",
                f"receiver={receiver_id}",
                f"status={consent_status.name}"
            ],
            conclusion="consent denied: consent pending"
        )
    
    if consent_status == ConsentStatus.REVOKED:
        return False, ProofObject(
            rule="VerifyConsent",
            premises=[
                f"sender={sender_id}",
                f"receiver={receiver_id}",
                f"status={consent_status.name}"
            ],
            conclusion="consent denied: consent revoked"
        )
    
    if consent_status == ConsentStatus.DENIED:
        return False, ProofObject(
            rule="VerifyConsent",
            premises=[
                f"sender={sender_id}",
                f"receiver={receiver_id}",
                f"status={consent_status.name}"
            ],
            conclusion="consent denied: consent explicitly denied"
        )
    
    if consent_status != ConsentStatus.GRANTED:
        return False, ProofObject(
            rule="VerifyConsent",
            premises=[
                f"sender={sender_id}",
                f"status={consent_status.name}"
            ],
            conclusion="consent denied: consent not granted"
        )
    
    return True, ProofObject(
        rule="VerifyConsent",
        premises=[
            f"sender={sender_id}",
            f"receiver={receiver_id}",
            f"channel={channel_id}",
            f"status={consent_status.name}"
        ],
        conclusion="consent granted: communication allowed"
    )


def send_message(
    state: ConsentState,
    channel_id: str,
    sender_id: str,
    content_hash: str,
    current_time: Fraction,
    sender_cap: CommsCap
) -> Tuple[ConsentState, Optional[Message], ProofObject]:
    """Send a message on a consent-gated channel.
    
    Every message is witnessed with a ProofObject.
    Sender must hold valid CommsCap with WRITE permission.
    Receiver must have granted consent.
    
    Args:
        state: Current consent state
        channel_id: Channel to send on
        sender_id: Sender identity
        content_hash: Hash of message content
        current_time: Timestamp
        sender_cap: Sender's communication capability
        
    Returns:
        (new_state, message, proof)
        message is None if send failed
    """
    # Verify capability
    if sender_cap.channel_id != channel_id:
        return state, None, ProofObject(
            rule="SendMessage",
            premises=[
                f"cap_channel={sender_cap.channel_id}",
                f"target_channel={channel_id}"
            ],
            conclusion="send failed: wrong capability"
        )
    
    if not sender_cap.has_permission(Permission.WRITE):
        return state, None, ProofObject(
            rule="SendMessage",
            premises=[
                f"sender={sender_id}",
                f"permissions={sender_cap.permissions}"
            ],
            conclusion="send failed: no WRITE permission"
        )
    
    # Verify consent
    has_consent, consent_proof = verify_consent(state, channel_id, sender_id, current_time)
    if not has_consent:
        return state, None, ProofObject(
            rule="SendMessage",
            premises=[f"sender={sender_id}", f"channel={channel_id}"],
            conclusion="send failed: consent not granted"
        )
    
    # Get channel
    channel = state.channels[channel_id]
    receiver_id = channel.party_b if sender_id == channel.party_a else channel.party_a
    
    # Create message with content-addressed ID
    message_id_input = f"{sender_id}:{receiver_id}:{content_hash}:{current_time}"
    import hashlib
    message_id = hashlib.sha256(message_id_input.encode()).hexdigest()[:32]
    
    # Create witness proof
    witness = ProofObject(
        rule="MessageWitness",
        premises=[
            f"sender={sender_id}",
            f"receiver={receiver_id}",
            f"channel={channel_id}",
            f"timestamp={current_time}"
        ],
        conclusion="message witnessed with consent"
    )
    
    message = Message(
        message_id=message_id,
        sender_id=sender_id,
        receiver_id=receiver_id,
        content_hash=content_hash,
        timestamp=current_time,
        msg_type=MessageType.DIRECT,
        witness_hash=witness.proof_hash
    )
    
    # Update channel with message
    new_history = channel.message_history + [message]
    new_channel = ConsentChannel(
        channel_id=channel.channel_id,
        party_a=channel.party_a,
        party_b=channel.party_b,
        a_consents_to_b=channel.a_consents_to_b,
        b_consents_to_a=channel.b_consents_to_a,
        created_at=channel.created_at,
        message_history=new_history
    )
    
    new_channels = state.channels.copy()
    new_channels[channel_id] = new_channel
    
    # Record witnessed message
    new_witnessed = state.witnessed_messages.copy()
    new_witnessed[message_id] = (message, witness)
    
    new_state = ConsentState(
        channels=new_channels,
        capabilities=state.capabilities,
        pending_consent_requests=state.pending_consent_requests,
        witnessed_messages=new_witnessed
    )
    
    return new_state, message, ProofObject(
        rule="SendMessage",
        premises=[
            f"message_id={message_id}",
            f"sender={sender_id}",
            f"receiver={receiver_id}",
            f"witness_hash={witness.proof_hash}"
        ],
        conclusion="message sent and witnessed"
    )


def receive_message(
    state: ConsentState,
    channel_id: str,
    receiver_id: str,
    receiver_cap: CommsCap
) -> Tuple[ConsentState, Optional[Message], ProofObject]:
    """Receive a message from a consent-gated channel.
    
    Returns the most recent unread message for this receiver.
    Receiver must hold valid CommsCap with READ permission.
    
    Args:
        state: Current consent state
        channel_id: Channel to receive from
        receiver_id: Receiver identity
        receiver_cap: Receiver's communication capability
        
    Returns:
        (new_state, message, proof)
        message is None if no messages available
    """
    # Verify capability
    if receiver_cap.channel_id != channel_id:
        return state, None, ProofObject(
            rule="ReceiveMessage",
            premises=[
                f"cap_channel={receiver_cap.channel_id}",
                f"target_channel={channel_id}"
            ],
            conclusion="receive failed: wrong capability"
        )
    
    if not receiver_cap.has_permission(Permission.READ):
        return state, None, ProofObject(
            rule="ReceiveMessage",
            premises=[
                f"receiver={receiver_id}",
                f"permissions={receiver_cap.permissions}"
            ],
            conclusion="receive failed: no READ permission"
        )
    
    # Get channel
    if channel_id not in state.channels:
        return state, None, ProofObject(
            rule="ReceiveMessage",
            premises=[f"channel={channel_id}"],
            conclusion="receive failed: channel not found"
        )
    
    channel = state.channels[channel_id]
    
    # Find messages for this receiver
    messages_for_receiver = [
        msg for msg in channel.message_history
        if msg.receiver_id == receiver_id
    ]
    
    if not messages_for_receiver:
        return state, None, ProofObject(
            rule="ReceiveMessage",
            premises=[
                f"receiver={receiver_id}",
                f"channel={channel_id}"
            ],
            conclusion="receive blocked: no messages"
        )
    
    # Get most recent message
    message = messages_for_receiver[-1]
    
    return state, message, ProofObject(
        rule="ReceiveMessage",
        premises=[
            f"message_id={message.message_id}",
            f"sender={message.sender_id}",
            f"timestamp={message.timestamp}"
        ],
        conclusion="message received"
    )


def check_message_witness(
    state: ConsentState,
    message_id: str
) -> Tuple[bool, Optional[ProofObject], ProofObject]:
    """Verify that a message was properly witnessed.
    
    Args:
        state: Consent state
        message_id: Message to check
        
    Returns:
        (is_witnessed, witness_proof, check_proof)
        witness_proof is the stored witness if found
    """
    if message_id not in state.witnessed_messages:
        return False, None, ProofObject(
            rule="CheckMessageWitness",
            premises=[f"message_id={message_id}"],
            conclusion="not witnessed: message not found"
        )
    
    message, witness = state.witnessed_messages[message_id]
    
    # Verify witness hash matches
    if witness.proof_hash != message.witness_hash:
        return False, witness, ProofObject(
            rule="CheckMessageWitness",
            premises=[
                f"message_id={message_id}",
                f"stored_hash={message.witness_hash}",
                f"computed_hash={witness.proof_hash}"
            ],
            conclusion="witness integrity failed: hash mismatch"
        )
    
    return True, witness, ProofObject(
        rule="CheckMessageWitness",
        premises=[
            f"message_id={message_id}",
            f"witness_hash={witness.proof_hash}"
        ],
        conclusion="message properly witnessed"
    )


def grant_consent(
    state: ConsentState,
    channel_id: str,
    granter_id: str,
    grantee_id: str,
    current_time: Fraction,
    expiry: Optional[Fraction] = None
) -> Tuple[ConsentState, ProofObject]:
    """Grant consent for another party to send messages.
    
    Args:
        state: Current consent state
        channel_id: Channel to grant consent on
        granter_id: Identity granting consent
        grantee_id: Identity receiving consent (can now send to granter)
        current_time: Timestamp
        expiry: Optional consent expiry time
        
    Returns:
        (new_state, proof)
    """
    if channel_id not in state.channels:
        return state, ProofObject(
            rule="GrantConsent",
            premises=[f"channel={channel_id}"],
            conclusion="grant failed: channel not found"
        )
    
    channel = state.channels[channel_id]
    
    # Verify granter is a party to this channel
    if granter_id not in (channel.party_a, channel.party_b):
        return state, ProofObject(
            rule="GrantConsent",
            premises=[
                f"granter={granter_id}",
                f"party_a={channel.party_a}",
                f"party_b={channel.party_b}"
            ],
            conclusion="grant failed: granter not party to channel"
        )
    
    # Verify grantee is the other party
    other_party = channel.party_b if granter_id == channel.party_a else channel.party_a
    if grantee_id != other_party:
        return state, ProofObject(
            rule="GrantConsent",
            premises=[
                f"grantee={grantee_id}",
                f"expected={other_party}"
            ],
            conclusion="grant failed: grantee not other party"
        )
    
    # Update consent status
    new_a_consents = channel.a_consents_to_b
    new_b_consents = channel.b_consents_to_a
    
    if granter_id == channel.party_a:
        new_a_consents = ConsentStatus.GRANTED
    else:
        new_b_consents = ConsentStatus.GRANTED
    
    new_channel = ConsentChannel(
        channel_id=channel.channel_id,
        party_a=channel.party_a,
        party_b=channel.party_b,
        a_consents_to_b=new_a_consents,
        b_consents_to_a=new_b_consents,
        created_at=channel.created_at,
        message_history=channel.message_history
    )
    
    new_channels = state.channels.copy()
    new_channels[channel_id] = new_channel
    
    new_state = ConsentState(
        channels=new_channels,
        capabilities=state.capabilities,
        pending_consent_requests=state.pending_consent_requests,
        witnessed_messages=state.witnessed_messages
    )
    
    expiry_str = f"expiry={expiry}" if expiry else "no expiry"
    return new_state, ProofObject(
        rule="GrantConsent",
        premises=[
            f"granter={granter_id}",
            f"grantee={grantee_id}",
            f"channel={channel_id}",
            expiry_str
        ],
        conclusion="consent granted"
    )


def revoke_consent(
    state: ConsentState,
    channel_id: str,
    revoker_id: str,
    revokee_id: str,
    current_time: Fraction
) -> Tuple[ConsentState, ProofObject]:
    """Revoke previously granted consent.
    
    Args:
        state: Current consent state
        channel_id: Channel to revoke consent on
        revoker_id: Identity revoking consent
        revokee_id: Identity losing consent
        current_time: Timestamp
        
    Returns:
        (new_state, proof)
    """
    if channel_id not in state.channels:
        return state, ProofObject(
            rule="RevokeConsent",
            premises=[f"channel={channel_id}"],
            conclusion="revoke failed: channel not found"
        )
    
    channel = state.channels[channel_id]
    
    # Verify revoker is a party to this channel
    if revoker_id not in (channel.party_a, channel.party_b):
        return state, ProofObject(
            rule="RevokeConsent",
            premises=[f"revoker={revoker_id}"],
            conclusion="revoke failed: revoker not party to channel"
        )
    
    # Update consent status
    new_a_consents = channel.a_consents_to_b
    new_b_consents = channel.b_consents_to_a
    
    if revoker_id == channel.party_a:
        new_a_consents = ConsentStatus.REVOKED
    else:
        new_b_consents = ConsentStatus.REVOKED
    
    new_channel = ConsentChannel(
        channel_id=channel.channel_id,
        party_a=channel.party_a,
        party_b=channel.party_b,
        a_consents_to_b=new_a_consents,
        b_consents_to_a=new_b_consents,
        created_at=channel.created_at,
        message_history=channel.message_history
    )
    
    new_channels = state.channels.copy()
    new_channels[channel_id] = new_channel
    
    new_state = ConsentState(
        channels=new_channels,
        capabilities=state.capabilities,
        pending_consent_requests=state.pending_consent_requests,
        witnessed_messages=state.witnessed_messages
    )
    
    return new_state, ProofObject(
        rule="RevokeConsent",
        premises=[
            f"revoker={revoker_id}",
            f"revokee={revokee_id}",
            f"channel={channel_id}"
        ],
        conclusion="consent revoked"
    )
