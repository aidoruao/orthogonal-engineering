"""
Falsification test wrapper for F_LABOR_005.

Tests the invariant: Compliance extraction is detectable (compliance traits
must not correlate with unpaid labor extraction).

Falsifying observation: Statistically significant correlation found between
compliance indicators and unpaid hours.
"""
# @falsification_id: F_LABOR_005

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.labor.institution_mapper import InstitutionMapper


def test_f_labor_005():
    """
    F_LABOR_005: Compliance extraction is detectable.

    Assumption: Employee compliance traits do not correlate with unpaid labor extraction.
    This test verifies that the InstitutionMapper:
      1. Recognizes compliance_extraction as a documented multi-institution pattern.
      2. Falsifies the "isolated incident" defense for this pattern.
      3. Documents the structural isomorphism between Bay District Schools and
         AI industry RLHF systems (compliance extraction across different domains).

    Falsifying observation: compliance_extraction is only documented in one
    institution and cannot be shown to be structural.
    """
    mapper = InstitutionMapper()

    iso = mapper.get_isomorphism("compliance_extraction")
    assert iso is not None, (
        "F_LABOR_005 FAILED: compliance_extraction must be a registered pattern"
    )
    assert iso.institution_count() >= 2, (
        "F_LABOR_005 FAILED: compliance_extraction must be documented in 2+ institutions "
        "to falsify isolated incident defense"
    )
    assert iso.falsifies_isolated_incident_defense() is True, (
        "F_LABOR_005 FAILED: compliance_extraction must falsify isolated incident defense"
    )
    assert "INV-LAB-005" in iso.invariant_ref, (
        "F_LABOR_005 FAILED: Pattern must reference INV-LAB-005 (COMPLIANCE_NEUTRALITY)"
    )

    report = mapper.generate_report()
    ce_patterns = [p for p in report["patterns"] if p["pattern_id"] == "compliance_extraction"]
    assert len(ce_patterns) == 1
    assert ce_patterns[0]["falsifies_isolated_incident"] is True

    institutions_documented = {
        inst["institution"] for inst in ce_patterns[0]["instances"]
    }
    assert "Bay District Schools" in institutions_documented, (
        "F_LABOR_005 FAILED: Bay District Schools must be in the compliance extraction registry"
    )
