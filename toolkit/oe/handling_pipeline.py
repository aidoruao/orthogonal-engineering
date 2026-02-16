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
