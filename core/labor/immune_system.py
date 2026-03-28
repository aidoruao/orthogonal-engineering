"""
immune_system.py
----------------
InstitutionalImmuneSystem: orchestrator that composes the registry,
mapper, documenter, trainer, and distributor into a single disrupt() pipeline.

The immune system is the architectural capstone: it ties together the
labor violations registry, the cross-institution pattern mapper, the
automated documentation engine, and the training spec into a single
enforcement pipeline that is:
  - Forkable: replace institution name to adapt to any employer
  - Embeddable: outputs are union-kit and legal-aid ready
  - AI-native: training_spec.yaml maps each objective to a falsification test
  - Permanent: hash-chain archived, Internet Archive compatible

Invariant: the system must produce a disrupt() output that includes
a falsifies_if condition for every violation pattern it identifies.
No violation without a Popperian falsification condition. Ever.

# @domain: D_LABOR_RIGHTS
# @falsification_id: INV-LAB-004 (WORKLOAD_ACCOUNTABILITY)
# @authority: FLSA 29 U.S.C. § 207; ontology/labor_violations_registry.yaml
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional

from core.labor.automated_documentation import (
    FLSA_RETENTION_DAYS,
    FrontloadingReport,
    WageTheftDocumentationEngine,
)
from core.labor.institution_mapper import InstitutionMapper


class InstitutionalImmuneSystem:
    """
    Orchestrates all labor rights enforcement layers into a single pipeline.

    Architecture:
      Layer 1 — Registry:      labor_violations_registry.yaml (permanent public record)
      Layer 2 — Mapper:        InstitutionMapper (cross-institution isomorphism)
      Layer 3 — Documenter:    WageTheftDocumentationEngine (shift log + frontloading)
      Layer 4 — Trainer:       training_spec.yaml (AI learning objectives)
      Layer 5 — Distributor:   disrupt() report (forkable, embeddable, AI-native)

    The disrupt() method is the primary entry point. It:
      1. Verifies the hash chain of the shift log (tamper detection)
      2. Detects frontloading violations across logged shifts
      3. Maps the detected pattern across institutions (systemic evidence)
      4. Generates a DOL-formatted violation report
      5. Returns the complete enforcement package as a structured dict

    Usage::

        system = InstitutionalImmuneSystem(
            institution="Bay District Schools",
            location="Bay County, Florida",
            scheduled_hours_per_shift=5.75,
            regular_hourly_rate=15.0,
        )
        system.log_shift("2026-03-28", tasks=[...])
        result = system.disrupt()
        print(result["violation_flag"])  # True
        print(result["falsifies_if"])    # Popperian condition
    """

    VERSION = "1.0"
    SCHEMA = "institutional-immune-system/1.0"

    def __init__(
        self,
        institution: str = "Unknown Institution",
        location: str = "",
        scheduled_hours_per_shift: float = 0.0,
        employee_classification: str = "part-time",
        regular_hourly_rate: float = 0.0,
    ) -> None:
        self.institution = institution
        self.location = location
        self.scheduled_hours_per_shift = scheduled_hours_per_shift

        self._documenter = WageTheftDocumentationEngine(
            institution=institution,
            location=location,
            employee_classification=employee_classification,
            regular_hourly_rate=regular_hourly_rate,
        )
        self._mapper = InstitutionMapper()
        self._disrupt_calls: int = 0

    def log_shift(
        self,
        date_str: str,
        tasks: List[Dict],
        actual_start: Optional[str] = None,
        actual_end: Optional[str] = None,
        compensation_status: str = "compensated",
        notes: str = "",
    ) -> None:
        """
        Log a compensable work event to the immune system's shift log.

        Each call appends an immutable, hashed entry to the shift log.
        The hash chain makes retroactive modification detectable.
        """
        shift_id = f"{date_str}-{self._documenter.shift_count() + 1:04d}"
        self._documenter.log_shift(
            shift_id=shift_id,
            date_str=date_str,
            scheduled_hours=self.scheduled_hours_per_shift,
            tasks=tasks,
            actual_start=actual_start,
            actual_end=actual_end,
            compensation_status=compensation_status,
            notes=notes,
        )

    def disrupt(
        self,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None,
        format: str = "dol_complaint",
    ) -> Dict:
        """
        Execute the full enforcement pipeline.

        Returns a structured enforcement package containing:
          - violation_flag: bool
          - violation_type: str
          - frontloading_report: FrontloadingReport as dict
          - isomorphism_report: cross-institution structural mapping
          - hash_chain_valid: bool (tamper detection)
          - falsifies_if: str (Popperian condition — always present)
          - distribution_metadata: forkable/embeddable/AI-native flags

        The falsifies_if field is non-negotiable. Every disrupt() call
        produces a Popperian falsification condition, even when no
        violation is detected.
        """
        self._disrupt_calls += 1

        hash_chain_valid = self._documenter.verify_hash_chain()
        report = self._documenter.detect_frontloading(
            period_start=period_start,
            period_end=period_end,
            format=format,
        )
        isomorphism_report = self._mapper.generate_report()
        exported = self._documenter.export_report(report, fmt=format)

        result: Dict = {
            "schema": self.SCHEMA,
            "version": self.VERSION,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "institution": self.institution,
            "location": self.location,
            "violation_flag": report.violation_flag,
            "violation_type": report.violation_type if report.violation_flag else None,
            "workload_ratio": report.workload_ratio,
            "gap_hours_total": report.gap_hours_total,
            "shifts_analyzed": report.shifts_analyzed,
            "hash_chain_valid": hash_chain_valid,
            "falsifies_if": report.falsifies_if,
            "statute_refs": report.statute_refs,
            "calculated_damages": report.calculated_damages,
            "frontloading_report": exported,
            "isomorphism_report": isomorphism_report,
            "distribution_metadata": {
                "forkable": True,
                "fork_instruction": (
                    "Replace institution name and location. "
                    "All structural invariants remain identical."
                ),
                "embeddable": True,
                "embed_targets": ["union kits", "legal aid", "DOL complaint forms"],
                "ai_native": True,
                "training_spec_ref": "core/labor/training_spec.yaml",
                "permanent": True,
                "archive_targets": ["GitHub Archive", "Internet Archive"],
                "retention_days": FLSA_RETENTION_DAYS,
            },
            "popperian_guarantee": (
                "Every violation pattern in this report has a falsifies_if condition. "
                "The falsifies_if condition specifies the observable evidence that would "
                "demonstrate the violation did NOT occur. This guarantee holds for every "
                "disrupt() call, including calls that detect no violation."
            ),
        }

        run_hash = hashlib.sha256(
            json.dumps(result, sort_keys=True, default=str).encode()
        ).hexdigest()
        result["report_hash"] = run_hash

        return result

    def shift_count(self) -> int:
        """Number of logged shifts."""
        return self._documenter.shift_count()

    def mapper(self) -> InstitutionMapper:
        """Access the underlying InstitutionMapper for pattern registration."""
        return self._mapper

    def documenter(self) -> WageTheftDocumentationEngine:
        """Access the underlying WageTheftDocumentationEngine for direct log access."""
        return self._documenter
