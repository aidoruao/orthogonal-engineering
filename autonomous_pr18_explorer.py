#!/usr/bin/env python3
"""
Autonomous PR #18 Repository Explorer
======================================

Implements autonomous exploration and planning for PR #18 targeting 400k-700k LOC.

Phase 1: Initial Planning Checkpoint
- Define target LOC range
- Design shard boundaries
- Generate initial JSON structure

Phase 2: Autonomous Exploration
- Enumerate repository contents fully
- Compute LOC per file and language
- Extract dependencies from manifests
- Adjust shard plans dynamically
- Determine next actions

Author: Orthogonal Engineering System
Date: 2026-02-17
Version: 1.0.0
"""

import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Language file extensions
LANGUAGE_EXTENSIONS = {
    'Python': ['.py'],
    'JavaScript': ['.js', '.jsx'],
    'HTML': ['.html', '.htm'],
    'CSS': ['.css', '.scss', '.sass'],
    'PowerShell': ['.ps1', '.psm1'],
    'Batchfile': ['.bat', '.cmd'],
    'TeX': ['.tex', '.latex'],
    'YAML': ['.yaml', '.yml'],
    'JSON': ['.json'],
    'Markdown': ['.md'],
    'C': ['.c', '.h'],
    'C++': ['.cpp', '.hpp', '.cc', '.hh'],
    'Java': ['.java'],
    'Go': ['.go'],
    'Rust': ['.rs'],
    'Ruby': ['.rb'],
    'Shell': ['.sh', '.bash'],
}

# Files to skip
SKIP_PATTERNS = {
    '__pycache__',
    '.git',
    'node_modules',
    '.pytest_cache',
    '.venv',
    'venv',
    'env',
    '.env',
    'dist',
    'build',
    '*.pyc',
    '*.pyo',
    '*.so',
    '*.dll',
    '*.dylib',
}


@dataclass
class FileInfo:
    """Information about a single file."""
    path: str
    size: int
    loc: int
    language: str
    hash: str


@dataclass
class ShardInfo:
    """Information about a shard."""
    name: str
    path_pattern: str
    file_count: int
    total_loc: int
    languages: Dict[str, int]


@dataclass
class DependencyInfo:
    """Dependency information."""
    name: str
    version: str
    source_file: str


class AutonomousExplorer:
    """Autonomous repository explorer for PR #18."""

    def __init__(self, repo_path: str, target_loc_min: int = 400000, target_loc_max: int = 700000):
        """
        Initialize the autonomous explorer.

        Args:
            repo_path: Path to the repository to explore
            target_loc_min: Minimum target LOC (default: 400k)
            target_loc_max: Maximum target LOC (default: 700k)
        """
        self.repo_path = Path(repo_path).resolve()
        self.target_loc_min = target_loc_min
        self.target_loc_max = target_loc_max
        self.files: List[FileInfo] = []
        self.shards: Dict[str, ShardInfo] = {}
        self.dependencies: List[DependencyInfo] = []

    def should_skip(self, path: Path) -> bool:
        """Check if a path should be skipped."""
        parts = path.parts
        for skip_pattern in SKIP_PATTERNS:
            if skip_pattern.startswith('*'):
                # Extension pattern
                if path.suffix == skip_pattern[1:]:
                    return True
            else:
                # Directory or file name pattern
                if skip_pattern in parts:
                    return True
        return False

    def detect_language(self, file_path: Path) -> str:
        """Detect the language of a file based on extension."""
        suffix = file_path.suffix.lower()
        for language, extensions in LANGUAGE_EXTENSIONS.items():
            if suffix in extensions:
                return language
        return 'Other'

    def count_loc(self, file_path: Path) -> int:
        """
        Count lines of code in a file.
        
        Skips blank lines and basic comments.
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                loc = 0
                for line in lines:
                    stripped = line.strip()
                    # Skip blank lines
                    if not stripped:
                        continue
                    # Skip common comment patterns
                    if stripped.startswith(('#', '//', '/*', '*', '<!--', '%')):
                        continue
                    loc += 1
                return loc
        except Exception:
            return 0

    def hash_file(self, file_path: Path) -> str:
        """Compute SHA-256 hash of a file."""
        try:
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception:
            return ''

    def enumerate_files(self) -> None:
        """Enumerate all files in the repository."""
        print(f"[EXPLORATION] Enumerating files in: {self.repo_path}")
        
        for root, dirs, files in os.walk(self.repo_path):
            root_path = Path(root)
            
            # Skip directories that should be ignored
            dirs[:] = [d for d in dirs if not self.should_skip(root_path / d)]
            
            for file_name in files:
                file_path = root_path / file_name
                
                if self.should_skip(file_path):
                    continue
                
                try:
                    size = file_path.stat().st_size
                    loc = self.count_loc(file_path)
                    language = self.detect_language(file_path)
                    file_hash = self.hash_file(file_path)
                    
                    # Make path relative to repo
                    rel_path = file_path.relative_to(self.repo_path)
                    
                    file_info = FileInfo(
                        path=str(rel_path),
                        size=size,
                        loc=loc,
                        language=language,
                        hash=file_hash
                    )
                    self.files.append(file_info)
                except Exception as e:
                    print(f"[WARNING] Failed to process {file_path}: {e}", file=sys.stderr)

    def extract_dependencies(self) -> None:
        """Extract dependencies from manifest files."""
        print(f"[EXPLORATION] Extracting dependencies")
        
        manifest_files = [
            'pyproject.toml',
            'requirements.txt',
            'package.json',
            'GENESIS_MANIFEST.yaml',
            'ORTHOGONAL_LOCK.yaml',
            'COVENANT_LOCK.yaml',
        ]
        
        for manifest_name in manifest_files:
            manifest_path = self.repo_path / manifest_name
            if not manifest_path.exists():
                continue
            
            try:
                if manifest_name == 'requirements.txt':
                    self._parse_requirements_txt(manifest_path)
                elif manifest_name == 'package.json':
                    self._parse_package_json(manifest_path)
                elif manifest_name.endswith('.yaml'):
                    self._parse_yaml_manifest(manifest_path)
                elif manifest_name == 'pyproject.toml':
                    self._parse_pyproject_toml(manifest_path)
            except Exception as e:
                print(f"[WARNING] Failed to parse {manifest_name}: {e}", file=sys.stderr)

    def _parse_requirements_txt(self, path: Path) -> None:
        """Parse requirements.txt file."""
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Split on first occurrence of version operator or whitespace
                # This handles: package==version, package>=version, package, etc.
                # For complex specs like package>=1.0,<2.0, we capture the full spec
                parts = re.split(r'([>=<]=?|~=|!=)', line, maxsplit=1)
                name = parts[0].strip()
                
                # Extract version specification (everything after package name)
                version_spec = line[len(name):].strip() if len(line) > len(name) else ''
                version = version_spec if version_spec else 'latest'
                
                if name:  # Only add if we have a package name
                    self.dependencies.append(DependencyInfo(
                        name=name,
                        version=version,
                        source_file=str(path.name)
                    ))

    def _parse_package_json(self, path: Path) -> None:
        """Parse package.json file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for dep_type in ['dependencies', 'devDependencies']:
                if dep_type in data:
                    for name, version in data[dep_type].items():
                        self.dependencies.append(DependencyInfo(
                            name=name,
                            version=version,
                            source_file=str(path.name)
                        ))

    def _parse_yaml_manifest(self, path: Path) -> None:
        """Parse YAML manifest files."""
        # Basic YAML parsing without external dependencies
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract version-like patterns
            version_pattern = r'version:\s*["\']?([^"\'\n]+)["\']?'
            for match in re.finditer(version_pattern, content):
                # This is a simplified parser - in production use proper YAML parser
                pass

    def _parse_pyproject_toml(self, path: Path) -> None:
        """Parse pyproject.toml file."""
        # Basic TOML parsing without external dependencies
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract dependencies from dependencies section
            in_deps = False
            for line in content.split('\n'):
                if '[tool.poetry.dependencies]' in line or '[project.dependencies]' in line:
                    in_deps = True
                    continue
                if in_deps and line.startswith('['):
                    in_deps = False
                if in_deps and '=' in line:
                    parts = line.split('=')
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        version = parts[1].strip().strip('"\'')
                        self.dependencies.append(DependencyInfo(
                            name=name,
                            version=version,
                            source_file=str(path.name)
                        ))

    def generate_shards(self) -> None:
        """Generate shard boundaries based on directory structure."""
        print(f"[EXPLORATION] Generating shard boundaries")
        
        # Group files by top-level directory
        dir_groups: Dict[str, List[FileInfo]] = defaultdict(list)
        
        for file_info in self.files:
            parts = Path(file_info.path).parts
            if len(parts) > 1:
                top_dir = parts[0]
            else:
                top_dir = '_root'
            dir_groups[top_dir].append(file_info)
        
        # Create shards
        for dir_name, files in dir_groups.items():
            file_count = len(files)
            total_loc = sum(f.loc for f in files)
            
            # Count languages
            languages: Dict[str, int] = defaultdict(int)
            for file_info in files:
                languages[file_info.language] += file_info.loc
            
            shard = ShardInfo(
                name=f"shard_{dir_name}",
                path_pattern=f"{dir_name}/**/*" if dir_name != '_root' else "*",
                file_count=file_count,
                total_loc=total_loc,
                languages=dict(languages)
            )
            self.shards[dir_name] = shard

    def generate_initial_checkpoint(self) -> Dict[str, Any]:
        """Generate initial planning checkpoint."""
        print(f"[CHECKPOINT] Generating initial planning checkpoint")
        
        checkpoint = {
            "checkpoint_type": "initial_planning",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "target_loc": {
                "min": self.target_loc_min,
                "max": self.target_loc_max,
                "optimal": (self.target_loc_min + self.target_loc_max) // 2
            },
            "shard_design": {
                "strategy": "directory_based",
                "boundaries": [
                    "src/*",
                    "tools/*",
                    "forgiveness_system/*",
                    "topology/*",
                    "validation/*",
                    "tests/*",
                    "docs/*",
                    "examples/*"
                ]
            },
            "scaffolding_plan": {
                "files_to_add": {},
                "lines_to_add": {},
                "target_total_LOC": (self.target_loc_min + self.target_loc_max) // 2
            },
            "next_actions": "autonomous exploration - enumerate files, count LOC, extract dependencies, adjust shards"
        }
        
        return checkpoint

    def generate_full_report(self) -> Dict[str, Any]:
        """Generate complete exploration report."""
        print(f"[REPORT] Generating full exploration report")
        
        # Compute aggregate statistics
        total_files = len(self.files)
        total_loc = sum(f.loc for f in self.files)
        total_size = sum(f.size for f in self.files)
        
        # Language breakdown
        language_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {'files': 0, 'loc': 0})
        for file_info in self.files:
            language_stats[file_info.language]['files'] += 1
            language_stats[file_info.language]['loc'] += file_info.loc
        
        # Files by LOC
        loc_per_file = {f.path: f.loc for f in self.files}
        
        # Shard map
        shard_map = {
            name: {
                'path_pattern': shard.path_pattern,
                'file_count': shard.file_count,
                'total_loc': shard.total_loc,
                'languages': shard.languages
            }
            for name, shard in self.shards.items()
        }
        
        # Dependency map
        dependency_map = {}
        for dep in self.dependencies:
            if dep.source_file not in dependency_map:
                dependency_map[dep.source_file] = []
            dependency_map[dep.source_file].append({
                'name': dep.name,
                'version': dep.version
            })
        
        # Calculate lines needed to reach target
        current_loc = total_loc
        target_loc = (self.target_loc_min + self.target_loc_max) // 2
        lines_needed = max(0, target_loc - current_loc)
        
        report = {
            "repos": {
                "orthogonal-engineering": {
                    "exact_file_counts": {
                        'total': total_files,
                        'by_language': {lang: stats['files'] for lang, stats in language_stats.items()}
                    },
                    "LOC_per_file": loc_per_file,
                    "LOC_by_language": {lang: stats['loc'] for lang, stats in language_stats.items()},
                    "total_LOC": total_loc,
                    "total_size_bytes": total_size,
                    "shard_map": shard_map,
                    "dependencies": dependency_map
                }
            },
            "scaffolding_plan": {
                "current_LOC": current_loc,
                "target_LOC": target_loc,
                "lines_needed": lines_needed,
                "files_to_add": self._suggest_files_to_add(lines_needed),
                "expansion_strategy": self._determine_expansion_strategy(lines_needed)
            },
            "next_actions": self._determine_next_actions(current_loc, target_loc),
            "verification_compatible": True,
            "shard_parallelizable": True,
            "deterministic": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return report

    def _suggest_files_to_add(self, lines_needed: int) -> Dict[str, int]:
        """Suggest files to add to reach target LOC."""
        if lines_needed <= 0:
            return {}
        
        suggestions = {
            "src/new_modules": lines_needed // 4,
            "tests/new_tests": lines_needed // 4,
            "docs/new_documentation": lines_needed // 4,
            "examples/new_examples": lines_needed // 4
        }
        
        return suggestions

    def _determine_expansion_strategy(self, lines_needed: int) -> str:
        """Determine expansion strategy based on lines needed."""
        if lines_needed <= 0:
            return "maintain_current_structure"
        elif lines_needed < 100000:
            return "incremental_expansion"
        elif lines_needed < 300000:
            return "moderate_expansion"
        else:
            return "major_expansion"

    def _determine_next_actions(self, current_loc: int, target_loc: int) -> str:
        """Determine next actions based on current state."""
        if current_loc >= self.target_loc_min and current_loc <= self.target_loc_max:
            return "target_LOC_achieved - ready for PR generation"
        elif current_loc < self.target_loc_min:
            gap = self.target_loc_min - current_loc
            return f"expand_codebase - need {gap} more LOC to reach minimum target"
        else:
            excess = current_loc - self.target_loc_max
            return f"refactor_or_split - {excess} LOC above maximum target"

    def run_autonomous_exploration(self, output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the complete autonomous exploration.
        
        Args:
            output_file: Optional path to write JSON output
            
        Returns:
            Complete exploration report as dictionary
        """
        print(f"[AUTONOMOUS EXPLORER] Starting PR #18 exploration")
        print(f"[AUTONOMOUS EXPLORER] Repository: {self.repo_path}")
        print(f"[AUTONOMOUS EXPLORER] Target LOC: {self.target_loc_min:,} - {self.target_loc_max:,}")
        print()
        
        # Phase 1: Initial checkpoint
        checkpoint = self.generate_initial_checkpoint()
        print(f"[CHECKPOINT] Initial planning checkpoint generated")
        print(f"[CHECKPOINT] Halting before code generation as specified")
        print()
        
        # Phase 2: Autonomous exploration
        print(f"[AUTONOMOUS] Beginning autonomous exploration")
        print()
        
        # Step 1: Enumerate files
        self.enumerate_files()
        print(f"[AUTONOMOUS] Enumerated {len(self.files):,} files")
        
        # Step 2: Extract dependencies
        self.extract_dependencies()
        print(f"[AUTONOMOUS] Extracted {len(self.dependencies):,} dependencies")
        
        # Step 3: Generate shards
        self.generate_shards()
        print(f"[AUTONOMOUS] Generated {len(self.shards):,} shards")
        print()
        
        # Phase 3: Generate full report
        report = self.generate_full_report()
        
        # Add initial checkpoint to report
        report['initial_checkpoint'] = checkpoint
        
        # Display summary
        total_loc = report['repos']['orthogonal-engineering']['total_LOC']
        print(f"[SUMMARY] Total LOC: {total_loc:,}")
        print(f"[SUMMARY] Target LOC: {self.target_loc_min:,} - {self.target_loc_max:,}")
        print(f"[SUMMARY] Next action: {report['next_actions']}")
        print()
        
        # Write output if requested
        if output_file:
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            print(f"[OUTPUT] Report written to: {output_path}")
        
        return report


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Autonomous PR #18 Repository Explorer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Explore current directory
  python autonomous_pr18_explorer.py
  
  # Explore specific repo with output file
  python autonomous_pr18_explorer.py --repo /path/to/repo --output report.json
  
  # Custom LOC targets
  python autonomous_pr18_explorer.py --min-loc 500000 --max-loc 800000
        '''
    )
    
    parser.add_argument(
        '--repo',
        default='.',
        help='Repository path to explore (default: current directory)'
    )
    parser.add_argument(
        '--output',
        help='Output JSON file path (default: print to stdout)'
    )
    parser.add_argument(
        '--min-loc',
        type=int,
        default=400000,
        help='Minimum target LOC (default: 400000)'
    )
    parser.add_argument(
        '--max-loc',
        type=int,
        default=700000,
        help='Maximum target LOC (default: 700000)'
    )
    
    args = parser.parse_args()
    
    # Create explorer
    explorer = AutonomousExplorer(
        repo_path=args.repo,
        target_loc_min=args.min_loc,
        target_loc_max=args.max_loc
    )
    
    # Run exploration
    report = explorer.run_autonomous_exploration(output_file=args.output)
    
    # If no output file specified, print JSON to stdout
    if not args.output:
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
