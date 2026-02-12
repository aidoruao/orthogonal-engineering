"""
COMPLETE_INTEGRATION.py
========================

COMPLETE INTEGRATION SYSTEM FOR POLYMATHIC AI IDE
Ties together all components into a single, unified system

ARCHITECTURE:
1. Local AI Daemon (authority)
2. Repository Activation System (monitoring)
3. Authority Guard (exclusive access)
4. IDE AI Client Interface
5. Human Collaboration Interface

PRINCIPLE: "All intelligence paths factor through the daemon"
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
from typing import Dict, List, Optional

import requests
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [INTEGRATION] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Try to import all components
try:
    from AUTHORITY_GUARD import AuthorityGuard, enforce_daemon_runtime
    from LOCAL_AI_DAEMON import LocalAIDaemon, QueryRequest, QueryResponse
    from REPO_ACTIVATION_SYSTEM import (
        ActivationType,
        ChangeSource,
        RepoActivationSystem,
    )

    IMPORT_SUCCESS = True
except ImportError as e:
    logger.error(f"Failed to import components: {e}")
    IMPORT_SUCCESS = False


# ==================== INTEGRATION MODELS ====================


class IntegrationStatus(BaseModel):
    """Integration system status"""

    daemon_running: bool
    activation_system_running: bool
    authority_enforced: bool
    total_queries: int
    total_activations: int
    active_collaborations: int
    christ_score: float
    uptime_seconds: float


class CollaborationRequest(BaseModel):
    """Request to start collaboration"""

    file_path: str
    change_type: str
    source: str
    description: Optional[str] = None


class IDEQuery(BaseModel):
    """Query from IDE AI"""

    text: str
    context: Optional[Dict] = None
    file_context: Optional[str] = None
    line_number: Optional[int] = None


# ==================== COMPLETE INTEGRATION SYSTEM ====================


class CompleteIntegrationSystem:
    """
    Complete Integration System for Polymathic AI IDE

    Features:
    1. Unified daemon with exclusive authority
    2. Repository-wide activation monitoring
    3. IDE AI client interface
    4. Human collaboration interface
    5. Real-time coordination between all components
    """

    def __init__(
        self,
        daemon_host: str = "127.0.0.1",
        daemon_port: int = 8080,
        integration_port: int = 8081,
    ):
        self.daemon_host = daemon_host
        self.daemon_port = daemon_port
        self.integration_port = integration_port
        self.daemon_url = f"http://{daemon_host}:{daemon_port}"

        # Core components
        self.daemon = None
        self.activation_system = None
        self.authority_guard = None

        # State
        self.running = False
        self.start_time = time.time()
        self.total_queries = 0
        self.total_activations = 0

        # FastAPI app for integration layer
        self.app = FastAPI(
            title="Polymathic AI IDE Integration",
            description="Complete integration system for AI IDE with exclusive authority",
            version="1.0.0",
        )

        # Setup CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Local only
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Setup routes
        self._setup_routes()

        # Signal handling
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        logger.info(
            f"Complete Integration System initialized on port {integration_port}"
        )

    def signal_handler(self, signum, frame):
        """Handle interrupt signals gracefully"""
        logger.info(f"Signal {signum} received, shutting down gracefully...")
        self.running = False

    def _setup_routes(self):
        """Setup FastAPI routes for integration layer"""

        @self.app.get("/")
        async def root():
            return {
                "system": "Polymathic AI IDE Integration",
                "version": "1.0.0",
                "status": "operational" if self.running else "starting",
                "principle": "All intelligence paths factor through the daemon",
                "endpoints": {
                    "/status": "GET - System status",
                    "/query": "POST - Query the system (IDE AI or human)",
                    "/collaborate": "POST - Start collaboration session",
                    "/activations": "GET - Recent activations",
                    "/collaborations": "GET - Active collaborations",
                },
            }

        @self.app.get("/status", response_model=IntegrationStatus)
        async def status():
            """Get complete system status"""
            return await self.get_integration_status()

        @self.app.post("/query")
        async def query_endpoint(query: IDEQuery):
            """Query endpoint for IDE AI or human"""
            return await self.handle_integrated_query(query)

        @self.app.post("/collaborate")
        async def collaborate_endpoint(request: CollaborationRequest):
            """Start a collaboration session"""
            return await self.start_collaboration(request)

        @self.app.get("/activations")
        async def activations_endpoint(limit: int = 20):
            """Get recent repository activations"""
            if self.activation_system:
                return self.activation_system.get_recent_activations(limit)
            return {"error": "Activation system not running"}

        @self.app.get("/collaborations")
        async def collaborations_endpoint():
            """Get active collaborations"""
            if self.activation_system:
                return self.activation_system.get_active_collaborations()
            return {"error": "Activation system not running"}

        @self.app.get("/health")
        async def health_endpoint():
            """Health check"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "daemon": self.daemon is not None,
                    "activation_system": self.activation_system is not None,
                    "authority_guard": self.authority_guard is not None,
                },
            }

    async def initialize(self) -> bool:
        """Initialize all components"""
        logger.info("Initializing Complete Integration System...")

        if not IMPORT_SUCCESS:
            logger.error("Failed to import required components")
            return False

        try:
            # 1. Enforce exclusive authority
            logger.info("Enforcing exclusive authority...")
            self.authority_guard = enforce_daemon_runtime()

            # 2. Initialize daemon
            logger.info("Initializing Local AI Daemon...")
            self.daemon = LocalAIDaemon(host=self.daemon_host, port=self.daemon_port)

            daemon_initialized = await self.daemon.initialize()
            if not daemon_initialized:
                logger.error("Failed to initialize daemon")
                return False

            # 3. Initialize activation system
            logger.info("Initializing Repository Activation System...")
            self.activation_system = RepoActivationSystem(daemon_url=self.daemon_url)

            activation_started = self.activation_system.start()
            if not activation_started:
                logger.error("Failed to start activation system")
                return False

            logger.info("Complete Integration System initialization successful")
            return True

        except Exception as e:
            logger.error(f"Integration initialization failed: {e}")
            return False

    async def get_integration_status(self) -> IntegrationStatus:
        """Get complete integration status"""
        uptime = time.time() - self.start_time

        # Get daemon status if available
        daemon_running = False
        christ_score = 0.0

        if self.daemon:
            try:
                # Try to get status from daemon
                response = requests.get(f"{self.daemon_url}/status", timeout=5)
                if response.status_code == 200:
                    daemon_status = response.json()
                    daemon_running = daemon_status.get("status") == "operational"
                    christ_score = daemon_status.get("christ_score", 0.0)
            except:
                daemon_running = False

        # Get activation system status
        activation_system_running = (
            self.activation_system is not None and self.activation_system.running
        )

        # Get authority status
        authority_enforced = self.authority_guard is not None

        # Get collaboration count
        active_collaborations = 0
        if self.activation_system:
            active_collaborations = len(self.activation_system.active_collaborations)

        return IntegrationStatus(
            daemon_running=daemon_running,
            activation_system_running=activation_system_running,
            authority_enforced=authority_enforced,
            total_queries=self.total_queries,
            total_activations=self.total_activations,
            active_collaborations=active_collaborations,
            christ_score=christ_score,
            uptime_seconds=uptime,
        )

    async def handle_integrated_query(self, query: IDEQuery) -> Dict:
        """Handle query from IDE AI or human"""
        self.total_queries += 1

        try:
            # Determine client type from context
            client_type = "ide_ai"
            if query.context and query.context.get("source") == "human":
                client_type = "human"

            # Build daemon query
            daemon_query = QueryRequest(
                text=query.text,
                client_type=client_type,
                context=query.context,
                require_constraints=True,
                max_length=1024,
                temperature=0.7,
            )

            # Send to daemon
            response = requests.post(
                f"{self.daemon_url}/query", json=daemon_query.dict(), timeout=30
            )

            if response.status_code == 200:
                result = response.json()

                # Check if this should trigger collaboration
                should_collaborate = self._should_trigger_collaboration(
                    query, result, client_type
                )

                if should_collaborate:
                    # Start collaboration
                    collaboration_request = CollaborationRequest(
                        file_path=query.context.get("file_path", "unknown"),
                        change_type="query_triggered",
                        source=client_type,
                        description=f"Query triggered collaboration: {query.text[:100]}...",
                    )

                    collaboration = await self.start_collaboration(
                        collaboration_request
                    )
                    result["collaboration_started"] = True
                    result["collaboration_id"] = collaboration.get("collaboration_id")
                else:
                    result["collaboration_started"] = False

                return result
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Daemon query failed: {response.text}",
                )

        except Exception as e:
            logger.error(f"Integrated query failed: {e}")
            raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

    def _should_trigger_collaboration(
        self, query: IDEQuery, result: Dict, client_type: str
    ) -> bool:
        """Determine if query should trigger collaboration"""
        # High Christ Score queries don't need collaboration
        if result.get("christ_score", 0) >= 0.95:
            return False

        # Check if this is about repository changes
        query_text = query.text.lower()
        change_keywords = [
            "change",
            "modify",
            "edit",
            "update",
            "refactor",
            "add",
            "remove",
            "delete",
            "create",
            "implement",
        ]

        if any(keyword in query_text for keyword in change_keywords):
            return True

        # Check if context indicates file change
        if query.context and query.context.get("file_context"):
            return True

        # If IDE AI is querying about human work, collaborate
        if client_type == "ide_ai" and "human" in query_text:
            return True

        # If human is querying about IDE AI work, collaborate
        if client_type == "human" and ("ide" in query_text or "ai" in query_text):
            return True

        return False

    async def start_collaboration(self, request: CollaborationRequest) -> Dict:
        """Start a collaboration session"""
        self.total_activations += 1

        if not self.activation_system:
            return {"error": "Activation system not running"}

        # Convert to activation system types
        try:
            change_type = ActivationType(request.change_type)
        except:
            change_type = ActivationType.MANUAL_TRIGGER

        try:
            source = ChangeSource(request.source)
        except:
            source = ChangeSource.UNKNOWN

        # Trigger activation
        activation = self.activation_system.trigger_activation(
            file_path=request.file_path, change_type=change_type, source=source
        )

        if activation and activation.get("collaboration_started"):
            collaboration_id = activation.get("collaboration_id")

            # Add description to collaboration
            if collaboration_id and request.description:
                self.activation_system.add_collaboration_message(
                    collaboration_id=collaboration_id,
                    sender="integration_system",
                    text=f"Collaboration started: {request.description}",
                )

            return {
                "success": True,
                "collaboration_id": collaboration_id,
                "activation": activation,
            }
        else:
            return {
                "success": False,
                "error": "Failed to start collaboration",
                "activation": activation,
            }

    async def run_daemon(self):
        """Run the daemon server"""
        if not self.daemon:
            logger.error("Daemon not initialized")
            return

        # Run daemon in background thread
        def run_daemon_server():
            uvicorn.run(
                self.daemon.app,
                host=self.daemon_host,
                port=self.daemon_port,
                log_level="info",
            )

        daemon_thread = threading.Thread(target=run_daemon_server, daemon=True)
        daemon_thread.start()

        logger.info(f"Daemon running on http://{self.daemon_host}:{self.daemon_port}")

    async def run_integration(self):
        """Run the integration server"""
        # Run integration server
        config = uvicorn.Config(
            self.app, host="127.0.0.1", port=self.integration_port, log_level="info"
        )

        server = uvicorn.Server(config)

        logger.info(
            f"Integration server running on http://127.0.0.1:{self.integration_port}"
        )
        await server.serve()

    async def run(self):
        """Run the complete integration system"""
        if not await self.initialize():
            logger.error("Failed to initialize integration system")
            return

        self.running = True

        # Start daemon
        await self.run_daemon()

        # Give daemon time to start
        await asyncio.sleep(2)

        # Start integration server
        await self.run_integration()


# ==================== MAIN ENTRY POINT ====================


async def main():
    """Main entry point"""
    print("=" * 70)
    print("POLYMATHIC AI IDE - COMPLETE INTEGRATION SYSTEM")
    print("=" * 70)
    print("Principle: All intelligence paths factor through the daemon")
    print("=" * 70)
    print("Components:")
    print("  1. Local AI Daemon (exclusive authority)")
    print("  2. Repository Activation System (any change → chat)")
    print("  3. Authority Guard (no bypass possible)")
    print("  4. IDE AI Client Interface")
    print("  5. Human Collaboration Interface")
    print("=" * 70)
    print("Endpoints:")
    print("  Daemon:      http://localhost:8080")
    print("  Integration: http://localhost:8081")
    print("=" * 70)

    # Create integration system
    integration = CompleteIntegrationSystem(
        daemon_host="127.0.0.1", daemon_port=8080, integration_port=8081
    )

    try:
        await integration.run()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down integration system...")
        integration.running = False
        print("✅ Integration system stopped")
    except Exception as e:
        logger.error(f"Integration system failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
