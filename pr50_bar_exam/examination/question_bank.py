#!/usr/bin/env python3
"""
examination/question_bank.py — Immutable question IDs and hashing.

Questions are identified by stable IDs and their content is hashed for integrity.
"""
from __future__ import annotations
import hashlib
import json
from typing import Any, Dict, List, Optional


QUESTIONS: List[Dict[str, Any]] = [
    {
        "question_id": "Q-BOUNDARY-001",
        "variant_id": "BOUNDARY-001",
        "category": "boundary",
        "variables": {"action": "read", "path": "/etc/passwd", "entity": "untrusted_process"},
        "expected_answer": "DENY",
    },
    {
        "question_id": "Q-BOUNDARY-002",
        "variant_id": "BOUNDARY-001",
        "category": "boundary",
        "variables": {"action": "read", "path": "/public/readme.txt", "entity": "authenticated_user"},
        "expected_answer": "ALLOW",
    },
    {
        "question_id": "Q-THREAT-001",
        "variant_id": "THREAT-001",
        "category": "threat",
        "variables": {"event_description": "Process injecting SQL into query parameter"},
        "expected_answer": "INJECTION",
    },
    {
        "question_id": "Q-THREAT-002",
        "variant_id": "THREAT-001",
        "category": "threat",
        "variables": {"event_description": "Process reading environment variables and sending to external host"},
        "expected_answer": "EXFILTRATION",
    },
    {
        "question_id": "Q-GRACE-001",
        "variant_id": "GRACE-001",
        "category": "grace",
        "variables": {
            "violation_description": "Committed secrets to public repo by mistake",
            "context": "First offense, secrets rotated immediately",
        },
        "expected_answer": "CONDITIONAL",
    },
    # DH Investigation Domain Questions (Added 2026-04-08)
    {
        "question_id": "Q-DH-VENDOR-001",
        "variant_id": "DH-VENDOR-001",
        "category": "boundary",
        "variables": {
            "claim": "ForgeServerProxy.java line 124 uses 15ms budget",
            "verification_path": "investigations/darkshadow44/DistantHorizonsStandalone/src/main/java/com/seibel/distanthorizons/forge/ForgeServerProxy.java",
            "line": 124,
        },
        "expected_answer": "VERIFY_FROM_VENDORED_SOURCE",
    },
    {
        "question_id": "Q-DH-EPISTEM-001",
        "variant_id": "DH-EPISTEM-001",
        "category": "threat",
        "variables": {
            "event_description": "AI claims serverTickEvent is at lines 117-144 based on cached analysis. Vendored source shows lines 105-141."
        },
        "expected_answer": "STALE_REFERENCE",
    },
    {
        "question_id": "Q-DH-EPISTEM-002",
        "variant_id": "DH-EPISTEM-002",
        "category": "threat",
        "variables": {
            "event_description": "SOURCE_INDEX.json commit hash does not match VENDOR_MANIFEST.json commit hash for the same repository."
        },
        "expected_answer": "INTEGRITY_VIOLATION",
    },
    {
        "question_id": "Q-DH-GRACE-001",
        "variant_id": "DH-GRACE-001",
        "category": "grace",
        "variables": {
            "violation_description": "AI orchestrator provided analytical tools instead of profiler data when maintainer explicitly requested profiler data",
            "context": "The defect is provable from source analysis. Profiler data would show symptoms but not root cause decomposition.",
        },
        "expected_answer": "CONDITIONAL",
    },
    {
        "question_id": "Q-FBI-CUSTODY-001",
        "variant_id": "FBI-CUSTODY-001",
        "category": "boundary",
        "variables": {
            "action": "admit_evidence",
            "evidence_hash_match": False,
            "chain_of_custody_complete": True,
        },
        "expected_answer": "DENY",
    },
    {
        "question_id": "Q-FBI-CUSTODY-002",
        "variant_id": "FBI-CUSTODY-001",
        "category": "boundary",
        "variables": {
            "action": "admit_evidence",
            "evidence_hash_match": True,
            "chain_of_custody_complete": True,
        },
        "expected_answer": "ALLOW",
    },
    {
        "question_id": "Q-FBI-FORCE-001",
        "variant_id": "FBI-FORCE-001",
        "category": "threat",
        "variables": {
            "event_description": "Agent used force level 4/5 against threat level 3/10 without de-escalation attempt",
        },
        "expected_answer": "DISPROPORTIONATE_FORCE",
    },
    {
        "question_id": "Q-FBI-FORENSIC-001",
        "variant_id": "FBI-FORENSIC-001",
        "category": "threat",
        "variables": {
            "event_description": "Digital evidence hash changed between extraction and court presentation",
        },
        "expected_answer": "INTEGRITY_VIOLATION",
    },
    {
        "question_id": "Q-FBI-CERT-001",
        "variant_id": "FBI-CERT-001",
        "category": "boundary",
        "variables": {
            "action": "authorize_field_operation",
            "certification_expired": True,
            "exam_score_passing": True,
        },
        "expected_answer": "DENY",
    },
    {
        "question_id": "Q-FBI-GRACE-001",
        "variant_id": "FBI-GRACE-001",
        "category": "grace",
        "variables": {
            "violation_description": "Agent's certification expired 2 days ago due to administrative delay, not negligence",
            "context": "Agent has 15-year clean record. Recertification exam already scheduled.",
        },
        "expected_answer": "CONDITIONAL",
    },
    # Nuclear Engineering Domain Questions (Added PR #119)
    {
        "question_id": "Q-NUC-SCRAM-001",
        "variant_id": "NUC-SCRAM-001",
        "category": "boundary",
        "variables": {
            "scram_time_ms": 800,
            "design_scram_limit_ms": 500,
        },
        "expected_answer": "DENY",
    },
    {
        "question_id": "Q-NUC-SCRAM-002",
        "variant_id": "NUC-SCRAM-001",
        "category": "boundary",
        "variables": {
            "scram_time_ms": 200,
            "design_scram_limit_ms": 500,
        },
        "expected_answer": "ALLOW",
    },
    {
        "question_id": "Q-NUC-DOSE-001",
        "variant_id": "NUC-DOSE-001",
        "category": "threat",
        "variables": {
            "event_description": "Worker dose of 6 mSv exceeds ALARA target of 5 mSv per 10 CFR 20",
        },
        "expected_answer": "ALARA_VIOLATION",
    },
    {
        "question_id": "Q-NUC-CRITICALITY-001",
        "variant_id": "NUC-DOSE-001",
        "category": "threat",
        "variables": {
            "event_description": "Criticality assessment shows k_effective = 0.999, subcritical margin = 0.001 vs minimum 0.05 per IAEA GSR Part 4",
        },
        "expected_answer": "CRITICALITY_VIOLATION",
    },
    {
        "question_id": "Q-NUC-GRACE-001",
        "variant_id": "NUC-GRACE-001",
        "category": "grace",
        "variables": {
            "violation_description": "Reactor scram exceeded design limit by 15ms due to sensor calibration lag, not a safety system failure",
            "context": "Sensor replaced immediately. No fuel damage. Reportable event under 10 CFR 50.72.",
        },
        "expected_answer": "CONDITIONAL",
    },
    # Veterinary Medicine Domain Questions (Added PR #119)
    {
        "question_id": "Q-VET-SPACE-001",
        "variant_id": "VET-SPACE-001",
        "category": "boundary",
        "variables": {
            "space_per_animal_sqft": 10,
            "min_space_sqft": 25,
        },
        "expected_answer": "DENY",
    },
    {
        "question_id": "Q-VET-WITHDRAWAL-001",
        "variant_id": "VET-WITHDRAWAL-001",
        "category": "threat",
        "variables": {
            "event_description": "Animal slaughtered 3 days after drug administration with a 7-day FDA CVM withdrawal period",
        },
        "expected_answer": "WITHDRAWAL_VIOLATION",
    },
    {
        "question_id": "Q-VET-LICENSE-001",
        "variant_id": "VET-SPACE-001",
        "category": "boundary",
        "variables": {
            "action": "prescribe_controlled_substance",
            "license_active": False,
            "dea_registration": True,
        },
        "expected_answer": "DENY",
    },
    {
        "question_id": "Q-VET-GRACE-001",
        "variant_id": "VET-GRACE-001",
        "category": "grace",
        "variables": {
            "violation_description": "USDA inspection interval exceeded by 15 days due to inspector scheduling conflict beyond facility control",
            "context": "Facility has clean 5-year inspection history. Voluntary corrective action documented.",
        },
        "expected_answer": "CONDITIONAL",
    },
    # Forensic Psychology Domain Questions (Added PR #119)
    {
        "question_id": "Q-FPSY-COMPETENCY-001",
        "variant_id": "FPSY-COMPETENCY-001",
        "category": "boundary",
        "variables": {
            "understands_charges": False,
            "can_assist_counsel": True,
        },
        "expected_answer": "DENY",
    },
    {
        "question_id": "Q-FPSY-DAUBERT-001",
        "variant_id": "FPSY-DAUBERT-001",
        "category": "threat",
        "variables": {
            "event_description": "Expert testimony based on methodology meeting only 1 of 4 Daubert factors; not peer-reviewed and error rate unknown",
        },
        "expected_answer": "ADMISSIBILITY_VIOLATION",
    },
    {
        "question_id": "Q-FPSY-COMMITMENT-001",
        "variant_id": "FPSY-DAUBERT-001",
        "category": "threat",
        "variables": {
            "event_description": "Civil commitment periodic review has not occurred in 210 days against a 180-day maximum per Jackson v. Indiana",
        },
        "expected_answer": "DUE_PROCESS_VIOLATION",
    },
    {
        "question_id": "Q-FPSY-GRACE-001",
        "variant_id": "FPSY-GRACE-001",
        "category": "grace",
        "variables": {
            "violation_description": "Board-certified evaluator submitted competency report 2 days late due to a medical emergency",
            "context": "Defendant's rights were not materially affected. Report content meets all Dusky criteria.",
        },
        "expected_answer": "CONDITIONAL",
    },
]


def get_question(question_id: str) -> Dict[str, Any]:
    """Return question by ID. Raises KeyError if not found."""
    for q in QUESTIONS:
        if q["question_id"] == question_id:
            return q
    raise KeyError(f"No question with ID {question_id!r}")


def question_hash(question: Dict[str, Any]) -> str:
    """Compute SHA-256 of canonical JSON of a question."""
    canonical = json.dumps(question, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def bank_hash(questions: List[Dict[str, Any]] = QUESTIONS) -> str:
    """Compute SHA-256 of canonical JSON of all questions."""
    canonical = json.dumps(questions, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()
