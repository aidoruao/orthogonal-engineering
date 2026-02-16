"""
Basic Usage Example

Demonstrates basic usage of the deterministic auditable Python scaffold.
"""

from pathlib import Path

from scaffold import (
    ScaffoldLogger,
    canonical_byte_representation,
    compute_file_hash,
)


def main():
    """Run basic usage examples."""
    print("=" * 60)
    print("Deterministic Auditable Python Scaffold - Basic Usage")
    print("=" * 60)
    
    # Initialize logger
    logger = ScaffoldLogger()
    print("\n✓ Logger initialized")
    
    # Example 1: Canonical byte representation
    print("\n--- Example 1: Canonical Byte Representation ---")
    
    # Create a test file
    test_file = Path("example_test.txt")
    test_file.write_text("Hello World\r\nThis is a test\r\n")
    
    # Get canonical bytes
    canonical_bytes = canonical_byte_representation(test_file)
    print(f"Original file size: {test_file.stat().st_size} bytes")
    print(f"Canonical bytes size: {len(canonical_bytes)} bytes")
    print(f"Canonical content preview: {canonical_bytes[:50]}...")
    
    # Example 2: File hashing
    print("\n--- Example 2: File Hashing ---")
    
    file_hash = compute_file_hash(test_file, use_canonical=True)
    print(f"Canonical hash: {file_hash}")
    
    file_hash_raw = compute_file_hash(test_file, use_canonical=False)
    print(f"Raw hash: {file_hash_raw}")
    print(f"Hashes match: {file_hash == file_hash_raw}")
    
    # Example 3: Logging
    print("\n--- Example 3: Logging ---")
    
    logger.log_handling_step(
        action="process_file",
        details={
            "file": str(test_file),
            "hash": file_hash,
            "size": len(canonical_bytes)
        }
    )
    print(f"✓ Logged handling step (ID: {logger.get_handling_steps()})")
    
    logger.log_verification_step(
        action="verify_hash",
        details={
            "file": str(test_file),
            "expected_hash": file_hash,
            "actual_hash": file_hash,
            "verified": True
        }
    )
    print(f"✓ Logged verification step (ID: {logger.get_verification_steps()})")
    
    # Read logs
    handling_logs = logger.read_handling_log()
    print(f"\nHandling log entries: {len(handling_logs)}")
    
    verification_logs = logger.read_verification_log()
    print(f"Verification log entries: {len(verification_logs)}")
    
    # Cleanup
    test_file.unlink()
    print("\n✓ Cleanup complete")
    
    print("\n" + "=" * 60)
    print("Basic usage example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
