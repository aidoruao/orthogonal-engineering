#!/usr/bin/env python3
"""
Syscall Interface — Userland to kernel boundary

System calls are the only way userland processes interact with the kernel.
Every syscall is capability-gated and returns a ProofObject.

Mathematical Foundation:
  - axioms/process_algebra.py — syscalls as CSP events
  - axioms/logic.py — pre/postcondition verification
  - axioms/capability_security.py — capability checking

Philosophy: "The syscall boundary is the veil between userland desire and kernel truth"

Biblical: Hebrews 10:20 — "By a new and living way opened for us through
  the curtain, that is, his body."
  The syscall is the curtain — the boundary between worlds.
"""

from .interface import SyscallTable, SyscallNumber, SyscallHandler
from .capability_check import CapabilityChecker, SyscallAudit

__all__ = [
    "SyscallTable",
    "SyscallNumber",
    "SyscallHandler",
    "CapabilityChecker",
    "SyscallAudit",
]
