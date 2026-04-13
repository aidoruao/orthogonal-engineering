#!/usr/bin/env python3
"""Hospitality Domain Invariants — Safety, accessibility, and service quality.

Standards:
- ADA Title III public accommodations
- NFPA 101 Life Safety Code
- FDA Food Code
- AH&LA lodging standards

Falsifies if:
- Property claims ADA compliance without accessible rooms
- Food outlet has critical violations above threshold
- Health inspection overdue
- Overbooking without compensation plan
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    AccommodationType,
    FoodService,
    GuestRoom,
    Property,
    Reservation,
    RoomStatus,
)


def check_ada_compliance(property: Property) -> Tuple[bool, ProofObject]:
    """ADA Title III requires accessible accommodations in public lodging.

    Falsifies if: property claims ADA compliance but has zero accessible rooms or
    falsifies_if: property claims ADA compliance but has zero accessible rooms or
    accessible room ratio is below the required threshold.
    """
    if not property.ada_compliant:
        return True, ProofObject(
            conclusion="Property not claiming ADA compliance",
            premises=["ADA compliant: False"],
            rule="ada_compliance_not_claimed"
        )
    
    accessible_rooms = sum(1 for r in property.rooms if r.ada_accessible)
    
    if accessible_rooms == 0:
        return False, ProofObject(
            conclusion="VIOLATION: Property claims ADA compliance but has no accessible rooms",
            premises=[
                f"Property: {property.name}",
                "ADA accessible rooms: 0"
            ],
            rule="ada_title_iii_accessible_rooms_required"
        )
    
    # ADA requires ~5% accessible rooms
    required_ratio = Fraction(1, 20)
    actual_ratio = Fraction(accessible_rooms, property.total_rooms)
    
    if actual_ratio < required_ratio:
        return False, ProofObject(
            conclusion=f"VIOLATION: Accessible rooms {actual_ratio} below required {required_ratio}",
            premises=[
                f"Accessible: {accessible_rooms}/{property.total_rooms}",
                f"Required: {required_ratio}"
            ],
            rule="ada_accessible_room_percentage"
        )
    
    return True, ProofObject(
        conclusion="Property meets ADA accessibility requirements",
        premises=[f"Accessible rooms: {accessible_rooms}/{property.total_rooms}"],
        rule="ada_compliant"
    )


def check_health_inspection_current(outlet: FoodService) -> Tuple[bool, ProofObject]:
    """FDA Food Code requires regular health inspections.

    Falsifies if: no inspection exists or last inspection is overdue.
    falsifies_if: no inspection exists or last inspection is overdue.
    """
    if outlet.last_health_inspection is None:
        return False, ProofObject(
            conclusion="VIOLATION: Food outlet has no health inspection record",
            premises=[f"Outlet: {outlet.name}", "Last inspection: None"],
            rule="fda_food_code_inspection_required"
        )
    
    if not outlet.inspection_current():
        from datetime import datetime
        days_overdue = (datetime.now() - outlet.last_health_inspection).days - 180
        return False, ProofObject(
            conclusion=f"VIOLATION: Health inspection overdue by {days_overdue} days",
            premises=[
                f"Last inspection: {outlet.last_health_inspection}",
                f"Days overdue: {days_overdue}"
            ],
            rule="health_inspection_currency"
        )
    
    return True, ProofObject(
        conclusion="Health inspection current",
        premises=[f"Last inspection: {outlet.last_health_inspection}"],
        rule="health_inspection_current"
    )


def check_fire_safety_compliance(property: Property) -> Tuple[bool, ProofObject]:
    """NFPA 101 Life Safety Code requires current fire inspection.

    Falsifies if: fire_inspection_current is False.
    falsifies_if: fire_inspection_current is False.
    """
    if not property.fire_inspection_current:
        return False, ProofObject(
            conclusion="VIOLATION: Property fire inspection not current",
            premises=[
                f"Property: {property.name}",
                "Fire inspection: Not current"
            ],
            rule="nfpa_101_fire_inspection"
        )
    
    return True, ProofObject(
        conclusion="Fire safety inspection current",
        premises=["Fire inspection: Current"],
        rule="fire_safety_compliant"
    )


def check_critical_violations(outlet: FoodService, threshold: int) -> Tuple[bool, ProofObject]:
    """Critical health violations pose immediate public health risk.

    Falsifies if: critical_violations exceed the allowed threshold.
    falsifies_if: critical_violations exceed the allowed threshold.
    """
    if outlet.critical_violations > threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: Critical violations {outlet.critical_violations} exceed threshold {threshold}",
            premises=[
                f"Outlet: {outlet.name}",
                f"Critical violations: {outlet.critical_violations}",
                f"Threshold: {threshold}"
            ],
            rule="food_safety_critical_violations"
        )
    
    return True, ProofObject(
        conclusion="Critical violations within acceptable range",
        premises=[f"Critical violations: {outlet.critical_violations}"],
        rule="critical_violations_acceptable"
    )


def check_overbooking_protection(property: Property, reservation_count: int) -> Tuple[bool, ProofObject]:
    """Overbooking without walk protection plan violates consumer protection.

    Falsifies if: reservation_count exceeds total_rooms by more than the allowed
    falsifies_if: reservation_count exceeds total_rooms by more than the allowed
    tolerance without protection.
    """
    if reservation_count > property.total_rooms:
        overbook_amount = reservation_count - property.total_rooms
        overbook_pct = Fraction(overbook_amount, property.total_rooms) * 100
        
        if overbook_pct > Fraction(5):  # > 5% overbook
            return False, ProofObject(
                conclusion=f"VIOLATION: Severe overbooking {overbook_pct}% without adequate protection",
                premises=[
                    f"Reservations: {reservation_count}",
                    f"Rooms: {property.total_rooms}",
                    f"Overbooked: {overbook_amount} ({overbook_pct}%)"
                ],
                rule="overbooking_walk_protection_required"
            )
    
    return True, ProofObject(
        conclusion="Booking level within capacity or acceptable overbooking",
        premises=[
            f"Reservations: {reservation_count}",
            f"Capacity: {property.total_rooms}"
        ],
        rule="booking_capacity_valid"
    )


def check_ada_reservation_honored(reservation: Reservation, assigned_room: GuestRoom) -> Tuple[bool, ProofObject]:
    """ADA requires accessible room requests be honored when available.

    Falsifies if: guest requested an accessible room but received a non-accessible
    falsifies_if: guest requested an accessible room but received a non-accessible
    assignment while such rooms are available.
    """
    if reservation.ada_room_requested and not assigned_room.ada_accessible:
        return False, ProofObject(
            conclusion="VIOLATION: ADA room request not honored",
            premises=[
                f"Reservation: {reservation.reservation_id}",
                "ADA requested: True",
                f"Room {assigned_room.room_number} accessible: False"
            ],
            rule="ada_room_request_accommodation"
        )
    
    return True, ProofObject(
        conclusion="Room assignment respects accessibility request",
        premises=[
            f"ADA requested: {reservation.ada_room_requested}",
            f"Room accessible: {assigned_room.ada_accessible}"
        ],
        rule="ada_reservation_honored"
    )


def run_all_invariants() -> dict:
    """Run all D_HOSPITALITY invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    property = Property(
        property_id=None,
        name=None,
        property_type=AccommodationType.HOTEL,
        star_rating=None,
        total_rooms=None,
        ada_compliant=None,
        fire_inspection_current=None,
    )
    reservation = Reservation(
        reservation_id=None,
        guest_name=None,
        property_id=None,
        room_number=None,
        check_in=None,
        check_out=None,
        rate_per_night=Fraction(1),
        total_charge=Fraction(1),
        ada_room_requested=None,
    )
    guest_room = GuestRoom(
        room_number=None,
        room_type=None,
        max_occupancy=None,
        ada_accessible=None,
        status=RoomStatus.OCCUPIED,
        rack_rate=Fraction(1),
        floor=None,
        square_feet=None,
    )
    food_service = FoodService(
        outlet_id=None,
        name=None,
        outlet_type=None,
        last_health_inspection=None,
        health_score=None,
        critical_violations=None,
        seating_capacity=None,
    )

    checks = [
        ("check_ada_compliance", lambda: check_ada_compliance(property)),
        ("check_ada_reservation_honored", lambda: check_ada_reservation_honored(reservation, guest_room)),
        ("check_critical_violations", lambda: check_critical_violations(food_service, 1)),
        ("check_fire_safety_compliance", lambda: check_fire_safety_compliance(property)),
        ("check_health_inspection_current", lambda: check_health_inspection_current(food_service)),
        ("check_overbooking_protection", lambda: check_overbooking_protection(property, 1)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            result = func()
            if isinstance(result, tuple) and len(result) == 2:
                success, proof = result
                results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
            else:
                passed = getattr(result, "passed", True)
                results[name] = "PASS" if passed else "FAIL: " + str(getattr(result, "evidence", result))
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_HOSPITALITY invariants: PASS")
