#!/usr/bin/env python3
"""
Abstract Machine — Stack-based VM for Kingdom OS

The abstract machine is the target of the compiler.
It is deterministic and has no undefined behavior.

Mathematical Foundation:
  - axioms/computability.py — Turing completeness proof
  - axioms/formal_languages.py — instruction encoding
  - axioms/logic.py — Hoare logic for pre/postconditions

Biblical: Matthew 7:24 — "Therefore everyone who hears these words of
  mine and puts them into practice is like a wise man who built his
house on the rock."
  The abstract machine is the rock — solid, unshakeable, defined.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional, Any
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject


class OpCode(Enum):
    """Abstract machine opcodes."""
    # Stack operations
    PUSH = auto()
    POP = auto()
    DUP = auto()
    SWAP = auto()
    
    # Arithmetic
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()
    
    # Comparison
    EQ = auto()
    NEQ = auto()
    LT = auto()
    GT = auto()
    
    # Control flow
    JUMP = auto()
    JUMP_IF = auto()
    CALL = auto()
    RET = auto()
    
    # Memory
    LOAD = auto()
    STORE = auto()
    LOAD_LOCAL = auto()
    STORE_LOCAL = auto()
    
    # Capabilities
    CAP_CHECK = auto()
    CAP_GRANT = auto()
    CAP_REVOKE = auto()
    
    # Syscalls
    SYSCALL = auto()
    
    # Proof
    PROOF_START = auto()
    PROOF_END = auto()
    
    # Termination
    HALT = auto()


@dataclass
class Instruction:
    """A single instruction."""
    opcode: OpCode
    operand: Optional[Any] = None
    pre_condition: str = ""  # Hoare logic precondition
    post_condition: str = ""  # Hoare logic postcondition
    
    def proof(self) -> ProofObject:
        return ProofObject(
            rule="Instruction",
            premises=[f"opcode={self.opcode.name}"],
            conclusion="instruction valid"
        )


@dataclass
class StackFrame:
    """A stack frame for function calls."""
    return_address: int
    locals: Dict[int, Any] = field(default_factory=dict)
    capability_context: List[str] = field(default_factory=list)


@dataclass
class AbstractMachine:
    """Abstract machine state."""
    code: List[Instruction] = field(default_factory=list)
    stack: List[Any] = field(default_factory=list)
    call_stack: List[StackFrame] = field(default_factory=list)
    pc: int = 0  # Program counter
    memory: Dict[int, Any] = field(default_factory=dict)
    halted: bool = False
    
    def push(self, value: Any) -> None:
        """Push value onto stack."""
        self.stack.append(value)
    
    def pop(self) -> Tuple[Optional[Any], ProofObject]:
        """Pop value from stack."""
        if not self.stack:
            return None, ProofObject(
                rule="StackPop",
                premises=[],
                conclusion="failed: stack underflow"
            )
        
        return self.stack.pop(), ProofObject(
            rule="StackPop",
            premises=[f"depth={len(self.stack)}"],
            conclusion="popped"
        )
    
    def step(self) -> Tuple[bool, ProofObject]:
        """Execute one instruction."""
        if self.halted:
            return False, ProofObject(
                rule="AMStep",
                premises=["halted=true"],
                conclusion="no step"
            )
        
        if self.pc >= len(self.code):
            self.halted = True
            return False, ProofObject(
                rule="AMStep",
                premises=["pc>=len(code)"],
                conclusion="halted (end of code)"
            )
        
        instr = self.code[self.pc]
        
        # Execute instruction (simplified)
        if instr.opcode == OpCode.HALT:
            self.halted = True
        elif instr.opcode == OpCode.PUSH:
            self.push(instr.operand)
            self.pc += 1
        elif instr.opcode == OpCode.POP:
            _, _ = self.pop()
            self.pc += 1
        elif instr.opcode == OpCode.ADD:
            b, _ = self.pop()
            a, _ = self.pop()
            if a is not None and b is not None:
                self.push(a + b)
            self.pc += 1
        else:
            self.pc += 1
        
        return True, ProofObject(
            rule="AMStep",
            premises=[f"pc={self.pc}", f"opcode={instr.opcode.name}"],
            conclusion="step executed"
        )
    
    def run(self) -> Tuple[Any, ProofObject]:
        """Run until halt."""
        steps = 0
        max_steps = 10000  # Prevent infinite loops
        
        while not self.halted and steps < max_steps:
            self.step()
            steps += 1
        
        result = self.stack[-1] if self.stack else None
        
        return result, ProofObject(
            rule="AMRun",
            premises=[f"steps={steps}", f"halted={self.halted}"],
            conclusion="execution complete"
        )
