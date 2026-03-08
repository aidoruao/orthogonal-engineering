#!/usr/bin/env python3
"""
Determinism Tests for the ExecutionContext pipeline.

Validates that the ExecutionContext, canonicalization, Merkle-root hashing,
command execution, and integrity-loop all behave deterministically across
repeated runs and are consistent with fixed expected values.

Tests:
  D_001  Canonicalize is idempotent
  D_002  sha256 of fixed bytes matches expected digest
  D_003  merkle_root of empty dict returns sha256(b'')
  D_004  merkle_root of single file matches expected value
  D_005  merkle_root of two files is order-sensitive (stable)
  D_006  MODE_1_EXECUTE mutates repo_state; MODE_2_SIMULATE does not
  D_007  execute_command always appends exactly one audit-log entry
  D_008  test_determinism returns True for a fixed command sequence
  D_009  verify_invariants returns True when manifest matches repo state
  D_010  integrity_loop returns True after canonicalization repairs mismatches
  D_011  integrity_loop returns False when invariants cannot be satisfied

Author: Orthogonal Engineering
PR: #64
Version: 1.0.0
"""

import sys
import os
from copy import deepcopy
from pathlib import Path

# ---------------------------------------------------------------------------
# Import the module under test
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from execution_context import (
    ExecutionContext,
    canonicalize,
    sha256,
    merkle_root,
    execute_command,
    log_operation,
    verify_invariants,
    canonicalize_repo,
    integrity_loop,
    enter_mode_0_halt,
    test_determinism,
    MAX_REPAIR_ATTEMPTS,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _violation(test_id: str, message: str) -> AssertionError:
    """Build a richly annotated AssertionError for CI log traceability."""
    frame = sys._getframe(1)
    location = f"{frame.f_code.co_filename}:{frame.f_lineno}"
    detail = (
        f"\n[DETERMINISM FAILURE]\n"
        f"  Test       : {test_id}\n"
        f"  OS         : {sys.platform}\n"
        f"  Python     : {sys.version}\n"
        f"  Location   : {location}\n"
        f"  Detail     : {message}"
    )
    return AssertionError(detail)


# ---------------------------------------------------------------------------
# D_001  canonicalize is idempotent
# ---------------------------------------------------------------------------

def run_d001_canonicalize_idempotent():
    """D_001: canonicalize(canonicalize(x).decode()) == canonicalize(x)."""
    samples = [
        "Hello World",
        "line1  \nline2\t\nline3",
        '{"b": 1, "a": 2}',
        "\r\nWindows\r\nLine\r\nEndings\r\n",
        "",
    ]
    for s in samples:
        first = canonicalize(s)
        second = canonicalize(first.decode('utf-8'))
        if first != second:
            raise _violation(
                "D_001",
                f"canonicalize not idempotent for input={s!r}: "
                f"first={first!r} second={second!r}",
            )


# ---------------------------------------------------------------------------
# D_002  sha256 of fixed bytes matches expected digest
# ---------------------------------------------------------------------------

def run_d002_sha256_known_vector():
    """D_002: sha256(b'') matches NIST reference value."""
    expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    got = sha256(b"")
    if got != expected:
        raise _violation(
            "D_002",
            f"sha256(b'') mismatch: expected={expected} got={got}",
        )

    expected2 = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    got2 = sha256(b"hello")
    if got2 != expected2:
        raise _violation(
            "D_002",
            f"sha256(b'hello') mismatch: expected={expected2} got={got2}",
        )


# ---------------------------------------------------------------------------
# D_003  merkle_root of empty dict
# ---------------------------------------------------------------------------

def run_d003_merkle_root_empty():
    """D_003: merkle_root({}) == sha256(b'')."""
    expected = sha256(b"")
    got = merkle_root({})
    if got != expected:
        raise _violation(
            "D_003",
            f"merkle_root({{}}) mismatch: expected={expected} got={got}",
        )


# ---------------------------------------------------------------------------
# D_004  merkle_root of single file
# ---------------------------------------------------------------------------

def run_d004_merkle_root_single_file():
    """D_004: merkle_root with one entry equals sha256(canonicalize(content))."""
    content = "Hello"
    expected = sha256(canonicalize(content))
    got = merkle_root({"a.txt": content})
    if got != expected:
        raise _violation(
            "D_004",
            f"merkle_root single file mismatch: expected={expected} got={got}",
        )


# ---------------------------------------------------------------------------
# D_005  merkle_root of two files is stable
# ---------------------------------------------------------------------------

def run_d005_merkle_root_two_files_stable():
    """D_005: merkle_root of two files is consistent across multiple calls."""
    files = {"a.txt": "Alpha", "b.txt": "Beta"}
    root1 = merkle_root(files)
    root2 = merkle_root(files)
    if root1 != root2:
        raise _violation(
            "D_005",
            f"merkle_root not stable: run1={root1} run2={root2}",
        )
    if len(root1) != 64:
        raise _violation(
            "D_005",
            f"merkle_root unexpected length: {len(root1)} (expected 64 hex chars)",
        )


# ---------------------------------------------------------------------------
# D_006  MODE_1_EXECUTE mutates; MODE_2_SIMULATE does not
# ---------------------------------------------------------------------------

def run_d006_execute_vs_simulate():
    """D_006: MODE_1_EXECUTE writes to repo_state; MODE_2_SIMULATE does not."""
    manifest = {"root_hash": sha256(b"")}
    cmd = {"file": "x.txt", "content": "data"}

    # MODE_1_EXECUTE should mutate
    ctx_exec = ExecutionContext("seed", manifest, [cmd])
    execute_command(ctx_exec, cmd, "MODE_1_EXECUTE")
    if "x.txt" not in ctx_exec.repo_state:
        raise _violation("D_006", "MODE_1_EXECUTE did not write to repo_state")

    # MODE_2_SIMULATE must not mutate
    ctx_sim = ExecutionContext("seed", manifest, [cmd])
    execute_command(ctx_sim, cmd, "MODE_2_SIMULATE")
    if ctx_sim.repo_state:
        raise _violation(
            "D_006",
            f"MODE_2_SIMULATE mutated repo_state: {ctx_sim.repo_state}",
        )


# ---------------------------------------------------------------------------
# D_007  execute_command always appends one audit-log entry
# ---------------------------------------------------------------------------

def run_d007_audit_log_entry():
    """D_007: every execute_command call appends exactly one audit-log record."""
    manifest = {"root_hash": sha256(b"")}
    cmd = {"file": "f.txt", "content": "v"}
    ctx = ExecutionContext("seed", manifest, [cmd])

    for mode in ("MODE_1_EXECUTE", "MODE_2_SIMULATE"):
        before = len(ctx.audit_log)
        execute_command(ctx, cmd, mode)
        after = len(ctx.audit_log)
        if after != before + 1:
            raise _violation(
                "D_007",
                f"audit_log length mismatch after {mode}: before={before} after={after}",
            )
        entry = ctx.audit_log[-1]
        for field in ("operation_id", "mode", "command", "output_hash", "metadata"):
            if field not in entry:
                raise _violation(
                    "D_007",
                    f"audit_log entry missing field '{field}': {entry}",
                )
        if entry["mode"] != mode:
            raise _violation(
                "D_007",
                f"audit_log entry mode mismatch: expected={mode} got={entry['mode']}",
            )


# ---------------------------------------------------------------------------
# D_008  test_determinism returns True for a fixed command sequence
# ---------------------------------------------------------------------------

def run_d008_test_determinism_true():
    """D_008: test_determinism returns True for a fixed seed and command list."""
    manifest = {"root_hash": sha256(b"")}
    commands = [{"file": "a.txt", "content": "Hello"}]
    result = test_determinism("seed123", manifest, commands)
    if not result:
        raise _violation(
            "D_008",
            "test_determinism returned False for a simple deterministic command",
        )


# ---------------------------------------------------------------------------
# D_009  verify_invariants: True when manifest matches repo state
# ---------------------------------------------------------------------------

def run_d009_verify_invariants_true():
    """D_009: verify_invariants returns True when manifest root_hash matches."""
    cmd = {"file": "a.txt", "content": "Hello"}
    ctx = ExecutionContext("seed", {"root_hash": sha256(b"")}, [cmd])
    execute_command(ctx, cmd, "MODE_1_EXECUTE")
    expected_root = merkle_root(ctx.repo_state)
    ctx.manifest["root_hash"] = expected_root
    if not verify_invariants(ctx):
        raise _violation(
            "D_009",
            "verify_invariants returned False despite matching manifest root_hash",
        )


def run_d009_verify_invariants_false():
    """D_009b: verify_invariants returns False when manifest root_hash mismatches."""
    cmd = {"file": "a.txt", "content": "Hello"}
    ctx = ExecutionContext("seed", {"root_hash": "deadbeef" * 8}, [cmd])
    execute_command(ctx, cmd, "MODE_1_EXECUTE")
    if verify_invariants(ctx):
        raise _violation(
            "D_009",
            "verify_invariants returned True despite mismatching manifest root_hash",
        )


# ---------------------------------------------------------------------------
# D_010  integrity_loop succeeds when manifest matches
# ---------------------------------------------------------------------------

def run_d010_integrity_loop_success():
    """D_010: integrity_loop returns True when repo state matches manifest."""
    cmd = {"file": "a.txt", "content": "Hello"}
    ctx = ExecutionContext("seed", {"root_hash": sha256(b"")}, [cmd])
    execute_command(ctx, cmd, "MODE_1_EXECUTE")
    ctx.manifest["root_hash"] = merkle_root(ctx.repo_state)
    result = integrity_loop(ctx)
    if not result:
        raise _violation(
            "D_010",
            "integrity_loop returned False despite matching manifest",
        )


def run_d010_integrity_loop_repairs():
    """D_010b: integrity_loop repairs CRLF content and succeeds."""
    crlf_content = "Hello\r\nWorld"
    canonical_content = canonicalize(crlf_content).decode('utf-8')
    expected_root = merkle_root({"a.txt": canonical_content})

    ctx = ExecutionContext("seed", {"root_hash": expected_root}, [])
    # Insert raw (non-canonical) content directly — simulating a dirty import
    ctx.repo_state["a.txt"] = crlf_content
    result = integrity_loop(ctx)
    if not result:
        raise _violation(
            "D_010",
            "integrity_loop failed to repair CRLF content",
        )


# ---------------------------------------------------------------------------
# D_011  integrity_loop enters MODE_0_HALT when invariants cannot be satisfied
# ---------------------------------------------------------------------------

def run_d011_integrity_loop_halt():
    """D_011: integrity_loop returns False when root_hash is permanently wrong."""
    cmd = {"file": "a.txt", "content": "Hello"}
    ctx = ExecutionContext("seed", {"root_hash": "0" * 64}, [cmd])
    execute_command(ctx, cmd, "MODE_1_EXECUTE")
    # manifest root_hash is '000...0' — will never match
    result = integrity_loop(ctx)
    if result is not False:
        raise _violation(
            "D_011",
            f"integrity_loop should have returned False (MODE_0_HALT), got {result!r}",
        )


# ---------------------------------------------------------------------------
# Test registry & entry point
# ---------------------------------------------------------------------------

ALL_TESTS = [
    run_d001_canonicalize_idempotent,
    run_d002_sha256_known_vector,
    run_d003_merkle_root_empty,
    run_d004_merkle_root_single_file,
    run_d005_merkle_root_two_files_stable,
    run_d006_execute_vs_simulate,
    run_d007_audit_log_entry,
    run_d008_test_determinism_true,
    run_d009_verify_invariants_true,
    run_d009_verify_invariants_false,
    run_d010_integrity_loop_success,
    run_d010_integrity_loop_repairs,
    run_d011_integrity_loop_halt,
]


def main() -> int:
    print("=" * 72)
    print("EXECUTION CONTEXT DETERMINISM TESTS")
    print(f"OS:     {sys.platform}")
    print(f"Python: {sys.version}")
    print("=" * 72)

    failures = []

    for fn in ALL_TESTS:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
        except AssertionError as exc:
            print(f"  FAIL  {fn.__name__}: {exc}")
            failures.append(fn.__name__)
        except Exception as exc:
            print(f"  ERROR {fn.__name__}: {exc}")
            failures.append(fn.__name__)

    print("=" * 72)
    if failures:
        print(f"RESULT: {len(failures)} test(s) FAILED")
        for name in failures:
            print(f"  - {name}")
        return 1

    print("RESULT: ALL DETERMINISM TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
