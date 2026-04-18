#!/usr/bin/env python3
"""tools/question_router.py — Master Questioner inquiry decomposition and routing.

Implements SubQuestion and InquiryDecomposition dataclasses plus invariant
checks for the Master Questioner meta-layer (Agent #14).

Usage:
    python tools/question_router.py --demo "What is the Nash equilibrium of a two-domain invariant conflict?"

Standard: Yeshua / Orthogonal Engineering
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(REPO_ROOT))

from axioms.logic import ProofObject  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_REASONING_TYPES: frozenset[str] = frozenset(
    {"epistemic", "strategic", "systemic", "pedagogical"}
)

VALID_SYNTHESIS_STRATEGIES: frozenset[str] = frozenset(
    {"consensus", "weighted", "adversarial", "dialectical"}
)

# Keyword markers used by _detect_reasoning_types()
_EPISTEMIC_MARKERS: tuple[str, ...] = (
    "what is", "how do we know", "is it true", "what are",
    "does", "which", "when", "where", "who", "why",
)
_STRATEGIC_MARKERS: tuple[str, ...] = (
    "should", "recommend", "prioritize", "best", "optimal",
    "trade-off", "approach", "strategy", "decide",
)
_SYSTEMIC_MARKERS: tuple[str, ...] = (
    "how do", "interact", "failure mode", "what happens when",
    "coupling", "integration", "emergent", "conflict",
)
_PEDAGOGICAL_MARKERS: tuple[str, ...] = (
    "explain", "teach", "summarize", "summarise", "quiz",
    "onboarding", "example", "exercise", "demonstrate",
)

# Routing table: reasoning_type -> agent_name
ROUTING_TABLE: dict[str, str] = {
    "epistemic":   "gemini",
    "strategic":   "devin",
    "systemic":    "kimi",
    "pedagogical": "notebooklm",
}

# Approximate token cost per character (4 chars ≈ 1 token)
_CHARS_PER_TOKEN: Fraction = Fraction(4)


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SubQuestion:
    """One routable sub-question produced by decompose_query().

    Attributes:
        question_id:    Unique identifier within the decomposition (e.g. "SQ-001").
        text:           The verbatim sub-question text.
        reasoning_type: One of "epistemic" | "strategic" | "systemic" | "pedagogical".
        assigned_agent: Agent name from the routing table.
        domain_ids:     Domain package names from src/domains/ taxonomy.
    """

    question_id: str
    text: str
    reasoning_type: str
    assigned_agent: str
    domain_ids: List[str]


@dataclass(frozen=True)
class InquiryDecomposition:
    """Full decomposition of an original query into routable sub-questions.

    Attributes:
        original_query:     The verbatim query received by the Master Questioner.
        sub_questions:      Ordered tuple of SubQuestion records.
        synthesis_strategy: One of "consensus" | "weighted" | "adversarial" | "dialectical".
        estimated_tokens:   Fraction estimate of total token cost (4 chars/token heuristic).
    """

    original_query: str
    sub_questions: Tuple[SubQuestion, ...]
    synthesis_strategy: str
    estimated_tokens: Fraction


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _detect_reasoning_types(text: str) -> List[str]:
    """Return the reasoning types detected in text, in priority order.

    Falsifies if: a detected type is not in VALID_REASONING_TYPES.
    falsifies_if: a detected type is not in VALID_REASONING_TYPES.
    """
    lower = text.lower()
    found: List[str] = []

    if any(m in lower for m in _EPISTEMIC_MARKERS):
        found.append("epistemic")
    if any(m in lower for m in _STRATEGIC_MARKERS):
        found.append("strategic")
    if any(m in lower for m in _SYSTEMIC_MARKERS):
        found.append("systemic")
    if any(m in lower for m in _PEDAGOGICAL_MARKERS):
        found.append("pedagogical")

    if not found:
        found.append("epistemic")

    return found


def _infer_domain_ids(text: str) -> List[str]:
    """Infer candidate domain IDs from the query text.

    Scans for known domain name fragments. Falls back to ["d_axioms"].

    Falsifies if: returns an empty list.
    falsifies_if: returns an empty list.
    """
    domains_dir = REPO_ROOT / "src" / "domains"
    found: List[str] = []
    lower = text.lower()
    if domains_dir.exists():
        for p in sorted(domains_dir.iterdir()):
            if p.is_dir() and p.name.startswith("d_"):
                fragment = p.name.replace("d_", "").replace("_", " ")
                if fragment and fragment in lower:
                    found.append(p.name)
    if not found:
        found = ["d_axioms"]
    return found


def _select_synthesis_strategy(
    reasoning_types: List[str],
) -> str:
    """Select synthesis strategy based on detected reasoning type diversity.

    Rules:
      - single type -> "consensus"
      - strategic present -> "weighted"
      - systemic + epistemic -> "dialectical"
      - mixed with contradictory potential -> "adversarial"

    Falsifies if: returned strategy is not in VALID_SYNTHESIS_STRATEGIES.
    falsifies_if: returned strategy is not in VALID_SYNTHESIS_STRATEGIES.
    """
    unique = set(reasoning_types)
    if len(unique) == 1:
        return "consensus"
    if "strategic" in unique:
        return "weighted"
    if "systemic" in unique and "epistemic" in unique:
        return "dialectical"
    return "adversarial"


def _estimate_tokens(query: str) -> Fraction:
    """Estimate token cost of a query using 4-chars-per-token heuristic.

    Falsifies if: returns a negative Fraction.
    falsifies_if: returns a negative Fraction.
    """
    return Fraction(len(query)) / _CHARS_PER_TOKEN


# ---------------------------------------------------------------------------
# Public invariant functions
# ---------------------------------------------------------------------------


def decompose_query(query: str) -> Tuple[bool, ProofObject]:
    """Decompose a query into routable sub-questions.

    Returns (True, proof) when at least one sub-question is produced and
    every sub-question's assigned_agent is registered in ROUTING_TABLE.

    Standard: MQ-001 (every decomposition identifies ≥1 reasoning type)
    Falsifies if: any sub-question is assigned an agent not in ROUTING_TABLE,
                  or the query produces zero sub-questions.
    falsifies_if: any sub-question is assigned an agent not in ROUTING_TABLE,
                  or the query produces zero sub-questions.
    """
    if not query or not query.strip():
        return False, ProofObject(
            rule="decompose_query",
            premises=["query is empty"],
            conclusion="VIOLATION: empty query cannot be decomposed",
        )

    reasoning_types = _detect_reasoning_types(query)
    domain_ids = _infer_domain_ids(query)

    if not reasoning_types:
        return False, ProofObject(
            rule="decompose_query",
            premises=[f"query={query!r}"],
            conclusion="VIOLATION: no reasoning type detected — MQ-001 violated",
        )

    for rtype in reasoning_types:
        if rtype not in VALID_REASONING_TYPES:
            return False, ProofObject(
                rule="decompose_query",
                premises=[f"rtype={rtype!r}"],
                conclusion=f"VIOLATION: unknown reasoning type {rtype!r}",
            )
        if rtype not in ROUTING_TABLE:
            return False, ProofObject(
                rule="decompose_query",
                premises=[f"rtype={rtype!r}"],
                conclusion=f"VIOLATION: no route for reasoning type {rtype!r}",
            )

    return True, ProofObject(
        rule="decompose_query",
        premises=[
            f"query_length={len(query)}",
            f"reasoning_types={reasoning_types!r}",
            f"domain_ids={domain_ids!r}",
        ],
        conclusion=(
            f"Decomposition valid: {len(reasoning_types)} sub-question(s) "
            f"covering types {reasoning_types!r}"
        ),
    )


def check_routing_completeness(decomp: InquiryDecomposition) -> Tuple[bool, ProofObject]:
    """Verify every reasoning type present in sub-questions has a routed agent.

    Every reasoning_type in the decomposition must appear in ROUTING_TABLE.

    Standard: MQ-001
    Falsifies if: reasoning_type detected but no sub-question assigned.
    falsifies_if: reasoning_type detected but no sub-question assigned.
    """
    if not decomp.sub_questions:
        return False, ProofObject(
            rule="check_routing_completeness",
            premises=["sub_questions=[]"],
            conclusion="VIOLATION: no sub-questions in decomposition",
        )

    missing: List[str] = []
    for sq in decomp.sub_questions:
        if sq.reasoning_type not in ROUTING_TABLE:
            missing.append(sq.reasoning_type)
        if sq.assigned_agent != ROUTING_TABLE.get(sq.reasoning_type, ""):
            missing.append(f"agent_mismatch:{sq.question_id}")

    if missing:
        return False, ProofObject(
            rule="check_routing_completeness",
            premises=[f"missing={missing!r}"],
            conclusion=f"VIOLATION: routing incomplete for {missing!r}",
        )

    return True, ProofObject(
        rule="check_routing_completeness",
        premises=[
            f"sub_question_count={len(decomp.sub_questions)}",
            f"types={[sq.reasoning_type for sq in decomp.sub_questions]!r}",
        ],
        conclusion="Routing complete: all sub-questions have valid agent assignments",
    )


def check_synthesis_strategy_validity(
    decomp: InquiryDecomposition,
) -> Tuple[bool, ProofObject]:
    """Verify synthesis strategy is one of the 4 canonical types.

    Standard: MQ-002 (strategy must match conflict level)
    Falsifies if: strategy not in {"consensus","weighted","adversarial","dialectical"}.
    falsifies_if: strategy not in {"consensus","weighted","adversarial","dialectical"}.
    """
    strategy = decomp.synthesis_strategy
    if strategy not in VALID_SYNTHESIS_STRATEGIES:
        return False, ProofObject(
            rule="check_synthesis_strategy_validity",
            premises=[f"strategy={strategy!r}"],
            conclusion=(
                f"VIOLATION: synthesis strategy {strategy!r} not in "
                f"{sorted(VALID_SYNTHESIS_STRATEGIES)!r}"
            ),
        )

    return True, ProofObject(
        rule="check_synthesis_strategy_validity",
        premises=[
            f"strategy={strategy!r}",
            f"valid_strategies={sorted(VALID_SYNTHESIS_STRATEGIES)!r}",
        ],
        conclusion=f"Synthesis strategy '{strategy}' is canonical — MQ-002 satisfied",
    )


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all Master Questioner routing invariants on a sample decomposition.

    Returns a list of (check_name, passed, proof) tuples.

    Falsifies if: any invariant check raises an exception rather than returning a ProofObject.
    falsifies_if: any invariant check raises an exception rather than returning a ProofObject.
    """
    sample_query = (
        "What is the Nash equilibrium of a two-domain invariant conflict "
        "and how should we resolve it?"
    )

    ok, proof = decompose_query(sample_query)
    decomp = _build_sample_decomposition(sample_query)

    results: List[Tuple[str, bool, ProofObject]] = [
        ("decompose_query", ok, proof),
    ]

    completeness_ok, completeness_proof = check_routing_completeness(decomp)
    results.append(("check_routing_completeness", completeness_ok, completeness_proof))

    validity_ok, validity_proof = check_synthesis_strategy_validity(decomp)
    results.append(("check_synthesis_strategy_validity", validity_ok, validity_proof))

    return results


# ---------------------------------------------------------------------------
# Demo / CLI helpers
# ---------------------------------------------------------------------------


def _build_sample_decomposition(query: str) -> InquiryDecomposition:
    """Construct an InquiryDecomposition from a query string.

    Falsifies if: the returned decomposition has zero sub-questions.
    falsifies_if: the returned decomposition has zero sub-questions.
    """
    reasoning_types = _detect_reasoning_types(query)
    domain_ids = _infer_domain_ids(query)
    strategy = _select_synthesis_strategy(reasoning_types)
    estimated = _estimate_tokens(query)

    sub_questions: List[SubQuestion] = []
    for idx, rtype in enumerate(reasoning_types):
        sq = SubQuestion(
            question_id=f"SQ-{idx + 1:03d}",
            text=f"[{rtype.upper()}] {query}",
            reasoning_type=rtype,
            assigned_agent=ROUTING_TABLE.get(rtype, "unknown"),
            domain_ids=domain_ids,
        )
        sub_questions.append(sq)

    return InquiryDecomposition(
        original_query=query,
        sub_questions=tuple(sub_questions),
        synthesis_strategy=strategy,
        estimated_tokens=estimated,
    )


def _decomposition_to_dict(decomp: InquiryDecomposition) -> dict:
    """Serialise an InquiryDecomposition to a JSON-serialisable dict.

    Falsifies if: estimated_tokens is not representable as a finite rational.
    falsifies_if: estimated_tokens is not representable as a finite rational.
    """
    return {
        "original_query": decomp.original_query,
        "synthesis_strategy": decomp.synthesis_strategy,
        "estimated_tokens": str(decomp.estimated_tokens),
        "sub_questions": [
            {
                "question_id": sq.question_id,
                "text": sq.text,
                "reasoning_type": sq.reasoning_type,
                "assigned_agent": sq.assigned_agent,
                "domain_ids": sq.domain_ids,
            }
            for sq in decomp.sub_questions
        ],
    }


def _main() -> int:
    """CLI entry point.

    Falsifies if: --demo flag does not produce a valid InquiryDecomposition.
    falsifies_if: --demo flag does not produce a valid InquiryDecomposition.
    """
    parser = argparse.ArgumentParser(
        description="Master Questioner inquiry decomposition and routing."
    )
    parser.add_argument(
        "--demo",
        metavar="QUERY",
        help="Decompose a query and print the InquiryDecomposition as JSON.",
    )
    parser.add_argument(
        "--run-invariants",
        action="store_true",
        help="Run all routing invariants and print results.",
    )
    args = parser.parse_args()

    if args.demo:
        decomp = _build_sample_decomposition(args.demo)
        ok, proof = decompose_query(args.demo)
        if not ok:
            print(f"ERROR: {proof.conclusion}", file=sys.stderr)
            return 1
        print(json.dumps(_decomposition_to_dict(decomp), indent=2))
        return 0

    if args.run_invariants:
        results = run_all_invariants()
        for name, passed, proof in results:
            status = "PASS" if passed else "FAIL"
            print(f"[{status}] {name}: {proof.conclusion}")
        failed = [name for name, passed, _ in results if not passed]
        return 1 if failed else 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
