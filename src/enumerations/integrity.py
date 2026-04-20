"""Integrity checks over the OE enumerations data files.

Uses PyYAML to load the YAML catalogs and stdlib ``json`` for the JSON
catalog. Every loader returns a list of dict entries.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

from axioms.logic import ProofObject

_HERE = Path(__file__).resolve().parent


def _load_yaml_entries(path: Path) -> List[Dict[str, Any]]:
    """Load ``entries`` from a YAML file and return as a list of dicts.

    Falsifies if: the YAML document lacks an ``entries`` key or the value is
    not a list.
    falsifies_if: the YAML document lacks an ``entries`` key or the value is
    not a list.
    """
    with path.open("r", encoding="utf-8") as fp:
        doc = yaml.safe_load(fp)
    if not isinstance(doc, dict):
        raise ValueError(f"{path} did not parse to a mapping")
    entries = doc.get("entries")
    if not isinstance(entries, list):
        raise ValueError(f"{path} has no 'entries' list")
    return [e for e in entries if isinstance(e, dict)]


def load_black_box_antipatterns() -> List[Dict[str, Any]]:
    """Load the anti-pattern catalog.

    Falsifies if: the YAML file cannot be parsed or yields no entries.
    falsifies_if: the YAML file cannot be parsed or yields no entries.
    """
    return _load_yaml_entries(_HERE / "black_box_antipatterns.yaml")


def load_hidden_failures() -> List[Dict[str, Any]]:
    """Load the hidden-failures catalog.

    Falsifies if: the YAML file cannot be parsed or yields no entries.
    falsifies_if: the YAML file cannot be parsed or yields no entries.
    """
    return _load_yaml_entries(_HERE / "hidden_failures.yaml")


def load_magic_numbers() -> List[Dict[str, Any]]:
    """Load the magic-number catalog from JSON.

    Falsifies if: the JSON file fails to parse or has no ``entries`` key.
    falsifies_if: the JSON file fails to parse or has no ``entries`` key.
    """
    with (_HERE / "magic_number_catalog.json").open("r", encoding="utf-8") as fp:
        data = json.load(fp)
    entries = data.get("entries")
    if not isinstance(entries, list):
        raise ValueError("magic_number_catalog.json has no 'entries' list")
    return [e for e in entries if isinstance(e, dict)]


def _all_catalogs() -> List[Tuple[str, List[Dict[str, Any]]]]:
    return [
        ("black_box_antipatterns", load_black_box_antipatterns()),
        ("hidden_failures", load_hidden_failures()),
        ("magic_numbers", load_magic_numbers()),
    ]


def check_all_entries_have_keys() -> Tuple[bool, ProofObject]:
    """Invariant: every entry across every file declares a 'key' field.

    Standard: ENUM-001 every enumeration entry is stable-identifiable.
    Falsifies if: any entry is missing a non-empty 'key' value.
    falsifies_if: any entry is missing a non-empty 'key' value.
    """
    offenders: List[str] = []
    for name, entries in _all_catalogs():
        for idx, entry in enumerate(entries):
            if not str(entry.get("key", "")).strip():
                offenders.append(f"{name}[{idx}]")
    success = not offenders
    proof = ProofObject(
        rule="check_all_entries_have_keys",
        premises=[f"offenders={offenders}"],
        conclusion=(
            "PASS: every entry has a key"
            if success else f"FAIL: missing keys={offenders}"
        ),
    )
    return success, proof


def check_all_entries_have_falsifies_if() -> Tuple[bool, ProofObject]:
    """Invariant: every entry declares a non-empty 'falsifies_if' field.

    Standard: YS-003 unfalsifiable = unaccountable.
    Falsifies if: any entry has an empty or missing falsifies_if string.
    falsifies_if: any entry has an empty or missing falsifies_if string.
    """
    offenders: List[str] = []
    for name, entries in _all_catalogs():
        for entry in entries:
            val = str(entry.get("falsifies_if", "")).strip()
            if not val:
                offenders.append(f"{name}:{entry.get('key', '<anon>')}")
    success = not offenders
    proof = ProofObject(
        rule="check_all_entries_have_falsifies_if",
        premises=[f"offenders={offenders}"],
        conclusion=(
            "PASS: every entry has a falsifies_if"
            if success else f"FAIL: missing falsifies_if={offenders}"
        ),
    )
    return success, proof


def check_all_keys_unique_per_file() -> Tuple[bool, ProofObject]:
    """Invariant: keys are pairwise unique within each file.

    Standard: OE-105 registry disjointness.
    Falsifies if: any file contains two entries with the same key.
    falsifies_if: any file contains two entries with the same key.
    """
    offenders: List[str] = []
    for name, entries in _all_catalogs():
        keys = [str(e.get("key", "")) for e in entries]
        duplicates = sorted({k for k in keys if keys.count(k) > 1 and k})
        for dup in duplicates:
            offenders.append(f"{name}:{dup}")
    success = not offenders
    proof = ProofObject(
        rule="check_all_keys_unique_per_file",
        premises=[f"offenders={offenders}"],
        conclusion=(
            "PASS: keys unique within every file"
            if success else f"FAIL: duplicates={offenders}"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run every enumeration integrity invariant.

    Standard: ENUM-010 enumeration self-audit.
    Falsifies if: any integrity check returns False.
    falsifies_if: any integrity check returns False.
    """
    checks = [
        ("check_all_entries_have_keys", check_all_entries_have_keys),
        ("check_all_entries_have_falsifies_if", check_all_entries_have_falsifies_if),
        ("check_all_keys_unique_per_file", check_all_keys_unique_per_file),
    ]
    out: List[Tuple[str, bool, ProofObject]] = []
    for name, fn in checks:
        ok, proof = fn()
        print(f"{name}: {'PASS' if ok else 'FAIL'}")
        out.append((name, ok, proof))
    return out
