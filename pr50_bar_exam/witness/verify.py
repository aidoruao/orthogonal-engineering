#!/usr/bin/env python3
"""
witness/verify.py — Full verification of witness chain from genesis.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pr50_bar_exam.witness.chain import (
    ENTRIES_DIR,
    GENESIS_PATH,
    canonical_bytes,
    entry_hash,
    load_genesis,
)


def verify_genesis(genesis: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Verify genesis block integrity."""
    errors: List[str] = []
    if "hash" not in genesis:
        errors.append("genesis missing 'hash' field")
        return False, errors
    filtered = {k: v for k, v in genesis.items() if k != "hash"}
    expected = hashlib.sha256(
        json.dumps(filtered, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()
    if genesis["hash"] != expected:
        errors.append(f"genesis hash mismatch: expected {expected}, got {genesis['hash']}")
    return not errors, errors


def verify_chain(
    entries_dir: Optional[Path] = None,
    genesis_path: Optional[Path] = None,
) -> Tuple[bool, List[str]]:
    """Verify entire chain from genesis. Returns (valid, errors)."""
    e_dir = entries_dir or ENTRIES_DIR
    g_path = genesis_path or GENESIS_PATH

    genesis = json.loads(g_path.read_text(encoding="utf-8"))
    valid, errors = verify_genesis(genesis)
    if not valid:
        return False, errors

    prev_hash = genesis["hash"]
    ids = sorted(p.stem for p in e_dir.glob("*.json") if p.stem != ".gitkeep") if e_dir.exists() else []

    for entry_id in ids:
        entry = json.loads((e_dir / f"{entry_id}.json").read_text(encoding="utf-8"))
        if entry.get("prev_hash") != prev_hash:
            errors.append(
                f"entry {entry_id}: prev_hash mismatch: expected {prev_hash}, got {entry.get('prev_hash')}"
            )
        expected_hash = entry_hash(entry)
        if entry.get("hash") != expected_hash:
            errors.append(
                f"entry {entry_id}: hash mismatch: expected {expected_hash}, got {entry.get('hash')}"
            )
        prev_hash = entry["hash"]

    return not errors, errors
