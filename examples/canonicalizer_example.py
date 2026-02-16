"""
Example: Using the canonicalizer for deterministic file hashing.

This example shows how to get canonical byte representations of different file types.
"""

import tempfile
import json
from pathlib import Path
from toolkit.oe.canonicalizer import canonical_byte_representation
from toolkit.oe.hasher import compute_sha256


def main():
    print("Canonicalizer Example\n" + "=" * 50)
    
    # Example 1: Text file with different line endings
    print("\n1. Text file with different line endings:")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Line 1\r\nLine 2\r\nLine 3")  # Windows line endings
        temp_path1 = Path(f.name)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Line 1\nLine 2\nLine 3")  # Unix line endings
        temp_path2 = Path(f.name)
    
    try:
        canonical1, type1 = canonical_byte_representation(temp_path1)
        canonical2, type2 = canonical_byte_representation(temp_path2)
        
        hash1 = compute_sha256(canonical1)
        hash2 = compute_sha256(canonical2)
        
        print(f"  Windows line endings hash: {hash1[:16]}...")
        print(f"  Unix line endings hash:    {hash2[:16]}...")
        print(f"  Hashes match: {hash1 == hash2}")
    finally:
        temp_path1.unlink()
        temp_path2.unlink()
    
    # Example 2: JSON with different formatting
    print("\n2. JSON files with different formatting:")
    
    data = {"zebra": 1, "apple": 2, "middle": 3}
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f, indent=4)  # Pretty printed
        temp_path1 = Path(f.name)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f)  # Compact
        temp_path2 = Path(f.name)
    
    try:
        canonical1, type1 = canonical_byte_representation(temp_path1)
        canonical2, type2 = canonical_byte_representation(temp_path2)
        
        hash1 = compute_sha256(canonical1)
        hash2 = compute_sha256(canonical2)
        
        print(f"  Pretty JSON hash: {hash1[:16]}...")
        print(f"  Compact JSON hash: {hash2[:16]}...")
        print(f"  Hashes match: {hash1 == hash2}")
        print(f"  Canonical form: {canonical1.decode('utf-8')}")
    finally:
        temp_path1.unlink()
        temp_path2.unlink()
    
    # Example 3: XML with different formatting
    print("\n3. XML files with different attribute order:")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write('<root z="1" a="2" m="3"></root>')
        temp_path1 = Path(f.name)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write('<root a="2" m="3" z="1"></root>')
        temp_path2 = Path(f.name)
    
    try:
        canonical1, type1 = canonical_byte_representation(temp_path1)
        canonical2, type2 = canonical_byte_representation(temp_path2)
        
        hash1 = compute_sha256(canonical1)
        hash2 = compute_sha256(canonical2)
        
        print(f"  XML order 1 hash: {hash1[:16]}...")
        print(f"  XML order 2 hash: {hash2[:16]}...")
        print(f"  Hashes match: {hash1 == hash2}")
    finally:
        temp_path1.unlink()
        temp_path2.unlink()
    
    # Example 4: Binary file
    print("\n4. Binary file (no changes):")
    
    binary_data = b'\x00\x01\x02\x03\xFF\xFE'
    
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.bin', delete=False) as f:
        f.write(binary_data)
        temp_path = Path(f.name)
    
    try:
        canonical, file_type = canonical_byte_representation(temp_path)
        hash_value = compute_sha256(canonical)
        
        print(f"  Binary file type: {file_type}")
        print(f"  Hash: {hash_value[:16]}...")
        print(f"  Data unchanged: {canonical == binary_data}")
    finally:
        temp_path.unlink()
    
    print("\n" + "=" * 50)
    print("All canonical representations are deterministic!")


if __name__ == '__main__':
    main()
