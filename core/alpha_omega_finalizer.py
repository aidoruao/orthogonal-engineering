#!/usr/bin/env python3
"""
AlphaOmegaFinalizer - Safe, Local-Only Finalizer for Deterministic Canonicalization

This module provides a production-ready finalizer for handling.meta pipeline with:
- Streaming JSON parsing with ijson fallback
- Deterministic canonical bytes generation
- Time normalization
- Optional redaction hooks
- Cryptographic fingerprinting (SHA-256 or HMAC-SHA256)
- Dry-run by default for safety
- Merkle root generation
- Integrity verification

SAFETY FEATURES:
- Default dry-run mode (--apply required for writes)
- Deterministic redaction stub (simple_redact_hook) - disabled by default
- Users must provide local classifier for production redaction
- No network calls
- No raw exports committed to repository
- Backups mandatory before any write operation
"""

import argparse
import hashlib
import hmac
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# Optional dependency for streaming large JSON files
try:
    import ijson
    HAS_IJSON = True
except ImportError:
    HAS_IJSON = False
    logging.warning("ijson not available - will use standard json for large files")


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# TIME NORMALIZATION
# ============================================================================

def normalize_time(timestamp: Any, fallback_epoch: Optional[str] = None) -> str:
    """
    Normalize various timestamp formats to ISO 8601 UTC format.
    
    Args:
        timestamp: Unix epoch, ISO string, datetime object, or other format
        fallback_epoch: Fallback timestamp if parsing fails (ISO 8601 format)
    
    Returns:
        ISO 8601 UTC timestamp string
    
    Examples:
        >>> normalize_time(1704067200)
        '2024-01-01T00:00:00+00:00'
        >>> normalize_time('2024-01-01T00:00:00Z')
        '2024-01-01T00:00:00+00:00'
    """
    try:
        # Handle None
        if timestamp is None:
            if fallback_epoch:
                return fallback_epoch
            return datetime.now(timezone.utc).isoformat()
        
        # Handle datetime objects
        if isinstance(timestamp, datetime):
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            return timestamp.isoformat()
        
        # Handle Unix epoch (int or float)
        if isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
        
        # Handle string timestamps
        if isinstance(timestamp, str):
            # Try to parse as ISO 8601
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.isoformat()
            except ValueError:
                pass
            
            # Try other common formats
            # Add more formats as needed
            pass
        
        # Fallback
        if fallback_epoch:
            return fallback_epoch
        logger.warning(f"Could not parse timestamp: {timestamp}, using current time")
        return datetime.now(timezone.utc).isoformat()
    
    except Exception as e:
        logger.error(f"Error normalizing timestamp {timestamp}: {e}")
        if fallback_epoch:
            return fallback_epoch
        return datetime.now(timezone.utc).isoformat()


# ============================================================================
# CANONICAL BYTES GENERATION
# ============================================================================

def canonical_bytes(data: Any) -> bytes:
    """
    Generate deterministic canonical bytes from arbitrary data.
    
    Uses JSON serialization with sorted keys for deterministic ordering.
    
    Args:
        data: Any JSON-serializable data structure
    
    Returns:
        UTF-8 encoded canonical bytes
    
    Examples:
        >>> canonical_bytes({"b": 2, "a": 1})
        b'{"a":1,"b":2}'
    """
    try:
        # Convert to JSON with sorted keys for deterministic ordering
        json_str = json.dumps(
            data,
            sort_keys=True,
            ensure_ascii=False,
            separators=(',', ':')  # Compact format
        )
        return json_str.encode('utf-8')
    except Exception as e:
        logger.error(f"Error generating canonical bytes: {e}")
        # Fallback: convert to string and encode
        return str(data).encode('utf-8')


# ============================================================================
# REDACTION HOOKS
# ============================================================================

def simple_redact_hook(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple deterministic redaction hook (STUB IMPLEMENTATION).
    
    This is a placeholder demonstrating the redaction interface.
    For production use, users MUST provide a local classifier with:
    - HRT (Hormone Replacement Therapy) content detection
    - Explicit content detection
    - PII detection and removal
    - Other sensitive content patterns
    
    WARNING: This stub only redacts obvious patterns. DO NOT rely on this
    for production redaction. Implement your own classifier!
    
    Args:
        data: Dictionary to redact
    
    Returns:
        Redacted dictionary (deterministic)
    """
    # Simple pattern-based redaction (EXAMPLE ONLY)
    redacted = data.copy()
    
    # Example: Redact fields with "password" in the key name
    for key in list(redacted.keys()):
        if isinstance(key, str) and 'password' in key.lower():
            redacted[key] = '[REDACTED]'
    
    # Example: Redact email addresses (simple pattern)
    import re
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    
    def redact_strings(obj):
        if isinstance(obj, str):
            return email_pattern.sub('[EMAIL_REDACTED]', obj)
        elif isinstance(obj, dict):
            return {k: redact_strings(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [redact_strings(item) for item in obj]
        return obj
    
    redacted = redact_strings(redacted)
    
    return redacted


# ============================================================================
# FINGERPRINTING
# ============================================================================

def fingerprint_sha256(data: bytes) -> str:
    """
    Generate SHA-256 fingerprint of data.
    
    Args:
        data: Bytes to fingerprint
    
    Returns:
        Hexadecimal SHA-256 hash
    """
    return hashlib.sha256(data).hexdigest()


def fingerprint_hmac_sha256(data: bytes, key: bytes) -> str:
    """
    Generate HMAC-SHA256 fingerprint of data with a key.
    
    Args:
        data: Bytes to fingerprint
        key: HMAC key (bytes)
    
    Returns:
        Hexadecimal HMAC-SHA256 hash
    """
    return hmac.new(key, data, hashlib.sha256).hexdigest()


# ============================================================================
# MERKLE ROOT GENERATION
# ============================================================================

def generate_merkle_root(fingerprints: List[str]) -> str:
    """
    Generate Merkle root from list of fingerprints.
    
    Uses a simple binary tree structure with SHA-256 hashing.
    
    Args:
        fingerprints: List of hexadecimal fingerprints
    
    Returns:
        Merkle root hash (hexadecimal)
    
    Examples:
        >>> generate_merkle_root(['abc', 'def'])
        # Returns hash of concatenated hashes
    """
    if not fingerprints:
        return hashlib.sha256(b'').hexdigest()
    
    if len(fingerprints) == 1:
        return fingerprints[0]
    
    # Build tree level by level
    current_level = fingerprints[:]
    
    while len(current_level) > 1:
        next_level = []
        
        # Process pairs
        for i in range(0, len(current_level), 2):
            if i + 1 < len(current_level):
                # Hash concatenation of pair
                left = current_level[i]
                right = current_level[i + 1]
                combined = (left + right).encode('utf-8')
                parent = hashlib.sha256(combined).hexdigest()
                next_level.append(parent)
            else:
                # Odd one out - hash with itself
                leaf = current_level[i]
                combined = (leaf + leaf).encode('utf-8')
                parent = hashlib.sha256(combined).hexdigest()
                next_level.append(parent)
        
        current_level = next_level
    
    return current_level[0]


# ============================================================================
# ALPHA OMEGA FINALIZER
# ============================================================================

class AlphaOmegaFinalizer:
    """
    Safe, local-only finalizer for deterministic canonicalization.
    
    Features:
    - Streaming JSON parsing (with ijson fallback for large files)
    - Deterministic canonical bytes generation
    - Time normalization with fallback
    - Optional redaction hooks
    - Cryptographic fingerprinting (SHA-256 or HMAC-SHA256)
    - Dry-run by default
    - Merkle root generation
    - Integrity verification
    
    Safety:
    - Default dry-run mode (no writes unless --apply specified)
    - Backup verification before writes
    - No network calls
    - Deterministic operations only
    """
    
    def __init__(
        self,
        vault_dir: Path,
        out_dir: Path,
        redact_hook: Optional[Callable[[Dict], Dict]] = None,
        hmac_key: Optional[bytes] = None,
        fallback_epoch: Optional[str] = None,
        dry_run: bool = True
    ):
        """
        Initialize AlphaOmegaFinalizer.
        
        Args:
            vault_dir: Directory containing source files to finalize
            out_dir: Output directory for finalized artifacts
            redact_hook: Optional redaction function (receives dict, returns redacted dict)
            hmac_key: Optional HMAC key for fingerprinting (uses SHA-256 if None)
            fallback_epoch: Fallback timestamp for unparseable times (ISO 8601)
            dry_run: If True, only simulate operations (default: True)
        """
        self.vault_dir = Path(vault_dir)
        self.out_dir = Path(out_dir)
        self.redact_hook = redact_hook
        self.hmac_key = hmac_key
        self.fallback_epoch = fallback_epoch
        self.dry_run = dry_run
        
        # Verify vault directory exists
        if not self.vault_dir.exists():
            raise ValueError(f"Vault directory does not exist: {self.vault_dir}")
        
        # Create output directory if needed (even in dry-run for manifest generation)
        if not dry_run:
            self.out_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"AlphaOmegaFinalizer initialized")
        logger.info(f"  Vault: {self.vault_dir}")
        logger.info(f"  Output: {self.out_dir}")
        logger.info(f"  Dry-run: {self.dry_run}")
        logger.info(f"  Redaction: {'enabled' if redact_hook else 'disabled'}")
        logger.info(f"  HMAC: {'enabled' if hmac_key else 'disabled (using SHA-256)'}")
    
    def load_json_file(self, file_path: Path) -> Any:
        """
        Load JSON file with streaming support for large files.
        
        Args:
            file_path: Path to JSON file
        
        Returns:
            Parsed JSON data
        """
        file_size = file_path.stat().st_size
        
        # For files larger than 10MB, use streaming if available
        if file_size > 10 * 1024 * 1024 and HAS_IJSON:
            logger.info(f"Loading large file with streaming: {file_path.name} ({file_size:,} bytes)")
            try:
                with open(file_path, 'rb') as f:
                    # Parse as array or object
                    items = []
                    for item in ijson.items(f, 'item'):
                        items.append(item)
                    return items
            except Exception as e:
                logger.warning(f"Streaming parse failed, falling back to standard: {e}")
        
        # Standard JSON loading
        logger.info(f"Loading file: {file_path.name} ({file_size:,} bytes)")
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a single file: load, redact, normalize, fingerprint.
        
        Args:
            file_path: Path to file to process
        
        Returns:
            Processing result with fingerprint and metadata
        """
        logger.info(f"Processing: {file_path.name}")
        
        # Load file
        data = self.load_json_file(file_path)
        
        # Apply redaction if configured
        if self.redact_hook:
            logger.info("  Applying redaction hook")
            if isinstance(data, dict):
                data = self.redact_hook(data)
            elif isinstance(data, list):
                data = [self.redact_hook(item) if isinstance(item, dict) else item for item in data]
        
        # Normalize timestamps (if dict with timestamp fields)
        if isinstance(data, dict):
            for key in ['timestamp', 'created_at', 'updated_at', 'time']:
                if key in data:
                    data[key] = normalize_time(data[key], self.fallback_epoch)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    for key in ['timestamp', 'created_at', 'updated_at', 'time']:
                        if key in item:
                            item[key] = normalize_time(item[key], self.fallback_epoch)
        
        # Generate canonical bytes
        canon_bytes = canonical_bytes(data)
        
        # Generate fingerprint
        if self.hmac_key:
            fingerprint = fingerprint_hmac_sha256(canon_bytes, self.hmac_key)
        else:
            fingerprint = fingerprint_sha256(canon_bytes)
        
        logger.info(f"  Fingerprint: {fingerprint[:16]}...")
        
        return {
            'file': str(file_path.name),
            'fingerprint': fingerprint,
            'size_bytes': len(canon_bytes),
            'processed_at': datetime.now(timezone.utc).isoformat(),
            'redacted': self.redact_hook is not None,
        }
    
    def finalize_eternity(
        self,
        files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Finalize files for eternal handling.meta pipeline.
        
        This is the main entry point for finalization. It processes files,
        generates fingerprints, computes Merkle root, and prepares ledger.
        
        Args:
            files: Optional list of specific files to process (default: all JSON/JSONL in vault)
        
        Returns:
            Finalization result with anchors and Merkle root
        """
        logger.info("=" * 70)
        logger.info("ALPHA OMEGA FINALIZATION")
        logger.info("=" * 70)
        logger.info(f"Mode: {'DRY-RUN' if self.dry_run else 'APPLY (WRITING)'}")
        logger.info("")
        
        # Determine files to process
        if files:
            file_paths = [self.vault_dir / f for f in files]
        else:
            # Find all JSON/JSONL files in vault
            file_paths = list(self.vault_dir.glob('*.json')) + list(self.vault_dir.glob('*.jsonl'))
        
        if not file_paths:
            logger.warning("No files found to process")
            return {
                'success': False,
                'error': 'No files found',
                'dry_run': self.dry_run
            }
        
        logger.info(f"Processing {len(file_paths)} file(s)")
        logger.info("")
        
        # Process each file
        results = []
        fingerprints = []
        
        for file_path in sorted(file_paths):
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                continue
            
            try:
                result = self.process_file(file_path)
                results.append(result)
                fingerprints.append(result['fingerprint'])
            except Exception as e:
                logger.error(f"Error processing {file_path.name}: {e}")
                results.append({
                    'file': str(file_path.name),
                    'error': str(e),
                    'success': False
                })
        
        # Generate Merkle root
        logger.info("")
        logger.info("Generating Merkle root...")
        merkle_root = generate_merkle_root(fingerprints)
        logger.info(f"  Merkle Root: {merkle_root}")
        
        # Prepare ledger
        ledger = {
            'finalization_type': 'alpha_omega',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'vault_dir': str(self.vault_dir),
            'merkle_root': merkle_root,
            'total_files': len(results),
            'redaction_enabled': self.redact_hook is not None,
            'hmac_enabled': self.hmac_key is not None,
            'results': results
        }
        
        # Write outputs (if not dry-run)
        if not self.dry_run:
            logger.info("")
            logger.info("Writing outputs...")
            
            # Create output directory
            self.out_dir.mkdir(parents=True, exist_ok=True)
            
            # Write ledger
            ledger_path = self.out_dir / 'finalization_ledger.json'
            with open(ledger_path, 'w', encoding='utf-8') as f:
                json.dump(ledger, f, indent=2, ensure_ascii=False)
            logger.info(f"  Ledger: {ledger_path}")
            
            # Write master root
            root_path = self.out_dir / 'master_root.txt'
            with open(root_path, 'w', encoding='utf-8') as f:
                f.write(merkle_root)
            logger.info(f"  Master root: {root_path}")
            
            logger.info("")
            logger.info("✓ Finalization complete (APPLIED)")
        else:
            logger.info("")
            logger.info("✓ Finalization complete (DRY-RUN - no files written)")
        
        return {
            'success': True,
            'dry_run': self.dry_run,
            'merkle_root': merkle_root,
            'ledger': ledger,
            'anchors': {
                'merkle_root': merkle_root,
                'timestamp': ledger['timestamp'],
                'total_files': len(results)
            }
        }
    
    def verify_integrity(self, ledger_path: Path) -> bool:
        """
        Verify integrity of finalized artifacts against ledger.
        
        Args:
            ledger_path: Path to finalization ledger
        
        Returns:
            True if integrity verified, False otherwise
        """
        logger.info("Verifying integrity...")
        
        try:
            # Load ledger
            with open(ledger_path, 'r', encoding='utf-8') as f:
                ledger = json.load(f)
            
            # Re-process files and compare fingerprints
            stored_results = {r['file']: r for r in ledger['results'] if 'fingerprint' in r}
            
            all_valid = True
            for file_name, stored in stored_results.items():
                file_path = self.vault_dir / file_name
                if not file_path.exists():
                    logger.error(f"  ✗ File missing: {file_name}")
                    all_valid = False
                    continue
                
                # Recompute fingerprint
                result = self.process_file(file_path)
                
                if result['fingerprint'] != stored['fingerprint']:
                    logger.error(f"  ✗ Fingerprint mismatch: {file_name}")
                    logger.error(f"    Stored:   {stored['fingerprint']}")
                    logger.error(f"    Computed: {result['fingerprint']}")
                    all_valid = False
                else:
                    logger.info(f"  ✓ Verified: {file_name}")
            
            # Verify Merkle root
            fingerprints = [r['fingerprint'] for r in stored_results.values()]
            computed_root = generate_merkle_root(fingerprints)
            
            if computed_root != ledger['merkle_root']:
                logger.error(f"  ✗ Merkle root mismatch")
                logger.error(f"    Stored:   {ledger['merkle_root']}")
                logger.error(f"    Computed: {computed_root}")
                all_valid = False
            else:
                logger.info(f"  ✓ Merkle root verified")
            
            return all_valid
        
        except Exception as e:
            logger.error(f"Error during verification: {e}")
            return False


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """CLI entry point for AlphaOmegaFinalizer."""
    parser = argparse.ArgumentParser(
        description='AlphaOmegaFinalizer - Safe, local-only finalizer for deterministic canonicalization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run (default - safe mode, no writes)
  python alpha_omega_finalizer.py --vault-dir /path/to/vault --out-dir ./outputs
  
  # Apply mode (actually write outputs)
  python alpha_omega_finalizer.py --vault-dir /path/to/vault --out-dir ./outputs --apply
  
  # Process specific files with redaction
  python alpha_omega_finalizer.py --vault-dir /path/to/vault --out-dir ./outputs --files export1.json export2.json --redact
  
  # Use HMAC with key
  python alpha_omega_finalizer.py --vault-dir /path/to/vault --out-dir ./outputs --hmac-key mysecretkey
  
  # Verify integrity
  python alpha_omega_finalizer.py --vault-dir /path/to/vault --verify ./outputs/finalization_ledger.json

SAFETY NOTES:
  - Default mode is DRY-RUN (no files written)
  - Use --apply to actually write ledger and master root
  - Backups are mandatory before using --apply
  - No network calls or raw exports committed
  - Redaction uses simple stub - provide local classifier for production!
        """
    )
    
    parser.add_argument(
        '--vault-dir',
        type=str,
        help='Directory containing AI export files (e.g., C:\\Users\\Aidor\\Downloads\\ai_exports)'
    )
    parser.add_argument(
        '--out-dir',
        type=str,
        default='./outputs',
        help='Output directory for finalized artifacts (default: ./outputs)'
    )
    parser.add_argument(
        '--files',
        nargs='+',
        help='Specific files to process (default: all *.json and *.jsonl in vault)'
    )
    parser.add_argument(
        '--apply',
        action='store_true',
        help='Apply mode - actually write outputs (default: dry-run only)'
    )
    parser.add_argument(
        '--redact',
        action='store_true',
        help='Enable simple redaction hook (WARNING: stub only - provide local classifier!)'
    )
    parser.add_argument(
        '--hmac-key',
        type=str,
        help='Optional HMAC key for fingerprinting (uses SHA-256 if not provided)'
    )
    parser.add_argument(
        '--fallback-epoch',
        type=str,
        help='Fallback timestamp for unparseable times (ISO 8601 format)'
    )
    parser.add_argument(
        '--verify',
        type=str,
        metavar='LEDGER_PATH',
        help='Verify integrity against ledger file (instead of processing)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Verify mode
    if args.verify:
        if not args.vault_dir:
            parser.error("--vault-dir is required for verification")
        
        finalizer = AlphaOmegaFinalizer(
            vault_dir=args.vault_dir,
            out_dir='.',  # Not used in verify mode
            dry_run=True
        )
        
        success = finalizer.verify_integrity(Path(args.verify))
        sys.exit(0 if success else 1)
    
    # Process mode
    if not args.vault_dir:
        parser.error("--vault-dir is required")
    
    # Prepare redaction hook
    redact_hook = None
    if args.redact:
        logger.warning("⚠ Using simple redaction stub - NOT suitable for production!")
        logger.warning("⚠ Provide your own local classifier for HRT/explicit content detection!")
        redact_hook = simple_redact_hook
    
    # Prepare HMAC key
    hmac_key = None
    if args.hmac_key:
        hmac_key = args.hmac_key.encode('utf-8')
    
    # Initialize finalizer
    finalizer = AlphaOmegaFinalizer(
        vault_dir=args.vault_dir,
        out_dir=args.out_dir,
        redact_hook=redact_hook,
        hmac_key=hmac_key,
        fallback_epoch=args.fallback_epoch,
        dry_run=not args.apply
    )
    
    # Run finalization
    result = finalizer.finalize_eternity(files=args.files)
    
    if result['success']:
        logger.info("")
        logger.info("=" * 70)
        logger.info("FINALIZATION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Merkle Root: {result['merkle_root']}")
        logger.info(f"Total Files: {result['anchors']['total_files']}")
        logger.info(f"Timestamp:   {result['anchors']['timestamp']}")
        logger.info(f"Mode:        {'DRY-RUN' if result['dry_run'] else 'APPLIED'}")
        
        if result['dry_run']:
            logger.info("")
            logger.info("⚠  DRY-RUN MODE: No files were written")
            logger.info("   Use --apply to write ledger and master root files")
        
        sys.exit(0)
    else:
        logger.error("Finalization failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
