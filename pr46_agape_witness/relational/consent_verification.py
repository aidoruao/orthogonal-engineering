# pr46_agape_witness/relational/consent_verification.py
# PR #46 — Agape Witness Layer (AWL)
# Standard: Yeshua
#
# Consent verification: verify that a given set of parties have all
# explicitly consented before proceeding with a sensitive operation.

from __future__ import annotations

from typing import Dict, List

from pr46_agape_witness.util.hashing import sha256_hash


def verify_all_consent(
    required_parties: List[str],
    consents: Dict[str, bool],
) -> bool:
    """
    Verify that every required party has consented (consents[party] == True).

    Parameters:
      required_parties — list of party identifiers that must consent.
      consents         — mapping of party_id → bool consent flag.

    Returns True if all required parties have consented.
    Raises ValueError listing the non-consenting or missing parties.
    """
    missing = [p for p in required_parties if not consents.get(p, False)]
    if missing:
        raise ValueError(
            f"Consent required but not given by parties: {sorted(missing)}"
        )
    return True


def consent_record_hash(party_id: str, consents: bool, timestamp: str) -> str:
    """Return a deterministic hash of a single consent record."""
    return sha256_hash({
        "consents": consents,
        "party_id": party_id,
        "timestamp": timestamp,
    })
