"""D_CONSUMER_PROTECTION: Consumer Protection (FTC Act, TILA, FCRA, warranties)

Layer 2 (Statutory) domain implementing consumer protection including
prohibitions on deceptive practices, disclosure requirements, and warranty law.

Biblical: Leviticus 19:35-36 — "Do not use dishonest standards when measuring
length, weight or quantity. Use honest scales and honest weights..."
"""

from src.domains.d_consumer_protection.implementation import (
    DeceptivePracticeAnalyzer,
    DisclosureRequirementsChecker,
    WarrantyAnalyzer,
    ConsumerTransaction,
    Advertisement,
    Product,
    DeceptivePracticeType,
    WarrantyType,
)
from src.domains.d_consumer_protection.invariants import (
    check_deceptive_practices_prohibited,
    check_disclosure_requirements_met,
    check_warranty_honored,
    check_unfair_practices_detected,
    check_cooling_off_period,
)

__all__ = [
    "DeceptivePracticeAnalyzer",
    "DisclosureRequirementsChecker",
    "WarrantyAnalyzer",
    "ConsumerTransaction",
    "Advertisement",
    "Product",
    "DeceptivePracticeType",
    "WarrantyType",
    "check_deceptive_practices_prohibited",
    "check_disclosure_requirements_met",
    "check_warranty_honored",
    "check_unfair_practices_detected",
    "check_cooling_off_period",
]
