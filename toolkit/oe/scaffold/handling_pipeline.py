"""
Parser for GTA handling.meta files.

Provides structured parsing and canonicalization of handling.meta XML files
from Grand Theft Auto games for deterministic auditing.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, field

from .canonicalizer import canonical_xml_bytes


@dataclass
class HandlingEntry:
    """Single vehicle handling entry from handling.meta."""
    name: str
    mass: Optional[float] = None
    drag_multiplier: Optional[float] = None
    centre_of_mass: Optional[List[float]] = field(default_factory=list)
    inertia_multiplier: Optional[Dict[str, float]] = field(default_factory=dict)
    initial_drag_coeff: Optional[float] = None
    raw_attributes: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export."""
        return {
            'name': self.name,
            'mass': self.mass,
            'drag_multiplier': self.drag_multiplier,
            'centre_of_mass': self.centre_of_mass,
            'inertia_multiplier': self.inertia_multiplier,
            'initial_drag_coeff': self.initial_drag_coeff,
            'raw_attributes': self.raw_attributes,
        }


class HandlingMetaParser:
    """
    Parser for GTA handling.meta XML files.
    
    Provides:
    - Structured parsing of vehicle handling data
    - Deterministic canonicalization
    - Validation and error reporting
    """
    
    def __init__(self):
        """Initialize parser."""
        self.entries: List[HandlingEntry] = []
        self.raw_xml: Optional[bytes] = None
        self.canonical_xml: Optional[bytes] = None
    
    def parse_file(self, file_path: Union[str, Path]) -> List[HandlingEntry]:
        """
        Parse a handling.meta file.
        
        Args:
            file_path: Path to handling.meta file
            
        Returns:
            List of HandlingEntry objects
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read and canonicalize
        self.raw_xml = path.read_bytes()
        
        # Try to canonicalize (may fail for invalid XML)
        try:
            self.canonical_xml = canonical_xml_bytes(self.raw_xml)
        except Exception as e:
            raise ValueError(f"Invalid XML in {file_path}: {e}")
        
        # Parse XML
        try:
            root = ET.fromstring(self.canonical_xml)
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML in {file_path}: {e}")
        
        # Extract handling entries
        self.entries = []
        
        # Look for typical handling.meta structure
        # Format can vary between GTA versions:
        # - Some use <Item> elements directly
        # - Others use <HandlingData> containers
        # We parse both patterns; validation will catch duplicates
        
        for item in root.findall('.//Item'):
            entry = self._parse_item(item)
            if entry:
                self.entries.append(entry)
        
        # Alternative structure - only process if no items found
        # This prevents double-parsing if both patterns exist in the same file
        if not self.entries:
            for item in root.findall('.//HandlingData'):
                entry = self._parse_item(item)
                if entry:
                    self.entries.append(entry)
        
        return self.entries
    
    def _parse_item(self, item: ET.Element) -> Optional[HandlingEntry]:
        """
        Parse a single handling entry item.
        
        Args:
            item: XML element
            
        Returns:
            HandlingEntry or None
        """
        # Try to get vehicle name
        name = item.get('name') or item.get('handlingName')
        
        if not name:
            # Try to find name in child elements
            name_elem = item.find('.//handlingName')
            if name_elem is not None and name_elem.text:
                name = name_elem.text.strip()
        
        if not name:
            return None
        
        # Initialize entry
        entry = HandlingEntry(name=name)
        
        # Parse common attributes
        self._parse_mass(item, entry)
        self._parse_drag_multiplier(item, entry)
        self._parse_centre_of_mass(item, entry)
        self._parse_inertia_multiplier(item, entry)
        self._parse_initial_drag_coeff(item, entry)
        
        # Store all raw attributes
        entry.raw_attributes = dict(item.attrib)
        
        return entry
    
    def _parse_mass(self, item: ET.Element, entry: HandlingEntry) -> None:
        """Parse mass attribute."""
        mass_text = item.get('fMass') or item.findtext('.//fMass')
        if mass_text:
            try:
                entry.mass = float(mass_text)
            except ValueError:
                pass
    
    def _parse_drag_multiplier(self, item: ET.Element, entry: HandlingEntry) -> None:
        """Parse drag multiplier attribute."""
        drag_text = item.get('fDragMult') or item.findtext('.//fDragMult')
        if drag_text:
            try:
                entry.drag_multiplier = float(drag_text)
            except ValueError:
                pass
    
    def _parse_centre_of_mass(self, item: ET.Element, entry: HandlingEntry) -> None:
        """Parse centre of mass vector."""
        com_text = item.get('vecCentreOfMassOffset') or item.findtext('.//vecCentreOfMassOffset')
        if com_text:
            try:
                # Parse as space or comma separated floats
                parts = com_text.replace(',', ' ').split()
                entry.centre_of_mass = [float(p) for p in parts if p]
            except ValueError:
                pass
    
    def _parse_inertia_multiplier(self, item: ET.Element, entry: HandlingEntry) -> None:
        """Parse inertia multiplier vector."""
        inertia_text = item.get('vecInertiaMultiplier') or item.findtext('.//vecInertiaMultiplier')
        if inertia_text:
            try:
                parts = inertia_text.replace(',', ' ').split()
                floats = [float(p) for p in parts if p]
                if len(floats) >= 3:
                    entry.inertia_multiplier = {
                        'x': floats[0],
                        'y': floats[1],
                        'z': floats[2]
                    }
            except ValueError:
                pass
    
    def _parse_initial_drag_coeff(self, item: ET.Element, entry: HandlingEntry) -> None:
        """Parse initial drag coefficient."""
        drag_text = item.get('fInitialDragCoeff') or item.findtext('.//fInitialDragCoeff')
        if drag_text:
            try:
                entry.initial_drag_coeff = float(drag_text)
            except ValueError:
                pass
    
    def get_entry_by_name(self, name: str) -> Optional[HandlingEntry]:
        """
        Get handling entry by vehicle name.
        
        Args:
            name: Vehicle name
            
        Returns:
            HandlingEntry or None
        """
        for entry in self.entries:
            if entry.name == name:
                return entry
        return None
    
    def validate(self) -> List[str]:
        """
        Validate parsed handling entries.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not self.entries:
            errors.append("No handling entries found")
        
        # Check for duplicate names
        names = [e.name for e in self.entries]
        duplicates = [n for n in names if names.count(n) > 1]
        if duplicates:
            errors.append(f"Duplicate vehicle names: {set(duplicates)}")
        
        # Validate individual entries
        for entry in self.entries:
            if entry.mass is not None and entry.mass <= 0:
                errors.append(f"{entry.name}: Mass must be positive")
            
            if entry.drag_multiplier is not None and entry.drag_multiplier < 0:
                errors.append(f"{entry.name}: Drag multiplier must be non-negative")
        
        return errors


# Unit tests and examples
def _test_handling_parser():
    """Test handling.meta parser."""
    import tempfile
    
    # Create test handling.meta
    test_xml = """<?xml version="1.0" encoding="UTF-8"?>
<CHandlingDataMgr>
    <HandlingData>
        <Item name="ADDER" fMass="1400.0" fDragMult="0.35" vecCentreOfMassOffset="0.0 0.0 0.0">
            <fInitialDragCoeff>10.5</fInitialDragCoeff>
        </Item>
        <Item name="BULLET" fMass="1200.0" fDragMult="0.30">
            <vecInertiaMultiplier>1.2 1.0 1.4</vecInertiaMultiplier>
        </Item>
    </HandlingData>
</CHandlingDataMgr>
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.meta', delete=False) as f:
        f.write(test_xml)
        temp_path = f.name
    
    try:
        # Parse
        parser = HandlingMetaParser()
        entries = parser.parse_file(temp_path)
        
        assert len(entries) == 2
        assert entries[0].name == "ADDER"
        assert entries[0].mass == 1400.0
        assert entries[1].name == "BULLET"
        
        # Test lookup
        adder = parser.get_entry_by_name("ADDER")
        assert adder is not None
        assert adder.mass == 1400.0
        
        # Test validation
        errors = parser.validate()
        assert len(errors) == 0
        
        print("✓ Handling parser tests passed")
    
    finally:
        import os
        os.unlink(temp_path)


if __name__ == "__main__":
    _test_handling_parser()
    print("\n✓ All handling_pipeline tests passed")
