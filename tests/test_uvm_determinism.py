#!/usr/bin/env python3
"""
UVM Determinism Tests — tests/test_uvm_determinism.py

Standalone test suite that exercises the Universal Virtual Machine across a
comprehensive set of programs.  Designed to be run on every CI runner
(Ubuntu / macOS / Windows × Python 3.11 / 3.12) so that the UVM state hash
can be compared cross-platform.

Each test program is small enough to execute quickly but exercises a
different part of the UVM instruction set.

Author: Orthogonal Engineering
PR: #28
Version: 1.0.0
"""

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from oe_ifm.universal_virtual_machine import UVM, UVMError


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def run_program(program):
    """Run a UVM program and return the final state hash."""
    uvm = UVM()
    uvm.run(program)
    return uvm.state_hash()


# ---------------------------------------------------------------------------
# Test programs
# ---------------------------------------------------------------------------

_PROG_ARITHMETIC = [
    ("SET", "R0", 1_000_000),
    ("SET", "R1", 999_999),
    ("ADD", "R2", "R0", "R1"),     # 1_999_999
    ("MUL", "R3", "R2", "R0"),     # 1_999_999_000_000
    ("SET", "R4", -1),
    ("ADD", "R5", "R0", "R4"),     # 999_999
    ("HALT",),
]

_PROG_BITWISE = [
    ("SET", "R0", 0xFF00FF00FF00FF00 & 0xFFFFFFFFFFFFFFFF),
    ("SET", "R1", 0x00FF00FF00FF00FF),
    ("AND", "R2", "R0", "R1"),     # 0
    ("OR",  "R3", "R0", "R1"),     # 0xFFFFFFFFFFFFFFFF
    ("XOR", "R4", "R0", "R1"),     # 0xFFFFFFFFFFFFFFFF
    ("SHL", "R5", "R1", 4),
    ("SHR", "R6", "R0", 8),
    ("HALT",),
]

_PROG_MEMORY = [
    ("SET",   "R0", 12345),
    ("STORE", "R0", 100),
    ("SET",   "R1", 67890),
    ("STORE", "R1", 200),
    ("LOAD",  "R2", 100),          # R2 = 12345
    ("LOAD",  "R3", 200),          # R3 = 67890
    ("ADD",   "R4", "R2", "R3"),   # R4 = 80235
    ("STORE", "R4", 300),
    ("LOAD",  "R5", 300),          # R5 = 80235
    ("HALT",),
]

_PROG_INT64_OVERFLOW = [
    ("SET", "R0", 2**62),
    ("SET", "R1", 2**62),
    ("ADD", "R2", "R0", "R1"),     # wraps: 2^63 → -(2^63)
    ("SET", "R3", -(2**63)),
    ("SET", "R4", -1),
    ("ADD", "R5", "R3", "R4"),     # wraps: -(2^63)-1 → 2^63-1
    ("HALT",),
]

_PROG_HASH_INSTRUCTION = [
    ("SET",   "R0", 0x41),         # 'A'
    ("STORE", "R0", 0),
    ("SET",   "R0", 0x42),         # 'B'
    ("STORE", "R0", 1),
    ("SET",   "R0", 0x43),         # 'C'
    ("STORE", "R0", 2),
    ("HASH",  "R1", 0, 3),         # sha256("ABC")[:8] as int64
    ("HALT",),
]

_PROG_NOP_SEQUENCE = [
    ("NOP",),
    ("NOP",),
    ("SET", "R0", 7),
    ("NOP",),
    ("SET", "R1", 3),
    ("MUL", "R2", "R0", "R1"),     # 21
    ("NOP",),
    ("HALT",),
]


# ---------------------------------------------------------------------------
# Determinism tests
# ---------------------------------------------------------------------------

def test_uvm_arithmetic_deterministic():
    """Arithmetic program produces identical state hash across two runs."""
    h1 = run_program(_PROG_ARITHMETIC)
    h2 = run_program(_PROG_ARITHMETIC)
    assert h1 == h2, f"Arithmetic program non-deterministic: {h1} != {h2}"


def test_uvm_bitwise_deterministic():
    """Bitwise program produces identical state hash across two runs."""
    h1 = run_program(_PROG_BITWISE)
    h2 = run_program(_PROG_BITWISE)
    assert h1 == h2, f"Bitwise program non-deterministic: {h1} != {h2}"


def test_uvm_memory_deterministic():
    """Memory load/store program produces identical state hash across two runs."""
    h1 = run_program(_PROG_MEMORY)
    h2 = run_program(_PROG_MEMORY)
    assert h1 == h2, f"Memory program non-deterministic: {h1} != {h2}"


def test_uvm_int64_overflow_deterministic():
    """Int64 overflow wrap-around is deterministic."""
    h1 = run_program(_PROG_INT64_OVERFLOW)
    h2 = run_program(_PROG_INT64_OVERFLOW)
    assert h1 == h2, f"Overflow program non-deterministic: {h1} != {h2}"


def test_uvm_hash_instruction_deterministic():
    """HASH instruction produces identical state hash across two runs."""
    h1 = run_program(_PROG_HASH_INSTRUCTION)
    h2 = run_program(_PROG_HASH_INSTRUCTION)
    assert h1 == h2, f"HASH instruction non-deterministic: {h1} != {h2}"


def test_uvm_nop_sequence_deterministic():
    """NOP-padded program produces identical state hash."""
    h1 = run_program(_PROG_NOP_SEQUENCE)
    h2 = run_program(_PROG_NOP_SEQUENCE)
    assert h1 == h2, f"NOP sequence non-deterministic: {h1} != {h2}"


def test_uvm_register_correctness():
    """Verify register values are arithmetically correct after execution."""
    uvm = UVM()
    uvm.run(_PROG_ARITHMETIC)
    assert uvm.get_register("R2") == 1_999_999
    assert uvm.get_register("R3") == 1_999_999_000_000
    assert uvm.get_register("R5") == 999_999


def test_uvm_memory_correctness():
    """Verify memory values are correct after load/store program."""
    uvm = UVM()
    uvm.run(_PROG_MEMORY)
    assert uvm.get_register("R2") == 12345
    assert uvm.get_register("R3") == 67890
    assert uvm.get_register("R5") == 80235


def test_uvm_illegal_opcode():
    """Executing an unknown opcode raises UVMError."""
    uvm = UVM()
    try:
        uvm.execute(("INVALID_OP",))
        assert False, "Expected UVMError was not raised"
    except UVMError:
        pass


def test_uvm_halt_stops_execution():
    """Instructions after HALT are not executed."""
    uvm = UVM()
    uvm.run([
        ("SET", "R0", 1),
        ("HALT",),
        ("SET", "R0", 2),     # should not execute
    ])
    assert uvm.get_register("R0") == 1, (
        f"Instruction after HALT was executed: R0={uvm.get_register('R0')}"
    )


# ---------------------------------------------------------------------------
# Cross-platform attestation (writes state hash for CI comparison)
# ---------------------------------------------------------------------------

def test_uvm_write_cross_platform_state_hash():
    """Write UVM state hashes to merkle_roots/ for CI cross-OS comparison."""
    programs = {
        "arithmetic": _PROG_ARITHMETIC,
        "bitwise": _PROG_BITWISE,
        "memory": _PROG_MEMORY,
        "overflow": _PROG_INT64_OVERFLOW,
    }

    out_dir = Path(__file__).parent.parent / "merkle_roots"
    out_dir.mkdir(parents=True, exist_ok=True)

    combined = ""
    for name, prog in sorted(programs.items()):
        h = run_program(prog)
        combined += f"{name}:{h}\n"
        print(f"  [uvm] {name} state_hash={h}")

    # Write a single file with all UVM hashes for this platform
    platform_tag = sys.platform
    out_path = out_dir / f"pr28_uvm_state_{platform_tag}.txt"
    out_path.write_text(combined, encoding="utf-8")
    print(f"  [uvm] Written to {out_path}")


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

ALL_TESTS = [
    test_uvm_arithmetic_deterministic,
    test_uvm_bitwise_deterministic,
    test_uvm_memory_deterministic,
    test_uvm_int64_overflow_deterministic,
    test_uvm_hash_instruction_deterministic,
    test_uvm_nop_sequence_deterministic,
    test_uvm_register_correctness,
    test_uvm_memory_correctness,
    test_uvm_illegal_opcode,
    test_uvm_halt_stops_execution,
    test_uvm_write_cross_platform_state_hash,
]


def main() -> int:
    print("=" * 72)
    print("PR #28 UVM DETERMINISM TESTS")
    print(f"OS:     {sys.platform}")
    print(f"Python: {sys.version}")
    print("=" * 72)

    failures = []
    for fn in ALL_TESTS:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
        except Exception as exc:
            print(f"  FAIL  {fn.__name__}: {exc}")
            failures.append(fn.__name__)

    print("=" * 72)
    if failures:
        print(f"RESULT: {len(failures)} test(s) FAILED")
        for name in failures:
            print(f"  - {name}")
        return 1

    print(f"RESULT: ALL {len(ALL_TESTS)} UVM TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
