"""D_HOUSING_LAW domain — Housing Law."""

from .implementation import RentalUnit
from .invariants import (
    check_fair_housing_compliance,
    check_habitability_standard,
    check_eviction_notice,
    run_all_invariants,
)

__all__ = [
    "RentalUnit",
    "check_fair_housing_compliance",
    "check_habitability_standard",
    "check_eviction_notice",
    "run_all_invariants",
]
