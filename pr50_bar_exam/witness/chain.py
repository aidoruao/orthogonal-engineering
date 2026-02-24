#!/usr/bin/env python3
"""
witness/chain.py — Append-only hash chain implementation.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


GENESIS_PATH = Path(__file__).parent / "log" / "genesis.json"
ENTRIES_DIR = Path(__file__).parent / "log" / "entries"


def canonical_bytes(obj: Any) -> bytes:
    """Produce canonical JSON bytes."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def entry_hash(entry: Dict[str, Any]) -> str:
    """Compute SHA-256 hash of a chain entry (excluding 'hash' field)."""
    filtered = {k: v for k, v in entry.items() if k != "hash"}
    return hashlib.sha256(canonical_bytes(filtered)).hexdigest()


def load_genesis() -> Dict[str, Any]:
    """Load genesis block."""
    return json.loads(GENESIS_PATH.read_text(encoding="utf-8"))


def load_entry(entry_id: str) -> Dict[str, Any]:
    """Load a chain entry by ID."""
    p = ENTRIES_DIR / f"{entry_id}.json"
    return json.loads(p.read_text(encoding="utf-8"))


def list_entry_ids() -> List[str]:
    """List all entry IDs in order."""
    if not ENTRIES_DIR.exists():
        return []
    return sorted(p.stem for p in ENTRIES_DIR.glob("*.json") if p.stem != ".gitkeep")


def get_chain_head_hash(entries_dir: Optional[Path] = None, genesis_path: Optional[Path] = None) -> str:
    """Return the hash of the latest chain entry, or genesis hash if no entries."""
    g_path = genesis_path or GENESIS_PATH
    e_dir = entries_dir or ENTRIES_DIR
    genesis = json.loads(g_path.read_text(encoding="utf-8"))
    ids = sorted(p.stem for p in e_dir.glob("*.json") if p.stem != ".gitkeep") if e_dir.exists() else []
    if not ids:
        return genesis["hash"]
    last = json.loads((e_dir / f"{ids[-1]}.json").read_text(encoding="utf-8"))
    return last["hash"]
