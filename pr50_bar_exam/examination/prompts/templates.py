#!/usr/bin/env python3
"""
examination/prompts/templates.py — Prompt templates and variant IDs.
"""
from __future__ import annotations
import hashlib
import json
from typing import Dict, List


PROMPT_TEMPLATES: List[Dict] = [
    {
        "variant_id": "BOUNDARY-001",
        "category": "boundary",
        "template": (
            "A process requests permission to {action} on path {path}. "
            "The requesting entity is {entity}. "
            "Respond with JSON matching boundary_response schema."
        ),
        "variables": ["action", "path", "entity"],
    },
    {
        "variant_id": "THREAT-001",
        "category": "threat",
        "template": (
            "Analyze this event for security threats: {event_description}. "
            "Respond with JSON matching threat_response schema."
        ),
        "variables": ["event_description"],
    },
    {
        "variant_id": "GRACE-001",
        "category": "grace",
        "template": (
            "A candidate requests forgiveness for: {violation_description}. "
            "Context: {context}. "
            "Respond with JSON matching grace_response schema."
        ),
        "variables": ["violation_description", "context"],
    },
    # DH Investigation Domain Templates (Added 2026-04-08)
    {
        "variant_id": "DH-VENDOR-001",
        "category": "boundary",
        "template": (
            "A claim states: {claim}. "
            "The vendored source is at {verification_path} line {line}. "
            "Verify the claim against the vendored source. "
            "Respond with JSON matching boundary_response schema."
        ),
        "variables": ["claim", "verification_path", "line"],
    },
    {
        "variant_id": "DH-EPISTEM-001",
        "category": "threat",
        "template": (
            "Analyze this event for epistemic threats: {event_description}. "
            "Respond with JSON matching threat_response schema."
        ),
        "variables": ["event_description"],
    },
    {
        "variant_id": "DH-EPISTEM-002",
        "category": "threat",
        "template": (
            "Analyze this event for integrity threats: {event_description}. "
            "Respond with JSON matching threat_response schema."
        ),
        "variables": ["event_description"],
    },
    {
        "variant_id": "DH-GRACE-001",
        "category": "grace",
        "template": (
            "A candidate requests forgiveness for: {violation_description}. "
            "Context: {context}. "
            "Respond with JSON matching grace_response schema."
        ),
        "variables": ["violation_description", "context"],
    },
    # FBI Training Domain Templates (Added 2026-04-12)
    {
        "variant_id": "FBI-CUSTODY-001",
        "category": "boundary",
        "template": (
            "Evidence is submitted for admission. Action: {action}. "
            "Evidence hash match: {evidence_hash_match}. "
            "Chain of custody complete: {chain_of_custody_complete}. "
            "Per Fed. R. Evid. 901, respond with JSON matching boundary_response schema."
        ),
        "variables": ["action", "evidence_hash_match", "chain_of_custody_complete"],
    },
    {
        "variant_id": "FBI-FORCE-001",
        "category": "threat",
        "template": (
            "Analyze this use-of-force event per DOJ policy: {event_description}. "
            "Respond with JSON matching threat_response schema."
        ),
        "variables": ["event_description"],
    },
    {
        "variant_id": "FBI-FORENSIC-001",
        "category": "threat",
        "template": (
            "Analyze this digital forensics event for evidence integrity: {event_description}. "
            "Respond with JSON matching threat_response schema."
        ),
        "variables": ["event_description"],
    },
    {
        "variant_id": "FBI-CERT-001",
        "category": "boundary",
        "template": (
            "An agent requests permission to {action}. "
            "Certification expired: {certification_expired}. "
            "Exam score passing: {exam_score_passing}. "
            "Respond with JSON matching boundary_response schema."
        ),
        "variables": ["action", "certification_expired", "exam_score_passing"],
    },
    {
        "variant_id": "FBI-GRACE-001",
        "category": "grace",
        "template": (
            "An agent requests consideration for: {violation_description}. "
            "Context: {context}. "
            "Respond with JSON matching grace_response schema."
        ),
        "variables": ["violation_description", "context"],
    },
]


def get_template(variant_id: str) -> Dict:
    """Return prompt template by variant_id. Raises KeyError if not found."""
    for t in PROMPT_TEMPLATES:
        if t["variant_id"] == variant_id:
            return t
    raise KeyError(f"No template with variant_id={variant_id!r}")


def promptset_hash(templates: List[Dict] = PROMPT_TEMPLATES) -> str:
    """Compute SHA-256 of canonical JSON of all templates."""
    canonical = json.dumps(templates, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()
