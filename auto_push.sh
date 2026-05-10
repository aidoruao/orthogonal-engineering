#!/bin/bash
cd /home/idor/oe-local

while true; do
    # Pull remote changes first (with rebase to avoid merge conflicts)
    git pull --rebase origin main 2>/dev/null
    
    # Check if there's anything to commit
    if [[ -n $(git status --porcelain) ]]; then
        # Stage everything
        git add -A
        
        # Commit with timestamp
        git commit -m "auto: $(git diff --cached --stat | tail -1) files changed at $(date '+%Y-%m-%d %H:%M:%S')"
        
        # SAFETY GATE: Never lose local work to remote
        # If local yeshua_agent.py is larger than remote, force local
        LOCAL_LINES=$(wc -l < yeshua_agent.py 2>/dev/null || echo 0)
        REMOTE_LINES=$(git show origin/main:yeshua_agent.py 2>/dev/null | wc -l || echo 0)
        
        if [ "$LOCAL_LINES" -gt "$REMOTE_LINES" ]; then
            # Local has more content — push with force to protect additions
            git push --force-with-lease origin main 2>/dev/null && echo "[$(date '+%H:%M:%S')] Pushed (local: ${LOCAL_LINES} lines > remote: ${REMOTE_LINES})"
        elif [ "$LOCAL_LINES" -eq "$REMOTE_LINES" ]; then
            # Same size — normal push
            git push origin main 2>/dev/null && echo "[$(date '+%H:%M:%S')] Pushed (${LOCAL_LINES} lines)"
        else
            # Remote has more — WARNING, don't lose remote work
            echo "[$(date '+%H:%M:%S')] WARNING: Remote has more lines (${REMOTE_LINES}) than local (${LOCAL_LINES}). Pulling."
            git pull --rebase origin main
            git push origin main 2>/dev/null
        fi
    fi
    
    sleep 30
done
