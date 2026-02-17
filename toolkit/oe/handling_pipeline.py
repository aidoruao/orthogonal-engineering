"""
Handling pipeline module for parsing GTA handling.meta files.

Provides parsing and validation for GTA handling metadata.
"""

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
