#!/usr/bin/env bash
# Forensic commit hook — generates forensic JSON and prints trailer.
# Usage: install as post-commit hook or run manually.
#
# Example:
#   bash scripts/forensic-commit-hook.sh --files file1.txt file2.txt

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

FILES=()
AI_CREDIT=""
THRESHOLD_CONFIG=""
THRESHOLD_OVERRIDES=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --files)
            shift
            while [[ $# -gt 0 && ! "$1" =~ ^-- ]]; do
                FILES+=("$1")
                shift
            done
            ;;
        --ai-credit)
            AI_CREDIT="$2"
            shift 2
            ;;
        --threshold-config)
            THRESHOLD_CONFIG="$2"
            shift 2
            ;;
        --threshold)
            THRESHOLD_OVERRIDES+=("$2")
            shift 2
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

COMMIT_SHA=$(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null || echo "UNKNOWN")
AUTHOR=$(git -C "$REPO_ROOT" log -1 --pretty=format:'%an <%ae>' 2>/dev/null || echo "unknown")

# Build metadata JSON
METADATA=$(jq -n \
    --arg sha "$COMMIT_SHA" \
    --arg author "$AUTHOR" \
    --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    '{commit_sha: $sha, authors: [$author], timestamp: $ts, co_authors: []}')

# Build artifacts JSON
ARTIFACTS="[]"
for f in "${FILES[@]}"; do
    if [[ -f "$f" ]]; then
        ABS_PATH=$(realpath "$f")
        SIZE=$(stat -c%s "$f" 2>/dev/null || stat -f%z "$f" 2>/dev/null || echo 0)
        ARTIFACTS=$(echo "$ARTIFACTS" | jq --arg path "$ABS_PATH" --argjson size "$SIZE" '. + [{path: $path, size: $size}]')
    fi
done

# Run Python forensic commit builder
python3 -m audit.forensic_commit --prepare \
    --metadata "$METADATA" \
    --artifacts "$ARTIFACTS" \
    --dest-dir "$REPO_ROOT/audit/forensic_commits" \
    ${THRESHOLD_CONFIG:+--threshold-config "$THRESHOLD_CONFIG"} \
    ${THRESHOLD_OVERRIDES:+"${THRESHOLD_OVERRIDES[@]/#/--threshold }"}

# Print trailer for copy-paste into commit message
python3 -m audit.forensic_commit --print-trailer \
    --commit-sha "$COMMIT_SHA" \
    --dest-dir "$REPO_ROOT/audit/forensic_commits"
