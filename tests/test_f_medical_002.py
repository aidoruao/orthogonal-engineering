"""
Falsification test: Implantable device rejects unauthorized commands.
Only authenticated clinician can reprogram.

# @falsification_id: F_MEDICAL_002
"""
import hashlib
import pytest

SECRET_KEY = b"clinician_secret_key_xyz"

def authenticate(token: bytes) -> bool:
    expected = hashlib.sha256(SECRET_KEY).digest()
    return token == expected

def send_command(token: bytes, cmd: str) -> str:
    if not authenticate(token):
        return "REJECTED"
    return f"EXECUTED:{cmd}"

def test_unauthenticated_command_rejected():
    bad_token = b"\x00" * 32
    result = send_command(bad_token, "reprogram_therapy")
    assert result == "REJECTED"

def test_authenticated_command_accepted():
    good_token = hashlib.sha256(SECRET_KEY).digest()
    result = send_command(good_token, "reprogram_therapy")
    assert result.startswith("EXECUTED:")
