"""
Falsification test: Network packets cannot trigger memory corruption.
All packet parsing is bounds-checked.

# @falsification_id: F_GAMING_004
"""
import struct
import pytest

def parse_packet(data: bytes) -> dict:
    if len(data) < 4:
        raise ValueError("Packet too short")
    length = struct.unpack_from(">H", data, 0)[0]
    if 4 + length > len(data):
        raise ValueError(f"Packet body truncated: claimed {length}, got {len(data)-4}")
    body = data[4:4+length]
    return {"length": length, "body": body}

def test_oversized_packet_rejected():
    oversized = struct.pack(">HH", 9000, 0) + b"x" * 10
    with pytest.raises(ValueError):
        parse_packet(oversized)

def test_short_packet_rejected():
    with pytest.raises(ValueError):
        parse_packet(b"\x00")

def test_valid_packet_parsed():
    body = b"hello"
    pkt = struct.pack(">HH", len(body), 0) + body
    result = parse_packet(pkt)
    assert result["body"] == body
