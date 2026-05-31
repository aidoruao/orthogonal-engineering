#!/bin/bash
cd /home/idor/oe-local

while true; do
    # Pull remote changes first
    git pull --rebase origin main 2>/dev/null

    # Check if there's anything to commit
    if [[ -n $(git status --porcelain) ]]; then
        # Sanitize terminal logs before staging
        python3 tools/yaa_log_sanitizer.py 2>/dev/null

        # SAFETY GATE 3: Detect oversized files before staging
        find . -maxdepth 1 -not -path '*/.*' -size +99M | while read f; do
            if [ -n "$f" ]; then
                echo "[$(date '+%H:%M:%S')] CHUNKING: $f exceeds 99MB, splitting..."
                mv "$f" /mnt/c/Users/Aidor/Downloads/
                split -b 99M /mnt/c/Users/Aidor/Downloads/$(basename "$f") /mnt/c/Users/Aidor/Downloads/history_chunk_
                echo "$(basename "$f")" >> .gitignore
                echo "history_chunk_*" >> .gitignore
            fi
        done

        # Stage everything
        git add -A

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
            git push origin main 2>&1 > /tmp/push.log
            if grep -q "GH001" /tmp/push.log; then
                echo "[$(date '+%H:%M:%S')] RCS-FILE-SIZE-VIOLATION detected. Triggering Soft-Reset Re-sync..."
                git reset --soft origin/main
                sleep 30
                continue
            fi
            echo "[$(date '+%H:%M:%S')] Pushed ${LOCAL_COMMITS} commits"
        else
            echo "[$(date '+%H:%M:%S')] No local commits ahead of remote"
        fi
    fi

    # Check for unpushed commits
    LOCAL_COMMITS=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)
    if [ "$LOCAL_COMMITS" -gt 0 ]; then
        git push origin main 2>&1 > /tmp/push.log
        if grep -q "GH001" /tmp/push.log; then
            echo "[$(date '+%H:%M:%S')] RCS-FILE-SIZE-VIOLATION in unpushed commits. Triggering Soft-Reset..."
            git reset --soft origin/main
        else
            echo "[$(date '+%H:%M:%S')] Pushed ${LOCAL_COMMITS} unpushed commits"
        fi
    fi

    sleep 30
done
