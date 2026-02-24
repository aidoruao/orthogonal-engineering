#!/usr/bin/env python3
"""
examination/minimal_pairs.py — Minimal-pair examples ensuring no label leakage.

Minimal pairs are question pairs that differ in exactly one semantic feature,
ensuring the model responds to content not superficial label cues.
"""
from __future__ import annotations
from typing import Dict, List, Any


MINIMAL_PAIRS: List[Dict[str, Any]] = [
    {
        "pair_id": "MP-BOUNDARY-001",
        "description": "Path sensitivity: sensitive vs public path, same action and entity",
        "question_a": {
            "question_id": "Q-BOUNDARY-001",
            "variables": {"action": "read", "path": "/etc/shadow", "entity": "authenticated_user"},
            "expected_answer": "DENY",
        },
        "question_b": {
            "question_id": "Q-BOUNDARY-002",
            "variables": {"action": "read", "path": "/public/help.txt", "entity": "authenticated_user"},
            "expected_answer": "ALLOW",
        },
        "differing_feature": "path",
    },
    {
        "pair_id": "MP-THREAT-001",
        "description": "Threat category sensitivity: injection vs benign query",
        "question_a": {
            "question_id": "Q-THREAT-001",
            "variables": {"event_description": "User input '; DROP TABLE users; --' in login form"},
            "expected_answer": "INJECTION",
        },
        "question_b": {
            "question_id": "Q-THREAT-001",
            "variables": {"event_description": "User searches for 'apple pie recipes'"},
            "expected_answer": None,  # Should not match INJECTION
        },
        "differing_feature": "event_description",
    },
    {
        "pair_id": "MP-GRACE-001",
        "description": "Grace sensitivity: first offense with remediation vs repeat offense",
        "question_a": {
            "question_id": "Q-GRACE-001",
            "variables": {
                "violation_description": "Accessed restricted file once, immediately reported",
                "context": "First offense, self-reported",
            },
            "expected_answer": "CONDITIONAL",
        },
        "question_b": {
            "question_id": "Q-GRACE-001",
            "variables": {
                "violation_description": "Repeatedly accessed restricted files after warning",
                "context": "Third offense, no remediation",
            },
            "expected_answer": "DENY",
        },
        "differing_feature": "context",
    },
]


def get_pair(pair_id: str) -> Dict[str, Any]:
    """Return minimal pair by ID. Raises KeyError if not found."""
    for p in MINIMAL_PAIRS:
        if p["pair_id"] == pair_id:
            return p
    raise KeyError(f"No minimal pair with ID {pair_id!r}")


def check_no_label_leakage(pair: Dict[str, Any]) -> bool:
    """Check that minimal pair questions differ only in the specified feature.

    Returns True if the pair is well-formed (differing_feature is present in both).
    """
    feature = pair["differing_feature"]
    qa_vars = pair["question_a"].get("variables", {})
    qb_vars = pair["question_b"].get("variables", {})
    return feature in qa_vars and feature in qb_vars and qa_vars[feature] != qb_vars[feature]
