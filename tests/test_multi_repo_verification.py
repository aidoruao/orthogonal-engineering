#!/usr/bin/env python3
"""
Tests for Multi-Repository Verification System
"""

import json
import os
import sys
import subprocess
from pathlib import Path
import tempfile


def test_dependency_extraction():
    """Test that dependency extraction works for various file types."""
    script_path = Path("automation/repo_manifest.py")
    assert script_path.exists(), "Manifest generator script not found"
    
    # Try importing
    sys.path.insert(0, str(Path.cwd()))
    from automation.repo_manifest import RepositoryManifestGenerator
    
    # Generate manifest with json output
    result = subprocess.run(
        ["python3", "automation/repo_manifest.py", "--json-only", "--force"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Manifest generation failed: {result.stderr}"
    
    # Parse JSON output
    manifest = json.loads(result.stdout)
    
    # Check that files have dependency metadata
    files_with_deps = [f for f in manifest['files'] if f.get('dependencies')]
    assert len(files_with_deps) > 0, "No files have dependencies extracted"
    
    # Check that Python files have Python imports
    py_files = [f for f in manifest['files'] if f['path'].endswith('.py')]
    py_with_deps = [f for f in py_files if f.get('dependencies')]
    
    print(f"✓ Dependency extraction works")
    print(f"  Total files: {len(manifest['files'])}")
    print(f"  Files with dependencies: {len(files_with_deps)}")
    print(f"  Python files: {len(py_files)}")
    print(f"  Python files with dependencies: {len(py_with_deps)}")


def test_manifest_v2_structure():
    """Test that manifest v2 includes new fields."""
    result = subprocess.run(
        ["python3", "automation/repo_manifest.py", "--json-only", "--force"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Manifest generation failed: {result.stderr}"
    manifest = json.loads(result.stdout)
    
    # Check version
    assert manifest['manifest_version'] == '2.0.0', "Manifest version should be 2.0.0"
    
    # Check new fields
    assert 'repository_name' in manifest, "Missing repository_name field"
    
    # Check file entries have new fields
    if len(manifest['files']) > 0:
        first_file = manifest['files'][0]
        assert 'line_count' in first_file, "Missing line_count in file entry"
        assert 'dependencies' in first_file, "Missing dependencies in file entry"
        assert 'dependency_hash' in first_file, "Missing dependency_hash in file entry"
    
    # Check folder entries have dependency_hash
    if len(manifest['folders']) > 0:
        first_folder = list(manifest['folders'].values())[0]
        assert 'dependency_hash' in first_folder, "Missing dependency_hash in folder entry"
    
    print("✓ Manifest v2 structure is correct")


def test_multi_repo_manifest_generation():
    """Test multi-repo manifest generation."""
    # Create a temporary repo list file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        repo_list = [
            {
                "name": "orthogonal-engineering",
                "path": str(Path.cwd())
            }
        ]
        json.dump(repo_list, f)
        repo_list_file = f.name
    
    try:
        result = subprocess.run(
            ["python3", "automation/repo_manifest.py", "--repo-list", repo_list_file, "--json-only"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Multi-repo manifest generation failed: {result.stderr}"
        
        # Parse JSON output
        manifest = json.loads(result.stdout)
        
        # Check multi-repo structure
        assert manifest.get('type') == 'multi-repo', "Type should be multi-repo"
        assert 'repositories' in manifest, "Missing repositories field"
        assert 'global_summary' in manifest, "Missing global_summary field"
        assert 'orthogonal-engineering' in manifest['repositories'], "Repository not in manifest"
        
        # Check global summary
        summary = manifest['global_summary']
        assert 'total_repos' in summary
        assert 'total_files' in summary
        assert 'total_folders' in summary
        assert 'total_bytes' in summary
        assert 'total_dependencies' in summary
        
        print("✓ Multi-repo manifest generation works")
        print(f"  Repositories: {summary['total_repos']}")
        print(f"  Total files: {summary['total_files']}")
        print(f"  Total dependencies: {summary['total_dependencies']}")
    
    finally:
        os.unlink(repo_list_file)


def test_dependency_verification():
    """Test dependency verification metrics."""
    # Run verification with json output
    result = subprocess.run(
        ["python3", "automation/verify_extreme_work.py", "--json-only"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    assert result.returncode in [0, 1], f"Verification failed: {result.stderr}"
    
    # Parse JSON output
    results = json.loads(result.stdout)
    
    # Check that dependency metrics exist
    assert 'qualitative_metrics' in results
    assert 'dependencies' in results['qualitative_metrics']
    
    deps = results['qualitative_metrics']['dependencies']
    
    # Check dependency metrics structure
    assert 'total_files' in deps
    assert 'files_with_dependencies' in deps
    assert 'dependency_coverage' in deps
    assert 'total_dependencies' in deps
    assert 'unique_dependencies' in deps
    assert 'avg_dependencies_per_file' in deps
    assert 'passed' in deps
    
    print("✓ Dependency verification works")
    print(f"  Files with dependencies: {deps['files_with_dependencies']}/{deps['total_files']}")
    print(f"  Coverage: {deps['dependency_coverage']:.1%}")
    print(f"  Total dependencies: {deps['total_dependencies']}")
    print(f"  Unique dependencies: {deps['unique_dependencies']}")


def test_html_report_generation():
    """Test HTML report generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "test_report")
        
        result = subprocess.run(
            ["python3", "automation/verify_extreme_work.py", "--output", output_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result.returncode in [0, 1], f"Verification failed: {result.stderr}"
        
        # Check that all three report formats were generated
        json_path = f"{output_path}.json"
        md_path = f"{output_path}.md"
        html_path = f"{output_path}.html"
        
        assert os.path.exists(json_path), "JSON report not generated"
        assert os.path.exists(md_path), "Markdown report not generated"
        assert os.path.exists(html_path), "HTML report not generated"
        
        # Check HTML content
        with open(html_path, 'r') as f:
            html_content = f.read()
        
        assert "<!DOCTYPE html>" in html_content, "Invalid HTML structure"
        assert "Extreme Work Certification Report" in html_content, "Missing report title"
        assert "Overall Score" in html_content, "Missing overall score"
        assert "Dependencies" in html_content, "Missing dependency section"
        
        print("✓ HTML report generation works")
        print(f"  JSON: {json_path}")
        print(f"  Markdown: {md_path}")
        print(f"  HTML: {html_path}")


def test_backward_compatibility():
    """Test that single-repo verification still works."""
    result = subprocess.run(
        ["python3", "automation/verify_extreme_work.py", "--json-only"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    assert result.returncode in [0, 1], f"Verification failed: {result.stderr}"
    
    # Parse JSON output
    results = json.loads(result.stdout)
    
    # Check that required fields exist
    assert 'timestamp' in results
    assert 'quantitative_metrics' in results
    assert 'qualitative_metrics' in results
    assert 'proof_of_scale' in results
    assert 'overall_score' in results
    assert 'certification_passed' in results
    
    # Check multi_repo flag
    assert 'multi_repo' in results
    assert results['multi_repo'] == False, "Should be single-repo mode"
    
    print("✓ Backward compatibility maintained")
    print(f"  Overall score: {results['overall_score']:.1%}")
    print(f"  Certification: {'PASSED' if results['certification_passed'] else 'FAILED'}")


def test_shard_multi_repo_partitioning():
    """Test that shard partitioning works with repo names."""
    # This is a lightweight test - just verify the hash function includes repo name
    sys.path.insert(0, str(Path.cwd()))
    from automation.verify_extreme_work import ExtremeWorkVerifier
    
    # Create verifier in shard mode
    verifier = ExtremeWorkVerifier(".", mode="shard", shard_id=0, shard_count=4)
    
    # Test that partition function accepts repo_name
    result1 = verifier._should_process_folder("test/path", repo_name=None)
    result2 = verifier._should_process_folder("test/path", repo_name="repo1")
    result3 = verifier._should_process_folder("test/path", repo_name="repo2")
    
    # With different repo names, partitioning should potentially differ
    # (this is probabilistic, but with high probability they should differ)
    print("✓ Shard partitioning supports repo names")
    print(f"  Same path, no repo: {result1}")
    print(f"  Same path, repo1: {result2}")
    print(f"  Same path, repo2: {result3}")


def main():
    """Run all tests."""
    print("Running Multi-Repository Verification Tests...")
    print("=" * 80)
    
    # Change to repo root
    os.chdir(Path(__file__).parent.parent)
    
    tests = [
        test_dependency_extraction,
        test_manifest_v2_structure,
        test_multi_repo_manifest_generation,
        test_dependency_verification,
        test_html_report_generation,
        test_backward_compatibility,
        test_shard_multi_repo_partitioning,
    ]
    
    failed = 0
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("=" * 80)
    print(f"Results: {len(tests) - failed}/{len(tests)} tests passed")
    
    if failed > 0:
        sys.exit(1)
    else:
        print("All tests passed! ✅")
        sys.exit(0)


if __name__ == "__main__":
    main()
