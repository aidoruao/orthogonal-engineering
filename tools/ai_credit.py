"""
AI co-author attribution with consent log.

Adds AI co-author metadata to commit trailers and .ai_registry.json.
Requires explicit consent flow.

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0

falsifies_if: consent hash does not match SHA-256 of the consent text.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


def _hash_consent(consent_text: str) -> str:
    return hashlib.sha256(consent_text.encode("utf-8")).hexdigest()


def format_ai_trailer(
    model_id: str,
    model_hash: str,
    name: str = "KimiAI",
    email: str = "kimi@local",
) -> str:
    """Format a Co-Authored-By trailer line for git commits."""
    return f"Co-Authored-By: {name} <{email}> id={model_id} model_hash={model_hash}"


def register_ai_coauthor(
    model_id: str,
    model_hash: str,
    consent_file: str,
    registry_path: str = ".ai_registry.json",
) -> Dict[str, Any]:
    """
    Update registry file and return registry entry dict.

    Args:
        model_id: Unique model identifier.
        model_hash: SHA-256 hash of model declaration or artifact.
        consent_file: Path to consent evidence file.
        registry_path: Path to .ai_registry.json.

    Returns:
        Registry entry dict.
    """
    consent_path = Path(consent_file)
    if not consent_path.exists():
        raise FileNotFoundError(f"Consent file not found: {consent_file}")

    consent_text = consent_path.read_text()
    consent_hash = _hash_consent(consent_text)

    entry = {
        "id": model_id,
        "model_hash": model_hash,
        "declaration": f"AI co-author registration for {model_id}",
        "consent_hash": consent_hash,
        "consent_file": str(consent_path.resolve()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    registry = Path(registry_path)
    if registry.exists():
        with open(registry) as f:
            data = json.load(f)
    else:
        data = {}

    if "co_authors" not in data:
        data["co_authors"] = []

    # Replace existing entry with same id
    data["co_authors"] = [e for e in data["co_authors"] if e.get("id") != model_id]
    data["co_authors"].append(entry)

    with open(registry, "w") as f:
        json.dump(data, f, indent=2, default=str)

    # Append to consent log
    log_entry = {
        "action": "ai_coauthor_consent",
        "authoriser": "@aidoruao",
        "candidate_id": model_id,
        "consent_hash": consent_hash,
        "justification": f"AI co-author consent registered for {model_id}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    log_path = Path("pr47_stewardship/witness/consent_log.jsonl")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return entry


def validate_ai_credit_env() -> Optional[str]:
    """
    Validate environment for automated AI credit in CI.

    Returns consent file path if valid, None otherwise.
    """
    if os.environ.get("KIMI_AI_CREDIT") != "1":
        return None
    consent_path = os.environ.get("KIMI_AI_CONSENT_FILE")
    if not consent_path or not Path(consent_path).exists():
        return None
    return consent_path
