# pr46_agape_witness/invariants/forgiveness_auditable.py
# PR #46 — Agape Witness Layer (AWL)
# Standard: Yeshua
#
# ForgivenessAuditable invariant: every forgiveness operation must
# leave verifiable, append-only witness evidence.

from __future__ import annotations

from pr46_agape_witness.forgiveness.justification_witness import JustificationWitnessChain


def check_forgiveness_auditable(
    witness_chain: JustificationWitnessChain,
    expected_forgiveness_count: int,
) -> bool:
    """
    ForgivenessAuditable invariant: the justification witness chain must
    contain at least expected_forgiveness_count entries, and its integrity
    must be verifiable.

    Raises ValueError if the chain is shorter than expected or integrity fails.
    Returns True on success.
    """
    if witness_chain.length < expected_forgiveness_count:
        raise ValueError(
            f"ForgivenessAuditable: witness chain has {witness_chain.length} entries "
            f"but {expected_forgiveness_count} forgiveness operations were expected"
        )
    witness_chain.verify_integrity()
    return True
