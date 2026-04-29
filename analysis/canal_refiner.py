"""Canal Refiner - LOGGING CONFIGURATION (UTF-8 file output, ASCII console)"""
import re
import json
import pathlib
import csv
import logging
from datetime import datetime

# LOGGING CONFIGURATION (UTF-8 file output, ASCII console)
logging.basicConfig(
    filename='pipeline_run_log.txt',
    level=logging.INFO,
    encoding='utf-8',
    format='%(asctime)s - %(message)s'
)

# CONFIGURATION
MD_DIR = pathlib.Path(".")
# Flexible Header: Matches '### 2024-01-01 User', '### assistant:', etc.
HEADER_RE = re.compile(r"^#{1,6}\s+(.*?)\b(user|human|assistant|bot|agent)\b", re.MULTILINE | re.IGNORECASE)
# Invariant Keywords
INVAR_RE = re.compile(r"\binvariant\b|\bconstraint\b|\bnever\b|\balways\b|\bmust\b|\bonly\b", re.IGNORECASE)
# 30 minutes of silence defines a new session
SESSION_GAP_SECONDS = 1800 

def extract_turns(md_file):
    text = md_file.read_text(encoding="utf-8", errors="ignore")
    matches = list(HEADER_RE.finditer(text))
    turns = []
    
    for i, match in enumerate(matches):
        header_text = match.group(1).strip()
        role = match.group(2).lower()
        # Standardize roles
        role_type = 'human' if role in ['human', 'user'] else 'assistant'
            
        # Capture the message content
        start_pos = match.end()
        end_pos = matches[i+1].start() if i+1 < len(matches) else start_pos + 3000
        content = text[start_pos:end_pos].strip()
        
        # Parse Timestamps (handles YYYY-MM-DD and Unix formats)
        ts = None
        ts_match = re.search(r"(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})|(\d{10}\.\d+)", header_text)
        if ts_match:
            try:
                if ts_match.group(1):
                    ts = datetime.strptime(ts_match.group(1), "%Y-%m-%d %H:%M:%S").timestamp()
                else:
                    ts = float(ts_match.group(2))
            except: pass
        
        turns.append({
            "file": md_file.name,
            "timestamp": ts,
            "role": role_type,
            "content_preview": content[:100].replace("\n", " "),
            "has_keyword": bool(INVAR_RE.search(content)),
            "word_count": len(content.split())
        })
    return turns

def process():
    all_turns = []
    logging.info("--- Orthogonal Engineering: Canal Refiner ---")
    for md_file in MD_DIR.glob("*.md"):
        logging.info(f"Reading {md_file.name}...")
        all_turns.extend(extract_turns(md_file))
    
    if not all_turns:
        logging.error("No conversation turns found. Check your Markdown header format.")
        print("[FAIL] No turns extracted. See pipeline_run_log.txt")
        return

    # 1. Sort and Sessionize
    all_turns.sort(key=lambda x: (x['file'], x['timestamp'] if x['timestamp'] else 0))
    current_session, last_ts, last_file = 0, None, None
    
    for turn in all_turns:
        if last_file != turn['file'] or (turn['timestamp'] and last_ts and (turn['timestamp'] - last_ts > SESSION_GAP_SECONDS)):
            current_session += 1
        turn['session_id'] = current_session
        last_ts, last_file = turn['timestamp'], turn['file']

    # 2. THE CANAL FILTER (5-Turn Window Logic)
    # Only verify an invariant if both Human and Assistant use keywords in the same window.
    for i in range(len(all_turns)):
        turn = all_turns[i]
        turn['verified_invariant'] = False
        if not turn['has_keyword']: continue
            
        # Look at window (2 turns before, 2 turns after)
        start_win = max(0, i - 2)
        end_win = min(len(all_turns), i + 3)
        window = all_turns[start_win:end_win]
        
        for peer in window:
            if peer['session_id'] == turn['session_id']: 
                if peer['role'] != turn['role'] and peer['has_keyword']:
                    turn['verified_invariant'] = True
                    break

    # 3. OUTPUT
    verified_count = sum(1 for t in all_turns if t['verified_invariant'])
    summary = {
        "total_turns": len(all_turns),
        "raw_keyword_matches": sum(1 for t in all_turns if t['has_keyword']),
        "verified_canal_invariants": verified_count,
        "depth_score_pct": round((verified_count / len(all_turns)) * 100, 2)
    }
    
    logging.info(f"Results: {json.dumps(summary, indent=2)}")
    print(f"\n[SUCCESS] Canal Refiner complete. See pipeline_run_log.txt for details.")
    
    with open("refined_inventory.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["file", "session_id", "role", "verified_invariant", "content_preview"])
        writer.writeheader()
        writer.writerows([{k: t[k] for k in ["file", "session_id", "role", "verified_invariant", "content_preview"]} for t in all_turns])

    logging.info("'refined_inventory.csv' created successfully.")
    print("[OUTPUT] refined_inventory.csv written")

if __name__ == "__main__":
    process()