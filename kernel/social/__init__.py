#!/usr/bin/env python3
"""
Kernel Social Layer — P2P Identity, Consent Communications, and Reputation

Implements the social substrate for the Yeshua Commonwealth:
- Identity: Self-sovereign, capability-gated identity
- Consent Communications: All communication requires explicit consent
- Reputation: Decentralized reputation without centralized authority

Mathematical Foundation:
  - axioms/cryptographic_verification.py for identity proofs
  - axioms/game_theory.py for reputation dynamics
  - axioms/epistemic_logic.py for knowledge and belief

Biblical: Matthew 18:16 — "By the testimony of two or three witnesses..."
"""

from .identity import Identity, IdentityCap, IdentityRegistry
from .consent_comms import ConsentChannel, ConsentRequest, ConsentGrant
from .reputation import ReputationScore, ReputationWitness, ReputationLedger

__all__ = [
    # Identity
    "Identity",
    "IdentityCap",
    "IdentityRegistry",
    # Consent Communications
    "ConsentChannel",
    "ConsentRequest",
    "ConsentGrant",
    # Reputation
    "ReputationScore",
    "ReputationWitness",
    "ReputationLedger",
]
