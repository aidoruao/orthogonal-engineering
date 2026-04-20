"""Integer-only Fraction rendering helpers.

The repo-wide rule is "no ``float``" — including in f-string rendering. These
helpers format a :class:`fractions.Fraction` as a fixed-point decimal,
percentage, or signed number without ever constructing a ``float``. They use
only integer arithmetic (``divmod``, ``numerator``, ``denominator``).
"""

from __future__ import annotations

from fractions import Fraction
from typing import Union


_Numberish = Union[Fraction, int]


def _coerce(value: _Numberish) -> Fraction:
    """Return ``value`` as a ``Fraction``; reject non-rational inputs.

    Falsifies if: a non-``Fraction``, non-``int`` input is accepted without
    raising ``TypeError``.
    falsifies_if: a non-rational input silently passes through coercion.
    """
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return Fraction(value)
    raise TypeError(
        f"fraction_display helpers require Fraction or int; got {type(value).__name__}"
    )


def format_decimal(value: _Numberish, places: int = 6) -> str:
    """Render ``value`` as a fixed-point decimal with ``places`` digits.

    Truncates (toward zero) rather than rounding, so the result is a
    deterministic integer-truncated rendering. Uses only integer math.

    Falsifies if: the returned string does not equal the truncated
    fixed-point representation of ``value`` for ``places >= 0``, or a
    negative ``places`` fails to raise ``ValueError``.
    falsifies_if: the string rendering disagrees with the integer-truncated
    fixed-point decimal of ``value``, or negative ``places`` does not raise.
    """
    if places < 0:
        raise ValueError("places must be non-negative")
    frac = _coerce(value)
    sign = "-" if frac < 0 else ""
    abs_frac = -frac if frac < 0 else frac
    scaled = abs_frac * (10 ** places)
    integer_scaled = scaled.numerator // scaled.denominator
    if places == 0:
        return f"{sign}{integer_scaled}"
    whole, frac_part = divmod(integer_scaled, 10 ** places)
    return f"{sign}{whole}." + str(frac_part).rjust(places, "0")


def format_percent(value: _Numberish, places: int = 2) -> str:
    """Render ``value`` as a percentage string (``x%``) with ``places`` digits.

    Falsifies if: the returned string does not equal ``format_decimal(value
    * 100, places) + "%"`` for any Fraction input.
    falsifies_if: the percentage rendering disagrees with
    ``format_decimal(value * 100, places) + "%"``.
    """
    frac = _coerce(value) * 100
    return format_decimal(frac, places) + "%"
