"""Deterministic Process Scheduler.

Uses process algebra (axioms/process_algebra.py) to model
scheduling as a formal reduction system. No randomness.
Priority is a Fraction. Ties broken by lexicographic process ID.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Optional
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject
from axioms.capability_security import Capability


class ProcessState(Enum):
    """Process execution states."""
    READY = auto()
    RUNNING = auto()
    BLOCKED = auto()
    TERMINATED = auto()


@dataclass
class ProcessDescriptor:
    """Description of a process in the system."""
    pid: str
    priority: Fraction
    state: ProcessState
    capability_set: List[Capability]
    memory_quota: Fraction  # In bytes (as Fraction for precision)
    cpu_quota: Fraction     # CPU time units
    cpu_used: Fraction = field(default_factory=lambda: Fraction(0))
    vruntime: Fraction = field(default_factory=lambda: Fraction(0))  # For CFS-like fairness
    
    def __lt__(self, other: ProcessDescriptor) -> bool:
        """Compare processes for scheduling (lower vruntime = higher priority)."""
        if self.vruntime != other.vruntime:
            return self.vruntime < other.vruntime
        # Tie-break by lexicographic pid
        return self.pid < other.pid


@dataclass
class SchedulerState:
    """Complete state of the scheduler."""
    ready_queue: List[ProcessDescriptor] = field(default_factory=list)
    running: Optional[ProcessDescriptor] = None
    blocked: List[ProcessDescriptor] = field(default_factory=list)
    tick: Fraction = field(default_factory=lambda: Fraction(0))
    time_slice: Fraction = field(default_factory=lambda: Fraction(1))  # Default 1 unit
    
    def get_all_processes(self) -> List[ProcessDescriptor]:
        """Get all processes in the system."""
        all_procs = self.ready_queue.copy()
        if self.running:
            all_procs.append(self.running)
        all_procs.extend(self.blocked)
        return all_procs


def schedule_next(state: SchedulerState) -> Tuple[SchedulerState, ProofObject]:
    """Deterministically select the next process to run.
    
    Uses CFS-like scheduling: lowest vruntime wins.
    Ties broken by lexicographic pid for determinism.
    
    Args:
        state: Current scheduler state
    
    Returns:
        (new_state, proof)
    """
    if not state.ready_queue and not state.running:
        # No processes to schedule
        return state, ProofObject(
            rule="Schedule",
            premises=["empty ready queue", "no running process"],
            conclusion="no scheduling possible"
        )
    
    # If there's a running process, put it back in ready queue
    new_ready = state.ready_queue.copy()
    if state.running and state.running.state != ProcessState.TERMINATED:
        # Update vruntime based on time slice
        updated_proc = ProcessDescriptor(
            pid=state.running.pid,
            priority=state.running.priority,
            state=ProcessState.READY,
            capability_set=state.running.capability_set,
            memory_quota=state.running.memory_quota,
            cpu_quota=state.running.cpu_quota,
            cpu_used=state.running.cpu_used + state.time_slice,
            vruntime=state.running.vruntime + state.time_slice / state.running.priority
        )
        new_ready.append(updated_proc)
    
    if not new_ready:
        return state, ProofObject(
            rule="Schedule",
            premises=["no ready processes after update"],
            conclusion="scheduler idle"
        )
    
    # Sort by vruntime (lowest first), tie-break by pid
    new_ready.sort(key=lambda p: (p.vruntime, p.pid))
    
    # Pick the first process
    next_proc = new_ready[0]
    remaining_ready = new_ready[1:]
    
    # Set it to running
    running_proc = ProcessDescriptor(
        pid=next_proc.pid,
        priority=next_proc.priority,
        state=ProcessState.RUNNING,
        capability_set=next_proc.capability_set,
        memory_quota=next_proc.memory_quota,
        cpu_quota=next_proc.cpu_quota,
        cpu_used=next_proc.cpu_used,
        vruntime=next_proc.vruntime
    )
    
    new_state = SchedulerState(
        ready_queue=remaining_ready,
        running=running_proc,
        blocked=state.blocked,
        tick=state.tick + Fraction(1),
        time_slice=state.time_slice
    )
    
    proof = ProofObject(
        rule="Schedule",
        premises=[
            f"ready_count={len(remaining_ready) + 1}",
            f"selected_pid={running_proc.pid}",
            f"vruntime={running_proc.vruntime}"
        ],
        conclusion=f"scheduled {running_proc.pid}"
    )
    
    return new_state, proof


def check_no_starvation(history: List[SchedulerState],
                       pid: str,
                       window: int) -> Tuple[bool, ProofObject]:
    """Check that a process was scheduled at least once in the last `window` ticks.
    
    Args:
        history: List of scheduler states over time
        pid: Process ID to check
        window: Number of ticks to look back
    
    Returns:
        (no_starvation, proof)
    """
    if not history:
        return True, ProofObject(
            rule="NoStarvation",
            premises=["empty history"],
            conclusion="no starvation (no history)"
        )
    
    # Look at last `window` states
    recent = history[-window:] if len(history) >= window else history
    
    # Check if pid was running in any of these states
    was_scheduled = any(
        state.running and state.running.pid == pid
        for state in recent
    )
    
    no_starvation = was_scheduled
    
    proof = ProofObject(
        rule="NoStarvation",
        premises=[
            f"pid={pid}",
            f"window={window}",
            f"history_len={len(recent)}",
            f"was_scheduled={was_scheduled}"
        ],
        conclusion=f"no_starvation={no_starvation}"
    )
    
    return no_starvation, proof


def check_quota_enforcement(process: ProcessDescriptor,
                           used_cpu: Fraction) -> Tuple[bool, ProofObject]:
    """Check that process has not exceeded its CPU quota.
    
    Args:
        process: Process to check
        used_cpu: Actual CPU time used
    
    Returns:
        (within_quota, proof)
    """
    within_quota = used_cpu <= process.cpu_quota
    
    proof = ProofObject(
        rule="QuotaEnforcement",
        premises=[
            f"pid={process.pid}",
            f"used={used_cpu}",
            f"quota={process.cpu_quota}"
        ],
        conclusion=f"within_quota={within_quota}"
    )
    
    return within_quota, proof


def block_process(state: SchedulerState, pid: str) -> Tuple[SchedulerState, ProofObject]:
    """Move a process from running to blocked state.
    
    Args:
        state: Current scheduler state
        pid: Process ID to block
    
    Returns:
        (new_state, proof)
    """
    if state.running and state.running.pid == pid:
        blocked_proc = ProcessDescriptor(
            pid=state.running.pid,
            priority=state.running.priority,
            state=ProcessState.BLOCKED,
            capability_set=state.running.capability_set,
            memory_quota=state.running.memory_quota,
            cpu_quota=state.running.cpu_quota,
            cpu_used=state.running.cpu_used,
            vruntime=state.running.vruntime
        )
        
        new_blocked = state.blocked + [blocked_proc]
        
        new_state = SchedulerState(
            ready_queue=state.ready_queue,
            running=None,
            blocked=new_blocked,
            tick=state.tick,
            time_slice=state.time_slice
        )
        
        proof = ProofObject(
            rule="BlockProcess",
            premises=[f"pid={pid}"],
            conclusion="process blocked"
        )
        
        return new_state, proof
    
    return state, ProofObject(
        rule="BlockProcess",
        premises=[f"pid={pid} not running"],
        conclusion="no change"
    )


def unblock_process(state: SchedulerState, pid: str) -> Tuple[SchedulerState, ProofObject]:
    """Move a process from blocked to ready state.
    
    Args:
        state: Current scheduler state
        pid: Process ID to unblock
    
    Returns:
        (new_state, proof)
    """
    for i, proc in enumerate(state.blocked):
        if proc.pid == pid:
            unblocked_proc = ProcessDescriptor(
                pid=proc.pid,
                priority=proc.priority,
                state=ProcessState.READY,
                capability_set=proc.capability_set,
                memory_quota=proc.memory_quota,
                cpu_quota=proc.cpu_quota,
                cpu_used=proc.cpu_used,
                vruntime=proc.vruntime
            )
            
            new_blocked = state.blocked[:i] + state.blocked[i+1:]
            new_ready = state.ready_queue + [unblocked_proc]
            
            new_state = SchedulerState(
                ready_queue=new_ready,
                running=state.running,
                blocked=new_blocked,
                tick=state.tick,
                time_slice=state.time_slice
            )
            
            proof = ProofObject(
                rule="UnblockProcess",
                premises=[f"pid={pid}"],
                conclusion="process unblocked"
            )
            
            return new_state, proof
    
    return state, ProofObject(
        rule="UnblockProcess",
        premises=[f"pid={pid} not in blocked queue"],
        conclusion="no change"
    )
