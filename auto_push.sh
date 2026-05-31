# GENERATED_BY: 2a_kimi_5-31-26
# SESSION: Citizen Kingdom Architecture
# DATE: 2026-05-31
# PURPOSE: Hardened auto-pusher with safety gates
# STATUS: deployed

#!/bin/bash
cd /home/idor/oe-local

# ── CONFIG ──
SLEEP_SECONDS=300          # 5 minutes between checks (not 30s)
MAX_FILE_MB=99             # GitHub GH001 limit
NO_PUSH_FLAG=".no_push"    # touch this file to pause auto-pusher

while true; do
    # ── KILL SWITCH ──
    if [ -f "$NO_PUSH_FLAG" ]; then
        echo "[$(date '+%H:%M:%S')] PAUSED: $NO_PUSH_FLAG exists. Remove to resume."
        sleep 60
        continue
    fi

    # ── PULL FIRST ──
    git pull --rebase origin main 2>/dev/null

    # ── CHECK IF ANYTHING TO COMMIT ──
    if [ -z "$(git status --porcelain)" ]; then
        sleep $SLEEP_SECONDS
        continue
    fi

    # ── SAFETY GATE 1: Oversized files ──
    OVERSIZED=$(find . -maxdepth 1 -not -path '*/.*' -size +${MAX_FILE_MB}M)
    if [ -n "$OVERSIZED" ]; then
        echo "[$(date '+%H:%M:%S')] CHUNKING: Oversized files detected:"
        echo "$OVERSIZED"
        for f in $OVERSIZED; do
            if [ -f "$f" ]; then
                mv "$f" /mnt/c/Users/Aidor/Downloads/
                split -b ${MAX_FILE_MB}M /mnt/c/Users/Aidor/Downloads/$(basename "$f") /mnt/c/Users/Aidor/Downloads/history_chunk_
                echo "$(basename "$f")" >> .gitignore
                echo "history_chunk_*" >> .gitignore
            fi
        done
    fi

    # ── SAFETY GATE 2: Ignore temp files ──
    git checkout -- '*.tmp' '*.swp' '*.log' 2>/dev/null

    # ── PREVIEW MODE ──
    echo "[$(date '+%H:%M:%S')] PREVIEW of next commit:"
    git status --short
    echo "[$(date '+%H:%M:%S')] Staging in 10 seconds... (Ctrl-C to abort)"
    sleep 10

    # ── STAGE ──
    git add -A

    # ── SAFETY GATE 3: Method body integrity (from old version) ──
    STAGED=$(git diff --cached --name-only | grep '\.py$' | head -1)
    if [ -n "$STAGED" ] && [ -f "$STAGED" ]; then
        METHOD_LOSS=0
        while IFS= read -r method; do
            CURRENT_LINES=$(sed -n "/def ${method}/,/def /p" "$STAGED" 2>/dev/null | wc -l)
            LAST_LINES=$(git show HEAD:"$STAGED" 2>/dev/null | sed -n "/def ${method}/,/def /p" | wc -l)
            if [ "$LAST_LINES" -gt 10 ] && [ "$CURRENT_LINES" -lt $((LAST_LINES / 10)) ]; then
                echo "[$(date '+%H:%M:%S')] WARNING: ${method}() dropped >90% lines. Aborting."
                git reset HEAD
                METHOD_LOSS=1
                break
            fi
        done < <(git show HEAD:"$STAGED" 2>/dev/null | grep -oP 'def \K\w+' | sort -u)
        if [ "$METHOD_LOSS" -eq 1 ]; then
            sleep $SLEEP_SECONDS
            continue
        fi
    fi

    # ── COMMIT ──
    git commit -m "auto: $(git diff --cached --stat | tail -1) files changed at $(date '+%Y-%m-%d %H:%M:%S')"

    # ── PUSH ──
    LOCAL_COMMITS=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)
    if [ "$LOCAL_COMMITS" -gt 0 ]; then
        git push origin main 2>&1 && echo "[$(date '+%H:%M:%S')] Pushed ${LOCAL_COMMITS} commits"
    fi

    sleep $SLEEP_SECONDS
done
