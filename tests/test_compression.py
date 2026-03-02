"""
Falsification test: Compression round-trip is lossless.
compress(data) then decompress gives original data.

# @falsification_id: F-NONCREATIVE-001
"""
import zlib
import pytest

TEST_DATA = [
    b"Hello, World!" * 100,
    b"\x00\xff\xab" * 50,
    b"",
    bytes(range(256)) * 10,
]

def test_compression_roundtrip():
    for data in TEST_DATA:
        compressed = zlib.compress(data)
        decompressed = zlib.decompress(compressed)
        assert decompressed == data, f"Round-trip failed for {len(data)}-byte input"
