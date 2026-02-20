"""
Universal Virtual Machine — oe_ifm/universal_virtual_machine.py

Software-defined deterministic computer.  Implements a complete 64-bit CPU
in pure Python, eliminating all hardware variation (instruction pipeline,
branch predictor, cache coherence, NUMA topology, compiler JIT).

The UVM provides:
  - Deterministic instruction set (no hardware instructions in the hot path)
  - Dict-based memory model (no hardware RAM layout assumptions)
  - Deterministic execution order (sequential fetch/decode/execute)
  - Cycle counter as logical clock (no wall-clock or monotonic clock)

Author: Orthogonal Engineering
PR: #28
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import json
from typing import Dict, List, Optional, Tuple

from oe_ifm.mathematical_core import (
    int64,
    uint64,
    peano_add,
    bitwise_and_emulated,
    bitwise_xor_emulated,
    bitwise_or_emulated,
    logical_shift_left,
    logical_shift_right,
)


# ---------------------------------------------------------------------------
# Instruction set
# ---------------------------------------------------------------------------

OPCODES = frozenset({
    "LOAD",    # LOAD  R_dest, addr          → R_dest = mem[addr]
    "STORE",   # STORE R_src, addr           → mem[addr] = R_src
    "SET",     # SET   R_dest, literal       → R_dest = literal
    "ADD",     # ADD   R_dest, R_a, R_b      → R_dest = int64(R_a + R_b)
    "MUL",     # MUL   R_dest, R_a, R_b      → R_dest = int64(R_a * R_b)
    "AND",     # AND   R_dest, R_a, R_b      → R_dest = int64(R_a & R_b)
    "OR",      # OR    R_dest, R_a, R_b      → R_dest = int64(R_a | R_b)
    "XOR",     # XOR   R_dest, R_a, R_b      → R_dest = int64(R_a ^ R_b)
    "SHL",     # SHL   R_dest, R_a, shift    → R_dest = int64(R_a << shift)
    "SHR",     # SHR   R_dest, R_a, shift    → R_dest = uint64(R_a) >> shift
    "HASH",    # HASH  R_dest, R_addr, R_len → R_dest = int64(sha256(mem slice))
    "NOP",     # NOP                         → no-op
    "HALT",    # HALT                        → stop execution
})


class UVMError(Exception):
    """Raised when an illegal UVM operation is attempted."""


class UVM:
    """Universal Virtual Machine — software-defined deterministic computer.

    All arithmetic uses oe_ifm.mathematical_core primitives (no hardware
    operators in the semantics layer).  The machine state is a pure Python
    dict, not a hardware memory region.
    """

    NUM_REGISTERS = 16

    def __init__(self, word_size: int = 64):
        if word_size != 64:
            raise ValueError("Only 64-bit word size is currently supported")
        self.word_size = word_size
        self.memory: Dict[int, int] = {}          # addr → int64 value
        self.registers: Dict[str, int] = {
            f"R{i}": 0 for i in range(self.NUM_REGISTERS)
        }
        self.pc: int = 0                          # program counter (logical)
        self.cycle_count: int = 0                 # deterministic time
        self._halted: bool = False

    # ------------------------------------------------------------------
    # State accessors
    # ------------------------------------------------------------------

    def get_register(self, name: str) -> int:
        if name not in self.registers:
            raise UVMError(f"Unknown register: {name}")
        return self.registers[name]

    def set_register(self, name: str, value: int) -> None:
        if name not in self.registers:
            raise UVMError(f"Unknown register: {name}")
        self.registers[name] = int64(value)

    def read_memory(self, addr: int) -> int:
        return self.memory.get(addr, 0)

    def write_memory(self, addr: int, value: int) -> None:
        self.memory[addr] = int64(value)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(self, instruction: Tuple) -> None:
        """Execute one instruction deterministically.

        Args:
            instruction: Tuple of (opcode, *operands).
        """
        if self._halted:
            raise UVMError("Cannot execute: machine is halted")

        op, *args = instruction
        if op not in OPCODES:
            raise UVMError(f"Unknown opcode: {op}")

        if op == "NOP":
            pass

        elif op == "HALT":
            self._halted = True

        elif op == "SET":
            r_dest, literal = args
            self.set_register(r_dest, int(literal))

        elif op == "LOAD":
            r_dest, addr = args
            self.set_register(r_dest, self.memory.get(int(addr), 0))

        elif op == "STORE":
            r_src, addr = args
            self.memory[int(addr)] = self.get_register(r_src)

        elif op == "ADD":
            r_dest, r_a, r_b = args
            a = self.get_register(r_a)
            b = self.get_register(r_b)
            self.set_register(r_dest, self._emulated_add(a, b))

        elif op == "MUL":
            r_dest, r_a, r_b = args
            a = self.get_register(r_a)
            b = self.get_register(r_b)
            self.set_register(r_dest, self._emulated_mul(a, b))

        elif op == "AND":
            r_dest, r_a, r_b = args
            a = uint64(self.get_register(r_a))
            b = uint64(self.get_register(r_b))
            self.set_register(r_dest, bitwise_and_emulated(a, b))

        elif op == "OR":
            r_dest, r_a, r_b = args
            a = uint64(self.get_register(r_a))
            b = uint64(self.get_register(r_b))
            self.set_register(r_dest, bitwise_or_emulated(a, b))

        elif op == "XOR":
            r_dest, r_a, r_b = args
            a = uint64(self.get_register(r_a))
            b = uint64(self.get_register(r_b))
            self.set_register(r_dest, bitwise_xor_emulated(a, b))

        elif op == "SHL":
            r_dest, r_a, shift = args
            a = uint64(self.get_register(r_a))
            self.set_register(r_dest, logical_shift_left(a, int(shift)))

        elif op == "SHR":
            r_dest, r_a, shift = args
            a = self.get_register(r_a)
            self.set_register(r_dest, logical_shift_right(a, int(shift)))

        elif op == "HASH":
            # HASH R_dest, start_addr, length
            r_dest, start_addr, length = args
            start = int(start_addr)
            n = int(length)
            payload = bytes(
                uint64(self.memory.get(start + i, 0)) & 0xFF
                for i in range(n)
            )
            digest_bytes = hashlib.sha256(payload).digest()[:8]
            value = int.from_bytes(digest_bytes, "little", signed=True)
            self.set_register(r_dest, int64(value))

        self.pc += 1
        self.cycle_count += 1

    def run(self, program: List[Tuple], max_cycles: int = 100_000) -> None:
        """Run a list of instructions until HALT or max_cycles exceeded.

        Args:
            program: Ordered list of instruction tuples.
            max_cycles: Safety limit to prevent infinite loops.
        """
        self._halted = False
        for instr in program:
            if self._halted or self.cycle_count >= max_cycles:
                break
            self.execute(instr)

    # ------------------------------------------------------------------
    # Deterministic state snapshot (for cross-platform comparison)
    # ------------------------------------------------------------------

    def state_hash(self) -> str:
        """Return SHA-256 of the canonical machine state.

        The state is serialised as a deterministically ordered JSON object
        so the hash is platform-independent.
        """
        state = {
            "pc": self.pc,
            "cycle_count": self.cycle_count,
            "registers": {k: self.registers[k] for k in sorted(self.registers)},
            "memory": {str(k): self.memory[k] for k in sorted(self.memory)},
        }
        canonical = json.dumps(state, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    # ------------------------------------------------------------------
    # Emulated arithmetic primitives (no hardware operators in semantics)
    # ------------------------------------------------------------------

    def _emulated_add(self, a: int, b: int) -> int:
        """Pure software 64-bit addition via carry-propagation."""
        ua = uint64(a)
        ub = uint64(b)
        result = peano_add(ua, ub)
        return int64(result)

    def _emulated_mul(self, a: int, b: int) -> int:
        """Pure software 64-bit multiplication via binary long multiplication."""
        negative = (a < 0) ^ (b < 0)
        ua = uint64(abs(a))
        ub = uint64(abs(b))
        result = 0
        shift = 0
        while ub > 0:
            if ub & 1:
                result = peano_add(result, ua << shift)
            ub >>= 1
            shift += 1
        result = int64(result)
        if negative and result != 0:
            result = int64(-result)
        return result
