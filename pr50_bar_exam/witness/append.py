#!/usr/bin/env python3
"""
witness/append.py — Append entries to the witness chain.
"""
from __future__ import annotations
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from pr50_bar_exam.witness.chain import (
    ENTRIES_DIR,
    GENESIS_PATH,
    canonical_bytes,
    entry_hash,
    get_chain_head_hash,
)


def append_entry(
    event_type: str,
    payload: Dict[str, Any],
    entries_dir: Optional[Path] = None,
    genesis_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Append a new entry to the witness chain. Returns the new entry."""
    e_dir = entries_dir or ENTRIES_DIR
    g_path = genesis_path or GENESIS_PATH
    e_dir.mkdir(parents=True, exist_ok=True)

    prev_hash = get_chain_head_hash(e_dir, g_path)
    # Use zero-padded sequence number prefix so entries sort in insertion order.
    existing = sorted(p.stem for p in e_dir.glob("*.json") if p.stem != ".gitkeep") if e_dir.exists() else []
    seq = len(existing)
    entry_id = f"{seq:010d}_{uuid.uuid4()}"
    timestamp = datetime.now(timezone.utc).isoformat()

    entry: Dict[str, Any] = {
        "entry_id": entry_id,
        "event_type": event_type,
        "timestamp_utc": timestamp,
        "prev_hash": prev_hash,
        "payload": payload,
    }
    entry["hash"] = entry_hash(entry)

    out_path = e_dir / f"{entry_id}.json"
    out_path.write_text(
        json.dumps(entry, sort_keys=True, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    return entry
