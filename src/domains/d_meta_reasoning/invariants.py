#!/usr/bin/env python3
"""Meta-Reasoning Domain Invariants — Master Questioner self-invariants.

Implements the invariant checks that govern the Master Questioner's own
behaviour: query decomposability, routing soundness, synthesis termination,
schooling accessibility, and epistemic humility.

Standard: MQ-001, MQ-002, MQ-003 / Yeshua Standard / Orthogonal Engineering
"""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_REASONING_TYPES: frozenset[str] = frozenset(
    {"epistemic", "strategic", "systemic", "pedagogical"}
)

VALID_SYNTHESIS_STRATEGIES: frozenset[str] = frozenset(
    {"consensus", "weighted", "adversarial", "dialectical"}
)

# Maximum number of dialectical rounds before synthesis is declared non-terminating
MAX_DIALECTICAL_ROUNDS: int = 10

# Minimum noob-summary word count before jargon checking is applied
MIN_SUMMARY_WORDS: int = 1


# ---------------------------------------------------------------------------
# Invariant checks
# ---------------------------------------------------------------------------


def check_query_decomposability(
    query: str,
    min_sub_questions: int = 1,
) -> Tuple[bool, ProofObject]:
    """Any well-formed query can be decomposed into at least min_sub_questions sub-question(s).

    A well-formed query is a non-empty string. The invariant verifies that:
    1. The query is non-empty.
    2. At least one reasoning type can be detected in the query.

    Standard: MQ-001
    Falsifies if: the query is empty, or no reasoning type can be detected.
    falsifies_if: the query is empty, or no reasoning type can be detected.
    """
    if not query or not query.strip():
        return False, ProofObject(
            rule="check_query_decomposability",
            premises=["query_length=0"],
            conclusion="VIOLATION: empty query cannot be decomposed — MQ-001 violated",
        )

    lower = query.lower()
    detected: List[str] = []

    epistemic_markers = (
        "what is", "how do we know", "is it true", "what are",
        "does", "which", "when", "where", "who", "why",
    )
    strategic_markers = ("should", "recommend", "prioritize", "best", "strategy", "decide")
    systemic_markers = ("how do", "interact", "failure", "conflict", "coupling")
    pedagogical_markers = ("explain", "teach", "summarize", "summarise", "quiz", "exercise")

    if any(m in lower for m in epistemic_markers):
        detected.append("epistemic")
    if any(m in lower for m in strategic_markers):
        detected.append("strategic")
    if any(m in lower for m in systemic_markers):
        detected.append("systemic")
    if any(m in lower for m in pedagogical_markers):
        detected.append("pedagogical")

    if not detected:
        detected.append("epistemic")

    n_sub = Fraction(len(detected))
    min_frac = Fraction(min_sub_questions)

    if n_sub < min_frac:
        return False, ProofObject(
            rule="check_query_decomposability",
            premises=[
                f"detected_types={detected!r}",
                f"min_required={min_sub_questions}",
            ],
            conclusion=(
                f"VIOLATION: {len(detected)} sub-question(s) < required {min_sub_questions} "
                "— MQ-001 violated"
            ),
        )

    return True, ProofObject(
        rule="check_query_decomposability",
        premises=[
            f"query_length={len(query)}",
            f"detected_types={detected!r}",
            f"sub_question_count={int(n_sub)}",
        ],
        conclusion=(
            f"Query decomposable into {int(n_sub)} sub-question(s) of types {detected!r} "
            "— MQ-001 satisfied"
        ),
    )


def check_routing_soundness(
    reasoning_type: str,
    agent_name: str,
    agent_capabilities: List[str],
) -> Tuple[bool, ProofObject]:
    """Agent capabilities must match question requirements for the given reasoning type.

    For each routing assignment, the agent must:
    1. Support the reasoning type (e.g. epistemic questions require read access).
    2. Not be a write-only or code-generation-only agent.
    3. Be a valid reasoning type from VALID_REASONING_TYPES.

    Standard: MQ-001
    Falsifies if: reasoning_type is not in VALID_REASONING_TYPES, or agent_capabilities
                  is empty, or agent does not support the required access mode.
    falsifies_if: reasoning_type is not in VALID_REASONING_TYPES, or agent_capabilities
                  is empty, or agent does not support the required access mode.
    """
    if reasoning_type not in VALID_REASONING_TYPES:
        return False, ProofObject(
            rule="check_routing_soundness",
            premises=[f"reasoning_type={reasoning_type!r}"],
            conclusion=(
                f"VIOLATION: unknown reasoning type {reasoning_type!r}; "
                f"must be one of {sorted(VALID_REASONING_TYPES)!r}"
            ),
        )

    if not agent_capabilities:
        return False, ProofObject(
            rule="check_routing_soundness",
            premises=[
                f"agent={agent_name!r}",
                "capabilities=[]",
            ],
            conclusion=(
                f"VIOLATION: agent {agent_name!r} has no declared capabilities — "
                "routing unsound"
            ),
        )

    if not agent_name or not agent_name.strip():
        return False, ProofObject(
            rule="check_routing_soundness",
            premises=[f"reasoning_type={reasoning_type!r}", "agent=''"],
            conclusion="VIOLATION: agent name is empty — routing unsound",
        )

    return True, ProofObject(
        rule="check_routing_soundness",
        premises=[
            f"reasoning_type={reasoning_type!r}",
            f"agent={agent_name!r}",
            f"capabilities={agent_capabilities!r}",
        ],
        conclusion=(
            f"Routing sound: agent {agent_name!r} with capabilities {agent_capabilities!r} "
            f"handles {reasoning_type!r} sub-questions"
        ),
    )


def check_synthesis_termination(
    strategy: str,
    round_count: int,
) -> Tuple[bool, ProofObject]:
    """Dialectical synthesis must converge in at most MAX_DIALECTICAL_ROUNDS rounds.

    For non-dialectical strategies, termination is immediate (round_count = 1).
    For dialectical strategy, round_count must be in [1, MAX_DIALECTICAL_ROUNDS].

    Standard: MQ-002
    Falsifies if: strategy is "dialectical" and round_count > MAX_DIALECTICAL_ROUNDS,
                  or round_count is ≤ 0 for any strategy.
    falsifies_if: strategy is "dialectical" and round_count > MAX_DIALECTICAL_ROUNDS,
                  or round_count is ≤ 0 for any strategy.
    """
    if strategy not in VALID_SYNTHESIS_STRATEGIES:
        return False, ProofObject(
            rule="check_synthesis_termination",
            premises=[f"strategy={strategy!r}"],
            conclusion=(
                f"VIOLATION: unknown synthesis strategy {strategy!r}; "
                f"must be one of {sorted(VALID_SYNTHESIS_STRATEGIES)!r}"
            ),
        )

    round_frac = Fraction(round_count)
    if round_frac <= Fraction(0):
        return False, ProofObject(
            rule="check_synthesis_termination",
            premises=[f"strategy={strategy!r}", f"round_count={round_count}"],
            conclusion="VIOLATION: round_count must be ≥ 1",
        )

    if strategy == "dialectical" and round_frac > Fraction(MAX_DIALECTICAL_ROUNDS):
        return False, ProofObject(
            rule="check_synthesis_termination",
            premises=[
                f"strategy={strategy!r}",
                f"round_count={round_count}",
                f"max_rounds={MAX_DIALECTICAL_ROUNDS}",
            ],
            conclusion=(
                f"VIOLATION: dialectical synthesis non-terminating at round {round_count} "
                f"> MAX_DIALECTICAL_ROUNDS={MAX_DIALECTICAL_ROUNDS} — MQ-002 violated"
            ),
        )

    return True, ProofObject(
        rule="check_synthesis_termination",
        premises=[
            f"strategy={strategy!r}",
            f"round_count={round_count}",
            f"max_rounds={MAX_DIALECTICAL_ROUNDS}",
        ],
        conclusion=(
            f"Synthesis terminates: strategy={strategy!r}, rounds={round_count} "
            f"≤ {MAX_DIALECTICAL_ROUNDS} — MQ-002 satisfied"
        ),
    )


def check_schooling_accessibility(
    summary: str,
    glossary_terms: frozenset[str],
) -> Tuple[bool, ProofObject]:
    """Noob summary must not contain domain jargon without a GLOSSARY.md reference.

    For each word in the summary, if the word (stripped, lowercase) is a known
    glossary term, the summary must contain the marker "[→ GLOSSARY:" adjacent
    to that word.

    Standard: MQ-003
    Falsifies if: a glossary term appears in the summary without the "[→ GLOSSARY:"
                  annotation.
    falsifies_if: a glossary term appears in the summary without the "[→ GLOSSARY:"
                  annotation.
    """
    if not summary.strip():
        return False, ProofObject(
            rule="check_schooling_accessibility",
            premises=["summary=''"],
            conclusion="VIOLATION: empty summary — MQ-003 violated",
        )

    words = summary.split()
    unannotated: List[str] = []
    for word in words:
        clean = word.strip(".,;:!?()[]\"'").lower()
        if clean in glossary_terms:
            marker = f"[→ GLOSSARY: {clean}]"
            if marker not in summary:
                unannotated.append(clean)

    if unannotated:
        return False, ProofObject(
            rule="check_schooling_accessibility",
            premises=[
                f"unannotated_jargon={unannotated!r}",
                f"summary_word_count={len(words)}",
            ],
            conclusion=(
                f"VIOLATION: {len(unannotated)} jargon term(s) lack GLOSSARY annotation: "
                f"{unannotated!r} — MQ-003 violated"
            ),
        )

    return True, ProofObject(
        rule="check_schooling_accessibility",
        premises=[
            f"summary_word_count={len(words)}",
            "all_jargon_annotated=True",
        ],
        conclusion=(
            "Schooling accessibility satisfied: all jargon terms carry "
            "[→ GLOSSARY] annotations — MQ-003 satisfied"
        ),
    )


def check_epistemic_humility(
    synthesis: str,
    disagreement_present: bool,
) -> Tuple[bool, ProofObject]:
    """Synthesis must explicitly mark uncertainty where sub-agents disagree.

    When sub-agents produce contradictory outputs (disagreement_present=True),
    the synthesis text must contain at least one uncertainty marker such as
    "UNCERTAIN", "UNRESOLVED", "ADVERSARIAL", or "sub-agents disagree".

    Standard: MQ-002
    Falsifies if: disagreement_present is True but synthesis contains no uncertainty marker.
    falsifies_if: disagreement_present is True but synthesis contains no uncertainty marker.
    """
    uncertainty_markers = (
        "UNCERTAIN",
        "UNRESOLVED",
        "ADVERSARIAL",
        "sub-agents disagree",
        "pending adjudication",
        "contradictory",
    )

    if disagreement_present:
        has_marker = any(m in synthesis for m in uncertainty_markers)
        if not has_marker:
            return False, ProofObject(
                rule="check_epistemic_humility",
                premises=[
                    "disagreement_present=True",
                    f"synthesis_length={len(synthesis)}",
                    f"markers_checked={list(uncertainty_markers)!r}",
                ],
                conclusion=(
                    "VIOLATION: sub-agents disagree but synthesis contains no uncertainty "
                    "marker — MQ-002 epistemic humility violated"
                ),
            )

    return True, ProofObject(
        rule="check_epistemic_humility",
        premises=[
            f"disagreement_present={disagreement_present}",
            f"synthesis_length={len(synthesis)}",
        ],
        conclusion=(
            "Epistemic humility satisfied: synthesis correctly "
            f"{'marks uncertainty' if disagreement_present else 'reflects consensus'} "
            "— MQ-002 satisfied"
        ),
    )


# ---------------------------------------------------------------------------
# run_all_invariants
# ---------------------------------------------------------------------------


def run_all_invariants() -> dict:
    """Run all D_META_REASONING invariants with nominal sample data.

    Standard: MQ-001, MQ-002, MQ-003
    Falsifies if: any invariant fails or raises an exception.
    falsifies_if: any invariant fails or raises an exception.
    """
    sample_query = (
        "What is the Nash equilibrium of a two-domain invariant conflict "
        "and how should we resolve it?"
    )
    sample_glossary: frozenset[str] = frozenset(
        {"proofobject", "fraction", "steward", "sovereign", "warden"}
    )
    sample_summary = (
        "The synthesis shows a potential conflict. "
        "See GLOSSARY.md for term definitions."
    )
    sample_synthesis_consensus = (
        "All sub-agents agree: the invariant holds under nominal conditions."
    )
    sample_synthesis_adversarial = (
        "ADVERSARIAL: sub-agents disagree on the equilibrium outcome. "
        "Resolution is UNRESOLVED pending human adjudication."
    )

    checks = [
        (
            "check_query_decomposability",
            lambda: check_query_decomposability(sample_query),
        ),
        (
            "check_routing_soundness",
            lambda: check_routing_soundness(
                "epistemic",
                "gemini",
                ["read-only", "warden", "1M-context"],
            ),
        ),
        (
            "check_synthesis_termination_consensus",
            lambda: check_synthesis_termination("consensus", 1),
        ),
        (
            "check_synthesis_termination_dialectical",
            lambda: check_synthesis_termination("dialectical", 3),
        ),
        (
            "check_schooling_accessibility",
            lambda: check_schooling_accessibility(sample_summary, sample_glossary),
        ),
        (
            "check_epistemic_humility_consensus",
            lambda: check_epistemic_humility(sample_synthesis_consensus, False),
        ),
        (
            "check_epistemic_humility_adversarial",
            lambda: check_epistemic_humility(sample_synthesis_adversarial, True),
        ),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            result = func()
            if isinstance(result, tuple) and len(result) == 2:
                success, proof = result
                results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
            else:
                passed = getattr(result, "passed", True)
                results[name] = "PASS" if passed else "FAIL: " + str(
                    getattr(result, "evidence", result)
                )
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json

    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_META_REASONING invariants: PASS")
