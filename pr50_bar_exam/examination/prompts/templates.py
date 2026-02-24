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
