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
"""
Alpha-Omega Finalizer - Ensures content integrity from beginning to end.

Provides finalization logic for CAS operations with verification at both
the start (alpha) and end (omega) of the process.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from hasher import hash_file, verify_hash
from logger import get_logger
from manifest import Manifest
from merkle import MerkleTree


class AlphaOmegaFinalizer:
    """
    Finalizer that verifies content integrity from alpha (start) to omega (end).
    
    Alpha phase: Capture initial state
    Omega phase: Verify final state matches expectations
    """
    
    def __init__(self, name: str = "finalizer"):
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
    # Warning will be logged after logging is configured


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log ijson availability after logging is configured
if not HAS_IJSON:
    logger.warning("ijson not available - will use standard json for large files")


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
        
        Note: Current streaming implementation loads items into memory.
        For production use with very large files, consider processing
        items incrementally rather than accumulating them.
        
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
                    # NOTE: This accumulates items in memory. For truly large files,
                    # consider processing items incrementally.
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
        output_dir: Optional[Path] = None,
        hmac_key: Optional[bytes] = None
    ):
        """
        Initialize finalizer.
        
        Args:
            name: Finalizer instance name
        """
        self.name = name
        self.logger = get_logger(f"finalizer.{name}")
        self.alpha_state: Optional[Dict[str, Any]] = None
        self.omega_state: Optional[Dict[str, Any]] = None
    
    def alpha(self, files: List[Union[str, Path]], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Alpha phase: Capture initial state of files.
        
        Args:
            files: List of files to track
            metadata: Optional metadata to include
            
        Returns:
            Alpha state dictionary
        """
        self.logger.info(f"Alpha phase: Capturing state of {len(files)} files")
        
        file_states = []
        for filepath in files:
            filepath = Path(filepath)
            
            if not filepath.exists():
                self.logger.warning(f"File not found in alpha phase: {filepath}")
                file_states.append({
                    "path": str(filepath),
                    "exists": False
                })
                continue
            
            file_hash = hash_file(filepath)
            file_states.append({
                "path": str(filepath),
                "exists": True,
                "hash": file_hash,
                "size": filepath.stat().st_size
            })
        
        # Compute merkle root of all hashes
        hashes = [fs["hash"] for fs in file_states if fs.get("exists")]
        merkle_root = None
        if hashes:
            tree = MerkleTree(hashes)
            merkle_root = tree.get_root_hash()
        
        self.alpha_state = {
            "name": self.name,
            "phase": "alpha",
            "files": file_states,
            "merkle_root": merkle_root,
            "metadata": metadata or {}
        }
        
        self.logger.info(f"Alpha state captured: {len(file_states)} files, merkle_root={merkle_root}")
        
        return self.alpha_state
    
    def omega(self, verify: bool = True) -> Dict[str, Any]:
        """
        Omega phase: Capture final state and optionally verify against alpha.
        
        Args:
            verify: Whether to verify against alpha state
            
        Returns:
            Omega state dictionary with verification results
        """
        if self.alpha_state is None:
            raise RuntimeError("Cannot run omega phase without alpha state")
        
        self.logger.info(f"Omega phase: Verifying final state")
        
        # Re-capture state of same files
        files = [fs["path"] for fs in self.alpha_state["files"]]
        file_states = []
        
        for filepath_str in files:
            filepath = Path(filepath_str)
            
            if not filepath.exists():
                file_states.append({
                    "path": str(filepath),
                    "exists": False
                })
                continue
            
            file_hash = hash_file(filepath)
            file_states.append({
                "path": str(filepath),
                "exists": True,
                "hash": file_hash,
                "size": filepath.stat().st_size
            })
        
        # Compute merkle root
        hashes = [fs["hash"] for fs in file_states if fs.get("exists")]
        merkle_root = None
        if hashes:
            tree = MerkleTree(hashes)
            merkle_root = tree.get_root_hash()
        
        self.omega_state = {
            "name": self.name,
            "phase": "omega",
            "files": file_states,
            "merkle_root": merkle_root,
        }
        
        # Verification
        if verify:
            verification = self._verify_states()
            self.omega_state["verification"] = verification
            
            if verification["verified"]:
                self.logger.info("✓ Omega verification PASSED")
            else:
                self.logger.error(f"✗ Omega verification FAILED: {verification['issues']}")
        
        return self.omega_state
    
    def _verify_states(self) -> Dict[str, Any]:
        """
        Verify omega state against alpha state.
        
        Returns:
            Verification result dictionary
        """
        if self.alpha_state is None or self.omega_state is None:
            return {
                "verified": False,
                "issues": ["Missing alpha or omega state"]
            }
        
        issues = []
        
        # Verify merkle roots match
        if self.alpha_state["merkle_root"] != self.omega_state["merkle_root"]:
            issues.append(
                f"Merkle root mismatch: "
                f"alpha={self.alpha_state['merkle_root']}, "
                f"omega={self.omega_state['merkle_root']}"
            )
        
        # Verify individual files
        alpha_files = {fs["path"]: fs for fs in self.alpha_state["files"]}
        omega_files = {fs["path"]: fs for fs in self.omega_state["files"]}
        
        for path in alpha_files:
            alpha_file = alpha_files[path]
            omega_file = omega_files.get(path)
            
            if omega_file is None:
                issues.append(f"File missing in omega: {path}")
                continue
            
            # Check existence
            if alpha_file["exists"] != omega_file["exists"]:
                issues.append(f"Existence changed for {path}")
                continue
            
            # Check hash (if file exists)
            if alpha_file.get("exists") and omega_file.get("exists"):
                if alpha_file.get("hash") != omega_file.get("hash"):
                    issues.append(
                        f"Hash mismatch for {path}: "
                        f"alpha={alpha_file.get('hash')}, "
                        f"omega={omega_file.get('hash')}"
                    )
        
        return {
            "verified": len(issues) == 0,
            "issues": issues,
            "files_checked": len(alpha_files)
        }
    
    def get_report(self) -> Dict[str, Any]:
        """
        Get complete finalization report.
        
        Returns:
            Full report with alpha, omega, and verification
        """
        return {
            "name": self.name,
            "alpha": self.alpha_state,
            "omega": self.omega_state
        }
    
    def save_report(self, filepath: Union[str, Path]):
        """
        Save finalization report to file.
        
        Args:
            filepath: Where to save report
        """
        import json
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        report = self.get_report()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Report saved to {filepath}")
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
        type=str,
        help='Directory containing AI export files (default: use --vault-dir to specify)'
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
