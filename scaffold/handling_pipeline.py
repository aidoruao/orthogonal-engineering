"""
Handling Pipeline Module

Parser for GTA handling.meta files. This module provides parsing and processing
for GTA vehicle handling metadata files.

Note: This is a simplified implementation. Full GTA handling.meta parsing would
require detailed XML schema knowledge.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .canonicalizer import canonical_byte_representation
from .hasher import compute_hash
from .logger import ScaffoldLogger


class HandlingVehicle:
    """Represents a single vehicle in handling.meta."""
    
    def __init__(self, vehicle_data: dict):
        """
        Initialize vehicle from parsed data.
        
        Args:
            vehicle_data: Dictionary of vehicle attributes
        """
        self.data = vehicle_data
        self.name = vehicle_data.get('handlingName', 'unknown')
    
    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Get vehicle attribute."""
        return self.data.get(key, default)
    
    def to_dict(self) -> dict:
        """Convert vehicle to dictionary."""
        # TODO: Expand to_dict() - stub detected by Yeshua Agent
        return self.data.copy()


class HandlingMetaParser:
    """Parser for GTA handling.meta XML files."""
    
    def __init__(self, logger: Optional[ScaffoldLogger] = None):
        """
        Initialize parser.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or ScaffoldLogger()
        self.vehicles: List[HandlingVehicle] = []
    
    def parse_file(self, file_path: Union[str, Path]) -> List[HandlingVehicle]:
        """
        Parse handling.meta file.
        
        Args:
            file_path: Path to handling.meta file
            
        Returns:
            List of HandlingVehicle objects
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is invalid XML
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        self.logger.log_handling_step(
            action="parse_file",
            details={"file": str(file_path)}
        )
        
        try:
            # Get canonical bytes
            canonical_bytes = canonical_byte_representation(path)
            file_hash = compute_hash(canonical_bytes)
            
            # Parse XML
            root = ET.fromstring(canonical_bytes)
            
            # Extract vehicle entries
            # Note: Actual GTA handling.meta structure may vary
            # This is a simplified generic XML parser
            vehicles = []
            
            # Look for common handling.meta structure
            for item in root.iter():
                if 'Item' in item.tag or 'SubHandlingData' in item.tag:
                    vehicle_data = {}
                    
                    # Extract attributes
                    for child in item:
                        tag_name = child.tag.split('}')[-1]  # Remove namespace
                        vehicle_data[tag_name] = child.get('value', child.text)
                    
                    if vehicle_data:
                        vehicles.append(HandlingVehicle(vehicle_data))
            
            self.vehicles = vehicles
            
            self.logger.log_handling_step(
                action="parse_complete",
                details={
                    "file": str(file_path),
                    "hash": file_hash,
                    "vehicle_count": len(vehicles)
                }
            )
            
            return vehicles
            
        except ET.ParseError as e:
            self.logger.log_error(
                pipeline="handling",
                error=f"XML parse error: {e}",
                details={"file": str(file_path)}
            )
            raise ValueError(f"Invalid XML in {file_path}: {e}")
    
    def get_vehicle(self, name: str) -> Optional[HandlingVehicle]:
        """
        Get vehicle by name.
        
        Args:
            name: Vehicle handling name
            
        Returns:
            HandlingVehicle or None if not found
        """
        for vehicle in self.vehicles:
            if vehicle.name == name:
                return vehicle
        return None
    
    def filter_vehicles(self, filter_func) -> List[HandlingVehicle]:
        """
        Filter vehicles by custom function.
        
        Args:
            filter_func: Function that takes HandlingVehicle and returns bool
            
        Returns:
            List of filtered vehicles
        """
        return [v for v in self.vehicles if filter_func(v)]
    
    def export_vehicles(self, output_path: Union[str, Path]):
        """
        Export vehicles to JSON file.
        
        Args:
            output_path: Path to output JSON file
        """
        import json
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "vehicle_count": len(self.vehicles),
            "vehicles": [v.to_dict() for v in self.vehicles]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.log_handling_step(
            action="export_vehicles",
            details={
                "output": str(output_path),
                "count": len(self.vehicles)
            }
        )


class HandlingPipeline:
    """
    Complete handling pipeline for processing GTA handling.meta files.
    """
    
    def __init__(self, logger: Optional[ScaffoldLogger] = None):
        """
        Initialize pipeline.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or ScaffoldLogger()
        self.parser = HandlingMetaParser(logger=self.logger)
    
    def process_file(self, 
                    file_path: Union[str, Path],
                    output_dir: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """
        Process a handling.meta file through the pipeline.
        
        Args:
            file_path: Path to handling.meta file
            output_dir: Optional output directory for results
            
        Returns:
            Processing results dictionary
        """
        path = Path(file_path)
        
        self.logger.log_handling_step(
            action="pipeline_start",
            details={"file": str(file_path)}
        )
        
        try:
            # Parse file
            vehicles = self.parser.parse_file(path)
            
            # Generate hash
            canonical_bytes = canonical_byte_representation(path)
            file_hash = compute_hash(canonical_bytes)
            
            results = {
                "file": str(file_path),
                "hash": file_hash,
                "vehicle_count": len(vehicles),
                "vehicles": [v.to_dict() for v in vehicles]
            }
            
            # Export if output directory specified
            if output_dir:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Export vehicles
                output_file = output_dir / f"{path.stem}_processed.json"
                self.parser.export_vehicles(output_file)
                results["output_file"] = str(output_file)
            
            self.logger.log_handling_step(
                action="pipeline_complete",
                details=results
            )
            
            return results
            
        except Exception as e:
            self.logger.log_error(
                pipeline="handling",
                error=str(e),
                details={"file": str(file_path)}
            )
            raise
    
    def process_directory(self,
                         directory: Union[str, Path],
                         output_dir: Optional[Union[str, Path]] = None,
                         pattern: str = "*.meta") -> List[Dict[str, Any]]:
        """
        Process all handling.meta files in a directory.
        
        Args:
            directory: Directory to search
            output_dir: Optional output directory
            pattern: File pattern to match (default: *.meta)
            
        Returns:
            List of processing results
        """
        directory = Path(directory)
        results = []
        
        self.logger.log_handling_step(
            action="batch_process_start",
            details={
                "directory": str(directory),
                "pattern": pattern
            }
        )
        
        for file_path in directory.rglob(pattern):
            if file_path.is_file():
                try:
                    result = self.process_file(file_path, output_dir)
                    results.append(result)
                except Exception as e:
                    self.logger.log_error(
                        pipeline="handling",
                        error=str(e),
                        details={"file": str(file_path)}
                    )
        
        self.logger.log_handling_step(
            action="batch_process_complete",
            details={
                "directory": str(directory),
                "processed_count": len(results)
            }
        )
        
        return results
