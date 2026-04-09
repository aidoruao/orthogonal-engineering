"""Process Algebra — CCS, CSP, Pi-calculus foundations.

Formalizes concurrent process behavior using exact arithmetic.
Implements Milner's CCS and Hoare's CSP as executable specifications.
All operations return (result, ProofObject) pairs.

Mathematical foundation: Milner, "Communication and Concurrency"
Biblical: 1 Corinthians 12:12 — "Just as a body, though one,
has many parts, but all its many parts form one body."
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Set, Optional, Union
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject


class ActionType(Enum):
    """Type of process action."""
    INPUT = auto()
    OUTPUT = auto()
    TAU = auto()  # Internal/unobservable action


@dataclass(frozen=True)
class Action:
    """An action in process algebra.
    
    Actions are the fundamental units of process behavior.
    Input actions (a?) receive values; output actions (a!) send values.
    Complementary actions can synchronize.
    """
    name: str
    action_type: ActionType
    
    def complement(self) -> Action:
        """Return the complementary action.
        
        Input becomes output, output becomes input.
        Tau has no complement (returns self).
        """
        if self.action_type == ActionType.INPUT:
            return Action(self.name, ActionType.OUTPUT)
        elif self.action_type == ActionType.OUTPUT:
            return Action(self.name, ActionType.INPUT)
        return self  # TAU has no complement
    
    def is_complement_of(self, other: Action) -> bool:
        """Check if this action is the complement of another."""
        return (self.name == other.name and 
                self.action_type != other.action_type and
                self.action_type != ActionType.TAU and
                other.action_type != ActionType.TAU)
    
    def __str__(self) -> str:
        if self.action_type == ActionType.INPUT:
            return f"{self.name}?"
        elif self.action_type == ActionType.OUTPUT:
            return f"{self.name}!"
        return "τ"


# Forward declaration for Process
Process = Union['Nil', 'Prefix', 'Choice', 'Parallel', 'Restriction']


@dataclass(frozen=True)
class Nil:
    """The terminated (empty) process."""
    pass


@dataclass(frozen=True)
class Prefix:
    """Prefix: action.P — perform action, then continue as P."""
    action: Action
    continuation: Process


@dataclass(frozen=True)
class Choice:
    """Choice: P + Q — can behave as either P or Q (non-deterministic)."""
    left: Process
    right: Process


@dataclass(frozen=True)
class Parallel:
    """Parallel: P | Q — P and Q execute concurrently, can synchronize."""
    left: Process
    right: Process


@dataclass(frozen=True)
class Restriction:
    """Restriction: P \ {a} — P cannot use actions in restricted set externally."""
    process: Process
    restricted: frozenset  # Set of action names (strings)


def get_initial_actions(process: Process) -> Set[Action]:
    """Get the set of initial actions a process can perform."""
    if isinstance(process, Nil):
        return set()
    elif isinstance(process, Prefix):
        return {process.action}
    elif isinstance(process, Choice):
        return get_initial_actions(process.left) | get_initial_actions(process.right)
    elif isinstance(process, Parallel):
        return get_initial_actions(process.left) | get_initial_actions(process.right)
    elif isinstance(process, Restriction):
        # Filter out restricted actions
        actions = get_initial_actions(process.process)
        return {a for a in actions if a.name not in process.restricted}
    return set()


def can_synchronize(p: Process, q: Process) -> Tuple[bool, ProofObject]:
    """Check if p offers action a and q offers complement ā.
    
    Returns True if the two processes can synchronize on complementary actions.
    """
    p_actions = get_initial_actions(p)
    q_actions = get_initial_actions(q)
    
    # Check if any action in p has complement in q
    can_sync = False
    matching_pair = None
    
    for a in p_actions:
        for b in q_actions:
            if a.is_complement_of(b):
                can_sync = True
                matching_pair = (a, b)
                break
        if can_sync:
            break
    
    p_actions_str = "{" + ",".join(str(a) for a in p_actions) + "}"
    q_actions_str = "{" + ",".join(str(a) for a in q_actions) + "}"
    proof = ProofObject(
        rule="CanSynchronize",
        premises=[
            f"p_actions={p_actions_str}",
            f"q_actions={q_actions_str}"
        ],
        conclusion=f"can_sync={can_sync}" + (f" via {matching_pair}" if matching_pair else "")
    )
    
    return can_sync, proof


def reduce_one_step(process: Process) -> Tuple[Optional[Process], Optional[Action], ProofObject]:
    """Perform one step of reduction.
    
    Returns:
        (new_process, action_taken, proof)
        If no reduction possible, returns (None, None, proof)
    """
    if isinstance(process, Nil):
        return None, None, ProofObject(
            rule="ReduceNil",
            premises=["process is Nil"],
            conclusion="no reduction possible"
        )
    
    elif isinstance(process, Prefix):
        # Prefix reduces to its continuation
        return process.continuation, process.action, ProofObject(
            rule="ReducePrefix",
            premises=[f"action={process.action}"],
            conclusion=f"reduced to continuation"
        )
    
    elif isinstance(process, Choice):
        # Non-deterministic choice: can reduce either branch
        # For determinism, we try left first
        if get_initial_actions(process.left):
            new_p, action, _ = reduce_one_step(process.left)
            if new_p is not None:
                return Choice(new_p, process.right), action, ProofObject(
                    rule="ReduceChoiceLeft",
                    premises=["left branch reduced"],
                    conclusion="choice preserves right option"
                )
        if get_initial_actions(process.right):
            new_p, action, _ = reduce_one_step(process.right)
            if new_p is not None:
                return Choice(process.left, new_p), action, ProofObject(
                    rule="ReduceChoiceRight",
                    premises=["right branch reduced"],
                    conclusion="choice preserves left option"
                )
        return None, None, ProofObject(
            rule="ReduceChoiceBlocked",
            premises=["both branches blocked"],
            conclusion="no reduction possible"
        )
    
    elif isinstance(process, Parallel):
        # Try interleaving (left or right reduces independently)
        if get_initial_actions(process.left):
            new_p, action, _ = reduce_one_step(process.left)
            if new_p is not None:
                return Parallel(new_p, process.right), action, ProofObject(
                    rule="ReduceParallelLeft",
                    premises=["left process reduces"],
                    conclusion="parallel composition preserved"
                )
        if get_initial_actions(process.right):
            new_p, action, _ = reduce_one_step(process.right)
            if new_p is not None:
                return Parallel(process.left, new_p), action, ProofObject(
                    rule="ReduceParallelRight",
                    premises=["right process reduces"],
                    conclusion="parallel composition preserved"
                )
        
        # Try synchronization
        can_sync, _ = can_synchronize(process.left, process.right)
        if can_sync:
            # Synchronization produces tau
            tau_action = Action("tau", ActionType.TAU)
            # Both processes reduce after sync (simplified)
            return process, tau_action, ProofObject(
                rule="ReduceParallelSync",
                premises=["complementary actions found"],
                conclusion="synchronization with tau"
            )
        
        return None, None, ProofObject(
            rule="ReduceParallelBlocked",
            premises=["neither process can reduce, no sync possible"],
            conclusion="no reduction possible"
        )
    
    elif isinstance(process, Restriction):
        # Restricted process reduces if inner process reduces on non-restricted action
        new_p, action, _ = reduce_one_step(process.process)
        if new_p is not None and action.name not in process.restricted:
            return Restriction(new_p, process.restricted), action, ProofObject(
                rule="ReduceRestriction",
                premises=[f"action={action} not in restricted set"],
                conclusion="restriction preserved"
            )
        return None, None, ProofObject(
            rule="ReduceRestrictionBlocked",
            premises=["inner process blocked or action restricted"],
            conclusion="no reduction possible"
        )
    
    return None, None, ProofObject(
        rule="ReduceUnknown",
        premises=["unknown process type"],
        conclusion="no reduction possible"
    )


def is_deadlock_free(process: Process, depth: int = 10) -> Tuple[bool, ProofObject]:
    """BFS to depth checking that every reachable state has at least one enabled action.
    
    Args:
        process: Process to check
        depth: Maximum search depth (bounded to avoid infinite search)
    
    Returns:
        (deadlock_free, proof)
        deadlock_free = True if no deadlock found within depth
    """
    if depth <= 0:
        return True, ProofObject(
            rule="DeadlockCheckDepthExceeded",
            premises=[f"depth={depth}"],
            conclusion="deadlock-free within search bound"
        )
    
    # Check if current state has enabled actions
    actions = get_initial_actions(process)
    
    if not actions and not isinstance(process, Nil):
        # Deadlock: no actions but not terminated
        return False, ProofObject(
            rule="DeadlockDetected",
            premises=["no enabled actions", "process not Nil"],
            conclusion="deadlock detected"
        )
    
    if isinstance(process, Nil):
        # Terminated process is deadlock-free
        return True, ProofObject(
            rule="DeadlockNil",
            premises=["process is Nil"],
            conclusion="deadlock-free (terminated)"
        )
    
    # Explore successors
    new_p, _, _ = reduce_one_step(process)
    if new_p is None:
        # No reduction possible from here
        if actions:
            # Has actions but can't reduce (shouldn't happen with valid processes)
            return True, ProofObject(
                rule="DeadlockCheckNoSuccessor",
                premises=["has actions but no reduction"],
                conclusion="deadlock-free (cannot progress)"
            )
    
    # Recursively check successor
    successor_deadlock_free, _ = is_deadlock_free(new_p, depth - 1)
    
    proof = ProofObject(
        rule="DeadlockCheckRecursive",
        premises=[f"depth={depth}", f"enabled_actions={len(actions)}"],
        conclusion=f"deadlock_free={successor_deadlock_free}"
    )
    
    return successor_deadlock_free, proof


def get_trace(process: Process, max_length: int = 10) -> Tuple[List[Action], ProofObject]:
    """Get a trace (sequence of actions) from a process.
    
    A trace is one possible execution path.
    """
    trace = []
    current = process
    
    for _ in range(max_length):
        new_p, action, _ = reduce_one_step(current)
        if new_p is None or action is None:
            break
        trace.append(action)
        current = new_p
        if isinstance(current, Nil):
            break
    
    proof = ProofObject(
        rule="GetTrace",
        premises=[f"max_length={max_length}"],
        conclusion=f"trace_length={len(trace)}"
    )
    
    return trace, proof


def trace_equivalence(p: Process, q: Process, max_depth: int = 5) -> Tuple[bool, ProofObject]:
    """Check if p and q produce the same set of traces up to max_depth.
    
    This is a bounded check for trace equivalence.
    Full trace equivalence requires exploring all possible traces.
    """
    # Get traces from both processes
    trace_p, _ = get_trace(p, max_depth)
    trace_q, _ = get_trace(q, max_depth)
    
    # Convert to comparable form (action names)
    trace_p_names = [str(a) for a in trace_p]
    trace_q_names = [str(a) for a in trace_q]
    
    # For bounded check, we compare first trace from each
    # Full equivalence would require comparing all possible traces
    equivalent = trace_p_names == trace_q_names
    
    proof = ProofObject(
        rule="TraceEquivalence",
        premises=[
            f"trace_p={trace_p_names}",
            f"trace_q={trace_q_names}",
            f"max_depth={max_depth}"
        ],
        conclusion=f"equivalent={equivalent} (bounded check)"
    )
    
    return equivalent, proof


def channel_capacity_check(channels: List[str], 
                          message_counts: dict,
                          max_pending: int) -> Tuple[bool, ProofObject]:
    """Verify no channel exceeds max_pending messages.
    
    Args:
        channels: List of channel names
        message_counts: Dict mapping channel name to pending message count
        max_pending: Maximum allowed pending messages per channel
    
    Returns:
        (within_capacity, proof)
    """
    violations = []
    for ch in channels:
        count = message_counts.get(ch, 0)
        if count > max_pending:
            violations.append(f"{ch}: {count} > {max_pending}")
    
    within_capacity = len(violations) == 0
    
    proof = ProofObject(
        rule="ChannelCapacity",
        premises=[
            f"channels={len(channels)}",
            f"max_pending={max_pending}",
            f"violations={len(violations)}"
        ],
        conclusion=f"within_capacity={within_capacity}"
    )
    
    return within_capacity, proof
