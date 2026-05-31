#!/bin/bash
cd /home/idor/oe-local

while true; do
    git pull --rebase origin main 2>/dev/null
    if [[ -n $(git status --porcelain) ]]; then
        python3 tools/yaa_log_sanitizer.py 2>/dev/null
        git add -A
        git commit -m "auto: $(git diff --cached --stat | tail -1) files changed at $(date +%Y-%m-%d %H:%M:%S)"
        LOCAL_COMMITS=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)
        if [ "$LOCAL_COMMITS" -gt 0 ]; then
            git push origin main 2>&1 && echo "[$(date +%H:%M:%S)] Pushed ${LOCAL_COMMITS} commits"
        fi
    fi
    LOCAL_COMMITS=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)
    if [ "$LOCAL_COMMITS" -gt 0 ]; then
        git push origin main 2>&1 && echo "[$(date +%H:%M:%S)] Pushed ${LOCAL_COMMITS} unpushed commits"
    fi
    sleep 30
done
