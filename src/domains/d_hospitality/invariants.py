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
from .implementation import Property, FoodService, Reservation, GuestRoom


def check_ada_compliance(property: Property) -> Tuple[bool, ProofObject]:
    """ADA Title III requires accessible accommodations in public lodging.
    
    falsifies_if:
        - ada_compliant is True but no ada_accessible rooms exist
        - Less than required percentage of rooms are accessible
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
    
    falsifies_if:
        - No inspection within 6 months
        - Critical violations not corrected
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
    
    falsifies_if:
        - fire_inspection_current is False
        - No evacuation plan posted
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
    
    falsifies_if:
        - critical_violations > threshold
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
    
    falsifies_if:
        - reservation_count > total_rooms without walk policy
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
    
    falsifies_if:
        - Guest requested accessible room but assigned non-accessible
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
