# pr45_uvdtl/forkability/forkability_checker.py
# PR #45 — Universal Verifiability & Deterministic Transparency Layer (UVDTL)
# Standard: Yeshua
#
# Section VII — Forkability Guarantee
#
# The system must guarantee:
#   1. No central signing authority required to rebuild.
#   2. No remote validation gate required to run.
#   3. All verification scripts included in repository.
#   4. Complete reproducibility without network access.

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


# ---------------------------------------------------------------------------
# Forkability Spec
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ForkabilitySpec:
    """
    Formal declaration of the forkability guarantee.
    All four conditions must hold for the system to be forkable.
    """
    no_central_signing: bool
    no_remote_validation_gate: bool
    verification_scripts_in_repo: bool
    offline_reproducible: bool

    def is_forkable(self) -> bool:
        """System is forkable iff all four conditions hold."""
        return (
            self.no_central_signing
            and self.no_remote_validation_gate
            and self.verification_scripts_in_repo
            and self.offline_reproducible
        )

    def as_dict(self) -> Dict:
        return {
            "forkable": self.is_forkable(),
            "no_central_signing": self.no_central_signing,
            "no_remote_validation_gate": self.no_remote_validation_gate,
            "offline_reproducible": self.offline_reproducible,
            "verification_scripts_in_repo": self.verification_scripts_in_repo,
        }


# ---------------------------------------------------------------------------
# Forkability Checker
# ---------------------------------------------------------------------------

def check_forkability(spec: ForkabilitySpec) -> Dict[str, bool]:
    """
    Evaluate the forkability spec and return a detailed result dict.
    """
    result = spec.as_dict()
    return result


def assert_forkable(spec: ForkabilitySpec) -> bool:
    """
    Assert that the system is forkable.
    Raises ValueError listing which conditions failed.
    """
    failures: List[str] = []
    if not spec.no_central_signing:
        failures.append("no_central_signing")
    if not spec.no_remote_validation_gate:
        failures.append("no_remote_validation_gate")
    if not spec.verification_scripts_in_repo:
        failures.append("verification_scripts_in_repo")
    if not spec.offline_reproducible:
        failures.append("offline_reproducible")
    if failures:
        raise ValueError(f"System not forkable; failed conditions: {failures}")
    return True


# ---------------------------------------------------------------------------
# PR45 Forkability Declaration
# ---------------------------------------------------------------------------

PR45_FORKABILITY: ForkabilitySpec = ForkabilitySpec(
    no_central_signing=True,
    no_remote_validation_gate=True,
    verification_scripts_in_repo=True,
    offline_reproducible=True,
)


# ---------------------------------------------------------------------------
# COMPARISON table
# ---------------------------------------------------------------------------

COMPARISON: dict = {
    "Centralised build service": (
        "Requires signing authority; remote gate; non-forkable without permission"
    ),
    "PR #45 forkability": (
        "No central signing; no remote gate; all scripts in repo; "
        "offline reproducible; git clone + run is sufficient"
    ),
}
