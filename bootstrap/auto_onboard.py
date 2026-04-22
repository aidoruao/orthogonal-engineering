#!/usr/bin/env python3
"""
bootstrap/auto_onboard.py — The Wand

Single-command agent onboarding. Chains health check, onboarding context,
and verification suite. Prints READY or NOT READY with exactly what failed.

Usage:
    python bootstrap/auto_onboard.py --agent kimi
    python bootstrap/auto_onboard.py --agent copilot --json

Standard: Yeshua / Orthogonal Engineering
Version: 1.0.0
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
HEALTH_CHECK = REPO_ROOT / "tools" / "agent_health_check.py"
ONBOARD_AGENT = REPO_ROOT / "tools" / "onboard_agent.py"
VERIFY_ALL = REPO_ROOT / "tools" / "verify_all.py"

SUPPORTED_AGENTS = frozenset({
    "copilot", "claude", "devin", "kimi",
    "aider", "cursor", "windsurf", "cline", "continue",
})

# ---------------------------------------------------------------------------
# ProofObject import — guard for environments where axioms isn't on PYTHONPATH
# ---------------------------------------------------------------------------

try:
    _sys_path_inserted = False
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
        _sys_path_inserted = True
    from axioms.logic import ProofObject
    _HAS_PROOFOBJECT = True
except Exception:  # noqa: BLE001
    _HAS_PROOFOBJECT = False

    class ProofObject:  # type: ignore[no-redef]
        """Fallback ProofObject when axioms module is unavailable.

        Falsifies if: proof_hash is not a non-empty string.
        falsifies_if: proof_hash is not a non-empty string.
        """

        def __init__(self, rule: str, premises: list[Any], conclusion: str) -> None:
            """Initialise fallback ProofObject.

            Falsifies if: proof_hash is not a non-empty string.
            falsifies_if: proof_hash is not a non-empty string.
            """
            self.rule = rule
            self.premises = premises
            self.conclusion = conclusion
            import hashlib
            payload = json.dumps(
                {"rule": rule, "premises": premises, "conclusion": conclusion},
                sort_keys=True,
            )
            self.proof_hash = hashlib.sha256(payload.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Step runners
# ---------------------------------------------------------------------------

def _run_step(
    cmd: list[str],
    timeout: int = 120,
) -> tuple[int, str, str]:
    """Run a subprocess and return (returncode, stdout, stderr).

    Falsifies if: returncode is misreported.
    falsifies_if: returncode is misreported.
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except FileNotFoundError:
        return -1, "", "command not found"


def run_health_check() -> tuple[bool, ProofObject]:
    """Run tools/agent_health_check.py --fast.

    Falsifies if: returns True when the subprocess exits non-zero.
    falsifies_if: returns True when the subprocess exits non-zero.
    """
    rc, out, err = _run_step(
        [sys.executable, str(HEALTH_CHECK), "--fast"],
        timeout=60,
    )
    ok = rc == 0
    detail = (out.strip().splitlines()[-1] if out.strip() else err.strip()) or "no output"
    proof = ProofObject(
        rule="HealthCheckStep",
        premises=[f"cmd=agent_health_check.py --fast", f"returncode={rc}"],
        conclusion=f"Health check {'PASS' if ok else 'FAIL'}: {detail[:120]}",
    )
    return ok, proof


def run_onboarding(agent: str) -> tuple[bool, ProofObject]:
    """Run tools/onboard_agent.py --agent <type>.

    Falsifies if: returns True when the subprocess exits non-zero.
    falsifies_if: returns True when the subprocess exits non-zero.
    """
    rc, out, err = _run_step(
        [sys.executable, str(ONBOARD_AGENT), "--agent", agent],
        timeout=60,
    )
    ok = rc == 0
    detail = (out.strip().splitlines()[-1] if out.strip() else err.strip()) or "no output"
    proof = ProofObject(
        rule="OnboardingStep",
        premises=[f"cmd=onboard_agent.py --agent {agent}", f"returncode={rc}"],
        conclusion=f"Onboarding {'PASS' if ok else 'FAIL'}: {detail[:120]}",
    )
    return ok, proof


def run_verification() -> tuple[bool, ProofObject]:
    """Run tools/verify_all.py --skip-tests --skip-merkle.

    Falsifies if: returns True when the subprocess exits non-zero.
    falsifies_if: returns True when the subprocess exits non-zero.
    """
    rc, out, err = _run_step(
        [sys.executable, str(VERIFY_ALL), "--skip-tests", "--skip-merkle"],
        timeout=120,
    )
    ok = rc == 0
    detail = (out.strip().splitlines()[-1] if out.strip() else err.strip()) or "no output"
    proof = ProofObject(
        rule="VerificationStep",
        premises=[
            "cmd=verify_all.py --skip-tests --skip-merkle",
            f"returncode={rc}",
        ],
        conclusion=f"Verification {'PASS' if ok else 'FAIL'}: {detail[:120]}",
    )
    return ok, proof


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def auto_onboard(agent: str) -> tuple[bool, ProofObject]:
    """Run the full auto-onboarding sequence.

    Chains health check, onboarding, and verification. Returns (ready, proof).

    Falsifies if: ready is True but any step failed.
    falsifies_if: ready is True but any step failed.
    """
    steps: list[dict[str, Any]] = []

    ok_health, proof_health = run_health_check()
    steps.append({
        "step": "health_check",
        "pass": ok_health,
        "conclusion": proof_health.conclusion,
        "proof_hash": proof_health.proof_hash,
    })

    ok_onboard, proof_onboard = run_onboarding(agent)
    steps.append({
        "step": "onboarding",
        "pass": ok_onboard,
        "conclusion": proof_onboard.conclusion,
        "proof_hash": proof_onboard.proof_hash,
    })

    ok_verify, proof_verify = run_verification()
    steps.append({
        "step": "verification",
        "pass": ok_verify,
        "conclusion": proof_verify.conclusion,
        "proof_hash": proof_verify.proof_hash,
    })

    all_pass = ok_health and ok_onboard and ok_verify
    failed_steps = [s["step"] for s in steps if not s["pass"]]

    conclusion = (
        "READY — all steps passed"
        if all_pass
        else f"NOT READY — failed: {', '.join(failed_steps)}"
    )

    proof = ProofObject(
        rule="AutoOnboard",
        premises=[f"{s['step']}={'PASS' if s['pass'] else 'FAIL'}" for s in steps],
        conclusion=conclusion,
    )
    return all_pass, proof, steps


def _print_table(steps: list[dict[str, Any]], ready: bool) -> None:
    """Print a READY / NOT READY table.

    Falsifies if: table claims READY when ready is False.
    falsifies_if: table claims READY when ready is False.
    """
    name_width = max(len(s["step"]) for s in steps)
    status_width = 4

    header = f"| {'Step':<{name_width}} | {'Status':<{status_width}} | Detail"
    separator = f"|{'-' * (name_width + 2)}|{'-' * (status_width + 2)}|{'-' * 50}"

    print(header)
    print(separator)
    for s in steps:
        status = "PASS" if s["pass"] else "FAIL"
        detail = s["conclusion"][:60]
        print(f"| {s['step']:<{name_width}} | {status:<{status_width}} | {detail}")

    print(separator)
    verdict = "READY" if ready else "NOT READY"
    print(f"| {'VERDICT':<{name_width}} | {verdict:<{status_width}} |")
    if not ready:
        failed = [s["step"] for s in steps if not s["pass"]]
        print(f"| {'FAILED':<{name_width}} | {', '.join(failed):<{status_width}} |")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """Entry point for the auto-onboard wand.

    Falsifies if: returns 0 when any step failed and --ignore-failures was not used.
    falsifies_if: returns 0 when any step failed and --ignore-failures was not used.
    """
    parser = argparse.ArgumentParser(
        description="Single-command agent onboarding wand.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--agent",
        default="kimi",
        choices=sorted(SUPPORTED_AGENTS),
        help="Agent type to onboard.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of human-readable table.",
    )
    parser.add_argument(
        "--ignore-failures",
        action="store_true",
        help="Exit 0 even if steps failed (for CI debugging).",
    )

    args = parser.parse_args(argv)

    ready, proof, steps = auto_onboard(args.agent)

    if args.json:
        output = {
            "ready": ready,
            "agent": args.agent,
            "steps": steps,
            "proof_hash": proof.proof_hash,
        }
        print(json.dumps(output, indent=2))
    else:
        _print_table(steps, ready)

    if ready or args.ignore_failures:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
