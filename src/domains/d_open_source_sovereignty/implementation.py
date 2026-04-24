"""D_OPEN_SOURCE_SOVEREIGNTY implementation -- Open source sovereignty structures.

Part 5 of Forensic Offensive Campaign.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class DependencyAudit:
    """Audit result for a single dependency.

    falsifies_if: license is empty when dependency is required.
    """
    name: str
    version: str
    license: str
    proprietary: bool
    reproducible: bool


@dataclass(frozen=True)
class SovereigntyState:
    """Aggregate open-source sovereignty state.

    falsifies_if: proprietary_dependency_count > 0 or reproducible_ratio < Fraction(1, 1).
    """
    state_id: str
    dependencies: Tuple[DependencyAudit, ...]
    economic_gatekeeping_detected: bool
    public_source_available: bool


DOMAIN_METADATA = {
    "name": "d_open_source_sovereignty",
    "version": "1.0.0",
    "part": "5",
    "campaign": "CAMPAIGN-FORENSIC-OFFENSIVE-001",
}
