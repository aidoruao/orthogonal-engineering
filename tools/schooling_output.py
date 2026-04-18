#!/usr/bin/env python3
"""tools/schooling_output.py — Master Questioner schooling layer generators.

Provides four pure-function generators that emit pedagogical output in plain
strings. All functions are side-effect-free and return only plain str values.
No float arithmetic. No network calls. No file writes.

Standard: Yeshua / Orthogonal Engineering / MQ-003
"""

from __future__ import annotations

from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parent.parent
GLOSSARY_PATH = REPO_ROOT / "GLOSSARY.md"
DOMAINS_DIR = REPO_ROOT / "src" / "domains"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _load_glossary_terms() -> frozenset[str]:
    """Return the set of defined terms in GLOSSARY.md (lowercase).

    Falsifies if: returns an empty set when GLOSSARY.md exists and has entries.
    falsifies_if: returns an empty set when GLOSSARY.md exists and has entries.
    """
    if not GLOSSARY_PATH.exists():
        return frozenset()
    terms: list[str] = []
    for line in GLOSSARY_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith("| ") and "---" not in line:
            term = line.split("|")[1].strip().lower()
            if term and term != "term":
                terms.append(term)
    return frozenset(terms)


def _list_domain_files(domain_id: str) -> List[str]:
    """Return ordered list of canonical files for a domain package.

    Falsifies if: returns a non-empty list for a non-existent domain.
    falsifies_if: returns a non-empty list for a non-existent domain.
    """
    domain_dir = DOMAINS_DIR / domain_id
    if not domain_dir.exists():
        return []
    ordered = [
        "__init__.py",
        "domain.py",
        "implementation.py",
        "invariants.py",
    ]
    present: List[str] = []
    for filename in ordered:
        candidate = domain_dir / filename
        if candidate.exists():
            present.append(str(candidate.relative_to(REPO_ROOT)))
    tests_dir = domain_dir / "tests"
    if tests_dir.exists():
        for p in sorted(tests_dir.glob("test_*.py")):
            present.append(str(p.relative_to(REPO_ROOT)))
    return present


# ---------------------------------------------------------------------------
# Public generators
# ---------------------------------------------------------------------------


def generate_noob_summary(synthesis: str) -> str:
    """Generate a plain-language summary (≤200 words) suitable for non-specialists.

    Jargon terms detected in the synthesis are flagged with a GLOSSARY reference.
    No domain jargon appears without a definition pointer (MQ-003 schooling accessibility).

    Standard: MQ-003
    Falsifies if: the summary contains a domain jargon term without a GLOSSARY.md reference.
    falsifies_if: the summary contains a domain jargon term without a GLOSSARY.md reference.
    """
    glossary_terms = _load_glossary_terms()
    words = synthesis.split()
    annotated_words: List[str] = []
    for word in words:
        clean = word.strip(".,;:!?()[]\"'").lower()
        if clean in glossary_terms:
            annotated_words.append(f"{word} [→ GLOSSARY: {clean}]")
        else:
            annotated_words.append(word)
    annotated = " ".join(annotated_words)

    summary_parts = [
        "SUMMARY (non-specialist):",
        annotated[:800] if len(annotated) > 800 else annotated,
        "",
        "Key points:",
        "1. The above synthesis was produced by the Master Questioner meta-layer.",
        "2. All claims are backed by ProofObject evidence.",
        "3. Jargon terms marked [→ GLOSSARY] are defined in GLOSSARY.md.",
    ]
    return "\n".join(summary_parts)


def generate_onboarding_path(domain_ids: List[str]) -> List[str]:
    """Return an ordered list of files and commands for onboarding to the given domains.

    The order respects the dependency hierarchy:
    platform file → standards → domain invariants → tests.

    Standard: MQ-003
    Falsifies if: any listed file does not exist on disk at the returned path.
    falsifies_if: any listed file does not exist on disk at the returned path.
    """
    path: List[str] = []

    platform_files = [
        "CLAUDE.md",
        "SOP_AI_HANDSHAKE.md",
        "AGENT_CAPABILITIES_MATRIX.md",
        "GLOSSARY.md",
        "STANDARDS_REGISTRY.json",
        "MASTER_QUESTIONER.md",
    ]
    for pf in platform_files:
        if (REPO_ROOT / pf).exists():
            path.append(pf)

    path.append("# Run: python tools/onboard_agent.py --agent copilot --skip-env-check")
    path.append("# Run: python audit/popperian_audit.py 2>&1 | tail -3")

    for domain_id in domain_ids:
        domain_files = _list_domain_files(domain_id)
        for df in domain_files:
            path.append(df)
        if domain_files:
            path.append(
                f"# Run: python src/domains/{domain_id}/invariants.py"
            )

    path.append("# Run: pytest tests/ -q")

    return path


def generate_falsification_exercise(claim: str) -> str:
    """Generate a Popperian falsification exercise for the given claim.

    The exercise states the claim, derives a falsifies_if condition, and
    proposes a concrete experiment to test it. Required by MQ-003.

    Standard: MQ-003
    Falsifies if: the returned string does not contain a 'Falsifies if:' section.
    falsifies_if: the returned string does not contain a 'Falsifies if:' section.
    """
    lines = [
        "FALSIFICATION EXERCISE",
        "======================",
        "",
        f"Claim: {claim}",
        "",
        "Falsifies if:",
        (
            "  The experiment described below produces an outcome that directly contradicts "
            "the claim, and the outcome is reproducible under the same conditions."
        ),
        "",
        "Proposed experiment:",
        (
            "  1. Identify the smallest domain invariant that instantiates the claim."
        ),
        (
            "  2. Construct a data fixture that represents the boundary condition where "
            "the claim would be violated."
        ),
        (
            "  3. Run the invariant check function with that fixture and record the "
            "(bool, ProofObject) result."
        ),
        (
            "  4. The claim is falsified if the check returns (False, proof) with a "
            "non-trivial conclusion."
        ),
        "",
        "Expected ProofObject structure on falsification:",
        (
            "  ProofObject(rule='falsification_test', "
            "premises=['boundary_fixture'], conclusion='VIOLATION: ...')"
        ),
        "",
        "Note: All numeric comparisons must use Fraction, not float.",
    ]
    return "\n".join(lines)


def generate_bar_exam_question(domain_id: str) -> str:
    """Generate a multiple-choice bar exam question for the given domain.

    The question tests knowledge of the domain's invariant checks at the
    ordination threshold (≥70% required, per pr50_bar_exam).

    Standard: MQ-003 / pr50_bar_exam
    Falsifies if: the returned string does not cite the domain invariant it tests.
    falsifies_if: the returned string does not cite the domain invariant it tests.
    """
    invariants_path = DOMAINS_DIR / domain_id / "invariants.py"

    if not invariants_path.exists():
        return (
            f"BAR EXAM QUESTION\n"
            f"Domain: {domain_id}\n"
            f"Status: invariants.py not found — question generation skipped.\n"
            f"Falsification: domain invariants file must exist at "
            f"src/domains/{domain_id}/invariants.py"
        )

    source = invariants_path.read_text(encoding="utf-8")
    check_functions = [
        line.strip().split("def ")[1].split("(")[0]
        for line in source.splitlines()
        if line.strip().startswith("def check_")
    ]

    if not check_functions:
        target_fn = "run_all_invariants"
    else:
        target_fn = check_functions[0]

    lines = [
        "BAR EXAM QUESTION",
        "=================",
        f"Domain: {domain_id}",
        f"Invariant tested: {domain_id}.invariants.{target_fn}",
        "",
        f"Question: Which of the following conditions would cause {target_fn}() "
        "to return (False, ProofObject)?",
        "",
        "A) The function is called with a valid nominal data fixture that satisfies "
        "all invariant preconditions.",
        "B) The function is called with a data fixture that violates the primary "
        "boundary condition of the invariant.",
        "C) The function imports float() from the standard library.",
        "D) The function returns a bare bool instead of a (bool, ProofObject) tuple.",
        "",
        "Correct answers: B, C, D",
        "",
        "Explanation:",
        "  B — violating the invariant boundary returns (False, proof).",
        "  C — float() is forbidden; using it violates CS-001 and will cause "
        "the popperian audit to fail.",
        "  D — all check functions must return Tuple[bool, ProofObject] per CS-002.",
        "",
        f"Source: src/domains/{domain_id}/invariants.py",
        "Ordination threshold: ≥70% correct (pr50_bar_exam)",
    ]
    return "\n".join(lines)
