#!/usr/bin/env python3
"""
City Infrastructure Domain System for Orthogonal Engineering
Urban Planning, Municipal Governance, Civic Technology

This module extends the OE domain system to include city-level infrastructure,
covering everything from utilities to transportation to public safety.

Author: Kimi CLI (Architectural Steward)
Session: 24ae8482-54c6-4ff6-869a-e737c2ad2917
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class InfrastructureLayer(Enum):
    """Layer classification for city infrastructure."""
    REGIONAL = "regional"          # Multi-city / County
    CITYWIDE = "citywide"          # Entire municipality
    DISTRICT = "district"          # Neighborhood/Borough
    BLOCK = "block"                # Street level
    BUILDING = "building"          # Individual structures
    SUBSTRUCTURE = "substructure"  # Below ground / internal


class InfrastructureCategory(Enum):
    """Categories of city infrastructure."""
    # Utilities
    WATER = "water_supply"
    WASTEWATER = "wastewater"
    ELECTRICITY = "electricity"
    GAS = "natural_gas"
    TELECOMMUNICATIONS = "telecommunications"
    INTERNET = "internet"
    
    # Transportation
    ROADS = "roads"
    BRIDGES = "bridges"
    PUBLIC_TRANSIT = "public_transit"
    RAIL = "rail"
    AIRPORTS = "airports"
    PORTS = "ports"
    CYCLING = "cycling_infrastructure"
    PEDESTRIAN = "pedestrian_infrastructure"
    
    # Public Safety
    POLICE = "police"
    FIRE = "fire_department"
    EMS = "emergency_medical"
    EMERGENCY_MANAGEMENT = "emergency_management"
    
    # Health & Social
    HEALTHCARE = "healthcare"
    PUBLIC_HEALTH = "public_health"
    SOCIAL_SERVICES = "social_services"
    EDUCATION = "education"
    LIBRARIES = "libraries"
    
    # Environmental
    WASTE_MANAGEMENT = "waste_management"
    RECYCLING = "recycling"
    PARKS = "parks_recreation"
    ENVIRONMENTAL = "environmental_protection"
    FLOOD_CONTROL = "flood_control"
    
    # Governance
    CITY_HALL = "city_governance"
    PERMITS = "permits_licensing"
    RECORDS = "records_management"
    ELECTIONS = "elections"
    
    # Digital
    OPEN_DATA = "open_data"
    SMART_CITY = "smart_city"
    DIGITAL_SERVICES = "digital_services"
    CYBERSECURITY = "cybersecurity"


@dataclass
class InfrastructureDomain:
    """A city infrastructure domain."""
    domain_id: str
    name: str
    category: InfrastructureCategory
    layer: InfrastructureLayer
    description: str
    
    # Dependencies
    upstream_dependencies: List[str] = field(default_factory=list)
    downstream_dependencies: List[str] = field(default_factory=list)
    
    # Criticality
    criticality_level: str = "MEDIUM"  # CRITICAL, HIGH, MEDIUM, LOW
    failure_cascade_risk: str = "MEDIUM"  # SEVERE, HIGH, MEDIUM, LOW
    
    # Governance
    governing_authority: str = ""
    regulatory_framework: List[str] = field(default_factory=list)
    
    # Digital components
    software_systems: List[str] = field(default_factory=list)
    iot_sensors: List[str] = field(default_factory=list)
    data_sources: List[str] = field(default_factory=list)
    
    # Vendored repositories (if applicable)
    relevant_repos: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CityInfrastructureSystem:
    """System for managing city infrastructure domains."""
    
    def __init__(self, city_name: str = "Orthogonal City"):
        self.city_name = city_name
        self.domains: Dict[str, InfrastructureDomain] = {}
        self._initialize_infrastructure()
    
    def _initialize_infrastructure(self) -> None:
        """Initialize the complete city infrastructure taxonomy."""
        
        # Water Infrastructure
        self.add_domain(InfrastructureDomain(
            domain_id="ci_water_supply",
            name="Water Supply System",
            category=InfrastructureCategory.WATER,
            layer=InfrastructureLayer.CITYWIDE,
            description="Potable water treatment, distribution, and storage",
            criticality_level="CRITICAL",
            failure_cascade_risk="SEVERE",
            governing_authority="Department of Water and Power",
            regulatory_framework=["Safe Drinking Water Act", "EPA Standards"],
            downstream_dependencies=["ci_wastewater", "ci_fire"],
            software_systems=["SCADA", "GIS Mapping", "Pressure Monitoring"],
        ))
        
        self.add_domain(InfrastructureDomain(
            domain_id="ci_wastewater",
            name="Wastewater Management",
            category=InfrastructureCategory.WASTEWATER,
            layer=InfrastructureLayer.CITYWIDE,
            description="Sewage collection, treatment, and environmental discharge",
            criticality_level="CRITICAL",
            failure_cascade_risk="SEVERE",
            governing_authority="Wastewater Treatment Authority",
            regulatory_framework=["Clean Water Act", "EPA NPDES"],
            upstream_dependencies=["ci_water_supply"],
            software_systems=["Treatment Plant SCADA", "Flow Monitoring"],
        ))
        
        # Energy Infrastructure
        self.add_domain(InfrastructureDomain(
            domain_id="ci_electricity",
            name="Electrical Grid",
            category=InfrastructureCategory.ELECTRICITY,
            layer=InfrastructureLayer.REGIONAL,
            description="Power generation, transmission, and distribution",
            criticality_level="CRITICAL",
            failure_cascade_risk="SEVERE",
            governing_authority="Municipal Utility Department",
            regulatory_framework=["NERC CIP", "State PUC Regulations"],
            downstream_dependencies=["ci_water_supply", "ci_telecommunications", "ci_smart_city"],
            software_systems=["Grid Management System", "Outage Management", "AMI"],
            iot_sensors=["Smart Meters", "Grid Sensors", "Transformer Monitors"],
        ))
        
        # Transportation
        self.add_domain(InfrastructureDomain(
            domain_id="ci_roads",
            name="Road Network",
            category=InfrastructureCategory.ROADS,
            layer=InfrastructureLayer.CITYWIDE,
            description="Street maintenance, traffic management, and paving",
            criticality_level="HIGH",
            failure_cascade_risk="HIGH",
            governing_authority="Department of Transportation",
            software_systems=["Traffic Signal Control", "Pavement Management", "Work Order System"],
            iot_sensors=["Traffic Counters", "Road Condition Sensors"],
        ))
        
        self.add_domain(InfrastructureDomain(
            domain_id="ci_public_transit",
            name="Public Transit System",
            category=InfrastructureCategory.PUBLIC_TRANSIT,
            layer=InfrastructureLayer.CITYWIDE,
            description="Bus, light rail, and paratransit services",
            criticality_level="HIGH",
            failure_cascade_risk="HIGH",
            governing_authority="Metropolitan Transit Authority",
            software_systems=["AVL System", "Fare Collection", "Scheduling", "Real-time Info"],
            iot_sensors=["GPS Trackers", "Passenger Counters", "Vehicle Diagnostics"],
        ))
        
        # Public Safety
        self.add_domain(InfrastructureDomain(
            domain_id="ci_police",
            name="Police Department",
            category=InfrastructureCategory.POLICE,
            layer=InfrastructureLayer.CITYWIDE,
            description="Law enforcement, patrol, and emergency response",
            criticality_level="CRITICAL",
            failure_cascade_risk="SEVERE",
            governing_authority="Police Department",
            regulatory_framework=["CJIS Security Policy", "State LE Standards"],
            software_systems=["CAD System", "RMS", "Body Cameras", "LPR", "Analytics"],
            relevant_repos=["codeforamerica/police-data-trust"],
        ))
        
        self.add_domain(InfrastructureDomain(
            domain_id="ci_fire",
            name="Fire Department",
            category=InfrastructureCategory.FIRE,
            layer=InfrastructureLayer.CITYWIDE,
            description="Fire suppression, rescue, and emergency medical first response",
            criticality_level="CRITICAL",
            failure_cascade_risk="SEVERE",
            governing_authority="Fire Department",
            upstream_dependencies=["ci_water_supply"],
            software_systems=["CAD System", "Mobile Data", "Hazmat Database"],
        ))
        
        self.add_domain(InfrastructureDomain(
            domain_id="ci_ems",
            name="Emergency Medical Services",
            category=InfrastructureCategory.EMS,
            layer=InfrastructureLayer.CITYWIDE,
            description="Ambulance services and medical emergency response",
            criticality_level="CRITICAL",
            failure_cascade_risk="SEVERE",
            governing_authority="EMS Department",
            software_systems=["CAD System", "ePCR", "Hospital Diversion"],
        ))
        
        # Healthcare
        self.add_domain(InfrastructureDomain(
            domain_id="ci_public_health",
            name="Public Health Department",
            category=InfrastructureCategory.PUBLIC_HEALTH,
            layer=InfrastructureLayer.CITYWIDE,
            description="Disease surveillance, health education, and prevention",
            criticality_level="CRITICAL",
            failure_cascade_risk="HIGH",
            governing_authority="Department of Public Health",
            regulatory_framework=["HIPAA", "CDC Guidelines"],
            software_systems=["Disease Surveillance", "Immunization Registry", "EHR"],
        ))
        
        # Environmental
        self.add_domain(InfrastructureDomain(
            domain_id="ci_waste_management",
            name="Solid Waste Management",
            category=InfrastructureCategory.WASTE_MANAGEMENT,
            layer=InfrastructureLayer.CITYWIDE,
            description="Trash collection, disposal, and landfill operations",
            criticality_level="HIGH",
            failure_cascade_risk="HIGH",
            governing_authority="Department of Sanitation",
            software_systems=["Route Optimization", "Fleet Management", "Weighbridge"],
            iot_sensors=["Bin Fill Sensors", "GPS Trackers"],
        ))
        
        self.add_domain(InfrastructureDomain(
            domain_id="ci_parks",
            name="Parks and Recreation",
            category=InfrastructureCategory.PARKS,
            layer=InfrastructureLayer.DISTRICT,
            description="Public parks, facilities, and recreational programs",
            criticality_level="MEDIUM",
            failure_cascade_risk="LOW",
            governing_authority="Parks and Recreation Department",
            software_systems=["Facility Booking", "Program Registration", "Asset Management"],
        ))
        
        # Digital Infrastructure
        self.add_domain(InfrastructureDomain(
            domain_id="ci_open_data",
            name="Open Data Portal",
            category=InfrastructureCategory.OPEN_DATA,
            layer=InfrastructureLayer.CITYWIDE,
            description="Public datasets, APIs, and transparency initiatives",
            criticality_level="MEDIUM",
            failure_cascade_risk="LOW",
            governing_authority="Chief Data Officer",
            software_systems=["Data Portal Platform", "ETL Pipelines", "API Gateway"],
            relevant_repos=["opendatakit", "ckan/ckan"],
        ))
        
        self.add_domain(InfrastructureDomain(
            domain_id="ci_smart_city",
            name="Smart City Platform",
            category=InfrastructureCategory.SMART_CITY,
            layer=InfrastructureLayer.CITYWIDE,
            description="IoT integration, data analytics, and intelligent infrastructure",
            criticality_level="HIGH",
            failure_cascade_risk="MEDIUM",
            governing_authority="Smart City Office",
            upstream_dependencies=["ci_electricity", "ci_telecommunications"],
            software_systems=["IoT Platform", "Data Lake", "Analytics Engine", "Dashboard"],
            iot_sensors=["Environmental Sensors", "Traffic Sensors", "Utility Sensors"],
            relevant_repos=["thingsboard/thingsboard", "fiware"],
        ))
        
        self.add_domain(InfrastructureDomain(
            domain_id="ci_cybersecurity",
            name="Municipal Cybersecurity",
            category=InfrastructureCategory.CYBERSECURITY,
            layer=InfrastructureLayer.CITYWIDE,
            description="Security operations, threat monitoring, and incident response",
            criticality_level="CRITICAL",
            failure_cascade_risk="SEVERE",
            governing_authority="CISO Office",
            regulatory_framework=["NIST CSF", "State Cybersecurity Laws"],
            software_systems=["SIEM", "EDR", "Vulnerability Scanner", "SOAR"],
            relevant_repos=["wazuh/wazuh", "Security-Onion-Solutions"],
        ))
        
        # Governance
        self.add_domain(InfrastructureDomain(
            domain_id="ci_permits",
            name="Permits and Licensing",
            category=InfrastructureCategory.PERMITS,
            layer=InfrastructureLayer.CITYWIDE,
            description="Building permits, business licenses, and regulatory approvals",
            criticality_level="HIGH",
            failure_cascade_risk="MEDIUM",
            governing_authority="Department of Building and Safety",
            software_systems=["Permit Tracking", "Inspection Scheduling", "Plan Review"],
        ))
        
        self.add_domain(InfrastructureDomain(
            domain_id="ci_elections",
            name="Elections Administration",
            category=InfrastructureCategory.ELECTIONS,
            layer=InfrastructureLayer.CITYWIDE,
            description="Voter registration, polling, and results reporting",
            criticality_level="CRITICAL",
            failure_cascade_risk="SEVERE",
            governing_authority="Elections Department",
            regulatory_framework=["HAVA", "State Election Codes"],
            software_systems=["Voter Registration", "Ballot Tabulation", "Results Reporting"],
        ))
        
        # Telecommunications
        self.add_domain(InfrastructureDomain(
            domain_id="ci_telecommunications",
            name="Telecommunications Infrastructure",
            category=InfrastructureCategory.TELECOMMUNICATIONS,
            layer=InfrastructureLayer.CITYWIDE,
            description="Fiber optic, wireless, and public safety networks",
            criticality_level="CRITICAL",
            failure_cascade_risk="HIGH",
            governing_authority="Information Technology Department",
            upstream_dependencies=["ci_electricity"],
            software_systems=["Network Monitoring", "DNS", "Radio Systems"],
        ))
        
        self.add_domain(InfrastructureDomain(
            domain_id="ci_internet",
            name="Municipal Broadband",
            category=InfrastructureCategory.INTERNET,
            layer=InfrastructureLayer.CITYWIDE,
            description="Public internet access and digital equity programs",
            criticality_level="HIGH",
            failure_cascade_risk="MEDIUM",
            governing_authority="Digital Equity Office",
            software_systems=["Network Management", "User Portal", "Bandwidth Monitoring"],
        ))
    
    def add_domain(self, domain: InfrastructureDomain) -> None:
        """Add a domain to the system."""
        self.domains[domain.domain_id] = domain
    
    def get_critical_infrastructure(self) -> List[InfrastructureDomain]:
        """Get all critical infrastructure domains."""
        return [d for d in self.domains.values() if d.criticality_level == "CRITICAL"]
    
    def get_domains_by_category(self, category: InfrastructureCategory) -> List[InfrastructureDomain]:
        """Get domains by category."""
        return [d for d in self.domains.values() if d.category == category]
    
    def analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze the dependency graph."""
        analysis = {
            "total_domains": len(self.domains),
            "critical_domains": len(self.get_critical_infrastructure()),
            "dependency_chains": [],
            "single_points_of_failure": [],
        }
        
        # Find domains with no upstream (sources)
        sources = [d for d in self.domains.values() if not d.upstream_dependencies]
        analysis["source_domains"] = [d.domain_id for d in sources]
        
        # Find domains with many downstream (critical hubs)
        hub_domains = sorted(
            self.domains.values(),
            key=lambda d: len(d.downstream_dependencies),
            reverse=True
        )[:5]
        analysis["critical_hubs"] = [
            {"domain": d.domain_id, "downstream_count": len(d.downstream_dependencies)}
            for d in hub_domains
        ]
        
        return analysis
    
    def export_to_json(self, path: Path) -> None:
        """Export the infrastructure system to JSON."""
        data = {
            "city_name": self.city_name,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_domains": len(self.domains),
            "domains": {
                domain_id: {
                    "domain_id": d.domain_id,
                    "name": d.name,
                    "category": d.category.value,
                    "layer": d.layer.value,
                    "description": d.description,
                    "criticality_level": d.criticality_level,
                    "failure_cascade_risk": d.failure_cascade_risk,
                    "governing_authority": d.governing_authority,
                    "regulatory_framework": d.regulatory_framework,
                    "upstream_dependencies": d.upstream_dependencies,
                    "downstream_dependencies": d.downstream_dependencies,
                    "software_systems": d.software_systems,
                    "iot_sensors": d.iot_sensors,
                    "relevant_repos": d.relevant_repos,
                }
                for domain_id, d in self.domains.items()
            }
        }
        
        with open(path, "w") as f:
            json.dump(data, f, indent=2, sort_keys=True)


# Global city infrastructure instance
city_infra = CityInfrastructureSystem("Orthogonal City")


if __name__ == "__main__":
    print("=" * 70)
    print("ORTHOGONAL CITY - INFRASTRUCTURE DOMAIN SYSTEM")
    print("=" * 70)
    print()
    
    print(f"Total Infrastructure Domains: {len(city_infra.domains)}")
    print()
    
    print("CRITICAL INFRASTRUCTURE:")
    for domain in city_infra.get_critical_infrastructure():
        print(f"  ⚠️  {domain.name} ({domain.category.value})")
    print()
    
    analysis = city_infra.analyze_dependencies()
    print("DEPENDENCY ANALYSIS:")
    print(f"  Source domains: {len(analysis['source_domains'])}")
    print(f"  Critical hubs: {len(analysis['critical_hubs'])}")
    print()
    print("TOP CRITICAL HUBS:")
    for hub in analysis['critical_hubs']:
        print(f"  • {hub['domain']}: {hub['downstream_count']} downstream dependencies")
    print()
    
    # Export to JSON
    output_path = Path("/home/idor/orthogonal-engineering/vendor_analysis/infrastructure/city_infrastructure.json")
    city_infra.export_to_json(output_path)
    print(f"Exported to: {output_path}")
    print()
    print("=" * 70)
