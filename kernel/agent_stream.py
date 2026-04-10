"""Agent Stream — Symbolic Subagent Spawning with Lazy Evaluation

Symbolic subagent spawning with AgentCap.
Lazy evaluation — agents only materialize when observed.
Copy-on-write forking — fork state without full copy.
Billion agents at near-zero marginal cost (Fraction accounting).

Mathematical foundation: Symbolic computation + COW state management.
Standard: Capability-gated spawning, deterministic materialization.
Biblical: Matthew 25:15 — "To one he gave five talents, to another two, to another one."
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Optional, Dict, Callable, Any, FrozenSet
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject
from axioms.capability_security import Capability, Permission


class AgentState(Enum):
    """Agent lifecycle states."""
    SYMBOLIC = auto()     # Not yet materialized (lazy)
    MATERIALIZED = auto() # Fully materialized and running
    SUSPENDED = auto()    # Materialized but paused
    TERMINATED = auto()   # Completed or killed


class MaterializationTrigger(Enum):
    """Events that trigger agent materialization."""
    OBSERVATION = auto()  # External observation request
    MESSAGE = auto()      # Message sent to agent
    SCHEDULER = auto()    # Scheduler selected agent
    CAPABILITY = auto()   # Capability delegation requiring verification


@dataclass
class AgentCapability:
    """Capability-specific metadata for agents."""
    can_spawn: bool = False
    can_delegate: bool = False
    can_terminate: bool = False
    max_spawns: int = 0  # Maximum subagents this agent can spawn


@dataclass(frozen=True)
class AgentCap:
    """Capability token for agent operations.
    
    Grants specific permissions:
    - SPAWN: Can create subagents
    - OBSERVE: Can observe agent state (may trigger materialization)
    - FORK: Can fork agent state (COW)
    - TERMINATE: Can terminate agent
    
    All operations are capability-gated.
    """
    agent_id: str
    holder_id: str
    permissions: frozenset
    delegator: str
    resource_quota: Fraction  # Resource allocation for this agent
    spawn_depth: int = 0  # Nesting depth (0 = root)
    attenuations: Tuple[str, ...] = field(default_factory=tuple)
    
    def has_permission(self, perm: Permission) -> bool:
        """Check if capability has specific permission."""
        return perm in self.permissions
    
    def can_spawn_at_depth(self, max_depth: int = 10) -> bool:
        """Check if agent can spawn subagents at current depth."""
        return self.spawn_depth < max_depth and self.has_permission(Permission.WRITE)


@dataclass
class SymbolicAgent:
    """A lazily-evaluated (symbolic) agent.
    
    Agents exist in symbolic form until observed.
    Materialization is deterministic and witnessed.
    """
    agent_id: str
    parent_id: Optional[str]  # None for root agents
    state: AgentState
    
    # Symbolic representation (before materialization)
    intent_hash: str  # Hash of agent's purpose/function
    capability_set: FrozenSet[AgentCap]
    
    # Resource accounting
    memory_quota: Fraction
    cpu_quota: Fraction
    spawn_quota: int  # Max subagents this agent can spawn
    
    # Lazy evaluation
    materialized_pid: Optional[str] = None  # Process ID if materialized
    materialization_trigger: Optional[MaterializationTrigger] = None
    materialization_time: Optional[Fraction] = None
    
    # COW forking support
    fork_parent: Optional[str] = None  # Parent agent in fork chain
    cow_layers: List[str] = field(default_factory=list)  # COW layer IDs


@dataclass
class AgentStreamState:
    """Complete agent stream subsystem state."""
    # agent_id -> SymbolicAgent
    agents: Dict[str, SymbolicAgent] = field(default_factory=dict)
    
    # COW state layers: layer_id -> Dict[str, Any] (state deltas)
    cow_layers: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Spawn counters for resource accounting
    spawn_count: int = 0
    materialized_count: int = 0
    
    # Resource totals (Fraction for precision)
    total_memory_allocated: Fraction = field(default_factory=lambda: Fraction(0))
    total_cpu_allocated: Fraction = field(default_factory=lambda: Fraction(0))
    
    def get_agent(self, agent_id: str) -> Optional[SymbolicAgent]:
        """Get agent by ID."""
        return self.agents.get(agent_id)
    
    def get_active_agents(self) -> List[SymbolicAgent]:
        """Get all non-terminated agents."""
        return [
            a for a in self.agents.values()
            if a.state != AgentState.TERMINATED
        ]
    
    def get_symbolic_count(self) -> int:
        """Count symbolic (non-materialized) agents."""
        return sum(
            1 for a in self.agents.values()
            if a.state == AgentState.SYMBOLIC
        )
    
    def get_materialized_count(self) -> int:
        """Count materialized agents."""
        return sum(
            1 for a in self.agents.values()
            if a.state == AgentState.MATERIALIZED
        )


def spawn_agent(
    state: AgentStreamState,
    parent_cap: AgentCap,
    intent_hash: str,
    memory_quota: Fraction,
    cpu_quota: Fraction,
    timestamp: Fraction,
    parent_id: Optional[str] = None
) -> Tuple[AgentStreamState, Optional[SymbolicAgent], ProofObject]:
    """Spawn a new symbolic subagent.
    
    Agents are created in SYMBOLIC state (lazy evaluation).
    Materialization happens only when observed.
    
    Args:
        state: Current agent stream state
        parent_cap: Parent's capability (must have SPAWN permission)
        intent_hash: Hash of agent's purpose/function
        memory_quota: Memory allocation (Fraction)
        cpu_quota: CPU allocation (Fraction)
        timestamp: Spawn timestamp
        parent_id: Parent agent ID (None for root)
        
    Returns:
        (new_state, agent, proof)
        agent is None if spawn failed
    """
    # Verify spawn permission
    if not parent_cap.has_permission(Permission.WRITE):
        return state, None, ProofObject(
            rule="SpawnAgent",
            premises=[
                f"parent={parent_cap.holder_id}",
                f"permissions={parent_cap.permissions}"
            ],
            conclusion="spawn failed: no WRITE permission"
        )
    
    # Check spawn depth limit
    max_depth = 10
    if parent_cap.spawn_depth >= max_depth:
        return state, None, ProofObject(
            rule="SpawnAgent",
            premises=[
                f"spawn_depth={parent_cap.spawn_depth}",
                f"max_depth={max_depth}"
            ],
            conclusion="spawn failed: maximum nesting depth exceeded"
        )
    
    # Generate agent ID (content-addressed)
    import hashlib
    agent_id_input = f"{parent_id}:{intent_hash}:{timestamp}:{state.spawn_count}"
    agent_id = f"agent_{hashlib.sha256(agent_id_input.encode()).hexdigest()[:16]}"
    
    # Create agent capability for the new agent
    agent_cap = AgentCap(
        agent_id=agent_id,
        holder_id=agent_id,
        permissions=frozenset([Permission.READ, Permission.WRITE, Permission.DELEGATE]),
        delegator=parent_cap.holder_id,
        resource_quota=memory_quota,
        spawn_depth=parent_cap.spawn_depth + 1,
        attenuations=parent_cap.attenuations + (f"spawned_by:{parent_cap.holder_id}",)
    )
    
    # Create symbolic agent
    agent = SymbolicAgent(
        agent_id=agent_id,
        parent_id=parent_id,
        state=AgentState.SYMBOLIC,
        intent_hash=intent_hash,
        capability_set=frozenset([agent_cap]),
        memory_quota=memory_quota,
        cpu_quota=cpu_quota,
        spawn_quota=100  # Default: can spawn 100 subagents
    )
    
    # Update state
    new_agents = state.agents.copy()
    new_agents[agent_id] = agent
    
    new_state = AgentStreamState(
        agents=new_agents,
        cow_layers=state.cow_layers,
        spawn_count=state.spawn_count + 1,
        materialized_count=state.materialized_count,
        total_memory_allocated=state.total_memory_allocated + memory_quota,
        total_cpu_allocated=state.total_cpu_allocated + cpu_quota
    )
    
    return new_state, agent, ProofObject(
        rule="SpawnAgent",
        premises=[
            f"agent_id={agent_id}",
            f"parent={parent_id}",
            f"intent_hash={intent_hash}",
            f"memory_quota={memory_quota}",
            f"cpu_quota={cpu_quota}",
            f"spawn_depth={agent_cap.spawn_depth}"
        ],
        conclusion="symbolic agent spawned"
    )


def materialize_agent(
    state: AgentStreamState,
    agent_id: str,
    trigger: MaterializationTrigger,
    timestamp: Fraction,
    observer_cap: AgentCap
) -> Tuple[AgentStreamState, bool, ProofObject]:
    """Materialize a symbolic agent when observed.
    
    Materialization converts a symbolic agent into a running process.
    This is the core of lazy evaluation — agents only materialize when needed.
    
    Args:
        state: Current agent stream state
        agent_id: Agent to materialize
        trigger: What triggered materialization
        timestamp: Materialization timestamp
        observer_cap: Capability of observer (must have OBSERVE permission)
        
    Returns:
        (new_state, success, proof)
    """
    # Verify observation permission
    if not observer_cap.has_permission(Permission.READ):
        return state, False, ProofObject(
            rule="MaterializeAgent",
            premises=[f"agent={agent_id}"],
            conclusion="materialization failed: no READ permission"
        )
    
    agent = state.get_agent(agent_id)
    if agent is None:
        return state, False, ProofObject(
            rule="MaterializeAgent",
            premises=[f"agent={agent_id}"],
            conclusion="materialization failed: agent not found"
        )
    
    if agent.state == AgentState.MATERIALIZED:
        return state, True, ProofObject(
            rule="MaterializeAgent",
            premises=[f"agent={agent_id}"],
            conclusion="already materialized"
        )
    
    if agent.state == AgentState.TERMINATED:
        return state, False, ProofObject(
            rule="MaterializeAgent",
            premises=[f"agent={agent_id}", f"state={agent.state.name}"],
            conclusion="materialization failed: agent terminated"
        )
    
    # Generate process ID
    import hashlib
    pid_input = f"{agent_id}:{timestamp}:{trigger.name}"
    process_id = f"pid_{hashlib.sha256(pid_input.encode()).hexdigest()[:12]}"
    
    # Update agent to materialized state
    materialized_agent = SymbolicAgent(
        agent_id=agent.agent_id,
        parent_id=agent.parent_id,
        state=AgentState.MATERIALIZED,
        intent_hash=agent.intent_hash,
        capability_set=agent.capability_set,
        memory_quota=agent.memory_quota,
        cpu_quota=agent.cpu_quota,
        spawn_quota=agent.spawn_quota,
        materialized_pid=process_id,
        materialization_trigger=trigger,
        materialization_time=timestamp,
        fork_parent=agent.fork_parent,
        cow_layers=agent.cow_layers.copy()
    )
    
    new_agents = state.agents.copy()
    new_agents[agent_id] = materialized_agent
    
    new_state = AgentStreamState(
        agents=new_agents,
        cow_layers=state.cow_layers,
        spawn_count=state.spawn_count,
        materialized_count=state.materialized_count + 1,
        total_memory_allocated=state.total_memory_allocated,
        total_cpu_allocated=state.total_cpu_allocated
    )
    
    return new_state, True, ProofObject(
        rule="MaterializeAgent",
        premises=[
            f"agent_id={agent_id}",
            f"process_id={process_id}",
            f"trigger={trigger.name}",
            f"timestamp={timestamp}"
        ],
        conclusion="agent materialized"
    )


def fork_agent_cow(
    state: AgentStreamState,
    agent_id: str,
    forker_cap: AgentCap,
    timestamp: Fraction,
    cow_memory_delta: Optional[Fraction] = None
) -> Tuple[AgentStreamState, Optional[SymbolicAgent], ProofObject]:
    """Fork an agent using copy-on-write (COW).
    
    COW forking creates a new agent that shares state with parent
    until either modifies it. This enables near-zero-cost forking.
    
    Args:
        state: Current agent stream state
        agent_id: Agent to fork
        forker_cap: Capability of forker
        timestamp: Fork timestamp
        cow_memory_delta: Additional memory for COW layer
        
    Returns:
        (new_state, forked_agent, proof)
    """
    agent = state.get_agent(agent_id)
    if agent is None:
        return state, None, ProofObject(
            rule="ForkAgentCOW",
            premises=[f"agent={agent_id}"],
            conclusion="fork failed: agent not found"
        )
    
    # Verify fork permission (WRITE on parent or DELEGATE)
    if not forker_cap.has_permission(Permission.WRITE):
        return state, None, ProofObject(
            rule="ForkAgentCOW",
            premises=[f"forker={forker_cap.holder_id}"],
            conclusion="fork failed: no WRITE permission"
        )
    
    # Generate fork ID
    import hashlib
    fork_id_input = f"{agent_id}:{timestamp}:{state.spawn_count}"
    fork_id = f"agent_fork_{hashlib.sha256(fork_id_input.encode()).hexdigest()[:12]}"
    
    # Create COW layer
    cow_layer_id = f"cow_{fork_id}"
    cow_quota = cow_memory_delta if cow_memory_delta else Fraction(0)
    
    # Create forked agent
    forked_agent = SymbolicAgent(
        agent_id=fork_id,
        parent_id=agent_id,
        state=AgentState.SYMBOLIC,  # Fork starts symbolic
        intent_hash=agent.intent_hash,
        capability_set=agent.capability_set,  # Shared capabilities
        memory_quota=agent.memory_quota + cow_quota,
        cpu_quota=agent.cpu_quota,
        spawn_quota=agent.spawn_quota,
        fork_parent=agent_id,
        cow_layers=agent.cow_layers + [cow_layer_id]
    )
    
    # Create COW layer
    new_cow_layers = state.cow_layers.copy()
    new_cow_layers[cow_layer_id] = {
        "parent_agent": agent_id,
        "fork_agent": fork_id,
        "created_at": timestamp,
        "delta_memory": cow_quota,
        "state_delta": {}  # Empty initially (pure COW)
    }
    
    # Update state
    new_agents = state.agents.copy()
    new_agents[fork_id] = forked_agent
    
    new_state = AgentStreamState(
        agents=new_agents,
        cow_layers=new_cow_layers,
        spawn_count=state.spawn_count + 1,
        materialized_count=state.materialized_count,
        total_memory_allocated=state.total_memory_allocated + cow_quota,
        total_cpu_allocated=state.total_cpu_allocated
    )
    
    return new_state, forked_agent, ProofObject(
        rule="ForkAgentCOW",
        premises=[
            f"parent_agent={agent_id}",
            f"fork_agent={fork_id}",
            f"cow_layer={cow_layer_id}",
            f"cow_quota={cow_quota}"
        ],
        conclusion="agent forked with COW"
    )


def terminate_agent(
    state: AgentStreamState,
    agent_id: str,
    terminator_cap: AgentCap,
    timestamp: Fraction
) -> Tuple[AgentStreamState, bool, ProofObject]:
    """Terminate an agent.
    
    Args:
        state: Current agent stream state
        agent_id: Agent to terminate
        terminator_cap: Capability of terminator
        timestamp: Termination timestamp
        
    Returns:
        (new_state, success, proof)
    """
    agent = state.get_agent(agent_id)
    if agent is None:
        return state, False, ProofObject(
            rule="TerminateAgent",
            premises=[f"agent={agent_id}"],
            conclusion="termination failed: agent not found"
        )
    
    # Verify termination permission
    can_terminate = (
        terminator_cap.has_permission(Permission.REVOKE) or
        agent.parent_id == terminator_cap.holder_id  # Parent can always terminate child
    )
    
    if not can_terminate:
        return state, False, ProofObject(
            rule="TerminateAgent",
            premises=[f"terminator={terminator_cap.holder_id}"],
            conclusion="termination failed: insufficient permission"
        )
    
    # Update agent to terminated
    terminated_agent = SymbolicAgent(
        agent_id=agent.agent_id,
        parent_id=agent.parent_id,
        state=AgentState.TERMINATED,
        intent_hash=agent.intent_hash,
        capability_set=frozenset(),  # Clear capabilities
        memory_quota=Fraction(0),
        cpu_quota=Fraction(0),
        spawn_quota=0,
        materialized_pid=agent.materialized_pid,
        materialization_time=agent.materialization_time,
        fork_parent=agent.fork_parent,
        cow_layers=agent.cow_layers
    )
    
    new_agents = state.agents.copy()
    new_agents[agent_id] = terminated_agent
    
    # Reclaim resources
    reclaimed_memory = agent.memory_quota
    reclaimed_cpu = agent.cpu_quota
    
    new_state = AgentStreamState(
        agents=new_agents,
        cow_layers=state.cow_layers,
        spawn_count=state.spawn_count,
        materialized_count=state.materialized_count - (1 if agent.state == AgentState.MATERIALIZED else 0),
        total_memory_allocated=state.total_memory_allocated - reclaimed_memory,
        total_cpu_allocated=state.total_cpu_allocated - reclaimed_cpu
    )
    
    return new_state, True, ProofObject(
        rule="TerminateAgent",
        premises=[
            f"agent_id={agent_id}",
            f"previous_state={agent.state.name}",
            f"reclaimed_memory={reclaimed_memory}"
        ],
        conclusion="agent terminated"
    )


def check_agent_resource_usage(
    state: AgentStreamState,
    agent_id: str
) -> Tuple[Optional[Tuple[Fraction, Fraction]], ProofObject]:
    """Check resource usage of an agent.
    
    Args:
        state: Agent stream state
        agent_id: Agent to check
        
    Returns:
        ((memory, cpu), proof) or (None, proof) if not found
    """
    agent = state.get_agent(agent_id)
    if agent is None:
        return None, ProofObject(
            rule="CheckAgentResourceUsage",
            premises=[f"agent={agent_id}"],
            conclusion="check failed: agent not found"
        )
    
    return (agent.memory_quota, agent.cpu_quota), ProofObject(
        rule="CheckAgentResourceUsage",
        premises=[
            f"agent_id={agent_id}",
            f"state={agent.state.name}",
            f"memory_quota={agent.memory_quota}",
            f"cpu_quota={agent.cpu_quota}",
            f"cow_layers={len(agent.cow_layers)}"
        ],
        conclusion="resource usage retrieved"
    )


def get_agent_statistics(state: AgentStreamState) -> Tuple[Dict[str, Any], ProofObject]:
    """Get aggregate statistics about the agent stream.
    
    Returns:
        (stats, proof)
    """
    stats = {
        "total_agents": len(state.agents),
        "symbolic_count": state.get_symbolic_count(),
        "materialized_count": state.get_materialized_count(),
        "active_agents": len(state.get_active_agents()),
        "total_spawns": state.spawn_count,
        "total_memory_allocated": state.total_memory_allocated,
        "total_cpu_allocated": state.total_cpu_allocated,
        "cow_layers": len(state.cow_layers)
    }
    
    return stats, ProofObject(
        rule="GetAgentStatistics",
        premises=[
            f"total_agents={stats['total_agents']}",
            f"symbolic={stats['symbolic_count']}",
            f"materialized={stats['materialized_count']}"
        ],
        conclusion="statistics retrieved"
    )


def observe_agent_state(
    state: AgentStreamState,
    agent_id: str,
    observer_cap: AgentCap,
    timestamp: Fraction
) -> Tuple[AgentStreamState, Optional[SymbolicAgent], ProofObject]:
    """Observe an agent, triggering materialization if symbolic.
    
    This is the primary interface for lazy evaluation — observation
    causes materialization.
    
    Args:
        state: Current agent stream state
        agent_id: Agent to observe
        observer_cap: Observer's capability
        timestamp: Observation timestamp
        
    Returns:
        (new_state, agent, proof)
    """
    agent = state.get_agent(agent_id)
    if agent is None:
        return state, None, ProofObject(
            rule="ObserveAgentState",
            premises=[f"agent={agent_id}"],
            conclusion="observation failed: agent not found"
        )
    
    # If already materialized, just return
    if agent.state == AgentState.MATERIALIZED:
        return state, agent, ProofObject(
            rule="ObserveAgentState",
            premises=[f"agent={agent_id}", "state=MATERIALIZED"],
            conclusion="observed already-materialized agent"
        )
    
    # If symbolic, materialize first
    if agent.state == AgentState.SYMBOLIC:
        new_state, success, materialize_proof = materialize_agent(
            state, agent_id, MaterializationTrigger.OBSERVATION, timestamp, observer_cap
        )
        
        if not success:
            return state, None, ProofObject(
                rule="ObserveAgentState",
                premises=[f"agent={agent_id}", f"materialize_error={materialize_proof.conclusion}"],
                conclusion="observation failed: materialization failed"
            )
        
        observed_agent = new_state.get_agent(agent_id)
        return new_state, observed_agent, ProofObject(
            rule="ObserveAgentState",
            premises=[
                f"agent={agent_id}",
                f"previous_state=SYMBOLIC",
                f"materialize_proof={materialize_proof.proof_hash}"
            ],
            conclusion="observed and materialized agent"
        )
    
    # Suspended or terminated
    return state, agent, ProofObject(
        rule="ObserveAgentState",
        premises=[f"agent={agent_id}", f"state={agent.state.name}"],
        conclusion=f"observed agent in {agent.state.name} state"
    )
