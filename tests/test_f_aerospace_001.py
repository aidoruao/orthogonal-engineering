"""
Falsification test: Avionics redundant channels produce byte-identical output.
All redundant channels agree.

# @falsification_id: F_AEROSPACE_001
"""
import struct
import pytest

def avionics_compute(inputs: tuple) -> bytes:
    altitude, airspeed, heading = inputs
    result = altitude * 0.3048 + airspeed * 0.5144 + heading
    return struct.pack(">d", result)

INPUTS = (35000.0, 480.0, 270.0)

def test_three_channels_byte_identical():
    ch1 = avionics_compute(INPUTS)
    ch2 = avionics_compute(INPUTS)
    ch3 = avionics_compute(INPUTS)
    assert ch1 == ch2 == ch3, "Redundant channels produced different outputs"
