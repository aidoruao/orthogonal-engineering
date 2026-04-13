"""oe_engine.conversation — Stateful multi-turn conversation engine.

Implements append-only ConversationState with per-turn cryptographic hashing
and context-based domain relevance boosting from prior turns.

Each turn is immutable after creation. State is updated by appending; prior
state is never mutated. The state_hash is a SHA-256 over all turn_hash values
in order.

Standard: Deterministic pipeline — route → generate → append.

falsifies_if: state_hash changes without appending a new turn.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Dict, List, Tuple

from axioms.logic import ProofObject, merkle_root_over_proofs
from oe_engine.router import DomainRouter
from oe_engine.generator import DomainGenerator, DomainQuery, GeneratedResponse


@dataclass(frozen=True)
class ConversationTurn:
    """A single immutable turn in a conversation.

    falsifies_if: turn_hash changes without changing turn_number, query, or
    response.response_hash.
    """

    turn_number: int
    query: str
    response: GeneratedResponse
    turn_hash: str  # SHA-256(turn_number + "|" + query + "|" + response_hash)


@dataclass(frozen=True)
class ConversationState:
    """Immutable append-only conversation state.

    falsifies_if: state_hash does not match SHA-256 over all turn_hash values.
    """

    turns: Tuple[ConversationTurn, ...]
    state_hash: str  # SHA-256("|".join(t.turn_hash for t in turns))


def _empty_state_hash() -> str:
    """Canonical hash for an empty conversation.

    falsifies_if: returns different value on two calls.
    """
    return hashlib.sha256(b"EMPTY_CONVERSATION").hexdigest()


def _compute_state_hash(turns: Tuple[ConversationTurn, ...]) -> str:
    """Compute SHA-256 over ordered turn hashes.

    Standard: deterministic ordering preserved by tuple order.
    falsifies_if: same turns in same order yields different hash.
    """
    if not turns:
        return _empty_state_hash()
    return hashlib.sha256(
        "|".join(t.turn_hash for t in turns).encode("utf-8")
    ).hexdigest()


class ConversationEngine:
    """Stateful multi-turn conversation engine.

    Each call to process_turn():
      1. Builds a context dict with domain relevance boosts from prior turns.
      2. Routes the input via DomainRouter.
      3. Generates a response via DomainGenerator.
      4. Wraps the response in an immutable ConversationTurn.
      5. Returns the updated ConversationState (append-only).

    The context boost applies Fraction decay so more-recent turns carry higher
    domain relevance (weight = (i+1) / (total_turns+1)).

    falsifies_if: same sequence of inputs yields different state_hash.
    """

    def __init__(self) -> None:
        self._router = DomainRouter()
        self._generator = DomainGenerator()
        self._state = ConversationState(
            turns=(),
            state_hash=_empty_state_hash(),
        )

    @property
    def state(self) -> ConversationState:
        """Return current (immutable) conversation state.

        falsifies_if: state mutates between calls without process_turn().
        """
        return self._state

    def process_turn(self, query: str) -> Tuple[str, ConversationState]:
        """Process a new conversation turn.

        Standard: route → generate → append-only state update.
        falsifies_if: same sequence of queries yields different state_hash.

        Returns:
            Tuple of (response_text, new_state).
        """
        # Build context with domain boosts from prior turns
        context = self._build_context()

        # Route the query
        route_result = self._router.route(query)

        # Generate response
        dq = DomainQuery(
            query=query,
            route_result=route_result,
            context=context,
        )
        response = self._generator.generate(dq)

        # Build immutable turn
        turn_number = len(self._state.turns)
        turn_hash = hashlib.sha256(
            f"{turn_number}|{query}|{response.response_hash}".encode("utf-8")
        ).hexdigest()
        turn = ConversationTurn(
            turn_number=turn_number,
            query=query,
            response=response,
            turn_hash=turn_hash,
        )

        # Append to state (old state never mutated)
        new_turns = self._state.turns + (turn,)
        new_state = ConversationState(
            turns=new_turns,
            state_hash=_compute_state_hash(new_turns),
        )
        self._state = new_state

        return response.text, new_state

    def _build_context(self) -> Dict[str, Any]:
        """Build context dict from prior turns with Fraction-based decay.

        More-recent turns receive higher weight: weight_i = (i+1)/(total+1).
        Accumulated boosts are serialised as strings for the context dict.

        falsifies_if: same turns yield different context dict.
        """
        if not self._state.turns:
            return {}

        total = len(self._state.turns)
        domain_boosts: Dict[str, Fraction] = {}

        for i, turn in enumerate(self._state.turns):
            weight = Fraction(i + 1, total + 1)
            for domain_id in turn.response.query.route_result.matched_domains:
                existing = domain_boosts.get(domain_id, Fraction(0))
                domain_boosts[domain_id] = existing + weight

        return {
            "domain_boosts": {k: str(v) for k, v in domain_boosts.items()}
        }

    def export_transcript(self) -> Dict[str, Any]:
        """Export the full conversation transcript with Merkle proof.

        Collects all ProofObjects from every turn's domain results and
        computes a Merkle root for cryptographic integrity verification.

        falsifies_if: same state yields different merkle_root.

        Returns:
            Dict with keys: turns, state_hash, merkle_root.
        """
        all_proofs: List[ProofObject] = []
        for turn in self._state.turns:
            all_proofs.append(turn.response.proof)
            for domain_out in turn.response.domain_results:
                all_proofs.extend(domain_out.proofs)

        merkle = (
            merkle_root_over_proofs(all_proofs)
            if all_proofs
            else hashlib.sha256(b"EMPTY").hexdigest()
        )

        return {
            "turns": [
                {
                    "turn_number": t.turn_number,
                    "query": t.query,
                    "response": t.response.text,
                    "turn_hash": t.turn_hash,
                }
                for t in self._state.turns
            ],
            "state_hash": self._state.state_hash,
            "merkle_root": merkle,
        }
