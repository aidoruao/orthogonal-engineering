"""
Unit tests for logger module.
"""

import tempfile
import json
import pytest
from pathlib import Path
from datetime import datetime

from toolkit.oe.scaffold.logger import ScaffoldLogger, create_hello_world_logger


def test_logger_initialization():
    """Test logger initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = ScaffoldLogger(output_dir=tmpdir, prefix="test")
        
        assert logger.output_dir == Path(tmpdir)
        assert logger.step_id == 0
        assert logger.prefix == "test"


def test_logger_creates_log_files():
    """Test that logger creates log file paths."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = ScaffoldLogger(output_dir=tmpdir, prefix="test")
        
        assert logger.pipeline_log.name == "test_pipeline.jsonl"
        assert logger.verification_log.name == "test_verification_pipeline.jsonl"


def test_log_pipeline():
    """Test logging to pipeline log."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = ScaffoldLogger(output_dir=tmpdir, prefix="test")
        
        logger.log_pipeline("test_event", {"key": "value"})
        
        # Verify file created and contains entry
        assert logger.pipeline_log.exists()
        
        with open(logger.pipeline_log, 'r') as f:
            line = f.readline()
            entry = json.loads(line)
            
            assert entry['step_id'] == 1
            assert entry['event'] == "test_event"
            assert entry['data']['key'] == "value"
            assert 'timestamp' in entry


def test_log_verification():
    """Test logging verification events."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = ScaffoldLogger(output_dir=tmpdir, prefix="test")
        
        logger.log_verification("hash_check", True, {"file": "test.txt"})
        
        # Verify file and entry
        assert logger.verification_log.exists()
        
        with open(logger.verification_log, 'r') as f:
            line = f.readline()
            entry = json.loads(line)
            
            assert entry['step_id'] == 1
            assert entry['event'] == "hash_check"
            assert entry['result'] is True
            assert entry['details']['file'] == "test.txt"


def test_monotonic_step_ids():
    """Test that step IDs are monotonically increasing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = ScaffoldLogger(output_dir=tmpdir, prefix="test")
        
        logger.log_pipeline("event1")
        logger.log_pipeline("event2")
        logger.log_verification("verify1", True)
        logger.log_pipeline("event3")
        
        # Collect all step IDs with their order of writing
        events = []
        
        # Log order: event1(1), event2(2), verify1(3), event3(4)
        # But files are separate, so we need to merge by step_id
        
        # Read pipeline log
        with open(logger.pipeline_log, 'r') as f:
            for line in f:
                entry = json.loads(line)
                events.append((entry['step_id'], entry['event']))
        
        # Read verification log
        with open(logger.verification_log, 'r') as f:
            for line in f:
                entry = json.loads(line)
                events.append((entry['step_id'], entry['event']))
        
        # Sort by step_id to get chronological order
        events.sort(key=lambda x: x[0])
        step_ids = [sid for sid, _ in events]
        
        # Should be monotonically increasing 1, 2, 3, 4
        assert step_ids == [1, 2, 3, 4]
        assert step_ids == list(range(1, len(step_ids) + 1))


def test_timestamp_format():
    """Test that timestamps are in ISO8601 UTC format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = ScaffoldLogger(output_dir=tmpdir, prefix="test")
        
        logger.log_pipeline("test")
        
        with open(logger.pipeline_log, 'r') as f:
            entry = json.loads(f.readline())
            timestamp = entry['timestamp']
        
        # Should be parseable as ISO8601
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        assert dt is not None


def test_log_general():
    """Test general log method."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = ScaffoldLogger(output_dir=tmpdir, prefix="test")
        
        logger.log("event", key1="value1", key2="value2")
        
        with open(logger.pipeline_log, 'r') as f:
            entry = json.loads(f.readline())
            
            assert entry['event'] == "event"
            assert entry['data']['key1'] == "value1"
            assert entry['data']['key2'] == "value2"


def test_create_hello_world_logger():
    """Test hello world logger creation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = create_hello_world_logger(output_dir=tmpdir)
        
        assert logger.prefix == "hello_world_handling"
        assert logger.pipeline_log.name == "hello_world_handling_pipeline.jsonl"


def test_multiple_logs_append():
    """Test that multiple logs append correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = ScaffoldLogger(output_dir=tmpdir, prefix="test")
        
        # Log multiple events
        for i in range(5):
            logger.log_pipeline(f"event_{i}")
        
        # Count lines
        with open(logger.pipeline_log, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 5
        
        # Verify each is valid JSON
        for line in lines:
            entry = json.loads(line)
            assert 'step_id' in entry
            assert 'event' in entry


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
