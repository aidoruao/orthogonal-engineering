"""
pcfe_kernel/certification.py — CertificationSimulator.

Implements the exam/certification layer:

    C = D_fdacs ∘ D_train ∘ F*

Structurally identical to the pr50_bar_exam pattern already in the repo.
A candidate supplies a list of proposed actions; the simulator evaluates them
against the kernel loop, regulatory constraints, and falsification tests.

PASS iff:
  1. All candidate actions are allowed by the registry (no prohibited action).
  2. All kernel transitions are accepted by OrthoKernel.transition().
  3. Every falsification_id listed in the regulatory department passes.
  4. No constraint violations are reported by any registered principle.

No partial credit unless explicitly parameterised.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Resolve OrthoState / OrthoKernel from the existing v1 core loop
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from minimal_ai_ide.ortho_kernel import (  # noqa: E402
    OrthoKernel,
    OrthoState,
    create_genesis_kernel,
    theo_projector,
)
from dataclasses import replace  # noqa: E402

from pcfe_kernel.department import Department, DepartmentRegistry  # noqa: E402
from pcfe_kernel.principles import Principle, ALL_PRINCIPLES, Artifact  # noqa: E402

# ---------------------------------------------------------------------------
# Path to the canonical falsification test registry
# ---------------------------------------------------------------------------
_FALSIFICATION_JSON = _REPO_ROOT / "ontology" / "falsification_tests.json"


def _make_action_transition(action: str):
    """Return an OrthoState transition function for the given action string.

    Extracted as a module-level factory (instead of a closure inside a loop)
    to avoid repeated function-definition overhead and linting concerns.
    """
    def η(s: OrthoState) -> OrthoState:
        new_manifest = s.manifest + (f"action:{action}",)
        return replace(
            s,
            manifest=new_manifest,
            logos_id=f"PCFE_{hashlib.sha256((s.logos_id + action).encode()).hexdigest()[:8]}",
            constraints_satisfied=s.constraints_satisfied + 1,
            hypostasis=s.hypostasis,
        )
    return η


def _load_falsification_ids() -> List[str]:
    """Load all test IDs from ontology/falsification_tests.json."""
    if not _FALSIFICATION_JSON.exists():
        return []
    with _FALSIFICATION_JSON.open(encoding="utf-8") as fh:
        data = json.load(fh)
    tests = data.get("falsification_tests", [])
    return [t["id"] for t in tests if "id" in t]


@dataclass
class ExamResult:
    """Immutable record of a single certification attempt.

    Attributes:
        candidate_id:  Identifier for the entity being examined.
        passed:        True iff all gates cleared.
        score:         Fraction of gates that passed (0.0 – 1.0).
        gates:         Per-gate pass/fail detail.
        transcript_hash: SHA-256 over the deterministic transcript.
        timestamp_utc: Unix timestamp of evaluation.
    """

    candidate_id: str
    passed: bool
    score: float
    gates: Dict[str, bool]
    transcript_hash: str
    timestamp_utc: float = field(default_factory=time.time)


@dataclass
class CertificationSimulator:
    """C = D_fdacs ∘ D_train ∘ F*

    Evaluates a candidate's proposed action sequence against:
      - The regulatory department (D_fdacs) hard constraint filter
      - A training-generated initial state (D_train)
      - The falsification test registry (F*)
      - All registered Principles

    Attributes:
        regulatory_dept:     D_fdacs — hard rule filter on transitions.
        training_dept:       D_train — initial state generator.
        falsification_engine: F* test IDs from falsification_tests.json.
        registry:            Full DepartmentRegistry for the session.
        principles:          Governance principles applied at each gate.
    """

    regulatory_dept: Department
    training_dept: Department
    falsification_engine: List[str]
    registry: DepartmentRegistry = field(default_factory=DepartmentRegistry)
    principles: List[Principle] = field(default_factory=lambda: list(ALL_PRINCIPLES))

    def generate_scenario(self) -> OrthoState:
        """Generate an initial OrthoState from the D_train ontology.

        Entities defined in D_train's ontology["entities"] are injected into
        OrthoState.manifest, establishing the starting domain context.
        """
        base_manifest = tuple(self.training_dept.manifest_entries())
        # Merge additional manifest entries from all state-input departments
        extra_manifest = tuple(self.registry.all_manifest_entries())
        full_manifest = base_manifest + extra_manifest
        if not full_manifest:
            full_manifest = ("pcfe_scenario_default",)

        scenario = OrthoState(
            logos_id="PCFE_SCENARIO_001",
            manifest=full_manifest,
            constraints_satisfied=len(self.regulatory_dept.constraint_keys),
            is_terminal=False,
            grace_field=1.0,
            hypostasis=f"pcfe_exam_{hashlib.sha256(str(full_manifest).encode()).hexdigest()[:8]}",
        )
        return scenario

    def evaluate(
        self,
        candidate_actions: List[str],
        candidate_id: str = "anonymous",
    ) -> ExamResult:
        """Run candidate actions through the kernel loop.

        PASS iff:
          1. Every action is allowed by action-constraint departments.
          2. Every corresponding kernel transition is accepted.
          3. Every falsification_id in the regulatory department is present
             in the falsification_engine (i.e., the test is registered).
          4. Every governance Principle is satisfied by a constructed artifact
             representing the action sequence.

        No partial credit unless explicitly parameterised.
        """
        gates: Dict[str, bool] = {}

        # ------------------------------------------------------------------
        # Gate 1: Action allowlist (D_chem hard filter)
        # ------------------------------------------------------------------
        for action in candidate_actions:
            gate_key = f"action_allowed:{action}"
            gates[gate_key] = self.registry.is_action_allowed(action)

        # ------------------------------------------------------------------
        # Gate 2: Kernel transitions
        # ------------------------------------------------------------------
        initial_state = self.generate_scenario()
        kernel = OrthoKernel(initial_state, theo_projector)

        for action in candidate_actions:
            prev_id = kernel._state.logos_id
            kernel = kernel.transition(_make_action_transition(action))
            accepted = kernel._state.logos_id != prev_id
            gates[f"transition:{action}"] = accepted

        # ------------------------------------------------------------------
        # Gate 3: Falsification test coverage
        # ------------------------------------------------------------------
        known_ids = set(self.falsification_engine)
        for fid in self.regulatory_dept.falsification_ids:
            gates[f"falsification:{fid}"] = fid in known_ids

        # ------------------------------------------------------------------
        # Gate 4: Principle verification
        # ------------------------------------------------------------------
        artifact = Artifact(
            content={"actions": candidate_actions, "kernel_history": len(kernel.get_history())},
            constraints=[c for dept in self.registry.all() for c in dept.constraint_keys],
        )
        for principle in self.principles:
            gates[f"principle:{principle.name}"] = principle.verify(artifact)

        # ------------------------------------------------------------------
        # Scoring
        # ------------------------------------------------------------------
        passed_count = sum(1 for v in gates.values() if v)
        total_count = len(gates)
        score = passed_count / total_count if total_count else 0.0
        passed = all(gates.values())

        # Deterministic transcript hash
        transcript_str = json.dumps(
            {
                "candidate_id": candidate_id,
                "actions": candidate_actions,
                "gates": {k: gates[k] for k in sorted(gates)},
            },
            sort_keys=True,
        )
        transcript_hash = hashlib.sha256(transcript_str.encode("utf-8")).hexdigest()

        return ExamResult(
            candidate_id=candidate_id,
            passed=passed,
            score=score,
            gates=gates,
            transcript_hash=transcript_hash,
        )
