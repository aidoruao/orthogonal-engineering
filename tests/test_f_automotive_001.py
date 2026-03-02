"""
Falsification test: OTA firmware update rejected if signature invalid.
ECU rejects unsigned firmware.

# @falsification_id: F-AUTOMOTIVE-001
"""
import hmac
import hashlib
import pytest

SIGNING_KEY = b"ecu_firmware_signing_key_v1"

def sign_firmware(firmware: bytes) -> bytes:
    return hmac.new(SIGNING_KEY, firmware, hashlib.sha256).digest()

def verify_and_apply(firmware: bytes, signature: bytes) -> str:
    expected = sign_firmware(firmware)
    if not hmac.compare_digest(expected, signature):
        return "REJECTED"
    return "APPLIED"

def test_bad_signature_rejected():
    firmware = b"firmware_v2.bin_content"
    bad_sig = b"\x00" * 32
    assert verify_and_apply(firmware, bad_sig) == "REJECTED"

def test_valid_signature_accepted():
    firmware = b"firmware_v2.bin_content"
    good_sig = sign_firmware(firmware)
    assert verify_and_apply(firmware, good_sig) == "APPLIED"
