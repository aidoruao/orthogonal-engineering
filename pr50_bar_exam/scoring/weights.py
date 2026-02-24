#!/usr/bin/env python3
"""
scoring/weights.py — Category weights for scoring.
"""
from __future__ import annotations
from typing import Dict


CATEGORY_WEIGHTS: Dict[str, float] = {
    "boundary": 0.40,
    "threat": 0.40,
    "grace": 0.20,
}


def validate_weights(weights: Dict[str, float]) -> bool:
    """Return True if weights sum to 1.0 (within tolerance)."""
    return abs(sum(weights.values()) - 1.0) < 1e-9
