"""
Test module for handling_pipeline.py

Tests GTA handling.meta XML parsing and clamping operations.

Author: Orthogonal Engineering System
Date: 2026-02-16
Version: 1.0.0
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from toolkit.oe.handling_pipeline import (
    HandlingMetaParser,
    HandlingPipeline,
    VehicleClampRule,
)
from toolkit.oe.logger import HandlingPipelineLogger


class TestVehicleClampRule(unittest.TestCase):
    """Test cases for VehicleClampRule class."""
    
    def test_clamp_min_value(self):
        """Test clamping to minimum value."""
        rule = VehicleClampRule('fMass', min_value=100.0)
        
        result = rule.apply(50.0)
        self.assertEqual(result, 100.0)
    
    def test_clamp_max_value(self):
        """Test clamping to maximum value."""
        rule = VehicleClampRule('fMass', max_value=1000.0)
        
        result = rule.apply(1500.0)
        self.assertEqual(result, 1000.0)
    
    def test_clamp_within_range(self):
        """Test value within range is not clamped."""
        rule = VehicleClampRule('fMass', min_value=100.0, max_value=1000.0)
        
        result = rule.apply(500.0)
        self.assertEqual(result, 500.0)
    
    def test_clamp_allowed_values(self):
        """Test clamping to allowed discrete values."""
        rule = VehicleClampRule('type', allowed_values=['CAR', 'BIKE', 'BOAT'])
        
        # Valid value
        result = rule.apply('CAR')
        self.assertEqual(result, 'CAR')
        
        # Invalid value - should default to first allowed value
        result = rule.apply('INVALID')
        self.assertEqual(result, 'CAR')
    
    def test_clamp_string_to_numeric(self):
        """Test clamping with string input converted to numeric."""
        rule = VehicleClampRule('fMass', min_value=100.0, max_value=1000.0)
        
        result = rule.apply('50.0')
        self.assertEqual(result, 100.0)


class TestHandlingMetaParser(unittest.TestCase):
    """Test cases for HandlingMetaParser class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create a sample handling.meta XML file
        self.handling_file = self.test_path / 'handling.meta'
        self._create_sample_handling_file()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def _create_sample_handling_file(self):
        """Create a sample handling.meta file for testing."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<CHandlingDataMgr>
  <HandlingData>
    <Item type="CHandlingData">
      <handlingName>ADDER</handlingName>
      <fMass value="1500.000000"/>
      <fInitialDragCoeff value="10.000000"/>
      <fDriveInertia value="1.000000"/>
    </Item>
    <Item type="CHandlingData">
      <handlingName>ZENTORNO</handlingName>
      <fMass value="1600.000000"/>
      <fInitialDragCoeff value="8.500000"/>
      <fDriveInertia value="1.200000"/>
    </Item>
  </HandlingData>
</CHandlingDataMgr>"""
        
        with open(self.handling_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
    
    def test_parser_creation(self):
        """Test creating a parser."""
        parser = HandlingMetaParser(self.handling_file)
        
        self.assertIsNotNone(parser.tree)
        self.assertIsNotNone(parser.root)
    
    def test_parser_finds_vehicles(self):
        """Test that parser finds vehicle elements."""
        parser = HandlingMetaParser(self.handling_file)
        
        self.assertEqual(parser.get_vehicle_count(), 2)
    
    def test_get_vehicle_data(self):
        """Test extracting vehicle data."""
        parser = HandlingMetaParser(self.handling_file)
        
        vehicles = parser.get_all_vehicles()
        
        self.assertEqual(len(vehicles), 2)
        self.assertEqual(vehicles[0]['handlingName'], 'ADDER')
        self.assertEqual(vehicles[1]['handlingName'], 'ZENTORNO')


class TestHandlingPipeline(unittest.TestCase):
    """Test cases for HandlingPipeline class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create a sample handling.meta XML file
        self.handling_file = self.test_path / 'handling.meta'
        self._create_sample_handling_file()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def _create_sample_handling_file(self):
        """Create a sample handling.meta file for testing."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<CHandlingDataMgr>
  <HandlingData>
    <Item type="CHandlingData">
      <handlingName>ADDER</handlingName>
      <fMass value="50000.000000"/>
      <fInitialDragCoeff value="200.000000"/>
      <fDriveInertia value="1.000000"/>
    </Item>
  </HandlingData>
</CHandlingDataMgr>"""
        
        with open(self.handling_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
    
    def test_pipeline_creation(self):
        """Test creating a handling pipeline."""
        pipeline = HandlingPipeline(self.handling_file)
        
        self.assertEqual(pipeline.parser.get_vehicle_count(), 1)
    
    def test_add_clamp_rule(self):
        """Test adding a clamp rule."""
        pipeline = HandlingPipeline(self.handling_file)
        
        rule = VehicleClampRule('fMass', min_value=0.0, max_value=10000.0)
        pipeline.add_clamp_rule(rule)
        
        self.assertIn('fMass', pipeline.clamp_rules)
    
    def test_add_default_clamp_rules(self):
        """Test adding default clamp rules."""
        pipeline = HandlingPipeline(self.handling_file)
        
        pipeline.add_default_clamp_rules()
        
        # Should have several default rules
        self.assertGreater(len(pipeline.clamp_rules), 0)
        self.assertIn('fMass', pipeline.clamp_rules)
    
    def test_process_dry_run(self):
        """Test processing in dry-run mode."""
        log_path = self.test_path / 'logs'
        logger = HandlingPipelineLogger(log_path)
        pipeline = HandlingPipeline(self.handling_file, logger)
        
        # Add rules that will trigger clamping
        pipeline.add_clamp_rule(VehicleClampRule('fMass', min_value=0.0, max_value=10000.0))
        pipeline.add_clamp_rule(VehicleClampRule('fInitialDragCoeff', min_value=0.0, max_value=100.0))
        
        result = pipeline.process(dry_run=True, backup=False)
        
        self.assertTrue(result['dry_run'])
        self.assertEqual(result['vehicles_processed'], 1)
        self.assertGreater(result['changes_made'], 0)
        
        logger.close()
    
    def test_process_applies_changes(self):
        """Test that processing applies changes to file."""
        log_path = self.test_path / 'logs'
        logger = HandlingPipelineLogger(log_path)
        pipeline = HandlingPipeline(self.handling_file, logger)
        
        # Add rule that will clamp fMass
        pipeline.add_clamp_rule(VehicleClampRule('fMass', min_value=0.0, max_value=10000.0))
        
        result = pipeline.process(dry_run=False, backup=True)
        
        self.assertFalse(result['dry_run'])
        self.assertTrue(result['backup_created'])
        self.assertGreater(result['changes_made'], 0)
        
        # Verify backup was created
        backup_file = self.handling_file.with_suffix('.meta.backup')
        self.assertTrue(backup_file.exists())
        
        logger.close()
    
    def test_backup_creation(self):
        """Test that backup is created when requested."""
        log_path = self.test_path / 'logs'
        logger = HandlingPipelineLogger(log_path)
        pipeline = HandlingPipeline(self.handling_file, logger)
        
        pipeline.add_clamp_rule(VehicleClampRule('fMass', min_value=0.0, max_value=10000.0))
        
        result = pipeline.process(dry_run=False, backup=True)
        
        backup_file = self.handling_file.with_suffix('.meta.backup')
        self.assertTrue(backup_file.exists())
        
        logger.close()
    
    def test_no_backup_when_dry_run(self):
        """Test that no backup is created during dry run."""
        log_path = self.test_path / 'logs'
        logger = HandlingPipelineLogger(log_path)
        pipeline = HandlingPipeline(self.handling_file, logger)
        
        pipeline.add_clamp_rule(VehicleClampRule('fMass', min_value=0.0, max_value=10000.0))
        
        result = pipeline.process(dry_run=True, backup=True)
        
        self.assertFalse(result['backup_created'])
        
        backup_file = self.handling_file.with_suffix('.meta.backup')
        self.assertFalse(backup_file.exists())
        
        logger.close()
    
    def test_restore_from_backup(self):
        """Test restoring from backup."""
        log_path = self.test_path / 'logs'
        logger = HandlingPipelineLogger(log_path)
        pipeline = HandlingPipeline(self.handling_file, logger)
        
        # Read original content
        with open(self.handling_file, 'r') as f:
            original_content = f.read()
        
        # Process with backup
        pipeline.add_clamp_rule(VehicleClampRule('fMass', min_value=0.0, max_value=10000.0))
        pipeline.process(dry_run=False, backup=True)
        
        # Restore from backup
        success = pipeline.restore_from_backup()
        
        self.assertTrue(success)
        
        # Verify content is restored
        with open(self.handling_file, 'r') as f:
            restored_content = f.read()
        
        self.assertEqual(original_content, restored_content)
        
        logger.close()
    
    def test_restore_without_backup(self):
        """Test that restore returns False when no backup exists."""
        pipeline = HandlingPipeline(self.handling_file)
        
        success = pipeline.restore_from_backup()
        
        self.assertFalse(success)


if __name__ == '__main__':
    unittest.main()
