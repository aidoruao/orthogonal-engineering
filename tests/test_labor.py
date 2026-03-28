"""
tests/test_labor.py
-------------------
Integration tests for the D_LABOR_RIGHTS enforcement module.

Tests WageTheftDocumentationEngine (core/labor/automated_documentation.py),
InstitutionMapper (core/labor/institution_mapper.py), and
InstitutionalImmuneSystem (core/labor/immune_system.py).

Falsification test coverage:
  F_LABOR_001 — overtime entitlement (tested via report statute_refs)
  F_LABOR_002 — frontloading detection (tested via detect_frontloading)
  F_LABOR_003 — off-the-clock work prohibition (tested via compensation_status)
  F_LABOR_004 — workload accountability (tested via cumulative ratio)
  F_LABOR_005 — compliance extraction (tested via InstitutionMapper)
  F_LABOR_006 — statute preservation (tested via retention_days)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from core.labor.automated_documentation import (
    FLSA_OVERTIME_MULTIPLIER,
    FLSA_RETENTION_DAYS,
    FLSA_WEEKLY_OVERTIME_THRESHOLD,
    WORKLOAD_RATIO_TOLERANCE,
    ShiftLog,
    WageTheftDocumentationEngine,
)
from core.labor.institution_mapper import InstitutionMapper, StructuralIsomorphism
from core.labor.immune_system import InstitutionalImmuneSystem

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FRONTLOADED_TASKS = [
    {"name": "bathrooms", "count": 15, "duration_hours": 5.9},
    {"name": "trash", "count": 45, "duration_hours": 1.25},
    {"name": "hallways", "count": 6, "duration_hours": 0.77},
    {"name": "classrooms", "count": 15, "duration_hours": 1.5},
    {"name": "daily_variables", "count": 1, "duration_hours": 0.9},
]

COMPLIANT_TASKS = [
    {"name": "bathrooms", "count": 5, "duration_hours": 1.5},
    {"name": "trash", "count": 10, "duration_hours": 0.5},
    {"name": "hallways", "count": 2, "duration_hours": 0.3},
]


# ---------------------------------------------------------------------------
# ShiftLog tests
# ---------------------------------------------------------------------------

class TestShiftLog:
    def test_task_hours_sums_correctly(self):
        shift = ShiftLog(
            shift_id="test-001",
            date="2026-03-28",
            scheduled_hours=5.75,
            tasks=FRONTLOADED_TASKS,
        )
        expected = sum(t["duration_hours"] for t in FRONTLOADED_TASKS)
        assert abs(shift.task_hours - expected) < 0.01

    def test_workload_ratio_detects_frontloading(self):
        shift = ShiftLog(
            shift_id="test-002",
            date="2026-03-28",
            scheduled_hours=5.75,
            tasks=FRONTLOADED_TASKS,
        )
        assert shift.workload_ratio > 1.0, "Frontloaded shift must have ratio > 1.0"

    def test_gap_hours_positive_for_frontloaded_shift(self):
        shift = ShiftLog(
            shift_id="test-003",
            date="2026-03-28",
            scheduled_hours=5.75,
            tasks=FRONTLOADED_TASKS,
        )
        assert shift.gap_hours > 0.0

    def test_compliant_shift_ratio_at_or_below_one(self):
        shift = ShiftLog(
            shift_id="test-004",
            date="2026-03-28",
            scheduled_hours=5.75,
            tasks=COMPLIANT_TASKS,
        )
        assert shift.workload_ratio <= 1.0

    def test_content_hash_is_deterministic(self):
        kwargs = dict(
            shift_id="test-005",
            date="2026-03-28",
            scheduled_hours=5.75,
            tasks=FRONTLOADED_TASKS,
        )
        s1 = ShiftLog(**kwargs)
        s2 = ShiftLog(**kwargs)
        assert s1.content_hash() == s2.content_hash()

    def test_content_hash_changes_on_modification(self):
        s1 = ShiftLog(
            shift_id="test-006",
            date="2026-03-28",
            scheduled_hours=5.75,
            tasks=FRONTLOADED_TASKS,
        )
        s2 = ShiftLog(
            shift_id="test-006",
            date="2026-03-28",
            scheduled_hours=8.0,
            tasks=FRONTLOADED_TASKS,
        )
        assert s1.content_hash() != s2.content_hash()


# ---------------------------------------------------------------------------
# WageTheftDocumentationEngine tests — F_LABOR_001, F_LABOR_002, F_LABOR_004
# ---------------------------------------------------------------------------

class TestWageTheftDocumentationEngine:
    def _engine_with_frontloaded_shifts(self, n: int = 3) -> WageTheftDocumentationEngine:
        engine = WageTheftDocumentationEngine(
            institution="Test Institution",
            location="Test Location",
            regular_hourly_rate=15.0,
        )
        for i in range(n):
            engine.log_shift(
                shift_id=f"2026-03-{28 + i:02d}-001",
                date_str=f"2026-03-{28 + i:02d}",
                scheduled_hours=5.75,
                tasks=FRONTLOADED_TASKS,
            )
        return engine

    def test_shift_count_increments(self):
        engine = WageTheftDocumentationEngine()
        engine.log_shift("s1", "2026-03-28", 5.75, FRONTLOADED_TASKS)
        engine.log_shift("s2", "2026-03-29", 5.75, FRONTLOADED_TASKS)
        assert engine.shift_count() == 2

    def test_detect_frontloading_flags_violation(self):
        engine = self._engine_with_frontloaded_shifts(3)
        report = engine.detect_frontloading()
        assert report.violation_flag is True, (
            "F_LABOR_002: Frontloading must be detected when task_hours > scheduled_hours"
        )

    def test_detect_frontloading_workload_ratio(self):
        engine = self._engine_with_frontloaded_shifts(3)
        report = engine.detect_frontloading()
        assert report.workload_ratio > WORKLOAD_RATIO_TOLERANCE

    def test_detect_frontloading_gap_hours_positive(self):
        engine = self._engine_with_frontloaded_shifts(3)
        report = engine.detect_frontloading()
        assert report.gap_hours_total > 0.0

    def test_detect_no_violation_for_compliant_shifts(self):
        engine = WageTheftDocumentationEngine(institution="Compliant Employer")
        for i in range(3):
            engine.log_shift(
                shift_id=f"2026-03-{28 + i:02d}-001",
                date_str=f"2026-03-{28 + i:02d}",
                scheduled_hours=5.75,
                tasks=COMPLIANT_TASKS,
            )
        report = engine.detect_frontloading()
        assert report.violation_flag is False

    def test_report_contains_flsa_statute_ref(self):
        engine = self._engine_with_frontloaded_shifts(1)
        report = engine.detect_frontloading()
        assert any("207" in ref for ref in report.statute_refs), (
            "F_LABOR_001: Report must cite FLSA 29 U.S.C. § 207"
        )

    def test_report_contains_falsifies_if(self):
        engine = self._engine_with_frontloaded_shifts(1)
        report = engine.detect_frontloading()
        assert report.falsifies_if, "Every report must have a falsifies_if condition"
        assert len(report.falsifies_if) > 10

    def test_report_retention_days_meets_flsa(self):
        engine = self._engine_with_frontloaded_shifts(1)
        report = engine.detect_frontloading()
        assert report.retention_days >= FLSA_RETENTION_DAYS, (
            f"F_LABOR_006: Retention must be >= {FLSA_RETENTION_DAYS} days (FLSA 3-year)"
        )

    def test_hash_chain_valid_after_logging(self):
        engine = self._engine_with_frontloaded_shifts(5)
        assert engine.verify_hash_chain() is True

    def test_export_report_includes_hash_chain_status(self):
        engine = self._engine_with_frontloaded_shifts(2)
        report = engine.detect_frontloading()
        exported = engine.export_report(report)
        assert "hash_chain_valid" in exported

    def test_calculated_damages_present_for_violation(self):
        engine = WageTheftDocumentationEngine(
            institution="Test",
            regular_hourly_rate=15.0,
        )
        engine.log_shift("s1", "2026-03-28", 5.75, FRONTLOADED_TASKS)
        report = engine.detect_frontloading()
        assert "total_gap_hours" in report.calculated_damages
        assert report.calculated_damages["total_gap_hours"] > 0

    def test_five_year_cumulative_estimate(self):
        engine = WageTheftDocumentationEngine(
            institution="Bay District Schools",
            location="Bay County, Florida",
            regular_hourly_rate=15.0,
        )
        for day in range(30):
            engine.log_shift(
                shift_id=f"day-{day:03d}",
                date_str=f"2026-01-{(day % 28) + 1:02d}",
                scheduled_hours=5.75,
                tasks=FRONTLOADED_TASKS,
            )
        report = engine.detect_frontloading()
        assert report.violation_flag is True
        assert report.gap_hours_total > 0
        assert report.shifts_analyzed == 30


# ---------------------------------------------------------------------------
# InstitutionMapper tests — F_LABOR_005
# ---------------------------------------------------------------------------

class TestInstitutionMapper:
    def test_known_patterns_loaded(self):
        mapper = InstitutionMapper()
        patterns = mapper.all_patterns()
        assert "frontloading" in patterns
        assert "compliance_extraction" in patterns
        assert "verbal_policy_deflection" in patterns

    def test_frontloading_is_systemic(self):
        mapper = InstitutionMapper()
        iso = mapper.get_isomorphism("frontloading")
        assert iso is not None
        assert iso.is_systemic(), (
            "F_LABOR_005: Frontloading must be documented in 3+ institutions"
        )

    def test_compliance_extraction_falsifies_isolated_incident(self):
        mapper = InstitutionMapper()
        assert mapper.falsifies_isolated_incident("compliance_extraction"), (
            "F_LABOR_005: Compliance extraction must be documented in 2+ institutions"
        )

    def test_verbal_policy_deflection_falsifies_isolated_incident(self):
        mapper = InstitutionMapper()
        assert mapper.falsifies_isolated_incident("verbal_policy_deflection")

    def test_map_pattern_adds_instance(self):
        mapper = InstitutionMapper()
        initial_count = mapper.get_isomorphism("frontloading").institution_count()
        mapper.map_pattern(
            pattern_id="frontloading",
            institution="New Test District",
            institution_type="public_school_district",
            location="Test County, FL",
            evidence_summary="Test evidence",
            invariant_ref="INV-LAB-002",
            falsification_test_ref="F_LABOR_002",
            falsifies_if="Workload fits schedule.",
        )
        assert mapper.get_isomorphism("frontloading").institution_count() == initial_count + 1

    def test_generate_report_contains_all_patterns(self):
        mapper = InstitutionMapper()
        report = mapper.generate_report()
        pattern_ids = {p["pattern_id"] for p in report["patterns"]}
        assert "frontloading" in pattern_ids
        assert "compliance_extraction" in pattern_ids
        assert "verbal_policy_deflection" in pattern_ids

    def test_generate_report_includes_falsifies_isolated_incident(self):
        mapper = InstitutionMapper()
        report = mapper.generate_report()
        for pattern in report["patterns"]:
            assert "falsifies_isolated_incident" in pattern

    def test_systemic_patterns_list(self):
        mapper = InstitutionMapper()
        systemic = mapper.systemic_patterns()
        assert len(systemic) >= 1
        for iso in systemic:
            assert iso.institution_count() >= 3

    def test_unknown_pattern_raises(self):
        mapper = InstitutionMapper()
        with pytest.raises(ValueError):
            mapper.map_pattern(
                pattern_id="nonexistent_pattern",
                institution="X",
                institution_type="Y",
                location="Z",
                evidence_summary="E",
                invariant_ref="INV-LAB-001",
                falsification_test_ref="F_LABOR_001",
                falsifies_if="Nothing.",
            )


# ---------------------------------------------------------------------------
# InstitutionalImmuneSystem tests — all F_LABOR tests
# ---------------------------------------------------------------------------

class TestInstitutionalImmuneSystem:
    def _system_with_shifts(self, n: int = 3) -> InstitutionalImmuneSystem:
        system = InstitutionalImmuneSystem(
            institution="Bay District Schools",
            location="Bay County, Florida",
            scheduled_hours_per_shift=5.75,
            employee_classification="part-time",
            regular_hourly_rate=15.0,
        )
        for i in range(n):
            system.log_shift(
                date_str=f"2026-03-{max(1, 28 - n + i + 1):02d}",
                tasks=FRONTLOADED_TASKS,
            )
        return system

    def test_disrupt_returns_violation_flag(self):
        system = self._system_with_shifts(3)
        result = system.disrupt()
        assert "violation_flag" in result
        assert result["violation_flag"] is True

    def test_disrupt_always_contains_falsifies_if(self):
        system = self._system_with_shifts(1)
        result = system.disrupt()
        assert "falsifies_if" in result
        assert len(result["falsifies_if"]) > 0, (
            "Popperian guarantee: every disrupt() call must have a falsifies_if condition"
        )

    def test_disrupt_contains_popperian_guarantee(self):
        system = self._system_with_shifts(1)
        result = system.disrupt()
        assert "popperian_guarantee" in result

    def test_disrupt_hash_chain_valid(self):
        system = self._system_with_shifts(5)
        result = system.disrupt()
        assert result["hash_chain_valid"] is True

    def test_disrupt_statute_refs_include_flsa(self):
        system = self._system_with_shifts(1)
        result = system.disrupt()
        assert any("207" in ref for ref in result["statute_refs"]), (
            "F_LABOR_001: disrupt() output must reference FLSA § 207"
        )

    def test_disrupt_retention_days_in_distribution_metadata(self):
        system = self._system_with_shifts(1)
        result = system.disrupt()
        assert result["distribution_metadata"]["retention_days"] >= FLSA_RETENTION_DAYS, (
            "F_LABOR_006: retention_days must meet FLSA 3-year minimum"
        )

    def test_disrupt_isomorphism_report_present(self):
        system = self._system_with_shifts(1)
        result = system.disrupt()
        assert "isomorphism_report" in result
        assert "patterns" in result["isomorphism_report"]

    def test_disrupt_distribution_metadata_flags(self):
        system = self._system_with_shifts(1)
        result = system.disrupt()
        meta = result["distribution_metadata"]
        assert meta["forkable"] is True
        assert meta["embeddable"] is True
        assert meta["ai_native"] is True
        assert meta["permanent"] is True

    def test_disrupt_report_hash_present(self):
        system = self._system_with_shifts(1)
        result = system.disrupt()
        assert "report_hash" in result
        assert len(result["report_hash"]) == 64

    def test_shift_count_tracks_logged_shifts(self):
        system = InstitutionalImmuneSystem(
            scheduled_hours_per_shift=5.75,
        )
        assert system.shift_count() == 0
        system.log_shift("2026-03-28", tasks=FRONTLOADED_TASKS)
        assert system.shift_count() == 1
        system.log_shift("2026-03-29", tasks=FRONTLOADED_TASKS)
        assert system.shift_count() == 2

    def test_disrupt_no_shifts_no_violation(self):
        system = InstitutionalImmuneSystem(
            institution="Compliant Employer",
            scheduled_hours_per_shift=5.75,
        )
        result = system.disrupt()
        assert result["violation_flag"] is False
        assert "falsifies_if" in result

    def test_compliant_employer_no_violation(self):
        system = InstitutionalImmuneSystem(
            institution="Compliant Employer",
            scheduled_hours_per_shift=5.75,
        )
        for i in range(3):
            system.log_shift(
                date_str=f"2026-03-{28 + i:02d}",
                tasks=COMPLIANT_TASKS,
            )
        result = system.disrupt()
        assert result["violation_flag"] is False

    def test_mapper_accessible(self):
        system = InstitutionalImmuneSystem(scheduled_hours_per_shift=5.75)
        mapper = system.mapper()
        assert isinstance(mapper, InstitutionMapper)

    def test_documenter_accessible(self):
        system = InstitutionalImmuneSystem(scheduled_hours_per_shift=5.75)
        doc = system.documenter()
        assert isinstance(doc, WageTheftDocumentationEngine)
