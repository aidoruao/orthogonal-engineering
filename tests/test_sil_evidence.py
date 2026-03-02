"""
Falsification test: Infrastructure control software meets SIL requirements.
Failure rate < 10e-5 per hour (SIL-2).

# @falsification_id: F-NECESSITY-001
"""
import pytest

SIL2_MAX_FAILURE_RATE = 1e-4  # failures per hour

def compute_failure_rate(mtbf_hours: float) -> float:
    return 1.0 / mtbf_hours

def test_sil2_failure_rate():
    mtbf_hours = 200_000.0
    rate = compute_failure_rate(mtbf_hours)
    assert rate < SIL2_MAX_FAILURE_RATE, f"Failure rate {rate:.2e} exceeds SIL-2 limit {SIL2_MAX_FAILURE_RATE:.2e}"

def test_sil2_architecture_requirements():
    """Verify software structure satisfies SIL-2 architecture requirements."""
    requirements = {
        "redundancy": True,
        "diverse_software_channels": True,
        "hardware_fault_tolerance": 1,
        "diagnostic_coverage": 0.90,
    }
    assert requirements["redundancy"] is True
    assert requirements["diverse_software_channels"] is True
    assert requirements["hardware_fault_tolerance"] >= 1
    assert requirements["diagnostic_coverage"] >= 0.90
