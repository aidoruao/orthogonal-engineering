"""
A-24: Semantic Divergence Detector
=====================================
Detects contradictions across multiple independent evidence sources using
structural cross-validation.

The Kimi spec calls for running 2+ models (Gemini vs other) and measuring the
contradiction score.  Since real LLM inference requires network access, this
module works with the **warden report structures** already collected by the
health-check pipeline — treating each warden as an independent "model" that
produced a verdict about the same ground truth.

The divergence score is:
    contradiction_score = |unique_verdicts| / |total_verdicts|
      → 0.0 when all sources agree (consensus)
      → 1.0 when every source disagrees (maximum divergence)

A consensus threshold of < 0.33 (≤ 1 divergent source in 3) is used by
default to declare consensus.

Verdict entropy (Shannon) is also computed — it should be 0 at true consensus
and log₂(k) at maximum divergence among k sources.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Set, Tuple


_CONSENSUS_THRESHOLD: float = 0.34  # ≥ 1/(n-1) for n sources all agreeing


class SemanticDivergenceDetector:
    """Detect semantic contradictions across independent evidence sources.

    Args:
        evidence_sources: Mapping of source_name → evidence dict.
            Each evidence dict must have a ``status`` or ``verdict`` key.
        consensus_threshold: contradiction_score below which consensus is declared.
    """

    def __init__(
        self,
        evidence_sources: Optional[Dict[str, Dict[str, Any]]] = None,
        consensus_threshold: float = _CONSENSUS_THRESHOLD,
    ) -> None:
        self.sources = evidence_sources or {}
        self.consensus_threshold = consensus_threshold

    # ---------------------------------------------------------------- #
    # Public API                                                         #
    # ---------------------------------------------------------------- #

    def cross_validate(
        self,
        evidence_sources: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Cross-validate verdicts from all evidence sources.

        Args:
            evidence_sources: Override for ``self.sources``.

        Returns:
            Dict with:
            - ``consensus``: True if contradiction_score < threshold
            - ``contradiction_score``: float [0, 1]
            - ``verdict_entropy``: Shannon entropy of verdict distribution
            - ``verdicts``: per-source verdict dict
            - ``divergent_pairs``: list of contradicting (source_a, source_b) pairs
            - ``majority_verdict``: the most common verdict, or None
        """
        sources = evidence_sources or self.sources
        if not sources:
            return {
                "consensus": True,
                "contradiction_score": 0.0,
                "verdict_entropy": 0.0,
                "verdicts": {},
                "divergent_pairs": [],
                "majority_verdict": None,
                "reason": "no_sources",
            }

        verdicts: Dict[str, str] = {}
        for name, evidence in sources.items():
            v = (
                evidence.get("status")
                or evidence.get("verdict")
                or evidence.get("overall_health")
                or "unknown"
            )
            verdicts[name] = str(v)

        unique_verdicts: Set[str] = set(verdicts.values())
        total = len(verdicts)
        # Normalize: 0.0 when all agree, 1.0 when all disagree
        # Formula: (unique - 1) / max(total - 1, 1)  preserves 0..1 range
        contradiction_score = round(
            (len(unique_verdicts) - 1) / max(total - 1, 1), 4
        )

        # Verdict entropy
        verdict_counts: Dict[str, int] = {}
        for v in verdicts.values():
            verdict_counts[v] = verdict_counts.get(v, 0) + 1
        entropy = 0.0
        for count in verdict_counts.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        entropy = round(entropy, 4)

        # Majority verdict
        majority_verdict = (
            max(verdict_counts, key=lambda k: verdict_counts[k])
            if verdict_counts
            else None
        )

        # Divergent pairs
        divergent_pairs = self._find_divergent_pairs(verdicts)

        return {
            "consensus": contradiction_score < self.consensus_threshold,
            "contradiction_score": contradiction_score,
            "verdict_entropy": entropy,
            "verdicts": verdicts,
            "divergent_pairs": divergent_pairs,
            "majority_verdict": majority_verdict,
            "total_sources": total,
            "unique_verdicts": sorted(unique_verdicts),
        }

    # ---------------------------------------------------------------- #
    # Helpers                                                            #
    # ---------------------------------------------------------------- #

    def _find_divergent_pairs(
        self, verdicts: Dict[str, str]
    ) -> List[Dict[str, str]]:
        """Return all (source_a, source_b) pairs where verdicts disagree."""
        names = list(verdicts)
        divergent = []
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                if verdicts[a] != verdicts[b]:
                    divergent.append(
                        {
                            "source_a": a,
                            "verdict_a": verdicts[a],
                            "source_b": b,
                            "verdict_b": verdicts[b],
                        }
                    )
        return divergent

    @staticmethod
    def from_warden_results(
        warden_results: Dict[str, Dict[str, Any]],
        consensus_threshold: float = _CONSENSUS_THRESHOLD,
    ) -> "SemanticDivergenceDetector":
        """Convenience constructor: build from health_check_integration warden results."""
        return SemanticDivergenceDetector(
            evidence_sources=warden_results,
            consensus_threshold=consensus_threshold,
        )
