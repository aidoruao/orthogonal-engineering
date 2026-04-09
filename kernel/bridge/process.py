"""Process Bridge — Spawn external processes via capability.

The kernel does not implement the external process.
It grants a capability to spawn, then mediates the result.

Yeshua Inversion: Don't implement process management. Mediate spawning.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Optional, Dict
from fractions import Fraction

from axioms.logic import ProofObject


@dataclass(frozen=True)
class ProcessCap:
    """Capability to spawn external processes."""
    process_id: str
    max_processes: int  # Maximum number of processes this cap can spawn
    allowed_binaries: frozenset  # Set of allowed binary hashes
    resource_quota: Fraction  # Maximum resources per spawned process


@dataclass
class ExternalProcess:
    """An external process spawned via capability."""
    pid: str
    parent_id: str  # Process that spawned this one
    binary_hash: str
    resources_granted: Fraction
    spawn_time: Fraction


@dataclass
class ProcessBridgeState:
    """State of the process bridge."""
    caps: Dict[str, List[ProcessCap]] = field(default_factory=dict)
    spawned: List[ExternalProcess] = field(default_factory=list)
    spawn_count: Dict[str, int] = field(default_factory=dict)  # process_id -> count


def spawn_external(state: ProcessBridgeState,
                  process_id: str,
                  binary_hash: str,
                  resources: Fraction,
                  cap: ProcessCap) -> Tuple[ProcessBridgeState, Optional[str], ProofObject]:
    """Spawn external process. Capability-gated.
    
    Args:
        state: Current process bridge state
        process_id: Process doing the spawning
        binary_hash: Hash of binary to spawn
        resources: Resources to grant to spawned process
        cap: Process capability
    
    Returns:
        (new_state, spawned_pid, proof)
        spawned_pid is None if spawn failed
    """
    # Verify process holds this cap
    process_caps = state.caps.get(process_id, [])
    if cap not in process_caps:
        return state, None, ProofObject(
            rule="SpawnExternal",
            premises=[f"process={process_id}", "cap not held"],
            conclusion="spawn denied: invalid capability"
        )
    
    # Check binary allowlist
    if binary_hash not in cap.allowed_binaries:
        return state, None, ProofObject(
            rule="SpawnExternal",
            premises=[
                f"binary={binary_hash[:16]}...",
                "not in allowlist"
            ],
            conclusion="spawn denied: binary not allowed"
        )
    
    # Check spawn limit
    current_count = state.spawn_count.get(process_id, 0)
    if current_count >= cap.max_processes:
        return state, None, ProofObject(
            rule="SpawnExternal",
            premises=[
                f"count={current_count}",
                f"limit={cap.max_processes}"
            ],
            conclusion="spawn denied: process limit exceeded"
        )
    
    # Check resource quota
    if resources > cap.resource_quota:
        return state, None, ProofObject(
            rule="SpawnExternal",
            premises=[
                f"requested={resources}",
                f"quota={cap.resource_quota}"
            ],
            conclusion="spawn denied: resource quota exceeded"
        )
    
    # Spawn process
    spawned_pid = f"spawned_{process_id}_{current_count}"
    new_process = ExternalProcess(
        pid=spawned_pid,
        parent_id=process_id,
        binary_hash=binary_hash,
        resources_granted=resources,
        spawn_time=Fraction(0)  # Would use actual time
    )
    
    new_spawned = state.spawned + [new_process]
    new_count = state.spawn_count.copy()
    new_count[process_id] = current_count + 1
    
    new_state = ProcessBridgeState(
        caps=state.caps,
        spawned=new_spawned,
        spawn_count=new_count
    )
    
    proof = ProofObject(
        rule="SpawnExternal",
        premises=[
            f"parent={process_id}",
            f"child={spawned_pid}",
            f"binary={binary_hash[:16]}...",
            f"resources={resources}"
        ],
        conclusion="process spawned"
    )
    
    return new_state, spawned_pid, proof
