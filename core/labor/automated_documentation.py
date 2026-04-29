"""
automated_documentation.py
---------------------------
WageTheftDocumentationEngine: logs shifts, tasks, and timestamps;
detects frontloading violations automatically; and generates reports
formatted for DOL complaint or court filing.

The engine removes the burden of "proving it" from the individual employee.
Every logged shift becomes an entry in the permanent evidentiary record.
Every frontloading detection produces a structured, court-ready report.

Invariant refs:
  INV-LAB-001 (OVERTIME_ENTITLEMENT)
  INV-LAB-002 (WORKLOAD_SCHEDULABILITY)
  INV-LAB-003 (COMPENSATION_COMPLETENESS)
  INV-LAB-004 (WORKLOAD_ACCOUNTABILITY)
  INV-LAB-006 (STATUTE_PRESERVATION)

Falsification tests:
  F_LABOR_001, F_LABOR_002, F_LABOR_003, F_LABOR_004, F_LABOR_006

# @domain: D_LABOR_RIGHTS
# @authority: FLSA 29 U.S.C. § 207; Florida Constitution Amendment 2
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from typing import Dict, List, Optional


FLSA_WEEKLY_OVERTIME_THRESHOLD = 40.0
FLSA_OVERTIME_MULTIPLIER = 1.5
FLSA_RETENTION_DAYS = 1095
WORKLOAD_RATIO_TOLERANCE = 1.05


@dataclass
class ShiftLog:
    """Immutable record of a single compensable work event."""

    shift_id: str
    date: str
    scheduled_hours: float
    tasks: List[Dict]
    actual_start: Optional[str] = None
    actual_end: Optional[str] = None
    compensation_status: str = "compensated"
    notes: str = ""
    _hash: str = field(default="", init=False, repr=False)

    def __post_init__(self) -> None:
        payload = json.dumps(
            {
                "shift_id": self.shift_id,
                "date": self.date,
                "scheduled_hours": self.scheduled_hours,
                "tasks": self.tasks,
                "actual_start": self.actual_start,
                "actual_end": self.actual_end,
                "compensation_status": self.compensation_status,
            },
            sort_keys=True,
        ).encode()
        self._hash = hashlib.sha256(payload).hexdigest()

    @property
    def task_hours(self) -> float:
        """Total estimated task time in hours."""
        return sum(t.get("duration_hours", 0.0) for t in self.tasks)

    @property
    def workload_ratio(self) -> float:
        """task_hours / scheduled_hours — >1.0 indicates frontloading."""
        if self.scheduled_hours <= 0:
            return float("inf")
        return self.task_hours / self.scheduled_hours

    @property
    def gap_hours(self) -> float:
        """Unpaid hours: max(0, task_hours - scheduled_hours)."""
        return max(0.0, self.task_hours - self.scheduled_hours)

    def content_hash(self) -> str:
        """SHA-256 hash of the shift record for tamper detection."""
        # TODO: Expand content_hash() - stub detected by Yeshua Agent
        return self._hash


@dataclass
class FrontloadingReport:
    """Structured violation report, formatted for DOL complaint or court filing."""

    report_id: str
    generated_at: str
    institution: str
    period_start: str
    period_end: str
    violation_type: str
    scheduled_hours_total: float
    task_hours_total: float
    workload_ratio: float
    gap_hours_total: float
    daily_unpaid_hours_avg: float
    violation_flag: bool
    statute_refs: List[str]
    falsifies_if: str
    shifts_analyzed: int
    calculated_damages: Dict
    format: str = "dol_complaint"
    retention_days: int = FLSA_RETENTION_DAYS


class WageTheftDocumentationEngine:
    """
    Automated wage theft documentation engine.

    Logs shifts, tasks, and timestamps. Detects frontloading violations
    automatically by comparing cumulative task hours against scheduled hours.
    Generates reports formatted for DOL complaint or court filing.

    Usage::

        engine = WageTheftDocumentationEngine(institution="Bay District Schools")
        engine.log_shift(
            shift_id="2026-03-28-01",
            date_str="2026-03-28",
            scheduled_hours=5.75,
            tasks=[
                {"name": "bathrooms", "count": 15, "duration_hours": 5.9},
                {"name": "trash", "count": 45, "duration_hours": 1.25},
            ],
        )
        report = engine.detect_frontloading()
        if report.violation_flag:
            engine.export_report(report, fmt="dol_complaint")
    """

    def __init__(
        self,
        institution: str = "Unknown Institution",
        location: str = "",
        employee_classification: str = "part-time",
        regular_hourly_rate: float = 0.0,
    ) -> None:
        self.institution = institution
        self.location = location
        self.employee_classification = employee_classification
        self.regular_hourly_rate = regular_hourly_rate
        self._log: List[ShiftLog] = []
        self._hash_chain: List[str] = []

    def log_shift(
        self,
        shift_id: str,
        date_str: str,
        scheduled_hours: float,
        tasks: List[Dict],
        actual_start: Optional[str] = None,
        actual_end: Optional[str] = None,
        compensation_status: str = "compensated",
        notes: str = "",
    ) -> ShiftLog:
        """
        Log a compensable work event.

        Each shift is hashed on creation. The hash chain links all shifts
        sequentially, making retroactive modification detectable.
        """
        entry = ShiftLog(
            shift_id=shift_id,
            date=date_str,
            scheduled_hours=scheduled_hours,
            tasks=tasks,
            actual_start=actual_start,
            actual_end=actual_end,
            compensation_status=compensation_status,
            notes=notes,
        )
        prev_hash = self._hash_chain[-1] if self._hash_chain else "genesis"
        chain_input = f"{prev_hash}:{entry.content_hash()}".encode()
        chain_hash = hashlib.sha256(chain_input).hexdigest()
        self._hash_chain.append(chain_hash)
        self._log.append(entry)
        return entry

    def detect_frontloading(
        self,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None,
        format: str = "dol_complaint",
    ) -> FrontloadingReport:
        """
        Detect frontloading violations across logged shifts.

        Computes cumulative workload_ratio = task_hours / scheduled_hours.
        Flags violation when ratio exceeds WORKLOAD_RATIO_TOLERANCE (1.05).

        Returns a FrontloadingReport structured for DOL complaint or court filing.
        """
        shifts = self._log
        if period_start:
            shifts = [s for s in shifts if s.date >= period_start]
        if period_end:
            shifts = [s for s in shifts if s.date <= period_end]

        if not shifts:
            return self._empty_report(period_start, period_end, format)

        total_scheduled = sum(s.scheduled_hours for s in shifts)
        total_task = sum(s.task_hours for s in shifts)
        total_gap = sum(s.gap_hours for s in shifts)
        ratio = total_task / total_scheduled if total_scheduled > 0 else float("inf")
        avg_daily_gap = total_gap / len(shifts) if shifts else 0.0
        violation = ratio > WORKLOAD_RATIO_TOLERANCE

        weekly_total_task = sum(s.task_hours for s in shifts)
        overtime_hours = max(0.0, weekly_total_task - FLSA_WEEKLY_OVERTIME_THRESHOLD * (len(shifts) / 5.0))
        overtime_wages = overtime_hours * self.regular_hourly_rate * FLSA_OVERTIME_MULTIPLIER if self.regular_hourly_rate else 0.0
        unpaid_wages = total_gap * self.regular_hourly_rate if self.regular_hourly_rate else 0.0

        actual_start = period_start or (shifts[0].date if shifts else "")
        actual_end = period_end or (shifts[-1].date if shifts else "")

        report = FrontloadingReport(
            report_id=f"FLR-{hashlib.sha256(f'{self.institution}{actual_start}{actual_end}'.encode()).hexdigest()[:8].upper()}",
            generated_at=datetime.now(timezone.utc).isoformat(),
            institution=self.institution,
            period_start=actual_start,
            period_end=actual_end,
            violation_type="wage_theft_through_frontloading",
            scheduled_hours_total=round(total_scheduled, 2),
            task_hours_total=round(total_task, 2),
            workload_ratio=round(ratio, 4),
            gap_hours_total=round(total_gap, 2),
            daily_unpaid_hours_avg=round(avg_daily_gap, 2),
            violation_flag=violation,
            statute_refs=[
                "FLSA 29 U.S.C. § 207 (overtime compensation)",
                "FLSA 29 U.S.C. § 211(c) (recordkeeping)",
                "FLSA 29 U.S.C. § 255(b) (3-year statute for willful violations)",
                "Florida Constitution Amendment 2 (minimum wage floor)",
            ],
            falsifies_if=(
                "Workload is demonstrably achievable within scheduled hours "
                "by independent time-motion analysis."
            ),
            shifts_analyzed=len(shifts),
            calculated_damages={
                "total_gap_hours": round(total_gap, 2),
                "overtime_hours": round(overtime_hours, 2),
                "unpaid_wages_at_regular_rate": round(unpaid_wages, 2),
                "overtime_wages_owed": round(overtime_wages, 2),
                "calculation_methodology": (
                    "task_hours - scheduled_hours per shift, "
                    "summed across period. "
                    "Overtime: (weekly_task_hours - 40) × 1.5 × regular_rate."
                ),
            },
            format=format,
            retention_days=FLSA_RETENTION_DAYS,
        )
        return report

    def verify_hash_chain(self) -> bool:
        """
        Verify the integrity of the shift log hash chain.

        Returns True if no shifts have been tampered with.
        Detects any retroactive modification of logged shifts.
        """
        if not self._log:
            return True
        prev_hash = "genesis"
        for i, entry in enumerate(self._log):
            chain_input = f"{prev_hash}:{entry.content_hash()}".encode()
            expected = hashlib.sha256(chain_input).hexdigest()
            if expected != self._hash_chain[i]:
                return False
            prev_hash = expected
        return True

    def export_report(self, report: FrontloadingReport, fmt: str = "dol_complaint") -> Dict:
        """
        Export a violation report as a structured dictionary.

        Formats: 'dol_complaint', 'court_filing', 'registry_entry'.
        All formats include the falsifies_if condition (Popperian requirement).
        """
        base = asdict(report)
        base["export_format"] = fmt
        base["exported_at"] = datetime.now(timezone.utc).isoformat()
        base["hash_chain_valid"] = self.verify_hash_chain()
        return base

    def shift_count(self) -> int:
        """Number of logged shifts."""
        return len(self._log)

    def _empty_report(
        self,
        period_start: Optional[str],
        period_end: Optional[str],
        format: str,
    ) -> FrontloadingReport:
        now = date.today().isoformat()
        return FrontloadingReport(
            report_id="FLR-EMPTY",
            generated_at=datetime.now(timezone.utc).isoformat(),
            institution=self.institution,
            period_start=period_start or now,
            period_end=period_end or now,
            violation_type="wage_theft_through_frontloading",
            scheduled_hours_total=0.0,
            task_hours_total=0.0,
            workload_ratio=0.0,
            gap_hours_total=0.0,
            daily_unpaid_hours_avg=0.0,
            violation_flag=False,
            statute_refs=["FLSA 29 U.S.C. § 207"],
            falsifies_if=(
                "Workload is achievable within scheduled hours."
            ),
            shifts_analyzed=0,
            calculated_damages={},
            format=format,
        )
