"""
Falsification test wrapper for F_LABOR_006.

Tests the invariant: Statute preservation holds (documentation persists for 3+ years).

Falsifying observation: Documentation expires or becomes inaccessible before
a claim can be filed (before 1095 days have elapsed).
"""
# @falsification_id: F_LABOR_006

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.labor.automated_documentation import (
    FLSA_RETENTION_DAYS,
    WageTheftDocumentationEngine,
)
from core.labor.immune_system import InstitutionalImmuneSystem


def test_f_labor_006():
    """
    F_LABOR_006: Statute preservation holds.

    Assumption: Documentation persists for the full FLSA statute of limitations
    (3 years = 1095 days for willful violations, per 29 U.S.C. § 255(b)).
    This test verifies that:
      1. FLSA_RETENTION_DAYS constant equals 1095 (3-year minimum).
      2. Generated reports carry retention_days >= 1095.
      3. The immune system disrupt() output includes retention_days in
         distribution metadata.

    Falsifying observation: Report or system output specifies retention_days < 1095,
    allowing statute of limitations to expire before a claim can be filed.
    """
    assert FLSA_RETENTION_DAYS == 1095, (
        f"F_LABOR_006 FAILED: FLSA_RETENTION_DAYS must be 1095 (3 years), got {FLSA_RETENTION_DAYS}"
    )

    engine = WageTheftDocumentationEngine(
        institution="Bay District Schools",
        location="Bay County, Florida",
        regular_hourly_rate=15.0,
    )
    engine.log_shift(
        shift_id="s1",
        date_str="2026-03-28",
        scheduled_hours=5.75,
        tasks=[
            {"name": "bathrooms", "count": 15, "duration_hours": 5.9},
            {"name": "trash", "count": 45, "duration_hours": 1.25},
        ],
    )
    report = engine.detect_frontloading()

    assert report.retention_days >= FLSA_RETENTION_DAYS, (
        f"F_LABOR_006 FAILED: report.retention_days={report.retention_days} "
        f"must be >= {FLSA_RETENTION_DAYS}"
    )
    assert any("255" in ref for ref in report.statute_refs), (
        "F_LABOR_006 FAILED: Report must cite FLSA 29 U.S.C. § 255 (statute of limitations)"
    )

    system = InstitutionalImmuneSystem(
        institution="Bay District Schools",
        scheduled_hours_per_shift=5.75,
        regular_hourly_rate=15.0,
    )
    system.log_shift("2026-03-28", tasks=[
        {"name": "bathrooms", "count": 15, "duration_hours": 5.9},
    ])
    result = system.disrupt()

    assert result["distribution_metadata"]["retention_days"] >= FLSA_RETENTION_DAYS, (
        "F_LABOR_006 FAILED: InstitutionalImmuneSystem must preserve retention_days "
        f">= {FLSA_RETENTION_DAYS} in distribution metadata"
    )
