#!/usr/bin/env python3
"""Geographic Information Domain Invariants — Spatial data quality, CRS, topology.

Standards:
- ISO 19115 metadata
- OGC Simple Features
- EPSG CRS registry
- INSPIRE data specifications

Falsifies if:
- Coordinates outside CRS valid bounds
- Polygon rings not closed
- Topology violations (overlaps, gaps)
- CRS mismatch between dataset and features
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    Coordinate, CoordinateReferenceSystem, Geometry,
    SpatialDataset, TopologyRule, RasterDataset, GeometryType
)


def check_crs_bounds(coord: Coordinate, crs: CoordinateReferenceSystem) -> Tuple[bool, ProofObject]:
    """Coordinates must be within valid range for their CRS.

    Falsifies if: coordinate exceeds CRS bounds (including |lon| > 180 or |lat| > 90 for geographic).
    """
    if crs.geographic:
        # Geographic: longitude [-180, 180], latitude [-90, 90]
        if coord.x < Fraction(-180) or coord.x > Fraction(180):
            return False, ProofObject(
                conclusion=f"VIOLATION: Longitude {coord.x} outside valid range [-180, 180]",
                premises=[f"Longitude: {coord.x}", "CRS: Geographic"],
                rule="geographic_longitude_bounds"
            )
        
        if coord.y < Fraction(-90) or coord.y > Fraction(90):
            return False, ProofObject(
                conclusion=f"VIOLATION: Latitude {coord.y} outside valid range [-90, 90]",
                premises=[f"Latitude: {coord.y}", "CRS: Geographic"],
                rule="geographic_latitude_bounds"
            )
    
    if not crs.is_valid_coordinate(coord):
        return False, ProofObject(
            conclusion="VIOLATION: Coordinate outside CRS defined bounds",
            premises=[
                f"Coordinate: ({coord.x}, {coord.y})",
                f"CRS: {crs.name} (EPSG:{crs.epsg_code})"
            ],
            rule="crs_coordinate_validity"
        )
    
    return True, ProofObject(
        conclusion="Coordinate within CRS bounds",
        premises=[f"CRS: {crs.name}", f"Coordinate: ({coord.x}, {coord.y})"],
        rule="crs_bounds_satisfied"
    )


def check_polygon_closure(geometry: Geometry) -> Tuple[bool, ProofObject]:
    """Polygon rings must be closed (first vertex = last vertex).

    Falsifies if: polygon ring lacks sufficient vertices or first/last coordinates differ.
    """
    if geometry.geometry_type not in (GeometryType.POLYGON, GeometryType.MULTIPOLYGON):
        return True, ProofObject(
            conclusion="Not a polygon type, closure check not applicable",
            premises=[f"Type: {geometry.geometry_type.name}"],
            rule="polygon_closure_not_applicable"
        )
    
    if len(geometry.coordinates) < 4:
        return False, ProofObject(
            conclusion="VIOLATION: Polygon has insufficient vertices (< 4)",
            premises=[f"Vertices: {len(geometry.coordinates)}"],
            rule="polygon_minimum_vertices"
        )
    
    first = geometry.coordinates[0]
    last = geometry.coordinates[-1]
    
    if first.x != last.x or first.y != last.y:
        return False, ProofObject(
            conclusion="VIOLATION: Polygon ring not closed",
            premises=[
                f"First: ({first.x}, {first.y})",
                f"Last: ({last.x}, {last.y})"
            ],
            rule="ogc_polygon_closure"
        )
    
    return True, ProofObject(
        conclusion="Polygon properly closed",
        premises=[f"Vertices: {len(geometry.coordinates)}"],
        rule="polygon_closure_valid"
    )


def check_crs_consistency(dataset: SpatialDataset) -> Tuple[bool, ProofObject]:
    """All features in dataset must use the dataset CRS.

    Falsifies if: any feature's CRS differs from the dataset CRS.
    """
    mismatches = []
    for feature in dataset.features:
        if feature.crs.epsg_code != dataset.crs.epsg_code:
            mismatches.append((feature.geometry_id, feature.crs.epsg_code))
    
    if mismatches:
        return False, ProofObject(
            conclusion=f"VIOLATION: {len(mismatches)} features have mismatched CRS",
            premises=[
                f"Dataset CRS: EPSG:{dataset.crs.epsg_code}",
                f"Mismatches: {mismatches[:3]}..."
            ],
            rule="dataset_crs_consistency"
        )
    
    return True, ProofObject(
        conclusion="All features use consistent CRS",
        premises=[f"Features: {len(dataset.features)}", f"CRS: EPSG:{dataset.crs.epsg_code}"],
        rule="crs_consistent"
    )


def check_topology_no_overlap(rule: TopologyRule, features: List[Geometry]) -> Tuple[bool, ProofObject]:
    """Polygons in same layer must not overlap (topological consistency).

    Falsifies if: geometry pairs overlap when rule type requires no overlap.
    """
    if rule.rule_type != "must_not_overlap":
        return True, ProofObject(
            conclusion="Not an overlap rule",
            premises=[f"Rule: {rule.rule_type}"],
            rule="topology_rule_type_check"
        )
    
    overlaps = []
    for i, f1 in enumerate(features):
        for f2 in features[i+1:]:
            if f1.intersects(f2):
                overlaps.append((f1.geometry_id, f2.geometry_id))
    
    if overlaps:
        return False, ProofObject(
            conclusion=f"VIOLATION: {len(overlaps)} overlapping feature pairs detected",
            premises=[
                f"Overlaps: {overlaps[:3]}...",
                "Rule: must_not_overlap"
            ],
            rule="topology_no_overlap"
        )
    
    return True, ProofObject(
        conclusion="No overlapping features detected",
        premises=[f"Features checked: {len(features)}"],
        rule="topology_valid"
    )


def check_metadata_completeness(dataset: SpatialDataset) -> Tuple[bool, ProofObject]:
    """ISO 19115 requires certain metadata fields.

    Falsifies if: abstract is missing/too short or creation_date is absent.
    """
    MIN_ABSTRACT_LENGTH = 50
    
    if not dataset.abstract or len(dataset.abstract) < MIN_ABSTRACT_LENGTH:
        return False, ProofObject(
            conclusion=f"VIOLATION: Abstract missing or too short ({len(dataset.abstract) if dataset.abstract else 0} chars)",
            premises=[
                f"Length: {len(dataset.abstract) if dataset.abstract else 0}",
                f"Required: >= {MIN_ABSTRACT_LENGTH}"
            ],
            rule="iso19115_abstract_required"
        )
    
    if dataset.creation_date is None:
        return False, ProofObject(
            conclusion="VIOLATION: Creation date missing",
            premises=["creation_date: None"],
            rule="iso19115_temporal_reference"
        )
    
    return True, ProofObject(
        conclusion="Required metadata fields present",
        premises=[
            f"Abstract: {len(dataset.abstract)} chars",
            f"Created: {dataset.creation_date}"
        ],
        rule="metadata_complete"
    )


def check_raster_consistency(raster: RasterDataset) -> Tuple[bool, ProofObject]:
    """Raster datasets must have consistent dimensions and cell size.
    
    Falsifies if: raster dimensions are non-positive, cell size is non-positive,
    or computed extent is invalid.
    """
    if raster.width <= 0 or raster.height <= 0:
        return False, ProofObject(
            conclusion="VIOLATION: Invalid raster dimensions",
            premises=[
                f"Width: {raster.width}",
                f"Height: {raster.height}"
            ],
            rule="raster_dimension_validity"
        )
    
    if raster.cell_size <= Fraction(0):
        return False, ProofObject(
            conclusion=f"VIOLATION: Invalid cell size {raster.cell_size}",
            premises=[f"Cell size: {raster.cell_size}"],
            rule="raster_cell_size_validity"
        )
    
    extent = raster.extent()
    if extent[0].x >= extent[1].x or extent[0].y >= extent[1].y:
        return False, ProofObject(
            conclusion="VIOLATION: Raster extent is invalid (negative or zero area)",
            premises=[f"Extent: {extent}"],
            rule="raster_extent_validity"
        )
    
    return True, ProofObject(
        conclusion="Raster dataset consistent",
        premises=[
            f"Dimensions: {raster.width}x{raster.height}",
            f"Cell size: {raster.cell_size}",
            f"Pixels: {raster.pixel_count()}"
        ],
        rule="raster_consistent"
    )
