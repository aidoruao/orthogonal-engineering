"""
Quarantine Enforcer
====================
Enforces AI provenance separation and runtime isolation between the internal
validation pipeline and external verification layers.

The Kimi spec requires:
  - AI-generated validation code cannot contaminate the validation pipeline
  - Internal and external pipelines must use different hash algorithms
  - External evidence must be produced in a separate runtime context

This module provides:
  1. ``QuarantineRule`` dataclass — individual rule with check + message
  2. ``QuarantineEnforcer`` — validates quarantine conditions against a manifest
  3. ``tag_ai_generated()`` — utility to mark AI-generated files in metadata

Invariants enforced:
  - ``no_shared_hash_algorithms``: internal SHA-256 ≠ external algorithm
  - ``no_merged_pipelines``: external_manifest.json is a separate file from latest_health_check.json
  - ``external_manifest_exists``: external pipeline ran before assert
  - ``runtime_isolation``: external process ID differs from internal (where detectable)
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


@dataclass(frozen=True)
class QuarantineRule:
    """A single quarantine check.

    Attributes:
        name:    Unique identifier.
        check:   Callable returning bool (True = rule satisfied).
        message: Human-readable description of what must hold.
    """

    name: str
    check: Callable[[], bool]
    message: str


class QuarantineViolation(Exception):
    """Raised when a hard quarantine rule is violated."""


class QuarantineEnforcer:
    """Validate quarantine conditions from a code/pipeline manifest.

    Args:
        manifest: Dict describing the pipeline setup.  Expected keys:
          - ``internal_algorithm``:  hash algorithm used internally (e.g. ``"sha256"``)
          - ``external_algorithm``:  hash algorithm used externally (e.g. ``"sha512"``)
          - ``internal_manifest_path``: path to internal manifest file
          - ``external_manifest_path``: path to external manifest file
          - ``external_process_id``:   PID of external witness (optional)
          - ``internal_process_id``:   PID of internal checker (optional)
    """

    def __init__(self, manifest: Dict[str, Any]) -> None:
        self.manifest = manifest
        self._rules = self._build_rules()

    # ---------------------------------------------------------------- #
    # Factory                                                            #
    # ---------------------------------------------------------------- #

    def _build_rules(self) -> List[QuarantineRule]:
        m = self.manifest
        int_algo = m.get("internal_algorithm", "sha256")
        ext_algo = m.get("external_algorithm", "sha256")
        int_path = m.get("internal_manifest_path", "")
        ext_path = m.get("external_manifest_path", "")
        int_pid = m.get("internal_process_id")
        ext_pid = m.get("external_process_id")

        def check_no_shared_algorithms() -> bool:
            return int_algo != ext_algo

        def check_no_merged_pipelines() -> bool:
            return bool(int_path) and bool(ext_path) and int_path != ext_path

        def check_external_manifest_exists() -> bool:
            return bool(ext_path) and Path(ext_path).exists()

        def check_runtime_isolation() -> bool:
            return int_pid is None or ext_pid is None or int_pid != ext_pid

        return [
            QuarantineRule(
                name="no_shared_hash_algorithms",
                check=check_no_shared_algorithms,
                message=(
                    "Internal and external pipelines must use different hash algorithms. "
                    f"Both are currently '{int_algo}'."
                ),
            ),
            QuarantineRule(
                name="no_merged_pipelines",
                check=check_no_merged_pipelines,
                message=(
                    "Internal and external manifests must be separate files. "
                    "Do not overwrite latest_health_check.json with external_manifest.json."
                ),
            ),
            QuarantineRule(
                name="external_manifest_exists",
                check=check_external_manifest_exists,
                message=(
                    "External manifest file does not exist. "
                    "Run ExternalWitness.run() before invoking QuarantineEnforcer."
                ),
            ),
            QuarantineRule(
                name="runtime_isolation",
                check=check_runtime_isolation,
                message=(
                    "External and internal pipelines must run in separate processes. "
                    "Same PID detected."
                ),
            ),
        ]

    # ---------------------------------------------------------------- #
    # Validation                                                         #
    # ---------------------------------------------------------------- #

    def validate_quarantine(self, strict: bool = False) -> Dict[str, Any]:
        """Check all quarantine rules.

        Args:
            strict: If True, raises QuarantineViolation on first failure.

        Returns:
            Dict with:
            - ``all_satisfied``: bool
            - ``results``: per-rule {name, satisfied, message}
            - ``violations``: list of violated rule names
        """
        results: List[Dict[str, Any]] = []
        violations: List[str] = []

        for rule in self._rules:
            try:
                satisfied = rule.check()
            except Exception as exc:
                satisfied = False
                if strict:
                    raise QuarantineViolation(
                        f"Rule '{rule.name}' raised: {exc}"
                    ) from exc

            results.append(
                {
                    "name": rule.name,
                    "satisfied": satisfied,
                    "message": rule.message if not satisfied else "OK",
                }
            )
            if not satisfied:
                violations.append(rule.name)
                if strict:
                    raise QuarantineViolation(
                        f"Quarantine violation: {rule.name} — {rule.message}"
                    )

        return {
            "all_satisfied": len(violations) == 0,
            "results": results,
            "violations": violations,
        }


def tag_ai_generated(model_id: str) -> str:
    """Generate a provenance tag for AI-generated code.

    The tag is inserted as a comment at the top of generated files so they
    can be excluded from internal validation (they are never treated as
    ground truth by the external witness).

    Returns:
        A string suitable for prepending to a Python file.
    """
    unique = hashlib.sha256(f"{model_id}{time.time()}".encode()).hexdigest()[:8]
    tag = f"AI-{model_id}-{unique}"
    return f"# GENERATED_BY: {tag}\n"
