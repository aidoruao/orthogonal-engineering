#!/usr/bin/env python3
"""
Tests for Repository Manifest Generation
"""

import json
import os
import sys
import subprocess
from pathlib import Path


def test_manifest_module_exists():
    """Test that manifest module exists and can be imported."""
    script_path = Path("automation/repo_manifest.py")
    assert script_path.exists(), "Manifest generator script not found"
    
    # Try importing
    sys.path.insert(0, str(Path.cwd()))
    try:
        from automation.repo_manifest import RepositoryManifestGenerator
        print("✓ Manifest module can be imported")
    except ImportError as e:
        raise AssertionError(f"Failed to import manifest module: {e}")


def test_manifest_cli_works():
    """Test that manifest CLI runs successfully."""
    result = subprocess.run(
        ["python3", "automation/repo_manifest.py", "--help"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, "Manifest CLI failed"
    assert "Generate deterministic repository manifest" in result.stdout
    print("✓ Manifest CLI works")


def test_manifest_generation():
    """Test that manifest can be generated."""
    # Generate manifest with json output
    result = subprocess.run(
        ["python3", "automation/repo_manifest.py", "--json-only"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Manifest generation failed: {result.stderr}"
    
    # Parse JSON output
    try:
        manifest = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid JSON output: {e}")
    
    # Verify manifest structure
    assert "manifest_version" in manifest
    assert "commit" in manifest
    assert "generated_at" in manifest
    assert "files" in manifest
    assert "folders" in manifest
    assert "summary" in manifest
    
    print("✓ Manifest can be generated")
    print(f"  Total files: {manifest['summary']['total_files']}")
    print(f"  Total folders: {manifest['summary']['total_folders']}")
    return manifest


def test_manifest_file_structure():
    """Test that manifest files have required fields."""
    result = subprocess.run(
        ["python3", "automation/repo_manifest.py", "--json-only"],
        capture_output=True,
        text=True
    )
    
    manifest = json.loads(result.stdout)
    
    # Check file entries
    assert len(manifest["files"]) > 0, "No files in manifest"
    
    first_file = manifest["files"][0]
    assert "path" in first_file
    assert "size" in first_file
    assert "mtime" in first_file
    assert "sha256" in first_file
    
    print("✓ Manifest file entries have required fields")


def test_manifest_folder_structure():
    """Test that manifest folders have required fields."""
    result = subprocess.run(
        ["python3", "automation/repo_manifest.py", "--json-only"],
        capture_output=True,
        text=True
    )
    
    manifest = json.loads(result.stdout)
    
    # Check folder entries
    assert len(manifest["folders"]) > 0, "No folders in manifest"
    
    # Check root folder
    assert "." in manifest["folders"], "Root folder not in manifest"
    
    root_folder = manifest["folders"]["."]
    assert "file_count" in root_folder
    assert "total_bytes" in root_folder
    assert "artifact_flags" in root_folder
    assert "folder_hash" in root_folder
    
    # Verify folder hash is valid SHA256
    assert len(root_folder["folder_hash"]) == 64, "Invalid folder hash length"
    
    print("✓ Manifest folder entries have required fields")


def test_manifest_determinism():
    """Test that manifest generation is deterministic."""
    # Generate manifest twice
    result1 = subprocess.run(
        ["python3", "automation/repo_manifest.py", "--json-only"],
        capture_output=True,
        text=True
    )
    
    result2 = subprocess.run(
        ["python3", "automation/repo_manifest.py", "--json-only"],
        capture_output=True,
        text=True
    )
    
    manifest1 = json.loads(result1.stdout)
    manifest2 = json.loads(result2.stdout)
    
    # Compare file lists (should be identical except for timestamp)
    files1 = sorted([f["path"] for f in manifest1["files"]])
    files2 = sorted([f["path"] for f in manifest2["files"]])
    
    assert files1 == files2, "File lists differ between runs"
    
    # Compare folder hashes (should be identical)
    for folder_path, folder_data in manifest1["folders"].items():
        assert folder_path in manifest2["folders"], f"Folder {folder_path} missing in second manifest"
        assert folder_data["folder_hash"] == manifest2["folders"][folder_path]["folder_hash"], \
               f"Folder hash differs for {folder_path}"
    
    print("✓ Manifest generation is deterministic")


def test_manifest_persistence():
    """Test that manifest is saved to correct location."""
    # Get current commit
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
        check=True
    )
    commit = result.stdout.strip()
    
    # Expected manifest path
    manifest_path = Path(f"documentation/sha256_manifests/manifest-{commit}.json")
    
    # Manifest should already exist (created during earlier tests)
    assert manifest_path.exists(), f"Manifest not found at {manifest_path}"
    
    # Load and verify
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    assert manifest["commit"] == commit
    assert "files" in manifest
    assert "folders" in manifest
    
    print(f"✓ Manifest persisted to {manifest_path}")


def main():
    """Run all tests."""
    print("Running Manifest Generation Tests...")
    print("=" * 80)
    
    # Change to repo root
    os.chdir(Path(__file__).parent.parent)
    
    tests = [
        test_manifest_module_exists,
        test_manifest_cli_works,
        test_manifest_generation,
        test_manifest_file_structure,
        test_manifest_folder_structure,
        test_manifest_determinism,
        test_manifest_persistence,
    ]
    
    failed = 0
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__} FAILED: {e}")
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
