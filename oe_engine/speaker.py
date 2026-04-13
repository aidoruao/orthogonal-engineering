"""oe_engine.speaker — Natural language response generator for the OE Engine.

Formats ProofObject chains into readable natural language responses.
All responses are deterministic (same proofs → same text → same hash).

falsifies_if: same thinker_proofs yields different speaker_hash on two calls.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from fractions import Fraction
from typing import List, Optional, Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class SpeakerOutput:
    """Output from the speaker module.

    falsifies_if: speaker_hash changes without changing proofs or query.
    """

    query: str
    text: str
    confidence: Fraction
    speaker_hash: str         # SHA-256 of text + confidence + all proof hashes
    proof_chain: Tuple[ProofObject, ...]


class SpeakerModule:
    """Deterministic proof-to-language formatter.

    Converts a list of ProofObjects into a natural language response.
    No LLM, no sampling — pure deterministic template formatting.

    falsifies_if: non-determinism (same input → different text on two calls).
    """

    def speak(
        self,
        query: str,
        thinker_proofs: List[ProofObject],
        confidence: Fraction,
    ) -> SpeakerOutput:
        """Format proofs into a natural language response.

        Standard: Deterministic template formatting
        falsifies_if: confidence > 0 but no proofs present

        Returns:
            SpeakerOutput with text, confidence, speaker_hash, proof_chain
        """
        if not thinker_proofs:
            text = (
                "No domain match found. Cannot provide a verified response. "
                "Query does not map to any registered invariant domain."
            )
            confidence = Fraction(0)
        else:
            lines: List[str] = []
            pass_count = sum(
                1 for p in thinker_proofs if "FAIL" not in p.conclusion.upper()
            )
            fail_count = len(thinker_proofs) - pass_count

            if fail_count == 0:
                lines.append(
                    f"All {pass_count} invariant check(s) passed for your query."
                )
            else:
                lines.append(
                    f"{pass_count} check(s) passed, {fail_count} VIOLATION(s) detected."
                )

            # Include conclusion of each proof
            for proof in thinker_proofs:
                lines.append(f"  [{proof.rule}]: {proof.conclusion}")

            text = "\n".join(lines)

        # Deterministic hash: SHA-256 of text + confidence + proof hashes
        proof_hash_concat = "|".join(
            p.proof_hash for p in thinker_proofs
        )
        speaker_hash = hashlib.sha256(
            f"{query}|{text}|{confidence}|{proof_hash_concat}".encode()
        ).hexdigest()

        return SpeakerOutput(
            query=query,
            text=text,
            confidence=confidence,
            speaker_hash=speaker_hash,
            proof_chain=tuple(thinker_proofs),
        )
