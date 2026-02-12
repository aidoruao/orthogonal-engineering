"""
instance_manager.py
===================

MULTI-INSTANCE AI MANAGEMENT SYSTEM
Folder isolation with clear instance tracking

PRINCIPLE: "Each AI instance gets its own folder, all artifacts stay inside"
FEATURES:
1. Automatic folder creation with deterministic naming
2. Instance registry for tracking all instances
3. File creation logging with hashes
4. Isolation enforcement (no cross-folder tampering)
5. Global audit trail
6. External invariants compliance

ARCHITECTURE:
/repo_root/instances/
    Logos_Repo-2026-02-01-A1B2/
        instance_registry.json
        files/
        logs/
    Logos_Repo-2026-02-01-B3C4/
        instance_registry.json
        files/
        logs/
"""

import hashlib
import json
import os
import shutil
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class InstanceConfig:
    """Configuration for instance management"""

    # Base paths
    INSTANCES_ROOT = "instances"
    FILES_SUBDIR = "files"
    LOGS_SUBDIR = "logs"
    REGISTRY_FILE = "instance_registry.json"
    GLOBAL_REGISTRY = "global_instance_registry.json"

    # Naming conventions
    NAME_PREFIX = "Logos_Repo"
    TIMESTAMP_FORMAT = "%Y-%m-%d"
    HASH_LENGTH = 8

    # Registry structure
    MAX_INSTANCES = 1000
    CLEANUP_DAYS = 30  # Auto-clean instances older than this


class InstanceFile:
    """Represents a file created by an instance"""

    def __init__(self, filename: str, content_hash: str, metadata: Dict = None):
        self.filename = filename
        self.content_hash = content_hash
        self.timestamp = datetime.now().isoformat()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict:
        return {
            "filename": self.filename,
            "hash": self.content_hash,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "InstanceFile":
        return cls(
            filename=data["filename"],
            content_hash=data["hash"],
            metadata=data.get("metadata", {}),
        )


class InstanceRegistry:
    """Registry for a single AI instance"""

    def __init__(self, instance_id: str, alias: str, instance_path: Path):
        self.instance_id = instance_id
        self.alias = alias
        self.instance_path = instance_path
        self.start_time = datetime.now().isoformat()
        self.files_created: List[InstanceFile] = []
        self.last_activity = self.start_time
        self.is_active = True

        # Create instance directory structure
        self._create_directory_structure()

    def _create_directory_structure(self):
        """Create the directory structure for this instance"""
        # Create main instance directory
        self.instance_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (self.instance_path / InstanceConfig.FILES_SUBDIR).mkdir(exist_ok=True)
        (self.instance_path / InstanceConfig.LOGS_SUBDIR).mkdir(exist_ok=True)

    def add_file(self, filename: str, content: str, metadata: Dict = None) -> str:
        """
        Add a file to this instance's registry

        Args:
            filename: Name of the file
            content: File content
            metadata: Optional metadata about the file

        Returns:
            Path to the created file
        """
        # Calculate content hash
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

        # Create file record
        file_record = InstanceFile(filename, content_hash, metadata)
        self.files_created.append(file_record)

        # Update last activity
        self.last_activity = datetime.now().isoformat()

        # Determine file path
        if "." in filename and filename.split(".")[-1] in [
            "py",
            "js",
            "html",
            "css",
            "json",
            "txt",
            "md",
        ]:
            # Code/text files go in files directory
            file_path = self.instance_path / InstanceConfig.FILES_SUBDIR / filename
        else:
            # Other files go in root instance directory
            file_path = self.instance_path / filename

        # Write file
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Save registry
        self.save()

        return str(file_path)

    def get_file_path(self, filename: str) -> Optional[Path]:
        """Get the path to a file created by this instance"""
        # Check files subdirectory first
        files_path = self.instance_path / InstanceConfig.FILES_SUBDIR / filename
        if files_path.exists():
            return files_path

        # Check root instance directory
        root_path = self.instance_path / filename
        if root_path.exists():
            return root_path

        return None

    def list_files(self) -> List[Dict]:
        """List all files created by this instance"""
        return [file.to_dict() for file in self.files_created]

    def get_stats(self) -> Dict:
        """Get statistics for this instance"""
        return {
            "instance_id": self.instance_id,
            "alias": self.alias,
            "start_time": self.start_time,
            "last_activity": self.last_activity,
            "total_files": len(self.files_created),
            "is_active": self.is_active,
            "instance_path": str(self.instance_path),
        }

    def save(self):
        """Save registry to disk"""
        registry_data = {
            "instance_id": self.instance_id,
            "alias": self.alias,
            "start_time": self.start_time,
            "last_activity": self.last_activity,
            "is_active": self.is_active,
            "files_created": [file.to_dict() for file in self.files_created],
        }

        registry_path = self.instance_path / InstanceConfig.REGISTRY_FILE
        with open(registry_path, "w", encoding="utf-8") as f:
            json.dump(registry_data, f, indent=2, ensure_ascii=False)

    def deactivate(self):
        """Deactivate this instance"""
        self.is_active = False
        self.last_activity = datetime.now().isoformat()
        self.save()

    @classmethod
    def load(cls, instance_path: Path) -> "InstanceRegistry":
        """Load registry from disk"""
        registry_path = instance_path / InstanceConfig.REGISTRY_FILE

        if not registry_path.exists():
            raise FileNotFoundError(f"Registry not found: {registry_path}")

        with open(registry_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        instance = cls(
            instance_id=data["instance_id"],
            alias=data["alias"],
            instance_path=instance_path,
        )

        instance.start_time = data["start_time"]
        instance.last_activity = data["last_activity"]
        instance.is_active = data.get("is_active", True)
        instance.files_created = [
            InstanceFile.from_dict(file_data)
            for file_data in data.get("files_created", [])
        ]

        return instance


class InstanceManager:
    """Manages multiple AI instances with folder isolation"""

    def __init__(self, root_path: str = None):
        self.root_path = Path(root_path or InstanceConfig.INSTANCES_ROOT)
        self.root_path.mkdir(parents=True, exist_ok=True)

        # Load or create global registry
        self.global_registry_path = self.root_path / InstanceConfig.GLOBAL_REGISTRY
        self.instances: Dict[str, InstanceRegistry] = {}
        self._load_global_registry()

    def _load_global_registry(self):
        """Load the global registry of all instances"""
        if self.global_registry_path.exists():
            with open(self.global_registry_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Load each instance
            for instance_data in data.get("instances", []):
                instance_path = self.root_path / instance_data["alias"]
                if instance_path.exists():
                    try:
                        instance = InstanceRegistry.load(instance_path)
                        self.instances[instance.instance_id] = instance
                    except Exception as e:
                        print(
                            f"Warning: Failed to load instance {instance_data['alias']}: {e}"
                        )
        else:
            # Create new global registry
            self._save_global_registry()

    def _save_global_registry(self):
        """Save the global registry to disk"""
        instances_data = []
        for instance in self.instances.values():
            instances_data.append(
                {
                    "instance_id": instance.instance_id,
                    "alias": instance.alias,
                    "start_time": instance.start_time,
                    "last_activity": instance.last_activity,
                    "is_active": instance.is_active,
                    "path": str(instance.instance_path.relative_to(self.root_path)),
                }
            )

        global_data = {
            "total_instances": len(self.instances),
            "active_instances": sum(1 for i in self.instances.values() if i.is_active),
            "last_updated": datetime.now().isoformat(),
            "instances": instances_data,
        }

        with open(self.global_registry_path, "w", encoding="utf-8") as f:
            json.dump(global_data, f, indent=2, ensure_ascii=False)

    def _generate_instance_alias(self) -> str:
        """Generate a deterministic alias for a new instance"""
        timestamp = datetime.now().strftime(InstanceConfig.TIMESTAMP_FORMAT)
        random_suffix = hashlib.sha256(
            f"{timestamp}{uuid.uuid4()}".encode()
        ).hexdigest()[: InstanceConfig.HASH_LENGTH]

        return f"{InstanceConfig.NAME_PREFIX}-{timestamp}-{random_suffix}"

    def create_instance(self, alias: str = None) -> InstanceRegistry:
        """
        Create a new AI instance with its own folder

        Args:
            alias: Optional custom alias, otherwise auto-generated

        Returns:
            The created instance registry
        """
        # Generate instance ID
        instance_id = hashlib.sha256(
            f"{alias or ''}{time.time()}{uuid.uuid4()}".encode()
        ).hexdigest()[:32]

        # Generate alias if not provided
        if not alias:
            alias = self._generate_instance_alias()

        # Ensure alias is unique
        counter = 1
        original_alias = alias
        while any(inst.alias == alias for inst in self.instances.values()):
            alias = f"{original_alias}_{counter}"
            counter += 1

        # Create instance
        instance_path = self.root_path / alias
        instance = InstanceRegistry(instance_id, alias, instance_path)

        # Register instance
        self.instances[instance_id] = instance
        self._save_global_registry()

        print(f"✅ Created instance: {alias} (ID: {instance_id})")
        print(f"   Path: {instance_path}")

        return instance

    def get_instance(self, instance_id: str) -> Optional[InstanceRegistry]:
        """Get an instance by ID"""
        return self.instances.get(instance_id)

    def get_instance_by_alias(self, alias: str) -> Optional[InstanceRegistry]:
        """Get an instance by alias"""
        for instance in self.instances.values():
            if instance.alias == alias:
                return instance
        return None

    def list_instances(self, active_only: bool = False) -> List[Dict]:
        """List all instances with their stats"""
        instances = []
        for instance in self.instances.values():
            if active_only and not instance.is_active:
                continue
            instances.append(instance.get_stats())

        # Sort by last activity (most recent first)
        instances.sort(key=lambda x: x["last_activity"], reverse=True)
        return instances

    def deactivate_instance(self, instance_id: str) -> bool:
        """Deactivate an instance"""
        instance = self.get_instance(instance_id)
        if instance:
            instance.deactivate()
            self._save_global_registry()
            return True
        return False

    def cleanup_old_instances(self, days: int = None):
        """
        Clean up instances older than specified days

        Args:
            days: Number of days, uses InstanceConfig.CLEANUP_DAYS if None
        """
        if days is None:
            days = InstanceConfig.CLEANUP_DAYS

        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        instances_to_remove = []

        for instance_id, instance in self.instances.items():
            instance_time = datetime.fromisoformat(instance.last_activity).timestamp()
            if instance_time < cutoff_time and not instance.is_active:
                instances_to_remove.append(instance_id)

        for instance_id in instances_to_remove:
            instance = self.instances[instance_id]
            try:
                # Remove directory
                shutil.rmtree(instance.instance_path)
                # Remove from registry
                del self.instances[instance_id]
                print(f"🧹 Cleaned up old instance: {instance.alias}")
            except Exception as e:
                print(f"Warning: Failed to clean up instance {instance.alias}: {e}")

        if instances_to_remove:
            self._save_global_registry()

    def get_global_stats(self) -> Dict:
        """Get global statistics about all instances"""
        total_files = sum(
            len(instance.files_created) for instance in self.instances.values()
        )
        active_instances = sum(
            1 for instance in self.instances.values() if instance.is_active
        )

        # Calculate storage usage
        total_size = 0
        for instance in self.instances.values():
            for root, dirs, files in os.walk(instance.instance_path):
                for file in files:
                    file_path = Path(root) / file
                    total_size += file_path.stat().st_size

        return {
            "total_instances": len(self.instances),
            "active_instances": active_instances,
            "total_files_created": total_files,
            "total_storage_bytes": total_size,
            "total_storage_mb": total_size / (1024 * 1024),
            "last_updated": datetime.now().isoformat(),
        }

    def scan_all_files(self) -> Dict[str, List[Dict]]:
        """
        Scan all files across all instances

        Returns:
            Dictionary mapping instance aliases to their files
        """
        all_files = {}
        for instance in self.instances.values():
            all_files[instance.alias] = instance.list_files()
        return all_files

    def find_file_by_hash(self, content_hash: str) -> List[Dict]:
        """
        Find all instances of a file by content hash

        Returns:
            List of file occurrences across instances
        """
        occurrences = []
        for instance in self.instances.values():
            for file in instance.files_created:
                if file.content_hash == content_hash:
                    occurrences.append(
                        {
                            "instance_alias": instance.alias,
                            "instance_id": instance.instance_id,
                            "filename": file.filename,
                            "timestamp": file.timestamp,
                            "metadata": file.metadata,
                        }
                    )
        return occurrences


class ConstrainedAIInstance:
    """
    AI instance constrained to its own folder

    This is the interface that AI instances should use
    """

    def __init__(self, manager: InstanceManager, alias: str = None):
        self.manager = manager
        self.instance = manager.create_instance(alias)
        self.instance_id = self.instance.instance_id
        self.alias = self.instance.alias

        print(f"🤖 AI Instance Initialized:")
        print(f"   ID: {self.instance_id}")
        print(f"   Alias: {self.alias}")
        print(f"   Folder: {self.instance.instance_path}")
        print(f"   Rules: All files stay in this folder")

    def create_file(self, filename: str, content: str, metadata: Dict = None) -> str:
        """
        Create a file in this instance's folder

        Args:
            filename: Name of the file
            content: File content
            metadata: Optional metadata

        Returns:
            Path to the created file
        """
        # Enforce filename constraints
        if not self._is_valid_filename(filename):
            raise ValueError(f"Invalid filename: {filename}")

        # Add instance metadata
        if metadata is None:
            metadata = {}

        metadata.update(
            {
                "created_by_instance": self.instance_id,
                "created_by_alias": self.alias,
                "creation_timestamp": datetime.now().isoformat(),
            }
        )

        # Create the file
        file_path = self.instance.add_file(filename, content, metadata)

        print(f"📄 Created file: {filename}")
        print(f"   Path: {file_path}")
        print(f"   Hash: {hashlib.sha256(content.encode()).hexdigest()[:16]}")

        return file_path

    def _is_valid_filename(self, filename: str) -> bool:
        """Validate filename to prevent path traversal"""
        # Prevent directory traversal
        if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
            return False

        # Prevent absolute paths
        if Path(filename).is_absolute():
            return False

        # Basic filename validation
        if not filename or len(filename) > 255:
            return False

        # Prevent reserved characters
        reserved_chars = ["<", ">", ":", '"', "|", "?", "*"]
        if any(char in filename for char in reserved_chars):
            return False

        return True

    def read_file(self, filename: str) -> Optional[str]:
        """Read a file from this instance's folder"""
        file_path = self.instance.get_file_path(filename)
        if file_path and file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return None

    def list_my_files(self) -> List[Dict]:
        """List all files created by this instance"""
        return self.instance.list_files()

    def get_my_stats(self) -> Dict:
        """Get statistics for this instance"""
        return self.instance.get_stats()

    def deactivate(self):
        """Deactivate this instance"""
        self.instance.deactivate()
        print(f"🛑 Instance deactivated: {self.alias}")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - deactivate instance"""
        self.deactivate()


# ==================== TEST FUNCTIONS ====================


def test_instance_management():
    """Test the instance management system"""
    print("\n" + "=" * 70)
    print("TESTING MULTI-INSTANCE AI MANAGEMENT SYSTEM")
    print("=" * 70)

    # Create manager
    manager = InstanceManager()
    print("✅ Instance Manager created")

    # Create first AI instance
    print("\n1. Creating first AI instance...")
    ai1 = ConstrainedAIInstance(manager, "Logos_Repo-2026-02-01-TEST1")

    # Create files in first instance
    print("\n2. Creating files in first instance...")
    file1_path = ai1.create_file(
        "test_script.py",
        "print('Hello from AI Instance 1')\n# Created by: " + ai1.alias,
        {"purpose": "test script", "language": "python"},
    )

    file2_path = ai1.create_file(
        "analysis.md",
        "# Analysis Report\n\nCreated by: "
        + ai1.alias
        + "\n\nThis is a test analysis.",
        {"report_type": "analysis", "pages": 1},
    )

    # Create second AI instance
    print("\n3. Creating second AI instance...")
    ai2 = ConstrainedAIInstance(manager, "Logos_Repo-2026-02-01-TEST2")

    # Create files in second instance
    print("\n4. Creating files in second instance...")
    file3_path = ai2.create_file(
        "data_processor.py",
        "def process_data():\n    print('Processing data from AI Instance 2')\n    return 42",
        {"purpose": "data processing", "language": "python"},
    )

    # List all instances
    print("\n5. Listing all instances...")
    instances = manager.list_instances()
    for i, instance in enumerate(instances, 1):
        print(
            f"   {i}. {instance['alias']} - {instance['total_files']} files - Active: {instance['is_active']}"
        )

    # Show global stats
    print("\n6. Global statistics:")
    stats = manager.get_global_stats()
    print(f"   Total instances: {stats['total_instances']}")
    print(f"   Active instances: {stats['active_instances']}")
    print(f"   Total files created: {stats['total_files_created']}")
    print(f"   Storage used: {stats['total_storage_mb']:.2f} MB")

    # Scan all files
    print("\n7. Scanning all files across instances...")
    all_files = manager.scan_all_files()
    for alias, files in all_files.items():
        print(f"   {alias}: {len(files)} files")
        for file in files[:3]:  # Show first 3 files
            print(f"     - {file['filename']} ({file['hash']})")

    # Test file hash search
    print("\n8. Testing file hash search...")
    if ai1.list_my_files():
        test_hash = ai1.list_my_files()[0]["hash"]
        occurrences = manager.find_file_by_hash(test_hash)
        print(f"   Hash {test_hash} found in {len(occurrences)} instance(s)")

    # Deactivate instances
    print("\n9. Deactivating instances...")
    ai1.deactivate()
    ai2.deactivate()

    # Cleanup test (optional)
    print("\n10. Cleaning up test instances...")
    manager.cleanup_old_instances(days=0)  # Clean up immediately for test

    print("\n" + "=" * 70)
    print("✅ TEST COMPLETED SUCCESSFULLY")
    print("=" * 70)
    return True


def create_minimal_ide_ai_instance():
    """
    Create a minimal IDE AI instance with folder constraint

    This is the main function to use when creating a new AI instance
    that needs to be constrained to its own folder.
    """
    print("\n" + "=" * 70)
    print("CREATING MINIMAL IDE AI INSTANCE")
    print("=" * 70)

    # Create manager
    manager = InstanceManager()

    # Create new instance with auto-generated name
    ai_instance = ConstrainedAIInstance(manager)

    print("\n📋 INSTANCE RULES:")
    print("   1. All files created stay in: " + str(ai_instance.instance.instance_path))
    print("   2. No files can escape this folder")
    print("   3. All file creations are logged")
    print("   4. Instance can be deactivated when done")
    print("   5. Global registry tracks all instances")

    print("\n💡 Usage:")
    print("   - Use ai_instance.create_file() to create files")
    print("   - Use ai_instance.read_file() to read files")
    print("   - Use ai_instance.list_my_files() to see what you've created")
    print("   - Use ai_instance.deactivate() when finished")
    print("   - Use 'with' context manager for automatic cleanup")

    print("\n" + "=" * 70)
    return ai_instance


def example_usage():
    """Example of how to use the constrained AI instance system"""
    print("\n" + "=" * 70)
    print("EXAMPLE: CONSTRAINED AI INSTANCE USAGE")
    print("=" * 70)

    # Method 1: Using context manager (recommended)
    print("\nMethod 1: Using context manager")
    print("-" * 40)

    manager = InstanceManager()

    with ConstrainedAIInstance(manager, "Example-Instance") as ai:
        # Create some files
        ai.create_file(
            "hello.py",
            "print('Hello from constrained AI instance!')\nprint(f'Instance: {ai.alias}')",
            {"example": True, "type": "python_script"},
        )

        ai.create_file(
            "README.md",
            f"# {ai.alias}\n\nThis is a test instance with folder constraint.",
            {"documentation": True},
        )

        # List created files
        print("\nFiles created:")
        for file in ai.list_my_files():
            print(f"  - {file['filename']} ({file['hash']})")

    print("\nInstance automatically deactivated when context exits")

    # Method 2: Manual management
    print("\n\nMethod 2: Manual management")
    print("-" * 40)

    ai2 = ConstrainedAIInstance(manager, "Manual-Example")

    try:
        # Create files
        ai2.create_file(
            "config.json", '{"mode": "test", "instance": "' + ai2.alias + '"}'
        )

        # Read file back
        content = ai2.read_file("config.json")
        print(f"\nRead file content: {content[:50]}...")

        # Get stats
        stats = ai2.get_my_stats()
        print(f"\nInstance stats: {stats['total_files']} files created")

    finally:
        # Always deactivate
        ai2.deactivate()

    # Show global view
    print("\n\nGlobal instance view:")
    print("-" * 40)
    global_stats = manager.get_global_stats()
    print(f"Total instances in system: {global_stats['total_instances']}")
    print(f"Total files created: {global_stats['total_files_created']}")

    print("\n" + "=" * 70)
    print("✅ EXAMPLE COMPLETED")
    print("=" * 70)


def main():
    """Main function to run tests or create instances"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Multi-Instance AI Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Run comprehensive tests
  python instance_manager.py --test

  # Create a new constrained AI instance
  python instance_manager.py --create

  # Show example usage
  python instance_manager.py --example

  # List all instances
  python instance_manager.py --list

  # Get global statistics
  python instance_manager.py --stats
        """,
    )

    parser.add_argument("--test", action="store_true", help="Run comprehensive tests")
    parser.add_argument("--create", action="store_true", help="Create new AI instance")
    parser.add_argument("--example", action="store_true", help="Show example usage")
    parser.add_argument("--list", action="store_true", help="List all instances")
    parser.add_argument("--stats", action="store_true", help="Show global statistics")
    parser.add_argument(
        "--cleanup", type=int, help="Cleanup instances older than N days"
    )

    args = parser.parse_args()

    if args.test:
        test_instance_management()
    elif args.create:
        create_minimal_ide_ai_instance()
    elif args.example:
        example_usage()
    elif args.list:
        manager = InstanceManager()
        instances = manager.list_instances()
        print("\n" + "=" * 70)
        print("ALL AI INSTANCES")
        print("=" * 70)
        for i, instance in enumerate(instances, 1):
            status = "🟢 ACTIVE" if instance["is_active"] else "🔴 INACTIVE"
            print(f"\n{i}. {instance['alias']} ({status})")
            print(f"   ID: {instance['instance_id']}")
            print(f"   Created: {instance['start_time']}")
            print(f"   Last activity: {instance['last_activity']}")
            print(f"   Files: {instance['total_files']}")
            print(f"   Path: {instance['instance_path']}")
        print("\n" + "=" * 70)
    elif args.stats:
        manager = InstanceManager()
        stats = manager.get_global_stats()
        print("\n" + "=" * 70)
        print("GLOBAL STATISTICS")
        print("=" * 70)
        print(f"\n📊 Instance Statistics:")
        print(f"   Total instances: {stats['total_instances']}")
        print(f"   Active instances: {stats['active_instances']}")
        print(f"   Total files created: {stats['total_files_created']}")
        print(f"\n💾 Storage Usage:")
        print(f"   Total: {stats['total_storage_mb']:.2f} MB")
        print(
            f"   Average per instance: {stats['total_storage_mb'] / max(1, stats['total_instances']):.2f} MB"
        )
        print(f"\n🕒 Last updated: {stats['last_updated']}")
        print("\n" + "=" * 70)
    elif args.cleanup is not None:
        manager = InstanceManager()
        print(f"\n🧹 Cleaning up instances older than {args.cleanup} days...")
        manager.cleanup_old_instances(days=args.cleanup)
        print("✅ Cleanup completed")
    else:
        # Default: show help
        parser.print_help()


if __name__ == "__main__":
    main()
