"""Fixture for infrastructure signature scanner tests."""

from __future__ import annotations

import hashlib
from pathlib import Path


def commit_consent(candidate_id: str) -> None:
    append_consent(candidate_id, "test")


def append_consent(candidate_id: str, action: str) -> None:
    pass


def verify_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_gate(capability: str) -> bool:
    return has_capability(capability)


def has_capability(capability: str) -> bool:
    return True


def record_witness(state: str) -> None:
    generate_feed_entry(state)


def generate_feed_entry(state: str) -> None:
    pass
