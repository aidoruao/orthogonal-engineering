#!/usr/bin/env python3
"""Lean4 Bridge — stdlib only, zero dependencies.
Receives Lean4 code from the Proving Ground HTML,
writes it to a temp file, compiles it with `lean`,
and returns the result as JSON.
"""

import json
import subprocess
import tempfile
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

LEAN4_DIR = Path("/home/idor/oe-local/lean4")
PORT = 28428

class Lean4Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Read the request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body)
            lean_code = data.get('code', '')
            row_num = data.get('row', 0)
        except json.JSONDecodeError:
            self.send_json(400, {"error": "Invalid JSON"})
            return
        
        if not lean_code:
            self.send_json(400, {"error": "No code provided"})
            return
        
        # Write code to temp file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.lean',
            dir="/tmp",
            delete=False
        ) as f:
            f.write(lean_code)
            temp_path = f.name
        
        try:
            # Compile with lean
            result = subprocess.run(
                ['lean', temp_path],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=LEAN4_DIR
            )
            
            success = result.returncode == 0
            output = result.stdout.strip()
            errors = result.stderr.strip()
            
            self.send_json(200, {
                "success": success,
                "output": output,
                "errors": errors,
                "row": row_num
            })
        except subprocess.TimeoutExpired:
            self.send_json(500, {"error": "Compilation timed out after 30 seconds"})
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def do_OPTIONS(self):
        # CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def log_message(self, format, *args):
        # Suppress default logging to stderr
        pass

if __name__ == '__main__':
    os.chdir(LEAN4_DIR)
    server = HTTPServer(('localhost', PORT), Lean4Handler)
    print(f"Lean4 Bridge running on http://localhost:{PORT}")
    print(f"Working directory: {LEAN4_DIR}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()
