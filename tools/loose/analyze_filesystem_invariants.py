#!/usr/bin/env python3
"""
Filesystem Invariant Analysis for Orthogonal Engineering

This script analyzes MASTER_INDEX.csv to detect canal-like structures
and compute invariants that validate the methodology claims.

Invariants detected:
- Canal structures: tests/, config files, schemas, CI configs
- Project structure patterns: package.json, requirements.txt, etc.
- Evidence of structured extraction (INVARIANT tags, CRAFTSMAN tags)
"""

import csv
import json
import re
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional

# Canal detection patterns (structural invariants)
CANAL_PATTERNS = {
    'test_structure': [
        r'test[s]?[/\\]',
        r'__test__',
        r'\.test\.',
        r'\.spec\.',
        r'/tests/',
        r'\btest\b'
    ],
    'config_structure': [
        r'\.config\.',
        r'config[/\\]',
        r'\.ini$',
        r'\.toml$',
        r'\.yaml$',
        r'\.yml$',
        r'\.json$',  # Many configs are JSON
        r'\.env',
        r'\.gitignore',
        r'\.gitattributes'
    ],
    'schema_structure': [
        r'schema[/\\]',
        r'\.schema\.',
        r'\.proto$',
        r'\.graphql$',
        r'\.avsc$',
        r'\.xsd$'
    ],
    'ci_structure': [
        r'\.github[/\\]',
        r'\.gitlab-ci\.yml',
        r'\.travis\.yml',
        r'\.circleci[/\\]',
        r'\.azure-pipelines\.yml',
        r'\.jenkinsfile',
        r'ci[/\\]'
    ],
    'package_structure': [
        r'package\.json',
        r'requirements\.txt',
        r'pyproject\.toml',
        r'Pipfile',
        r'poetry\.lock',
        r'Cargo\.toml',
        r'go\.mod',
        r'pom\.xml',
        r'build\.gradle'
    ],
    'documentation_structure': [
        r'README\.',
        r'\.md$',
        r'docs[/\\]',
        r'documentation[/\\]',
        r'\.rst$'
    ]
}

# Invariant extraction patterns (from methodology)
INVARIANT_EXTRACTION_PATTERNS = {
    'invariant_tag': r'\[INVARIANT\]',
    'craftsman_tag': r'\[CRAFTSMAN\]',
    'canal_marker': r'\[CANAL\]',
    'structured_output': r'\{.*\}',  # JSON-like structures
    'enum_pattern': r'enum\s+\w+',
    'type_definition': r'(type|interface|class)\s+\w+'
}

def detect_canal_structure(filepath: str, filename: str) -> Dict[str, bool]:
    """Detect if a file is part of a canal structure."""
    full_path = f"{filepath}/{filename}".lower()
    detected = {}
    
    for canal_type, patterns in CANAL_PATTERNS.items():
        detected[canal_type] = any(
            re.search(pattern, full_path, re.IGNORECASE) 
            for pattern in patterns
        )
    
    return detected

def detect_invariant_markers(filepath: str, filename: str, extension: str) -> Dict[str, bool]:
    """Detect invariant extraction markers in file paths/names."""
    full_path = f"{filepath}/{filename}".lower()
    detected = {}
    
    for marker_type, pattern in INVARIANT_EXTRACTION_PATTERNS.items():
        detected[marker_type] = bool(
            re.search(pattern, full_path, re.IGNORECASE)
        )
    
    return detected

def classify_project_type(filepath: str, extension: str, project_tag: str) -> str:
    """Classify project type based on structure."""
    path_lower = filepath.lower()
    
    # Code projects
    if any(x in path_lower for x in ['.git', 'node_modules', 'src/', 'lib/']):
        return 'code_project'
    
    # AI work (conversations, embeddings)
    if 'conversation' in path_lower or 'embedding' in path_lower or extension == '.json':
        if project_tag in ['INVARIANT', 'CRAFTSMAN', 'AI_ARCHAEOLOGY']:
            return 'ai_work_structured'
        return 'ai_work_raw'
    
    # Game mods
    if project_tag in ['MINECRAFT', 'RDR2'] or extension in ['.pak', '.fbmod']:
        return 'game_mod'
    
    # Archives
    if extension in ['.zip', '.7z', '.rar', '.tar', '.gz']:
        return 'archive'
    
    return 'other'

def analyze_csv(csv_path: str) -> Dict:
    """Main analysis function."""
    print(f"Analyzing {csv_path}...")
    
    canal_counts = defaultdict(int)
    invariant_marker_counts = defaultdict(int)
    project_type_counts = defaultdict(int)
    extension_counts = Counter()
    project_tag_counts = Counter()
    
    canal_by_project = defaultdict(lambda: defaultdict(int))
    invariant_by_project = defaultdict(lambda: defaultdict(int))
    
    total_files = 0
    total_size_bytes = 0
    
    code_projects = set()
    projects_with_tests = set()
    projects_with_configs = set()
    projects_with_schemas = set()
    projects_with_ci = set()
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            total_files += 1
            try:
                total_size_bytes += int(row.get('size_bytes', 0))
            except (ValueError, TypeError):
                pass
            
            filepath = row.get('filepath', '')
            filename = row.get('filename', '')
            extension = row.get('extension', '')
            project_tag = row.get('project_tag', 'UNCATEGORIZED')
            
            # Detect canal structures
            canals = detect_canal_structure(filepath, filename)
            for canal_type, detected in canals.items():
                if detected:
                    canal_counts[canal_type] += 1
                    canal_by_project[project_tag][canal_type] += 1
                    
                    # Track which projects have which canals
                    project_root = filepath.split('\\')[0] if '\\' in filepath else filepath.split('/')[0]
                    if canal_type == 'test_structure':
                        projects_with_tests.add(project_root)
                    elif canal_type == 'config_structure':
                        projects_with_configs.add(project_root)
                    elif canal_type == 'schema_structure':
                        projects_with_schemas.add(project_root)
                    elif canal_type == 'ci_structure':
                        projects_with_ci.add(project_root)
            
            # Detect invariant markers
            invariants = detect_invariant_markers(filepath, filename, extension)
            for marker_type, detected in invariants.items():
                if detected:
                    invariant_marker_counts[marker_type] += 1
                    invariant_by_project[project_tag][marker_type] += 1
            
            # Classify project type
            project_type = classify_project_type(filepath, extension, project_tag)
            project_type_counts[project_type] += 1
            
            # Count extensions and project tags
            if extension:
                extension_counts[extension] += 1
            project_tag_counts[project_tag] += 1
            
            # Track code projects
            if project_type == 'code_project':
                project_root = filepath.split('\\')[0] if '\\' in filepath else filepath.split('/')[0]
                code_projects.add(project_root)
    
    # Compute canal coverage statistics
    canal_coverage = {
        'projects_with_tests': len(projects_with_tests),
        'projects_with_configs': len(projects_with_configs),
        'projects_with_schemas': len(projects_with_schemas),
        'projects_with_ci': len(projects_with_ci),
        'total_code_projects': len(code_projects)
    }
    
    # Compute invariant extraction evidence
    invariant_evidence = {
        'invariant_tagged_files': project_tag_counts.get('INVARIANT', 0),
        'craftsman_tagged_files': project_tag_counts.get('CRAFTSMAN', 0),
        'total_tagged_files': project_tag_counts.get('INVARIANT', 0) + project_tag_counts.get('CRAFTSMAN', 0),
        'tagging_rate': (project_tag_counts.get('INVARIANT', 0) + project_tag_counts.get('CRAFTSMAN', 0)) / max(total_files, 1)
    }
    
    return {
        'metadata': {
            'analysis_date': datetime.now().isoformat(),
            'source_file': csv_path,
            'total_files': total_files,
            'total_size_gb': round(total_size_bytes / (1024**3), 2)
        },
        'canal_detection': {
            'canal_counts': dict(canal_counts),
            'canal_by_project': {k: dict(v) for k, v in canal_by_project.items()},
            'canal_coverage': canal_coverage
        },
        'invariant_detection': {
            'marker_counts': dict(invariant_marker_counts),
            'marker_by_project': {k: dict(v) for k, v in invariant_by_project.items()},
            'tagging_evidence': invariant_evidence
        },
        'project_classification': {
            'by_type': dict(project_type_counts),
            'by_tag': dict(project_tag_counts),
            'top_extensions': dict(extension_counts.most_common(20))
        },
        'methodology_validation': {
            'canal_structures_found': sum(1 for v in canal_counts.values() if v > 0),
            'invariant_markers_found': sum(1 for v in invariant_marker_counts.values() if v > 0),
            'structured_projects': len(code_projects),
            'canal_coverage_rate': len(projects_with_configs) / max(len(code_projects), 1) if code_projects else 0
        }
    }

if __name__ == '__main__':
    import sys
    
    csv_path = sys.argv[1] if len(sys.argv) > 1 else r'c:\Users\Aidor\Desktop\MASTER_INDEX.csv'
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'data/filesystem_invariants_analysis.json'
    
    print(f"Reading from: {csv_path}")
    print(f"Writing to: {output_path}")
    
    results = analyze_csv(csv_path)
    
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nAnalysis complete!")
    print(f"Total files analyzed: {results['metadata']['total_files']}")
    print(f"Total size: {results['metadata']['total_size_gb']} GB")
    print(f"\nCanal structures detected:")
    for canal, count in results['canal_detection']['canal_counts'].items():
        print(f"  {canal}: {count}")
    print(f"\nInvariant markers detected:")
    for marker, count in results['invariant_detection']['marker_counts'].items():
        print(f"  {marker}: {count}")
    print(f"\nMethodology validation:")
    print(f"  Canal structures found: {results['methodology_validation']['canal_structures_found']}")
    print(f"  Invariant markers found: {results['methodology_validation']['invariant_markers_found']}")
    print(f"  Structured projects: {results['methodology_validation']['structured_projects']}")
    print(f"  Canal coverage rate: {results['methodology_validation']['canal_coverage_rate']:.2%}")
