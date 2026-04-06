"""D_TREATIES: Treaty Obligations

Layer 0 (Supranational) domain implementing treaty registry,
supremacy clause resolution, and withdrawal procedures.

Biblical: 2 Kings 23:3 — King Josiah made a covenant "to keep his
commandments... with all his heart and all his soul." Treaties bind
the nation.
"""

from src.domains.d_treaties.implementation import (
    TreatyRegistry,
    TreatyStatus,
    RatificationRecord,
    check_treaty_supremacy,
)

__all__ = [
    "TreatyRegistry",
    "TreatyStatus",
    "RatificationRecord",
    "check_treaty_supremacy",
]
