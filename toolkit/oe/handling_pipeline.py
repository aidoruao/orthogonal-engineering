"""
Handling pipeline module for orthogonal-engineering.

Provides parsing and clamping operations for GTA handling.meta XML files.
Detects vehicle elements, applies value constraints, and logs all operations.

Author: Orthogonal Engineering System
Date: 2026-02-16
Version: 1.0.0
"""

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Union
from xml.etree import ElementTree as ET

from .logger import HandlingPipelineLogger


class VehicleClampRule:
    """Represents a clamping rule for vehicle fields."""
    
    def __init__(self, field_name: str, min_value: float = None, 
                 max_value: float = None, allowed_values: list = None):
        """
        Initialize clamp rule.
        
        Args:
            field_name: Name of the field to clamp
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            allowed_values: List of allowed discrete values
        """
        self.field_name = field_name
        self.min_value = min_value
        self.max_value = max_value
        self.allowed_values = allowed_values
    
    def apply(self, value: Any) -> Any:
        """
        Apply clamping rule to a value.
        
        Args:
            value: Original value
            
        Returns:
            Clamped value
        """
        # Handle allowed values (discrete)
        if self.allowed_values is not None:
            if value not in self.allowed_values:
                return self.allowed_values[0]  # Default to first allowed value
            return value
        
        # Handle numeric clamping
        try:
            numeric_value = float(value)
            
            if self.min_value is not None and numeric_value < self.min_value:
                return self.min_value
            
            if self.max_value is not None and numeric_value > self.max_value:
                return self.max_value
            
            return numeric_value
        except (ValueError, TypeError):
            return value


class HandlingMetaParser:
    """Parser for GTA handling.meta XML files."""
    
    def __init__(self, file_path: Union[str, Path]):
        """
        Initialize parser.
        
        Args:
            file_path: Path to handling.meta XML file
        """
        self.file_path = Path(file_path)
        self.tree = None
        self.root = None
        self.vehicles: List[ET.Element] = []
        
        if self.file_path.exists():
            self._parse()
    
    def _parse(self):
        """Parse the XML file."""
        self.tree = ET.parse(self.file_path)
        self.root = self.tree.getroot()
        
        # Find all vehicle elements
        # Common GTA handling.meta structure has <Item> elements under <InitDatas>
        for item in self.root.iter('Item'):
            # Check if this is a vehicle item (has handlingName or similar)
            if item.find('handlingName') is not None or item.find('HandlingName') is not None:
                self.vehicles.append(item)
    
    def get_vehicle_count(self) -> int:
        """Get number of vehicles in file."""
        return len(self.vehicles)
    
    def get_vehicle_data(self, vehicle_element: ET.Element) -> Dict[str, Any]:
        """
        Extract vehicle data as dictionary.
        
        Args:
            vehicle_element: Vehicle XML element
            
        Returns:
            Dictionary of vehicle properties
        """
        data = {}
        for child in vehicle_element:
            # Handle both text and attributes
            if child.text and child.text.strip():
                data[child.tag] = child.text.strip()
            elif 'value' in child.attrib:
                data[child.tag] = child.attrib['value']
        return data
    
    def get_all_vehicles(self) -> List[Dict[str, Any]]:
        """
        Get all vehicles as list of dictionaries.
        
        Returns:
            List of vehicle data dictionaries
        """
        return [self.get_vehicle_data(v) for v in self.vehicles]


class HandlingPipeline:
    """Pipeline for processing handling.meta files with clamping."""
    
    def __init__(self, file_path: Union[str, Path], logger: HandlingPipelineLogger = None):
        """
        Initialize handling pipeline.
        
        Args:
            file_path: Path to handling.meta file
            logger: Optional logger instance
        """
        self.file_path = Path(file_path)
        self.parser = HandlingMetaParser(file_path)
        self.logger = logger or HandlingPipelineLogger()
        self.clamp_rules: Dict[str, VehicleClampRule] = {}
    
    def add_clamp_rule(self, rule: VehicleClampRule):
        """
        Add a clamping rule.
        
        Args:
            rule: VehicleClampRule to add
        """
        self.clamp_rules[rule.field_name] = rule
    
    def add_default_clamp_rules(self):
        """Add common default clamping rules for GTA handling."""
        # Example rules for common GTA handling fields
        self.add_clamp_rule(VehicleClampRule('fMass', min_value=0.0, max_value=50000.0))
        self.add_clamp_rule(VehicleClampRule('fInitialDragCoeff', min_value=0.0, max_value=100.0))
        self.add_clamp_rule(VehicleClampRule('fDriveInertia', min_value=0.0, max_value=10.0))
        self.add_clamp_rule(VehicleClampRule('fClutchChangeRateScaleUpShift', min_value=0.0, max_value=10.0))
        self.add_clamp_rule(VehicleClampRule('fClutchChangeRateScaleDownShift', min_value=0.0, max_value=10.0))
        self.add_clamp_rule(VehicleClampRule('fBrakeForce', min_value=0.0, max_value=10.0))
    
    def process(self, dry_run: bool = False, backup: bool = True) -> Dict[str, Any]:
        """
        Process handling.meta file with clamping.
        
        Args:
            dry_run: If True, don't modify file, just log what would change
            backup: If True, create backup before modifying
            
        Returns:
            Dictionary with processing results
        """
        # Log parsing start
        self.logger.log_parsing_start(str(self.file_path))
        
        # Create backup if needed
        if backup and not dry_run:
            backup_path = self.file_path.with_suffix('.meta.backup')
            shutil.copy2(self.file_path, backup_path)
        
        # Track changes
        changes_made = 0
        total_fields = 0
        
        # Process each vehicle
        for vehicle in self.parser.vehicles:
            vehicle_name = self._get_vehicle_name(vehicle)
            
            # Apply clamp rules to each field
            for field_name, rule in self.clamp_rules.items():
                element = vehicle.find(field_name)
                if element is not None:
                    total_fields += 1
                    old_value = element.text if element.text else element.get('value', '')
                    
                    # Apply clamping
                    new_value = rule.apply(old_value)
                    
                    # Check if value changed
                    if str(old_value) != str(new_value):
                        changes_made += 1
                        
                        # Log the clamp
                        self.logger.log_vehicle_clamp(
                            vehicle_name=vehicle_name,
                            field=field_name,
                            old_value=old_value,
                            new_value=new_value,
                            dry_run=dry_run
                        )
                        
                        # Apply change if not dry run
                        if not dry_run:
                            if element.text:
                                element.text = str(new_value)
                            else:
                                element.set('value', str(new_value))
        
        # Write modified XML if not dry run
        if not dry_run and changes_made > 0:
            self.parser.tree.write(self.file_path, encoding='utf-8', xml_declaration=True)
        
        # Log completion
        self.logger.log_parsing_complete(
            str(self.file_path),
            self.parser.get_vehicle_count()
        )
        
        return {
            'vehicles_processed': self.parser.get_vehicle_count(),
            'total_fields_checked': total_fields,
            'changes_made': changes_made,
            'dry_run': dry_run,
            'backup_created': backup and not dry_run
        }
    
    def _get_vehicle_name(self, vehicle_element: ET.Element) -> str:
        """
        Extract vehicle name from element.
        
        Args:
            vehicle_element: Vehicle XML element
            
        Returns:
            Vehicle name string
        """
        # Try common name fields
        for name_field in ['handlingName', 'HandlingName', 'modelName', 'ModelName']:
            element = vehicle_element.find(name_field)
            if element is not None:
                return element.text if element.text else element.get('value', 'unknown')
        
        return 'unknown'
    
    def restore_from_backup(self) -> bool:
        """
        Restore handling.meta from backup.
        
        Returns:
            True if restore successful
        """
        backup_path = self.file_path.with_suffix('.meta.backup')
        if backup_path.exists():
            shutil.copy2(backup_path, self.file_path)
            return True
        return False


import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from xml.etree import ElementTree as ET


class HandlingMetaParser:
    """Parser for GTA handling.meta XML files."""
    
    def __init__(self):
        self.vehicles: List[Dict[str, Any]] = []
    
    def parse_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Parse a handling.meta file.
        
        Args:
            file_path: Path to handling.meta file
            
        Returns:
            List of vehicle handling data
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # GTA handling.meta typically has <CHandlingData> elements
            for item in root.findall('.//Item'):
                vehicle_data = self._parse_vehicle_item(item)
                if vehicle_data:
                    self.vehicles.append(vehicle_data)
            
            return self.vehicles
            
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse handling.meta: {e}")
    
    def _parse_vehicle_item(self, item: ET.Element) -> Optional[Dict[str, Any]]:
        """
        Parse a single vehicle item from handling.meta.
        
        Args:
            item: XML element for vehicle
            
        Returns:
            Vehicle data dictionary
        """
        vehicle = {}
        
        # Extract handlingName
        name_elem = item.find('handlingName')
        if name_elem is not None:
            vehicle['handlingName'] = name_elem.text
        else:
            # Skip items without handlingName
            return None
        
        # Extract common handling properties
        properties = [
            'fMass',
            'fInitialDragCoeff',
            'fPercentSubmerged',
            'vecCentreOfMassOffset',
            'vecInertiaMultiplier',
            'fDriveBiasFront',
            'nInitialDriveGears',
            'fInitialDriveForce',
            'fDriveInertia',
            'fClutchChangeRateScaleUpShift',
            'fClutchChangeRateScaleDownShift',
            'fInitialDriveMaxFlatVel',
            'fBrakeForce',
            'fBrakeBiasFront',
            'fHandBrakeForce',
            'fSteeringLock',
            'fTractionCurveMax',
            'fTractionCurveMin',
            'fTractionCurveLateral',
            'fTractionSpringDeltaMax',
            'fLowSpeedTractionLossMult',
            'fCamberStiffnesss',
            'fTractionBiasFront',
            'fTractionLossMult',
            'fSuspensionForce',
            'fSuspensionCompDamp',
            'fSuspensionReboundDamp',
            'fSuspensionUpperLimit',
            'fSuspensionLowerLimit',
            'fSuspensionRaise',
            'fSuspensionBiasFront',
            'fAntiRollBarForce',
            'fAntiRollBarBiasFront',
            'fRollCentreHeightFront',
            'fRollCentreHeightRear',
            'fCollisionDamageMult',
            'fWeaponDamageMult',
            'fDeformationDamageMult',
            'fEngineDamageMult',
            'fPetrolTankVolume',
            'fOilVolume',
        ]
        
        for prop in properties:
            elem = item.find(prop)
            if elem is not None:
                # Try to parse as number
                value = elem.text
                if value:
                    try:
                        # Try float first
                        if '.' in value:
                            vehicle[prop] = float(value)
                        else:
                            vehicle[prop] = int(value)
                    except ValueError:
                        # Keep as string if not a number
                        vehicle[prop] = value
        
        # Extract vector properties (special handling)
        vector_props = ['vecCentreOfMassOffset', 'vecInertiaMultiplier']
        for prop in vector_props:
            elem = item.find(prop)
            if elem is not None:
                vector_value = self._parse_vector(elem)
                if vector_value:
                    vehicle[prop] = vector_value
        
        return vehicle
    
    def _parse_vector(self, elem: ET.Element) -> Optional[Dict[str, float]]:
        """
        Parse a vector element with x, y, z attributes.
        
        Args:
            elem: XML element with x, y, z attributes
            
        Returns:
            Dictionary with x, y, z values
        """
        vector = {}
        
        for axis in ['x', 'y', 'z']:
            value = elem.get(axis)
            if value:
                try:
                    vector[axis] = float(value)
                except ValueError:
                    pass
        
        return vector if vector else None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert parsed data to dictionary.
        
        Returns:
            Dictionary with all vehicle data
        """
        return {
            'vehicles': self.vehicles,
            'count': len(self.vehicles)
        }
    
    def validate(self) -> List[str]:
        """
        Validate parsed handling data.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check for duplicate handlingNames
        names = [v.get('handlingName') for v in self.vehicles if 'handlingName' in v]
        duplicates = [name for name in names if names.count(name) > 1]
        if duplicates:
            errors.append(f"Duplicate handlingNames found: {set(duplicates)}")
        
        # Validate critical properties exist
        for i, vehicle in enumerate(self.vehicles):
            name = vehicle.get('handlingName', f'vehicle_{i}')
            
            if 'fMass' not in vehicle:
                errors.append(f"{name}: Missing required property 'fMass'")
            
            if 'fInitialDriveForce' not in vehicle:
                errors.append(f"{name}: Missing required property 'fInitialDriveForce'")
        
        return errors


def parse_handling_meta(file_path: Path) -> Dict[str, Any]:
    """
    Parse a GTA handling.meta file.
    
    Args:
        file_path: Path to handling.meta file
        
    Returns:
        Dictionary with parsed data
    """
    parser = HandlingMetaParser()
    parser.parse_file(file_path)
    return parser.to_dict()
