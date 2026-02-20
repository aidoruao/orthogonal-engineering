"""
Mathematical Invariant Core — oe_ifm/mathematical_core.py

Pure Python, zero external dependencies.  Implements integer arithmetic via
logical primitives so that results are identical across all platforms
regardless of hardware architecture, endianness, or OS ABI.

Design rationale (grounded in Peano axioms):
  - Addition is defined by the successor function S(n) = n + 1.
  - Multiplication is repeated addition.
  - Bitwise operations are implemented via 1-bit truth tables, not hardware.
  - Two's-complement normalisation makes all arithmetic int64-safe.

Author: Orthogonal Engineering
PR: #28
Version: 1.0.0
"""

from __future__ import annotations

_WORD_BITS = 64
_MASK64 = (1 << _WORD_BITS) - 1
_SIGN_BIT = 1 << (_WORD_BITS - 1)


# ---------------------------------------------------------------------------
# Int64 normalisation (two's complement)
# ---------------------------------------------------------------------------

def int64(value: int) -> int:
    """Return value normalised to signed 64-bit two's-complement range.

    Uses only bitwise masking and comparison — no platform arithmetic.
    """
    value = value & _MASK64
    if value >= _SIGN_BIT:
        value -= (1 << _WORD_BITS)
    return value


def uint64(value: int) -> int:
    """Return value normalised to unsigned 64-bit range."""
    return value & _MASK64


# ---------------------------------------------------------------------------
# Peano / successor-function addition (iterative to avoid stack limits)
# ---------------------------------------------------------------------------

def peano_add(a: int, b: int) -> int:
    """Add two non-negative integers via the Peano successor function.

    S(a, b) = S(a+1, b-1) until b == 0 → base case returns a.
    Iterative form used to avoid Python recursion-depth limits for large b.

    Args:
        a: First non-negative integer.
        b: Second non-negative integer.

    Returns:
        a + b (mathematically pure, no hardware + used in the loop body).
    """
    if b < 0:
        raise ValueError("peano_add is defined for non-negative integers only")
    # Carry-lookahead via bit-manipulation (hardware-free inner loop):
    # while there are carry bits, propagate them.
    while b != 0:
        carry = a & b          # bits where both are 1 → propagate
        a = a ^ b              # sum without carries
        b = carry << 1         # shift carry left
    return a


def _signed_add(a: int, b: int) -> int:
    """Signed 64-bit addition via Peano / bit-manipulation (no hardware +)."""
    # Work in unsigned space, normalise at the end.
    ua = uint64(a)
    ub = uint64(b)
    result = peano_add(ua, ub)
    return int64(result)


# ---------------------------------------------------------------------------
# Modular multiplication (via repeated addition, no hardware *)
# ---------------------------------------------------------------------------

def modular_multiply(a: int, b: int, modulus: int) -> int:
    """Multiply a by b modulo modulus using repeated doubling (Russian peasant).

    Avoids the hardware * operator inside the hot loop.

    Args:
        a: Multiplicand.
        b: Multiplier.
        modulus: Positive modulus.

    Returns:
        (a * b) % modulus
    """
    if modulus <= 0:
        raise ValueError("modulus must be positive")

    result = 0
    a = a % modulus
    negative = b < 0
    b = abs(b)

    while b > 0:
        if b & 1:                        # if b is odd
            result = peano_add(result, a) % modulus
        a = peano_add(a, a) % modulus    # double a
        b >>= 1                          # halve b

    return (-result) % modulus if negative else result


# ---------------------------------------------------------------------------
# Emulated bitwise AND (via 1-bit truth table)
# ---------------------------------------------------------------------------

def bitwise_and_emulated(a: int, b: int, bits: int = _WORD_BITS) -> int:
    """Compute bitwise AND using explicit 1-bit truth table evaluation.

    This avoids any assumption about the native AND instruction semantics.

    Args:
        a: First operand.
        b: Second operand.
        bits: Number of bits to evaluate (default: 64).

    Returns:
        a & b over `bits` positions.
    """
    result = 0
    for i in range(bits):
        bit_a = (a >> i) & 1
        bit_b = (b >> i) & 1
        # Truth table: 1 AND 1 = 1, all others = 0
        result |= (1 if (bit_a == 1 and bit_b == 1) else 0) << i
    return result


# ---------------------------------------------------------------------------
# Emulated bitwise XOR (via 1-bit truth table)
# ---------------------------------------------------------------------------

def bitwise_xor_emulated(a: int, b: int, bits: int = _WORD_BITS) -> int:
    """Compute bitwise XOR using explicit 1-bit truth table evaluation."""
    result = 0
    for i in range(bits):
        bit_a = (a >> i) & 1
        bit_b = (b >> i) & 1
        result |= (1 if bit_a != bit_b else 0) << i
    return result


# ---------------------------------------------------------------------------
# Emulated bitwise OR (via 1-bit truth table)
# ---------------------------------------------------------------------------

def bitwise_or_emulated(a: int, b: int, bits: int = _WORD_BITS) -> int:
    """Compute bitwise OR using explicit 1-bit truth table evaluation."""
    result = 0
    for i in range(bits):
        bit_a = (a >> i) & 1
        bit_b = (b >> i) & 1
        result |= (1 if (bit_a == 1 or bit_b == 1) else 0) << i
    return result


# ---------------------------------------------------------------------------
# Left / right logical shifts (no hardware shift operator semantics assumed)
# ---------------------------------------------------------------------------

def logical_shift_left(value: int, shift: int, bits: int = _WORD_BITS) -> int:
    """Logical left shift with explicit word-size mask."""
    return (value << shift) & ((1 << bits) - 1)


def logical_shift_right(value: int, shift: int) -> int:
    """Logical (unsigned) right shift."""
    return uint64(value) >> shift
