#!/usr/bin/env python3
"""
scoring/peano.py — Peano representation and unambiguous constructors.

Peano naturals: 0 = Z, succ(n) = S(n)
"""
from __future__ import annotations
from typing import Any, Dict, Union


class Peano:
    """Peano natural number."""
    __slots__ = ("_n",)

    def __init__(self, n: int) -> None:
        if not isinstance(n, int) or n < 0:
            raise ValueError(f"Peano requires non-negative integer, got {n!r}")
        self._n = n

    @classmethod
    def from_int(cls, n: int) -> "Peano":
        """Construct Peano from non-negative integer."""
        return cls(n)

    @classmethod
    def from_peano(cls, peano_str: str) -> "Peano":
        """Construct Peano from string representation like 'S(S(S(Z)))'.

        Z = 0, S(x) = succ(x).
        """
        return cls(_parse_peano_str(peano_str))

    def to_int(self) -> int:
        """Convert to Python int."""
        return self._n

    def to_str(self) -> str:
        """Convert to string Peano representation."""
        return _int_to_peano_str(self._n)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Peano):
            return self._n == other._n
        return NotImplemented

    def __repr__(self) -> str:
        return f"Peano({self._n})"

    def succ(self) -> "Peano":
        """Return successor."""
        return Peano(self._n + 1)

    def pred(self) -> "Peano":
        """Return predecessor. Raises ValueError at zero."""
        if self._n == 0:
            raise ValueError("No predecessor of zero")
        return Peano(self._n - 1)


def _int_to_peano_str(n: int) -> str:
    """Convert int to Peano string."""
    result = "Z"
    for _ in range(n):
        result = f"S({result})"
    return result


def _parse_peano_str(s: str) -> int:
    """Parse Peano string to int."""
    s = s.strip()
    count = 0
    while s.startswith("S(") and s.endswith(")"):
        s = s[2:-1].strip()
        count += 1
    if s != "Z":
        raise ValueError(f"Invalid Peano string: {s!r}")
    return count


def conversion_proof(n: int) -> Dict[str, Any]:
    """Generate a proof that int n equals its Peano representation."""
    p = Peano.from_int(n)
    peano_str = p.to_str()
    reparsed = _parse_peano_str(peano_str)
    return {
        "input_int": n,
        "peano_str": peano_str,
        "roundtrip_int": reparsed,
        "proof_valid": reparsed == n,
    }
