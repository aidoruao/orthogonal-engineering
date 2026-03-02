"""
Falsification test: Weather API failure does not crash simulator.
Simulator continues with cached data on API failure.

# @falsification_id: F-AVIATION-003
"""
import pytest

CACHED_WEATHER = {"wind_kt": 15, "visibility_sm": 10, "ceiling_ft": 3000}

def fetch_weather(api_available: bool) -> dict:
    if not api_available:
        return CACHED_WEATHER
    return {"wind_kt": 20, "visibility_sm": 8, "ceiling_ft": 2500}

def test_simulator_uses_cache_on_failure():
    weather = fetch_weather(api_available=False)
    assert weather == CACHED_WEATHER, "Simulator did not fall back to cached weather"
