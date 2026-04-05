"""
D_MEDICAL — Medical Systems domain implementation.
Safety-critical dosimetry with hard ceiling enforcement.

Invariants (from ontology/ontology.json#D_MEDICAL):
  1. Computed dose must never exceed the physician-prescribed ceiling.
  2. Dose calculations use integer arithmetic in micrograms to avoid float rounding errors.
  3. Any dose computation that would exceed the ceiling raises DoseExceedsCeilingError.

Biblical inspiration: "A little yeast works through the whole batch of dough." (Galatians 5:9)
A single unchecked floating-point rounding error in a dose calculation can cascade to lethal
outcomes. Integer micrograms are the leaven of correctness — exact, irreducible, non-negotiable.

Falsification IDs: F_MEDICAL_001, F_MEDICAL_002, F_MEDICAL_003
"""

from __future__ import annotations

from fractions import Fraction
from typing import NamedTuple


# ---------------------------------------------------------------------------
# Unit conversion constants (integer micrograms)
# ---------------------------------------------------------------------------

MCG_PER_MG = 1000          # 1 mg = 1 000 mcg
MCG_PER_G = 1_000_000      # 1 g  = 1 000 000 mcg

# Maximum safe weight-adjusted dose constant: used only in test fixtures.
# Real ceiling is always set by the prescribing physician.
ABSOLUTE_MAX_WEIGHT_MCG_PER_KG = 100_000  # 100 mg/kg — hard upper bound for all known drugs


class DoseExceedsCeilingError(Exception):
    """
    Raised whenever a computed dose would exceed the physician-prescribed ceiling.

    Invariant: No dose computation may silently return a value above the ceiling.
    Falsification: If any code path returns a dose above the ceiling without raising,
    F_MEDICAL_001 is violated.
    """


class DoseResult(NamedTuple):
    """Structured result of a dose calculation."""
    dose_mcg: int           # Actual computed dose in micrograms
    ceiling_mcg: int        # Physician-prescribed ceiling in micrograms
    weight_kg: Fraction     # Patient weight used in calculation
    drug_name: str          # Drug identifier
    within_ceiling: bool    # Always True — constructor enforces this


# ---------------------------------------------------------------------------
# Core dosimetry (F_MEDICAL_001)
# ---------------------------------------------------------------------------

def compute_dose_mcg(
    weight_kg: Fraction,
    dose_mcg_per_kg: Fraction,
    ceiling_mcg: int,
    drug_name: str = "unknown",
) -> DoseResult:
    """
    Compute weight-adjusted dose in integer micrograms.

    Invariant: Result dose_mcg <= ceiling_mcg, or DoseExceedsCeilingError is raised.
    Falsification: If dose_mcg > ceiling_mcg is returned without exception, F_MEDICAL_001 fails.

    Uses Fraction arithmetic to avoid any floating-point rounding error.
    The final integer is derived via floor division after exact rational computation.

    Args:
        weight_kg:       Patient weight as an exact Fraction (e.g., Fraction(70)).
        dose_mcg_per_kg: Dosing rate as an exact Fraction.
        ceiling_mcg:     Physician-prescribed hard ceiling in micrograms (integer).
        drug_name:       Drug identifier for error messages.

    Returns:
        DoseResult with dose_mcg <= ceiling_mcg.

    Raises:
        DoseExceedsCeilingError: If computed dose exceeds ceiling.
        ValueError: If weight_kg <= 0 or dose_mcg_per_kg < 0 or ceiling_mcg <= 0.
    """
    if weight_kg <= 0:
        raise ValueError(f"weight_kg must be positive, got {weight_kg}")
    if dose_mcg_per_kg < 0:
        raise ValueError(f"dose_mcg_per_kg must be non-negative, got {dose_mcg_per_kg}")
    if ceiling_mcg <= 0:
        raise ValueError(f"ceiling_mcg must be positive, got {ceiling_mcg}")

    # Exact rational arithmetic — no float rounding
    raw_dose_rational = weight_kg * dose_mcg_per_kg
    # Floor to integer micrograms (conservative — never round up)
    dose_mcg = int(raw_dose_rational)

    if dose_mcg > ceiling_mcg:
        raise DoseExceedsCeilingError(
            f"Computed dose {dose_mcg} mcg for {drug_name} exceeds ceiling "
            f"{ceiling_mcg} mcg — F_MEDICAL_001 ENFORCED"
        )

    return DoseResult(
        dose_mcg=dose_mcg,
        ceiling_mcg=ceiling_mcg,
        weight_kg=weight_kg,
        drug_name=drug_name,
        within_ceiling=True,
    )


def mg_to_mcg(mg: int) -> int:
    """Convert milligrams to micrograms (integer, exact)."""
    if not isinstance(mg, int):
        raise TypeError(f"mg must be int, got {type(mg).__name__}")
    if mg < 0:
        raise ValueError(f"mg must be non-negative, got {mg}")
    return mg * MCG_PER_MG


def mcg_to_mg_fraction(mcg: int) -> Fraction:
    """Convert micrograms to milligrams as an exact Fraction."""
    if not isinstance(mcg, int):
        raise TypeError(f"mcg must be int, got {type(mcg).__name__}")
    return Fraction(mcg, MCG_PER_MG)


# ---------------------------------------------------------------------------
# Infusion rate validation (F_MEDICAL_003)
# ---------------------------------------------------------------------------

INFUSION_TOLERANCE_NUMERATOR = 5
INFUSION_TOLERANCE_DENOMINATOR = 100   # 5%


def validate_infusion_rate(
    programmed_mcg_per_hr: int,
    actual_mcg_per_hr: Fraction,
) -> bool:
    """
    Verify that actual infusion rate is within ±5% of programmed rate.

    Invariant: |actual - programmed| / programmed <= 5/100.
    Falsification: If an out-of-tolerance rate is accepted, F_MEDICAL_003 is violated.

    Returns True if within tolerance.
    Raises ValueError if outside tolerance.
    """
    if programmed_mcg_per_hr <= 0:
        raise ValueError("programmed_mcg_per_hr must be positive")
    programmed = Fraction(programmed_mcg_per_hr)
    tolerance = programmed * Fraction(INFUSION_TOLERANCE_NUMERATOR, INFUSION_TOLERANCE_DENOMINATOR)
    deviation = abs(actual_mcg_per_hr - programmed)
    if deviation > tolerance:
        raise ValueError(
            f"Infusion rate {actual_mcg_per_hr} mcg/hr deviates {deviation} mcg/hr "
            f"from programmed {programmed_mcg_per_hr} mcg/hr — exceeds 5% tolerance"
        )
    return True


# ---------------------------------------------------------------------------
# Authentication for implantable device commands (F_MEDICAL_002)
# ---------------------------------------------------------------------------

import hashlib
import hmac as _hmac


def make_clinician_token(secret_key: bytes) -> bytes:
    """Derive the expected auth token from a clinician secret key."""
    if not isinstance(secret_key, (bytes, bytearray)):
        raise TypeError("secret_key must be bytes")
    if len(secret_key) < 16:
        raise ValueError("secret_key must be at least 16 bytes")
    return hashlib.sha256(secret_key).digest()


def authenticate_device_command(token: bytes, secret_key: bytes) -> bool:
    """
    Authenticate a device command token against the clinician secret key.

    Invariant: Only authenticated clinicians may issue device commands.
    Falsification: If an unauthenticated token is accepted, F_MEDICAL_002 is violated.

    Uses constant-time comparison to prevent timing oracle attacks.
    """
    if not isinstance(token, (bytes, bytearray)):
        raise TypeError("token must be bytes")
    expected = make_clinician_token(secret_key)
    return _hmac.compare_digest(token, expected)


def send_device_command(token: bytes, secret_key: bytes, command: str) -> str:
    """
    Send a command to an implantable device if the token is valid.

    Returns 'EXECUTED:<command>' on success, 'REJECTED' on auth failure.
    Raises ValueError on empty command string.
    """
    if not command:
        raise ValueError("command must not be empty")
    if authenticate_device_command(token, secret_key):
        return f"EXECUTED:{command}"
    return "REJECTED"


# ---------------------------------------------------------------------------
# Domain metadata
# ---------------------------------------------------------------------------

DOMAIN_METADATA = {
    "id": "D_MEDICAL",
    "name": "Medical Systems",
    "invariants": [
        "Computed dose must never exceed the physician-prescribed ceiling.",
        "Dose calculations use integer arithmetic in micrograms to avoid float rounding.",
        "Any dose computation that would exceed the ceiling raises DoseExceedsCeilingError.",
    ],
    "falsification_tests": ["F_MEDICAL_001", "F_MEDICAL_002", "F_MEDICAL_003"],
    "implementation_functions": [
        "compute_dose_mcg",
        "mg_to_mcg",
        "mcg_to_mg_fraction",
        "validate_infusion_rate",
        "authenticate_device_command",
        "send_device_command",
    ],
    "uses_integer_arithmetic": True,
    "uses_fraction_for_exact_math": True,
}
