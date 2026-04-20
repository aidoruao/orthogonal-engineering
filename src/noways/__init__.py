"""Impossibility-proof catalog module (noways)."""
from .impossibility_proofs import (
    Noway,
    by_key,
    catalog,
    check_catalog_size_at_floor,
    check_certainty_bounded,
    check_domains_covered,
    check_every_entry_has_falsifier,
    check_keys_unique,
    run_all_invariants,
)

__all__ = [
    "Noway",
    "by_key",
    "catalog",
    "check_catalog_size_at_floor",
    "check_certainty_bounded",
    "check_domains_covered",
    "check_every_entry_has_falsifier",
    "check_keys_unique",
    "run_all_invariants",
]
