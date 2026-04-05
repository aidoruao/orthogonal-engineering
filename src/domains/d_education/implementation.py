"""
D_EDUCATION — credential integrity implementation.

Invariants:
  1. Credential hash is immutable after issuance.
  2. Credential verification is deterministic.
  3. Verification requires matching subject and payload.

Biblical inspiration: Proverbs 22:6 — trust in formation requires integrity.
"""

from __future__ import annotations

import hashlib
import json
import copy
from dataclasses import dataclass


@dataclass(frozen=True)
class Credential:
    student_id: str
    payload: dict
    issued_hash: str


def _canonical_payload(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def issue_credential(student_id: str, payload: dict) -> Credential:
    if not student_id:
        raise ValueError("student_id must not be empty")
    canonical = _canonical_payload(payload)
    digest = hashlib.sha256(f"{student_id}:{canonical}".encode("utf-8")).hexdigest()
    return Credential(student_id=student_id, payload=copy.deepcopy(payload), issued_hash=digest)


def verify_credential(credential: Credential) -> bool:
    canonical = _canonical_payload(credential.payload)
    digest = hashlib.sha256(
        f"{credential.student_id}:{canonical}".encode("utf-8")
    ).hexdigest()
    return digest == credential.issued_hash


DOMAIN_METADATA = {
    "id": "D_EDUCATION",
    "name": "Education",
    "invariants": [
        "Credential hash is immutable after issuance.",
        "Credential verification is deterministic.",
        "Verification requires matching subject and payload.",
    ],
    "falsification_tests": ["F_EDUCATION_001"],
    "implementation_functions": ["Credential", "issue_credential", "verify_credential"],
}
