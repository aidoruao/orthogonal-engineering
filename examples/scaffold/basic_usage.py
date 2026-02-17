"""
Basic Scaffold Usage Example

Demonstrates basic operations with the scaffold:
- File canonicalization
- Hashing
- Manifest generation
"""

import sys
import tempfile
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from toolkit.oe.scaffold.canonicalizer import canonical_byte_representation
from toolkit.oe.scaffold.hasher import compute_file_hash
from toolkit.oe.scaffold.manifest import generate_manifest
from toolkit.oe.scaffold.logger import ScaffoldLogger


def main():
    """Run basic scaffold examples."""
    print("=" * 60)
    print("Basic Scaffold Usage Example")
    print("=" * 60)
    
    # Create temporary directory for examples
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create logger
        logger = ScaffoldLogger(temp_path / "example.jsonl")
        logger.log_start("basic_example")
        
        # Example 1: Canonicalization
        print("\n1. File Canonicalization")
        print("-" * 40)
        
        # Create sample files
        text_file = temp_path / "sample.txt"
        text_file.write_text("Hello\r\nWorld\r\n", encoding="utf-8")
        
        json_file = temp_path / "sample.json"
        json_file.write_text('{"z": 3, "a": 1, "m": 2}', encoding="utf-8")
        
        # Canonicalize
        text_canonical = canonical_byte_representation(text_file)
        json_canonical = canonical_byte_representation(json_file)
        
        print(f"Text file: {text_file.name}")
        print(f"  Original: {repr(text_file.read_text())}")
        print(f"  Canonical: {repr(text_canonical.decode('utf-8'))}")
        
        print(f"\nJSON file: {json_file.name}")
        print(f"  Original: {json_file.read_text()}")
        print(f"  Canonical: {json_canonical.decode('utf-8')}")
        
        logger.log_info("canonicalization_complete", files=2)
        
        # Example 2: Hashing
        print("\n2. File Hashing")
        print("-" * 40)
        
        text_hash = compute_file_hash(text_file)
        json_hash = compute_file_hash(json_file)
        
        print(f"Text file hash: {text_hash}")
        print(f"JSON file hash: {json_hash}")
        
        logger.log_info("hashing_complete", files=2)
        
        # Example 3: Manifest Generation
        print("\n3. Manifest Generation")
        print("-" * 40)
        
        manifest_path = temp_path / "manifest.jsonl"
        files = [text_file, json_file]
        
        count = generate_manifest(files, manifest_path, base_path=temp_path)
        
        print(f"Manifest generated: {manifest_path.name}")
        print(f"Entries: {count}")
        
        # Show manifest contents
        print("\nManifest contents:")
        with open(manifest_path, "r") as f:
            for i, line in enumerate(f, 1):
                print(f"  Entry {i}: {line.strip()[:80]}...")
        
        logger.log_complete("basic_example", manifest_entries=count)
        
        # Example 4: Read logs
        print("\n4. Log Review")
        print("-" * 40)
        
        from toolkit.oe.scaffold.logger import LogReader
        
        log_entries = LogReader.read_log(temp_path / "example.jsonl")
        print(f"Log entries: {len(log_entries)}")
        
        for entry in log_entries:
            print(f"  Step {entry['step_id']}: {entry['event_type']} - {entry['message']}")
        
        print("\n" + "=" * 60)
        print("Example completed successfully!")
        print("=" * 60)


if __name__ == "__main__":
    main()
