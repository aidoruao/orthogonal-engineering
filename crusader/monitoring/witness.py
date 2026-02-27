"""
Crusader Combat Refrigerator - Witness Layer
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Cryptographic witness layer for system integrity verification.
Provides SHA-256 hashing, Merkle tree construction, and digital signatures.
"""

import asyncio
import hashlib
import json
import os
import time
from base64 import b64decode, b64encode
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import uuid4

from ..core.constants import CryptographicConstants, FileConstants
from ..core.utils.hash_utils import HashEngine, MerkleTree


class WitnessEventType(Enum):
    """Types of witness events."""

    SYSTEM_STARTUP = auto()
    SYSTEM_SHUTDOWN = auto()
    CYCLE_COMPLETION = auto()
    WARFARE_OPERATION = auto()
    SENSOR_READING = auto()
    CONFIGURATION_CHANGE = auto()
    ERROR_DETECTED = auto()
    MAINTENANCE_EVENT = auto()
    BACKUP_EVENT = auto()
    RESTORE_EVENT = auto()
    CUSTOM_EVENT = auto()


class WitnessStatus(Enum):
    """Witness event status."""

    PENDING = auto()
    PROCESSED = auto()
    VERIFIED = auto()
    INVALID = auto()
    EXPIRED = auto()


@dataclass
class WitnessEvent:
    """Witness event data structure."""

    event_id: str
    timestamp: datetime
    event_type: WitnessEventType
    status: WitnessStatus
    data_hash: str
    previous_hash: Optional[str] = None
    next_hash: Optional[str] = None
    merkle_root: Optional[str] = None
    merkle_proof: Optional[List[str]] = None
    digital_signature: Optional[str] = None
    public_key: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    raw_data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["event_type"] = self.event_type.name
        data["status"] = self.status.name
        return data

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class WitnessChain:
    """Witness chain (blockchain-like structure)."""

    chain_id: str
    genesis_hash: str
    current_hash: str
    block_count: int
    total_events: int
    chain_integrity: bool
    last_update: datetime
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MerkleProof:
    """Merkle tree proof for verification."""

    leaf_hash: str
    root_hash: str
    proof_path: List[Tuple[str, bool]]  # (hash, is_left)
    leaf_index: int
    tree_depth: int
    verification_time_ms: float


class WitnessLayer:
    """
    Cryptographic witness layer for system integrity.
    Provides tamper-evident logging, chain of custody, and verification.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize witness layer."""
        self.config = config or self._default_config()

        # Core components
        self.hash_engine = HashEngine()
        self.merkle_tree: Optional[MerkleTree] = None

        # Witness chain
        self.witness_chain: Optional[WitnessChain] = None
        self.event_store: Dict[str, WitnessEvent] = {}
        self.event_chain: List[WitnessEvent] = []

        # State
        self.initialized = False
        self.event_lock = asyncio.Lock()
        self.chain_lock = asyncio.Lock()

        # Storage
        self.storage_path = Path(self.config["storage"]["local_path"])
        self.backup_path = Path(self.config["storage"]["backup_path"])

        # Statistics
        self.statistics = {
            "total_events": 0,
            "events_by_type": {event_type.name: 0 for event_type in WitnessEventType},
            "events_by_status": {status.name: 0 for status in WitnessStatus},
            "hash_computations": 0,
            "merkle_updates": 0,
            "chain_verifications": 0,
            "failed_verifications": 0,
            "storage_operations": 0,
            "backup_operations": 0,
        }

        # Performance tracking
        self.performance = {
            "average_hash_time_ms": 0.0,
            "average_merkle_time_ms": 0.0,
            "average_verification_time_ms": 0.0,
            "total_processing_time_ms": 0.0,
        }

    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "hash_algorithm": "sha256",
            "merkle_tree_depth": 8,
            "digital_signature": False,
            "signature_algorithm": "ECDSA",
            "curve_name": "secp256k1",
            "storage": {
                "local_path": FileConstants.WITNESS_DIRECTORY,
                "backup_path": "./backups/witness/",
                "retention_days": 30,
                "compression": True,
                "encryption": False,
                "max_file_size_mb": 10,
                "backup_interval_hours": 24,
            },
            "verification": {
                "self_verification": True,
                "cross_validation": True,
                "timestamp_validation": True,
                "chain_integrity": True,
                "merkle_validation": True,
                "signature_validation": False,
            },
            "performance": {
                "hash_cache_size": 1000,
                "event_buffer_size": 100,
                "verification_batch_size": 10,
                "async_processing": True,
            },
            "security": {
                "salt_generation": True,
                "salt_size": 16,
                "key_derivation_iterations": 100000,
                "entropy_source": "os.urandom",
            },
        }

    async def initialize(self) -> bool:
        """Initialize the witness layer."""
        print("🔧 Initializing Witness Layer...")

        try:
            # Initialize storage
            await self._initialize_storage()

            # Initialize hash engine
            self.hash_engine.initialize()

            # Load or create witness chain
            await self._load_or_create_chain()

            # Initialize Merkle tree
            await self._initialize_merkle_tree()

            # Start background tasks
            await self._start_background_tasks()

            self.initialized = True
            print(
                f"✅ Witness Layer initialized. Chain ID: {self.witness_chain.chain_id}"
            )
            return True

        except Exception as e:
            print(f"❌ Witness Layer initialization failed: {e}")
            return False

    async def _initialize_storage(self):
        """Initialize storage directories."""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.backup_path.mkdir(parents=True, exist_ok=True)

        print(f"  📁 Storage initialized: {self.storage_path}")

    async def _load_or_create_chain(self):
        """Load existing witness chain or create new one."""
        chain_file = self.storage_path / "witness_chain.json"

        if chain_file.exists():
            try:
                with open(chain_file, "r") as f:
                    chain_data = json.load(f)

                self.witness_chain = WitnessChain(
                    chain_id=chain_data["chain_id"],
                    genesis_hash=chain_data["genesis_hash"],
                    current_hash=chain_data["current_hash"],
                    block_count=chain_data["block_count"],
                    total_events=chain_data["total_events"],
                    chain_integrity=chain_data["chain_integrity"],
                    last_update=datetime.fromisoformat(chain_data["last_update"]),
                    metadata=chain_data.get("metadata"),
                )

                # Load events
                await self._load_events()

                print(
                    f"  🔗 Loaded existing witness chain: {self.witness_chain.chain_id}"
                )

            except Exception as e:
                print(f"  ⚠️ Failed to load witness chain: {e}. Creating new chain.")
                await self._create_new_chain()
        else:
            await self._create_new_chain()

    async def _create_new_chain(self):
        """Create new witness chain."""
        chain_id = str(uuid4())
        genesis_time = datetime.now()

        # Create genesis hash
        genesis_data = {
            "chain_id": chain_id,
            "creation_time": genesis_time.isoformat(),
            "system": "Crusader Combat Refrigerator",
            "version": "1.0.0",
        }

        genesis_hash = self._compute_hash(genesis_data)

        self.witness_chain = WitnessChain(
            chain_id=chain_id,
            genesis_hash=genesis_hash,
            current_hash=genesis_hash,
            block_count=1,
            total_events=0,
            chain_integrity=True,
            last_update=genesis_time,
            metadata=genesis_data,
        )

        # Save chain
        await self._save_chain()

        print(f"  🆕 Created new witness chain: {chain_id}")

    async def _load_events(self):
        """Load witness events from storage."""
        events_dir = self.storage_path / "events"
        if not events_dir.exists():
            return

        event_files = sorted(events_dir.glob("*.json"))

        for event_file in event_files:
            try:
                with open(event_file, "r") as f:
                    event_data = json.load(f)

                event = WitnessEvent(
                    event_id=event_data["event_id"],
                    timestamp=datetime.fromisoformat(event_data["timestamp"]),
                    event_type=WitnessEventType[event_data["event_type"]],
                    status=WitnessStatus[event_data["status"]],
                    data_hash=event_data["data_hash"],
                    previous_hash=event_data.get("previous_hash"),
                    next_hash=event_data.get("next_hash"),
                    merkle_root=event_data.get("merkle_root"),
                    merkle_proof=event_data.get("merkle_proof"),
                    digital_signature=event_data.get("digital_signature"),
                    public_key=event_data.get("public_key"),
                    metadata=event_data.get("metadata"),
                    raw_data=event_data.get("raw_data"),
                )

                self.event_store[event.event_id] = event
                self.event_chain.append(event)

                # Update statistics
                self.statistics["total_events"] += 1
                self.statistics["events_by_type"][event.event_type.name] += 1
                self.statistics["events_by_status"][event.status.name] += 1

            except Exception as e:
                print(f"  ⚠️ Failed to load event {event_file}: {e}")

        print(f"  📊 Loaded {len(self.event_store)} witness events")

    async def _initialize_merkle_tree(self):
        """Initialize Merkle tree with existing events."""
        if not self.event_chain:
            self.merkle_tree = MerkleTree()
            return

        # Extract hashes from events
        event_hashes = [event.data_hash for event in self.event_chain]

        # Build Merkle tree
        self.merkle_tree = MerkleTree()
        root = self.merkle_tree.build_from_data(event_hashes)

        print(f"  🌳 Merkle tree initialized. Root hash: {root.hash_value}")

    async def _start_background_tasks(self):
        """Start background maintenance tasks."""
        # Start chain verification task
        if self.config["verification"]["self_verification"]:
            asyncio.create_task(self._periodic_chain_verification())

        # Start backup task
        asyncio.create_task(self._periodic_backup())

    async def witness_event(
        self,
        event_type: WitnessEventType,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        require_verification: bool = True,
    ) -> WitnessEvent:
        """
        Create and store a witness event.

        Args:
            event_type: Type of event
            data: Event data to witness
            metadata: Additional metadata
            require_verification: Whether to verify the event immediately

        Returns:
            WitnessEvent object
        """
        if not self.initialized:
            raise RuntimeError("Witness Layer not initialized")

        async with self.event_lock:
            return await self._create_witness_event(
                event_type, data, metadata, require_verification
            )

    async def _create_witness_event(
        self,
        event_type: WitnessEventType,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]],
        require_verification: bool,
    ) -> WitnessEvent:
        """Internal method to create witness event."""
        event_id = str(uuid4())
        timestamp = datetime.now()

        # Compute data hash
        start_time = time.time()
        data_hash = self._compute_hash(data)
        hash_time = (time.time() - start_time) * 1000

        # Update performance statistics
        self.performance["total_processing_time_ms"] += hash_time
        self.performance["average_hash_time_ms"] = self.performance[
            "total_processing_time_ms"
        ] / (self.statistics["hash_computations"] + 1)
        self.statistics["hash_computations"] += 1

        # Get previous hash
        previous_hash = self.witness_chain.current_hash if self.witness_chain else None

        # Create event
        event = WitnessEvent(
            event_id=event_id,
            timestamp=timestamp,
            event_type=event_type,
            status=WitnessStatus.PENDING,
            data_hash=data_hash,
            previous_hash=previous_hash,
            metadata=metadata,
            raw_data=data,
        )

        # Update Merkle tree
        if self.merkle_tree:
            start_time = time.time()
            # Add to Merkle tree
            # Note: In a real implementation, we would update the Merkle tree incrementally
            merkle_time = (time.time() - start_time) * 1000
            self.performance["average_merkle_time_ms"] = (
                self.performance["average_merkle_time_ms"]
                * self.statistics["merkle_updates"]
                + merkle_time
            ) / (self.statistics["merkle_updates"] + 1)
            self.statistics["merkle_updates"] += 1

        # Update witness chain
        async with self.chain_lock:
            # Compute new chain hash
            chain_data = {
                "previous_hash": self.witness_chain.current_hash,
                "event_hash": data_hash,
                "timestamp": timestamp.isoformat(),
                "event_count": self.witness_chain.total_events + 1,
            }

            new_hash = self._compute_hash(chain_data)

            # Update event
            event.next_hash = new_hash
            if self.merkle_tree and self.merkle_tree.root:
                event.merkle_root = self.merkle_tree.root.hash_value

            # Update chain
            self.witness_chain.current_hash = new_hash
            self.witness_chain.block_count += 1
            self.witness_chain.total_events += 1
            self.witness_chain.last_update = timestamp

        # Store event
        self.event_store[event_id] = event
        self.event_chain.append(event)

        # Update statistics
        self.statistics["total_events"] += 1
        self.statistics["events_by_type"][event_type.name] += 1
        self.statistics["events_by_status"][WitnessStatus.PENDING.name] += 1

        # Save event and chain
        await self._save_event(event)
        await self._save_chain()

        # Verify if required
        if require_verification:
            verification_result = await self.verify_event(event_id)
            if verification_result["valid"]:
                event.status = WitnessStatus.VERIFIED
                self.statistics["events_by_status"][WitnessStatus.VERIFIED.name] += 1
                self.statistics["events_by_status"][WitnessStatus.PENDING.name] -= 1
            else:
                event.status = WitnessStatus.INVALID
                self.statistics["events_by_status"][WitnessStatus.INVALID.name] += 1
                self.statistics["events_by_status"][WitnessStatus.PENDING.name] -= 1
                self.statistics["failed_verifications"] += 1

            await self._save_event(event)

        print(f"🔐 Witnessed event {event_id} ({event_type.name})")
        return event

    def _compute_hash(self, data: Any) -> str:
        """Compute hash of data."""
        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)

        return hashlib.sha256(data_str.encode("utf-8")).hexdigest()

    async def verify_event(self, event_id: str) -> Dict[str, Any]:
        """
        Verify a witness event.

        Returns:
            Dictionary with verification results
        """
        if event_id not in self.event_store:
            return {"valid": False, "error": "Event not found"}

        event = self.event_store[event_id]
        start_time = time.time()

        verification_results = {
            "event_id": event_id,
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type.name,
            "valid": True,
            "checks": {},
            "errors": [],
        }

        # Check 1: Data hash verification
        if event.raw_data:
            computed_hash = self._compute_hash(event.raw_data)
            verification_results["checks"]["data_hash"] = (
                computed_hash == event.data_hash
            )
            if not verification_results["checks"]["data_hash"]:
                verification_results["valid"] = False
                verification_results["errors"].append("Data hash mismatch")

        # Check 2: Chain integrity
        if event.previous_hash:
            # Find previous event
            prev_event = None
            for e in self.event_chain:
                if e.data_hash == event.previous_hash:
                    prev_event = e
                    break

            if prev_event:
                verification_results["checks"]["chain_integrity"] = True
                verification_results["checks"]["previous_event_found"] = True
                verification_results["checks"]["timestamp_order"] = (
                    prev_event.timestamp <= event.timestamp
                )

                if not verification_results["checks"]["timestamp_order"]:
                    verification_results["valid"] = False
                    verification_results["errors"].append("Timestamp out of order")
            else:
                verification_results["checks"]["chain_integrity"] = False
                verification_results["checks"]["previous_event_found"] = False
                verification_results["valid"] = False
                verification_results["errors"].append(
                    "Previous event not found in chain"
                )
        else:
            verification_results["checks"]["chain_integrity"] = (
                True  # First event in chain
            )
            verification_results["checks"]["previous_event_found"] = True

        # Check 3: Signature verification (if signed)
        if event.signature and event.public_key:
            try:
                verification_results["checks"]["signature_valid"] = (
                    self._verify_signature(
                        event.data_hash, event.signature, event.public_key
                    )
                )
                if not verification_results["checks"]["signature_valid"]:
                    verification_results["valid"] = False
                    verification_results["errors"].append("Invalid signature")
            except Exception as e:
                verification_results["checks"]["signature_valid"] = False
                verification_results["valid"] = False
                verification_results["errors"].append(
                    f"Signature verification failed: {e}"
                )
        else:
            verification_results["checks"]["signature_valid"] = True  # Not required

        # Check 4: Timestamp validity
        now = datetime.now()
        time_diff = abs((event.timestamp - now).total_seconds())
        verification_results["checks"]["timestamp_valid"] = (
            time_diff < 3600
        )  # Within 1 hour
        if not verification_results["checks"]["timestamp_valid"]:
            verification_results["valid"] = False
            verification_results["errors"].append("Timestamp too far from current time")

        # Check 5: Event type validity
        verification_results["checks"]["event_type_valid"] = (
            event.event_type in WitnessEventType
        )
        if not verification_results["checks"]["event_type_valid"]:
            verification_results["valid"] = False
            verification_results["errors"].append("Invalid event type")

        # Add verification metadata
        verification_results["verification_time_ms"] = (time.time() - start_time) * 1000
        verification_results["chain_length"] = len(self.event_chain)
        verification_results["event_index"] = self._get_event_index(event_id)

        # Update verification statistics
        self.verification_stats["total_verifications"] += 1
        if verification_results["valid"]:
            self.verification_stats["successful_verifications"] += 1
        else:
            self.verification_stats["failed_verifications"] += 1

        # Cache verification result
        self.verification_cache[event_id] = {
            "result": verification_results,
            "timestamp": datetime.now(),
        }

        return verification_results
