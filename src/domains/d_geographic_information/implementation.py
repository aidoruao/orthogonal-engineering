"""D_GEOGRAPHIC_INFORMATION implementation — GIS & Spatial Data

Layer: 4 (Institutional - Technical)
CardinalStrength: PREDICATIVE

Standards:
- ISO 19115 (geographic metadata)
- OGC Simple Features
- EPSG coordinate reference systems
- FGDC metadata standard
- INSPIRE (EU spatial data infrastructure)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum, auto
from datetime import datetime
from fractions import Fraction


class GeometryType(Enum):
    """OGC Simple Feature geometry types."""
    POINT = auto()
    LINESTRING = auto()
    POLYGON = auto()
    MULTIPOINT = auto()
    MULTILINESTRING = auto()
    MULTIPOLYGON = auto()
    GEOMETRYCOLLECTION = auto()


class SpatialDataTheme(Enum):
    """INSPIRE spatial data themes."""
    ADMINISTRATIVE_UNITS = auto()
    ADDRESSES = auto()
    CADASTRE = auto()
    ELEVATION = auto()
    GEOLOGY = auto()
    HYDROGRAPHY = auto()
    PROTECTED_SITES = auto()
    TRANSPORT_NETWORKS = auto()


@dataclass(frozen=True)
class Coordinate:
    """2D or 3D coordinate in a CRS."""
    x: Fraction  # Longitude or Easting
    y: Fraction  # Latitude or Northing
    z: Optional[Fraction] = None  # Elevation
    
    def to_2d(self) -> Tuple[Fraction, Fraction]:
        """Project to 2D."""
        return (self.x, self.y)
    
    def dimension(self) -> int:
        """2 or 3."""
        return 3 if self.z is not None else 2


@dataclass
class CoordinateReferenceSystem:
    """CRS with EPSG code."""
    epsg_code: int
    name: str
    
    # Properties
    geographic: bool  # True for lat/lon, False for projected
    unit: str  # meters, degrees, feet
    
    # Bounds (if known)
    valid_bounds: Optional[Tuple[Coordinate, Coordinate]] = None
    
    def is_valid_coordinate(self, coord: Coordinate) -> bool:
        """Check if coordinate within CRS domain."""
        if self.valid_bounds is None:
            return True
        
        min_coord, max_coord = self.valid_bounds
        if coord.x < min_coord.x or coord.x > max_coord.x:
            return False
        if coord.y < min_coord.y or coord.y > max_coord.y:
            return False
        return True


@dataclass
class Geometry:
    """Geometric feature with spatial attributes."""
    geometry_id: str
    geometry_type: GeometryType
    coordinates: List[Coordinate]
    crs: CoordinateReferenceSystem
    
    # Bounding box (computed)
    bbox_min: Optional[Coordinate] = None
    bbox_max: Optional[Coordinate] = None
    
    def compute_bbox(self) -> None:
        """Calculate bounding box from coordinates."""
        if not self.coordinates:
            return
        
        xs = [c.x for c in self.coordinates]
        ys = [c.y for c in self.coordinates]
        
        self.bbox_min = Coordinate(min(xs), min(ys))
        self.bbox_max = Coordinate(max(xs), max(ys))
    
    def intersects(self, other: Geometry) -> bool:
        """Bounding box intersection test."""
        if self.bbox_min is None or other.bbox_min is None:
            return False
        
        # Separating axis test for AABB
        if self.bbox_max.x < other.bbox_min.x or self.bbox_min.x > other.bbox_max.x:
            return False
        if self.bbox_max.y < other.bbox_min.y or self.bbox_min.y > other.bbox_max.y:
            return False
        return True
    
    def vertex_count(self) -> int:
        """Number of vertices."""
        return len(self.coordinates)


@dataclass
class SpatialDataset:
    """Collection of geographic features."""
    dataset_id: str
    title: str
    theme: SpatialDataTheme
    
    # CRS
    crs: CoordinateReferenceSystem
    
    # Features
    features: List[Geometry] = field(default_factory=list)
    
    # Metadata (ISO 19115)
    abstract: str = ""
    purpose: str = ""
    creation_date: Optional[datetime] = None
    update_frequency: str = ""
    
    # Quality
    positional_accuracy: Optional[Fraction] = None  # meters
    completeness: Optional[Fraction] = None  # 0-1
    
    def feature_count(self) -> int:
        """Total features in dataset."""
        return len(self.features)
    
    def total_vertices(self) -> int:
        """Sum of all vertices."""
        return sum(f.vertex_count() for f in self.features)
    
    def compute_extent(self) -> Optional[Tuple[Coordinate, Coordinate]]:
        """Overall bounding box."""
        if not self.features:
            return None
        
        all_coords = []
        for f in self.features:
            if f.bbox_min and f.bbox_max:
                all_coords.extend([f.bbox_min, f.bbox_max])
        
        if not all_coords:
            return None
        
        xs = [c.x for c in all_coords]
        ys = [c.y for c in all_coords]
        
        return (
            Coordinate(min(xs), min(ys)),
            Coordinate(max(xs), max(ys))
        )
    
    def crs_consistency(self) -> bool:
        """All features use dataset CRS."""
        return all(f.crs.epsg_code == self.crs.epsg_code for f in self.features)


@dataclass
class TopologyRule:
    """GIS topology validation rule."""
    rule_type: str  # "must_not_overlap", "must_be_covered_by", etc.
    feature_class_a: str
    feature_class_b: Optional[str] = None
    
    def validate(self, features_a: List[Geometry], features_b: Optional[List[Geometry]] = None) -> List[str]:
        """Check topology and return errors."""
        errors = []
        
        if self.rule_type == "must_not_overlap":
            # Polygons cannot overlap
            for i, f1 in enumerate(features_a):
                for f2 in features_a[i+1:]:
                    if f1.intersects(f2):
                        errors.append(f"Overlap: {f1.geometry_id} and {f2.geometry_id}")
        
        elif self.rule_type == "must_be_covered_by" and features_b:
            # Features A must be covered by features B
            for fa in features_a:
                covered = any(fa.intersects(fb) for fb in features_b)
                if not covered:
                    errors.append(f"Not covered: {fa.geometry_id}")
        
        return errors


@dataclass
class RasterDataset:
    """Raster/grid spatial data."""
    raster_id: str
    width: int
    height: int
    cell_size: Fraction
    crs: CoordinateReferenceSystem
    origin: Coordinate  # Upper-left corner
    
    nodata_value: Optional[Fraction] = None
    
    def pixel_count(self) -> int:
        """Total pixels."""
        return self.width * self.height
    
    def extent(self) -> Tuple[Coordinate, Coordinate]:
        """Bounding box in CRS units."""
        min_x = self.origin.x
        max_y = self.origin.y
        max_x = min_x + Fraction(self.width) * self.cell_size
        min_y = max_y - Fraction(self.height) * self.cell_size
        
        return (
            Coordinate(min_x, min_y),
            Coordinate(max_x, max_y)
        )


@dataclass
class GISCheker:
    """Checker for GIS data quality and standards."""
    vector_datasets: List[SpatialDataset] = field(default_factory=list)
    raster_datasets: List[RasterDataset] = field(default_factory=list)
    topology_rules: List[TopologyRule] = field(default_factory=list)
    
    def datasets_missing_metadata(self) -> List[SpatialDataset]:
        """Datasets without required ISO 19115 fields."""
        return [
            d for d in self.vector_datasets
            if not d.abstract or not d.creation_date
        ]
    
    def crs_mismatches(self) -> List[Tuple[str, str]]:
        """Features with CRS different from their dataset."""
        mismatches = []
        for ds in self.vector_datasets:
            for f in ds.features:
                if f.crs.epsg_code != ds.crs.epsg_code:
                    mismatches.append((ds.dataset_id, f.geometry_id))
        return mismatches
    
    def topology_errors(self) -> Dict[str, List[str]]:
        """Run all topology rules and return errors."""
        errors = {}
        # Simplified: would organize features by class
        return errors
