"""D_ENVIRONMENTAL_LAW domain — Environmental Law."""

from .implementation import EnvironmentalPermit
from .invariants import (
    check_clean_air_act,
    check_clean_water_npdes,
    check_nepa_eis,
    check_rcra_manifest,
    run_all_invariants,
)

__all__ = [
    "EnvironmentalPermit",
    "check_clean_air_act",
    "check_clean_water_npdes",
    "check_nepa_eis",
    "check_rcra_manifest",
    "run_all_invariants",
]
