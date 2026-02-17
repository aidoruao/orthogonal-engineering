"""
Alpha Omega Finalizer - Robust finalizer with streaming JSON parsing.

This module provides:
- Streaming JSON parsing (ijson optional)
- Time normalization to UTC
- Canonical bytes generation
- Redact hook stub (disabled by default)
- Fingerprinting (SHA-256/HMAC)
- Finalize eternity (dry-run default)
- Merkle root generation
- Integrity verification
- CLI with --vault-dir support

Author: Orthogonal Engineering
Date: 2026-02-16
Version: 1.0.0
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

# Import from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from canonicalizer import canonicalize_json
from hasher import sha256_hex, hmac_sha256_hex
from merkle import MerkleTreeBuilder
from backup import backup_before_write


# Try to import ijson for streaming JSON parsing
try:
    import ijson
    HAS_IJSON = True
except ImportError:
    HAS_IJSON = False


def normalize_time(timestamp: Any) -> str:
    """
    Normalize timestamp to UTC ISO8601 format.
    
    Args:
        timestamp: Timestamp in various formats
        
    Returns:
        ISO8601 UTC timestamp string
    """
    if isinstance(timestamp, str):
        try:
            # Try to parse ISO format
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            # Fallback to current time
            dt = datetime.now(timezone.utc)
    elif isinstance(timestamp, (int, float)):
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    elif isinstance(timestamp, datetime):
        dt = timestamp.astimezone(timezone.utc)
    else:
        dt = datetime.now(timezone.utc)
    
    return dt.isoformat()


def canonical_bytes(data: Any) -> bytes:
    """
    Convert data to canonical bytes representation.
    
    Args:
        data: Data to canonicalize
        
    Returns:
        Canonical bytes
    """
    if isinstance(data, bytes):
        return data
    elif isinstance(data, str):
        return data.encode('utf-8')
    elif isinstance(data, (dict, list)):
        return canonicalize_json(data)
    else:
        return str(data).encode('utf-8')


def redact_hook(data: Dict, config: Optional[Dict] = None) -> Dict:
    """
    Redaction hook stub (DISABLED BY DEFAULT).
    
    Users must configure local classifiers for stronger redaction.
    
    Args:
        data: Data to potentially redact
        config: Optional redaction configuration
        
    Returns:
        Data (unmodified by default)
    """
    # Stub implementation - no redaction by default
    # Users can implement custom redaction logic here
    return data


def compute_fingerprint(data: bytes, key: Optional[bytes] = None) -> str:
    """
    Compute cryptographic fingerprint (SHA-256 or HMAC-SHA256).
    
    Args:
        data: Data to fingerprint
        key: Optional HMAC key
        
    Returns:
        Hexadecimal fingerprint
    """
    if key:
        return hmac_sha256_hex(data, key)
    return sha256_hex(data)


def stream_json_objects(file_path: Path) -> Iterator[Dict]:
    """
    Stream JSON objects from file (using ijson if available).
    
    Args:
        file_path: Path to JSON or JSONL file
        
    Yields:
        Parsed JSON objects
    """
    with open(file_path, 'rb') as f:
        # Check if it's JSONL (one JSON object per line)
        first_byte = f.read(1)
        f.seek(0)
        
        if first_byte == b'{':
            # Could be JSONL, try line-by-line parsing
            try:
                for line in f:
                    line = line.strip()
                    if line:
                        yield json.loads(line)
                return
            except:
                # Not JSONL, reset for full parse
                f.seek(0)
        
        # Try streaming with ijson if available
        if HAS_IJSON:
            try:
                for obj in ijson.items(f, 'item'):
                    yield obj
                return
            except:
                f.seek(0)
        
        # Fallback: load entire file
        data = json.load(f)
        if isinstance(data, list):
            for obj in data:
                yield obj
        else:
            yield data


class AlphaOmegaFinalizer:
    """Robust finalizer for vault processing."""
    
    def __init__(
        self,
        vault_dir: Path,
        output_dir: Optional[Path] = None,
        hmac_key: Optional[bytes] = None
    ):
        """
        Initialize finalizer.
        
        Args:
            vault_dir: Directory containing files to finalize
            output_dir: Optional output directory (defaults to vault_dir)
            hmac_key: Optional HMAC key for fingerprinting
        """
        self.vault_dir = Path(vault_dir)
        self.output_dir = Path(output_dir) if output_dir else self.vault_dir
        self.hmac_key = hmac_key
        self.manifest: List[Dict] = []
    
    def process_file(self, file_path: Path) -> Dict:
        """
        Process a single file.
        
        Args:
            file_path: Path to file
            
        Returns:
            File processing record
        """
        # Read file
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Compute fingerprint
        fingerprint = compute_fingerprint(content, self.hmac_key)
        
        # Create record
        record = {
            'path': str(file_path.relative_to(self.vault_dir)),
            'fingerprint': fingerprint,
            'size_bytes': len(content),
            'timestamp': normalize_time(datetime.now(timezone.utc))
        }
        
        self.manifest.append(record)
        return record
    
    def finalize_eternity(
        self,
        dry_run: bool = True,
        generate_merkle: bool = True
    ) -> Dict:
        """
        Finalize vault with optional Merkle tree generation.
        
        Args:
            dry_run: If True, don't write files (DEFAULT)
            generate_merkle: Generate Merkle root
            
        Returns:
            Summary dictionary
        """
        summary = {
            'vault_dir': str(self.vault_dir),
            'dry_run': dry_run,
            'files_processed': 0,
            'total_bytes': 0
        }
        
        # Process all files
        for file_path in sorted(self.vault_dir.rglob('*')):
            if file_path.is_file():
                record = self.process_file(file_path)
                summary['files_processed'] += 1
                summary['total_bytes'] += record['size_bytes']
        
        # Generate Merkle root if requested
        if generate_merkle and self.manifest:
            merkle_root = self.generate_merkle_root()
            summary['merkle_root'] = merkle_root
        
        # Write manifest if not dry-run
        if not dry_run:
            manifest_path = self.output_dir / 'finalization_manifest.jsonl'
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(manifest_path, 'w') as f:
                for record in self.manifest:
                    f.write(json.dumps(record) + '\n')
            
            summary['manifest_path'] = str(manifest_path)
        
        return summary
    
    def generate_merkle_root(self) -> str:
        """
        Generate Merkle root for all processed files.
        
        Returns:
            Merkle root hash
        """
        builder = MerkleTreeBuilder()
        
        for record in self.manifest:
            # Use fingerprint as canonical content
            canonical_content = record['fingerprint'].encode('utf-8')
            builder.add_leaf(record['path'], canonical_content)
        
        return builder.build_tree()
    
    def verify_integrity(self, manifest_path: Path) -> bool:
        """
        Verify integrity against a manifest.
        
        Args:
            manifest_path: Path to manifest file
            
        Returns:
            True if integrity check passes
        """
        if not manifest_path.exists():
            return False
        
        # Load manifest
        expected_records = []
        with open(manifest_path, 'r') as f:
            for line in f:
                expected_records.append(json.loads(line))
        
        # Check each file
        for record in expected_records:
            file_path = self.vault_dir / record['path']
            
            if not file_path.exists():
                print(f"Missing file: {file_path}")
                return False
            
            # Verify fingerprint
            with open(file_path, 'rb') as f:
                content = f.read()
            
            actual_fingerprint = compute_fingerprint(content, self.hmac_key)
            
            if actual_fingerprint != record['fingerprint']:
                print(f"Fingerprint mismatch: {file_path}")
                return False
        
        return True


def main():
    """CLI for alpha_omega_finalizer."""
    parser = argparse.ArgumentParser(
        description='Alpha Omega Finalizer - Robust vault finalization'
    )
    
    parser.add_argument(
        '--vault-dir',
        type=Path,
        default=Path(r'C:\Users\Aidor\Downloads\ai_exports'),
        help='Vault directory (EXAMPLE ONLY - default: C:\\Users\\Aidor\\Downloads\\ai_exports)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=Path,
        help='Output directory (defaults to vault-dir)'
    )
    
    parser.add_argument(
        '--apply',
        action='store_true',
        help='Apply changes (default is dry-run)'
    )
    
    parser.add_argument(
        '--generate-merkle',
        action='store_true',
        default=True,
        help='Generate Merkle root (default: True)'
    )
    
    parser.add_argument(
        '--verify',
        type=Path,
        help='Verify integrity against manifest'
    )
    
    args = parser.parse_args()
    
    # Create finalizer
    finalizer = AlphaOmegaFinalizer(
        vault_dir=args.vault_dir,
        output_dir=args.output_dir
    )
    
    # Check if vault exists
    if not args.vault_dir.exists():
        print(f"Warning: Vault directory does not exist: {args.vault_dir}")
        print("This is expected if using the default example path.")
        print("Please specify --vault-dir with an actual path.")
        return 1
    
    # Verify mode
    if args.verify:
        print(f"Verifying integrity against: {args.verify}")
        result = finalizer.verify_integrity(args.verify)
        if result:
            print("✓ Integrity check passed")
            return 0
        else:
            print("✗ Integrity check failed")
            return 1
    
    # Finalize mode
    dry_run = not args.apply
    print(f"{'DRY RUN - ' if dry_run else ''}Finalizing vault: {args.vault_dir}")
    
    summary = finalizer.finalize_eternity(
        dry_run=dry_run,
        generate_merkle=args.generate_merkle
    )
    
    print(json.dumps(summary, indent=2))
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
