#!/usr/bin/env python3
"""
ordination/verify_certificate.py — Verify certificate signatures and witness references.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pr50_bar_exam.ordination.signing_repo_key import make_verify_fn
from pr50_bar_exam.witness.chain import ENTRIES_DIR, GENESIS_PATH, entry_hash


def canonical_bytes(obj: Any) -> bytes:
    """Produce canonical JSON bytes."""
    # TODO: Expand canonical_bytes() - stub detected by Yeshua Agent
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def verify_certificate(
    cert: Dict[str, Any],
    secret_key: Optional[str] = None,
    entries_dir: Optional[Path] = None,
    genesis_path: Optional[Path] = None,
) -> Tuple[bool, List[str]]:
    """Verify certificate signature and witness reference. Returns (valid, errors)."""
    errors: List[str] = []
    e_dir = entries_dir or ENTRIES_DIR
    g_path = genesis_path or GENESIS_PATH

    # Verify signature
    signature = cert.get("signature", "")
    cert_without_sig = {k: v for k, v in cert.items() if k != "signature"}
    verify_fn = make_verify_fn(secret_key)
    if not verify_fn(canonical_bytes(cert_without_sig), signature):
        errors.append("signature verification failed")

    # Verify witness entry exists and references this certificate
    witness_id = cert.get("witness_entry_id", "")
    if witness_id:
        witness_path = e_dir / f"{witness_id}.json"
        if not witness_path.exists():
            errors.append(f"witness entry {witness_id!r} not found")
        else:
            witness_entry = json.loads(witness_path.read_text(encoding="utf-8"))
            expected_hash = entry_hash(witness_entry)
            if witness_entry.get("hash") != expected_hash:
                errors.append(f"witness entry {witness_id!r} hash mismatch")
    else:
        errors.append("certificate missing witness_entry_id")

    return not errors, errors
