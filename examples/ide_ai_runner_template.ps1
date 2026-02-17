# IDE AI Runner Template (PowerShell)
# Example script for running deterministic pipeline operations
# 
# IMPORTANT: This is a TEMPLATE. Customize paths and parameters for your use.
# 
# Usage: .\ide_ai_runner_template.ps1

# Configuration
$REPO_PATH = "C:\path\to\your\repository"
$VAULT_PATH = "C:\Users\YourName\Downloads\your_vault"  # NOT the example path!
$OUTPUT_DIR = ".\pipeline_output"

# Create output directory
New-Item -ItemType Directory -Force -Path $OUTPUT_DIR | Out-Null

Write-Host "Deterministic Pipeline Runner" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green
Write-Host ""

# Step 1: Index Repository (Dry-Run First)
Write-Host "[1/5] Indexing repository (dry-run)..." -ForegroundColor Cyan
python cli.py index --repo $REPO_PATH --out "$OUTPUT_DIR\manifest.jsonl"

Write-Host ""
Read-Host "Review the output above. Press Enter to continue with actual indexing, or Ctrl+C to abort"

# Step 2: Index Repository (Apply)
Write-Host "[2/5] Indexing repository (apply)..." -ForegroundColor Cyan
python cli.py index --repo $REPO_PATH --out "$OUTPUT_DIR\manifest.jsonl" --apply

# Step 3: Build Merkle Tree
Write-Host "[3/5] Building Merkle tree..." -ForegroundColor Cyan
python cli.py merkle --manifest "$OUTPUT_DIR\manifest.jsonl" --apply

# Step 4: Verify Proofs
Write-Host "[4/5] Verifying Merkle proofs..." -ForegroundColor Cyan
python cli.py verify --manifest "$OUTPUT_DIR\merkle_proofs.jsonl"

# Step 5: Finalize Vault (if vault exists)
if (Test-Path $VAULT_PATH) {
    Write-Host "[5/5] Finalizing vault..." -ForegroundColor Cyan
    python core\alpha_omega_finalizer.py --vault-dir $VAULT_PATH --apply
} else {
    Write-Host "[5/5] Vault path does not exist, skipping finalization" -ForegroundColor Yellow
    Write-Host "      Vault path: $VAULT_PATH" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Pipeline execution complete!" -ForegroundColor Green
Write-Host "Outputs in: $OUTPUT_DIR" -ForegroundColor Green
Write-Host "Logs in: .\logs\" -ForegroundColor Green
Write-Host ""

# Display summary
Write-Host "Summary:" -ForegroundColor Cyan
if (Test-Path "$OUTPUT_DIR\manifest.jsonl") {
    $manifest_lines = (Get-Content "$OUTPUT_DIR\manifest.jsonl" | Measure-Object -Line).Lines
    Write-Host "  Manifest entries: $manifest_lines" -ForegroundColor White
}
if (Test-Path "$OUTPUT_DIR\merkle_proofs.jsonl") {
    $proof_lines = (Get-Content "$OUTPUT_DIR\merkle_proofs.jsonl" | Measure-Object -Line).Lines
    Write-Host "  Merkle proofs: $proof_lines" -ForegroundColor White
}

Write-Host ""
Write-Host "Review logs in .\logs\ for detailed operation history" -ForegroundColor Cyan
