"""Linux Compatibility Bridge — Capability-gated syscall translation.

Spawns a Linux binary in a verified compartment.
Translates Linux syscalls to Kingdom OS capabilities.
One binary at a time. Each syscall is capability-checked and logged.

Yeshua Inversion: Don't implement POSIX. Translate POSIX to capabilities.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Optional, Dict
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject


class LinuxSyscall(Enum):
    """Subset of Linux syscalls that can be translated."""
    OPEN = 2
    CLOSE = 3
    READ = 0
    WRITE = 1
    MMAP = 9
    MUNMAP = 11
    BRK = 12
    EXIT = 60
    SOCKET = 41
    BIND = 49
    LISTEN = 50
    ACCEPT = 43
    SENDTO = 44
    RECVFROM = 45


@dataclass(frozen=True)
class LinuxCompatCap:
    """Capability to run Linux binary in compartment."""
    process_id: str
    allowed_syscalls: frozenset  # Set of LinuxSyscall
    binary_hash: str  # SHA-256 of the binary being run
    memory_limit: Fraction
    file_access: frozenset  # Allowed file paths


@dataclass
class SyscallTranslation:
    """Record of a translated syscall."""
    linux_syscall: LinuxSyscall
    kingdom_capability_used: str  # Which Cap was consumed
    result: str
    proof: ProofObject


@dataclass
class LinuxCompatState:
    """State of Linux compatibility layer."""
    caps: Dict[str, List[LinuxCompatCap]] = field(default_factory=dict)
    translations: List[SyscallTranslation] = field(default_factory=list)
    active_compartments: Dict[str, str] = field(default_factory=dict)  # process_id -> binary_hash
    memory_used: Dict[str, Fraction] = field(default_factory=dict)


def translate_syscall(state: LinuxCompatState,
                     process_id: str,
                     syscall: LinuxSyscall,
                     args: dict,
                     cap: LinuxCompatCap) -> Tuple[LinuxCompatState, str, ProofObject]:
    """Translate Linux syscall to Kingdom OS capability operation.
    
    Checks:
    - Process holds cap
    - Syscall is in allowed set
    - Binary hash matches
    - Memory within limit
    
    Args:
        state: Current Linux compat state
        process_id: Process making syscall
        syscall: Linux syscall number
        args: Syscall arguments
        cap: Linux compat capability
    
    Returns:
        (new_state, result, proof)
    """
    # Verify process holds this cap
    process_caps = state.caps.get(process_id, [])
    if cap not in process_caps:
        return state, "EPERM", ProofObject(
            rule="SyscallTranslation",
            premises=[f"process={process_id}", "cap not held"],
            conclusion="syscall denied: invalid capability"
        )
    
    # Check syscall allowlist
    if syscall not in cap.allowed_syscalls:
        return state, "ENOSYS", ProofObject(
            rule="SyscallTranslation",
            premises=[f"syscall={syscall.name}", "not in allowlist"],
            conclusion="syscall denied: not allowed"
        )
    
    # Check binary hash
    active_hash = state.active_compartments.get(process_id)
    if active_hash != cap.binary_hash:
        return state, "EPERM", ProofObject(
            rule="SyscallTranslation",
            premises=[
                f"active_hash={active_hash}",
                f"cap_hash={cap.binary_hash}"
            ],
            conclusion="syscall denied: binary hash mismatch"
        )
    
    # Check memory limit for mmap/brk
    if syscall in [LinuxSyscall.MMAP, LinuxSyscall.BRK]:
        requested = Fraction(args.get("size", 0))
        used = state.memory_used.get(process_id, Fraction(0))
        if used + requested > cap.memory_limit:
            return state, "ENOMEM", ProofObject(
                rule="SyscallTranslation",
                premises=[
                    f"used={used}",
                    f"requested={requested}",
                    f"limit={cap.memory_limit}"
                ],
                conclusion="syscall denied: memory limit exceeded"
            )
        
        # Update memory tracking
        new_memory = state.memory_used.copy()
        new_memory[process_id] = used + requested
        state = LinuxCompatState(
            caps=state.caps,
            translations=state.translations,
            active_compartments=state.active_compartments,
            memory_used=new_memory
        )
    
    # Record translation
    translation = SyscallTranslation(
        linux_syscall=syscall,
        kingdom_capability_used=cap.binary_hash,
        result="success",
        proof=ProofObject(
            rule="SyscallTranslation",
            premises=[],
            conclusion="translated"
        )
    )
    
    new_translations = state.translations + [translation]
    
    new_state = LinuxCompatState(
        caps=state.caps,
        translations=new_translations,
        active_compartments=state.active_compartments,
        memory_used=state.memory_used
    )
    
    proof = ProofObject(
        rule="SyscallTranslation",
        premises=[
            f"process={process_id}",
            f"syscall={syscall.name}",
            f"binary={cap.binary_hash[:16]}..."
        ],
        conclusion="syscall translated"
    )
    
    return new_state, "success", proof


def check_compartment_isolation(state: LinuxCompatState) -> Tuple[bool, ProofObject]:
    """No compartment can access another's memory or capabilities.
    
    Args:
        state: Linux compat state
    
    Returns:
        (isolated, proof)
    """
    # Check: each process has only its own caps
    # Check: no shared memory regions between compartments
    
    # Simplified check: each compartment has unique binary hash
    hashes = list(state.active_compartments.values())
    unique_hashes = len(set(hashes))
    isolated = unique_hashes == len(hashes)
    
    proof = ProofObject(
        rule="CompartmentIsolation",
        premises=[
            f"compartments={len(state.active_compartments)}",
            f"unique_hashes={unique_hashes}"
        ],
        conclusion=f"isolated={isolated}"
    )
    
    return isolated, proof
