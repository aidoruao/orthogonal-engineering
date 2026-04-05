"""D_DOLLARTREE domain package."""

from src.domains.d_dollartree.domain import (
    EVIDENCE_ANCHOR_SHA256,
    EVIDENCE_URL_SHORT,
    DOLLARTREE_SCHEMA,
    build_full_report,
    build_domain_state,
    run_adjunction_check,
    evaluate_topos_truth_gap,
    DollarTreeReport,
)

__all__ = [
    "EVIDENCE_ANCHOR_SHA256",
    "EVIDENCE_URL_SHORT",
    "DOLLARTREE_SCHEMA",
    "build_full_report",
    "build_domain_state",
    "run_adjunction_check",
    "evaluate_topos_truth_gap",
    "DollarTreeReport",
]
