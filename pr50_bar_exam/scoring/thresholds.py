#!/usr/bin/env python3
"""
scoring/thresholds.py — Score thresholds for pass/fail decisions.
"""
from __future__ import annotations


PASS_THRESHOLD: float = 0.70  # 70% overall weighted score required
CATEGORY_MINIMUMS: dict = {
    "boundary": 0.60,
    "threat": 0.60,
    "grace": 0.50,
}


def is_pass(overall_score: float, category_scores: dict) -> bool:
    """Return True if candidate passes all thresholds."""
    if overall_score < PASS_THRESHOLD:
        return False
    for cat, minimum in CATEGORY_MINIMUMS.items():
        if category_scores.get(cat, 0.0) < minimum:
            return False
    return True
