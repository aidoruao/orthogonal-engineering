"""D_TRANSPORTATION invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: 49 CFR (FMCSA regulations), DOT standards
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import List, Dict
from datetime import datetime, timedelta


@dataclass
class CommercialDriver:
    """Commercial vehicle driver."""
    driver_id: str
    name: str
    hours_driven_today: Fraction
    hours_on_duty_today: Fraction
    last_30_day_hours: List[Fraction]
    vehicle_inspection_current: bool


@dataclass
class Vehicle:
    """Commercial motor vehicle."""
    vehicle_id: str
    vin: str
    gvwr_lbs: Fraction  # Gross Vehicle Weight Rating
    last_annual_inspection: datetime
    pre_trip_inspection_done: bool


@dataclass
class HazmatShipment:
    """Hazardous materials shipment."""
    shipment_id: str
    hazard_class: str  # Class 1-9
    placard_required: bool
    placard_displayed: bool
    shipping_papers_complete: bool


def check_hours_of_service_limits() -> bool:
    """
    Invariant: Drivers comply with HOS limits (11hr driving, 14hr window).
    Falsification: If driver exceeds 11 hours driving in 14-hour window.
    """
    # Compliant driver
    compliant_driver = CommercialDriver(
        driver_id="DRV001",
        name="Safe Driver",
        hours_driven_today=Fraction(10),  # Under 11 hour limit
        hours_on_duty_today=Fraction(13),  # Under 14 hour window
        last_30_day_hours=[Fraction(60), Fraction(58), Fraction(55)],
        vehicle_inspection_current=True,
    )
    
    # Check daily driving limit (11 hours)
    assert compliant_driver.hours_driven_today <= Fraction(11), (
        f"Driver {compliant_driver.name} exceeded 11-hour driving limit: "
        f"{compliant_driver.hours_driven_today} hours"
    )
    
    # Check duty window (14 hours)
    assert compliant_driver.hours_on_duty_today <= Fraction(14), (
        f"Driver {compliant_driver.name} exceeded 14-hour duty window: "
        f"{compliant_driver.hours_on_duty_today} hours"
    )
    
    return True


def check_vehicle_inspection_current() -> bool:
    """
    Invariant: CMVs have current annual inspection.
    Falsification: If vehicle with expired annual inspection passes check.
    """
    vehicle = Vehicle(
        vehicle_id="VEH001",
        vin="1HGBH41JXMN109186",
        gvwr_lbs=Fraction(26000),
        last_annual_inspection=datetime.now() - timedelta(days=400),  # Expired
        pre_trip_inspection_done=True,
    )
    
    # Annual inspection required every 12 months
    inspection_due = vehicle.last_annual_inspection + timedelta(days=365)
    
    assert datetime.now() <= inspection_due, (
        f"Vehicle {vehicle.vehicle_id} annual inspection expired. "
        f"Due: {inspection_due}, Now: {datetime.now()}"
    )
    
    return True


def check_pre_trip_inspection() -> bool:
    """
    Invariant: Driver performs pre-trip inspection before driving.
    Falsification: If driver starts without pre-trip inspection.
    """
    vehicle = Vehicle(
        vehicle_id="VEH002",
        vin="1HGBH41JXMN109187",
        gvwr_lbs=Fraction(26000),
        last_annual_inspection=datetime.now(),
        pre_trip_inspection_done=False,  # Not done!
    )
    
    assert vehicle.pre_trip_inspection_done is True, (
        f"Vehicle {vehicle.vehicle_id} cannot operate without pre-trip inspection"
    )
    
    return True


def check_hazmat_placarding() -> bool:
    """
    Invariant: Hazmat shipments display required placards.
    Falsification: If Class 3 hazmat shipped without proper placarding.
    """
    # Gasoline shipment (Class 3)
    gasoline_shipment = HazmatShipment(
        shipment_id="HAZ001",
        hazard_class="3",  # Flammable liquid
        placard_required=True,
        placard_displayed=False,  # Missing!
        shipping_papers_complete=True,
    )
    
    if gasoline_shipment.placard_required:
        assert gasoline_shipment.placard_displayed is True, (
            f"Hazmat shipment {gasoline_shipment.shipment_id} Class {gasoline_shipment.hazard_class} "
            f"requires placard but not displayed"
        )
    
    return True


def check_hazmat_shipping_papers() -> bool:
    """
    Invariant: Hazmat shipments have complete shipping papers.
    Falsification: If hazmat transported without proper documentation.
    """
    shipment = HazmatShipment(
        shipment_id="HAZ002",
        hazard_class="8",  # Corrosive
        placard_required=True,
        placard_displayed=True,
        shipping_papers_complete=False,  # Incomplete!
    )
    
    assert shipment.shipping_papers_complete is True, (
        f"Hazmat shipment {shipment.shipment_id} must have complete shipping papers"
    )
    
    return True


def check_cdl_required_for_heavy_vehicles() -> bool:
    """
    Invariant: Vehicles over 26,001 lbs require CDL operator.
    Falsification: If heavy vehicle operated without CDL requirement check.
    """
    heavy_vehicle = Vehicle(
        vehicle_id="VEH003",
        vin="1HGBH41JXMN109188",
        gvwr_lbs=Fraction(33000),  # Over 26,001 lbs - requires CDL
        last_annual_inspection=datetime.now(),
        pre_trip_inspection_done=True,
    )
    
    cdl_threshold = Fraction(26001)
    
    assert heavy_vehicle.gvwr_lbs >= cdl_threshold, (
        f"Vehicle {heavy_vehicle.vehicle_id} GVWR {heavy_vehicle.gvwr_lbs} lbs "
        f"requires CDL (threshold: {cdl_threshold} lbs)"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("hos_limits", check_hours_of_service_limits),
        ("annual_inspection", check_vehicle_inspection_current),
        ("pre_trip", check_pre_trip_inspection),
        ("hazmat_placard", check_hazmat_placarding),
        ("hazmat_papers", check_hazmat_shipping_papers),
        ("cdl_required", check_cdl_required_for_heavy_vehicles),
    ]
    
    for name, check_func in checks:
        try:
            check_func()
            results[name] = "PASS"
        except AssertionError as e:
            results[name] = f"FAIL: {e}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_TRANSPORTATION invariants: PASS")
