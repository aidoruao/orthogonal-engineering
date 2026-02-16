# IDE AI Runner Template (PowerShell)
# 
# This template demonstrates how to use the CAS CLI for IDE AI workflows.
# Follows safety-first principles: dry-run default, mandatory backups, no auto-push.

# Configuration
$DRY_RUN = $true  # ALWAYS start with dry-run
# NOTE: Update this vault path to match your local environment
$VAULT_PATH = "C:\Users\Aidor\Downloads\ai_exports"  # Example local-only vault
$BACKUP_DIR = ".\backups"
$OUTPUT_DIR = ".\output"

Write-Host "=" * 60
Write-Host "IDE AI Runner (PowerShell Template)"
Write-Host "=" * 60

# Check if running in dry-run mode
if ($DRY_RUN) {
    Write-Host "MODE: DRY-RUN (safe, no modifications)" -ForegroundColor Green
} else {
    Write-Host "MODE: LIVE (WARNING: will modify files)" -ForegroundColor Red
    $confirm = Read-Host "Are you sure you want to proceed in LIVE mode? (yes/no)"
    if ($confirm -ne "yes") {
        Write-Host "Operation cancelled" -ForegroundColor Yellow
        exit 0
    }
}

# Example files to process (adjust as needed)
$sourceFiles = @(
    "example_file1.txt",
    "example_file2.py"
)

Write-Host ""
Write-Host "Step 1: Checking files..." -ForegroundColor Cyan

# Filter to existing files
$existingFiles = $sourceFiles | Where-Object { Test-Path $_ }

if ($existingFiles.Count -eq 0) {
    Write-Host "ERROR: No files found to process" -ForegroundColor Red
    exit 1
}

Write-Host "Found $($existingFiles.Count) files to process"

# Step 2: Create manifest
Write-Host ""
Write-Host "Step 2: Creating manifest..." -ForegroundColor Cyan

$manifestPath = "manifests\ide_ai_session_manifest.json"
New-Item -ItemType Directory -Force -Path (Split-Path $manifestPath) | Out-Null

$manifestCmd = "python cli.py manifest create"
foreach ($file in $existingFiles) {
    $manifestCmd += " `"$file`""
}
$manifestCmd += " --name ide_ai_session --output `"$manifestPath`""

Write-Host "Command: $manifestCmd"
Invoke-Expression $manifestCmd

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Manifest creation failed" -ForegroundColor Red
    exit 1
}

# Step 3: Hash files for verification
Write-Host ""
Write-Host "Step 3: Computing hashes..." -ForegroundColor Cyan

foreach ($file in $existingFiles) {
    python cli.py hash "$file"
}

# Step 4: Process files
Write-Host ""
Write-Host "Step 4: Processing files..." -ForegroundColor Cyan

$processCmd = "python cli.py process"
foreach ($file in $existingFiles) {
    $processCmd += " `"$file`""
}

if ($DRY_RUN) {
    $processCmd += " --dry-run"
} else {
    $processCmd += " --live"
}

$processCmd += " --backup-dir `"$BACKUP_DIR`" --output-dir `"$OUTPUT_DIR`" --verbose"

Write-Host "Command: $processCmd"
Invoke-Expression $processCmd

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Processing failed" -ForegroundColor Red
    exit 1
}

# Step 5: Verify manifest
Write-Host ""
Write-Host "Step 5: Verifying manifest..." -ForegroundColor Cyan

python cli.py manifest verify --manifest "$manifestPath" --verbose

if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Manifest verification failed" -ForegroundColor Yellow
} else {
    Write-Host "Manifest verification PASSED" -ForegroundColor Green
}

# Step 6: List backups (if in live mode)
if (-not $DRY_RUN) {
    Write-Host ""
    Write-Host "Step 6: Listing backups..." -ForegroundColor Cyan
    python cli.py backup list
}

# Summary
Write-Host ""
Write-Host "=" * 60
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  Mode: $(if ($DRY_RUN) { 'DRY-RUN' } else { 'LIVE' })"
Write-Host "  Files processed: $($existingFiles.Count)"
Write-Host "  Manifest: $manifestPath"
Write-Host "  Vault path: $VAULT_PATH"

if ($DRY_RUN) {
    Write-Host ""
    Write-Host "To run in LIVE mode:" -ForegroundColor Yellow
    Write-Host "  1. Review the dry-run results above"
    Write-Host "  2. Set `$DRY_RUN = `$false in this script"
    Write-Host "  3. Re-run this script"
    Write-Host "  WARNING: Live mode creates backups and modifies files"
}

Write-Host "=" * 60

# Exit with success
exit 0
