"""
Unit tests for handling_pipeline module.
"""

import tempfile
import pytest
from pathlib import Path

from toolkit.oe.scaffold.handling_pipeline import HandlingMetaParser, HandlingEntry


def test_handling_entry_to_dict():
    """Test HandlingEntry conversion to dict."""
    entry = HandlingEntry(
        name="ADDER",
        mass=1400.0,
        drag_multiplier=0.35,
        centre_of_mass=[0.0, 0.0, 0.0]
    )
    
    result = entry.to_dict()
    
    assert result['name'] == "ADDER"
    assert result['mass'] == 1400.0
    assert result['drag_multiplier'] == 0.35
    assert result['centre_of_mass'] == [0.0, 0.0, 0.0]


def test_parser_initialization():
    """Test parser initialization."""
    parser = HandlingMetaParser()
    
    assert parser.entries == []
    assert parser.raw_xml is None
    assert parser.canonical_xml is None


def test_parse_simple_handling_meta():
    """Test parsing simple handling.meta file."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<CHandlingDataMgr>
    <HandlingData>
        <Item name="ADDER" fMass="1400.0" fDragMult="0.35"/>
    </HandlingData>
</CHandlingDataMgr>
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.meta', delete=False) as f:
        f.write(xml_content)
        temp_path = f.name
    
    try:
        parser = HandlingMetaParser()
        entries = parser.parse_file(temp_path)
        
        assert len(entries) == 1
        assert entries[0].name == "ADDER"
        assert entries[0].mass == 1400.0
        assert entries[0].drag_multiplier == 0.35
    finally:
        Path(temp_path).unlink()


def test_parse_multiple_vehicles():
    """Test parsing multiple vehicle entries."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<CHandlingDataMgr>
    <HandlingData>
        <Item name="ADDER" fMass="1400.0"/>
        <Item name="BULLET" fMass="1200.0"/>
        <Item name="CHEETAH" fMass="1300.0"/>
    </HandlingData>
</CHandlingDataMgr>
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.meta', delete=False) as f:
        f.write(xml_content)
        temp_path = f.name
    
    try:
        parser = HandlingMetaParser()
        entries = parser.parse_file(temp_path)
        
        assert len(entries) == 3
        assert entries[0].name == "ADDER"
        assert entries[1].name == "BULLET"
        assert entries[2].name == "CHEETAH"
    finally:
        Path(temp_path).unlink()


def test_parse_centre_of_mass():
    """Test parsing centre of mass vector."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<CHandlingDataMgr>
    <HandlingData>
        <Item name="TEST" vecCentreOfMassOffset="0.5 -0.2 0.1"/>
    </HandlingData>
</CHandlingDataMgr>
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.meta', delete=False) as f:
        f.write(xml_content)
        temp_path = f.name
    
    try:
        parser = HandlingMetaParser()
        entries = parser.parse_file(temp_path)
        
        assert entries[0].centre_of_mass == [0.5, -0.2, 0.1]
    finally:
        Path(temp_path).unlink()


def test_parse_inertia_multiplier():
    """Test parsing inertia multiplier."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<CHandlingDataMgr>
    <HandlingData>
        <Item name="TEST" vecInertiaMultiplier="1.2 1.0 1.4"/>
    </HandlingData>
</CHandlingDataMgr>
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.meta', delete=False) as f:
        f.write(xml_content)
        temp_path = f.name
    
    try:
        parser = HandlingMetaParser()
        entries = parser.parse_file(temp_path)
        
        assert entries[0].inertia_multiplier['x'] == 1.2
        assert entries[0].inertia_multiplier['y'] == 1.0
        assert entries[0].inertia_multiplier['z'] == 1.4
    finally:
        Path(temp_path).unlink()


def test_get_entry_by_name():
    """Test looking up entry by name."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<CHandlingDataMgr>
    <HandlingData>
        <Item name="ADDER" fMass="1400.0"/>
        <Item name="BULLET" fMass="1200.0"/>
    </HandlingData>
</CHandlingDataMgr>
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.meta', delete=False) as f:
        f.write(xml_content)
        temp_path = f.name
    
    try:
        parser = HandlingMetaParser()
        parser.parse_file(temp_path)
        
        adder = parser.get_entry_by_name("ADDER")
        assert adder is not None
        assert adder.name == "ADDER"
        assert adder.mass == 1400.0
        
        nonexistent = parser.get_entry_by_name("NONEXISTENT")
        assert nonexistent is None
    finally:
        Path(temp_path).unlink()


def test_validate_no_errors():
    """Test validation with valid entries."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<CHandlingDataMgr>
    <HandlingData>
        <Item name="ADDER" fMass="1400.0" fDragMult="0.35"/>
    </HandlingData>
</CHandlingDataMgr>
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.meta', delete=False) as f:
        f.write(xml_content)
        temp_path = f.name
    
    try:
        parser = HandlingMetaParser()
        parser.parse_file(temp_path)
        
        errors = parser.validate()
        assert len(errors) == 0
    finally:
        Path(temp_path).unlink()


def test_validate_negative_mass():
    """Test validation catches negative mass."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<CHandlingDataMgr>
    <HandlingData>
        <Item name="TEST" fMass="-1400.0"/>
    </HandlingData>
</CHandlingDataMgr>
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.meta', delete=False) as f:
        f.write(xml_content)
        temp_path = f.name
    
    try:
        parser = HandlingMetaParser()
        parser.parse_file(temp_path)
        
        errors = parser.validate()
        assert len(errors) > 0
        assert any("Mass must be positive" in e for e in errors)
    finally:
        Path(temp_path).unlink()


def test_validate_duplicate_names():
    """Test validation catches duplicate vehicle names."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<CHandlingDataMgr>
    <HandlingData>
        <Item name="ADDER" fMass="1400.0"/>
        <Item name="ADDER" fMass="1500.0"/>
    </HandlingData>
</CHandlingDataMgr>
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.meta', delete=False) as f:
        f.write(xml_content)
        temp_path = f.name
    
    try:
        parser = HandlingMetaParser()
        parser.parse_file(temp_path)
        
        errors = parser.validate()
        assert len(errors) > 0
        assert any("Duplicate" in e for e in errors)
    finally:
        Path(temp_path).unlink()


def test_parse_file_not_found():
    """Test FileNotFoundError for missing file."""
    parser = HandlingMetaParser()
    
    with pytest.raises(FileNotFoundError):
        parser.parse_file("/nonexistent/file.meta")


def test_parse_invalid_xml():
    """Test ValueError for invalid XML."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.meta', delete=False) as f:
        f.write("This is not valid XML")
        temp_path = f.name
    
    try:
        parser = HandlingMetaParser()
        
        with pytest.raises(ValueError):
            parser.parse_file(temp_path)
    finally:
        Path(temp_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
