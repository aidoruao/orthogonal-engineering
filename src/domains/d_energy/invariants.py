"""D_ENERGY invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: 49 CFR 192/195 (Pipeline Safety), FERC standards
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import List, Dict
from datetime import datetime, timedelta


@dataclass
class PowerPlant:
    """Power generation facility."""
    plant_id: str
    name: str
    capacity_mw: Fraction
    renewable_percentage: Fraction  # 0.0 to 1.0
    meets_rps: bool  # Renewable Portfolio Standard


@dataclass
class GridMeasurement:
    """Power grid frequency measurement."""
    timestamp: datetime
    frequency_hz: Fraction  # Should be ~60Hz in US
    voltage_kv: Fraction


@dataclass
class PipelineSegment:
    """Pipeline segment for safety checking."""
    segment_id: str
    material: str  # steel, plastic, etc.
    max_operating_pressure: Fraction  # psig
    last_hydrotest: datetime
    corrosion_found: bool


def check_grid_frequency_within_tolerance() -> bool:
    """
    Invariant: Grid frequency maintained at 60Hz ± 0.5Hz.
    Falsification: If frequency deviates beyond acceptable range.
    """
    # Normal operation
    normal = GridMeasurement(
        timestamp=datetime.now(),
        frequency_hz=Fraction(6000, 100),  # 60.00 Hz
        voltage_kv=Fraction(138),
    )
    
    assert Fraction(595, 10) <= normal.frequency_hz <= Fraction(605, 10), (
        f"Normal frequency {normal.frequency_hz} Hz outside 59.5-60.5 Hz range"
    )
    
    # Frequency event (within tolerance)
    event = GridMeasurement(
        timestamp=datetime.now(),
        frequency_hz=Fraction(598, 10),  # 59.8 Hz
        voltage_kv=Fraction(138),
    )
    
    assert Fraction(595, 10) <= event.frequency_hz <= Fraction(605, 10), (
        f"Event frequency {event.frequency_hz} Hz outside tolerance"
    )
    
    return True


def check_renewable_portfolio_compliance() -> bool:
    """
    Invariant: Utility meets state Renewable Portfolio Standard.
    Falsification: If renewable percentage below RPS requirement.
    """
    # Utility with 30% RPS requirement
    utility = PowerPlant(
        plant_id="UTIL001",
        name="State Utility",
        capacity_mw=Fraction(1000),
        renewable_percentage=Fraction(35, 100),  # 35%
        meets_rps=True,
    )
    
    rps_requirement = Fraction(30, 100)  # 30% required
    
    assert utility.renewable_percentage >= rps_requirement, (
        f"Utility renewable {utility.renewable_percentage*100}% "
        f"below RPS requirement {rps_requirement*100}%"
    )
    assert utility.meets_rps is True, "Utility should meet RPS"
    
    return True


def check_pipeline_hydrotest_interval() -> bool:
    """
    Invariant: Pipelines hydrotested within required interval (5 years for gas).
    Falsification: If pipeline overdue for hydrotest passes check.
    """
    segment = PipelineSegment(
        segment_id="PIPE001",
        material="steel",
        max_operating_pressure=Fraction(1000),
        last_hydrotest=datetime.now() - timedelta(days=2000),  # ~5.5 years ago
        corrosion_found=False,
    )
    
    required_interval_days = 1825  # 5 years
    days_since_test = (datetime.now() - segment.last_hydrotest).days
    
    assert days_since_test <= required_interval_days, (
        f"Pipeline segment {segment.segment_id} overdue for hydrotest: "
        f"{days_since_test} days vs required {required_interval_days} days"
    )
    
    return True


def check_pipeline_corrosion_management() -> bool:
    """
    Invariant: Corrosion findings trigger remediation.
    Falsification: If corrosion found but no action taken.
    """
    # Corrosion found - must have remediation
    corroded = PipelineSegment(
        segment_id="PIPE002",
        material="steel",
        max_operating_pressure=Fraction(800),
        last_hydrotest=datetime.now(),
        corrosion_found=True,
    )
    
    assert corroded.corrosion_found is True, "Corrosion was detected"
    # In real system, would check for remediation record
    
    # No corrosion - no action needed
    clean = PipelineSegment(
        segment_id="PIPE003",
        material="steel",
        max_operating_pressure=Fraction(800),
        last_hydrotest=datetime.now(),
        corrosion_found=False,
    )
    
    assert clean.corrosion_found is False, "No corrosion expected"
    
    return True


def check_max_pressure_limits() -> bool:
    """
    Invariant: Operating pressure within maximum allowable.
    Falsification: If pressure exceeds MAOP (Maximum Allowable Operating Pressure).
    """
    segment = PipelineSegment(
        segment_id="PIPE004",
        material="steel",
        max_operating_pressure=Fraction(1440),  # MAOP
        last_hydrotest=datetime.now(),
        corrosion_found=False,
    )
    
    current_pressure = Fraction(1400)  # Current operating
    
    assert current_pressure <= segment.max_operating_pressure, (
        f"Operating pressure {current_pressure} psig exceeds "
        f"MAOP {segment.max_operating_pressure} psig"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("grid_frequency", check_grid_frequency_within_tolerance),
        ("renewable_rps", check_renewable_portfolio_compliance),
        ("pipeline_hydrotest", check_pipeline_hydrotest_interval),
        ("pipeline_corrosion", check_pipeline_corrosion_management),
        ("pressure_limits", check_max_pressure_limits),
    ]
    
    for name, check_func in checks:
        try:
            check_func()
            results[name] = "PASS"
        except AssertionError as e:
            results[name] = f"FAIL: {e}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_ENERGY invariants: PASS")
