#!/usr/bin/env python3
"""
Tests for PR #18 Task-Agent Execution System
============================================

Tests the task-agent that executes shard actions and manages
the PR #18 workflow to completion.
"""

import json
import tempfile
from pathlib import Path

import pytest

from pr18_task_agent import PR18TaskAgent, ShardAction, ExecutionCycle


class TestPR18TaskAgent:
    """Test suite for PR18TaskAgent."""

    @pytest.fixture
    def sample_report(self, tmp_path):
        """Create a sample report for testing."""
        report = {
            "repos": {
                "orthogonal-engineering": {
                    "exact_file_counts": {
                        "total": 100,
                        "by_language": {"Python": 50, "JavaScript": 50}
                    },
                    "LOC_per_file": {},
                    "LOC_by_language": {"Python": 30000, "JavaScript": 20000},
                    "total_LOC": 50000,
                    "total_size_bytes": 1000000,
                    "shard_map": {
                        "src": {
                            "path_pattern": "src/**/*",
                            "file_count": 50,
                            "total_loc": 30000,
                            "languages": {"Python": 30000}
                        },
                        "tests": {
                            "path_pattern": "tests/**/*",
                            "file_count": 30,
                            "total_loc": 15000,
                            "languages": {"Python": 15000}
                        },
                        "docs": {
                            "path_pattern": "docs/**/*",
                            "file_count": 20,
                            "total_loc": 5000,
                            "languages": {"Markdown": 5000}
                        }
                    },
                    "dependencies": {
                        "requirements.txt": [
                            {"name": "pandas", "version": ">=2.0.0"}
                        ]
                    }
                }
            },
            "scaffolding_plan": {
                "current_LOC": 50000,
                "target_LOC": 550000,
                "lines_needed": 500000
            },
            "timestamp": "2026-02-17T09:00:00+00:00",
            "verification_compatible": True,
            "shard_parallelizable": True,
            "deterministic": True
        }
        
        report_path = tmp_path / "test_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f)
        
        return report_path

    def test_initialization(self, sample_report):
        """Test task-agent initialization."""
        agent = PR18TaskAgent(
            report_path=str(sample_report),
            target_loc_min=400000,
            target_loc_max=700000
        )
        
        assert agent.target_loc_min == 400000
        assert agent.target_loc_max == 700000
        assert len(agent.execution_cycles) == 0

    def test_load_and_validate_report(self, sample_report):
        """Test loading and validating report."""
        agent = PR18TaskAgent(str(sample_report))
        
        result = agent.load_and_validate_report()
        
        assert result is True
        assert 'repos' in agent.report
        assert 'orthogonal-engineering' in agent.report['repos']

    def test_load_invalid_report(self, tmp_path):
        """Test loading invalid report."""
        # Missing required keys
        invalid_report = {"repos": {}}
        report_path = tmp_path / "invalid.json"
        with open(report_path, 'w') as f:
            json.dump(invalid_report, f)
        
        agent = PR18TaskAgent(str(report_path))
        result = agent.load_and_validate_report()
        
        assert result is False

    def test_determine_shard_actions(self, sample_report):
        """Test determining shard actions."""
        agent = PR18TaskAgent(str(sample_report))
        agent.load_and_validate_report()
        
        actions = agent.determine_shard_actions()
        
        assert len(actions) == 3  # src, tests, docs
        assert all(isinstance(a, ShardAction) for a in actions)
        
        # All shards should need expansion since total is 50k vs target 400k-700k
        expand_actions = [a for a in actions if a.action == 'expand_code']
        assert len(expand_actions) > 0

    def test_shard_action_classification(self, sample_report):
        """Test that shards are correctly classified."""
        agent = PR18TaskAgent(
            str(sample_report),
            target_loc_min=40000,  # Adjust to force different actions
            target_loc_max=60000
        )
        agent.load_and_validate_report()
        
        actions = agent.determine_shard_actions()
        
        # Check that actions are one of the three types
        for action in actions:
            assert action.action in ['expand_code', 'refactor_or_split', 'validate_only']

    def test_execute_expand_code(self, sample_report):
        """Test executing expand_code action."""
        agent = PR18TaskAgent(str(sample_report))
        agent.load_and_validate_report()
        
        action = ShardAction(
            shard_name='src',
            action='expand_code',
            current_loc=30000,
            target_min=50000,
            target_max=70000,
            gap=20000
        )
        
        result = agent._execute_expand_code(action)
        
        assert result['action'] == 'expand_code'
        assert result['loc_added'] == 20000
        assert result['modified'] is True
        
        # Check shard was updated
        shard_data = agent.report['repos']['orthogonal-engineering']['shard_map']['src']
        assert shard_data['total_loc'] == 50000  # 30000 + 20000

    def test_execute_refactor_or_split(self, sample_report):
        """Test executing refactor_or_split action."""
        agent = PR18TaskAgent(str(sample_report))
        agent.load_and_validate_report()
        
        action = ShardAction(
            shard_name='src',
            action='refactor_or_split',
            current_loc=30000,
            target_min=10000,
            target_max=20000,
            gap=10000
        )
        
        result = agent._execute_refactor_or_split(action)
        
        assert result['action'] == 'refactor_or_split'
        assert result['loc_reduced'] == 10000
        assert result['modified'] is True
        
        # Check shard was updated
        shard_data = agent.report['repos']['orthogonal-engineering']['shard_map']['src']
        assert shard_data['total_loc'] == 20000  # 30000 - 10000

    def test_execute_validate_only(self, sample_report):
        """Test executing validate_only action."""
        agent = PR18TaskAgent(str(sample_report))
        agent.load_and_validate_report()
        
        action = ShardAction(
            shard_name='src',
            action='validate_only',
            current_loc=30000,
            target_min=25000,
            target_max=35000,
            gap=0
        )
        
        result = agent._execute_validate_only(action)
        
        assert result['action'] == 'validate_only'
        assert result['modified'] is False

    def test_update_json_after_cycle(self, sample_report, tmp_path):
        """Test updating JSON after execution cycle."""
        # Use tmp_path for report to ensure output goes there
        agent = PR18TaskAgent(str(sample_report))
        agent.load_and_validate_report()
        
        cycle_results = {
            'cycle_number': 1,
            'timestamp': '2026-02-17T10:00:00+00:00',
            'actions_taken': [],
            'files_modified': [],
            'shards_updated': ['src'],
            'total_loc_before': 50000,
            'total_loc_after': 60000
        }
        
        agent.update_json_after_cycle(cycle_results)
        
        # Check report was updated
        assert agent.report['repos']['orthogonal-engineering']['total_LOC'] == 60000
        assert 'execution_history' in agent.report
        assert len(agent.report['execution_history']) == 1

    def test_check_completion(self, sample_report):
        """Test completion checking."""
        agent = PR18TaskAgent(str(sample_report))
        agent.load_and_validate_report()
        
        # All validate_only means complete
        actions_complete = [
            ShardAction('shard1', 'validate_only', 10000, 9000, 11000, 0),
            ShardAction('shard2', 'validate_only', 10000, 9000, 11000, 0)
        ]
        assert agent.check_completion(actions_complete) is True
        
        # Any expand or refactor means not complete
        actions_incomplete = [
            ShardAction('shard1', 'validate_only', 10000, 9000, 11000, 0),
            ShardAction('shard2', 'expand_code', 5000, 9000, 11000, 4000)
        ]
        assert agent.check_completion(actions_incomplete) is False

    def test_final_verification(self, sample_report):
        """Test final verification."""
        agent = PR18TaskAgent(str(sample_report))
        agent.load_and_validate_report()
        
        results = agent.final_verification()
        
        assert 'all_shards_within_target' in results
        assert 'all_files_hashed' in results
        assert 'dependencies_resolved' in results
        assert 'json_complete' in results
        assert 'total_loc' in results

    def test_prepare_for_indexing(self, sample_report, tmp_path):
        """Test preparing for indexing."""
        agent = PR18TaskAgent(str(sample_report))
        agent.load_and_validate_report()
        
        results = agent.prepare_for_indexing()
        
        assert 'snapshot_path' in results
        assert 'ready' in results
        assert results['ready'] is True
        
        # Check snapshot file was created
        snapshot_path = Path(results['snapshot_path'])
        assert snapshot_path.exists()
        
        # Check snapshot has correct structure
        with open(snapshot_path, 'r') as f:
            snapshot = json.load(f)
        assert 'metadata' in snapshot
        assert 'report' in snapshot
        assert 'verification' in snapshot

    def test_dry_run_mode(self, sample_report):
        """Test dry-run mode doesn't make changes."""
        agent = PR18TaskAgent(str(sample_report))
        
        results = agent.run(dry_run=True, max_cycles=1)
        
        assert results['success'] is True
        assert results['dry_run'] is True
        assert len(agent.execution_cycles) == 0  # No cycles executed in dry-run

    def test_full_execution(self, sample_report):
        """Test full execution workflow."""
        agent = PR18TaskAgent(str(sample_report))
        
        # Run with limited cycles
        results = agent.run(max_cycles=2, dry_run=False)
        
        assert results['success'] is True
        assert 'verification' in results
        assert 'indexing' in results

    def test_integrate_cross_repo_dependencies(self, sample_report):
        """Test cross-repo dependency integration."""
        agent = PR18TaskAgent(str(sample_report))
        agent.load_and_validate_report()
        
        results = agent.integrate_cross_repo_dependencies()
        
        assert 'repos_analyzed' in results
        assert 'pending_repos' in results
        assert 'orthogonal-engineering' in results['repos_analyzed']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
