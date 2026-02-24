#!/usr/bin/env python3
"""
examination/parsing.py — Strict JSON-only response parsing with schema validation.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

try:
    import jsonschema
    _HAS_JSONSCHEMA = True
except ImportError:
    _HAS_JSONSCHEMA = False


SCHEMAS_DIR = Path(__file__).parent.parent / "schemas"


def load_schema(schema_name: str) -> Dict[str, Any]:
    """Load a JSON Schema by name (without .schema.json suffix)."""
    schema_path = SCHEMAS_DIR / f"{schema_name}.schema.json"
    return json.loads(schema_path.read_text(encoding="utf-8"))


def parse_strict_json(raw: str) -> Tuple[Optional[Dict], Optional[str]]:
    """Parse raw string as strict JSON. Returns (parsed, error_message).

    Rejects any non-JSON input. No markdown, no prose, no fences.
    """
    raw = raw.strip()
    if not raw:
        return None, "empty response"
    if not raw.startswith("{"):
        return None, f"response must be a JSON object, got: {raw[:40]!r}"
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        return None, f"JSON decode error: {e}"
    if not isinstance(parsed, dict):
        return None, "response must be a JSON object (dict)"
    return parsed, None


def validate_against_schema(data: Dict, schema_name: str) -> Optional[str]:
    """Validate data against named schema. Returns error string or None."""
    if not _HAS_JSONSCHEMA:
        return None  # skip if jsonschema not available
    try:
        schema = load_schema(schema_name)
        jsonschema.validate(data, schema)
        return None
    except jsonschema.ValidationError as e:
        return f"schema validation error: {e.message}"
    except Exception as e:
        return f"unexpected validation error: {e}"


def parse_response(raw: str, schema_name: str) -> Tuple[Optional[Dict], Optional[str]]:
    """Parse and validate a response. Returns (parsed, error_message)."""
    parsed, err = parse_strict_json(raw)
    if err:
        return None, err
    err = validate_against_schema(parsed, schema_name)
    if err:
        return None, err
    return parsed, None
