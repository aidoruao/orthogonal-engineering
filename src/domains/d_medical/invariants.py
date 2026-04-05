"""
D_MEDICAL invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: ontology/ontology.json#D_MEDICAL
"""

from fractions import Fraction

from src.domains.d_medical.implementation import (
    DoseExceedsCeilingError,
    compute_dose_mcg,
    mg_to_mcg,
    mcg_to_mg_fraction,
    validate_infusion_rate,
    authenticate_device_command,
    send_device_command,
    make_clinician_token,
    MCG_PER_MG,
)


def check_dose_ceiling_enforced() -> bool:
    """
    Invariant: Computed dose must never exceed the physician-prescribed ceiling.
    Falsification: If compute_dose_mcg returns a value above ceiling_mcg without raising,
    F_MEDICAL_001 is violated.
    """
    raised = False
    try:
        compute_dose_mcg(
            weight_kg=Fraction(70),
            dose_mcg_per_kg=Fraction(200),
            ceiling_mcg=1000,  # 70 * 200 = 14 000 >> 1000
            drug_name="test_drug",
        )
    except DoseExceedsCeilingError:
        raised = True
    assert raised, (
        "compute_dose_mcg must raise DoseExceedsCeilingError when dose exceeds ceiling — "
        "F_MEDICAL_001 VIOLATED"
    )
    return True


def check_dose_within_ceiling_accepted() -> bool:
    """
    Invariant: Doses at or below the ceiling must be accepted and returned correctly.
    Falsification: If a safe dose raises an exception, the implementation is over-restrictive.
    """
    result = compute_dose_mcg(
        weight_kg=Fraction(70),
        dose_mcg_per_kg=Fraction(5),
        ceiling_mcg=500,   # 70 * 5 = 350 <= 500
        drug_name="morphine",
    )
    assert result.dose_mcg == 350, f"Expected 350 mcg, got {result.dose_mcg}"
    assert result.within_ceiling is True
    assert result.drug_name == "morphine"
    return True


def check_integer_arithmetic_no_float() -> bool:
    """
    Invariant: Dose calculations use integer arithmetic / Fraction, not float.
    Falsification: If implementation uses float arithmetic, rounding errors may occur.
    """
    import inspect
    source = inspect.getsource(compute_dose_mcg)
    assert "float(" not in source, (
        "compute_dose_mcg must not use float() — integer/Fraction arithmetic required"
    )
    return True


def check_mg_mcg_conversion_exact() -> bool:
    """
    Invariant: mg → mcg conversion is exact (integer, no rounding).
    Falsification: If mg_to_mcg(1) != 1000, the conversion is incorrect.
    """
    assert mg_to_mcg(1) == MCG_PER_MG, f"mg_to_mcg(1) must equal {MCG_PER_MG}"
    assert mg_to_mcg(0) == 0
    assert mg_to_mcg(500) == 500_000
    assert mcg_to_mg_fraction(1500) == Fraction(3, 2)
    return True


def check_infusion_tolerance_enforced() -> bool:
    """
    Invariant: Infusion rates outside ±5% are rejected.
    Falsification: If a 10%-off rate is accepted, F_MEDICAL_003 is violated.
    """
    raised = False
    try:
        validate_infusion_rate(
            programmed_mcg_per_hr=1000,
            actual_mcg_per_hr=Fraction(1200),  # 20% above — out of tolerance
        )
    except ValueError:
        raised = True
    assert raised, (
        "validate_infusion_rate must reject rates >5% off programmed rate — "
        "F_MEDICAL_003 VIOLATED"
    )
    return True


def check_infusion_within_tolerance_accepted() -> bool:
    """
    Invariant: Infusion rates within ±5% are accepted.
    Falsification: If a 2%-off rate raises ValueError, the implementation is too strict.
    """
    result = validate_infusion_rate(
        programmed_mcg_per_hr=1000,
        actual_mcg_per_hr=Fraction(1020),  # 2% above — within tolerance
    )
    assert result is True
    return True


def check_unauthenticated_command_rejected() -> bool:
    """
    Invariant: Only authenticated clinicians may issue device commands.
    Falsification: If an unauthenticated token is accepted, F_MEDICAL_002 is violated.
    """
    secret = b"clinician_secret_key_xyz_pad_pad"
    bad_token = b"\x00" * 32
    result = send_device_command(bad_token, secret, "reprogram_therapy")
    assert result == "REJECTED", (
        f"send_device_command accepted bad token — F_MEDICAL_002 VIOLATED, got: {result}"
    )
    return True


def check_authenticated_command_accepted() -> bool:
    """
    Invariant: A correctly authenticated command must be executed.
    Falsification: If a valid token is rejected, patients cannot receive care.
    """
    secret = b"clinician_secret_key_xyz_pad_pad"
    good_token = make_clinician_token(secret)
    result = send_device_command(good_token, secret, "adjust_pacing")
    assert result.startswith("EXECUTED:"), (
        f"send_device_command rejected valid token — got: {result}"
    )
    return True


def run_all_invariants() -> dict:
    """Run all D_MEDICAL invariants. Returns dict of check_name → pass/fail."""
    checks = [
        check_dose_ceiling_enforced,
        check_dose_within_ceiling_accepted,
        check_integer_arithmetic_no_float,
        check_mg_mcg_conversion_exact,
        check_infusion_tolerance_enforced,
        check_infusion_within_tolerance_accepted,
        check_unauthenticated_command_rejected,
        check_authenticated_command_accepted,
    ]
    results = {}
    for check in checks:
        try:
            check()
            results[check.__name__] = "PASS"
        except AssertionError as e:
            results[check.__name__] = f"FAIL: {e}"
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if v != "PASS"]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_MEDICAL invariants: PASS")
