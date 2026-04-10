#!/usr/bin/env python3
"""D_TRANSIT Invariants — Public Transit Systems

Verifies ADA accessibility, FTA safety standards, on-time performance,
headway reliability, vehicle useful life, incident reporting.
Federal Transit Administration (FTA), Americans with Disabilities Act (ADA).
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    TransitVehicle, TransitRoute, TransitStop, ServiceReliability, SafetyIncident,
    VehicleType, AccessibilityFeature,
    fta_minimum_ada_compliance_pct, fta_on_time_performance_threshold,
    fta_headway_reliability_threshold, ada_wheelchair_space_minimum,
    fta_vehicle_useful_life_bus_years, fta_reportable_incident_threshold_usd
)


def check_ada_vehicle_compliance(vehicle: TransitVehicle) -> Tuple[bool, ProofObject]:
    """
    Fixed-route transit vehicles must be ADA accessible with wheelchair spaces.

    ADA 49 CFR Part 38: All fixed-route buses must have wheelchair ramps/lifts
    and minimum 2 wheelchair spaces.

    Falsifies if: ada_compliant=False or wheelchair_spaces < 2
    """
    min_spaces = ada_wheelchair_space_minimum()

    if not vehicle.ada_compliant:
        return False, ProofObject(
            conclusion=f"VIOLATION: Vehicle {vehicle.vehicle_id} not ADA compliant",
            premises=[
                f"Vehicle: {vehicle.vehicle_id} ({vehicle.vehicle_type.name})",
                f"ADA compliant: {vehicle.ada_compliant}",
                "ADA requires all fixed-route vehicles be accessible"
            ],
            rule="ada_49_cfr_part_38"
        )

    if vehicle.wheelchair_spaces < min_spaces:
        return False, ProofObject(
            conclusion=f"VIOLATION: Vehicle {vehicle.vehicle_id} has {vehicle.wheelchair_spaces} wheelchair spaces, need {min_spaces}",
            premises=[
                f"Wheelchair spaces: {vehicle.wheelchair_spaces}",
                f"Required: {min_spaces}",
                "ADA requires minimum 2 wheelchair spaces per bus"
            ],
            rule="ada_wheelchair_space_minimum"
        )

    return True, ProofObject(
        conclusion=f"Vehicle {vehicle.vehicle_id} meets ADA requirements",
        premises=[
            f"ADA compliant: {vehicle.ada_compliant}",
            f"Wheelchair spaces: {vehicle.wheelchair_spaces} >= {min_spaces}"
        ],
        rule="ada_49_cfr_part_38"
    )


def check_on_time_performance(reliability: ServiceReliability) -> Tuple[bool, ProofObject]:
    """
    Routes must meet FTA on-time performance threshold (≥80%).

    FTA National Transit Database: On-time performance measures service quality.
    Arrivals within 5 minutes of schedule count as on-time.

    Falsifies if: on_time_arrivals_pct < 80%
    """
    threshold = fta_on_time_performance_threshold()

    if reliability.on_time_arrivals_pct < threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: Route {reliability.route_id} on-time performance {reliability.on_time_arrivals_pct}% below threshold {threshold}%",
            premises=[
                f"Route: {reliability.route_id}",
                f"On-time: {reliability.on_time_arrivals_pct}%",
                f"Threshold: {threshold}%",
                "FTA: Service quality requires ≥80% on-time arrivals"
            ],
            rule="fta_on_time_performance"
        )

    return True, ProofObject(
        conclusion=f"Route {reliability.route_id} meets on-time performance standard",
        premises=[f"On-time: {reliability.on_time_arrivals_pct}% >= {threshold}%"],
        rule="fta_on_time_performance"
    )


def check_headway_reliability(route: TransitRoute, actual_headway: Fraction) -> Tuple[bool, ProofObject]:
    """
    Actual headway must not deviate more than 20% from scheduled headway.

    FTA: Headway reliability measures service consistency. Excessive deviation
    (bunching or gaps) degrades service quality.

    Falsifies if: |actual - scheduled| / scheduled > 20%
    """
    scheduled = route.frequency_minutes
    deviation_pct = abs(actual_headway - scheduled) * Fraction(100) / scheduled
    threshold = fta_headway_reliability_threshold()

    if deviation_pct > threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: Route {route.route_id} headway deviation {deviation_pct}% exceeds {threshold}%",
            premises=[
                f"Route: {route.route_id}",
                f"Scheduled headway: {scheduled} min",
                f"Actual headway: {actual_headway} min",
                f"Deviation: {deviation_pct}%",
                f"Threshold: {threshold}%"
            ],
            rule="fta_headway_reliability"
        )

    return True, ProofObject(
        conclusion=f"Route {route.route_id} headway within acceptable deviation",
        premises=[f"Deviation: {deviation_pct}% <= {threshold}%"],
        rule="fta_headway_reliability"
    )


def check_vehicle_useful_life(vehicle: TransitVehicle) -> Tuple[bool, ProofObject]:
    """
    Vehicles must not exceed FTA useful life standards (12 years for buses).

    FTA: Vehicles exceeding useful life may not be eligible for federal funding
    replacement and pose higher safety/reliability risks.

    Falsifies if: age_years > 12 for buses
    """
    if vehicle.vehicle_type not in [VehicleType.BUS, VehicleType.BRT]:
        return True, ProofObject(
            conclusion=f"Vehicle {vehicle.vehicle_id} not bus type, useful life N/A",
            premises=[f"Type: {vehicle.vehicle_type.name}"],
            rule="fta_useful_life"
        )

    limit = fta_vehicle_useful_life_bus_years()

    if vehicle.age_years > limit:
        return False, ProofObject(
            conclusion=f"VIOLATION: Vehicle {vehicle.vehicle_id} age {vehicle.age_years} years exceeds useful life {limit} years",
            premises=[
                f"Vehicle: {vehicle.vehicle_id}",
                f"Type: {vehicle.vehicle_type.name}",
                f"Age: {vehicle.age_years} years",
                f"Useful life: {limit} years",
                "FTA: Buses beyond useful life ineligible for federal funding"
            ],
            rule="fta_useful_life"
        )

    return True, ProofObject(
        conclusion=f"Vehicle {vehicle.vehicle_id} within useful life",
        premises=[f"Age: {vehicle.age_years} years <= {limit} years"],
        rule="fta_useful_life"
    )


def check_ada_stop_accessibility(stop: TransitStop) -> Tuple[bool, ProofObject]:
    """
    Transit stops on fixed routes must be ADA accessible.

    ADA 49 CFR Part 37: Bus stops must have accessible boarding areas
    (level platform, clear space, connection to pedestrian paths).

    Falsifies if: ada_accessible=False
    """
    if not stop.ada_accessible:
        return False, ProofObject(
            conclusion=f"VIOLATION: Stop {stop.stop_id} on route {stop.route_id} not ADA accessible",
            premises=[
                f"Stop: {stop.stop_id}",
                f"Route: {stop.route_id}",
                f"ADA accessible: {stop.ada_accessible}",
                "ADA requires accessible boarding areas for fixed-route stops"
            ],
            rule="ada_stop_accessibility"
        )

    return True, ProofObject(
        conclusion=f"Stop {stop.stop_id} is ADA accessible",
        premises=["ADA accessible boarding area provided"],
        rule="ada_stop_accessibility"
    )


def check_fta_incident_reporting(incident: SafetyIncident) -> Tuple[bool, ProofObject]:
    """
    Major incidents must be reported to FTA (injuries, fatalities, or $25k+ damage).

    FTA 49 CFR Part 659: Transit agencies must report safety incidents meeting
    defined thresholds to National Transit Database.

    Falsifies if: fta_reportable=False when criteria met
    """
    threshold = fta_reportable_incident_threshold_usd()

    reportable_criteria = (
        incident.fatalities > Fraction(0) or
        incident.injuries > Fraction(0) or
        incident.property_damage_usd >= threshold
    )

    if reportable_criteria and not incident.fta_reportable:
        return False, ProofObject(
            conclusion=f"VIOLATION: Incident {incident.incident_id} meets FTA reporting criteria but not flagged as reportable",
            premises=[
                f"Incident: {incident.incident_id}",
                f"Fatalities: {incident.fatalities}",
                f"Injuries: {incident.injuries}",
                f"Damage: ${incident.property_damage_usd}",
                f"Threshold: ${threshold}",
                f"FTA reportable: {incident.fta_reportable}",
                "FTA requires reporting of major incidents"
            ],
            rule="fta_incident_reporting_49_cfr_659"
        )

    if not reportable_criteria and incident.fta_reportable:
        return False, ProofObject(
            conclusion=f"VIOLATION: Incident {incident.incident_id} flagged as FTA reportable but doesn't meet criteria",
            premises=[
                f"Fatalities: {incident.fatalities}",
                f"Injuries: {incident.injuries}",
                f"Damage: ${incident.property_damage_usd}",
                "Incident does not meet reporting threshold"
            ],
            rule="fta_incident_reporting_49_cfr_659"
        )

    return True, ProofObject(
        conclusion=f"Incident {incident.incident_id} correctly classified for FTA reporting",
        premises=[
            f"Reportable: {incident.fta_reportable}",
            f"Meets criteria: {reportable_criteria}"
        ],
        rule="fta_incident_reporting_49_cfr_659"
    )
