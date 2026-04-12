"""oe_engine.engine — Main pipeline for the OE Engine.

Wires manifest, router, thinker, and speaker into a single deterministic
query pipeline. Every response includes a cryptographic proof chain.

falsifies_if: same query + context produces different EngineResponse.speaker_hash.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple

from axioms.logic import ProofObject
from oe_engine.manifest import EngineManifest
from oe_engine.router import DomainRouter, RouteResult
from oe_engine.thinker import ThinkerInput, ThinkerModule, ThinkerOutput
from oe_engine.speaker import SpeakerModule, SpeakerOutput


@dataclass(frozen=True)
class EngineResponse:
    """Final response from the OrthogonalEngine.

    falsifies_if: thinker_hash or speaker_hash changes for identical inputs.
    """

    query: str
    text: str
    confidence: Fraction
    thinker_hash: str     # combined hash of all thinker outputs
    speaker_hash: str     # from SpeakerOutput
    proof_chain: Tuple[ProofObject, ...]
    route_result: RouteResult


class OrthogonalEngine:
    """Deterministic invariant-locked inference engine.

    Pipeline:
      1. Manifest load (domain hash registry)
      2. Router (query → matched domains)
      3. Thinker (domain invariant execution per matched domain)
      4. Speaker (proofs → natural language)

    No neural networks. No sampling. No randomness.
    Every output is hash-anchored and reproducible.

    falsifies_if: non-determinism introduced anywhere in the pipeline.
    """

    def __init__(self) -> None:
        self._manifest = EngineManifest()
        self._router = DomainRouter()
        self._thinker = ThinkerModule()
        self._speaker = SpeakerModule()

    def query(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> EngineResponse:
        """Execute a query through the full pipeline.

        Standard: Deterministic pipeline — Manifest → Router → Thinker → Speaker
        falsifies_if: same text + context yields different speaker_hash

        Returns:
            EngineResponse with text, confidence, proof_chain
        """
        if context is None:
            context = {}

        # Step 1: Route
        route_result = self._router.route(text)

        all_proofs: List[ProofObject] = [route_result.proof]
        thinker_hashes: List[str] = []
        all_passed = True

        # Step 2: Think — run thinker for each matched domain
        for domain_id in route_result.matched_domains[:3]:  # top-3 domains max
            inp = ThinkerInput(
                query=text,
                domain_id=domain_id,
                context=context,
            )
            thinker_out = self._thinker.think(inp)
            all_proofs.extend(thinker_out.proofs)
            thinker_hashes.append(thinker_out.thinker_hash)
            if not thinker_out.all_passed:
                all_passed = False

        # Compute combined thinker hash
        combined_thinker_hash = hashlib.sha256(
            "|".join(thinker_hashes).encode()
        ).hexdigest()

        # Step 3: Compute confidence
        if not route_result.matched_domains:
            confidence = Fraction(0)
        elif all_passed:
            confidence = Fraction(1)
        else:
            # Proportion of proofs that passed
            pass_count = sum(
                1 for p in all_proofs if "FAIL" not in p.conclusion.upper()
            )
            total = len(all_proofs)
            confidence = Fraction(pass_count, total) if total > 0 else Fraction(0)

        # Step 4: Speak
        speaker_out = self._speaker.speak(
            query=text,
            thinker_proofs=all_proofs,
            confidence=confidence,
        )

        return EngineResponse(
            query=text,
            text=speaker_out.text,
            confidence=confidence,
            thinker_hash=combined_thinker_hash,
            speaker_hash=speaker_out.speaker_hash,
            proof_chain=tuple(all_proofs),
            route_result=route_result,
        )
