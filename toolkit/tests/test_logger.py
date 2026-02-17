"""
Test module for logger.py

Tests structured JSONL logging functionality.

Author: Orthogonal Engineering System
Date: 2026-02-16
Version: 1.0.0
"""

import json
import shutil
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from toolkit.oe.logger import (
    HandlingPipelineLogger,
    StructuredLogger,
    VerificationPipelineLogger,
)


class TestStructuredLogger(unittest.TestCase):
    """Test cases for StructuredLogger class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_logger_creation(self):
        """Test creating a logger."""
        log_path = self.test_path / 'test.jsonl'
        logger = StructuredLogger(log_path)
        
        self.assertEqual(logger.output_path, log_path)
        self.assertIsNotNone(logger.file_handle)
        
        logger.close()
    
    def test_log_basic_event(self):
        """Test logging a basic event."""
        log_path = self.test_path / 'test.jsonl'
        
        with StructuredLogger(log_path) as logger:
            logger.log('test_step', 'start')
        
        # Read log
        with open(log_path, 'r') as f:
            record = json.loads(f.readline())
        
        self.assertEqual(record['step_id'], 'test_step')
        self.assertEqual(record['event_type'], 'start')
        self.assertIn('timestamp', record)
    
    def test_log_with_data(self):
        """Test logging with additional data."""
        log_path = self.test_path / 'test.jsonl'
        
        with StructuredLogger(log_path) as logger:
            logger.log('test_step', 'complete', data={'count': 42})
        
        # Read log
        with open(log_path, 'r') as f:
            record = json.loads(f.readline())
        
        self.assertIn('data', record)
        self.assertEqual(record['data']['count'], 42)
    
    def test_log_timestamp_iso8601(self):
        """Test that timestamps are in ISO8601 format."""
        log_path = self.test_path / 'test.jsonl'
        
        with StructuredLogger(log_path) as logger:
            logger.log('test_step', 'start')
        
        # Read log
        with open(log_path, 'r') as f:
            record = json.loads(f.readline())
        
        # Verify timestamp is valid ISO8601
        timestamp = record['timestamp']
        # Should be parseable
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    
    def test_log_hello_world(self):
        """Test logging hello world event."""
        log_path = self.test_path / 'test.jsonl'
        
        with StructuredLogger(log_path) as logger:
            logger.log_hello_world('test_pipeline')
        
        # Read log
        with open(log_path, 'r') as f:
            record = json.loads(f.readline())
        
        self.assertEqual(record['step_id'], 'hello_world')
        self.assertEqual(record['event_type'], 'greeting')
        self.assertIn('message', record)
        self.assertEqual(record['pipeline'], 'test_pipeline')
    
    def test_context_manager(self):
        """Test using logger as context manager."""
        log_path = self.test_path / 'test.jsonl'
        
        with StructuredLogger(log_path) as logger:
            logger.log('step1', 'start')
            logger.log('step1', 'complete')
        
        # File should exist and contain records
        self.assertTrue(log_path.exists())
        
        with open(log_path, 'r') as f:
            lines = f.readlines()
        
        self.assertEqual(len(lines), 2)


class TestHandlingPipelineLogger(unittest.TestCase):
    """Test cases for HandlingPipelineLogger class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_handling_logger_filename(self):
        """Test that handling logger uses correct filename."""
        logger = HandlingPipelineLogger(self.test_path)
        
        expected_path = self.test_path / 'hello_world_handling_pipeline.jsonl'
        self.assertEqual(logger.output_path, expected_path)
        
        logger.close()
    
    def test_log_vehicle_clamp(self):
        """Test logging vehicle clamp operation."""
        logger = HandlingPipelineLogger(self.test_path)
        
        logger.log_vehicle_clamp(
            vehicle_name='ADDER',
            field='fMass',
            old_value='1000.0',
            new_value='1500.0',
            dry_run=False
        )
        
        logger.close()
        
        # Read log
        log_path = self.test_path / 'hello_world_handling_pipeline.jsonl'
        with open(log_path, 'r') as f:
            record = json.loads(f.readline())
        
        self.assertEqual(record['step_id'], 'vehicle_clamp')
        self.assertEqual(record['event_type'], 'clamp_applied')
        self.assertIn('data', record)
        self.assertEqual(record['data']['vehicle_name'], 'ADDER')
        self.assertEqual(record['data']['field'], 'fMass')
    
    def test_log_vehicle_clamp_dry_run(self):
        """Test logging vehicle clamp in dry-run mode."""
        logger = HandlingPipelineLogger(self.test_path)
        
        logger.log_vehicle_clamp(
            vehicle_name='ADDER',
            field='fMass',
            old_value='1000.0',
            new_value='1500.0',
            dry_run=True
        )
        
        logger.close()
        
        # Read log
        log_path = self.test_path / 'hello_world_handling_pipeline.jsonl'
        with open(log_path, 'r') as f:
            record = json.loads(f.readline())
        
        self.assertEqual(record['event_type'], 'clamp_dry_run')
        self.assertTrue(record['dry_run'])
    
    def test_log_parsing_start(self):
        """Test logging parsing start."""
        logger = HandlingPipelineLogger(self.test_path)
        
        logger.log_parsing_start('handling.meta')
        logger.close()
        
        # Read log
        log_path = self.test_path / 'hello_world_handling_pipeline.jsonl'
        with open(log_path, 'r') as f:
            record = json.loads(f.readline())
        
        self.assertEqual(record['step_id'], 'parse_handling')
        self.assertEqual(record['event_type'], 'start')
        self.assertEqual(record['file_path'], 'handling.meta')
    
    def test_log_parsing_complete(self):
        """Test logging parsing completion."""
        logger = HandlingPipelineLogger(self.test_path)
        
        logger.log_parsing_complete('handling.meta', 10)
        logger.close()
        
        # Read log
        log_path = self.test_path / 'hello_world_handling_pipeline.jsonl'
        with open(log_path, 'r') as f:
            record = json.loads(f.readline())
        
        self.assertEqual(record['step_id'], 'parse_handling')
        self.assertEqual(record['event_type'], 'complete')
        self.assertEqual(record['vehicle_count'], 10)


class TestVerificationPipelineLogger(unittest.TestCase):
    """Test cases for VerificationPipelineLogger class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_verification_logger_filename(self):
        """Test that verification logger uses correct filename."""
        logger = VerificationPipelineLogger(self.test_path)
        
        expected_path = self.test_path / 'handling_verification_pipeline.jsonl'
        self.assertEqual(logger.output_path, expected_path)
        
        logger.close()
    
    def test_log_hash_verification(self):
        """Test logging hash verification."""
        logger = VerificationPipelineLogger(self.test_path)
        
        logger.log_hash_verification(
            file_path='test.txt',
            expected_hash='abc123',
            actual_hash='abc123',
            verified=True
        )
        
        logger.close()
        
        # Read log
        log_path = self.test_path / 'handling_verification_pipeline.jsonl'
        with open(log_path, 'r') as f:
            record = json.loads(f.readline())
        
        self.assertEqual(record['step_id'], 'verify_hash')
        self.assertTrue(record['data']['verified'])
    
    def test_log_merkle_verification(self):
        """Test logging Merkle proof verification."""
        logger = VerificationPipelineLogger(self.test_path)
        
        logger.log_merkle_verification(
            file_path='test.txt',
            root_hash='root123',
            verified=True
        )
        
        logger.close()
        
        # Read log
        log_path = self.test_path / 'handling_verification_pipeline.jsonl'
        with open(log_path, 'r') as f:
            record = json.loads(f.readline())
        
        self.assertEqual(record['step_id'], 'verify_merkle')
        self.assertEqual(record['data']['root_hash'], 'root123')


if __name__ == '__main__':
    unittest.main()
