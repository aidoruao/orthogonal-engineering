"""
Falsification test suite for D_MEDICAL domain.

Tests dosimetry ceiling enforcement, device authentication, and infusion rate validation.

# @falsification_id: F_MEDICAL_001, F_MEDICAL_002, F_MEDICAL_003
"""

import hashlib
import pytest
from fractions import Fraction

from src.domains.d_medical.implementation import (
    DoseExceedsCeilingError,
    DoseResult,
    MCG_PER_MG,
    authenticate_device_command,
    compute_dose_mcg,
    make_clinician_token,
    mcg_to_mg_fraction,
    mg_to_mcg,
    send_device_command,
    validate_infusion_rate,
)


# ---------------------------------------------------------------------------
# F_MEDICAL_001 — Dose ceiling enforcement
# ---------------------------------------------------------------------------

def test_dose_ceiling_exceeded_raises():
    """Dose above ceiling must raise DoseExceedsCeilingError."""
    with pytest.raises(DoseExceedsCeilingError):
        compute_dose_mcg(
            weight_kg=Fraction(80),
            dose_mcg_per_kg=Fraction(100),
            ceiling_mcg=500,  # 80 * 100 = 8000 > 500
            drug_name="test",
        )


def test_dose_at_ceiling_accepted():
    """Dose exactly at ceiling must be accepted."""
    # weight=10, rate=50 → 500 mcg = ceiling
    result = compute_dose_mcg(
        weight_kg=Fraction(10),
        dose_mcg_per_kg=Fraction(50),
        ceiling_mcg=500,
        drug_name="paracetamol",
    )
    assert result.dose_mcg == 500
    assert result.within_ceiling is True


def test_dose_below_ceiling_accepted():
    """Dose safely below ceiling must be accepted and within_ceiling is True."""
    result = compute_dose_mcg(
        weight_kg=Fraction(70),
        dose_mcg_per_kg=Fraction(5),
        ceiling_mcg=1000,  # 350 << 1000
        drug_name="morphine",
    )
    assert result.dose_mcg == 350
    assert result.within_ceiling is True
    assert result.drug_name == "morphine"
    assert result.ceiling_mcg == 1000


def test_dose_integer_arithmetic_no_float():
    """Dose calculation must use integer/Fraction arithmetic, not float."""
    import inspect
    source = inspect.getsource(compute_dose_mcg)
    assert "float(" not in source


def test_dose_negative_weight_raises():
    """Negative patient weight must raise ValueError."""
    with pytest.raises(ValueError):
        compute_dose_mcg(
            weight_kg=Fraction(-1),
            dose_mcg_per_kg=Fraction(10),
            ceiling_mcg=500,
        )


def test_dose_zero_ceiling_raises():
    """Zero ceiling must raise ValueError (not silently reject all doses)."""
    with pytest.raises(ValueError):
        compute_dose_mcg(
            weight_kg=Fraction(70),
            dose_mcg_per_kg=Fraction(5),
            ceiling_mcg=0,
        )


def test_dose_result_is_named_tuple():
    """DoseResult must be a NamedTuple with expected fields."""
    result = compute_dose_mcg(
        weight_kg=Fraction(50),
        dose_mcg_per_kg=Fraction(4),
        ceiling_mcg=300,
    )
    assert hasattr(result, "dose_mcg")
    assert hasattr(result, "ceiling_mcg")
    assert hasattr(result, "within_ceiling")


# ---------------------------------------------------------------------------
# Unit conversions
# ---------------------------------------------------------------------------

def test_mg_to_mcg_conversion():
    """1 mg = 1000 mcg, 500 mg = 500000 mcg."""
    assert mg_to_mcg(1) == MCG_PER_MG
    assert mg_to_mcg(0) == 0
    assert mg_to_mcg(500) == 500_000


def test_mcg_to_mg_exact():
    """1500 mcg = 3/2 mg (exact Fraction, no rounding)."""
    assert mcg_to_mg_fraction(1500) == Fraction(3, 2)
    assert mcg_to_mg_fraction(1000) == Fraction(1)


def test_mg_to_mcg_non_int_raises():
    """mg_to_mcg must reject non-integer input."""
    with pytest.raises(TypeError):
        mg_to_mcg(1.5)  # type: ignore


# ---------------------------------------------------------------------------
# F_MEDICAL_002 — Device command authentication
# ---------------------------------------------------------------------------

def test_unauthenticated_command_rejected():
    """Bad token must produce REJECTED."""
    secret = b"clinician_secret_key_xyz_pad_pad"
    bad_token = b"\x00" * 32
    result = send_device_command(bad_token, secret, "reprogram_therapy")
    assert result == "REJECTED"


def test_authenticated_command_accepted():
    """Correct token must produce EXECUTED:<command>."""
    secret = b"clinician_secret_key_xyz_pad_pad"
    good_token = make_clinician_token(secret)
    result = send_device_command(good_token, secret, "adjust_pacing")
    assert result.startswith("EXECUTED:")
    assert "adjust_pacing" in result


def test_empty_command_raises():
    """Empty command string must raise ValueError."""
    secret = b"clinician_secret_key_xyz_pad_pad"
    good_token = make_clinician_token(secret)
    with pytest.raises(ValueError):
        send_device_command(good_token, secret, "")


def test_token_constant_time_comparison():
    """authenticate_device_command must use constant-time comparison."""
    import inspect
    from src.domains.d_medical import implementation as impl_mod
    source = inspect.getsource(impl_mod)
    assert "compare_digest" in source


def test_short_secret_key_raises():
    """Secret keys shorter than 16 bytes must be rejected."""
    with pytest.raises(ValueError):
        make_clinician_token(b"short")


# ---------------------------------------------------------------------------
# F_MEDICAL_003 — Infusion rate tolerance
# ---------------------------------------------------------------------------

def test_infusion_within_tolerance_accepted():
    """2% deviation from programmed rate must be accepted (within 5% tolerance)."""
    result = validate_infusion_rate(1000, Fraction(1020))
    assert result is True


def test_infusion_at_tolerance_boundary_accepted():
    """Exactly 5% above programmed rate must be accepted."""
    result = validate_infusion_rate(1000, Fraction(1050))
    assert result is True


def test_infusion_above_tolerance_rejected():
    """10% deviation must raise ValueError."""
    with pytest.raises(ValueError):
        validate_infusion_rate(1000, Fraction(1100))


def test_infusion_below_tolerance_rejected():
    """12% below programmed rate must raise ValueError."""
    with pytest.raises(ValueError):
        validate_infusion_rate(1000, Fraction(880))


def test_infusion_zero_programmed_raises():
    """Zero programmed rate must raise ValueError."""
    with pytest.raises(ValueError):
        validate_infusion_rate(0, Fraction(100))
