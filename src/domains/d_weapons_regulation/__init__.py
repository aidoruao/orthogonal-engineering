"""D_WEAPONS_REGULATION domain — Weapons Regulation."""

from .implementation import FirearmTransaction
from .invariants import (
    check_background_check_required,
    check_nfa_compliance,
    check_straw_purchase,
    run_all_invariants,
)

__all__ = [
    "FirearmTransaction",
    "check_background_check_required",
    "check_nfa_compliance",
    "check_straw_purchase",
    "run_all_invariants",
]
