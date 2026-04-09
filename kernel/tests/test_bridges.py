"""Tests for Kingdom OS bridge layer."""

import sys
sys.path.insert(0, '/home/idor/orthogonal-engineering')

from fractions import Fraction

from kernel.hal import HalState, HalCap, HalCapType, hal_read, hal_write, check_no_unmapped_access
from kernel.bridge.gpu import GpuBridgeState, GpuCap, GpuCapType, CommandBuffer, gpu_submit, check_vram_bounded
from kernel.bridge.net import NetworkBridgeState, NetworkCap, NetworkCapType, Packet, net_send, check_bandwidth_bounded
from kernel.bridge.storage import StorageBridgeState, StorageCap, storage_write, storage_read, check_integrity
from kernel.bridge.linux_compat import LinuxCompatState, LinuxCompatCap, LinuxSyscall, translate_syscall
from kernel.bridge.process import ProcessBridgeState, ProcessCap, spawn_external
from kernel.boot import boot, verify_boot_integrity


def test_hal_read_requires_cap():
    """HAL read requires valid capability."""
    state = HalState()
    cap = HalCap("cap1", "p1", HalCapType.MMIO, Fraction(0x1000), Fraction(0x100))
    state.caps["p1"] = [cap]
    
    value, _, proof = hal_read(state, "p1", Fraction(0x1000), cap)
    assert value is not None
    assert "successful" in proof.conclusion


def test_hal_unmapped_access_rejected():
    """Access without capability is rejected."""
    state = HalState()
    cap = HalCap("cap1", "p1", HalCapType.MMIO, Fraction(0x1000), Fraction(0x100))
    state.caps["p1"] = [cap]
    
    # Try to read outside cap range
    value, _, proof = hal_read(state, "p1", Fraction(0x2000), cap)
    assert value is None
    assert "denied" in proof.conclusion


def test_gpu_submit_requires_cap():
    """GPU submit requires valid capability."""
    state = GpuBridgeState(total_vram=Fraction(1024*1024*1024))
    cap = GpuCap("p1", GpuCapType.SUBMIT_COMMANDS, Fraction(256*1024*1024), 1000)
    state.caps["p1"] = [cap]
    
    buffer = CommandBuffer("buf1", 100, Fraction(128*1024*1024), "hash123", Fraction(0))
    new_state, proof = gpu_submit(state, "p1", buffer, cap)
    
    assert len(new_state.submitted_buffers) == 1
    assert "submitted" in proof.conclusion


def test_gpu_vram_bounded():
    """GPU VRAM allocation is bounded."""
    state = GpuBridgeState(total_vram=Fraction(1024))
    state.allocated_vram = Fraction(512)
    
    bounded, _ = check_vram_bounded(state)
    assert bounded


def test_net_send_requires_cap():
    """Network send requires valid capability."""
    state = NetworkBridgeState()
    cap = NetworkCap("p1", NetworkCapType.SEND, frozenset([80, 443]), Fraction(1024*1024))
    state.caps["p1"] = [cap]
    
    packet = Packet("pkt1", 12345, 80, "hash", Fraction(100), Fraction(0))
    new_state, proof = net_send(state, "p1", packet, cap)
    
    assert len(new_state.packet_log) == 1
    assert "sent" in proof.conclusion


def test_net_bandwidth_bounded():
    """Network bandwidth is bounded."""
    state = NetworkBridgeState()
    state.bandwidth_used["p1"] = Fraction(900)
    cap = NetworkCap("p1", NetworkCapType.SEND, frozenset([80]), Fraction(1024))
    state.caps["p1"] = [cap]
    
    bounded, _ = check_bandwidth_bounded(state)
    assert bounded  # 900 < 1024


def test_storage_write_integrity():
    """Storage write maintains integrity."""
    state = StorageBridgeState()
    cap = StorageCap("p1", True, True, Fraction(1024))
    state.caps["p1"] = [cap]
    
    content = b"Hello, Kingdom OS!"
    hash_val, new_state, proof = storage_write(state, "p1", content, cap)
    
    assert hash_val != ""
    assert hash_val in new_state.blobs
    assert "written" in proof.conclusion


def test_storage_read_integrity():
    """Storage read verifies integrity."""
    state = StorageBridgeState()
    cap = StorageCap("p1", True, True, Fraction(1024))
    state.caps["p1"] = [cap]
    
    content = b"Test content"
    hash_val, state, _ = storage_write(state, "p1", content, cap)
    
    read_content, _, proof = storage_read(state, "p1", hash_val, cap)
    
    assert read_content == content
    assert "read" in proof.conclusion


def test_linux_syscall_translation():
    """Linux syscalls are translated to capabilities."""
    state = LinuxCompatState()
    cap = LinuxCompatCap("p1", frozenset([LinuxSyscall.WRITE]), "binary_hash", Fraction(1024), frozenset())
    state.caps["p1"] = [cap]
    state.active_compartments["p1"] = "binary_hash"
    
    new_state, result, proof = translate_syscall(state, "p1", LinuxSyscall.WRITE, {}, cap)
    
    assert result == "success"
    assert len(new_state.translations) == 1


def test_process_spawn_requires_cap():
    """Process spawn requires valid capability."""
    state = ProcessBridgeState()
    cap = ProcessCap("p1", 5, frozenset(["binary_hash"]), Fraction(1024))
    state.caps["p1"] = [cap]
    
    new_state, pid, proof = spawn_external(state, "p1", "binary_hash", Fraction(512), cap)
    
    assert pid is not None
    assert "spawned" in proof.conclusion


def test_boot_sequence_complete():
    """Boot sequence completes all phases."""
    final_state, proof = boot(Fraction(1024*1024*1024))
    
    assert final_state.hal_initialized
    assert final_state.memory_initialized
    assert final_state.scheduler_initialized
    assert final_state.ipc_initialized
    assert final_state.bridges_initialized
    assert final_state.userland_reached
    assert "complete" in proof.conclusion


def test_boot_integrity_verified():
    """Boot integrity can be verified."""
    final_state, _ = boot(Fraction(1024*1024*1024))
    valid, proof = verify_boot_integrity(final_state)
    
    assert valid
    assert "valid=True" in proof.conclusion


if __name__ == "__main__":
    print("Running Kingdom OS bridge tests...\n")
    
    test_hal_read_requires_cap()
    print("✓ HAL read requires cap")
    
    test_hal_unmapped_access_rejected()
    print("✓ HAL unmapped access rejected")
    
    test_gpu_submit_requires_cap()
    print("✓ GPU submit requires cap")
    
    test_gpu_vram_bounded()
    print("✓ GPU VRAM bounded")
    
    test_net_send_requires_cap()
    print("✓ Network send requires cap")
    
    test_net_bandwidth_bounded()
    print("✓ Network bandwidth bounded")
    
    test_storage_write_integrity()
    print("✓ Storage write integrity")
    
    test_storage_read_integrity()
    print("✓ Storage read integrity")
    
    test_linux_syscall_translation()
    print("✓ Linux syscall translation")
    
    test_process_spawn_requires_cap()
    print("✓ Process spawn requires cap")
    
    test_boot_sequence_complete()
    print("✓ Boot sequence complete")
    
    test_boot_integrity_verified()
    print("✓ Boot integrity verified")
    
    print("\n✓ All 12 bridge tests passed!")
