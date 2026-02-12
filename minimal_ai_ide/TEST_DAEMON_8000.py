"""
TEST_DAEMON_8000.py
===================

Simple daemon test on port 8000 to bypass Windows port blocking.
This tests the core daemon functionality without firewall issues.

PRINCIPLE: "All intelligence paths factor through the daemon"
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [TEST-DAEMON-8000] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# ==================== DATA MODELS ====================


class QueryRequest(BaseModel):
    """Query payload from any client"""

    query: str
    context: dict = {}
    constraints: list = []


class QueryResponse(BaseModel):
    """Response from daemon"""

    response: str
    timestamp: str
    constraints_preserved: bool
    processing_time_ms: float


# ==================== FASTAPI APP ====================

app = FastAPI(
    title="Test Daemon 8000",
    description="Simple working daemon on port 8000 for Self-Automative Master System",
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== STATE ====================

startup_time = datetime.now()
constraints = ["LOGOS", "CHALCEDON", "GRACE", "ESCHATON", "AGAPE", "KENOSIS"]
query_count = 0

# ==================== ENDPOINTS ====================


@app.get("/")
async def root():
    """Root endpoint - system information"""
    return {
        "system": "Self-Automative Master System - Test Daemon 8000",
        "status": "operational",
        "uptime": str(datetime.now() - startup_time),
        "port": 8000,
        "principle": "All intelligence paths factor through this daemon",
        "constraints": constraints,
        "query_count": query_count,
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": str(datetime.now() - startup_time),
    }


@app.get("/status")
async def status():
    """System status endpoint"""
    return {
        "system": "Test Daemon 8000",
        "version": "1.0.0",
        "status": "operational",
        "startup_time": startup_time.isoformat(),
        "current_time": datetime.now().isoformat(),
        "uptime": str(datetime.now() - startup_time),
        "constraints": constraints,
        "query_count": query_count,
        "endpoints": [
            "/",
            "/health",
            "/status",
            "/constraints",
            "/test",
            "/query (POST)",
        ],
    }


@app.get("/constraints")
async def get_constraints():
    """Get Σ_LORA constraints"""
    return {
        "constraints": constraints,
        "count": len(constraints),
        "description": "Σ_LORA maximal mathematics constraints",
        "preserved": True,
    }


@app.get("/test")
async def test_endpoint():
    """Test endpoint for connectivity"""
    return {
        "message": "Test Daemon 8000 is working!",
        "timestamp": datetime.now().isoformat(),
        "success": True,
        "port": 8000,
    }


@app.post("/query")
async def process_query(request: QueryRequest):
    """Process a query through the daemon"""
    global query_count
    query_count += 1

    start_time = time.time()

    logger.info(f"Processing query #{query_count}: {request.query[:50]}...")

    # Check constraints
    constraints_preserved = all(
        constraint in constraints for constraint in request.constraints
    )

    # Simulate processing
    await asyncio.sleep(0.1)

    processing_time_ms = (time.time() - start_time) * 1000

    response = QueryResponse(
        response=f"Processed query: '{request.query}'. Constraints preserved: {constraints_preserved}",
        timestamp=datetime.now().isoformat(),
        constraints_preserved=constraints_preserved,
        processing_time_ms=processing_time_ms,
    )

    logger.info(f"Query #{query_count} processed in {processing_time_ms:.2f}ms")

    return response.dict()


@app.post("/echo")
async def echo(request: Request):
    """Echo endpoint for testing"""
    try:
        data = await request.json()
        return {"echo": data, "timestamp": datetime.now().isoformat(), "received": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")


# ==================== STARTUP ====================


def start_daemon():
    """Start the test daemon on port 8000"""
    logger.info("=" * 60)
    logger.info("SELF-AUTOMATIVE MASTER SYSTEM - TEST DAEMON 8000")
    logger.info("=" * 60)
    logger.info("Principle: All intelligence paths factor through this daemon")
    logger.info("Port: 8000")
    logger.info("Endpoints:")
    logger.info("  • http://127.0.0.1:8000/")
    logger.info("  • http://127.0.0.1:8000/health")
    logger.info("  • http://127.0.0.1:8000/status")
    logger.info("  • http://127.0.0.1:8000/constraints")
    logger.info("  • http://127.0.0.1:8000/test")
    logger.info("  • http://127.0.0.1:8000/query (POST)")
    logger.info("  • http://127.0.0.1:8000/echo (POST)")
    logger.info("=" * 60)
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info", access_log=True)


if __name__ == "__main__":
    start_daemon()
