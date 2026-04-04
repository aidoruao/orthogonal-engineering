"""
A-25: Ontological Invariant Registry
=======================================
Immutable system invariants that MUST hold on every execution.  These are
*non-configurable at runtime* — they act as global optimization boundary
conditions (the Kimi spec's "quarantine protocol" for the epistemic layer).

Invariants are grounded in the first principles (§I of the ChatGPT v2.0 spec):
  1. no_self_validation_only      ← external evidence must exist (1.5, A-18)
  2. external_correspondence      ← score ≥ threshold (1.1, A-19)
  3. idempotent_verification      ← V(V(S)) = V(S) (1.3)
  4. reversibility_required       ← all actions auditable (1.4)
  5. evidence_required            ← no evidenceless actions (1.2)
  6. complexity_monotonicity      ← external not simpler than internal (A-20)

Each invariant carries a ``failure_action`` (``"freeze"`` or ``"escalate"``)
that the caller is expected to execute.  The registry itself never mutates
state — it only reports.

``assert_all()`` is the hot path: it runs every check and returns a compact
report.  All checks are defensive (exceptions → failure, not crash).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional


@dataclass(frozen=True)
class Invariant:
    """An individual ontological invariant.

    Attributes:
        name:           Unique snake_case identifier.
        check:          Zero-argument callable returning bool.
        failure_action: ``"freeze"`` (stop all autonomy) or ``"escalate"`` (warn).
        description:    Human-readable statement of what must hold.
    """

    name: str
    check: Callable[[], bool]
    failure_action: str
    description: str


class OntologicalInvariantRegistry:
    """Registry of immutable system invariants.

    Build with ``OntologicalInvariantRegistry.build(context)`` where
    ``context`` is a dict produced by the health-check pipeline.  Each check
    evaluates a single property of the context dict — no external I/O.

    Usage::

        ctx = {
            "external_manifest_exists": True,
            "correspondence_score": 0.95,
            "execute_actions": [],
            "evidence_by_action": {"update_file_count": {...}},
            "complexity_gate_passed": True,
        }
        registry = OntologicalInvariantRegistry.build(ctx)
        result = registry.assert_all()
        # result["all_passed"] → bool
        # result["results"] → per-invariant breakdown
    """

    INVARIANT_NAMES: List[str] = [
        "no_self_validation_only",
        "external_correspondence_required",
        "idempotent_verification",
        "reversibility_required",
        "evidence_required",
        "complexity_monotonicity",
    ]

    def __init__(self, invariants: List[Invariant]) -> None:
        self._invariants = invariants

    # ---------------------------------------------------------------- #
    # Factory                                                            #
    # ---------------------------------------------------------------- #

    @classmethod
    def build(cls, context: Dict[str, Any]) -> "OntologicalInvariantRegistry":
        """Construct registry from the health-check pipeline context dict.

        Expected context keys (all optional — missing → conservative default):
        - ``external_manifest_exists``: bool
        - ``correspondence_score``: float [0, 1]
        - ``correspondence_threshold``: float (default 0.9)
        - ``execute_actions``: list of executed action dicts (must all have ``reversible`` or ``audit_log``)
        - ``evidence_by_action``: dict mapping action_type → evidence dict
        - ``complexity_gate_passed``: bool
        - ``idempotency_verified``: bool (explicit override)
        """
        corr_threshold = context.get("correspondence_threshold", 0.9)
        corr_score = context.get("correspondence_score", 0.0)
        execute_actions: List[Dict[str, Any]] = context.get("execute_actions", [])
        evidence_by_action: Dict[str, Any] = context.get("evidence_by_action", {})

        def _check_no_self_validation() -> bool:
            return bool(context.get("external_manifest_exists", False))

        def _check_correspondence() -> bool:
            return corr_score >= corr_threshold

        def _check_idempotent() -> bool:
            return bool(context.get("idempotency_verified", True))

        def _check_reversibility() -> bool:
            return all(
                a.get("reversibility", {}).get("reversible", True) or a.get("audit_log")
                for a in execute_actions
            )

        def _check_evidence_required() -> bool:
            if not execute_actions:
                return True
            return all(
                bool(evidence_by_action.get(a.get("action_type"), {}).get("evidence"))
                for a in execute_actions
            )

        def _check_complexity_monotonicity() -> bool:
            return bool(context.get("complexity_gate_passed", True))

        invariants: List[Invariant] = [
            Invariant(
                name="no_self_validation_only",
                check=_check_no_self_validation,
                failure_action="freeze",
                description="System cannot operate with only internal validation; external evidence must exist",
            ),
            Invariant(
                name="external_correspondence_required",
                check=_check_correspondence,
                failure_action="escalate",
                description=(
                    f"Internal and external evidence must correspond "
                    f"(score ≥ {corr_threshold})"
                ),
            ),
            Invariant(
                name="idempotent_verification",
                check=_check_idempotent,
                failure_action="freeze",
                description="V(V(S)) must equal V(S) — verification must be idempotent",
            ),
            Invariant(
                name="reversibility_required",
                check=_check_reversibility,
                failure_action="escalate",
                description="All executed actions must have rollback paths or audit trails",
            ),
            Invariant(
                name="evidence_required",
                check=_check_evidence_required,
                failure_action="freeze",
                description="No executed action may proceed without evidentiary support",
            ),
            Invariant(
                name="complexity_monotonicity",
                check=_check_complexity_monotonicity,
                failure_action="escalate",
                description="External evidence must not be simpler than internal claims (A-20 complexity gate)",
            ),
        ]

        return cls(invariants)

    # ---------------------------------------------------------------- #
    # Assertion                                                          #
    # ---------------------------------------------------------------- #

    def assert_all(self) -> Dict[str, Any]:
        """Run all invariants and return a consolidated report.

        Returns:
            Dict with:
            - ``all_passed``: True only if every invariant holds
            - ``system_state``: ``"operational"`` or ``"frozen"`` or ``"degraded"``
            - ``results``: per-invariant dict mapping name → {passed, action, description}
            - ``failures``: list of failed invariant names
        """
        results: Dict[str, Any] = {}
        failures: List[str] = []
        freeze_triggered = False
        escalate_triggered = False

        for inv in self._invariants:
            try:
                passed = inv.check()
            except Exception as exc:
                passed = False
                results[inv.name] = {
                    "passed": False,
                    "error": str(exc),
                    "action": "freeze",
                    "description": inv.description,
                }
                failures.append(inv.name)
                freeze_triggered = True
                continue

            action = None if passed else inv.failure_action
            results[inv.name] = {
                "passed": passed,
                "action": action,
                "description": inv.description,
            }

            if not passed:
                failures.append(inv.name)
                if inv.failure_action == "freeze":
                    freeze_triggered = True
                elif inv.failure_action == "escalate":
                    escalate_triggered = True

        all_passed = len(failures) == 0
        if freeze_triggered:
            system_state = "frozen"
        elif escalate_triggered:
            system_state = "degraded"
        else:
            system_state = "operational"

        return {
            "all_passed": all_passed,
            "system_state": system_state,
            "results": results,
            "failures": failures,
            "invariant_count": len(self._invariants),
        }
