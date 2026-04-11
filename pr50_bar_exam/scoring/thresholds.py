#!/usr/bin/env python3
"""
scoring/thresholds.py — Score thresholds for pass/fail decisions.
"""
from __future__ import annotations

from fractions import Fraction


PASS_THRESHOLD = Fraction(7, 10)  # 70% overall weighted score required
CATEGORY_MINIMUMS: dict = {
    "boundary": Fraction(6, 10),
    "threat": Fraction(6, 10),
    "grace": Fraction(1, 2),
}


def is_pass(overall_score: Fraction, category_scores: dict) -> bool:
    """Return True if candidate passes all thresholds."""
    if overall_score < PASS_THRESHOLD:
        return False
    for cat, minimum in CATEGORY_MINIMUMS.items():
        if category_scores.get(cat, Fraction(0)) < minimum:
            return False
    return True
