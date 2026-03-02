"""
Falsification test: Software continues correctly after single-bit memory flip.
Bit flip detected and corrected by redundancy.

# @falsification_id: F-SPACE-002
"""
import pytest

def hamming_encode(nibble: int) -> int:
    """Encode 4-bit value with 3 parity bits (Hamming(7,4))."""
    d = [(nibble >> i) & 1 for i in range(4)]
    p = [d[0]^d[1]^d[3], d[0]^d[2]^d[3], d[1]^d[2]^d[3]]
    bits = [p[0], p[1], d[0], p[2], d[1], d[2], d[3]]
    return sum(b << i for i, b in enumerate(bits))

def hamming_correct(code: int) -> int:
    bits = [(code >> i) & 1 for i in range(7)]
    syndrome = (bits[0]^bits[2]^bits[4]^bits[6]) | ((bits[1]^bits[2]^bits[5]^bits[6])<<1) | ((bits[3]^bits[4]^bits[5]^bits[6])<<2)
    if syndrome:
        bits[syndrome-1] ^= 1
    return (bits[2]) | (bits[4]<<1) | (bits[5]<<2) | (bits[6]<<3)

def test_single_bit_flip_corrected():
    for nibble in range(16):
        code = hamming_encode(nibble)
        for bit_pos in range(7):
            flipped = code ^ (1 << bit_pos)
            corrected = hamming_correct(flipped)
            assert corrected == nibble, f"Failed to correct flip at bit {bit_pos} for nibble {nibble}"
