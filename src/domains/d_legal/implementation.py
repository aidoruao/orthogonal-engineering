"""
D_LEGAL — statute/citation verification implementation.

Invariants:
  1. Every legal citation resolves to a verifiable statute reference.
  2. Citation parsing is deterministic.
  3. Precedent chains preserve order and verifiability.

Biblical inspiration: Proverbs 22:28 — do not move ancient boundary stones.
"""

from __future__ import annotations

from dataclasses import dataclass


KNOWN_STATUTES = {
    "29 U.S.C. § 207": "FLSA overtime",
    "18 U.S.C. § 1030": "Computer Fraud and Abuse Act",
    "15 U.S.C. § 45": "FTC unfair practices",
}


@dataclass(frozen=True)
class Citation:
    raw: str
    title: str
    code: str
    section: str


def parse_citation(raw: str) -> Citation:
    if "§" not in raw or "U.S.C." not in raw:
        raise ValueError("Citation must contain '§' and 'U.S.C.' (e.g., '29 U.S.C. § 207')")
    left, right = raw.split("§", 1)
    left = left.strip()
    right = right.strip()
    title = left.split("U.S.C.")[0].strip()
    code = "U.S.C."
    return Citation(raw=raw.strip(), title=title, code=code, section=right)


def citation_key(c: Citation) -> str:
    return f"{c.title} U.S.C. § {c.section}"


def verify_statute_reference(raw: str) -> bool:
    c = parse_citation(raw)
    return citation_key(c) in KNOWN_STATUTES


def validate_precedent_chain(citations: list[str]) -> bool:
    if not citations:
        raise ValueError("citations must not be empty")
    for raw in citations:
        if not verify_statute_reference(raw):
            return False
    return True


DOMAIN_METADATA = {
    "id": "D_LEGAL",
    "name": "Legal",
    "invariants": [
        "Every legal citation resolves to a verifiable statute reference.",
        "Citation parsing is deterministic.",
        "Precedent chains preserve order and verifiability.",
    ],
    "falsification_tests": ["F_LEGAL_001"],
    "implementation_functions": [
        "Citation",
        "parse_citation",
        "verify_statute_reference",
        "validate_precedent_chain",
    ],
}
