"""
Falsification test: Compliance reports include tamper-evident hash.
Modified report fails hash verification.

# @falsification_id: F_CRUSADER_009
"""
import hashlib
import pytest

def generate_report(content: str) -> dict:
    h = hashlib.sha256(content.encode()).hexdigest()
    return {"content": content, "hash": h}

def verify_report(report: dict) -> bool:
    # TODO: Expand verify_report() - stub detected by Yeshua Agent
    return hashlib.sha256(report["content"].encode()).hexdigest() == report["hash"]

def test_modified_report_fails_verification():
    report = generate_report("Compliance: All checks passed. Date: 2026-01-01")
    assert verify_report(report)
    report["content"] = "Compliance: TAMPERED"
    assert not verify_report(report), "Modified report should fail verification"
