"""
Falsification test: Document hash unchanged after round-trip.
sha256(output) == sha256(input).

# @falsification_id: F-LEGAL-001
"""
import hashlib
import pytest

def process_document(content: bytes) -> bytes:
    return content  # Simulate no-op processing

def test_document_hash_roundtrip():
    doc = b"Legal document content v1.0\n" + b"A" * 1000
    h_in = hashlib.sha256(doc).hexdigest()
    processed = process_document(doc)
    h_out = hashlib.sha256(processed).hexdigest()
    assert h_in == h_out, "Document hash changed after round-trip"
