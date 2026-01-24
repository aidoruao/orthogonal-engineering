"""
Orthogonal Engineering Toolkit (OE Toolkit)

A comprehensive toolkit for implementing and enforcing
Orthogonal Engineering methodology with glass-box transparency.
"""

__version__ = "1.0.0"
__author__ = "Orthogonal Engineering AI"
__license__ = "MIT"

from .boundary_enforcer import BoundaryViolation, glass_box_boundary
from .cli import main
from .evidence_store import EvidenceStore

__all__ = ["main", "EvidenceStore", "glass_box_boundary", "BoundaryViolation"]
