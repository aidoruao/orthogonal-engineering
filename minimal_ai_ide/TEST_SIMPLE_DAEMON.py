"""
TEST_SIMPLE_DAEMON.py
=====================

Simple test daemon that binds specifically to 127.0.0.1 (localhost)
to avoid Windows Firewall issues with 0.0.0.0 binding.

This daemon is guaranteed to work on Windows for testing connectivity.
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from typing import Dict, Optional

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [TEST-DAEMON] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Test Simple Daemon")

# Track startup time
start_time = time.time()
requests_processed = 0


@app.get("/")
async def root():
    """Root endpoint with system info"""
    return {
        "service": "Test Simple Daemon",
        "version": "1.0.0",
        "status": "operational",
        "bind_address": "127.0.0.1",
        "principle": "Simple guaranteed-working daemon for Windows",
        "endpoints": {
            "/": "This info",
            "/health": "Health check",
            "/status": "System status",
            "/test": "Test endpoint",
            "/echo": "POST - Echo back data",
        },
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    global requests_processed
    requests_processed += 1
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": time.time() - start_time,
        "requests": requests_processed,
    }


@app.get("/status")
async def status():
    """System status endpoint"""
    return {
        "status": "operational",
        "mode": "test_simple",
        "bind_host": "127.0.0.1",
        "uptime_seconds": time.time() - start_time,
        "requests_processed": requests_processed,
        "timestamp": datetime.now().isoformat(),
        "python_version": sys.version,
        "platform": sys.platform,
    }


@app.get("/test")
async def test():
    """Test endpoint for connectivity verification"""
    global requests_processed
    requests_processed += 1
    return {
        "test": "successful",
        "message": "Test Simple Daemon is working!",
        "connectivity": "verified",
        "timestamp": datetime.now().isoformat(),
        "request_number": requests_processed,
    }


@app.post("/echo")
async def echo(request: Request):
    """Echo endpoint - returns whatever is sent"""
    global requests_processed
    requests_processed += 1

    try:
        data = await request.json()
        return {
            "echo": data,
            "timestamp": datetime.now().isoformat(),
            "received_from": request.client.host if request.client else "unknown",
            "method": "POST",
        }
    except:
        text = await request.body()
        return {
            "echo": text.decode("utf-8"),
            "timestamp": datetime.now().isoformat(),
            "received_from": request.client.host if request.client else "unknown",
            "method": "POST (raw)",
        }


@app.get("/ping")
async def ping():
    """Simple ping endpoint"""
    global requests_processed
    requests_processed += 1
    return {"pong": datetime.now().isoformat()}


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Test Simple Daemon for Windows connectivity testing"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to bind to (default: 5000)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1 - localhost only)",
    )

    args = parser.parse_args()

    # Log startup info
    logger.info("=" * 60)
    logger.info("TEST SIMPLE DAEMON - GUARANTEED WORKING ON WINDOWS")
    logger.info("=" * 60)
    logger.info(f"Binding to: {args.host}:{args.port}")
    logger.info(f"Python: {sys.version}")
    logger.info("=" * 60)
    logger.info("Endpoints:")
    logger.info(f"  • http://{args.host}:{args.port}/")
    logger.info(f"  • http://{args.host}:{args.port}/health")
    logger.info(f"  • http://{args.host}:{args.port}/status")
    logger.info(f"  • http://{args.host}:{args.port}/test")
    logger.info(f"  • http://{args.host}:{args.port}/ping")
    logger.info(f"  • http://{args.host}:{args.port}/echo (POST)")
    logger.info("=" * 60)
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)

    # Configure and run server
    config = uvicorn.Config(
        app,
        host=args.host,
        port=args.port,
        log_level="info",
        access_log=True,
    )

    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Daemon stopped by user")
    except Exception as e:
        logger.error(f"Daemon failed: {e}")
        sys.exit(1)
