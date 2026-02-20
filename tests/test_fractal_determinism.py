#!/usr/bin/env python3
"""
Fractal Determinism Tests — tests/test_fractal_determinism.py

Same determinism pattern verified at every scale:
  - Bit level:        individual bit operations via oe_ifm.mathematical_core
  - Byte level:       struct.pack/unpack round-trips
  - Integer level:    int64 arithmetic vectors (emulated vs. native)
  - Hash level:       sha256 over fixed payloads
  - Merkle level:     binary Merkle tree over generated weights
  - UVM level:        Universal Virtual Machine state hash across two runs
  - Chain level:      Attestation chain hash for a deterministic event log

"Fractal" means: the same invariant (determinism) holds at every level of
abstraction, from a single bit flip to a full model attestation chain.

Author: Orthogonal Engineering
PR: #28
Version: 1.0.0
"""

import hashlib
import struct
import sys
from pathlib import Path

# Ensure oe_ifm is importable when running from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

from oe_ifm.mathematical_core import (
    int64,
    uint64,
    peano_add,
    bitwise_and_emulated,
    bitwise_xor_emulated,
    bitwise_or_emulated,
    logical_shift_left,
    logical_shift_right,
)
from oe_ifm.universal_virtual_machine import UVM
from oe_ifm.blockchain_attestation import AttestationChain, create_attestation_block

# Re-use the weight/Merkle helpers from the existing determinism test
from tests.test_cross_platform_determinism import (
    generate_weights,
    compute_merkle_root,
    CANONICAL_MERKLE_ROOT_SEED,
)


# ---------------------------------------------------------------------------
# Level 1 — Bit-level determinism
# ---------------------------------------------------------------------------

def test_bit_level_and():
    """Emulated AND matches native Python & for all 64 bit positions."""
    for bit_position in range(64):
        mask = 1 << bit_position
        emulated = bitwise_and_emulated(mask, mask)
        native = mask & mask
        assert emulated == native, (
            f"bitwise_and_emulated mismatch at bit {bit_position}: "
            f"emulated={emulated} native={native}"
        )


def test_bit_level_xor():
    """Emulated XOR matches native Python ^ for all 64 bit positions."""
    for bit_position in range(64):
        mask = 1 << bit_position
        # XOR with itself = 0
        emulated = bitwise_xor_emulated(mask, mask)
        assert emulated == 0, (
            f"bitwise_xor_emulated(mask, mask) != 0 at bit {bit_position}: {emulated}"
        )
        # XOR with 0 = identity
        emulated_id = bitwise_xor_emulated(mask, 0)
        assert emulated_id == mask, (
            f"bitwise_xor_emulated(mask, 0) != mask at bit {bit_position}"
        )


def test_bit_level_shifts():
    """Logical shifts produce correct values for all shift amounts 0..63."""
    for shift in range(64):
        val = 0xDEADBEEF_CAFEBABE & 0xFFFFFFFFFFFFFFFF
        shl = logical_shift_left(val, shift)
        expected_shl = (val << shift) & 0xFFFFFFFFFFFFFFFF
        assert shl == expected_shl, (
            f"logical_shift_left mismatch at shift={shift}: {shl} != {expected_shl}"
        )


def test_bit_level_int64_boundary():
    """_int64 correctly wraps at 2^63 and 2^63-1 boundaries."""
    assert int64(2**63 - 1) == 2**63 - 1     # max positive
    assert int64(2**63) == -(2**63)           # wraps to min negative
    assert int64(2**64 - 1) == -1            # all-ones = -1
    assert int64(0) == 0


# ---------------------------------------------------------------------------
# Level 2 — Byte-level determinism
# ---------------------------------------------------------------------------

def test_byte_level_struct_pack():
    """struct.pack('B', v) == bytes([v]) for all 256 byte values."""
    for byte_val in range(256):
        packed = struct.pack("B", byte_val)
        assert packed == bytes([byte_val]), (
            f"struct.pack('B', {byte_val}) = {packed!r}, expected {bytes([byte_val])!r}"
        )


def test_byte_level_struct_int64():
    """struct.pack/unpack round-trips for signed int64 boundary values."""
    boundary_values = [0, 1, -1, 2**63 - 1, -(2**63), 0x0102030405060708]
    for v in boundary_values:
        packed = struct.pack("<q", v)
        unpacked = struct.unpack("<q", packed)[0]
        assert unpacked == v, (
            f"struct int64 round-trip failed for {v}: got {unpacked}"
        )


# ---------------------------------------------------------------------------
# Level 3 — Integer-level determinism (emulated vs. reference)
# ---------------------------------------------------------------------------

def test_integer_level_peano_add():
    """peano_add(a, b) == a + b for a range of values."""
    pairs = [(0, 0), (1, 0), (0, 1), (100, 200), (2**32, 2**32), (0xDEAD, 0xBEEF)]
    for a, b in pairs:
        expected = a + b
        got = peano_add(a, b)
        assert got == expected, (
            f"peano_add({a}, {b}) = {got}, expected {expected}"
        )


def test_integer_level_emulated_vs_native_int64():
    """Emulated int64() matches Python's native signed overflow semantics."""
    values = [0, 1, -1, 2**63 - 1, 2**63, 2**64 - 1, 2**64, -(2**63)]
    for v in values:
        emulated = int64(v)
        # Reference: same mask+sign-extension logic independently verified
        ref = v & 0xFFFFFFFFFFFFFFFF
        if ref >= 0x8000000000000000:
            ref -= 0x10000000000000000
        assert emulated == ref, (
            f"int64({v}) = {emulated}, expected {ref}"
        )


# ---------------------------------------------------------------------------
# Level 4 — Hash-level determinism
# ---------------------------------------------------------------------------

def test_hash_level_sha256_fixed_inputs():
    """sha256 of fixed byte strings returns known hex digests."""
    cases = [
        (b"", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
        (b"\x00", "6e340b9cffb37a989ca544e6bb780a2c78901d3fb33738768511a30617afa01d"),
        (b"OE_PR26_DETERMINISM_SEED_V1",
         "96cc20a24313ba22105ed5c06b40eba8d61bb50f89afa5689d7fa9e86e1a8112"),
    ]
    for data, expected in cases:
        got = hashlib.sha256(data).hexdigest()
        assert got == expected, (
            f"sha256({data!r}) = {got}, expected {expected}"
        )


def test_hash_level_two_runs_identical():
    """Running sha256 twice on the same input yields the same digest."""
    data = CANONICAL_MERKLE_ROOT_SEED
    assert hashlib.sha256(data).hexdigest() == hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Level 5 — Merkle-level determinism
# ---------------------------------------------------------------------------

def test_merkle_level_weight_generation():
    """generate_weights produces identical lists across two calls."""
    w1 = generate_weights(CANONICAL_MERKLE_ROOT_SEED)
    w2 = generate_weights(CANONICAL_MERKLE_ROOT_SEED)
    assert w1 == w2, "generate_weights is not deterministic"


def test_merkle_level_root_stable():
    """Merkle root is identical across two independent computations."""
    root1 = compute_merkle_root(generate_weights(CANONICAL_MERKLE_ROOT_SEED))
    root2 = compute_merkle_root(generate_weights(CANONICAL_MERKLE_ROOT_SEED))
    assert root1 == root2, (
        f"Merkle root unstable: {root1} != {root2}"
    )


def test_merkle_level_sensitivity():
    """Changing any weight changes the Merkle root (soundness)."""
    weights = generate_weights(CANONICAL_MERKLE_ROOT_SEED)
    root_original = compute_merkle_root(weights)

    # Flip the first weight
    mutated = list(weights)
    mutated[0] ^= 1
    root_mutated = compute_merkle_root(mutated)

    assert root_original != root_mutated, (
        "Merkle root did not change after weight mutation (soundness failure)"
    )


# ---------------------------------------------------------------------------
# Level 6 — UVM-level determinism
# ---------------------------------------------------------------------------

_UVM_PROGRAM = [
    ("SET", "R0", 42),
    ("SET", "R1", 58),
    ("ADD", "R2", "R0", "R1"),    # R2 = 100
    ("SET", "R3", 7),
    ("MUL", "R4", "R2", "R3"),    # R4 = 700
    ("STORE", "R4", 1000),
    ("LOAD", "R5", 1000),          # R5 = 700
    ("XOR", "R6", "R2", "R5"),    # R6 = 100 XOR 700
    ("HALT",),
]


def test_uvm_level_deterministic_state_hash():
    """Running the same UVM program twice yields identical state hashes."""
    uvm1 = UVM()
    uvm1.run(_UVM_PROGRAM)
    hash1 = uvm1.state_hash()

    uvm2 = UVM()
    uvm2.run(_UVM_PROGRAM)
    hash2 = uvm2.state_hash()

    assert hash1 == hash2, (
        f"UVM state hash non-deterministic:\n  run1={hash1}\n  run2={hash2}"
    )


def test_uvm_level_emulated_add_correctness():
    """UVM ADD instruction produces correct results for known inputs."""
    uvm = UVM()
    uvm.run([
        ("SET", "R0", 1000),
        ("SET", "R1", -1),
        ("ADD", "R2", "R0", "R1"),   # 999
        ("SET", "R3", -(2**63)),
        ("SET", "R4", -1),
        ("ADD", "R5", "R3", "R4"),   # wraps to 2^63 - 1
        ("HALT",),
    ])
    assert uvm.get_register("R2") == 999
    assert uvm.get_register("R5") == 2**63 - 1


def test_uvm_level_emulated_mul_correctness():
    """UVM MUL instruction produces correct results for known inputs."""
    uvm = UVM()
    uvm.run([
        ("SET", "R0", 7),
        ("SET", "R1", 8),
        ("MUL", "R2", "R0", "R1"),   # 56
        ("SET", "R3", -3),
        ("SET", "R4", 4),
        ("MUL", "R5", "R3", "R4"),   # -12
        ("HALT",),
    ])
    assert uvm.get_register("R2") == 56
    assert uvm.get_register("R5") == -12


# ---------------------------------------------------------------------------
# Level 7 — Chain-level determinism (blockchain attestation)
# ---------------------------------------------------------------------------

def test_chain_level_deterministic_chain_hash():
    """Building the same attestation chain twice yields identical tip hashes."""

    def build_chain():
        chain = AttestationChain()
        chain.append(b"ubuntu-py311-merkle-root", timestamp=1000, label="ubuntu-py311")
        chain.append(b"macos-py311-merkle-root", timestamp=1001, label="macos-py311")
        chain.append(b"windows-py311-merkle-root", timestamp=1002, label="windows-py311")
        return chain

    chain_a = build_chain()
    chain_b = build_chain()

    assert chain_a.chain_hash() == chain_b.chain_hash(), (
        f"Attestation chain hash non-deterministic:\n"
        f"  chain_a={chain_a.chain_hash()}\n  chain_b={chain_b.chain_hash()}"
    )


def test_chain_level_integrity_verification():
    """AttestationChain.verify() returns True for a valid chain."""
    chain = AttestationChain()
    chain.append(b"block-0-data", timestamp=0, label="genesis")
    chain.append(b"block-1-data", timestamp=1, label="second")
    assert chain.verify(), "Valid chain failed integrity check"


def test_chain_level_tamper_detection():
    """Modifying a block makes AttestationChain.verify() return False."""
    chain = AttestationChain()
    chain.append(b"original-data", timestamp=0, label="genesis")
    chain.append(b"more-data", timestamp=1, label="second")

    # Tamper with block 0's data_hash
    chain.blocks[0].data_hash = "deadbeef" * 8  # wrong hash

    assert not chain.verify(), "Tampered chain passed integrity check"


def test_chain_level_single_block_helper():
    """create_attestation_block() helper produces consistent results."""
    block_a = create_attestation_block(
        previous_hash="0" * 64,
        data=b"test-payload",
        timestamp=42,
        sequence=0,
        label="test",
    )
    block_b = create_attestation_block(
        previous_hash="0" * 64,
        data=b"test-payload",
        timestamp=42,
        sequence=0,
        label="test",
    )
    assert block_a["hash"] == block_b["hash"], (
        "create_attestation_block is not deterministic"
    )


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

ALL_TESTS = [
    # Bit level
    test_bit_level_and,
    test_bit_level_xor,
    test_bit_level_shifts,
    test_bit_level_int64_boundary,
    # Byte level
    test_byte_level_struct_pack,
    test_byte_level_struct_int64,
    # Integer level
    test_integer_level_peano_add,
    test_integer_level_emulated_vs_native_int64,
    # Hash level
    test_hash_level_sha256_fixed_inputs,
    test_hash_level_two_runs_identical,
    # Merkle level
    test_merkle_level_weight_generation,
    test_merkle_level_root_stable,
    test_merkle_level_sensitivity,
    # UVM level
    test_uvm_level_deterministic_state_hash,
    test_uvm_level_emulated_add_correctness,
    test_uvm_level_emulated_mul_correctness,
    # Chain level
    test_chain_level_deterministic_chain_hash,
    test_chain_level_integrity_verification,
    test_chain_level_tamper_detection,
    test_chain_level_single_block_helper,
]


def main() -> int:
    print("=" * 72)
    print("PR #28 FRACTAL DETERMINISM TESTS")
    print(f"OS:     {sys.platform}")
    print(f"Python: {sys.version}")
    print("=" * 72)

    failures = []
    for fn in ALL_TESTS:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
        except Exception as exc:
            print(f"  FAIL  {fn.__name__}: {exc}")
            failures.append(fn.__name__)

    print("=" * 72)
    if failures:
        print(f"RESULT: {len(failures)} test(s) FAILED")
        for name in failures:
            print(f"  - {name}")
        return 1

    print(f"RESULT: ALL {len(ALL_TESTS)} FRACTAL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
