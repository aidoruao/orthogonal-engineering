"""D_FBI_TRAINING Implementation — Quantico evidence and certification records.

All arithmetic uses Fraction. No floats.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple


@dataclass(frozen=True)
class EvidenceItem:
    """Evidence item with chain-of-custody hashes (FBI DIOG, Fed. R. Evid. 901)."""

    item_id: str
    collector_id: str
    timestamp: Fraction  # collection time
    chain_of_custody: Tuple[str, ...]  # ordered list of handlers
    hash_at_collection: str  # SHA-256 at time of collection
    current_hash: str  # SHA-256 now
    sealed: bool


@dataclass(frozen=True)
class AgentCertification:
    """Agent certification record (Quantico training and periodic qualification)."""

    agent_id: str
    certification_type: str  # e.g. "firearms", "forensics"
    exam_score: Fraction  # 0-1
    pass_threshold: Fraction  # minimum to pass
    exam_date: Fraction  # timestamp
    expiry_date: Fraction  # certification expiry
    witnessed: bool
    witness_id: str


@dataclass(frozen=True)
class UseOfForceReport:
    """Use-of-force report aligned with DOJ/FBI policy proportionality tests."""

    report_id: str
    agent_id: str
    force_level: Fraction  # 0-1 scale
    threat_level: Fraction  # 0-1 scale
    proportionality_ratio: Fraction  # force/threat
    max_authorized_ratio: Fraction  # policy limit
    de_escalation_attempted: bool
    witnesses: Tuple[str, ...]
    timestamp: Fraction


@dataclass(frozen=True)
class DigitalForensicArtifact:
    """Digital forensic artifact integrity record (hash preservation, chain-of-custody)."""

    artifact_id: str
    source_device: str
    extraction_method: str
    hash_at_extraction: str
    current_hash: str
    examiner_id: str
    tool_version: str
    timestamp: Fraction
