"""D_VETERINARY Implementation — Animal facility, licensing, and treatment records.

All arithmetic uses Fraction. No floats.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple


@dataclass(frozen=True)
class AnimalFacility:
    """Regulated animal housing facility record (AWA 7 U.S.C. §2131, 9 CFR Part 3)."""

    facility_id: str
    license_number: str
    space_per_animal_sqft: Fraction
    min_space_sqft: Fraction
    veterinarian_on_call: bool
    last_inspection_days_ago: Fraction
    max_inspection_interval_days: Fraction


@dataclass(frozen=True)
class VeterinaryLicense:
    """Veterinary practitioner license record (Veterinary Practice Act, state licensing board)."""

    vet_id: str
    state: str
    license_active: bool
    days_until_expiry: Fraction
    dea_registration: bool
    ce_hours_completed: Fraction
    ce_hours_required: Fraction


@dataclass(frozen=True)
class AnimalTreatment:
    """Animal drug administration record (FDA CVM, 21 CFR, extra-label use AMDUCA)."""

    treatment_id: str
    animal_id: str
    drug_administered: str
    fda_cvm_approved: bool
    withdrawal_period_days: Fraction
    days_since_treatment: Fraction
    extra_label_use: bool
    veterinarian_supervised: bool


@dataclass(frozen=True)
class ZoonoticReport:
    """Zoonotic disease surveillance report (OIE Terrestrial Code, state regulations)."""

    report_id: str
    disease_name: str
    reportable: bool
    reported_within_hours: Fraction
    max_reporting_hours: Fraction
    species_affected: str


@dataclass(frozen=True)
class EuthanasiaRecord:
    """Euthanasia compliance record (AVMA Guidelines for the Euthanasia of Animals)."""

    record_id: str
    method: str
    avma_approved: bool
    veterinarian_present: bool
    pain_minimized: bool
