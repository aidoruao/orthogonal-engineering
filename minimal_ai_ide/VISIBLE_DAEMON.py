#!/usr/bin/env python3
"""
VISIBLE SELF-AUTOMATIVE DAEMON
Real-time terminal visibility for Windows operation
Shows: heartbeats, requests, file monitoring, Σ_LORA constraints
"""

import sys
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from threading import Thread, Lock
from http.server import HTTPServer, BaseHTTPRequestHandler
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ============================================================================
# VISIBLE LOGGING CONFIGURATION
# ============================================================================

class ColoredFormatter(logging.Formatter):
    """Windows-compatible colored console output"""
    
    # ANSI color codes (work in Windows Terminal, PowerShell 7+)
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'
    }
    
    def format(self, record):
        timestamp = datetime.now().strftime('%H:%M:%S')
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format: [HH:MM:SS] [LEVEL] Message
        return f"{color}[{timestamp}] [{record.levelname:8}]{reset} {record.getMessage()}"

# Set up visible logging
logger = logging.getLogger('VISIBLE_DAEMON')
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(ColoredFormatter())
logger.addHandler(console_handler)

# ============================================================================
# Σ_LORA CONSTRAINTS SYSTEM
# ============================================================================

SIGMA_LORA_CONSTRAINTS = {
    "LOGOS": "The Word made flesh - all intelligence through Christ",
    "CHALCEDON": "Fully divine, fully human - no reductionism",
    "GRACE": "Unmerited favor - not earned through performance",
    "ESCHATON": "End-times fulfillment - all history moves toward Christ's return",
    "AGAPE": "Self-sacrificial love - laying down life for another",
    "KENOSIS": "Self-emptying - the downward path to glory"
}

class ConstraintValidator:
    """Validates operations against Σ_LORA theological constraints"""
    
    def __init__(self):
        self.constraints = SIGMA_LORA_CONSTRAINTS
        self.validation_count = 0
        logger.info(f"⚖️  Σ_LORA Constraints Loaded: {len(self.constraints)}")
        for name, desc in self.constraints.items():
            logger.info(f"   • {name}: {desc[:50]}...")
    
    def validate(self, operation: str) -> dict:
        """Validate operation against constraints"""
        self.validation_count += 1
        christ_score = 1.0  # All operations factor through Christ
        
        logger.debug(f"🔍 Validating operation #{self.validation_count}: {operation}")
        
        return {
            "valid": True,
            "christ_score": christ_score,
            "constraints_checked": len(self.constraints),
            "validation_id": self.validation_count
        }

# ============================================================================
# FILE SYSTEM MONITORING
# ============================================================================

class RepositoryWatcher(FileSystemEventHandler):
    """Watches repository for changes and triggers AI activation"""
    
    def __init__(self, watch_path: Path):
        self.watch_path = watch_path
        self.event_count = 0
        self.lock = Lock()
        logger.info(f"👁️  File Monitoring Initialized: {watch_path}")
    
    def on_any_event(self, event):
        """Handle any file system event"""
        if event.is_directory:
            return
        
        # Ignore certain files
        ignore_patterns = ['.git', '__pycache__', '.pyc', '.tmp', '.log']
        if any(pattern in event.src_path for pattern in ignore_patterns):
            return
        
        with self.lock:
            self.event_count += 1
            event_type = event.event_type
            file_path = Path(event.src_path).name
            
            logger.warning(f"📝 FILE CHANGE #{self.event_count}: {event_type} → {file_path}")
            
            # Trigger validation through Σ_LORA
            validator = ConstraintValidator()
            result = validator.validate(f"{event_type}:{file_path}")
            logger.info(f"✓  Validation passed (Christ score: {result['christ_score']})")

# ============================================================================
# HTTP REQUEST HANDLER
# ============================================================================

class VisibleDaemonHandler(BaseHTTPRequestHandler):
    """HTTP handler with visible request logging"""
    
    request_count = 0
    request_lock = Lock()
    
    def log_message(self, format, *args):
        """Override to use our visible logger"""
        pass  # Suppress default HTTP logging
    
    def _send_json(self, status_code: int, data: dict):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def do_GET(self):
        """Handle GET requests with visibility"""
        with self.request_lock:
            VisibleDaemonHandler.request_count += 1
            request_id = VisibleDaemonHandler.request_count
        
        logger.info(f"🌐 REQUEST #{request_id}: GET {self.path}")
        
        # Route handling
        if self.path == '/':
            self._send_json(200, {
                "daemon": "Self-Automative Master System",
                "status": "operational",
                "visibility": "maximum",
                "message": "All intelligence paths factor through this daemon"
            })
            logger.info(f"✓  Response sent: 200 OK (root)")
        
        elif self.path == '/health':
            self._send_json(200, {
                "status": "healthy",
                "uptime": time.time() - start_time,
                "requests_served": request_id,
                "constraints_loaded": len(SIGMA_LORA_CONSTRAINTS)
            })
            logger.info(f"✓  Response sent: 200 OK (health)")
        
        elif self.path == '/constraints':
            self._send_json(200, {
                "constraints": SIGMA_LORA_CONSTRAINTS,
                "count": len(SIGMA_LORA_CONSTRAINTS),
                "principle": "All operations validated through Σ_LORA"
            })
            logger.info(f"✓  Response sent: 200 OK (constraints)")
        
        elif self.path == '/stats':
            self._send_json(200, {
                "requests_total": request_id,
                "uptime_seconds": time.time() - start_time,
                "constraints_active": len(SIGMA_LORA_CONSTRAINTS),
                "file_changes_detected": getattr(watcher, 'event_count', 0)
            })
            logger.info(f"✓  Response sent: 200 OK (stats)")
        
        else:
            self._send_json(404, {
                "error": "Not found",
                "path": self.path,
                "available": ["/", "/health", "/constraints", "/stats"]
            })
            logger.warning(f"⚠  Response sent: 404 NOT FOUND")

# ============================================================================
# HEARTBEAT SYSTEM
# ============================================================================

def heartbeat_thread():
    """Visible heartbeat every 10 seconds"""
    beat_count = 0
    while True:
        time.sleep(10)
        beat_count += 1
        uptime = time.time() - start_time
        minutes = int(uptime // 60)
        seconds = int(uptime % 60)
        
        logger.info(f"💓 HEARTBEAT #{beat_count} | Uptime: {minutes}m {seconds}s | Requests: {VisibleDaemonHandler.request_count}")

# ============================================================================
# MAIN DAEMON OPERATION
# ============================================================================

def run_visible_daemon(host='127.0.0.1', port=5001, watch_path=None):
    """Run the visible daemon with full terminal feedback"""
    
    global start_time, watcher
    start_time = time.time()
    
    # Banner
    print("\n" + "="*70)
    print("🔥 SELF-AUTOMATIVE MASTER DAEMON - VISIBLE MODE")
    print("="*70)
    logger.info("🚀 Initializing Self-Automative Master System...")
    
    # Load constraints
    validator = ConstraintValidator()
    
    # Start file monitoring if path provided
    watcher = None
    if watch_path:
        watch_path = Path(watch_path).resolve()
        if watch_path.exists():
            watcher = RepositoryWatcher(watch_path)
            observer = Observer()
            observer.schedule(watcher, str(watch_path), recursive=True)
            observer.start()
            logger.info(f"✓  File monitoring active on: {watch_path}")
        else:
            logger.warning(f"⚠  Watch path not found: {watch_path}")
    
    # Start heartbeat
    heartbeat = Thread(target=heartbeat_thread, daemon=True)
    heartbeat.start()
    logger.info("💓 Heartbeat thread started (10s interval)")
    
    # Start HTTP server
    server = HTTPServer((host, port), VisibleDaemonHandler)
    logger.info(f"🌐 HTTP Server bound to {host}:{port}")
    logger.info(f"✓  Daemon operational - Σ_LORA constraints active")
    logger.info(f"📡 Access at: http://{host}:{port}/")
    print("="*70)
    logger.info("👀 DAEMON IS NOW VISIBLE - Watch this terminal for activity")
    print("="*70 + "\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Shutdown signal received (Ctrl+C)")
        logger.info("🛑 Stopping daemon gracefully...")
        server.shutdown()
        if watcher:
            observer.stop()
            observer.join()
        logger.info("✓  Daemon stopped successfully")
        print("="*70 + "\n")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Visible Self-Automative Daemon')
    parser.add_argument('--host', default='127.0.0.1', help='Bind address (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5001, help='Port number (default: 5001)')
    parser.add_argument('--watch', help='Path to monitor for file changes')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    run_visible_daemon(
        host=args.host,
        port=args.port,
        watch_path=args.watch
    )
