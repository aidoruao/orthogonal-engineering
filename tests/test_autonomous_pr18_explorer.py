#!/usr/bin/env python3
"""
Tests for Autonomous PR #18 Explorer
====================================

Tests the autonomous exploration and planning system.
"""

import json
import tempfile
from pathlib import Path

import pytest

from autonomous_pr18_explorer import (
    AutonomousExplorer,
    DependencyInfo,
    FileInfo,
    ShardInfo,
)


class TestAutonomousExplorer:
    """Test suite for AutonomousExplorer."""

    def test_initialization(self):
        """Test explorer initialization."""
        explorer = AutonomousExplorer(
            repo_path='.',
            target_loc_min=400000,
            target_loc_max=700000
        )
        
        assert explorer.target_loc_min == 400000
        assert explorer.target_loc_max == 700000
        assert len(explorer.files) == 0
        assert len(explorer.shards) == 0
        assert len(explorer.dependencies) == 0

    def test_should_skip_patterns(self):
        """Test file skipping logic."""
        explorer = AutonomousExplorer('.')
        
        # Should skip
        assert explorer.should_skip(Path('__pycache__/test.pyc'))
        assert explorer.should_skip(Path('.git/config'))
        assert explorer.should_skip(Path('node_modules/package'))
        assert explorer.should_skip(Path('test.pyc'))
        
        # Should not skip
        assert not explorer.should_skip(Path('test.py'))
        assert not explorer.should_skip(Path('src/main.py'))

    def test_detect_language(self):
        """Test language detection."""
        explorer = AutonomousExplorer('.')
        
        assert explorer.detect_language(Path('test.py')) == 'Python'
        assert explorer.detect_language(Path('test.js')) == 'JavaScript'
        assert explorer.detect_language(Path('test.html')) == 'HTML'
        assert explorer.detect_language(Path('test.ps1')) == 'PowerShell'
        assert explorer.detect_language(Path('test.bat')) == 'Batchfile'
        assert explorer.detect_language(Path('test.tex')) == 'TeX'
        assert explorer.detect_language(Path('test.yaml')) == 'YAML'
        assert explorer.detect_language(Path('test.md')) == 'Markdown'
        assert explorer.detect_language(Path('test.unknown')) == 'Other'

    def test_count_loc(self, tmp_path):
        """Test LOC counting."""
        explorer = AutonomousExplorer('.')
        
        # Create test file with various line types
        test_file = tmp_path / 'test.py'
        test_file.write_text('''# This is a comment
import os

def main():
    # Another comment
    print("Hello")
    
    return True

# Final comment
''')
        
        loc = explorer.count_loc(test_file)
        # Should count: import, def, print, return (4 lines)
        # Should skip: comments and blank lines
        assert loc == 4

    def test_hash_file(self, tmp_path):
        """Test file hashing."""
        explorer = AutonomousExplorer('.')
        
        test_file = tmp_path / 'test.txt'
        test_file.write_text('test content')
        
        hash1 = explorer.hash_file(test_file)
        assert len(hash1) == 64  # SHA-256 hash length
        
        # Same content should produce same hash
        test_file2 = tmp_path / 'test2.txt'
        test_file2.write_text('test content')
        hash2 = explorer.hash_file(test_file2)
        assert hash1 == hash2

    def test_generate_initial_checkpoint(self):
        """Test initial checkpoint generation."""
        explorer = AutonomousExplorer(
            repo_path='.',
            target_loc_min=400000,
            target_loc_max=700000
        )
        
        checkpoint = explorer.generate_initial_checkpoint()
        
        assert checkpoint['checkpoint_type'] == 'initial_planning'
        assert 'timestamp' in checkpoint
        assert checkpoint['target_loc']['min'] == 400000
        assert checkpoint['target_loc']['max'] == 700000
        assert checkpoint['target_loc']['optimal'] == 550000
        assert 'shard_design' in checkpoint
        assert 'scaffolding_plan' in checkpoint
        assert 'next_actions' in checkpoint

    def test_parse_requirements_txt(self, tmp_path):
        """Test requirements.txt parsing."""
        explorer = AutonomousExplorer('.')
        
        # Create test requirements.txt
        req_file = tmp_path / 'requirements.txt'
        req_file.write_text('''# Comment line
pandas>=2.0.0
numpy==1.24.0
requests
''')
        
        explorer.repo_path = tmp_path
        explorer._parse_requirements_txt(req_file)
        
        assert len(explorer.dependencies) == 3
        
        # Check pandas
        pandas_dep = next(d for d in explorer.dependencies if d.name == 'pandas')
        assert pandas_dep.version == '2.0.0'
        
        # Check numpy
        numpy_dep = next(d for d in explorer.dependencies if d.name == 'numpy')
        assert numpy_dep.version == '1.24.0'

    def test_parse_package_json(self, tmp_path):
        """Test package.json parsing."""
        explorer = AutonomousExplorer('.')
        
        # Create test package.json
        pkg_file = tmp_path / 'package.json'
        pkg_content = {
            "name": "test-package",
            "dependencies": {
                "express": "^4.18.0",
                "lodash": "~4.17.0"
            },
            "devDependencies": {
                "jest": "^29.0.0"
            }
        }
        pkg_file.write_text(json.dumps(pkg_content))
        
        explorer.repo_path = tmp_path
        explorer._parse_package_json(pkg_file)
        
        assert len(explorer.dependencies) == 3
        
        # Check dependencies are parsed
        dep_names = {d.name for d in explorer.dependencies}
        assert 'express' in dep_names
        assert 'lodash' in dep_names
        assert 'jest' in dep_names

    def test_generate_shards(self, tmp_path):
        """Test shard generation."""
        explorer = AutonomousExplorer(str(tmp_path))
        
        # Create test files in different directories
        (tmp_path / 'src').mkdir()
        (tmp_path / 'tests').mkdir()
        
        src_file = tmp_path / 'src' / 'main.py'
        src_file.write_text('def main():\n    pass\n')
        
        test_file = tmp_path / 'tests' / 'test_main.py'
        test_file.write_text('def test_main():\n    pass\n')
        
        # Add files manually for testing
        explorer.files = [
            FileInfo(path='src/main.py', size=100, loc=2, language='Python', hash='abc123'),
            FileInfo(path='tests/test_main.py', size=100, loc=2, language='Python', hash='def456'),
        ]
        
        explorer.generate_shards()
        
        assert 'src' in explorer.shards
        assert 'tests' in explorer.shards
        
        src_shard = explorer.shards['src']
        assert src_shard.file_count == 1
        assert src_shard.total_loc == 2
        assert 'Python' in src_shard.languages

    def test_full_exploration_structure(self, tmp_path):
        """Test complete exploration report structure."""
        # Create minimal test repository
        (tmp_path / 'src').mkdir()
        test_file = tmp_path / 'src' / 'test.py'
        test_file.write_text('print("hello")\n')
        
        explorer = AutonomousExplorer(str(tmp_path))
        
        # Run exploration
        report = explorer.run_autonomous_exploration()
        
        # Verify report structure
        assert 'repos' in report
        assert 'orthogonal-engineering' in report['repos']
        
        repo_data = report['repos']['orthogonal-engineering']
        assert 'exact_file_counts' in repo_data
        assert 'LOC_per_file' in repo_data
        assert 'total_LOC' in repo_data
        assert 'shard_map' in repo_data
        assert 'dependencies' in repo_data
        
        assert 'scaffolding_plan' in report
        assert 'current_LOC' in report['scaffolding_plan']
        assert 'target_LOC' in report['scaffolding_plan']
        assert 'lines_needed' in report['scaffolding_plan']
        
        assert 'next_actions' in report
        assert 'timestamp' in report
        assert 'initial_checkpoint' in report

    def test_output_to_file(self, tmp_path):
        """Test writing output to file."""
        # Create minimal test repository
        test_file = tmp_path / 'test.py'
        test_file.write_text('print("test")\n')
        
        output_file = tmp_path / 'output.json'
        
        explorer = AutonomousExplorer(str(tmp_path))
        explorer.run_autonomous_exploration(output_file=str(output_file))
        
        # Verify output file exists and is valid JSON
        assert output_file.exists()
        
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        assert 'repos' in data
        assert 'scaffolding_plan' in data

    def test_determine_next_actions(self):
        """Test next actions determination."""
        explorer = AutonomousExplorer('.', target_loc_min=400000, target_loc_max=700000)
        
        # Below minimum
        action = explorer._determine_next_actions(300000, 550000)
        assert 'expand_codebase' in action
        assert 'need' in action.lower()
        assert 'LOC' in action
        
        # Within range
        action = explorer._determine_next_actions(500000, 550000)
        assert 'target_LOC_achieved' in action
        
        # Above maximum
        action = explorer._determine_next_actions(800000, 550000)
        assert 'refactor_or_split' in action
        assert 'LOC above' in action

    def test_suggest_files_to_add(self):
        """Test file addition suggestions."""
        explorer = AutonomousExplorer('.')
        
        # Need 100k lines
        suggestions = explorer._suggest_files_to_add(100000)
        
        assert 'src/new_modules' in suggestions
        assert 'tests/new_tests' in suggestions
        assert 'docs/new_documentation' in suggestions
        assert 'examples/new_examples' in suggestions
        
        # Total should approximately equal lines needed
        total = sum(suggestions.values())
        assert total == 100000

    def test_expansion_strategy(self):
        """Test expansion strategy determination."""
        explorer = AutonomousExplorer('.')
        
        # No expansion needed
        strategy = explorer._determine_expansion_strategy(0)
        assert strategy == 'maintain_current_structure'
        
        # Small expansion
        strategy = explorer._determine_expansion_strategy(50000)
        assert strategy == 'incremental_expansion'
        
        # Moderate expansion
        strategy = explorer._determine_expansion_strategy(200000)
        assert strategy == 'moderate_expansion'
        
        # Major expansion
        strategy = explorer._determine_expansion_strategy(400000)
        assert strategy == 'major_expansion'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
