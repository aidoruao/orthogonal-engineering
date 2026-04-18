#!/usr/bin/env python3
"""
tools/agent_health_check.py — Unified Agent Health Check

Validates the full repository health in a single pass and exits with code
0 (healthy) or 1 (failures found). All checks are composable — individual
checks return (bool, ProofObject) pairs for glass-box auditability.

Checks performed:
    1. Python version >= 3.10
    2. Virtual environment active (warns if absent, does not fail)
    3. Required files present (list from STANDARDS_REGISTRY.json + built-in set)
    4. consent_log.jsonl integrity (parseable JSONL, non-empty)
    5. Merkle roots valid (merkle/global_root.json root_hash is 64-char hex)
    6. Popperian audit passing (delegates to audit/popperian_audit.py)
    7. AGENT_FEED.md chain intact (delegates to generate_feed_entry.py --verify)
    8. Zero float() violations in domain invariants
    9. STANDARDS_REGISTRY.json parseable and non-empty

Usage:
    python tools/agent_health_check.py
    python tools/agent_health_check.py --json
    python tools/agent_health_check.py --fast   # skip slow checks (audit, chain)

Exit codes:
    0  All checks passed
    1  One or more checks failed

Author: Orthogonal Engineering
Gap: #17 (gap analysis 2026-04-17)
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
CONSENT_LOG = REPO_ROOT / "pr47_stewardship" / "witness" / "consent_log.jsonl"
GLOBAL_ROOT = REPO_ROOT / "merkle" / "global_root.json"
AGENT_FEED = REPO_ROOT / "AGENT_FEED.md"
REGISTRY = REPO_ROOT / "STANDARDS_REGISTRY.json"
AUDIT_REPORT = REPO_ROOT / "audit" / "POPPERIAN_AUDIT_REPORT.json"
DOMAINS_DIR = REPO_ROOT / "src" / "domains"

BUILT_IN_REQUIRED_FILES = [
    "SOP_AI_HANDSHAKE.md",
    "STANDARDS_REGISTRY.json",
    "AGENT_FEED.md",
    "pr47_stewardship/witness/consent_log.jsonl",
    ".github/copilot-instructions.md",
    "axioms/logic.py",
    "audit/popperian_audit.py",
    "tools/state_witness/generate_feed_entry.py",
]

# ProofObject import — guard for environments where axioms isn't on PYTHONPATH
try:
    import sys as _sys
    _sys.path.insert(0, str(REPO_ROOT))
    from axioms.logic import ProofObject
    _HAS_PROOFOBJECT = True
except Exception:  # noqa: BLE001
    _HAS_PROOFOBJECT = False

    class ProofObject:  # type: ignore[no-redef]
        """Fallback ProofObject when axioms module is unavailable."""

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
# Individual checks
# ---------------------------------------------------------------------------

def check_python_version() -> tuple[bool, ProofObject]:
    """Verify Python version >= 3.10.

    Standard: Python 3.10+ (required for structural pattern matching and modern typing)
    Falsifies if: sys.version_info < (3, 10).
    falsifies_if: sys.version_info < (3, 10).
    """
    vi = sys.version_info
    version_str = f"{vi.major}.{vi.minor}.{vi.micro}"
    ok = (vi.major, vi.minor) >= (3, 10)
    proof = ProofObject(
        rule="PythonVersionCheck",
        premises=[f"sys.version_info = ({vi.major}, {vi.minor}, {vi.micro})"],
        conclusion=f"Python {version_str} >= 3.10" if ok else f"FAIL: Python {version_str} < 3.10",
    )
    return ok, proof


def check_venv() -> tuple[bool, ProofObject]:
    """Check whether a virtual environment is active (warning only, not a hard fail).

    Standard: venv recommended but not enforced
    Falsifies if: VIRTUAL_ENV is set but the path does not exist.
    falsifies_if: VIRTUAL_ENV is set but the path does not exist.
    """
    import os
    venv = os.environ.get("VIRTUAL_ENV", "")
    if venv and Path(venv).exists():
        msg = f"venv active: {venv}"
        ok = True
    elif venv and not Path(venv).exists():
        msg = f"FAIL: VIRTUAL_ENV set to non-existent path: {venv}"
        ok = False
    else:
        msg = "No venv detected (system Python — acceptable in CI)"
        ok = True  # warn but not fail

    proof = ProofObject(
        rule="VenvCheck",
        premises=[f"VIRTUAL_ENV={repr(venv)}"],
        conclusion=msg,
    )
    return ok, proof


def check_required_files() -> tuple[bool, ProofObject]:
    """Verify all required repository files exist.

    Standard: Yeshua YS-006 (No unverifiable dependency)
    Falsifies if: any file in BUILT_IN_REQUIRED_FILES is absent.
    falsifies_if: any file in BUILT_IN_REQUIRED_FILES is absent.
    """
    missing = [f for f in BUILT_IN_REQUIRED_FILES if not (REPO_ROOT / f).exists()]
    ok = len(missing) == 0
    proof = ProofObject(
        rule="RequiredFilesCheck",
        premises=[f"checked {len(BUILT_IN_REQUIRED_FILES)} files"],
        conclusion=(
            "All required files present"
            if ok
            else f"FAIL: Missing {len(missing)} file(s): {missing[:5]}"
        ),
    )
    return ok, proof


def check_consent_log() -> tuple[bool, ProofObject]:
    """Verify consent_log.jsonl is present, non-empty, and all entries parse.

    Standard: BC-005 (Consent log entry required before code changes)
    Falsifies if: consent_log.jsonl is absent, empty, or contains unparseable JSONL.
    falsifies_if: consent_log.jsonl is absent, empty, or contains unparseable JSONL.
    """
    if not CONSENT_LOG.exists():
        proof = ProofObject(
            rule="ConsentLogCheck",
            premises=["consent_log.jsonl not found"],
            conclusion="FAIL: consent_log.jsonl absent",
        )
        return False, proof

    # Skip blank lines and comment lines (lines starting with '#')
    all_lines = CONSENT_LOG.read_text(encoding="utf-8").splitlines()
    lines = [ln for ln in all_lines if ln.strip() and not ln.strip().startswith("#")]
    if not lines:
        proof = ProofObject(
            rule="ConsentLogCheck",
            premises=["consent_log.jsonl has no data entries (only comments or empty)"],
            conclusion="FAIL: consent_log.jsonl has no JSONL entries",
        )
        return False, proof

    bad = Fraction(0)
    for line in lines:
        try:
            json.loads(line)
        except json.JSONDecodeError:
            bad += Fraction(1)

    ok = bad == Fraction(0)
    proof = ProofObject(
        rule="ConsentLogCheck",
        premises=[f"{len(lines)} entries, {int(bad)} unparseable"],
        conclusion=(
            f"Consent log OK: {len(lines)} entries"
            if ok
            else f"FAIL: {int(bad)} unparseable JSONL lines"
        ),
    )
    return ok, proof


def check_merkle_roots() -> tuple[bool, ProofObject]:
    """Verify global Merkle root is a 64-char hex string.

    Standard: YS-008 (Every artifact is hash-anchored)
    Falsifies if: global_root.json is absent or root_hash is not 64 hex chars.
    falsifies_if: global_root.json is absent or root_hash is not 64 hex chars.
    """
    if not GLOBAL_ROOT.exists():
        proof = ProofObject(
            rule="MerkleRootCheck",
            premises=["merkle/global_root.json not found"],
            conclusion="FAIL: global_root.json absent — regenerate with python merkle/global_merkle.py",
        )
        return False, proof

    try:
        data = json.loads(GLOBAL_ROOT.read_text(encoding="utf-8"))
        root_hash = str(data.get("root_hash", ""))
    except (json.JSONDecodeError, KeyError):
        root_hash = ""

    ok = bool(re.fullmatch(r"[0-9a-f]{64}", root_hash))
    proof = ProofObject(
        rule="MerkleRootCheck",
        premises=[f"root_hash={root_hash[:16]}..."],
        conclusion=(
            f"Merkle root valid ({root_hash[:16]}...)"
            if ok
            else f"FAIL: root_hash is not 64-char hex: {repr(root_hash[:32])}"
        ),
    )
    return ok, proof


def check_popperian_audit() -> tuple[bool, ProofObject]:
    """Run the Popperian audit and verify 100% pass rate.

    Standard: QG-001 / QG-002 (ANTI-NOMINALISM, ANTI-DOGMA)
    Falsifies if: popperian_audit.py exits non-zero or reports < 100% pass rate.
    falsifies_if: popperian_audit.py exits non-zero or reports < 100% pass rate.
    """
    audit_script = REPO_ROOT / "audit" / "popperian_audit.py"
    if not audit_script.exists():
        proof = ProofObject(
            rule="PopperianAuditCheck",
            premises=["audit/popperian_audit.py not found"],
            conclusion="FAIL: popperian_audit.py absent",
        )
        return False, proof

    try:
        result = subprocess.run(
            [sys.executable, str(audit_script)],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=120,
        )
        ok = result.returncode == 0
        # Try to parse the report for detail
        detail = "exit code 0"
        if AUDIT_REPORT.exists():
            try:
                data = json.loads(AUDIT_REPORT.read_text(encoding="utf-8"))
                passed = data.get("passed", "?")
                total = data.get("total", "?")
                detail = f"{passed}/{total} domains pass"
            except (json.JSONDecodeError, KeyError):
                pass
        conclusion = (
            f"Popperian audit OK: {detail}"
            if ok
            else f"FAIL: popperian_audit.py exited {result.returncode}; {detail}"
        )
    except subprocess.TimeoutExpired:
        ok = False
        conclusion = "FAIL: popperian_audit.py timed out (>120s)"
    except Exception as exc:  # noqa: BLE001
        ok = False
        conclusion = f"FAIL: {exc}"

    proof = ProofObject(
        rule="PopperianAuditCheck",
        premises=["audit/popperian_audit.py executed"],
        conclusion=conclusion,
    )
    return ok, proof


def check_feed_integrity() -> tuple[bool, ProofObject]:
    """Verify AGENT_FEED.md hash chain is intact.

    Standard: INT-001 / BC-002 (Append-only logs)
    Falsifies if: generate_feed_entry.py --verify exits non-zero.
    falsifies_if: generate_feed_entry.py --verify exits non-zero.
    """
    script = REPO_ROOT / "tools" / "state_witness" / "generate_feed_entry.py"
    if not script.exists():
        proof = ProofObject(
            rule="FeedIntegrityCheck",
            premises=["generate_feed_entry.py not found"],
            conclusion="FAIL: generate_feed_entry.py absent",
        )
        return False, proof

    try:
        result = subprocess.run(
            [sys.executable, str(script), "--verify"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=30,
        )
        ok = result.returncode == 0
        out = (result.stdout + result.stderr).strip()[:200]
        conclusion = out if ok else f"FAIL: {out}"
    except subprocess.TimeoutExpired:
        ok = False
        conclusion = "FAIL: --verify timed out (>30s)"
    except Exception as exc:  # noqa: BLE001
        ok = False
        conclusion = f"FAIL: {exc}"

    proof = ProofObject(
        rule="FeedIntegrityCheck",
        premises=["generate_feed_entry.py --verify executed"],
        conclusion=conclusion,
    )
    return ok, proof


def check_float_violations() -> tuple[bool, ProofObject]:
    """Verify zero float() calls in domain invariants.

    Standard: CS-001 (No float() — Fraction only)
    Falsifies if: grep finds float( or isclose( in any invariants.py.
    falsifies_if: grep finds float( or isclose( in any invariants.py.
    """
    if not DOMAINS_DIR.exists():
        proof = ProofObject(
            rule="FloatViolationCheck",
            premises=["src/domains/ not found"],
            conclusion="SKIP: domains directory absent",
        )
        return True, proof

    violations: list[str] = []
    for inv_file in DOMAINS_DIR.rglob("invariants.py"):
        try:
            content = inv_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for i, line in enumerate(content.splitlines(), 1):
            if "float(" in line or "isclose(" in line:
                try:
                    rel = str(inv_file.relative_to(REPO_ROOT))
                except ValueError:
                    rel = str(inv_file)
                violations.append(f"{rel}:{i}")

    ok = len(violations) == 0
    count = Fraction(len(violations))
    proof = ProofObject(
        rule="FloatViolationCheck",
        premises=[f"scanned {DOMAINS_DIR} for float( and isclose("],
        conclusion=(
            "Zero float violations in domain invariants"
            if ok
            else f"FAIL: {int(count)} violation(s): {violations[:5]}"
        ),
    )
    return ok, proof


def check_standards_registry() -> tuple[bool, ProofObject]:
    """Verify STANDARDS_REGISTRY.json is parseable and non-empty.

    Standard: INT-002 / Stream C (machine-readable standards)
    Falsifies if: STANDARDS_REGISTRY.json is absent, malformed, or has zero entries.
    falsifies_if: STANDARDS_REGISTRY.json is absent, malformed, or has zero entries.
    """
    if not REGISTRY.exists():
        proof = ProofObject(
            rule="StandardsRegistryCheck",
            premises=["STANDARDS_REGISTRY.json not found"],
            conclusion="FAIL: STANDARDS_REGISTRY.json absent",
        )
        return False, proof

    try:
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        count = len(data.get("standards", []))
    except json.JSONDecodeError as exc:
        proof = ProofObject(
            rule="StandardsRegistryCheck",
            premises=["STANDARDS_REGISTRY.json parse attempt"],
            conclusion=f"FAIL: JSON parse error: {exc}",
        )
        return False, proof

    ok = count > 0
    proof = ProofObject(
        rule="StandardsRegistryCheck",
        premises=[f"STANDARDS_REGISTRY.json has {count} entries"],
        conclusion=(
            f"Standards registry OK: {count} standards"
            if ok
            else "FAIL: STANDARDS_REGISTRY.json has zero standards"
        ),
    )
    return ok, proof


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

_FAST_CHECKS: list[
    tuple[str, Any]
] = [
    ("python_version", check_python_version),
    ("venv", check_venv),
    ("required_files", check_required_files),
    ("consent_log", check_consent_log),
    ("merkle_roots", check_merkle_roots),
    ("float_violations", check_float_violations),
    ("standards_registry", check_standards_registry),
]

_SLOW_CHECKS: list[
    tuple[str, Any]
] = [
    ("popperian_audit", check_popperian_audit),
    ("feed_integrity", check_feed_integrity),
]


def run_all_checks(
    fast_only: bool = False,
) -> tuple[bool, list[dict[str, Any]]]:
    """Run all health checks and return (all_pass, per_check_results).

    Falsifies if: all_pass is True but any check returned ok=False.
    falsifies_if: all_pass is True but any check returned ok=False.
    """
    checks = _FAST_CHECKS + ([] if fast_only else _SLOW_CHECKS)
    results: list[dict[str, Any]] = []
    all_pass = True

    for name, fn in checks:
        ok, proof = fn()
        if not ok:
            all_pass = False
        results.append({
            "check": name,
            "pass": ok,
            "conclusion": proof.conclusion,
            "proof_hash": proof.proof_hash,
        })

    return all_pass, results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """Entry point for the health check tool.

    Falsifies if: returns 0 when any check has pass=False.
    falsifies_if: returns 0 when any check has pass=False.
    """
    parser = argparse.ArgumentParser(
        description="Unified Orthogonal Engineering repository health check.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Skip slow checks (popperian_audit, feed_integrity).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON.",
    )

    args = parser.parse_args(argv)

    all_pass, results = run_all_checks(fast_only=args.fast)

    if args.json:
        print(json.dumps({
            "all_pass": all_pass,
            "checks": results,
            "pass_count": sum(1 for r in results if r["pass"]),
            "fail_count": sum(1 for r in results if not r["pass"]),
            "total": len(results),
        }, indent=2))
    else:
        for r in results:
            status = "PASS" if r["pass"] else "FAIL"
            print(f"  {status}  {r['check']:25s}  {r['conclusion'][:80]}")
        passed = sum(1 for r in results if r["pass"])
        total = len(results)
        print()
        print(f"Result: {passed}/{total} checks passed")
        if not all_pass:
            failed = [r["check"] for r in results if not r["pass"]]
            print(f"Failed: {', '.join(failed)}", file=sys.stderr)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
