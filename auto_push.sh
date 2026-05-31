#!/bin/bash
cd /home/idor/oe-local

while true; do
    # Pull remote changes first
    git pull --rebase origin main 2>/dev/null

    # Check if there's anything to commit
    if [[ -n $(git status --porcelain) ]]; then
        # Sanitize terminal logs before staging
        python3 tools/yaa_log_sanitizer.py 2>/dev/null

        # Stage everything
        git add -A

        # SAFETY GATE 3: Chunk oversized files before commit
        git diff --cached --name-only | while read f; do
            if [ -f "$f" ] && [ $(stat -c%s "$f" 2>/dev/null || stat -f%z "$f" 2>/dev/null || echo 0) -gt 104857600 ]; then
                echo "[$(date '+%H:%M:%S')] CHUNKING: $f exceeds 100MB, splitting..."
                # Move to Downloads for chunking, remove from repo
                mv "$f" /mnt/c/Users/Aidor/Downloads/
                git rm --cached "$f"
                # Chunk it in Downloads (WSL path to Windows)
                cd /mnt/c/Users/Aidor/Downloads && split -b 99m "$f" "history_chunk_"
                cd /home/idor/oe-local
            fi
        done

        # SAFETY GATE 2: Method body integrity
        STAGED=$(git diff --cached --name-only | head -1)
        if [ -n "$STAGED" ] && [ -f "$STAGED" ]; then
            METHOD_LOSS=0
            while IFS= read -r method; do
                CURRENT_LINES=$(sed -n "/def ${method}/,/def /p" "$STAGED" 2>/dev/null | wc -l)
                LAST_LINES=$(git show HEAD:"$STAGED" 2>/dev/null | sed -n "/def ${method}/,/def /p" | wc -l)
                if [ "$LAST_LINES" -gt 10 ] && [ "$CURRENT_LINES" -lt $((LAST_LINES / 10)) ]; then
                    echo "[$(date '+%H:%M:%S')] WARNING: ${method}() dropped from ${LAST_LINES} to ${CURRENT_LINES} lines. Refusing to commit."
                    METHOD_LOSS=1
                fi
            done < <(grep -oP "def \\K\\w+" "$STAGED" 2>/dev/null)
            if [ "$METHOD_LOSS" -eq 1 ]; then
                sleep 30
                continue
            fi
        fi

        # Commit with timestamp
        git commit -m "auto: $(git diff --cached --stat | tail -1) files changed at $(date '+%Y-%m-%d %H:%M:%S')"

        # FIXED PUSH GATE
        LOCAL_COMMITS=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)
        if [ "$LOCAL_COMMITS" -gt 0 ]; then
            git push origin main 2>&1 && echo "[$(date '+%H:%M:%S')] Pushed ${LOCAL_COMMITS} commits"
        else
            echo "[$(date '+%H:%M:%S')] No local commits ahead of remote"
        fi
    fi

    # Check for unpushed commits even if nothing new to stage
    LOCAL_COMMITS=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)
    if [ "$LOCAL_COMMITS" -gt 0 ]; then
        git push origin main 2>&1 && echo "[$(date '+%H:%M:%S')] Pushed ${LOCAL_COMMITS} unpushed commits"
    fi

    sleep 30
done
