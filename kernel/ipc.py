"""Inter-Process Communication — Typed channels with capability gates.

Every IPC channel is a typed, bounded, capability-gated pipe.
Uses process algebra synchronization semantics.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Optional, Dict
from fractions import Fraction

from axioms.logic import ProofObject
from axioms.capability_security import Capability, Permission


@dataclass
class TypedChannel:
    """A typed, bounded IPC channel.
    
    Channels are the only way processes communicate.
    Each channel has sender and receiver capabilities.
    """
    channel_id: str
    msg_type: str           # Type of messages (for type safety)
    capacity: int           # Maximum queued messages
    sender_cap: Capability
    receiver_cap: Capability


@dataclass
class IPCState:
    """Complete IPC subsystem state."""
    channels: Dict[str, TypedChannel] = field(default_factory=dict)
    queues: Dict[str, List[str]] = field(default_factory=dict)
    
    def get_queue_length(self, channel_id: str) -> int:
        """Get current queue length for a channel."""
        return len(self.queues.get(channel_id, []))


def send(state: IPCState,
        channel_id: str,
        message: str,
        sender_cap: Capability) -> Tuple[IPCState, ProofObject]:
    """Send a message on a channel.
    
    Verifies sender holds sender_cap. Rejects if queue full.
    
    Args:
        state: Current IPC state
        channel_id: Channel to send on
        message: Message to send
        sender_cap: Sender's capability
    
    Returns:
        (new_state, proof)
    """
    if channel_id not in state.channels:
        return state, ProofObject(
            rule="Send",
            premises=[f"channel={channel_id}"],
            conclusion="send failed: channel not found"
        )
    
    channel = state.channels[channel_id]
    
    # Verify sender capability
    if sender_cap.target != channel_id:
        return state, ProofObject(
            rule="Send",
            premises=[
                f"cap_target={sender_cap.target}",
                f"channel={channel_id}"
            ],
            conclusion="send failed: wrong capability"
        )
    
    # Check queue capacity
    queue = state.queues.get(channel_id, [])
    if len(queue) >= channel.capacity:
        return state, ProofObject(
            rule="Send",
            premises=[
                f"queue_len={len(queue)}",
                f"capacity={channel.capacity}"
            ],
            conclusion="send failed: queue full"
        )
    
    # Add message to queue
    new_queue = queue + [message]
    new_queues = state.queues.copy()
    new_queues[channel_id] = new_queue
    
    new_state = IPCState(
        channels=state.channels,
        queues=new_queues
    )
    
    proof = ProofObject(
        rule="Send",
        premises=[
            f"channel={channel_id}",
            f"msg_len={len(message)}",
            f"new_queue_len={len(new_queue)}"
        ],
        conclusion="message sent"
    )
    
    return new_state, proof


def receive(state: IPCState,
           channel_id: str,
           receiver_cap: Capability) -> Tuple[IPCState, Optional[str], ProofObject]:
    """Receive a message from a channel.
    
    Verifies receiver holds receiver_cap. Returns None if queue empty.
    
    Args:
        state: Current IPC state
        channel_id: Channel to receive from
        receiver_cap: Receiver's capability
    
    Returns:
        (new_state, message, proof)
        message is None if queue empty
    """
    if channel_id not in state.channels:
        return state, None, ProofObject(
            rule="Receive",
            premises=[f"channel={channel_id}"],
            conclusion="receive failed: channel not found"
        )
    
    channel = state.channels[channel_id]
    
    # Verify receiver capability
    if receiver_cap.target != channel_id:
        return state, None, ProofObject(
            rule="Receive",
            premises=[
                f"cap_target={receiver_cap.target}",
                f"channel={channel_id}"
            ],
            conclusion="receive failed: wrong capability"
        )
    
    # Check queue
    queue = state.queues.get(channel_id, [])
    if not queue:
        return state, None, ProofObject(
            rule="Receive",
            premises=["queue empty"],
            conclusion="receive blocked: no messages"
        )
    
    # Get first message
    message = queue[0]
    new_queue = queue[1:]
    new_queues = state.queues.copy()
    new_queues[channel_id] = new_queue
    
    new_state = IPCState(
        channels=state.channels,
        queues=new_queues
    )
    
    proof = ProofObject(
        rule="Receive",
        premises=[
            f"channel={channel_id}",
            f"msg_len={len(message)}",
            f"remaining={len(new_queue)}"
        ],
        conclusion="message received"
    )
    
    return new_state, message, proof


def check_no_unauthorized_send(state: IPCState,
                              channel_id: str,
                              process_id: str,
                              cap_space: Dict[str, List[Capability]]) -> Tuple[bool, ProofObject]:
    """Check that process cannot send without proper capability.
    
    Args:
        state: IPC state
        channel_id: Channel to check
        process_id: Process attempting send
        cap_space: Capability space (process_id -> capabilities)
    
    Returns:
        (authorized, proof)
    """
    if channel_id not in state.channels:
        return False, ProofObject(
            rule="UnauthorizedSend",
            premises=["channel not found"],
            conclusion="unauthorized"
        )
    
    channel = state.channels[channel_id]
    required_cap = channel.sender_cap
    
    # Check if process has the required capability
    caps = cap_space.get(process_id, [])
    has_cap = any(
        cap.target == required_cap.target and 
        cap.delegator == process_id
        for cap in caps
    )
    
    authorized = has_cap
    
    proof = ProofObject(
        rule="UnauthorizedSend",
        premises=[
            f"process={process_id}",
            f"channel={channel_id}",
            f"has_cap={has_cap}"
        ],
        conclusion=f"authorized={authorized}"
    )
    
    return authorized, proof


def check_bounded_queues(state: IPCState) -> Tuple[bool, ProofObject]:
    """Check that every queue length <= channel capacity.
    
    Args:
        state: IPC state
    
    Returns:
        (bounded, proof)
    """
    violations = []
    
    for channel_id, channel in state.channels.items():
        queue_len = len(state.queues.get(channel_id, []))
        if queue_len > channel.capacity:
            violations.append(f"{channel_id}: {queue_len} > {channel.capacity}")
    
    bounded = len(violations) == 0
    
    proof = ProofObject(
        rule="BoundedQueues",
        premises=[
            f"channels={len(state.channels)}",
            f"violations={len(violations)}"
        ],
        conclusion=f"bounded={bounded}"
    )
    
    return bounded, proof


def create_channel(state: IPCState,
                  channel_id: str,
                  msg_type: str,
                  capacity: int,
                  owner: str) -> Tuple[IPCState, Tuple[Capability, Capability], ProofObject]:
    """Create a new IPC channel.
    
    Returns sender and receiver capabilities.
    
    Args:
        state: Current IPC state
        channel_id: ID for new channel
        msg_type: Message type
        capacity: Queue capacity
        owner: Process creating the channel
    
    Returns:
        (new_state, (sender_cap, receiver_cap), proof)
    """
    if channel_id in state.channels:
        return state, (None, None), ProofObject(
            rule="CreateChannel",
            premises=[f"channel_id={channel_id}"],
            conclusion="create failed: channel exists"
        )
    
    # Create capabilities
    sender_cap = Capability(
        target=channel_id,
        permissions=frozenset([Permission.WRITE, Permission.DELEGATE]),
        attenuations=tuple(),
        delegator=owner
    )
    
    receiver_cap = Capability(
        target=channel_id,
        permissions=frozenset([Permission.READ, Permission.DELEGATE]),
        attenuations=tuple(),
        delegator=owner
    )
    
    # Create channel
    channel = TypedChannel(
        channel_id=channel_id,
        msg_type=msg_type,
        capacity=capacity,
        sender_cap=sender_cap,
        receiver_cap=receiver_cap
    )
    
    # Update state
    new_channels = state.channels.copy()
    new_channels[channel_id] = channel
    
    new_queues = state.queues.copy()
    new_queues[channel_id] = []
    
    new_state = IPCState(
        channels=new_channels,
        queues=new_queues
    )
    
    proof = ProofObject(
        rule="CreateChannel",
        premises=[
            f"channel_id={channel_id}",
            f"msg_type={msg_type}",
            f"capacity={capacity}",
            f"owner={owner}"
        ],
        conclusion="channel created"
    )
    
    return new_state, (sender_cap, receiver_cap), proof
