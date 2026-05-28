#!/bin/bash
# YAA Watchdog — detects when steward is operating manually
# Source in ~/.bashrc: source ~/oe-local/tools/yaa_watchdog.sh

export YAA_BYPASS_COUNT=0
export YAA_MAX_BYPASS=10

preexec() {
    YAA_TRIGGERS="^(grep|sed|awk|find|lake|python3|git grep|curl|lean|cat|head|tail|wc)\b"
    if echo "$1" | grep -qE "$YAA_TRIGGERS"; then
        if echo "$1" | grep -q "yaa"; then
            export YAA_BYPASS_COUNT=0
            return
        fi
        export YAA_BYPASS_COUNT=$((YAA_BYPASS_COUNT + 1))
        if [ "$YAA_BYPASS_COUNT" -eq 3 ]; then
            echo "⚠️  YAA: $YAA_BYPASS_COUNT manual commands. Try 'yaa query' or 'yaa audit'."
        elif [ "$YAA_BYPASS_COUNT" -ge 10 ]; then
            echo "🛑 YAA: $YAA_BYPASS_COUNT manual commands. Run 'yaa reset' to continue."
        fi
    fi
}

yaa() {
    export YAA_BYPASS_COUNT=0
    case "$1" in
        query) python3 ~/oe-local/yeshua_agent.py --query "$2" 2>/dev/null || echo "YAA query failed." ;;
        audit) python3 ~/oe-local/yeshua_agent.py --audit 2>/dev/null || echo "YAA audit failed." ;;
        repair) python3 ~/oe-local/tools/repair_loop.py --execute 2>/dev/null || echo "YAA repair failed." ;;
        scan) python3 ~/oe-local/tools/yeshua_scanner.py 2>/dev/null || echo "YAA scan failed." ;;
        dashboard) bash ~/oe-local/tools/yaa_dashboard.sh ;;
        reset) export YAA_BYPASS_COUNT=0; echo "YAA bypass counter reset." ;;
        logs) python3 ~/oe-local/tools/yaa_log_audit.py summary 2>/dev/null || echo "No logs yet." ;;
        log-errors) python3 ~/oe-local/tools/yaa_log_audit.py errors 2>/dev/null ;;
        log-search) python3 ~/oe-local/tools/yaa_log_audit.py search "$2" 2>/dev/null ;;
        *) echo "YAA: query | audit | repair | scan | dashboard | reset | logs | log-errors | log-search <pattern>" ;;
    esac
}

echo "🛡️  YAA Watchdog active. $(date '+%H:%M:%S')"
