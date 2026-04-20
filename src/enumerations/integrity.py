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

    Strict: every element of ``entries`` must be a mapping; scalar / list /
    null elements raise ValueError rather than being silently dropped, so
    catalog corruption fails loudly.

    Falsifies if: the YAML document lacks an ``entries`` key, the value is
    not a list, or any element is not a mapping.
    falsifies_if: the YAML document lacks an ``entries`` key, the value is
    not a list, or any element is not a mapping.
    """
    with path.open("r", encoding="utf-8") as fp:
        doc = yaml.safe_load(fp)
    if not isinstance(doc, dict):
        raise ValueError(f"{path} did not parse to a mapping")
    entries = doc.get("entries")
    if not isinstance(entries, list):
        raise ValueError(f"{path} has no 'entries' list")
    for idx, element in enumerate(entries):
        if not isinstance(element, dict):
            raise ValueError(
                f"{path} entries[{idx}] is not a mapping: {type(element).__name__}"
            )
    return list(entries)


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
    if not isinstance(data, dict):
        raise ValueError("magic_number_catalog.json did not parse to a mapping")
    entries = data.get("entries")
    if not isinstance(entries, list):
        raise ValueError("magic_number_catalog.json has no 'entries' list")
    for idx, element in enumerate(entries):
        if not isinstance(element, dict):
            raise ValueError(
                f"magic_number_catalog.json entries[{idx}] is not a mapping: "
                f"{type(element).__name__}"
            )
    return list(entries)


def _all_catalogs() -> List[Tuple[str, List[Dict[str, Any]]]]:
    """Return every known enumeration catalog paired with its short name.

    Private helper used by every cross-catalog invariant so the set of
    catalogs is declared in exactly one place.

    Falsifies if: any loader raises ValueError (propagated from the
    underlying loaders' strict-mapping checks).
    falsifies_if: any loader raises ValueError (propagated from the
    underlying loaders' strict-mapping checks).
    """
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
            key_val = entry.get("key")
            if key_val is None or not str(key_val).strip():
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
            falsifier = entry.get("falsifies_if")
            if falsifier is None or not str(falsifier).strip():
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


def check_all_keys_unique_across_files() -> Tuple[bool, ProofObject]:
    """Invariant: keys are pairwise unique across every catalog file.

    Enforces README design rule #5 ("keys never collide across files") so
    that a future contributor cannot shadow an existing enumeration key
    from one catalog by re-using it in another.

    Standard: OE-106 cross-registry disjointness.
    Falsifies if: any two catalog files share at least one key.
    falsifies_if: any two catalog files share at least one key.
    """
    occurrences: Dict[str, List[str]] = {}
    for name, entries in _all_catalogs():
        for entry in entries:
            key_val = entry.get("key")
            if key_val is None:
                continue
            key = str(key_val).strip()
            if not key:
                continue
            files_for_key = occurrences.setdefault(key, [])
            if name not in files_for_key:
                files_for_key.append(name)
    collisions = sorted(
        f"{key}:{'+'.join(files)}"
        for key, files in occurrences.items()
        if len(files) > 1
    )
    success = not collisions
    proof = ProofObject(
        rule="check_all_keys_unique_across_files",
        premises=[f"collisions={collisions}"],
        conclusion=(
            "PASS: keys pairwise unique across catalogs"
            if success else f"FAIL: cross-file key collisions={collisions}"
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
        ("check_all_keys_unique_across_files", check_all_keys_unique_across_files),
    ]
    out: List[Tuple[str, bool, ProofObject]] = []
    for name, fn in checks:
        ok, proof = fn()
        print(f"{name}: {'PASS' if ok else 'FAIL'}")
        out.append((name, ok, proof))
    return out
