"""
REPO_ACTIVATION_SYSTEM.py
=========================

REPO-WIDE ACTIVATION SYSTEM
Any change to repository → Daemon activates → Chat pops up → Collaboration required

ARCHITECTURE:
- File system watcher monitors entire repo
- Any change triggers daemon activation
- Chat interface opens automatically
- Daemon knows who made change (human vs IDE AI)
- Collaboration enforced via constraint system

FEATURES:
1. Real-time file monitoring
2. Automatic daemon activation
3. Intelligent change analysis
4. Multi-client chat coordination
5. Collaboration enforcement
"""

import asyncio
import json
import logging
import os
import signal
import sys
import threading
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import requests
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [ACTIVATION] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


# ==================== ACTIVATION TYPES ====================


class ActivationType(Enum):
    """Types of repository activations"""

    FILE_CREATED = "file_created"
    FILE_MODIFIED = "file_modified"
    FILE_DELETED = "file_deleted"
    FILE_RENAMED = "file_renamed"
    DIRECTORY_CREATED = "directory_created"
    DIRECTORY_DELETED = "directory_deleted"
    GIT_COMMIT = "git_commit"
    GIT_PUSH = "git_push"
    MANUAL_TRIGGER = "manual_trigger"
    IDE_AI_CHANGE = "ide_ai_change"
    HUMAN_CHANGE = "human_change"


class ChangeSource(Enum):
    """Source of the change"""

    HUMAN = "human"  # Direct human edit
    IDE_AI = "ide_ai"  # IDE AI suggestion/autocomplete
    DAEMON = "daemon"  # Daemon-generated change
    SCRIPT = "script"  # Script/automation
    UNKNOWN = "unknown"  # Unknown source


# ==================== CHANGE ANALYSIS ====================


class ChangeAnalysis:
    """Analyze repository changes"""

    def __init__(self):
        self.change_history = []
        self.lock = threading.Lock()

    def analyze_change(
        self, file_path: str, change_type: ActivationType, source: ChangeSource
    ) -> Dict:
        """Analyze a change and return intelligence"""

        path = Path(file_path)
        timestamp = datetime.now().isoformat()

        # Basic analysis
        analysis = {
            "timestamp": timestamp,
            "file_path": str(path),
            "file_name": path.name,
            "file_extension": path.suffix.lower(),
            "change_type": change_type.value,
            "source": source.value,
            "is_python": path.suffix.lower() == ".py",
            "is_config": path.suffix.lower() in [".json", ".yaml", ".yml", ".toml"],
            "is_documentation": path.suffix.lower() in [".md", ".txt", ".rst"],
            "file_size": path.stat().st_size if path.exists() else 0,
            "in_git": self._is_in_git(path),
        }

        # Add content analysis for text files
        if (
            analysis["is_python"]
            or analysis["is_config"]
            or analysis["is_documentation"]
        ):
            if path.exists():
                try:
                    content = path.read_text(encoding="utf-8", errors="ignore")
                    analysis["line_count"] = len(content.splitlines())
                    analysis["char_count"] = len(content)

                    # Python-specific analysis
                    if analysis["is_python"]:
                        analysis["imports"] = self._extract_python_imports(content)
                        analysis["function_count"] = content.count("def ")
                        analysis["class_count"] = content.count("class ")
                except:
                    analysis["line_count"] = 0
                    analysis["char_count"] = 0

        # Determine change significance
        analysis["significance"] = self._calculate_significance(analysis)

        # Store in history
        with self.lock:
            self.change_history.append(analysis)
            # Keep only last 1000 changes
            if len(self.change_history) > 1000:
                self.change_history = self.change_history[-1000:]

        return analysis

    def _is_in_git(self, path: Path) -> bool:
        """Check if file is in git repository"""
        try:
            git_dir = path
            while git_dir != git_dir.parent:
                if (git_dir / ".git").exists():
                    return True
                git_dir = git_dir.parent
            return False
        except:
            return False

    def _extract_python_imports(self, content: str) -> List[str]:
        """Extract Python imports from content"""
        imports = []
        lines = content.splitlines()

        for line in lines:
            line = line.strip()
            if line.startswith("import ") or line.startswith("from "):
                imports.append(line)

        return imports

    def _calculate_significance(self, analysis: Dict) -> str:
        """Calculate change significance"""
        score = 0

        # File type weights
        if analysis["is_python"]:
            score += 3
        if analysis["is_config"]:
            score += 2
        if analysis.get("function_count", 0) > 0:
            score += 2
        if analysis.get("class_count", 0) > 0:
            score += 2

        # Change type weights
        change_type = analysis["change_type"]
        if change_type == "file_created":
            score += 3
        elif change_type == "file_deleted":
            score += 4
        elif change_type == "file_modified":
            score += 1

        # Source weights
        source = analysis["source"]
        if source == "ide_ai":
            score += 2  # IDE AI changes need more attention
        elif source == "daemon":
            score += 3  # Daemon changes are significant

        # Determine significance level
        if score >= 5:
            return "high"
        elif score >= 3:
            return "medium"
        else:
            return "low"


# ==================== FILE SYSTEM WATCHER ====================


class RepoWatcher(FileSystemEventHandler):
    """Watch for repository changes"""

    def __init__(self, activation_system):
        self.activation_system = activation_system
        self.ignored_patterns = {
            "__pycache__",
            ".git",
            ".pytest_cache",
            "node_modules",
            ".venv",
            "venv",
            ".env",
        }
        self.ignored_extensions = {".pyc", ".pyo", ".pyd", ".so", ".dll"}

    def on_created(self, event):
        """File/directory created"""
        if self._should_ignore(event.src_path):
            return

        change_type = (
            ActivationType.DIRECTORY_CREATED
            if event.is_directory
            else ActivationType.FILE_CREATED
        )

        self.activation_system.trigger_activation(
            file_path=event.src_path,
            change_type=change_type,
            source=ChangeSource.UNKNOWN,
        )

    def on_modified(self, event):
        """File/directory modified"""
        if self._should_ignore(event.src_path):
            return

        if not event.is_directory:
            self.activation_system.trigger_activation(
                file_path=event.src_path,
                change_type=ActivationType.FILE_MODIFIED,
                source=ChangeSource.UNKNOWN,
            )

    def on_deleted(self, event):
        """File/directory deleted"""
        if self._should_ignore(event.src_path):
            return

        change_type = (
            ActivationType.DIRECTORY_DELETED
            if event.is_directory
            else ActivationType.FILE_DELETED
        )

        self.activation_system.trigger_activation(
            file_path=event.src_path,
            change_type=change_type,
            source=ChangeSource.UNKNOWN,
        )

    def on_moved(self, event):
        """File/directory renamed/moved"""
        if self._should_ignore(event.src_path) or self._should_ignore(event.dest_path):
            return

        self.activation_system.trigger_activation(
            file_path=event.dest_path,
            change_type=ActivationType.FILE_RENAMED,
            source=ChangeSource.UNKNOWN,
        )

    def _should_ignore(self, path: str) -> bool:
        """Check if path should be ignored"""
        path_obj = Path(path)

        # Check ignored directories
        for part in path_obj.parts:
            if part in self.ignored_patterns:
                return True

        # Check ignored extensions
        if path_obj.suffix.lower() in self.ignored_extensions:
            return True

        # Check if it's a hidden file (starts with .)
        if path_obj.name.startswith("."):
            return True

        return False


# ==================== ACTIVATION SYSTEM ====================


class RepoActivationSystem:
    """
    Repository Activation System

    Monitors entire repo and triggers daemon + chat on any change.
    Enforces collaboration between human and IDE AI.
    """

    def __init__(self, daemon_url: str = "http://localhost:8080"):
        self.daemon_url = daemon_url
        self.running = False
        self.observer = None
        self.analysis = ChangeAnalysis()
        self.activation_lock = threading.Lock()
        self.last_activation_time = 0
        self.activation_cooldown = 2.0  # seconds

        # Activation history
        self.activations = []
        self.max_activations = 100

        # Collaboration state
        self.active_collaborations = {}
        self.collaboration_timeout = 300  # 5 minutes

        logger.info(f"Repo Activation System initialized (Daemon: {daemon_url})")

    def start(self):
        """Start the activation system"""
        if self.running:
            logger.warning("Activation system already running")
            return False

        try:
            # Start file system watcher
            self.observer = Observer()
            event_handler = RepoWatcher(self)

            # Watch the entire project root
            self.observer.schedule(event_handler, str(project_root), recursive=True)

            self.observer.start()
            self.running = True

            logger.info(f"Started watching repository: {project_root}")
            logger.info(
                f"Ignoring patterns: {', '.join(RepoWatcher(None).ignored_patterns)}"
            )

            # Start collaboration monitor
            self._start_collaboration_monitor()

            return True

        except Exception as e:
            logger.error(f"Failed to start activation system: {e}")
            return False

    def stop(self):
        """Stop the activation system"""
        if not self.running:
            return

        self.running = False

        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None

        logger.info("Activation system stopped")

    def trigger_activation(
        self, file_path: str, change_type: ActivationType, source: ChangeSource
    ):
        """
        Trigger activation for a repository change

        This is the core method that:
        1. Analyzes the change
        2. Activates the daemon
        3. Opens chat for collaboration
        4. Enforces correspondence between human and IDE AI
        """
        # Cooldown check to prevent rapid activations
        current_time = time.time()
        if current_time - self.last_activation_time < self.activation_cooldown:
            return

        with self.activation_lock:
            self.last_activation_time = current_time

            # Analyze the change
            analysis = self.analysis.analyze_change(file_path, change_type, source)

            # Determine source if unknown
            if source == ChangeSource.UNKNOWN:
                source = self._detect_change_source(analysis)
                analysis["source"] = source.value

            logger.info(
                f"Activation triggered: {analysis['file_name']} "
                f"({change_type.value}) by {source.value}"
            )

            # Store activation
            activation = {
                "timestamp": datetime.now().isoformat(),
                "analysis": analysis,
                "triggered_daemon": False,
                "chat_opened": False,
                "collaboration_started": False,
            }

            self.activations.append(activation)
            if len(self.activations) > self.max_activations:
                self.activations = self.activations[-self.max_activations :]

            # Activate daemon
            daemon_activated = self._activate_daemon(analysis)
            activation["triggered_daemon"] = daemon_activated

            # Open chat for collaboration
            if daemon_activated:
                chat_opened = self._open_collaboration_chat(analysis)
                activation["chat_opened"] = chat_opened

                if chat_opened:
                    collaboration_id = self._start_collaboration(analysis)
                    activation["collaboration_started"] = bool(collaboration_id)
                    activation["collaboration_id"] = collaboration_id

            return activation

    def _detect_change_source(self, analysis: Dict) -> ChangeSource:
        """Detect the source of a change"""
        file_path = analysis["file_path"]

        # Check if it's a daemon-generated file
        if "daemon" in file_path.lower() or "generated" in file_path.lower():
            return ChangeSource.DAEMON

        # Check if it's a script file
        if "script" in file_path.lower() or "automation" in file_path.lower():
            return ChangeSource.SCRIPT

        # Check file content for IDE AI patterns
        if analysis.get("is_python", False):
            try:
                content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
                # IDE AI often adds specific comments or patterns
                if any(
                    pattern in content
                    for pattern in [
                        "# Generated by AI",
                        "# AI suggestion",
                        "# IDE AI",
                        "# autocomplete",
                    ]
                ):
                    return ChangeSource.IDE_AI
            except:
                pass

        # Default to human (most changes are human)
        return ChangeSource.HUMAN

    def _activate_daemon(self, analysis: Dict) -> bool:
        """Activate the daemon with change analysis"""
        try:
            # Prepare query for daemon
            query = self._build_daemon_query(analysis)

            # Send to daemon
            response = requests.post(f"{self.daemon_url}/query", json=query, timeout=10)

            if response.status_code == 200:
                result = response.json()
                logger.info(
                    f"Daemon activated successfully: {result.get('model_used', 'unknown')}"
                )

                # Store daemon response
                analysis["daemon_response"] = result
                return True
            else:
                logger.warning(f"Daemon activation failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Failed to activate daemon: {e}")
            return False

    def _build_daemon_query(self, analysis: Dict) -> Dict:
        """Build query for daemon based on change analysis"""

        # Determine query text based on change
        file_name = analysis["file_name"]
        change_type = analysis["change_type"]
        source = analysis["source"]

        if change_type == "file_created":
            action = f"created file {file_name}"
        elif change_type == "file_modified":
            action = f"modified file {file_name}"
        elif change_type == "file_deleted":
            action = f"deleted file {file_name}"
        elif change_type == "file_renamed":
            action = f"renamed to {file_name}"
        else:
            action = f"changed {file_name}"

        query_text = (
            f"Repository change detected: {source} {action}. "
            f"File type: {analysis.get('file_extension', 'unknown')}. "
            f"Significance: {analysis.get('significance', 'unknown')}. "
            f"Please analyze this change and prepare for collaboration."
        )

        return {
            "text": query_text,
            "client_type": "activation_system",
            "context": {
                "change_analysis": analysis,
                "action_required": "collaboration",
                "urgency": "high"
                if analysis.get("significance") == "high"
                else "medium",
            },
            "require_constraints": True,
            "max_length": 1024,
            "temperature": 0.7,
        }

    def _open_collaboration_chat(self, analysis: Dict) -> bool:
        """Open chat interface for collaboration"""
        try:
            # This would open a chat interface in the IDE
            # For now, we log and simulate

            file_name = analysis["file_name"]
            source = analysis["source"]
            significance = analysis.get("significance", "unknown")

            chat_message = (
                f"🔔 REPOSITORY ACTIVATION 🔔\n\n"
                f"File: {file_name}\n"
                f"Change: {analysis['change_type']}\n"
                f"Source: {source}\n"
                f"Significance: {significance}\n\n"
                f"Daemon activated. Collaboration required.\n"
                f"Please respond to coordinate next steps."
            )

            logger.info(f"Chat opened: {chat_message}")

            # In a real implementation, this would:
            # 1. Open chat window in IDE
            # 2. Display the message
            # 3. Wait for human response
            # 4. Forward to daemon

            return True

        except Exception as e:
            logger.error(f"Failed to open chat: {e}")
            return False

    def _start_collaboration(self, analysis: Dict) -> str:
        """Start a collaboration session"""
        collaboration_id = (
            f"collab_{int(time.time())}_{analysis['file_name'].replace('.', '_')}"
        )

        collaboration = {
            "id": collaboration_id,
            "start_time": datetime.now().isoformat(),
            "analysis": analysis,
            "participants": [analysis["source"]],
            "messages": [],
            "status": "active",
            "requires_human": analysis["source"] != ChangeSource.HUMAN.value,
            "requires_ide_ai": analysis["source"] != ChangeSource.IDE_AI.value,
            "resolved": False,
        }

        # Add initial message from activation system
        initial_message = {
            "timestamp": datetime.now().isoformat(),
            "sender": "activation_system",
            "text": f"Collaboration started for change to {analysis['file_name']}. Source: {analysis['source']}. Significance: {analysis.get('significance', 'unknown')}.",
            "type": "system",
        }

        collaboration["messages"].append(initial_message)

        # Store collaboration
        self.active_collaborations[collaboration_id] = collaboration

        logger.info(f"Collaboration started: {collaboration_id}")

        # Send to daemon for coordination
        self._notify_daemon_collaboration(collaboration)

        return collaboration_id

    def _notify_daemon_collaboration(self, collaboration: Dict):
        """Notify daemon about collaboration session"""
        try:
            query = {
                "text": f"Collaboration session {collaboration['id']} started. Change: {collaboration['analysis']['change_type']} on {collaboration['analysis']['file_name']}. Please coordinate between {', '.join(collaboration['participants'])}.",
                "client_type": "collaboration_coordinator",
                "context": {
                    "collaboration": collaboration,
                    "action_required": "coordinate_participants",
                    "participants": collaboration["participants"],
                },
                "require_constraints": True,
                "max_length": 512,
                "temperature": 0.7,
            }

            response = requests.post(f"{self.daemon_url}/query", json=query, timeout=10)

            if response.status_code == 200:
                result = response.json()
                collaboration["daemon_coordination"] = result
                logger.info(f"Daemon notified of collaboration: {collaboration['id']}")
            else:
                logger.warning(f"Failed to notify daemon: {response.status_code}")

        except Exception as e:
            logger.error(f"Failed to notify daemon of collaboration: {e}")

    def _start_collaboration_monitor(self):
        """Start monitoring active collaborations"""

        def monitor():
            while self.running:
                try:
                    current_time = time.time()
                    expired_collaborations = []

                    # Check for expired collaborations
                    for collab_id, collaboration in list(
                        self.active_collaborations.items()
                    ):
                        start_time = datetime.fromisoformat(
                            collaboration["start_time"]
                        ).timestamp()
                        if current_time - start_time > self.collaboration_timeout:
                            expired_collaborations.append(collab_id)
                            logger.warning(f"Collaboration expired: {collab_id}")

                    # Clean up expired collaborations
                    for collab_id in expired_collaborations:
                        del self.active_collaborations[collab_id]

                    # Sleep for 30 seconds
                    time.sleep(30)

                except Exception as e:
                    logger.error(f"Collaboration monitor error: {e}")
                    time.sleep(10)

        # Start monitor thread
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        logger.info("Collaboration monitor started")

    def add_collaboration_message(self, collaboration_id: str, sender: str, text: str):
        """Add a message to a collaboration session"""
        if collaboration_id not in self.active_collaborations:
            logger.warning(f"Collaboration not found: {collaboration_id}")
            return False

        collaboration = self.active_collaborations[collaboration_id]

        message = {
            "timestamp": datetime.now().isoformat(),
            "sender": sender,
            "text": text,
            "type": "participant",
        }

        collaboration["messages"].append(message)

        # Update participants if new
        if sender not in collaboration["participants"]:
            collaboration["participants"].append(sender)

        logger.info(f"Message added to {collaboration_id} from {sender}")

        # Forward to daemon for processing
        self._forward_message_to_daemon(collaboration_id, message)

        return True

    def _forward_message_to_daemon(self, collaboration_id: str, message: Dict):
        """Forward collaboration message to daemon"""
        try:
            collaboration = self.active_collaborations[collaboration_id]

            query = {
                "text": f"Collaboration {collaboration_id} message from {message['sender']}: {message['text']}",
                "client_type": "collaboration_participant",
                "context": {
                    "collaboration_id": collaboration_id,
                    "message": message,
                    "analysis": collaboration["analysis"],
                    "current_participants": collaboration["participants"],
                },
                "require_constraints": True,
                "max_length": 1024,
                "temperature": 0.7,
            }

            response = requests.post(f"{self.daemon_url}/query", json=query, timeout=10)

            if response.status_code == 200:
                result = response.json()

                # Add daemon response as a message
                daemon_message = {
                    "timestamp": datetime.now().isoformat(),
                    "sender": "daemon",
                    "text": result["response"],
                    "type": "daemon_response",
                    "christ_score": result["christ_score"],
                }

                collaboration["messages"].append(daemon_message)
                logger.info(f"Daemon responded to collaboration {collaboration_id}")

                # Check if collaboration is resolved
                if self._check_collaboration_resolved(collaboration, result):
                    collaboration["resolved"] = True
                    collaboration["resolved_time"] = datetime.now().isoformat()
                    logger.info(f"Collaboration resolved: {collaboration_id}")

            else:
                logger.warning(f"Daemon response failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Failed to forward message to daemon: {e}")

    def _check_collaboration_resolved(
        self, collaboration: Dict, daemon_response: Dict
    ) -> bool:
        """Check if collaboration is resolved based on daemon response"""
        # Check Christ Score - high score indicates resolution
        if daemon_response.get("christ_score", 0) >= 0.95:
            return True

        # Check response content for resolution indicators
        response_text = daemon_response.get("response", "").lower()
        resolution_indicators = [
            "resolved",
            "completed",
            "agreed",
            "consensus",
            "approved",
            "finalized",
            "done",
            "finished",
        ]

        if any(indicator in response_text for indicator in resolution_indicators):
            return True

        # Check if all required participants have responded
        messages = collaboration["messages"]
        participants = set(collaboration["participants"])
        responding_participants = set(
            msg["sender"] for msg in messages if msg["type"] == "participant"
        )

        # If human was required and has responded
        if collaboration["requires_human"] and "human" in responding_participants:
            return True

        # If IDE AI was required and has responded
        if collaboration["requires_ide_ai"] and "ide_ai" in responding_participants:
            return True

        return False

    def get_collaboration_status(self, collaboration_id: str) -> Optional[Dict]:
        """Get status of a collaboration session"""
        if collaboration_id not in self.active_collaborations:
            return None

        collaboration = self.active_collaborations[collaboration_id]

        return {
            "id": collaboration_id,
            "status": collaboration["status"],
            "resolved": collaboration["resolved"],
            "participants": collaboration["participants"],
            "message_count": len(collaboration["messages"]),
            "start_time": collaboration["start_time"],
            "requires_human": collaboration["requires_human"],
            "requires_ide_ai": collaboration["requires_ide_ai"],
            "analysis_summary": {
                "file": collaboration["analysis"]["file_name"],
                "change_type": collaboration["analysis"]["change_type"],
                "source": collaboration["analysis"]["source"],
                "significance": collaboration["analysis"].get(
                    "significance", "unknown"
                ),
            },
        }

    def resolve_collaboration(self, collaboration_id: str, resolution: str):
        """Manually resolve a collaboration session"""
        if collaboration_id not in self.active_collaborations:
            logger.warning(f"Collaboration not found: {collaboration_id}")
            return False

        collaboration = self.active_collaborations[collaboration_id]
        collaboration["resolved"] = True
        collaboration["resolved_time"] = datetime.now().isoformat()
        collaboration["manual_resolution"] = resolution
        collaboration["status"] = "manually_resolved"

        # Add resolution message
        resolution_message = {
            "timestamp": datetime.now().isoformat(),
            "sender": "system",
            "text": f"Collaboration manually resolved: {resolution}",
            "type": "resolution",
        }

        collaboration["messages"].append(resolution_message)

        logger.info(f"Collaboration manually resolved: {collaboration_id}")

        # Notify daemon
        self._notify_daemon_resolution(collaboration_id, resolution)

        return True

    def _notify_daemon_resolution(self, collaboration_id: str, resolution: str):
        """Notify daemon of collaboration resolution"""
        try:
            query = {
                "text": f"Collaboration {collaboration_id} resolved: {resolution}",
                "client_type": "collaboration_resolution",
                "context": {
                    "collaboration_id": collaboration_id,
                    "resolution": resolution,
                    "action_required": "update_knowledge",
                },
                "require_constraints": True,
                "max_length": 512,
                "temperature": 0.7,
            }

            response = requests.post(f"{self.daemon_url}/query", json=query, timeout=10)

            if response.status_code == 200:
                logger.info(f"Daemon notified of resolution: {collaboration_id}")
            else:
                logger.warning(
                    f"Failed to notify daemon of resolution: {response.status_code}"
                )

        except Exception as e:
            logger.error(f"Failed to notify daemon of resolution: {e}")

    def get_recent_activations(self, limit: int = 20) -> List[Dict]:
        """Get recent activations"""
        return self.activations[-limit:] if self.activations else []

    def get_active_collaborations(self) -> List[Dict]:
        """Get all active collaborations"""
        return [
            {
                "id": collab_id,
                "start_time": collab["start_time"],
                "file": collab["analysis"]["file_name"],
                "source": collab["analysis"]["source"],
                "participants": collab["participants"],
                "message_count": len(collab["messages"]),
                "resolved": collab["resolved"],
            }
            for collab_id, collab in self.active_collaborations.items()
        ]


# ==================== MAIN ENTRY POINT ====================


def main():
    """Main entry point for repo activation system"""
    print("=" * 70)
    print("REPOSITORY ACTIVATION SYSTEM")
    print("=" * 70)
    print("Any change to repository → Daemon activates → Chat pops up")
    print("Collaboration enforced between human and IDE AI")
    print("=" * 70)

    # Create activation system
    activation_system = RepoActivationSystem()

    # Start the system
    if activation_system.start():
        print("✅ Activation system started")
        print(f"   Watching: {project_root}")
        print(f"   Daemon URL: {activation_system.daemon_url}")
        print("   Press Ctrl+C to stop")
        print("=" * 70)

        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping activation system...")
            activation_system.stop()
            print("✅ Activation system stopped")
    else:
        print("❌ Failed to start activation system")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
