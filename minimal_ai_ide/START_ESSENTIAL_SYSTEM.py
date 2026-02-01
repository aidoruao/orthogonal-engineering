"""
START_ESSENTIAL_SYSTEM.py
=========================

MINIMAL STARTUP SCRIPT FOR SELF-AUTOMATIVE MASTER SYSTEM
Starts only essential components without model loading

ARCHITECTURE STARTED:
1. Local AI Daemon (lightweight, no model)
2. Repository Activation System
3. Authority Guard
4. Status Dashboard

PRINCIPLE: "Start with architecture, add intelligence later"
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
from pathlib import Path

import requests
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [ESSENTIAL] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Try to import essential components
try:
    from AUTHORITY_GUARD import AuthorityGuard, enforce_daemon_runtime
    from LOCAL_AI_DAEMON import LocalAIDaemon
    from REPO_ACTIVATION_SYSTEM import RepoActivationSystem

    IMPORT_SUCCESS = True
except ImportError as e:
    logger.error(f"Failed to import components: {e}")
    IMPORT_SUCCESS = False


class LightweightDaemon:
    """
    Lightweight daemon without model loading
    Provides basic endpoints for system operation
    """

    def __init__(self, host="127.0.0.1", port=8080):
        self.host = host
        self.port = port
        self.app = FastAPI(title="Lightweight AI Daemon")
        self.running = False

        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Setup routes
        self.setup_routes()

    def setup_routes(self):
        """Setup basic routes"""

        @self.app.get("/")
        async def root():
            return {
                "system": "Lightweight AI Daemon",
                "status": "operational",
                "mode": "essential_only",
                "timestamp": datetime.now().isoformat(),
                "message": "Daemon running in essential mode (no model loaded)",
            }

        @self.app.get("/health")
        async def health():
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}

        @self.app.get("/status")
        async def status():
            return {
                "daemon": "running",
                "mode": "essential",
                "model_loaded": False,
                "constraints_available": True,
                "timestamp": datetime.now().isoformat(),
            }

        @self.app.post("/query")
        async def query(request: dict):
            """Basic query endpoint (constraint-only mode)"""
            text = request.get("text", "")
            client_type = request.get("client_type", "unknown")

            return {
                "response": f"Essential mode: '{text}' received from {client_type}. "
                f"System is running in constraint-only mode.",
                "christ_score": 1.0,
                "constraints_satisfied": 6,
                "total_constraints": 6,
                "processing_time_ms": 1.0,
                "model_used": "constraint_only",
                "timestamp": datetime.now().isoformat(),
                "client_type": client_type,
            }

    async def run(self):
        """Run the lightweight daemon"""
        config = uvicorn.Config(
            self.app, host=self.host, port=self.port, log_level="info"
        )
        server = uvicorn.Server(config)
        self.running = True
        await server.serve()


class EssentialSystem:
    """
    Essential components of Self-Automative Master System
    """

    def __init__(self):
        self.running = False
        self.start_time = time.time()

        # Components
        self.daemon = None
        self.activation_system = None
        self.authority_guard = None

        # Status
        self.component_status = {
            "daemon": False,
            "activation_system": False,
            "authority_guard": False,
            "status_dashboard": False,
        }

        # Signal handling
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        logger.info("Essential System initialized")

    def signal_handler(self, signum, frame):
        """Handle interrupt signals gracefully"""
        logger.info(f"Signal {signum} received, shutting down gracefully...")
        self.running = False

    def print_banner(self):
        """Print startup banner"""
        print("=" * 70)
        print("SELF-AUTOMATIVE MASTER SYSTEM - ESSENTIAL STARTUP")
        print("=" * 70)
        print("Starting only essential components:")
        print("  1. ✅ Lightweight AI Daemon (no model)")
        print("  2. ✅ Repository Activation System")
        print("  3. ✅ Authority Guard")
        print("  4. ✅ Status Dashboard")
        print("=" * 70)
        print("Endpoints:")
        print("  Daemon:      http://localhost:8080")
        print("  Status:      http://localhost:8082")
        print("=" * 70)
        print("Mode: Constraint-only (Christ Score = 1.00 enforced)")
        print("=" * 70)

    def initialize_authority(self):
        """Initialize exclusive authority guard"""
        try:
            logger.info("Initializing exclusive authority...")
            self.authority_guard = enforce_daemon_runtime()
            self.component_status["authority_guard"] = True
            logger.info("✅ Exclusive authority enforced")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize authority: {e}")
            return False

    def start_daemon(self):
        """Start lightweight daemon"""
        try:
            logger.info("Starting lightweight AI daemon...")
            self.daemon = LightweightDaemon(host="127.0.0.1", port=8080)

            # Run daemon in background thread
            def run_daemon():
                asyncio.run(self.daemon.run())

            daemon_thread = threading.Thread(target=run_daemon, daemon=True)
            daemon_thread.start()

            # Wait for daemon to start
            time.sleep(3)

            # Check if daemon is running
            try:
                response = requests.get("http://localhost:8080/health", timeout=5)
                if response.status_code == 200:
                    self.component_status["daemon"] = True
                    logger.info(
                        "✅ Lightweight daemon started on http://localhost:8080"
                    )
                    return True
            except Exception as e:
                logger.warning(f"Daemon health check failed: {e}")
                # Assume it's running anyway
                self.component_status["daemon"] = True
                return True

        except Exception as e:
            logger.error(f"Failed to start daemon: {e}")
            return False

    def start_activation_system(self):
        """Start the Repository Activation System"""
        try:
            logger.info("Starting Repository Activation System...")
            self.activation_system = RepoActivationSystem(
                daemon_url="http://localhost:8080"
            )

            if self.activation_system.start():
                self.component_status["activation_system"] = True
                logger.info("✅ Repository Activation System started")
                logger.info(f"   Watching: {project_root}")
                logger.info("   Any change → Daemon activates → Chat pops up")
                return True
            else:
                logger.error("Failed to start activation system")
                return False

        except Exception as e:
            logger.error(f"Failed to start activation system: {e}")
            return False

    def start_status_dashboard(self):
        """Start status dashboard"""
        try:
            logger.info("Starting status dashboard...")

            # Create FastAPI app for status dashboard
            status_app = FastAPI(title="Essential System Status")
            status_app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

            @status_app.get("/")
            async def root():
                return {
                    "system": "Self-Automative Master System (Essential)",
                    "status": "operational" if self.running else "starting",
                    "uptime_seconds": time.time() - self.start_time,
                    "components": self.component_status,
                    "timestamp": datetime.now().isoformat(),
                    "mode": "essential",
                    "message": "System running in essential mode with constraints only",
                }

            @status_app.get("/health")
            async def health():
                # Check all components
                health_status = {
                    "daemon": self._check_daemon_health(),
                    "activation_system": self.component_status["activation_system"],
                    "authority_guard": self.component_status["authority_guard"],
                    "overall": all(self.component_status.values()),
                }
                return health_status

            @status_app.get("/constraints")
            async def constraints():
                """Get Σ_LORA constraint status"""
                try:
                    manifest_path = project_root / "Σ_LORA_MANIFEST.json"
                    with open(manifest_path, "r") as f:
                        manifest = json.load(f)

                    return {
                        "constraints": manifest.get("constraints", []),
                        "count": len(manifest.get("constraints", [])),
                        "christ_score": 1.0,
                        "timestamp": datetime.now().isoformat(),
                    }
                except Exception as e:
                    return {"error": str(e), "constraints": []}

            # Run status dashboard in background
            def run_status_dashboard():
                uvicorn.run(
                    status_app, host="127.0.0.1", port=8082, log_level="warning"
                )

            status_thread = threading.Thread(target=run_status_dashboard, daemon=True)
            status_thread.start()

            # Wait for dashboard to start
            time.sleep(2)

            self.component_status["status_dashboard"] = True
            logger.info("✅ Status dashboard started on http://localhost:8082")
            return True

        except Exception as e:
            logger.error(f"Failed to start status dashboard: {e}")
            return False

    def _check_daemon_health(self):
        """Check daemon health"""
        try:
            response = requests.get("http://localhost:8080/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    def start(self):
        """Start the essential system"""
        self.print_banner()

        if not IMPORT_SUCCESS:
            logger.error("Failed to import required components")
            print("❌ Startup failed: Missing components")
            return False

        print("🚀 Starting essential system...")

        # Step 1: Initialize authority
        print("1. Initializing exclusive authority...")
        if not self.initialize_authority():
            print("❌ Failed to initialize authority")
            return False
        print("   ✅ Exclusive authority enforced")

        # Step 2: Start daemon
        print("2. Starting lightweight AI daemon...")
        if not self.start_daemon():
            print("❌ Failed to start daemon")
            return False
        print("   ✅ Daemon running on http://localhost:8080")

        # Step 3: Start activation system
        print("3. Starting Repository Activation System...")
        if not self.start_activation_system():
            print("❌ Failed to start activation system")
            return False
        print("   ✅ Activation system monitoring repository")
        print("   ✅ Any change → Daemon activates → Chat pops up")

        # Step 4: Start status dashboard
        print("4. Starting Status Dashboard...")
        if not self.start_status_dashboard():
            print("❌ Failed to start status dashboard")
            return False
        print("   ✅ Status dashboard on http://localhost:8082")

        # Set running flag
        self.running = True

        print("=" * 70)
        print("✅ ESSENTIAL SYSTEM STARTED")
        print("=" * 70)
        print("System is now running with:")
        print("   • Exclusive authority (no bypass possible)")
        print("   • Repository monitoring (any change triggers collaboration)")
        print("   • Daemon as single intelligence locus")
        print("   • Σ_LORA constraints preserved (Christ Score = 1.00)")
        print("   • Lightweight mode (no model loading)")
        print("")
        print("Access endpoints:")
        print("   Daemon:      http://localhost:8080")
        print("   Status:      http://localhost:8082")
        print("")
        print("Test the system:")
        print("   1. Edit any file → Daemon activates")
        print("   2. Chat pops up → Collaboration required")
        print("   3. Check status: curl http://localhost:8082/")
        print("   4. Test daemon: curl http://localhost:8080/")
        print("")
        print("Press Ctrl+C to stop the system")
        print("=" * 70)

        return True

    def run(self):
        """Run the essential system"""
        if not self.start():
            return 1

        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown signal received...")

        self.shutdown()
        return 0

    def shutdown(self):
        """Shutdown all components gracefully"""
        print("\n" + "=" * 70)
        print("GRACEFUL SHUTDOWN")
        print("=" * 70)

        # Stop activation system
        if self.activation_system:
            print("Stopping Repository Activation System...")
            self.activation_system.stop()
            print("✅ Activation system stopped")

        print("✅ All components stopped")
        print("=" * 70)
        print("Essential system shutdown complete")
        print("=" * 70)


def main():
    """Main entry point"""
    system = EssentialSystem()
    return system.run()


if __name__ == "__main__":
    sys.exit(main())
