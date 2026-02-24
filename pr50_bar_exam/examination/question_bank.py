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
