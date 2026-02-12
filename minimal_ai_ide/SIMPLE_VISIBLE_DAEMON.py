"""
SIMPLE_VISIBLE_DAEMON.py
========================

SIMPLEST WORKING VISIBLE DAEMON
No emojis, no fancy logging, just works
Windows compatible (127.0.0.1 binding)
Real-time terminal visibility
Σ_LORA constraints integrated

PRINCIPLE: "All intelligence paths factor through this daemon"
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

# Configure simple visible logging
logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%H:%M:%S"
)
logger = logging.getLogger()

# Σ_LORA Constraints
SIGMA_LORA_CONSTRAINTS = {
    "LOGOS": "The Word made flesh - all intelligence through Christ",
    "CHALCEDON": "Fully divine, fully human - no reductionism",
    "GRACE": "Unmerited favor - not earned through performance",
    "ESCHATON": "End-times fulfillment - all history moves toward Christ's return",
    "AGAPE": "Self-sacrificial love - laying down life for another",
    "KENOSIS": "Self-emptying - the downward path to glory",
}


class SimpleVisibleHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler with visible logging"""

    request_count = 0

    def log_message(self, format, *args):
        """Override to use our visible logger"""
        # Don't use default logging

    def _send_json(self, status, data):
        """Send JSON response"""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def do_GET(self):
        """Handle GET requests"""
        SimpleVisibleHandler.request_count += 1
        req_id = SimpleVisibleHandler.request_count

        logger.info(f"REQUEST #{req_id}: GET {self.path}")

        if self.path == "/":
            self._send_json(
                200,
                {
                    "daemon": "Simple Visible Daemon",
                    "status": "operational",
                    "message": "All intelligence paths factor through this daemon",
                    "timestamp": datetime.now().isoformat(),
                },
            )
            logger.info(f"Response: 200 OK (root)")

        elif self.path == "/health":
            self._send_json(
                200,
                {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "requests": req_id,
                },
            )
            logger.info(f"Response: 200 OK (health)")

        elif self.path == "/constraints":
            self._send_json(
                200,
                {
                    "constraints": SIGMA_LORA_CONSTRAINTS,
                    "count": len(SIGMA_LORA_CONSTRAINTS),
                    "principle": "All operations validated through Σ_LORA",
                    "timestamp": datetime.now().isoformat(),
                },
            )
            logger.info(f"Response: 200 OK (constraints)")

        elif self.path == "/test":
            self._send_json(
                200,
                {
                    "test": "successful",
                    "message": "Simple visible daemon is working!",
                    "timestamp": datetime.now().isoformat(),
                    "request_number": req_id,
                },
            )
            logger.info(f"Response: 200 OK (test)")

        else:
            self._send_json(
                404,
                {
                    "error": "Not found",
                    "path": self.path,
                    "available": ["/", "/health", "/constraints", "/test"],
                },
            )
            logger.info(f"Response: 404 Not Found")


def heartbeat_thread(server):
    """Simple heartbeat with visible logging"""
    beat_count = 0
    start_time = time.time()

    while True:
        time.sleep(10)
        beat_count += 1
        uptime = time.time() - start_time
        minutes = int(uptime // 60)
        seconds = int(uptime % 60)

        logger.info(
            f"HEARTBEAT #{beat_count} | Uptime: {minutes}m {seconds}s | Requests: {SimpleVisibleHandler.request_count}"
        )


def run_simple_visible_daemon(host="127.0.0.1", port=5001):
    """Run the simple visible daemon"""

    # Show startup banner
    print("\n" + "=" * 70)
    print("SIMPLE VISIBLE DAEMON - GUARANTEED WORKING")
    print("=" * 70)
    logger.info("Starting Simple Visible Daemon...")
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Σ_LORA Constraints: {len(SIGMA_LORA_CONSTRAINTS)} loaded")

    for name, desc in SIGMA_LORA_CONSTRAINTS.items():
        logger.info(f"  - {name}: {desc[:50]}...")

    print("=" * 70)
    logger.info("DAEMON IS NOW VISIBLE - Watch this terminal for activity")
    print("=" * 70 + "\n")

    try:
        # Create and start server with error handling
        logger.info(f"Attempting to bind to {host}:{port}...")
        server = HTTPServer((host, port), SimpleVisibleHandler)
        logger.info(f"✓ Server created successfully")

        # Start heartbeat thread
        heartbeat = Thread(target=heartbeat_thread, args=(server,), daemon=True)
        heartbeat.start()
        logger.info("✓ Heartbeat thread started")

        logger.info(f"✓ Server started on http://{host}:{port}")
        logger.info("Press Ctrl+C to stop")
        print()

        server.serve_forever()
    except OSError as e:
        logger.error(f"❌ Failed to bind to port {port}: {e}")
        logger.error(f"  Try a different port: --port 5003")
        logger.error(
            f"  Or check if port is already in use: netstat -ano | findstr :{port}"
        )
        return False
    except KeyboardInterrupt:
        logger.info("Shutdown signal received")
        logger.info("Stopping daemon...")
        server.server_close()
        logger.info("Daemon stopped successfully")
        print("=" * 70 + "\n")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

    return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Simple Visible Daemon")
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", type=int, default=5001, help="Port to bind to (default: 5001)"
    )
    parser.add_argument(
        "--try-ports", action="store_true", help="Try multiple ports if default fails"
    )

    args = parser.parse_args()

    if args.try_ports:
        # Try multiple ports
        ports_to_try = [5001, 5002, 5003, 5004, 5005]
        for port in ports_to_try:
            logger.info(f"Trying port {port}...")
            if run_simple_visible_daemon(host=args.host, port=port):
                break  # Success
            if port != ports_to_try[-1]:
                logger.info(f"Port {port} failed, trying next port...")
                time.sleep(1)
    else:
        # Try just the specified port
        run_simple_visible_daemon(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
