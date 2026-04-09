# Session Log Truncation Report

## Affected File
`Kimi Code CLI na.txt` (commit 3391157)

## Symptom
The beginning of the session transcript is missing. The commit message
states: "ENTIRE BEGINNING HALF OF SESSION TRUNCATED FOR SOME REASON"

## Root Cause Analysis

Terminal emulators (GNOME Terminal, Windows Terminal, etc.) maintain a
**scrollback buffer** with a finite line limit (typically 1,000-10,000
lines). When a Kimi CLI session produces output exceeding this limit,
the oldest lines are discarded from the buffer.

When the user performs Ctrl+A (select all) → Ctrl+C (copy) at session
end, only the lines still in the scrollback buffer are captured.

## Prevention

### Option A: Increase scrollback buffer
```bash
# GNOME Terminal: Edit → Preferences → Profiles → Scrolling
# Set to "Unlimited" or 100,000 lines

# Windows Terminal: settings.json
# "historySize": 100000
```

### Option B: Use `script` command (recommended)
```bash
# Wrap Kimi CLI in script to capture ALL output
script -q "session_$(date +%Y%m%d_%H%M%S).txt" kimi
# This captures everything from the start, regardless of scrollback
```

### Option C: Use `tee`
```bash
kimi 2>&1 | tee "session_$(date +%Y%m%d_%H%M%S).txt"
# Note: may interfere with Kimi's interactive features
```

### Option D: Kimi CLI built-in (if available)
Check if Kimi CLI has a `--log` or `--transcript` flag.

## Recommendation
Use Option B (`script` command) for all future sessions. Add to
shell profile:
```bash
alias kimi-logged='script -q "$HOME/orthogonal-engineering/session_$(date +%Y%m%d_%H%M%S).txt" kimi'
```
