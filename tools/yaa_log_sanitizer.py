#!/usr/bin/env python3
"""YAA Log Sanitizer — strips secrets from terminal logs before commit."""
import re, sys
from pathlib import Path

LOG_DIR = Path("/home/idor/oe-local/logs/terminal")

# Patterns to strip
SECRETS = [
    (r'sk-[a-zA-Z0-9]{20,60}', 'DEEPSEEK_API_KEY_REDACTED'),
    (r'export DEEPSEEK_API_KEY=.*', 'export DEEPSEEK_API_KEY=REDACTED'),
    (r'api_key.*=.*["\']?[a-zA-Z0-9_-]{20,}', 'API_KEY_REDACTED'),
    (r'token [a-zA-Z0-9_-]{20,}', 'TOKEN_REDACTED'),
    (r'ghp_[a-zA-Z0-9]{36}', 'GITHUB_TOKEN_REDACTED'),
    (r'gho_[a-zA-Z0-9]{36}', 'GITHUB_OAUTH_REDACTED'),
    (r'ghu_[a-zA-Z0-9]{36}', 'GITHUB_USER_TOKEN_REDACTED'),
    (r'ghs_[a-zA-Z0-9]{36}', 'GITHUB_SERVER_TOKEN_REDACTED'),
    (r'ghr_[a-zA-Z0-9]{36}', 'GITHUB_REFRESH_TOKEN_REDACTED'),
    (r'Authorization:.*', 'AUTHORIZATION_HEADER_REDACTED'),
    (r'Bearer [a-zA-Z0-9._-]+', 'BEARER_TOKEN_REDACTED'),
]

def sanitize_file(filepath):
    """Strip secrets from a log file."""
    try:
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        
        original_len = len(content)
        for pattern, replacement in SECRETS:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        if len(content) != original_len:
            with open(filepath, 'w') as f:
                f.write(content)
            return True
        return False
    except:
        return False

def sanitize_all():
    """Sanitize all log files."""
    if not LOG_DIR.exists():
        return
    for logfile in LOG_DIR.glob("session_*.log"):
        if sanitize_file(logfile):
            print(f"Sanitized: {logfile.name}")

if __name__ == "__main__":
    sanitize_all()
    print("Log sanitization complete.")
