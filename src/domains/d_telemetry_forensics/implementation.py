"""D_TELEMETRY_FORENSICS implementation -- Telemetry forensics structures.

Part 7 of Forensic Offensive Campaign.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class CrashEvent:
    """A single crash event in the telemetry log.

    falsifies_if: timestamp is empty or version is empty.
    """
    timestamp: str
    version: str
    feature: str
    error_type: str


@dataclass(frozen=True)
class VersionDelta:
    """Delta between two versions.

    falsifies_if: days_to_fix < 0 or feature_count_delta < 0.
    """
    previous_version: str
    current_version: str
    days_to_fix: int
    feature_count_delta: int


@dataclass(frozen=True)
class TelemetryCorpus:
    """Aggregate telemetry corpus.

    falsifies_if: crash_count < 0 or session_count <= 0.
    """
    corpus_id: str
    crash_events: Tuple[CrashEvent, ...]
    version_deltas: Tuple[VersionDelta, ...]
    session_count: int
    correlation_score: Fraction


DOMAIN_METADATA = {
    "name": "d_telemetry_forensics",
    "version": "1.0.0",
    "part": "7",
    "campaign": "CAMPAIGN-FORENSIC-OFFENSIVE-001",
}
