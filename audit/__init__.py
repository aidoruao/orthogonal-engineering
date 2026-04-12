"""audit/ — Popperian integrity audit tooling for Orthogonal Engineering.

Exports:
    popperian_audit — domain-level falsifiability compliance scanner.
"""
from audit.popperian_audit import (
    AuditResult,
    DomainAuditReport,
    run_popperian_audit,
)

__all__ = [
    "AuditResult",
    "DomainAuditReport",
    "run_popperian_audit",
]
