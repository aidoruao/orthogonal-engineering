#!/bin/bash
cd /home/idor/oe-local

while true; do
    # Pull remote changes first (with rebase to avoid merge conflicts)
    git pull --rebase origin main 2>/dev/null

    # Check if there's anything to commit
    if [[ -n $(git status --porcelain) ]]; then
        # Sanitize terminal logs before staging
        python3 tools/yaa_log_sanitizer.py 2>/dev/null
        
        # Stage everything
        git add -A

        # SAFETY GATE 2: Method body integrity — combinatorial
        # Compare every method body against git history
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

        # SAFETY GATE 1: Never lose local work to remote
        LOCAL_LINES=$(wc -l < yeshua_agent.py 2>/dev/null || echo 0)
        REMOTE_LINES=$(git show origin/main:yeshua_agent.py 2>/dev/null | wc -l || echo 0)

        if [ "$LOCAL_LINES" -gt "$REMOTE_LINES" ]; then
            git push --force-with-lease origin main 2>/dev/null && echo "[$(date '+%H:%M:%S')] Pushed (local: ${LOCAL_LINES} lines > remote: ${REMOTE_LINES})"
        elif [ "$LOCAL_LINES" -eq "$REMOTE_LINES" ]; then
            git push origin main 2>/dev/null && echo "[$(date '+%H:%M:%S')] Pushed (${LOCAL_LINES} lines)"
        else
            echo "[$(date '+%H:%M:%S')] WARNING: Remote has more lines (${REMOTE_LINES}) than local (${LOCAL_LINES}). Pulling."
            git pull --rebase origin main
            git push origin main 2>/dev/null
        fi
    fi

    sleep 30
done
