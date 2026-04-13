"""D_ZONING invariants — Yeshua Standard. 0 floats.

Standards:
- Village of Euclid v. Ambler Realty Co., 272 U.S. 365 (1926) — zoning authority
- Fair Housing Act §3604 — exclusionary zoning prohibition
- APA Standard Planning Act — comprehensive plan consistency
- 42 U.S.C. §3604(f) — disability accommodation in zoning
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from datetime import datetime
from axioms.logic import ProofObject
from .implementation import Parcel, VarianceApplication, ZoneType, VarianceType


def check_parcel_area_positive(parcel: Parcel) -> Tuple[bool, ProofObject]:
    """Parcel area must be > 0 sq ft.

    Standard: APA — minimum lot size requirements
    falsifies_if: parcel.area_sqft <= 0.
    """
    ok = parcel.area_sqft > Fraction(0)
    premises = [
        f"parcel_id={parcel.parcel_id}",
        f"area_sqft={parcel.area_sqft}",
    ]
    return ok, ProofObject(
        rule="ParcelAreaPositive",
        premises=premises,
        conclusion=f"PASS: area {parcel.area_sqft} sqft" if ok else "VIOLATION: non-positive parcel area",
    )


def check_parcel_address_nonempty(parcel: Parcel) -> Tuple[bool, ProofObject]:
    """Parcel must have a non-empty address.

    Standard: Local government zoning ordinance — address assignment required
    falsifies_if: parcel.address is empty.
    """
    ok = bool(parcel.address.strip())
    premises = [f"parcel_id={parcel.parcel_id}", f"address={parcel.address!r}"]
    return ok, ProofObject(
        rule="ParcelAddressNonEmpty",
        premises=premises,
        conclusion="PASS: address set" if ok else "VIOLATION: parcel address empty",
    )


def check_floor_area_ratio_nonneg(parcel: Parcel) -> Tuple[bool, ProofObject]:
    """Floor area ratio must be >= 0.

    Standard: IBC (International Building Code) — FAR definition
    falsifies_if: parcel.floor_area_ratio < 0.
    """
    ok = parcel.floor_area_ratio >= Fraction(0)
    premises = [
        f"parcel_id={parcel.parcel_id}",
        f"floor_area_ratio={parcel.floor_area_ratio}",
    ]
    return ok, ProofObject(
        rule="FloorAreaRatioNonNeg",
        premises=premises,
        conclusion=f"PASS: FAR {parcel.floor_area_ratio}" if ok else "VIOLATION: negative FAR",
    )


def check_variance_has_applicant(app: VarianceApplication) -> Tuple[bool, ProofObject]:
    """Variance application must identify the applicant.

    Standard: APA zoning procedures — standing to apply for variance
    falsifies_if: app.applicant is empty.
    """
    ok = bool(app.applicant.strip())
    premises = [
        f"application_id={app.application_id}",
        f"applicant={app.applicant!r}",
    ]
    return ok, ProofObject(
        rule="VarianceHasApplicant",
        premises=premises,
        conclusion="PASS: applicant identified" if ok else "VIOLATION: applicant empty",
    )


def check_zone_type_valid(parcel: Parcel) -> Tuple[bool, ProofObject]:
    """Parcel zone_type must be a valid ZoneType enum value.

    Standard: Local zoning ordinance — zone district classification
    falsifies_if: parcel.zone_type is not a ZoneType instance.
    """
    ok = isinstance(parcel.zone_type, ZoneType)
    premises = [
        f"parcel_id={parcel.parcel_id}",
        f"zone_type={parcel.zone_type!r}",
    ]
    return ok, ProofObject(
        rule="ZoneTypeValid",
        premises=premises,
        conclusion=f"PASS: zone type {parcel.zone_type.name}" if ok else "VIOLATION: invalid zone type",
    )


def check_variance_type_valid(app: VarianceApplication) -> Tuple[bool, ProofObject]:
    """Variance type must be a valid VarianceType enum.

    Standard: APA — area vs. use variance distinction
    falsifies_if: app.variance_type is not a VarianceType instance.
    """
    ok = isinstance(app.variance_type, VarianceType)
    premises = [
        f"application_id={app.application_id}",
        f"variance_type={app.variance_type!r}",
    ]
    return ok, ProofObject(
        rule="VarianceTypeValid",
        premises=premises,
        conclusion=f"PASS: variance type {app.variance_type.name}" if ok else "VIOLATION: invalid variance type",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS

    Falsifies if: any check returns FAIL (nominal inputs should always pass).."""
    parcel = Parcel(
        parcel_id="PARCEL-001",
        address="456 Oak Ave, Springfield, IL",
        area_sqft=Fraction(10000),
        zone_type=ZoneType.RESIDENTIAL,
        floor_area_ratio=Fraction(5, 10),
    )
    app = VarianceApplication(
        application_id="VAR-001",
        parcel_id="PARCEL-001",
        variance_type=list(VarianceType)[0],
        applicant="Bob Builder",
        application_date=datetime(2024, 1, 1),
    )
    results = {}
    for fn, args in [
        (check_parcel_area_positive, (parcel,)),
        (check_parcel_address_nonempty, (parcel,)),
        (check_floor_area_ratio_nonneg, (parcel,)),
        (check_variance_has_applicant, (app,)),
        (check_zone_type_valid, (parcel,)),
        (check_variance_type_valid, (app,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
