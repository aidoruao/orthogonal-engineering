"""D_FORENSIC_TELEMETRY implementation -- Forensic telemetry evidence structures.

Part 1 of Forensic Offensive Campaign.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, List


@dataclass(frozen=True)
class TelemetryEvidence:
    """A single piece of forensic telemetry evidence.

    falsifies_if: timestamp is empty or source is empty.
    """
    timestamp: str
    source: str
    event_type: str
    metadata: Dict[str, str]


@dataclass(frozen=True)
class DataPipelineState:
    """State of the OE->Kimi data pipeline at a point in time.

    falsifies_if: structural_isomorphism_count < 0 or beta_window_days < 0.
    """
    pipeline_id: str
    confirmed_open: bool
    structural_isomorphism_count: int
    data_policy_version: str
    cross_validation_lineage_length: int
    rfc_date: str
    solution_date: str
    beta_window_days: int


@dataclass(frozen=True)
class ForensicReport:
    """Aggregate forensic report over a corpus of telemetry evidence.

    falsifies_if: total_evidence == 0 while claiming confirmation.
    """
    report_id: str
    total_evidence: int
    confirmed_pipeline_count: int
    timeline_gaps: int
    lineage_gaps: int
    dating_anomalies: int
    beta_overlaps: int
    confidence_ratio: Fraction


DOMAIN_METADATA = {
    "name": "d_forensic_telemetry",
    "version": "1.0.0",
    "part": "1",
    "campaign": "CAMPAIGN-FORENSIC-OFFENSIVE-001",
}
