"""
constrained_ai_system.py
========================

INTEGRATED CONSTRAINED AI SYSTEM
Combines instance management with DeepSeek API communication

ARCHITECTURE:
1. Each AI instance gets its own isolated folder
2. All file operations stay within instance folder
3. DeepSeek API communication with Σ_LORA constraints
4. Complete audit trail of all operations
5. Global registry for multi-instance tracking

PRINCIPLE: "Each AI instance is constrained to its folder, all artifacts stay inside"
"""

import hashlib
import json
import os
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

# ==================== CONFIGURATION ====================


class SystemConfig:
    """System-wide configuration"""

    # Instance Management
    INSTANCES_ROOT = "instances"
    FILES_SUBDIR = "files"
    LOGS_SUBDIR = "logs"
    REGISTRY_FILE = "instance_registry.json"
    GLOBAL_REGISTRY = "global_instance_registry.json"

    # Instance Naming
    NAME_PREFIX = "AI_Instance"
    TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"
    HASH_LENGTH = 6

    # DeepSeek API
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
    DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
    DEFAULT_MODEL = "deepseek-chat"
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 2000

    # Σ_LORA Constraints
    ENABLE_CONSTRAINTS = True
    CHRIST_SCORE_THRESHOLD = 0.5

    # System Limits
    MAX_FILES_PER_INSTANCE = 100
    MAX_INSTANCES = 1000
    CLEANUP_DAYS = 30


# ==================== INSTANCE MANAGEMENT ====================


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


class InstanceRegistry:
    """Registry for a single AI instance"""

    def __init__(self, instance_id: str, alias: str, instance_path: Path):
        self.instance_id = instance_id
        self.alias = alias
        self.instance_path = instance_path
        self.start_time = datetime.now().isoformat()
        self.files_created: List[InstanceFile] = []
        self.api_calls: List[Dict] = []
        self.last_activity = self.start_time
        self.is_active = True

        # Create directory structure
        self._create_directory_structure()

    def _create_directory_structure(self):
        """Create the directory structure for this instance"""
        self.instance_path.mkdir(parents=True, exist_ok=True)
        (self.instance_path / SystemConfig.FILES_SUBDIR).mkdir(exist_ok=True)
        (self.instance_path / SystemConfig.LOGS_SUBDIR).mkdir(exist_ok=True)

    def add_file(self, filename: str, content: str, metadata: Dict = None) -> Path:
        """Add a file to this instance's registry"""
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
            file_path = self.instance_path / SystemConfig.FILES_SUBDIR / filename
        else:
            file_path = self.instance_path / filename

        # Write file
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Save registry
        self.save()

        return file_path

    def log_api_call(self, request: Dict, response: Dict, metadata: Dict = None):
        """Log an API call made by this instance"""
        api_log = {
            "timestamp": datetime.now().isoformat(),
            "request": request,
            "response": response,
            "metadata": metadata or {},
        }
        self.api_calls.append(api_log)
        self.last_activity = datetime.now().isoformat()
        self.save()

    def get_stats(self) -> Dict:
        """Get statistics for this instance"""
        return {
            "instance_id": self.instance_id,
            "alias": self.alias,
            "start_time": self.start_time,
            "last_activity": self.last_activity,
            "total_files": len(self.files_created),
            "total_api_calls": len(self.api_calls),
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
            "api_calls": self.api_calls,
        }

        registry_path = self.instance_path / SystemConfig.REGISTRY_FILE
        with open(registry_path, "w", encoding="utf-8") as f:
            json.dump(registry_data, f, indent=2, ensure_ascii=False)

    def deactivate(self):
        """Deactivate this instance"""
        self.is_active = False
        self.last_activity = datetime.now().isoformat()
        self.save()


# ==================== DEEPSEEK API INTEGRATION ====================


class DeepSeekAPI:
    """DeepSeek API integration with instance awareness"""

    def __init__(self, instance_registry: InstanceRegistry):
        self.instance = instance_registry
        self.api_key = SystemConfig.DEEPSEEK_API_KEY
        self.api_url = SystemConfig.DEEPSEEK_API_URL

        if not self.api_key:
            print("⚠️  WARNING: DEEPSEEK_API_KEY not found in environment")

    def query(self, prompt: str, context: Dict = None, **kwargs) -> Dict:
        """
        Query DeepSeek API with instance context

        Args:
            prompt: User's message
            context: Additional context for the query
            **kwargs: Additional API parameters

        Returns:
            Dictionary with response and metadata
        """
        # Prepare request
        model = kwargs.get("model", SystemConfig.DEFAULT_MODEL)
        temperature = kwargs.get("temperature", SystemConfig.DEFAULT_TEMPERATURE)
        max_tokens = kwargs.get("max_tokens", SystemConfig.DEFAULT_MAX_TOKENS)

        # Build system message with instance context
        system_message = self._build_system_message(context)

        # Prepare messages
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ]

        # Prepare request payload
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        # Prepare headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Make API call
        try:
            response = requests.post(
                self.api_url, headers=headers, json=payload, timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})

                # Log successful API call
                self.instance.log_api_call(
                    request={
                        "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                        "model": model,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                    response={
                        "success": True,
                        "response": ai_response[:200] + "..."
                        if len(ai_response) > 200
                        else ai_response,
                        "model": result.get("model", model),
                        "usage": usage,
                    },
                    metadata={
                        "instance_id": self.instance.instance_id,
                        "instance_alias": self.instance.alias,
                    },
                )

                return {
                    "success": True,
                    "response": ai_response,
                    "model": result.get("model", model),
                    "usage": usage,
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                }
            else:
                # Log failed API call
                error_msg = f"API Error {response.status_code}: {response.text[:200]}"
                self.instance.log_api_call(
                    request={"prompt": prompt[:100] + "...", "model": model},
                    response={"success": False, "error": error_msg},
                    metadata={"instance_id": self.instance.instance_id},
                )

                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code,
                }

        except Exception as e:
            error_msg = f"Request failed: {str(e)}"
            self.instance.log_api_call(
                request={"prompt": prompt[:100] + "...", "model": model},
                response={"success": False, "error": error_msg},
                metadata={"instance_id": self.instance.instance_id},
            )

            return {"success": False, "error": error_msg}

    def _build_system_message(self, context: Dict = None) -> str:
        """Build system message with instance context"""
        base_message = f"""You are an AI assistant operating within a constrained environment.

INSTANCE CONTEXT:
- Instance ID: {self.instance.instance_id}
- Instance Alias: {self.instance.alias}
- Created: {self.instance.start_time}
- Files created: {len(self.instance.files_created)}

RULES:
1. All outputs should be helpful and accurate
2. Stay within the scope of the instance's purpose
3. Be aware of the instance's file history
"""

        if SystemConfig.ENABLE_CONSTRAINTS:
            base_message += """
Σ_LORA CONSTRAINTS:
1. LOGOS: Be logically consistent and truthful
2. CHALCEDON: Collaborate with human intelligence
3. GRACE: Be forgiving and patient with errors
4. ESCHATON: Serve the ultimate purpose
5. AGAPE: Prioritize love and benefit for others
6. KENOSIS: Do not seek autonomy or self-exaltation
"""

        if context:
            base_message += f"\nADDITIONAL CONTEXT:\n{json.dumps(context, indent=2)}"

        return base_message


# ==================== CONSTRAINED AI INSTANCE ====================


class ConstrainedAIInstance:
    """
    Main class for constrained AI instances

    Each instance:
    1. Has its own isolated folder
    2. Can create files only in its folder
    3. Can communicate with DeepSeek API
    4. Maintains complete audit trail
    5. Cannot access other instances' folders
    """

    def __init__(self, alias: str = None):
        """Initialize a new constrained AI instance"""
        # Generate instance ID
        self.instance_id = hashlib.sha256(
            f"{alias or ''}{time.time()}{uuid.uuid4()}".encode()
        ).hexdigest()[:32]

        # Generate alias if not provided
        if not alias:
            timestamp = datetime.now().strftime(SystemConfig.TIMESTAMP_FORMAT)
            random_suffix = hashlib.sha256(
                f"{timestamp}{uuid.uuid4()}".encode()
            ).hexdigest()[: SystemConfig.HASH_LENGTH]
            self.alias = f"{SystemConfig.NAME_PREFIX}-{timestamp}-{random_suffix}"
        else:
            self.alias = alias

        # Create instance path
        self.instance_path = Path(SystemConfig.INSTANCES_ROOT) / self.alias

        # Create registry
        self.registry = InstanceRegistry(
            self.instance_id, self.alias, self.instance_path
        )

        # Initialize DeepSeek API
        self.api = DeepSeekAPI(self.registry)

        # Print initialization message
        self._print_init_message()

    def _print_init_message(self):
        """Print initialization message"""
        print("\n" + "=" * 70)
        print("🤖 CONSTRAINED AI INSTANCE CREATED")
        print("=" * 70)
        print(f"Instance ID: {self.instance_id}")
        print(f"Instance Alias: {self.alias}")
        print(f"Instance Path: {self.instance_path}")
        print(
            f"DeepSeek API: {'Available' if SystemConfig.DEEPSEEK_API_KEY else 'Not configured'}"
        )
        print(
            f"Σ_LORA Constraints: {'Enabled' if SystemConfig.ENABLE_CONSTRAINTS else 'Disabled'}"
        )
        print("\n📋 INSTANCE RULES:")
        print("   1. All files stay in instance folder")
        print("   2. No cross-instance file access")
        print("   3. Complete audit trail maintained")
        print("   4. API calls are logged")
        print("   5. Deactivate when finished")
        print("=" * 70)

    def create_file(self, filename: str, content: str, metadata: Dict = None) -> str:
        """
        Create a file in the instance's folder

        Args:
            filename: Name of the file
            content: File content
            metadata: Optional metadata

        Returns:
            Path to the created file
        """
        # Validate filename
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
        file_path = self.registry.add_file(filename, content, metadata)

        print(f"📄 Created file: {filename}")
        print(f"   Path: {file_path}")
        print(f"   Size: {len(content)} bytes")

        return str(file_path)

    def _is_valid_filename(self, filename: str) -> bool:
        """Validate filename to prevent path traversal"""
        if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
            return False
        if Path(filename).is_absolute():
            return False
        if not filename or len(filename) > 255:
            return False
        reserved_chars = ["<", ">", ":", '"', "|", "?", "*"]
        if any(char in filename for char in reserved_chars):
            return False
        return True

    def query_ai(self, prompt: str, context: Dict = None, **kwargs) -> Dict:
        """
        Query DeepSeek AI with instance context

        Args:
            prompt: User's message
            context: Additional context
            **kwargs: API parameters (model, temperature, max_tokens)

        Returns:
            Dictionary with response and metadata
        """
        print(f"\n🤔 Querying AI with instance context...")
        print(f"   Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")

        result = self.api.query(prompt, context, **kwargs)

        if result["success"]:
            print(f"✅ AI Response received")
            print(f"   Tokens: {result.get('total_tokens', 0)}")
            return result
        else:
            print(f"❌ AI Query failed: {result.get('error', 'Unknown error')}")
            return result

    def create_file_from_ai(
        self, filename: str, prompt: str, context: Dict = None
    ) -> Optional[str]:
        """
        Create a file using AI assistance

        Args:
            filename: Name of the file to create
            prompt: Instructions for the AI
            context: Additional context

        Returns:
            Path to created file, or None if failed
        """
        # Build AI prompt for file creation
        ai_prompt = f"""Create content for a file named '{filename}'.

Instructions:
{prompt}

Requirements:
1. Provide only the file content, no explanations
2. Format appropriately for the file type
3. Include necessary imports/headers if applicable
4. Make it production-ready code/documentation

File content:"""

        # Query AI
        result = self.query_ai(ai_prompt, context)

        if result["success"]:
            # Create file with AI content
            file_path = self.create_file(
                filename,
                result["response"],
                {
                    "created_with_ai": True,
                    "ai_prompt": prompt,
                    "ai_model": result.get("model"),
                    "ai_tokens": result.get("total_tokens", 0),
                },
            )
            return file_path

        return None

    def get_stats(self) -> Dict:
        """Get statistics for this instance"""
        return self.registry.get_stats()

    def list_files(self) -> List[Dict]:
        """List all files created by this instance"""
        return [file.to_dict() for file in self.registry.files_created]

    def list_api_calls(self) -> List[Dict]:
        """List all API calls made by this instance"""
        return self.registry.api_calls

    def deactivate(self):
        """Deactivate this instance"""
        self.registry.deactivate()
        print(f"\n🛑 Instance deactivated: {self.alias}")
        print(f"   Total files created: {len(self.registry.files_created)}")
        print(f"   Total API calls: {len(self.registry.api_calls)}")
        print(f"   Instance folder: {self.instance_path}")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - deactivate instance"""
        self.deactivate()


# ==================== INTERACTIVE INTERFACE ====================


def interactive_constrained_ai():
    """Interactive interface for constrained AI instances"""
    print("\n" + "=" * 70)
    print("🤖 INTERACTIVE CONSTRAINED AI SYSTEM")
    print("=" * 70)
    print("Each AI instance is constrained to its own folder")
    print("All files stay within the instance folder")
    print("Complete audit trail maintained")
    print("=" * 70)

    # Check API key
    if not SystemConfig.DEEPSEEK_API_KEY:
        print("\n⚠️  WARNING: DEEPSEEK_API_KEY not found in environment")
        print("   AI queries will fail without API key")
        print("   Set it with: set DEEPSEEK_API_KEY=your_key_here")
        print("   File creation will still work")

    # Create instance
    print("\nCreating new constrained AI instance...")
    instance = ConstrainedAIInstance()

    print("\n💡 Available commands:")
    print("   create <filename> <content> - Create a file")
    print("   ai <prompt> - Query DeepSeek AI")
    print("   aifile <filename> <prompt> - Create file with AI")
    print("   list - List all files in instance")
    print("   stats - Show instance statistics")
    print("   help - Show this help")
    print("   quit - Deactivate and exit")
    print("=" * 70)

    while True:
        try:
            # Get user input
            user_input = input(f"\n[{instance.alias}]> ").strip()

            if not user_input:
                continue

            # Parse command
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()

            if command == "quit":
                instance.deactivate()
                print("\n👋 Goodbye!")
                break

            elif command == "help":
                print("\n📋 Available commands:")
                print("   create <filename> <content> - Create a file")
                print("   ai <prompt> - Query DeepSeek AI")
                print("   aifile <filename> <prompt> - Create file with AI")
                print("   list - List all files in instance")
                print("   stats - Show instance statistics")
                print("   help - Show this help")
                print("   quit - Deactivate and exit")

            elif command == "create":
                if len(parts) < 2:
                    print("❌ Usage: create <filename> <content>")
                    continue

                # Parse filename and content
                subparts = parts[1].split(maxsplit=1)
                if len(subparts) < 2:
                    print("❌ Usage: create <filename> <content>")
                    continue

                filename, content = subparts
                try:
                    file_path = instance.create_file(filename, content)
                    print(f"✅ File created: {file_path}")
                except ValueError as e:
                    print(f"❌ Error: {e}")

            elif command == "ai":
                if len(parts) < 2:
                    print("❌ Usage: ai <prompt>")
                    continue

                prompt = parts[1]
                result = instance.query_ai(prompt)

                if result["success"]:
                    print(f"\n🤖 AI Response:")
                    print("-" * 40)
                    print(result["response"])
                    print("-" * 40)
                    if "total_tokens" in result:
                        print(f"📊 Tokens used: {result['total_tokens']}")
                else:
                    print(f"❌ AI query failed: {result.get('error', 'Unknown error')}")

            elif command == "aifile":
                if len(parts) < 2:
                    print("❌ Usage: aifile <filename> <prompt>")
                    continue

                # Parse filename and prompt
                subparts = parts[1].split(maxsplit=1)
                if len(subparts) < 2:
                    print("❌ Usage: aifile <filename> <prompt>")
                    continue

                filename, prompt = subparts
                file_path = instance.create_file_from_ai(filename, prompt)

                if file_path:
                    print(f"✅ AI-created file: {file_path}")
                else:
                    print("❌ Failed to create file with AI")

            elif command == "list":
                files = instance.list_files()
                if files:
                    print(f"\n📁 Files in instance ({len(files)} total):")
                    for i, file in enumerate(files, 1):
                        print(f"  {i}. {file['filename']} ({file['hash']})")
                        print(f"     Created: {file['timestamp']}")
                else:
                    print("📁 No files created yet")

            elif command == "stats":
                stats = instance.get_stats()
                print(f"\n📊 Instance Statistics:")
                print(f"  ID: {stats['instance_id']}")
                print(f"  Alias: {stats['alias']}")
                print(f"  Created: {stats['start_time']}")
                print(f"  Last activity: {stats['last_activity']}")
                print(f"  Total files: {stats['total_files']}")
                print(f"  Total API calls: {stats['total_api_calls']}")
                print(f"  Active: {'Yes' if stats['is_active'] else 'No'}")
                print(f"  Path: {stats['instance_path']}")

            else:
                print(f"❌ Unknown command: {command}")
                print("   Type 'help' for available commands")

        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
            instance.deactivate()
            break
        except EOFError:
            print("\n\n👋 End of input")
            instance.deactivate()
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback

            traceback.print_exc()


# ==================== MAIN FUNCTION ====================


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Constrained AI System - Multi-instance AI with folder isolation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Interactive mode
  python constrained_ai_system.py

  # Create instance and run command
  python constrained_ai_system.py --create "test_instance"

  # Test with sample files
  python constrained_ai_system.py --test

  # Show system status
  python constrained_ai_system.py --status
        """,
    )

    parser.add_argument(
        "--interactive", action="store_true", help="Start interactive mode"
    )
    parser.add_argument("--create", type=str, help="Create instance with given alias")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--status", action="store_true", help="Show system status")

    args = parser.parse_args()

    if args.interactive or (not args.create and not args.test and not args.status):
        interactive_constrained_ai()
    elif args.create:
        print(f"\nCreating instance: {args.create}")
        instance = ConstrainedAIInstance(args.create)
        print(f"\n✅ Instance created:")
        print(f"   ID: {instance.instance_id}")
        print(f"   Path: {instance.instance_path}")
        instance.deactivate()
    elif args.test:
        run_tests()
    elif args.status:
        show_system_status()


def run_tests():
    """Run system tests"""
    print("\n" + "=" * 70)
    print("🧪 RUNNING CONSTRAINED AI SYSTEM TESTS")
    print("=" * 70)

    # Test 1: Create instance
    print("\n1. Testing instance creation...")
    instance = ConstrainedAIInstance("Test-Instance-1")
    print("✅ Instance created")

    # Test 2: Create files
    print("\n2. Testing file creation...")
    file1 = instance.create_file("test.txt", "Hello from constrained AI instance")
    print(f"✅ File created: {file1}")

    # Test 3: AI query (if API key available)
    print("\n3. Testing AI query...")
    if SystemConfig.DEEPSEEK_API_KEY:
        result = instance.query_ai("Say hello in a creative way")
        if result["success"]:
            print(f"✅ AI query successful: {len(result['response'])} characters")
        else:
            print(f"⚠️  AI query failed: {result.get('error')}")
    else:
        print("⚠️  Skipping AI test (no API key)")

    # Test 4: Stats
    print("\n4. Testing statistics...")
    stats = instance.get_stats()
    print(
        f"✅ Stats: {stats['total_files']} files, {stats['total_api_calls']} API calls"
    )

    # Test 5: Deactivate
    print("\n5. Testing deactivation...")
    instance.deactivate()
    print("✅ Instance deactivated")

    print("\n" + "=" * 70)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 70)


def show_system_status():
    """Show system status"""
    print("\n" + "=" * 70)
    print("📊 CONSTRAINED AI SYSTEM STATUS")
    print("=" * 70)

    # Check instances directory
    instances_path = Path(SystemConfig.INSTANCES_ROOT)
    if instances_path.exists():
        instances = list(instances_path.iterdir())
        print(f"\n📁 Instances directory: {instances_path}")
        print(f"   Total instances: {len(instances)}")

        # Count active instances
        active_count = 0
        for instance_dir in instances:
            registry_file = instance_dir / SystemConfig.REGISTRY_FILE
            if registry_file.exists():
                try:
                    with open(registry_file, "r") as f:
                        data = json.load(f)
                        if data.get("is_active", False):
                            active_count += 1
                except:
                    pass

        print(f"   Active instances: {active_count}")
    else:
        print(f"\n📁 Instances directory not found: {instances_path}")

    # Check API key
    print(f"\n🔑 DeepSeek API:")
    print(f"   Key configured: {'Yes' if SystemConfig.DEEPSEEK_API_KEY else 'No'}")

    # System configuration
    print(f"\n⚙️  System Configuration:")
    print(
        f"   Σ_LORA Constraints: {'Enabled' if SystemConfig.ENABLE_CONSTRAINTS else 'Disabled'}"
    )
    print(f"   Max instances: {SystemConfig.MAX_INSTANCES}")
    print(f"   Max files per instance: {SystemConfig.MAX_FILES_PER_INSTANCE}")
    print(f"   Auto-cleanup days: {SystemConfig.CLEANUP_DAYS}")

    print("\n" + "=" * 70)
    print("✅ SYSTEM STATUS REPORT COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
