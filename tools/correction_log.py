"""tools/correction_log.py — Persistent Bayesian correction tracker.

Component 3 of 9a Therapeutic Pipeline.

Every AI session reads this at startup to know:
"user has corrected scope reduction N times, posterior P(literal_maximal) = X"
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Tuple

from axioms.logic import ProofObject


REPO_ROOT = Path(__file__).resolve().parent.parent
CORRECTION_LOG_PATH = REPO_ROOT / "corrections" / "correction_log.jsonl"


def _hash_entry(entry: Dict[str, str]) -> str:
    """Compute SHA-256 hash of a correction entry."""
    payload = json.dumps(entry, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_corrections(path: Path | None = None) -> List[Dict[str, str]]:
    """Read all corrections from JSONL."""
    if path is None:
        path = CORRECTION_LOG_PATH
    corrections: List[Dict[str, str]] = []
    if not path.exists():
        return corrections
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                corrections.append(json.loads(line))
    return corrections


def append_correction(
    session_id: str,
    correction_type: str,
    user_instruction: str,
    ai_deviation: str,
    path: Path | None = None,
) -> Dict[str, str]:
    """Append a correction entry to the log.

    Returns the entry dict.
    """
    if path is None:
        path = CORRECTION_LOG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    entry: Dict[str, str] = {
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correction_type": correction_type,
        "user_instruction": user_instruction,
        "ai_deviation": ai_deviation,
        "correction_hash": "",  # filled below
    }
    entry["correction_hash"] = _hash_entry(entry)

    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")

    return entry


def compute_literal_maximal_posterior(
    corrections: List[Dict[str, str]] | None = None,
) -> Tuple[Fraction, ProofObject]:
    """Compute P(literal_maximal | N corrections) via iterative Bayesian update.

    prior = Fraction(1, 10)
    For each correction:
        evidence = P(correction|literal) * prior + P(correction|figurative) * (1 - prior)
        posterior = P(correction|literal) * prior / evidence
        prior = posterior

    Falsifies if: evidence becomes zero during update.
    falsifies_if: evidence becomes zero during update.
    """
    if corrections is None:
        corrections = load_corrections()

    prior = Fraction(1, 10)
    likelihood_literal = Fraction(1, 1)
    likelihood_figurative = Fraction(1, 10)

    for i, _ in enumerate(corrections):
        evidence = likelihood_literal * prior + likelihood_figurative * (Fraction(1, 1) - prior)
        if evidence == Fraction(0, 1):
            return prior, ProofObject(
                conclusion=f"VIOLATION: Bayesian evidence zero at correction {i}",
                premises=[f"Corrections: {i}"],
                rule="bayesian_posterior",
            )
        prior = (likelihood_literal * prior) / evidence

    return prior, ProofObject(
        conclusion=f"Posterior P(literal_maximal | {len(corrections)} corrections) = {prior}",
        premises=[
            f"Corrections: {len(corrections)}",
            f"Posterior: {prior}",
        ],
        rule="bayesian_posterior",
    )


def get_summary() -> Dict[str, str]:
    """Return summary of correction log."""
    corrections = load_corrections()
    posterior, _ = compute_literal_maximal_posterior(corrections)
    verdict = "LITERAL" if posterior > Fraction(9, 10) else "UNCERTAIN"
    return {
        "total_corrections": str(len(corrections)),
        "posterior_literal_maximal": str(posterior),
        "verdict": verdict,
    }


def main() -> int:
    """CLI entry point."""
    summary = get_summary()
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
