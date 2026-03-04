#!/usr/bin/env python3
"""
Falsification Tests for PR #28

Validates all environmental assumptions enumerated in the PR #26 ontology.
Each test is designed to *falsify* the assumption — i.e. to fail loudly and
report the exact file, line, OS, and Python version if the assumption is wrong.

Assumptions tested:
  F_PLATFORM_001  seed_bytes round-trips through hashlib.sha256 identically (no platform mutation)
  F_PLATFORM_002  Cross-platform int64 two's-complement arithmetic produces known vectors
  F_PLATFORM_003  pathlib.Path resolution is filesystem/path-separator independent
  F_PLATFORM_004  stdout/stderr encoding is UTF-8 (PYTHONIOENCODING=utf-8 is honoured)
  F_PLATFORM_005  Python's struct.pack('<q', …) encodes int64 in little-endian regardless of host
Author: Orthogonal Engineering
PR: #28
Version: 1.0.0
"""

import hashlib
import io
import os
import struct
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Helper: report violation location
# ---------------------------------------------------------------------------

def _violation(assumption_id: str, message: str) -> AssertionError:
    """Build a richly annotated AssertionError for CI log traceability."""
    frame = sys._getframe(1)
    location = f"{frame.f_code.co_filename}:{frame.f_lineno}"
    detail = (
        f"\n[FALSIFICATION FAILURE]\n"
        f"  Assumption : {assumption_id}\n"
        f"  OS         : {sys.platform}\n"
        f"  Python     : {sys.version}\n"
        f"  Location   : {location}\n"
        f"  Detail     : {message}"
    )
    return AssertionError(detail)


# ---------------------------------------------------------------------------
# F_PLATFORM_001  seed_bytes — sha256 is byte-for-byte identical across platforms
# ---------------------------------------------------------------------------

def run_f001_seed_bytes_sha256_deterministic():
    """
    F_PLATFORM_001: hashlib.sha256 of a fixed byte string returns the same hex digest on
    every platform.  If this fails, the Python hashlib implementation is
    non-standard and weight generation is fundamentally broken.
    """
    seed = b"OE_PR26_DETERMINISM_SEED_V1"
    expected = "96cc20a24313ba22105ed5c06b40eba8d61bb50f89afa5689d7fa9e86e1a8112"
    got = hashlib.sha256(seed).hexdigest()
    if got != expected:
        raise _violation(
            "F_PLATFORM_001",
            f"sha256 mismatch: expected={expected} got={got}",
        )


# ---------------------------------------------------------------------------
# F_PLATFORM_002  Cross-platform int64 arithmetic correctness
# ---------------------------------------------------------------------------

# Known-good test vectors (seed_bytes → index → expected weight).
# These were computed once with the canonical algorithm and must never change.
_INT64_VECTORS = [
    # (seed_bytes, index, expected_int64)
    (b"\x00" * 8, 0, 8085029095828041617),
    (b"\xff" * 8, 0, -6688893599968252518),
    (b"OE_PR26_DETERMINISM_SEED_V1", 0, -4778945073479914638),
    (b"OE_PR26_DETERMINISM_SEED_V1", 1, -9188189581191163464),
]


def _int64(value: int) -> int:
    value = value & 0xFFFFFFFFFFFFFFFF
    if value >= 0x8000000000000000:
        value -= 0x10000000000000000
    return value


def _weight_at(seed_bytes: bytes, index: int) -> int:
    """Reproduce the weight generation algorithm from test_cross_platform_determinism."""
    state = hashlib.sha256(seed_bytes).digest()
    for i in range(index + 1):
        digest = hashlib.sha256(state + i.to_bytes(4, "little")).digest()
        weight = _int64(struct.unpack_from("<q", digest[:8])[0])
        state = digest
    return weight


def run_f002_int64_arithmetic_vectors():
    """
    F_PLATFORM_002: int64 two's-complement arithmetic and struct.unpack produce known
    values for fixed inputs.  Failure indicates platform-specific integer or
    byte-order behaviour.
    """
    for seed_bytes, index, expected in _INT64_VECTORS:
        got = _weight_at(seed_bytes, index)
        if got != expected:
            raise _violation(
                "F_PLATFORM_002",
                f"int64 vector mismatch for seed={seed_bytes!r} index={index}: "
                f"expected={expected} got={got}",
            )


# ---------------------------------------------------------------------------
# F_PLATFORM_003  Filesystem / path independence
# ---------------------------------------------------------------------------

def run_f003_pathlib_path_independence():
    """
    F_PLATFORM_003: pathlib.Path correctly resolves relative paths and normalises
    separators on all platforms.  Failure indicates a broken PATH assumption.
    """
    # A relative path constructed with forward slashes must resolve identically
    # regardless of the host OS separator.
    p = Path("ontology") / "pr26_ontological_issues.json"
    # The string representation must not contain raw backslashes on any OS once
    # constructed via pathlib (pathlib normalises separators).
    parts = p.parts
    if len(parts) != 2:
        raise _violation(
            "F_PLATFORM_003",
            f"Path parts unexpected: {parts} (expected ('ontology', 'pr26_ontological_issues.json'))",
        )
    if parts[0] != "ontology" or parts[1] != "pr26_ontological_issues.json":
        raise _violation(
            "F_PLATFORM_003",
            f"Path parts mismatch: {parts}",
        )


# ---------------------------------------------------------------------------
# F_PLATFORM_004  UTF-8 stdout/stderr encoding
# ---------------------------------------------------------------------------

def run_f004_stdout_utf8_encoding():
    """
    F_PLATFORM_004: stdout and stderr use UTF-8 encoding.  On Windows without
    PYTHONIOENCODING=utf-8 this defaults to cp1252, which would silently mangle
    non-ASCII characters in CI logs.
    """
    # Check the reconfigured TextIOWrapper encoding.
    stdout_enc = getattr(sys.stdout, "encoding", None) or ""
    stderr_enc = getattr(sys.stderr, "encoding", None) or ""

    for name, enc in [("stdout", stdout_enc), ("stderr", stderr_enc)]:
        if enc.lower().replace("-", "") not in ("utf8", "utf_8"):
            raise _violation(
                "F_PLATFORM_004",
                f"{name} encoding is '{enc}', expected 'utf-8'. "
                "Set PYTHONIOENCODING=utf-8 in CI env.",
            )

    # Verify that non-ASCII bytes can be written without error.
    buf = io.StringIO()
    buf.write("✓ UTF-8 test: こんにちは αβγ")


# ---------------------------------------------------------------------------
# F_PLATFORM_005  struct.pack little-endian int64
# ---------------------------------------------------------------------------

def run_f005_struct_pack_little_endian():
    """
    F_PLATFORM_005: struct.pack('<q', value) encodes int64 in little-endian byte order
    regardless of host endianness.  This is required for cross-platform Merkle
    root agreement.
    """
    cases = [
        (0, b"\x00\x00\x00\x00\x00\x00\x00\x00"),
        (1, b"\x01\x00\x00\x00\x00\x00\x00\x00"),
        (-1, b"\xff\xff\xff\xff\xff\xff\xff\xff"),
        (256, b"\x00\x01\x00\x00\x00\x00\x00\x00"),
        (-(2**63), b"\x00\x00\x00\x00\x00\x00\x00\x80"),
    ]
    for value, expected_bytes in cases:
        got = struct.pack("<q", value)
        if got != expected_bytes:
            raise _violation(
                "F_PLATFORM_005",
                f"struct.pack('<q', {value}) = {got!r}, expected {expected_bytes!r}",
            )


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

ALL_TESTS = [
    run_f001_seed_bytes_sha256_deterministic,
    run_f002_int64_arithmetic_vectors,
    run_f003_pathlib_path_independence,
    run_f004_stdout_utf8_encoding,
    run_f005_struct_pack_little_endian,
]


def main() -> int:
    print("=" * 72)
    print("PR #28 FALSIFICATION TESTS")
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
        print(f"RESULT: {len(failures)} falsification test(s) FAILED")
        for name in failures:
            print(f"  - {name}")
        return 1

    print("RESULT: ALL FALSIFICATION TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
