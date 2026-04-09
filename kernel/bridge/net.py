"""Network Bridge — Capability-gated network access.

The kernel does not implement TCP/IP. It mediates access to
a host network stack or userspace TCP (e.g., smoltcp).
A NetworkCap grants the right to send/receive bytes.
Every packet is capability-checked and logged with ProofObject.

Yeshua Inversion: Don't write a TCP stack. Mediate network access.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Optional, Dict
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject


class NetworkCapType(Enum):
    """Types of network capabilities."""
    LISTEN = auto()     # Listen on a port
    CONNECT = auto()    # Connect to remote
    SEND = auto()       # Send bytes
    RECEIVE = auto()    # Receive bytes


@dataclass(frozen=True)
class NetworkCap:
    """Capability for network access."""
    process_id: str
    net_cap_type: NetworkCapType
    allowed_ports: frozenset  # Ports this cap can access
    bandwidth_quota: Fraction  # Bytes per second


@dataclass
class Packet:
    """A network packet."""
    packet_id: str
    source_port: int
    dest_port: int
    payload_hash: str  # SHA-256 of payload
    size: Fraction
    timestamp: Fraction


@dataclass
class NetworkBridgeState:
    """State of the network bridge."""
    caps: Dict[str, List[NetworkCap]] = field(default_factory=dict)
    packet_log: List[Packet] = field(default_factory=list)
    bandwidth_used: Dict[str, Fraction] = field(default_factory=dict)  # process_id -> bytes sent this window
    window_start: Fraction = field(default_factory=lambda: Fraction(0))


def net_send(state: NetworkBridgeState,
            process_id: str,
            packet: Packet,
            cap: NetworkCap) -> Tuple[NetworkBridgeState, ProofObject]:
    """Send packet. Capability-gated. Bandwidth-limited.
    
    Args:
        state: Current network bridge state
        process_id: Process sending packet
        packet: Packet to send
        cap: Network capability
    
    Returns:
        (new_state, proof)
    """
    # Verify process holds this cap
    process_caps = state.caps.get(process_id, [])
    if cap not in process_caps:
        return state, ProofObject(
            rule="NetSend",
            premises=[f"process={process_id}", "cap not held"],
            conclusion="send denied: invalid capability"
        )
    
    # Check port authorization
    if packet.dest_port not in cap.allowed_ports:
        return state, ProofObject(
            rule="NetSend",
            premises=[
                f"dest_port={packet.dest_port}",
                f"allowed={cap.allowed_ports}"
            ],
            conclusion="send denied: port not authorized"
        )
    
    # Check bandwidth quota
    used = state.bandwidth_used.get(process_id, Fraction(0))
    if used + packet.size > cap.bandwidth_quota:
        return state, ProofObject(
            rule="NetSend",
            premises=[
                f"used={used}",
                f"size={packet.size}",
                f"quota={cap.bandwidth_quota}"
            ],
            conclusion="send denied: bandwidth quota exceeded"
        )
    
    # Log packet and update bandwidth
    new_log = state.packet_log + [packet]
    new_bandwidth = state.bandwidth_used.copy()
    new_bandwidth[process_id] = used + packet.size
    
    new_state = NetworkBridgeState(
        caps=state.caps,
        packet_log=new_log,
        bandwidth_used=new_bandwidth,
        window_start=state.window_start
    )
    
    proof = ProofObject(
        rule="NetSend",
        premises=[
            f"process={process_id}",
            f"dest_port={packet.dest_port}",
            f"size={packet.size}"
        ],
        conclusion="packet sent"
    )
    
    return new_state, proof


def check_bandwidth_bounded(state: NetworkBridgeState) -> Tuple[bool, ProofObject]:
    """Check that no process exceeds its bandwidth quota.
    
    Args:
        state: Network bridge state
    
    Returns:
        (bounded, proof)
    """
    violations = []
    
    for process_id, caps in state.caps.items():
        used = state.bandwidth_used.get(process_id, Fraction(0))
        for cap in caps:
            if used > cap.bandwidth_quota:
                violations.append(process_id)
                break
    
    bounded = len(violations) == 0
    
    proof = ProofObject(
        rule="BandwidthBounded",
        premises=[
            f"processes={len(state.caps)}",
            f"violations={len(violations)}"
        ],
        conclusion=f"bounded={bounded}"
    )
    
    return bounded, proof


def check_no_unauthorized_traffic(state: NetworkBridgeState) -> Tuple[bool, ProofObject]:
    """Every packet in log has a corresponding NetworkCap.
    
    Args:
        state: Network bridge state
    
    Returns:
        (authorized, proof)
    """
    # Verify each packet was sent by a process with appropriate cap
    violations = []
    
    for packet in state.packet_log:
        # Find which process could have sent this
        found = False
        for process_id, caps in state.caps.items():
            for cap in caps:
                if packet.dest_port in cap.allowed_ports:
                    found = True
                    break
            if found:
                break
        
        if not found:
            violations.append(packet.packet_id)
    
    authorized = len(violations) == 0
    
    proof = ProofObject(
        rule="NoUnauthorizedTraffic",
        premises=[
            f"packets={len(state.packet_log)}",
            f"violations={len(violations)}"
        ],
        conclusion=f"authorized={authorized}"
    )
    
    return authorized, proof
