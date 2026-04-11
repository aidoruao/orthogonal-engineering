#!/usr/bin/env python3
"""
Runtime — Verification layer that turns specifications into executable witnesses

The runtime extends Kingdom OS from specification to witnessed execution.
It verifies that live systems satisfy all kernel invariants.

Biblical: 1 Thessalonians 5:21 — "Test everything. Hold fast what is good."
"""

from .system_snapshot import SystemSnapshot, ProcessInfo, MemoryRegion
from .verifier import KernelVerifier, VerificationReport

__all__ = [
    "SystemSnapshot",
    "ProcessInfo", 
    "MemoryRegion",
    "KernelVerifier",
    "VerificationReport",
]
