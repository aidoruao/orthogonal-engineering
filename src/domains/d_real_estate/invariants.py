"""D_REAL_ESTATE invariants — Yeshua Standard. 0 floats.

Standards:
- Fair Housing Act (42 U.S.C. §3601) — anti-discrimination
- RESPA (12 U.S.C. §2601) — settlement procedures
- ECOA (15 U.S.C. §1691) — equal credit opportunity
- TILA (15 U.S.C. §1638) — truth in lending disclosure
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import Property, PropertyAssessment, LoanApplication, PropertyType


def check_property_lot_size_positive(property: Property) -> Tuple[bool, ProofObject]:
    """Property lot size must be > 0 sq ft.

    Standard: USPAP Standard 1 — appraisal development
    falsifies_if: property.lot_size_sqft <= 0.
    """
    ok = property.lot_size_sqft > Fraction(0)
    premises = [
        f"property_id={property.property_id}",
        f"lot_size_sqft={property.lot_size_sqft}",
    ]
    return ok, ProofObject(
        rule="PropertyLotSizePositive",
        premises=premises,
        conclusion=f"PASS: lot size {property.lot_size_sqft} sqft" if ok else "VIOLATION: non-positive lot size",
    )


def check_property_address_nonempty(property: Property) -> Tuple[bool, ProofObject]:
    """Property must have a non-empty address.

    Standard: RESPA §4 — settlement disclosures require property address
    falsifies_if: property.address is empty.
    """
    ok = bool(property.address.strip())
    premises = [f"property_id={property.property_id}", f"address={property.address!r}"]
    return ok, ProofObject(
        rule="PropertyAddressNonEmpty",
        premises=premises,
        conclusion="PASS: address set" if ok else "VIOLATION: address empty",
    )


def check_loan_amount_positive(app: LoanApplication) -> Tuple[bool, ProofObject]:
    """Loan amount must be > 0.

    Standard: TILA 12 CFR Part 1026 — credit amount disclosure
    falsifies_if: app.loan_amount <= 0.
    """
    ok = app.loan_amount > Fraction(0)
    premises = [
        f"application_id={app.application_id}",
        f"loan_amount={app.loan_amount}",
    ]
    return ok, ProofObject(
        rule="LoanAmountPositive",
        premises=premises,
        conclusion=f"PASS: loan amount {app.loan_amount}" if ok else "VIOLATION: non-positive loan amount",
    )


def check_debt_to_income_ratio_range(app: LoanApplication) -> Tuple[bool, ProofObject]:
    """Debt-to-income ratio must be in [0, 1].

    Standard: CFPB Qualified Mortgage rule — 43% DTI max (Fraction(43, 100))
    falsifies_if: app.debt_to_income_ratio < 0 or > 1.
    """
    ok = Fraction(0) <= app.debt_to_income_ratio <= Fraction(1)
    premises = [
        f"application_id={app.application_id}",
        f"dti={app.debt_to_income_ratio}",
    ]
    return ok, ProofObject(
        rule="DTIRatioRange",
        premises=premises,
        conclusion=f"PASS: DTI {app.debt_to_income_ratio}" if ok else "VIOLATION: DTI out of [0,1]",
    )


def check_credit_score_range(app: LoanApplication) -> Tuple[bool, ProofObject]:
    """Credit score must be in [300, 850] (FICO range).

    Standard: ECOA 12 CFR Part 1002 — credit scoring range
    falsifies_if: app.credit_score < 300 or > 850.
    """
    ok = 300 <= app.credit_score <= 850
    premises = [
        f"application_id={app.application_id}",
        f"credit_score={app.credit_score}",
    ]
    return ok, ProofObject(
        rule="CreditScoreRange",
        premises=premises,
        conclusion=f"PASS: credit score {app.credit_score} in [300, 850]" if ok else f"VIOLATION: credit score {app.credit_score} out of FICO range",
    )


def check_assessment_year_positive(assessment: PropertyAssessment) -> Tuple[bool, ProofObject]:
    """Assessment year must be >= 1900.

    Standard: USPAP Standards — valid assessment year range
    falsifies_if: assessment.assessment_year < 1900.
    """
    ok = assessment.assessment_year >= 1900
    premises = [
        f"property_id={assessment.property_id}",
        f"assessment_year={assessment.assessment_year}",
    ]
    return ok, ProofObject(
        rule="AssessmentYearPositive",
        premises=premises,
        conclusion=f"PASS: year {assessment.assessment_year}" if ok else "VIOLATION: assessment year < 1900",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS

    Falsifies if: any check returns FAIL (nominal inputs should always pass).."""
    prop = Property(
        property_id="PROP-001",
        address="123 Main St, Springfield, IL 62701",
        parcel_number="12-34-567-890",
        property_type=PropertyType.SINGLE_FAMILY_RESIDENTIAL,
        lot_size_sqft=Fraction(8000),
    )
    assessment = PropertyAssessment(
        property_id="PROP-001",
        assessment_year=2024,
        land_value=Fraction(100000),
        improvement_value=Fraction(200000),
        total_value=Fraction(300000),
    )
    app = LoanApplication(
        application_id="APP-001",
        applicant_id="APP-001",
        property_id="PROP-001",
        loan_amount=Fraction(300000),
        applicant_income=Fraction(80000),
        credit_score=740,
        debt_to_income_ratio=Fraction(28, 100),
    )
    results = {}
    for fn, args in [
        (check_property_lot_size_positive, (prop,)),
        (check_property_address_nonempty, (prop,)),
        (check_loan_amount_positive, (app,)),
        (check_debt_to_income_ratio_range, (app,)),
        (check_credit_score_range, (app,)),
        (check_assessment_year_positive, (assessment,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
