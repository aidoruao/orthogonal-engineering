#!/usr/bin/env python3
"""
Syscall Interface — Core system call table and handlers

This module defines the system call interface for Kingdom OS.
Every syscall takes (args, capability) and returns (result, ProofObject).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional, Any, Callable
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject
from axioms.capability_security import Capability


class SyscallNumber(Enum):
    """System call numbers."""
    # Process management
    EXIT = 0
    FORK = 1
    EXEC = 2
    WAIT = 3
    GETPID = 4
    
    # Memory management
    MMAP = 10
    MUNMAP = 11
    MPROTECT = 12
    BRK = 13
    
    # File operations
    OPEN = 20
    CLOSE = 21
    READ = 22
    WRITE = 23
    LSEEK = 24
    STAT = 25
    
    # IPC
    SEND_IPC = 30
    RECV_IPC = 31
    CREATE_CHANNEL = 32
    
    # Capabilities
    GRANT_CAP = 40
    REVOKE_CAP = 41
    CHECK_CAP = 42
    
    # Agents
    SPAWN_AGENT = 50
    WAIT_AGENT = 51
    
    # Time
    GET_TIME = 60
    SLEEP = 61
    
    # Identity
    GET_IDENTITY = 70
    ATTEST_IDENTITY = 71


@dataclass(frozen=True)
class SyscallHandler:
    """A system call handler."""
    number: SyscallNumber
    name: str
    arg_count: int
    handler_fn: str  # Symbol name
    time_bound_ms: Fraction  # Maximum execution time
    
    def proof(self) -> ProofObject:
        return ProofObject(
            rule="SyscallHandler",
            premises=[
                f"num={self.number.value}",
                f"name={self.name}",
                f"args={self.arg_count}",
            ],
            conclusion="handler registered"
        )


@dataclass
class SyscallTable:
    """Table of system call handlers."""
    handlers: Dict[SyscallNumber, SyscallHandler] = field(default_factory=dict)
    audit_log: List[Dict] = field(default_factory=list)
    
    def register(
        self,
        handler: SyscallHandler
    ) -> Tuple[bool, ProofObject]:
        """Register a syscall handler."""
        self.handlers[handler.number] = handler
        
        return True, ProofObject(
            rule="SyscallRegister",
            premises=[f"num={handler.number.value}", f"name={handler.name}"],
            conclusion="syscall registered"
        )
    
    def dispatch(
        self,
        number: SyscallNumber,
        args: Tuple[Any, ...],
        capability: Capability,
        process_id: str
    ) -> Tuple[Any, ProofObject]:
        """Dispatch a system call.
        
        This is the entry point from userland.
        """
        handler = self.handlers.get(number)
        
        if handler is None:
            return None, ProofObject(
                rule="SyscallDispatch",
                premises=[f"num={number.value}", f"pid={process_id}"],
                conclusion="failed: no handler"
            )
        
        # Log the syscall
        self.audit_log.append({
            "number": number.value,
            "name": handler.name,
            "process_id": process_id,
            "capability": capability.target if capability else None,
        })
        
        # Abstract dispatch
        return {"status": "dispatched", "handler": handler.name}, ProofObject(
            rule="SyscallDispatch",
            premises=[
                f"num={number.value}",
                f"name={handler.name}",
                f"pid={process_id}",
                f"args={len(args)}",
            ],
            conclusion="syscall dispatched"
        )
    
    def get_audit_log(self) -> Tuple[List[Dict], ProofObject]:
        """Get syscall audit log."""
        return self.audit_log, ProofObject(
            rule="SyscallGetAudit",
            premises=[f"entries={len(self.audit_log)}"],
            conclusion="audit log retrieved"
        )
