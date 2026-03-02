"""
Falsification test: IFF system does not misclassify friendly as hostile.
Friendly IFF codes are never classified as hostile.

# @falsification_id: F_MILITARY_001
"""
import pytest

FRIENDLY_CODES = {f"IFF_{i:04d}" for i in range(100)}

def classify(code: str, friendly_codes: set) -> str:
    return "FRIENDLY" if code in friendly_codes else "HOSTILE"

def test_friendly_codes_never_hostile():
    for code in FRIENDLY_CODES:
        result = classify(code, FRIENDLY_CODES)
        assert result == "FRIENDLY", f"Code {code} misclassified as {result}"
