#!/bin/bash
# GENERATED_BY: 2a_kimi_5-31-26
# DATE: 2026-05-31
# PURPOSE: Auto-pusher — COMMIT FIRST, then pull, then push

cd /home/idor/oe-local || { echo "FATAL: cannot cd to oe-local"; exit 1; }

mkdir -p logs
LOGFILE="logs/auto_push_$(date +%Y%m%d_%H%M%S).log"
exec 1> >(tee -a "$LOGFILE") 2> >(tee -a "$LOGFILE" >&2)

SLEEP_SECONDS=30
NO_PUSH_FLAG=".no_push"

log_info()  { echo "[$(date '+%H:%M:%S')] INFO:  $*"; }
log_warn()  { echo "[$(date '+%H:%M:%S')] WARN:  $*"; }
log_error() { echo "[$(date '+%H:%M:%S')] ERROR: $*"; }

log_info "Auto-pusher started. Interval: ${SLEEP_SECONDS}s. Log: $LOGFILE"

while true; do
    log_info "=== Starting cycle ==="

    if [ -f "$NO_PUSH_FLAG" ]; then
        log_warn "PAUSED: $NO_PUSH_FLAG exists"
        sleep 60
        continue
    fi

    # --- STEP 1: CHECK FOR LOCAL CHANGES ---
    CHANGED=$(git status --porcelain)
    if [ -n "$CHANGED" ]; then
        log_info "Local changes detected:"
        echo "$CHANGED" | while read line; do log_info "  $line"; done

        # Validate before staging
        > /tmp/corruption_flag.txt
        echo "$CHANGED" | awk '{print $2}' | while read f; do
            [ -f "$f" ] || continue
            if [[ "$f" == *.md ]]; then
                COUNT=$(grep -c '```' "$f" 2>/dev/null || echo 0)
                if [ $((COUNT % 2)) -ne 0 ]; then
                    log_error "CORRUPTION: $f unclosed markdown ($COUNT backticks)"
                    echo "1" >> /tmp/corruption_flag.txt
                fi
            fi
            if [[ "$f" == *.py ]]; then
                if ! python3 -m py_compile "$f" 2>/dev/null; then
                    log_error "CORRUPTION: $f Python syntax error"
                    echo "1" >> /tmp/corruption_flag.txt
                fi
            fi
        done

        if [ -s /tmp/corruption_flag.txt ]; then
            log_error "COMMIT ABORTED: fix in Terminal 2"
            sleep $SLEEP_SECONDS
            continue
        fi

        # Stage and commit LOCAL changes first
        git add -A
        MSG="auto: $(git diff --cached --stat | tail -1) files changed at $(date '+%Y-%m-%d %H:%M:%S')"
        if git commit -m "$MSG" >/dev/null 2>&1; then
            log_info "Local commit OK: $MSG"
        else
            log_error "Local commit failed"
            sleep $SLEEP_SECONDS
            continue
        fi
    fi

    # --- STEP 2: PULL REMOTE CHANGES (now working tree is clean) ---
    if ! git pull --rebase origin main >/dev/null 2>&1; then
        log_error "git pull FAILED. Causes:"
        log_error "  - Network down"
        log_error "  - Remote history rewritten"
        log_error "  - Merge conflicts (manual fix needed in Terminal 2)"
        sleep $SLEEP_SECONDS
        continue
    fi
    log_info "git pull OK"

    # --- STEP 3: PUSH ---
    LOCAL=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)
    if [ "$LOCAL" -gt 0 ]; then
        if git push origin main >/dev/null 2>&1; then
            log_info "SUCCESS: Pushed ${LOCAL} commits"
        else
            log_error "git push FAILED. Will retry next cycle."
        fi
    else
        log_info "No local commits to push"
    fi

    log_info "=== Cycle complete. Sleeping ${SLEEP_SECONDS}s ==="
    sleep $SLEEP_SECONDS
done
