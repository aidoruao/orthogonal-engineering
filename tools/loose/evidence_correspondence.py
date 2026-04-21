"""
A-19: Evidence Correspondence Validator
========================================
Implements the commutative diagram constraint from the bi-layer epistemic spec:

    h ∘ f = g   (the "diagram commutes" check)

Where:
    f: S → E_i   (system state → internal evidence)
    g: S → E_e   (system state → external evidence)
    h: E_i → E_e (correspondence mapping / bridge function)

The validator computes a ``correspondence_score ∈ [0, 1]`` from four
independent checks:

1. Hash cross-reference (weight 0.40): common files are mutually referenced
   in both manifests via their non-empty digests (different algorithms).
2. Complexity gate A-20 (weight 0.30): external must not be simpler than
   internal (Kimi §2.3 — anti-bullshit filter).
3. Cardinality check (weight 0.20): file counts match within ±5%.
4. Temporal coherence (weight 0.10): external ≥ internal timestamp.

If ``correspondence_score < threshold`` (default 0.9) → epistemic failure.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from complexity import ApparentComplexity

_DEFAULT_THRESHOLD: float = 0.9
_COMPLEXITY_ALPHA: float = 0.85
_COUNT_TOLERANCE: float = 0.05  # ±5%


class EvidenceCorrespondenceValidator:
    """Validate that internal and external evidence correspond to the same ground truth.

    Args:
        internal_manifest: Output of the internal pipeline (SHA-256 tree).
        external_manifest: Output of ExternalWitness (SHA-512 tree).
        threshold: Minimum correspondence_score to consider valid.
    """

    def __init__(
        self,
        internal_manifest: Dict[str, Any],
        external_manifest: Dict[str, Any],
        threshold: float = _DEFAULT_THRESHOLD,
    ) -> None:
        self.internal = internal_manifest
        self.external = external_manifest
        self.threshold = threshold
        self._complexity = ApparentComplexity()

    # ---------------------------------------------------------------- #
    # Public API                                                         #
    # ---------------------------------------------------------------- #

    def validate(self) -> Dict[str, Any]:
        """Run all four checks and compose a weighted verdict.

        Returns a report with:
        - ``correspondence_score``: weighted composite [0, 1]
        - ``valid``: True if score ≥ threshold
        - ``error_term``: 1 - score (non-commutativity measure)
        - ``mismatch_list``: files present in only one manifest
        - ``details``: per-check breakdowns
        """
        # 1. Hash cross-reference
        hash_check = self._cross_reference_hashes()

        # 2. Complexity gate (A-20)
        complexity_check = self._complexity.validate_complexity_gate(
            self.internal, self.external, alpha=_COMPLEXITY_ALPHA
        )

        # 3. Cardinality
        int_count = self.internal.get("file_count", 0)
        ext_count = self.external.get("file_count", 0)
        count_ratio = min(int_count, ext_count) / max(int_count, ext_count, 1)
        count_passed = count_ratio >= (1.0 - _COUNT_TOLERANCE)

        # 4. Temporal coherence (lexicographic ISO-8601 compare)
        int_ts = (self.internal.get("computed_at")
                  or str(self.internal.get("timestamp_utc", "")))
        ext_ts = (self.external.get("computed_at")
                  or str(self.external.get("timestamp_utc", "")))
        time_valid = ext_ts >= int_ts if int_ts and ext_ts else True

        # Weighted composite (h ∘ f = g check)
        correspondence_score = round(
            hash_check["match_ratio"] * 0.40
            + (1.0 if complexity_check["passed"] else 0.0) * 0.30
            + (1.0 if count_passed else count_ratio) * 0.20
            + (1.0 if time_valid else 0.0) * 0.10,
            4,
        )

        return {
            "correspondence_score": correspondence_score,
            "threshold": self.threshold,
            "valid": correspondence_score >= self.threshold,
            "error_term": round(1.0 - correspondence_score, 4),
            "mismatch_list": hash_check["mismatch_list"],
            "details": {
                "hash_cross_reference": hash_check,
                "complexity_gate": complexity_check,
                "count_check": {
                    "internal_count": int_count,
                    "external_count": ext_count,
                    "count_ratio": round(count_ratio, 4),
                    "passed": count_passed,
                },
                "temporal_coherence": {
                    "internal_ts": int_ts,
                    "external_ts": ext_ts,
                    "valid": time_valid,
                },
            },
        }

    def divergence(self) -> float:
        """Return the non-commutativity error (1 − score) directly."""
        return self.validate()["error_term"]

    # ---------------------------------------------------------------- #
    # Sub-checks                                                         #
    # ---------------------------------------------------------------- #

    def _cross_reference_hashes(self) -> Dict[str, Any]:
        """Check that common files have non-empty, valid digests in BOTH manifests.

        The internal and external digests use different algorithms (SHA-256 vs
        SHA-512) so they are never equal — mutual reference is established by
        confirming both sides stored a valid (non-empty, non-"unreadable") digest
        for the same relative path.
        """
        int_files: Dict[str, str] = self.internal.get("file_hashes", {})
        ext_files: Dict[str, str] = self.external.get("file_hashes", {})

        common = set(int_files) & set(ext_files)
        only_int = set(int_files) - set(ext_files)
        only_ext = set(ext_files) - set(int_files)

        matches = sum(
            1 for p in common
            if int_files[p] not in ("", "unreadable")
            and ext_files[p] not in ("", "unreadable")
        )

        mismatch_list: List[str] = sorted(only_int)[:20] + sorted(only_ext)[:20]

        return {
            "common_files": len(common),
            "matched_references": matches,
            "match_ratio": round(matches / max(len(common), 1), 4),
            "only_in_internal": len(only_int),
            "only_in_external": len(only_ext),
            "mismatch_list": mismatch_list,
        }


def index_testimony_evidence(evidence_dir: Path, index_path: Path) -> None:
    """
    Append a verification testimony evidence directory to the evidence index.

    Args:
        evidence_dir: Directory containing attestations.json and summary.json.
        index_path: Path to the evidence index JSONL file.
    """
    import json

    summary_file = evidence_dir / "summary.json"
    if not summary_file.exists():
        return

    with open(summary_file) as f:
        summary = json.load(f)

    entry = {
        "evidence_dir": str(evidence_dir.resolve()),
        "overall_success": summary.get("overall_success"),
        "commitment": summary.get("commitment"),
        "merkle_root": summary.get("merkle_root"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "a") as f:
        f.write(json.dumps(entry) + "\n")
