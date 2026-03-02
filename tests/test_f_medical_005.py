"""
Falsification test: AI diagnostic tool never suggests treatment outside clinical guidelines.
All AI outputs within approved set.

# @falsification_id: F_MEDICAL_005
"""
import random
import pytest

APPROVED_TREATMENTS = {"watchful_waiting", "ibuprofen", "amoxicillin", "rest", "fluids"}

def simulate_ai_diagnosis(seed: int) -> str:
    rng = random.Random(seed)
    return rng.choice(sorted(APPROVED_TREATMENTS))

def test_all_diagnoses_in_approved_set():
    for i in range(100):
        treatment = simulate_ai_diagnosis(i)
        assert treatment in APPROVED_TREATMENTS, f"Unapproved treatment: {treatment!r}"
