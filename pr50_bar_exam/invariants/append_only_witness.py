#!/usr/bin/env python3
"""
invariants/append_only_witness.py — Checks witness chain integrity.
"""
from __future__ import annotations
from pathlib import Path
from typing import List, Optional, Tuple

from pr50_bar_exam.witness.verify import verify_chain


def assert_chain_integrity(
    entries_dir: Optional[Path] = None,
    genesis_path: Optional[Path] = None,
) -> Tuple[bool, List[str]]:
    """Assert witness chain is intact and append-only.

    Returns (valid, errors).
    """
    return verify_chain(entries_dir, genesis_path)
