"""
falsification/hypothesis.py — Popperian Hypothesis Framework

Every invariant must declare a hypothesis with:
  - claim        (what we assert to be true)
  - assumptions  (what must hold for the claim to be meaningful)
  - invariant    (the specific property that must not be violated)

CI must attempt falsification.  If a counterexample is found → build fails.
Truth survives only if it withstands attack.

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

__all__ = [
    "Hypothesis",
    "FalsificationResult",
    "register_hypothesis",
    "HYPOTHESIS_REGISTRY",
]

# Global registry of all declared hypotheses
HYPOTHESIS_REGISTRY: List["Hypothesis"] = []


@dataclass
class FalsificationResult:
    """Result of attempting to falsify a hypothesis."""

    hypothesis_id: str
    survived: bool  # True = hypothesis survived (no counterexample found)
    counterexample: Optional[Any] = None
    detail: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "survived": self.survived,
            "counterexample": str(self.counterexample) if self.counterexample is not None else None,
            "detail": self.detail,
        }


@dataclass
class Hypothesis:
    """
    A Popperian hypothesis: a claim that is falsifiable.

    Attributes:
        hypothesis_id: Unique identifier (e.g., "H-001").
        claim:         Human-readable assertion.
        assumptions:   Preconditions that must hold.
        invariant:     Callable that returns True if invariant holds for a witness.
        domain:        Optional list of witnesses to test against.
    """

    hypothesis_id: str
    claim: str
    assumptions: List[str]
    invariant: Callable[[Any], bool]
    domain: List[Any] = field(default_factory=list)

    def attempt_falsification(self) -> FalsificationResult:
        """
        Try to find a counterexample from self.domain.

        Returns FalsificationResult with survived=True if no counterexample found.
        """
        for witness in self.domain:
            try:
                holds = self.invariant(witness)
            except Exception as exc:
                return FalsificationResult(
                    hypothesis_id=self.hypothesis_id,
                    survived=False,
                    counterexample=witness,
                    detail=f"Exception during falsification: {exc}",
                )
            if not holds:
                return FalsificationResult(
                    hypothesis_id=self.hypothesis_id,
                    survived=False,
                    counterexample=witness,
                    detail=f"Invariant returned False for witness={witness!r}",
                )
        return FalsificationResult(
            hypothesis_id=self.hypothesis_id,
            survived=True,
            detail=f"No counterexample found in {len(self.domain)} witnesses",
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "claim": self.claim,
            "assumptions": self.assumptions,
            "domain_size": len(self.domain),
        }


def register_hypothesis(h: Hypothesis) -> Hypothesis:
    """Register a hypothesis in the global registry."""
    HYPOTHESIS_REGISTRY.append(h)
    return h
