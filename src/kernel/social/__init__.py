"""Kernel Social Layer — P2P Identity, Consent Communications, Reputation

The social layer provides decentralized social primitives:
- Identity: Cryptographic self-sovereign identity (no centralized auth)
- Consent Communications: Consent-gated messaging with ProofObject witnessing
- Reputation: Decentralized reputation scoring without central authority

Mathematical foundation: Object-capability model + Merkle witnessing.
Biblical: Matthew 18:16 — "Every matter may be established by testimony of two or three witnesses."
"""

from __future__ import annotations

from .identity import (
    IdentityCap,
    IdentityClaim,
    BarExamStatus,
    check_identity_valid,
    delegate_identity,
    verify_identity_chain,
)

from .consent_comms import (
    CommsCap,
    ConsentChannel,
    ConsentStatus,
    send_message,
    receive_message,
    verify_consent,
    check_message_witness,
)

from .reputation import (
    ReputationCap,
    ReputationScore,
    ReputationEvent,
    read_reputation,
    write_reputation,
    aggregate_reputation,
    check_reputation_threshold,
)

__all__ = [
    # Identity
    "IdentityCap",
    "IdentityClaim", 
    "BarExamStatus",
    "check_identity_valid",
    "delegate_identity",
    "verify_identity_chain",
    # Consent Communications
    "CommsCap",
    "ConsentChannel",
    "ConsentStatus",
    "send_message",
    "receive_message",
    "verify_consent",
    "check_message_witness",
    # Reputation
    "ReputationCap",
    "ReputationScore",
    "ReputationEvent",
    "read_reputation",
    "write_reputation",
    "aggregate_reputation",
    "check_reputation_threshold",
]
