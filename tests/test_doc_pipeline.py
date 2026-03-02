"""
Falsification test: Document processing pipeline is idempotent.
Processing same document twice gives same output.

# @falsification_id: F_WHITECOLLAR_001
"""
import hashlib
import pytest

def process_document(doc: str) -> str:
    """Simulate document normalization pipeline."""
    import re
    return re.sub(r' +', ' ', doc.strip().lower())

def test_pipeline_idempotent():
    doc = "  Hello   World  "
    out1 = process_document(doc)
    out2 = process_document(out1)
    assert out1 == out2, "Document pipeline is not idempotent"

def test_pipeline_hash_stable():
    doc = "Invoice #1234 for services rendered"
    h1 = hashlib.sha256(process_document(doc).encode()).hexdigest()
    h2 = hashlib.sha256(process_document(doc).encode()).hexdigest()
    assert h1 == h2
