"""
D_EDUCATION — credential integrity implementation.

Invariants:
  1. Credential hash is immutable after issuance.
  2. Credential verification is deterministic.
  3. Verification requires matching subject and payload.
  4. Reissuance is append-only and preserves audit chain.

Biblical inspiration: Proverbs 22:6 — trust in formation requires integrity.
"""

from __future__ import annotations

import copy
import hashlib
import json
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class Credential:
    student_id: str
    payload: dict
    issued_hash: str
    issued_at_ns: int


@dataclass(frozen=True)
class CredentialRevision:
    prior_hash: str
    next_hash: str
    reason: str
    revised_at_ns: int


def _canonical_payload(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _compute_hash(student_id: str, payload: dict) -> str:
    canonical = _canonical_payload(payload)
    return hashlib.sha256(f"{student_id}:{canonical}".encode("utf-8")).hexdigest()


def issue_credential(student_id: str, payload: dict) -> Credential:
    if not student_id:
        raise ValueError("student_id must not be empty")
    digest = _compute_hash(student_id, payload)
    return Credential(
        student_id=student_id,
        payload=copy.deepcopy(payload),
        issued_hash=digest,
        issued_at_ns=time.monotonic_ns(),
    )


def verify_credential(credential: Credential) -> bool:
    digest = _compute_hash(credential.student_id, credential.payload)
    return digest == credential.issued_hash


def issue_revised_credential(
    previous: Credential,
    new_payload: dict,
    reason: str,
) -> tuple[Credential, CredentialRevision]:
    if not reason.strip():
        raise ValueError("reason must not be empty")
    revised = issue_credential(previous.student_id, new_payload)
    revision = CredentialRevision(
        prior_hash=previous.issued_hash,
        next_hash=revised.issued_hash,
        reason=reason,
        revised_at_ns=time.monotonic_ns(),
    )
    return revised, revision


def verify_revision_chain(
    original: Credential,
    revised: Credential,
    revision: CredentialRevision,
) -> bool:
    if revision.prior_hash != original.issued_hash:
        return False
    if revision.next_hash != revised.issued_hash:
        return False
    return verify_credential(original) and verify_credential(revised)


def deterministic_credential_fingerprint(credential: Credential) -> str:
    payload = {
        "student_id": credential.student_id,
        "issued_hash": credential.issued_hash,
        "issued_at_ns": credential.issued_at_ns,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


DOMAIN_METADATA = {
    "id": "D_EDUCATION",
    "name": "Education",
    "invariants": [
        "Credential hash is immutable after issuance.",
        "Credential verification is deterministic.",
        "Verification requires matching subject and payload.",
        "Credential revisions are append-only and auditable.",
    ],
    "falsification_tests": ["F_EDUCATION_001"],
    "implementation_functions": [
        "Credential",
        "CredentialRevision",
        "issue_credential",
        "verify_credential",
        "issue_revised_credential",
        "verify_revision_chain",
        "deterministic_credential_fingerprint",
    ],
}
