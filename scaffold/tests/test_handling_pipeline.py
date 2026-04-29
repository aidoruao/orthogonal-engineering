"""
Unit tests for handling_pipeline module.

Tests GTA handling.meta parsing and processing.
"""

import tempfile
import unittest
from pathlib import Path

from scaffold.handling_pipeline import (
    HandlingMetaParser,
    HandlingPipeline,
    HandlingVehicle,
)
from scaffold.logger import ScaffoldLogger


class TestHandlingVehicle(unittest.TestCase):
    """Test cases for HandlingVehicle class."""
    
    def test_creation(self):
        """Test creating vehicle from data."""
        data = {
            "handlingName": "TestVehicle",
            "mass": "1500.0",
            "initialDragCoeff": "8.5"
        }
        
        vehicle = HandlingVehicle(data)
        
        self.assertEqual(vehicle.name, "TestVehicle")
        self.assertEqual(vehicle.get_attribute("mass"), "1500.0")
    
    def test_get_attribute_default(self):
        """Test getting attribute with default."""
        vehicle = HandlingVehicle({"handlingName": "Test"})
        
        self.assertEqual(vehicle.get_attribute("missing", "default"), "default")
    
    def test_to_dict(self):
        """Test converting vehicle to dictionary."""
        data = {"handlingName": "Test", "mass": "1000"}
        vehicle = HandlingVehicle(data)
        
        result = vehicle.to_dict()
        
        self.assertEqual(result, data)


class TestHandlingMetaParser(unittest.TestCase):
    """Test cases for HandlingMetaParser class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        self.logger = ScaffoldLogger(log_dir=self.test_path / "logs")
        self.parser = HandlingMetaParser(logger=self.logger)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_parse_simple_xml(self):
        """Test parsing simple XML file."""
        # TODO: Expand test_parse_simple_xml() - stub detected by Yeshua Agent
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<CHandlingDataMgr>
    <HandlingData>
        <Item type="CHandlingData">
            <handlingName value="ADDER"/>
            <fMass value="1600.0"/>
            <fInitialDragCoeff value="8.5"/>
        </Item>
    </HandlingData>
</CHandlingDataMgr>"""
        
        meta_file = self.test_path / "handling.meta"
        meta_file.write_text(xml_content)
        
        vehicles = self.parser.parse_file(meta_file)
        
        # Parser should extract vehicle data
        self.assertIsInstance(vehicles, list)
    
    def test_get_vehicle(self):
        """Test getting vehicle by name."""
        # Add vehicle manually
        vehicle_data = {"handlingName": "TestCar"}
        self.parser.vehicles = [HandlingVehicle(vehicle_data)]
        
        vehicle = self.parser.get_vehicle("TestCar")
        
        self.assertIsNotNone(vehicle)
        self.assertEqual(vehicle.name, "TestCar")
    
    def test_get_nonexistent_vehicle(self):
        """Test getting non-existent vehicle."""
        vehicle = self.parser.get_vehicle("NonExistent")
        self.assertIsNone(vehicle)
    
    def test_filter_vehicles(self):
        """Test filtering vehicles."""
        self.parser.vehicles = [
            HandlingVehicle({"handlingName": "Car1", "mass": "1000"}),
            HandlingVehicle({"handlingName": "Car2", "mass": "2000"}),
        ]
        
        # Filter for heavy vehicles
        heavy = self.parser.filter_vehicles(
            lambda v: int(v.get_attribute("mass", "0")) > 1500
        )
        
        self.assertEqual(len(heavy), 1)
        self.assertEqual(heavy[0].name, "Car2")
    
    def test_export_vehicles(self):
        """Test exporting vehicles to JSON."""
        self.parser.vehicles = [
            HandlingVehicle({"handlingName": "Car1"}),
        ]
        
        output_file = self.test_path / "vehicles.json"
        self.parser.export_vehicles(output_file)
        
        self.assertTrue(output_file.exists())
        
        # Verify JSON content
        import json
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        self.assertIn('vehicle_count', data)
        self.assertIn('vehicles', data)
        self.assertEqual(data['vehicle_count'], 1)
    
    def test_file_not_found(self):
        """Test parsing non-existent file."""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_file(self.test_path / "nonexistent.meta")


class TestHandlingPipeline(unittest.TestCase):
    """Test cases for HandlingPipeline class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        self.logger = ScaffoldLogger(log_dir=self.test_path / "logs")
        self.pipeline = HandlingPipeline(logger=self.logger)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_process_file(self):
        """Test processing a single file."""
        # TODO: Expand test_process_file() - stub detected by Yeshua Agent
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<CHandlingDataMgr>
    <HandlingData>
        <Item type="CHandlingData">
            <handlingName value="TEST"/>
        </Item>
    </HandlingData>
</CHandlingDataMgr>"""
        
        meta_file = self.test_path / "handling.meta"
        meta_file.write_text(xml_content)
        
        result = self.pipeline.process_file(meta_file)
        
        self.assertIn('file', result)
        self.assertIn('hash', result)
        self.assertIn('vehicle_count', result)
    
    def test_process_file_with_output(self):
        """Test processing file with output directory."""
        # TODO: Expand test_process_file_with_output() - stub detected by Yeshua Agent
        xml_content = """<?xml version="1.0"?>
<root><item><handlingName value="CAR"/></item></root>"""
        
        meta_file = self.test_path / "test.meta"
        meta_file.write_text(xml_content)
        
        output_dir = self.test_path / "output"
        result = self.pipeline.process_file(meta_file, output_dir)
        
        self.assertIn('output_file', result)
        self.assertTrue(Path(result['output_file']).exists())
    
    def test_process_directory(self):
        """Test processing multiple files in directory."""
        # Create multiple .meta files
        for i in range(3):
            xml_content = f"""<?xml version="1.0"?>
<root><item><handlingName value="CAR{i}"/></item></root>"""
            meta_file = self.test_path / f"handling{i}.meta"
            meta_file.write_text(xml_content)
        
        results = self.pipeline.process_directory(self.test_path)
        
        # Should process all .meta files
        self.assertGreaterEqual(len(results), 3)


if __name__ == '__main__':
    unittest.main()
