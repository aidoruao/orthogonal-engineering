#!/usr/bin/env python3
"""
Repository Health Assessment Tool
Applies orthogonal engineering methodology to repository assessment.
"""
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

def calculate_file_hash(filepath):
    """Calculate SHA256 hash of file."""
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None

def assess_repository(repo_path):
    """Comprehensive repository health assessment."""
    repo_path = Path(repo_path)
    if not repo_path.exists():
        return None
    
    assessment = {
        'path': str(repo_path),
        'assessment_time': datetime.now().isoformat(),
        'exists': repo_path.exists(),
        'is_directory': repo_path.is_dir(),
        'file_count': 0,
        'directory_count': 0,
        'total_size': 0,
        'key_files': {},
        'git_present': False,
        'git_status': None,
        'structure_score': 0,
        'completeness_score': 0,
        'health_status': 'unknown'
    }
    
    # Check for git
    git_dir = repo_path / '.git'
    assessment['git_present'] = git_dir.exists()
    
    # Count files and directories
    for root, dirs, files in os.walk(repo_path):
        assessment['directory_count'] += len(dirs)
        assessment['file_count'] += len(files)
        for file in files:
            filepath = Path(root) / file
            try:
                assessment['total_size'] += filepath.stat().st_size
            except:
                pass
    
    # Check key files (orthogonal engineering specific)
    key_files = [
        'README.md',
        'FORMAL_FOUNDATIONS.md',
        'INVARIANTS.md',
        'FAILURES.md',
        'canal_detector.py',
        'correspondence_validator.py',
        'requirements.txt',
        '.gitignore'
    ]
    
    for key_file in key_files:
        filepath = repo_path / key_file
        if filepath.exists():
            file_hash = calculate_file_hash(filepath)
            assessment['key_files'][key_file] = {
                'exists': True,
                'hash': file_hash,
                'size': filepath.stat().st_size if filepath.exists() else 0
            }
        else:
            assessment['key_files'][key_file] = {'exists': False}
    
    # Calculate scores
    existing_key_files = sum(1 for f in assessment['key_files'].values() if f['exists'])
    assessment['completeness_score'] = existing_key_files / len(key_files) if key_files else 0
    
    # Structure score based on directory organization
    expected_dirs = ['analysis', 'evidence', 'methodology', 'tools']
    existing_dirs = []
    for dir_name in expected_dirs:
        if (repo_path / dir_name).exists():
            existing_dirs.append(dir_name)
    assessment['structure_score'] = len(existing_dirs) / len(expected_dirs) if expected_dirs else 0
    
    # Overall health
    total_score = (assessment['completeness_score'] + assessment['structure_score']) / 2
    if total_score >= 0.8:
        assessment['health_status'] = 'healthy'
    elif total_score >= 0.5:
        assessment['health_status'] = 'partial'
    else:
        assessment['health_status'] = 'fragmented'
    
    assessment['total_score'] = total_score
    
    return assessment

def main():
    """Main assessment function."""
    if len(sys.argv) < 2:
        print("Usage: python assess_repository.py <repo_path1> <repo_path2> ...")
        sys.exit(1)
    
    assessments = []
    for repo_path in sys.argv[1:]:
        print(f"Assessing: {repo_path}")
        assessment = assess_repository(repo_path)
        if assessment:
            assessments.append(assessment)
    
    # Output results
    output_file = f"repository_assessments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(assessments, f, indent=2, ensure_ascii=False)
    
    print(f"\nAssessment complete. Results saved to: {output_file}")
    
    # Print summary
    print("\n=== REPOSITORY ASSESSMENT SUMMARY ===")
    for assessment in assessments:
        print(f"\nRepository: {assessment['path']}")
        print(f"  Health: {assessment['health_status']} (Score: {assessment['total_score']:.1%})")
        print(f"  Files: {assessment['file_count']}, Size: {assessment['total_size']:,} bytes")
        print(f"  Git: {'Present' if assessment['git_present'] else 'Missing'}")
        print(f"  Key files: {sum(1 for f in assessment['key_files'].values() if f['exists'])}/{len(assessment['key_files'])}")

if __name__ == '__main__':
    main()
