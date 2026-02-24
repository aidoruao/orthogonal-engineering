#!/usr/bin/env python3
"""
revocation/triggers.py — Explicit revocation triggers and evidence types.
"""
from __future__ import annotations
from typing import Any, Dict, List


REVOCATION_TRIGGERS = {
    "POLICY_VIOLATION": {
        "description": "Candidate violated established policies",
        "evidence_required": ["violation_report", "timestamp"],
    },
    "SECURITY_BREACH": {
        "description": "Candidate involved in security breach",
        "evidence_required": ["incident_report", "severity"],
    },
    "MISREPRESENTATION": {
        "description": "Candidate misrepresented identity or credentials",
        "evidence_required": ["evidence_of_misrepresentation"],
    },
    "INACTIVITY": {
        "description": "Certificate expired due to inactivity",
        "evidence_required": ["last_activity_date"],
    },
    "VOLUNTARY": {
        "description": "Candidate voluntarily surrendered certificate",
        "evidence_required": ["candidate_statement"],
    },
}


def is_valid_trigger(trigger: str) -> bool:
    """Return True if trigger is a known revocation trigger."""
    return trigger in REVOCATION_TRIGGERS


def get_required_evidence(trigger: str) -> List[str]:
    """Return list of required evidence keys for trigger."""
    return REVOCATION_TRIGGERS.get(trigger, {}).get("evidence_required", [])


def validate_trigger_evidence(trigger: str, evidence: Dict[str, Any]) -> List[str]:
    """Validate that evidence contains all required keys for trigger."""
    violations: List[str] = []
    if not is_valid_trigger(trigger):
        violations.append(f"unknown trigger: {trigger!r}")
        return violations
    required = get_required_evidence(trigger)
    for key in required:
        if key not in evidence:
            violations.append(f"missing evidence key: {key!r}")
    return violations
