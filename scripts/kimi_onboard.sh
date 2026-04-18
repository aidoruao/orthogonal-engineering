#!/usr/bin/env bash
# KIMI Onboarding Script
# ======================
# Validates environment, creates threshold config from template,
# optionally installs git hooks, and runs a verification smoke-test.
#
# Usage: bash scripts/kimi_onboard.sh [--install-hooks]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

INSTALL_HOOKS=false
if [[ "${1:-}" == "--install-hooks" ]]; then
    INSTALL_HOOKS=true
fi

echo "========================================"
echo "  KIMI Onboarding for Orthogonal Engineering"
echo "  Agent ID: 597e0d23-f404-4bdf-801f-64962ce0e722"
echo "========================================"
echo

# 1. Validate Python
echo "[1/5] Validating Python environment..."
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found in PATH" >&2
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "  ✓ $PYTHON_VERSION"

# 2. Validate dependencies
echo "[2/5] Validating dependencies..."
python3 -c "import yaml, jsonschema" 2>/dev/null || {
    echo "  Installing dependencies..."
    pip install pyyaml jsonschema >/dev/null 2>&1 || true
}
echo "  ✓ Dependencies OK"

# 3. Create threshold config from template if missing
echo "[3/5] Checking threshold config..."
THRESHOLD_CONFIG="$REPO_ROOT/config/thresholds.yaml"
if [[ -f "$THRESHOLD_CONFIG" ]]; then
    echo "  ✓ Threshold config exists: $THRESHOLD_CONFIG"
else
    echo "  Creating default threshold config..."
    mkdir -p "$(dirname "$THRESHOLD_CONFIG")"
    cat > "$THRESHOLD_CONFIG" << 'EOF'
certain: "247/1"
high_confidence: "200/1"
probable: "150/1"
unknown: "100/1"
suspicious: "50/1"
invalid: "0/1"
EOF
    echo "  ✓ Created: $THRESHOLD_CONFIG"
fi

# 4. Optionally install git hooks
echo "[4/5] Git hooks..."
if [[ "$INSTALL_HOOKS" == true ]]; then
    HOOK_DIR="$REPO_ROOT/.git/hooks"
    if [[ -d "$HOOK_DIR" ]]; then
        cp "$REPO_ROOT/scripts/forensic-commit-hook.sh" "$HOOK_DIR/post-commit"
        chmod +x "$HOOK_DIR/post-commit"
        echo "  ✓ Installed post-commit hook"
    else
        echo "  ⚠ No .git/hooks directory found; skipping hook installation"
    fi
else
    echo "  (Skipped; use --install-hooks to enable)"
fi

# 5. Smoke test
echo "[5/5] Running smoke tests..."
cd "$REPO_ROOT"
PYTEST="python3 -m pytest"
if [[ -f "$REPO_ROOT/.venv/bin/python" ]]; then
    PYTEST="$REPO_ROOT/.venv/bin/python -m pytest"
fi
$PYTEST tests/test_state_classification.py tests/test_threshold_loading.py tests/test_forensic_commit.py tests/test_verification_testimony.py tests/test_ai_credit.py -q || {
    echo "  ✗ Smoke tests failed" >&2
    exit 1
}
echo "  ✓ Smoke tests passed"

echo
echo "========================================"
echo "  Onboarding Complete"
echo "========================================"
echo
echo "Next steps:"
echo "  1. Review config/thresholds.yaml and adjust thresholds if needed."
echo "  2. Run classification: python3 cli.py classify --path <file> --checksum <sha256> --score <rational>"
echo "  3. Run forensic commit: python3 cli.py forensic-commit --files <files...>"
echo "  4. Read ONBOARDING_FOR_AI_AGENTS.md for the full AI_INTERACTION_CONTRACT."
echo "  5. Run all tests: python3 -m pytest tests/test_state_classification.py tests/test_threshold_loading.py tests/test_forensic_commit.py tests/test_verification_testimony.py tests/test_ai_credit.py -v"
echo
