"""
GTA Handling.meta Pipeline Module

Robust parser for GTA handling.meta files containing CHandlingData Item elements.
Extracts vehicle handling data and provides clamp/validation pipeline.
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Union, List, Dict, Optional, Any
from .logger import ScaffoldLogger


class HandlingDataItem:
    """Represents a single CHandlingData Item element."""
    
    def __init__(self, name: str, data: Dict[str, Any]):
        self.name = name
        self.data = data
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "handlingName": self.name,
            **self.data
        }


class HandlingMetaParser:
    """Parser for GTA handling.meta files."""
    
    def __init__(self, logger: Optional[ScaffoldLogger] = None):
        """
        Initialize parser.
        
        Args:
            logger: Optional logger for pipeline events
        """
        self.logger = logger
        self.items = []
    
    def parse_file(self, file_path: Union[str, Path]) -> List[HandlingDataItem]:
        """
        Parse handling.meta file.
        
        Args:
            file_path: Path to handling.meta file
            
        Returns:
            List of HandlingDataItem objects
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is malformed
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if self.logger:
            self.logger.log_start("parse_handling_meta", file=str(file_path))
        
        try:
            # Read file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Parse XML
            root = ET.fromstring(content)
            
            # Find all Item elements
            items = []
            
            # Look for CHandlingData Items
            for item in root.findall(".//Item[@type='CHandlingData']"):
                handling_item = self._parse_item(item)
                if handling_item:
                    items.append(handling_item)
            
            # Also check for Items without type attribute
            for item in root.findall(".//Item"):
                if item.get("type") != "CHandlingData":
                    # Try to parse anyway - might have handlingName
                    handling_item = self._parse_item(item)
                    if handling_item and handling_item not in items:
                        items.append(handling_item)
            
            self.items = items
            
            if self.logger:
                self.logger.log_complete("parse_handling_meta", 
                                       items_found=len(items))
            
            return items
            
        except ET.ParseError as e:
            error_msg = f"XML parse error: {e}"
            if self.logger:
                self.logger.log_error("parse_handling_meta", error_msg)
            raise ValueError(error_msg)
    
    def _parse_item(self, item_element: ET.Element) -> Optional[HandlingDataItem]:
        """
        Parse a single Item element.
        
        Args:
            item_element: XML Element for Item
            
        Returns:
            HandlingDataItem or None if no handlingName found
        """
        # Extract handlingName
        name_elem = item_element.find("handlingName")
        if name_elem is None or not name_elem.text:
            return None
        
        handling_name = name_elem.text.strip()
        
        # Extract all child elements as data
        data = {}
        for child in item_element:
            tag = child.tag
            
            # Handle different value types
            if child.get("value"):
                # Attribute-based value
                data[tag] = child.get("value")
            elif child.text:
                # Text-based value
                data[tag] = child.text.strip()
            elif len(child) > 0:
                # Nested elements - store as dict
                data[tag] = self._parse_nested(child)
            else:
                # Empty element
                data[tag] = None
        
        return HandlingDataItem(handling_name, data)
    
    def _parse_nested(self, element: ET.Element) -> dict:
        """Parse nested XML elements."""
        result = {}
        for child in element:
            if child.get("value"):
                result[child.tag] = child.get("value")
            elif child.text:
                result[child.tag] = child.text.strip()
            else:
                result[child.tag] = self._parse_nested(child)
        return result
    
    def get_vehicle_names(self) -> List[str]:
        """Get list of vehicle handling names."""
        return [item.name for item in self.items]
    
    def get_item_by_name(self, name: str) -> Optional[HandlingDataItem]:
        """Get handling item by vehicle name."""
        for item in self.items:
            if item.name == name:
                return item
        return None


class HandlingClampPipeline:
    """
    Pipeline for clamping/validating GTA handling values.
    
    Ensures values are within acceptable ranges to prevent game crashes.
    """
    
    # Example clamps - these would be tuned for actual GTA handling limits
    CLAMPS = {
        "fMass": (50.0, 50000.0),          # Mass in kg
        "fInitialDragCoeff": (0.0, 100.0),  # Drag coefficient
        "fDriveInertia": (0.01, 10.0),      # Drive inertia
        "fClutchChangeRateScaleUpShift": (0.1, 10.0),
        "fClutchChangeRateScaleDownShift": (0.1, 10.0),
    }
    
    def __init__(self, logger: Optional[ScaffoldLogger] = None):
        self.logger = logger
        self.violations = []
    
    def clamp_item(self, item: HandlingDataItem, apply: bool = False) -> Dict[str, Any]:
        """
        Clamp values in handling item.
        
        Args:
            item: HandlingDataItem to clamp
            apply: If True, modify item in place; if False, just report
            
        Returns:
            Dictionary of clamped values and violations
        """
        if self.logger:
            self.logger.log_start("clamp_handling", vehicle=item.name, 
                                apply=apply)
        
        violations = []
        clamped_values = {}
        
        for field, (min_val, max_val) in self.CLAMPS.items():
            if field in item.data:
                try:
                    value = float(item.data[field])
                    
                    if value < min_val or value > max_val:
                        clamped = max(min_val, min(max_val, value))
                        violations.append({
                            "field": field,
                            "original": value,
                            "clamped": clamped,
                            "min": min_val,
                            "max": max_val
                        })
                        clamped_values[field] = clamped
                        
                        if apply:
                            item.data[field] = str(clamped)
                            
                except (ValueError, TypeError):
                    # Not a numeric value, skip
                    pass
        
        if self.logger:
            self.logger.log_complete("clamp_handling", 
                                   vehicle=item.name,
                                   violations_found=len(violations))
        
        self.violations.extend(violations)
        
        return {
            "vehicle": item.name,
            "violations": violations,
            "clamped_values": clamped_values
        }
    
    def clamp_all(self, items: List[HandlingDataItem], apply: bool = False) -> List[Dict[str, Any]]:
        """
        Clamp all items in list.
        
        Args:
            items: List of HandlingDataItem objects
            apply: If True, modify items in place
            
        Returns:
            List of clamp results
        """
        results = []
        for item in items:
            result = self.clamp_item(item, apply=apply)
            results.append(result)
        
        return results


def create_sample_handling_meta(output_path: Union[str, Path]) -> None:
    """
    Create a sample handling.meta file for testing.
    
    Args:
        output_path: Path to output file
    """
    sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
<CHandlingDataMgr>
  <HandlingData>
    <Item type="CHandlingData">
      <handlingName>ADDER</handlingName>
      <fMass value="1800.0" />
      <fInitialDragCoeff value="8.5" />
      <fDriveInertia value="1.0" />
      <fClutchChangeRateScaleUpShift value="2.0" />
      <fClutchChangeRateScaleDownShift value="2.0" />
      <fInitialDriveMaxFlatVel value="165.0" />
      <fBrakeForce value="1.2" />
      <fBrakeBiasFront value="0.5" />
      <fHandBrakeForce value="0.8" />
      <fSteeringLock value="40.0" />
      <fTractionCurveMax value="2.55" />
      <fTractionCurveMin value="2.4" />
    </Item>
    <Item type="CHandlingData">
      <handlingName>ZENTORNO</handlingName>
      <fMass value="1650.0" />
      <fInitialDragCoeff value="7.5" />
      <fDriveInertia value="0.95" />
      <fClutchChangeRateScaleUpShift value="2.2" />
      <fClutchChangeRateScaleDownShift value="2.2" />
      <fInitialDriveMaxFlatVel value="170.0" />
      <fBrakeForce value="1.3" />
      <fBrakeBiasFront value="0.52" />
      <fHandBrakeForce value="0.7" />
      <fSteeringLock value="38.0" />
      <fTractionCurveMax value="2.65" />
      <fTractionCurveMin value="2.5" />
    </Item>
  </HandlingData>
</CHandlingDataMgr>
"""
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(sample_xml)
