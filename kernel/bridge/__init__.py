"""Kingdom OS Bridge Layer — Capability-gated mediation to external systems.

Each bridge defines:
1. A capability type (what permission is needed)
2. Invariants (what the external system must satisfy)
3. A mediation interface (how the kernel forwards requests)
4. A witness log (ProofObject for every operation)

The kernel never implements the external system.
The kernel only mediates access and verifies invariants.
"""

from kernel.bridge.gpu import GpuBridgeState, GpuCap, CommandBuffer, gpu_submit, check_vram_bounded
from kernel.bridge.net import NetworkBridgeState, NetworkCap, Packet, net_send, check_bandwidth_bounded
from kernel.bridge.storage import StorageBridgeState, StorageCap, Blob, storage_write, storage_read, check_integrity
from kernel.bridge.linux_compat import LinuxCompatState, LinuxCompatCap, translate_syscall
from kernel.bridge.process import ProcessBridgeState, ProcessCap, spawn_external

__all__ = [
    # GPU bridge
    "GpuBridgeState",
    "GpuCap",
    "CommandBuffer",
    "gpu_submit",
    "check_vram_bounded",
    # Network bridge
    "NetworkBridgeState",
    "NetworkCap",
    "Packet",
    "net_send",
    "check_bandwidth_bounded",
    # Storage bridge
    "StorageBridgeState",
    "StorageCap",
    "Blob",
    "storage_write",
    "storage_read",
    "check_integrity",
    # Linux compat bridge
    "LinuxCompatState",
    "LinuxCompatCap",
    "translate_syscall",
    # Process bridge
    "ProcessBridgeState",
    "ProcessCap",
    "spawn_external",
]
