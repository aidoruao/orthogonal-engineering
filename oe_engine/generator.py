"""oe_engine.generator — Verification-first response generator.

Composes deterministic responses from domain invariant results.
No stochastic generation: same DomainQuery always yields the same
GeneratedResponse (identical response_hash).

Standard: Template composition — every sentence cites an invariant result.

falsifies_if: same DomainQuery yields different response_hash on two calls.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Dict, List, Tuple

from axioms.logic import ProofObject, merkle_root_over_proofs
from oe_engine.router import RouteResult
from oe_engine.thinker import ThinkerInput, ThinkerModule, ThinkerOutput


@dataclass(frozen=True)
class DomainQuery:
    """A routed query ready for generation.

    falsifies_if: two DomainQuery objects with the same query and route_result
    produce different GeneratedResponse instances.
    """

    query: str
    route_result: RouteResult
    context: Dict[str, Any]


@dataclass(frozen=True)
class GeneratedResponse:
    """A verification-first generated response.

    falsifies_if: response_hash changes without changing text or proof.
    """

    query: DomainQuery
    domain_results: Tuple[ThinkerOutput, ...]
    text: str
    proof: ProofObject
    response_hash: str  # SHA-256(text + "|" + proof.proof_hash)


class DomainGenerator:
    """Verification-first deterministic response generator.

    Loads domain invariant modules, runs invariant checks against the query
    context, and composes a response from a fixed template based on results.

    Pipeline:
      1. Receive DomainQuery with routed domains.
      2. Load and execute invariant checks for each matched domain.
      3. Compose response text from per-domain pass/fail counts.
      4. Build ProofObject (Merkle root over all domain proofs).
      5. Return GeneratedResponse with SHA-256 response_hash.

    falsifies_if: non-determinism (same DomainQuery → different response_hash).
    """

    def __init__(self) -> None:
        self._thinker = ThinkerModule()

    def generate(self, dq: DomainQuery) -> GeneratedResponse:
        """Generate a response from a DomainQuery.

        Standard: Template composition — no stochastic generation.
        falsifies_if: same DomainQuery yields different response_hash.

        Returns:
            GeneratedResponse with text, proof, and response_hash.
        """
        results: List[ThinkerOutput] = []

        # Run invariant checks for each matched domain (up to 5)
        for domain_id in dq.route_result.matched_domains[:5]:
            inp = ThinkerInput(
                query=dq.query,
                domain_id=domain_id,
                context=dq.context,
            )
            out = self._thinker.think(inp)
            results.append(out)

        # Compose text from per-domain invariant results
        if not results:
            text = (
                "No domain match found. Cannot provide a verified response. "
                "Query does not map to any registered invariant domain."
            )
        else:
            lines: List[str] = []
            for out in results:
                total = len(out.proofs)
                passed = sum(
                    1 for p in out.proofs if "FAIL" not in p.conclusion.upper()
                )
                status = "PASS" if out.all_passed else "VIOLATION"
                lines.append(
                    f"Domain {out.domain_id}: {passed}/{total} invariants "
                    f"satisfied [{status}]."
                )
            text = "\n".join(lines)

        # Collect all proofs for Merkle root
        all_proofs: List[ProofObject] = [dq.route_result.proof]
        for out in results:
            all_proofs.extend(out.proofs)

        merkle = merkle_root_over_proofs(all_proofs)

        proof = ProofObject(
            rule="DomainGeneration",
            premises=[
                f"query_hash={dq.route_result.query_hash[:16]}...",
                f"domains={[r.domain_id for r in results]}",
                f"all_passed={all(r.all_passed for r in results)}",
                f"merkle_root={merkle[:16]}...",
            ],
            conclusion=(
                f"Generated response for {len(results)} domain(s)"
                if results
                else "No domain matched — refusal issued"
            ),
        )

        response_hash = hashlib.sha256(
            f"{text}|{proof.proof_hash}".encode("utf-8")
        ).hexdigest()

        return GeneratedResponse(
            query=dq,
            domain_results=tuple(results),
            text=text,
            proof=proof,
            response_hash=response_hash,
        )

    def confidence(self, response: GeneratedResponse) -> Fraction:
        """Compute Fraction confidence from domain results.

        Standard: pass_count / total_proofs across all domains.
        falsifies_if: confidence > 0 when no domains matched.

        Returns:
            Fraction in [0, 1].
        """
        if not response.domain_results:
            return Fraction(0)

        all_proofs: List[ProofObject] = []
        for out in response.domain_results:
            all_proofs.extend(out.proofs)

        if not all_proofs:
            return Fraction(0)

        passed = sum(
            1 for p in all_proofs if "FAIL" not in p.conclusion.upper()
        )
        return Fraction(passed, len(all_proofs))
