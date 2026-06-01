#!/bin/bash
cd /home/idor/oe-local || { echo "FATAL: cannot cd to oe-local"; exit 1; }

# ── CONFIG ──
SLEEP_SECONDS=300          # 5 minutes between checks
MAX_FILE_MB=99             # GitHub GH001 limit
NO_PUSH_FLAG=".no_push"    # touch this file to pause auto-pusher
LOGDIR="logs"
LOGFILE="$LOGDIR/auto_push_$(date +%Y%m%d_%H%M%S).log"

mkdir -p "$LOGDIR"
exec 1> >(tee -a "$LOGFILE") 2> >(tee -a "$LOGFILE" >&2)

log_info()  { echo "[$(date '+%H:%M:%S')] INFO:  $*"; }
log_warn()  { echo "[$(date '+%H:%M:%S')] WARN:  $*"; }
log_error() { echo "[$(date '+%H:%M:%S')] ERROR: $*"; }

log_info "Auto-pusher started. Interval: ${SLEEP_SECONDS}s. Log: $LOGFILE"

while true; do
    log_info "=== Starting cycle ==="

    # ── KILL SWITCH ──
    if [ -f "$NO_PUSH_FLAG" ]; then
        log_warn "PAUSED: $NO_PUSH_FLAG exists. Remove to resume."
        sleep 60
        continue
    fi

    # ── PULL FIRST (always) ──
    log_info "Pulling from origin..."
    if ! git pull --rebase origin main 2>/dev/null; then
        log_error "git pull FAILED. Rebase may be stuck. Aborting and retrying."
        git rebase --abort 2>/dev/null
        git fetch origin main 2>/dev/null
        git reset --soft origin/main 2>/dev/null
        log_warn "Reset to origin/main. Local changes preserved as staged."
    fi

    # ── CHECK IF ANYTHING TO COMMIT ──
    if [ -z "$(git status --porcelain)" ]; then
        log_info "Nothing to commit. Sleeping ${SLEEP_SECONDS}s."
        sleep $SLEEP_SECONDS
        continue
    fi

    # ── FILE SIZE GATE ──
    OVERSIZED=$(find . -maxdepth 1 -not -path '*/.*' -size +${MAX_FILE_MB}M -type f 2>/dev/null)
    if [ -n "$OVERSIZED" ]; then
        log_error "OVERSIZED FILES detected (>${MAX_FILE_MB}MB):"
        echo "$OVERSIZED" | while read -r f; do
            log_error "  $f ($(du -h "$f" | cut -f1))"
            # Auto-chunk to Downloads
            BASENAME=$(basename "$f")
            split -b ${MAX_FILE_MB}M --numeric-suffixes "$f" "$HOME/Downloads/${BASENAME}_chunk_"
            rm "$f"
            echo "$BASENAME" >> .gitignore
            log_info "Chunked $BASENAME to ~/Downloads/"
        done
        git add .gitignore
    fi

    # ── SANITIZE LOGS ──
    python3 tools/yaa_log_sanitizer.py 2>/dev/null

    # ── STAGE ──
    git add -A

    # ── METHOD-BODY INTEGRITY GATE ──
    STAGED=$(git diff --cached --name-only | grep '\.py$' | head -1)
    if [ -n "$STAGED" ] && [ -f "$STAGED" ]; then
        METHOD_LOSS=0
        while IFS= read -r method; do
            CURRENT_LINES=$(sed -n "/def ${method}/,/def /p" "$STAGED" 2>/dev/null | wc -l)
            LAST_LINES=$(git show HEAD:"$STAGED" 2>/dev/null | sed -n "/def ${method}/,/def /p" | wc -l)
            if [ "$LAST_LINES" -gt 10 ] && [ "$CURRENT_LINES" -lt $((LAST_LINES / 10)) ]; then
                log_warn "${method}() dropped from ${LAST_LINES} to ${CURRENT_LINES} lines. Refusing to commit."
                METHOD_LOSS=1
            fi
        done < <(grep -oP "def \\K\\w+" "$STAGED" 2>/dev/null)
        if [ "$METHOD_LOSS" -eq 1 ]; then
            log_error "Method integrity check FAILED. Resetting staged changes."
            git reset HEAD
            sleep $SLEEP_SECONDS
            continue
        fi
    fi

    # ── COMMIT ──
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    filecount=$(git status --porcelain | wc -l)
    git commit -m "auto: $filecount files changed at $timestamp"

    # ── PUSH ──
    LOCAL_COMMITS=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)
    if [ "$LOCAL_COMMITS" -gt 0 ]; then
        if git push origin main 2>/dev/null; then
            log_info "Pushed $LOCAL_COMMITS commits."
        else
            log_error "Push failed. Will retry on next cycle."
        fi
    fi

    log_info "=== Cycle complete. Sleeping ${SLEEP_SECONDS}s ==="
    sleep $SLEEP_SECONDS
done
