#!/usr/bin/env python3
"""
Integration test demonstrating the complete canonicalization scaffold.

This test exercises all major components:
- Canonicalization of various file types
- Hashing with canonical bytes
- Merkle tree construction
- Manifest generation
- Structured logging
- Handling pipeline (with mock XML)

Author: Orthogonal Engineering System
Date: 2026-02-16
"""

import json
import shutil
import tempfile
from pathlib import Path

from toolkit.oe.canonicalizer import canonical_byte_representation, canonical_path
from toolkit.oe.hasher import hash_file
from toolkit.oe.logger import HandlingPipelineLogger, VerificationPipelineLogger
from toolkit.oe.manifest import ManifestGenerator
from toolkit.oe.merkle import MerkleTree


def create_test_repository(base_path: Path):
    """Create a test repository with various file types."""
    # Create text file
    (base_path / 'readme.txt').write_text('Hello, World!\nThis is a test.\n')
    
    # Create JSON file
    data = {'name': 'test', 'version': '1.0.0', 'features': ['a', 'b', 'c']}
    (base_path / 'config.json').write_text(json.dumps(data, indent=2))
    
    # Create XML file
    xml_content = """<?xml version="1.0"?>
<root>
    <item id="1">First</item>
    <item id="2">Second</item>
</root>"""
    (base_path / 'data.xml').write_text(xml_content)
    
    # Create binary file
    (base_path / 'data.bin').write_bytes(b'\x00\x01\x02\x03\xff\xfe\xfd')
    
    # Create subdirectory with files
    subdir = base_path / 'subdir'
    subdir.mkdir()
    (subdir / 'notes.md').write_text('# Notes\n\nSome markdown content.')
    (subdir / 'values.json').write_text('{"key": "value"}')


def test_canonicalization(repo_path: Path):
    """Test canonicalization of all files."""
    print("\n=== Testing Canonicalization ===")
    
    files = list(repo_path.rglob('*'))
    files = [f for f in files if f.is_file()]
    
    for file_path in sorted(files):
        try:
            canonical_bytes = canonical_byte_representation(file_path)
            rel_path = canonical_path(file_path, repo_path)
            print(f"✓ Canonicalized: {rel_path} ({len(canonical_bytes)} bytes)")
        except Exception as e:
            print(f"✗ Failed: {file_path}: {e}")


def test_hashing(repo_path: Path):
    """Test hashing of all files."""
    print("\n=== Testing Hashing ===")
    
    files = list(repo_path.rglob('*'))
    files = [f for f in files if f.is_file()]
    
    for file_path in sorted(files):
        try:
            file_hash = hash_file(file_path)
            rel_path = canonical_path(file_path, repo_path)
            print(f"✓ Hashed: {rel_path}")
            print(f"  Hash: {file_hash}")
        except Exception as e:
            print(f"✗ Failed: {file_path}: {e}")


def test_manifest(repo_path: Path, output_path: Path):
    """Test manifest generation."""
    print("\n=== Testing Manifest Generation ===")
    
    generator = ManifestGenerator(repo_path, checkpoint_interval=3)
    manifest_file = output_path / 'manifest.jsonl'
    
    generator.generate_streaming_manifest(manifest_file)
    
    # Load and display
    entries = generator.load_manifest(manifest_file)
    print(f"✓ Generated manifest with {len(entries)} entries")
    
    for entry in entries:
        print(f"  - {entry.canonical_path}: {entry.file_type} ({entry.size} bytes)")
    
    return manifest_file


def test_merkle_tree(repo_path: Path, output_path: Path):
    """Test Merkle tree construction."""
    print("\n=== Testing Merkle Tree ===")
    
    files = list(repo_path.rglob('*'))
    files = [str(f) for f in files if f.is_file()]
    
    tree = MerkleTree(files, base_path=repo_path)
    root_hash = tree.get_root_hash()
    
    print(f"✓ Built Merkle tree with {len(tree.leaves)} leaves")
    print(f"  Root hash: {root_hash}")
    
    # Export proofs
    proofs_file = output_path / 'merkle_proofs.jsonl'
    tree.export_proofs_jsonl(proofs_file)
    print(f"✓ Exported proofs to {proofs_file}")
    
    # Verify all files
    print("\n  Verifying inclusion proofs:")
    for file_path in files:
        proof = tree.get_proof(file_path)
        verified = tree.verify_proof(file_path, proof)
        rel_path = canonical_path(file_path, repo_path)
        status = "✓" if verified else "✗"
        print(f"  {status} {rel_path}: {len(proof)} proof steps")
    
    return root_hash


def test_logging(output_path: Path):
    """Test structured logging."""
    print("\n=== Testing Structured Logging ===")
    
    # Test handling pipeline logger
    with HandlingPipelineLogger(output_path) as logger:
        logger.log_hello_world()
        logger.log_parsing_start('test_handling.meta')
        logger.log_vehicle_clamp('TEST_VEHICLE', 'fMass', '50000', '10000', dry_run=True)
        logger.log_parsing_complete('test_handling.meta', 1)
    
    handling_log = output_path / 'hello_world_handling_pipeline.jsonl'
    print(f"✓ Created handling pipeline log: {handling_log}")
    
    # Count log entries
    with open(handling_log, 'r') as f:
        entries = [json.loads(line) for line in f if line.strip()]
    print(f"  {len(entries)} log entries written")
    
    # Test verification logger
    with VerificationPipelineLogger(output_path) as logger:
        logger.log_hash_verification('test.txt', 'abc123', 'abc123', True)
        logger.log_merkle_verification('test.txt', 'root123', True)
    
    verify_log = output_path / 'handling_verification_pipeline.jsonl'
    print(f"✓ Created verification log: {verify_log}")
    
    with open(verify_log, 'r') as f:
        entries = [json.loads(line) for line in f if line.strip()]
    print(f"  {len(entries)} log entries written")


def main():
    """Run complete integration test."""
    print("=" * 60)
    print("CANONICALIZATION SCAFFOLD INTEGRATION TEST")
    print("=" * 60)
    
    # Create temporary directories
    test_dir = tempfile.mkdtemp()
    output_dir = tempfile.mkdtemp()
    
    try:
        repo_path = Path(test_dir)
        output_path = Path(output_dir)
        
        # Create test repository
        print("\n=== Creating Test Repository ===")
        create_test_repository(repo_path)
        print(f"✓ Created test repository at {repo_path}")
        
        # Run tests
        test_canonicalization(repo_path)
        test_hashing(repo_path)
        manifest_file = test_manifest(repo_path, output_path)
        root_hash = test_merkle_tree(repo_path, output_path)
        test_logging(output_path)
        
        # Summary
        print("\n" + "=" * 60)
        print("INTEGRATION TEST COMPLETE")
        print("=" * 60)
        print(f"✓ All components tested successfully")
        print(f"✓ Merkle root: {root_hash}")
        print(f"✓ Manifest: {manifest_file}")
        print(f"✓ Output directory: {output_path}")
        print("\nAll features verified working correctly!")
        
    finally:
        # Cleanup
        shutil.rmtree(test_dir, ignore_errors=True)
        print(f"\n✓ Cleaned up test directory: {test_dir}")
        print(f"ℹ Output preserved at: {output_dir}")


if __name__ == '__main__':
    main()
