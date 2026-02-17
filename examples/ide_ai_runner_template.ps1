# IDE AI Runner Template - PowerShell
# Orthogonal Engineering Deterministic Scaffold Automation
#
# Purpose: Non-destructive automation template for running the scaffold validation
# pipeline on Windows. Defaults to dry-run mode and produces a JSON report.
#
# Usage:
#   .\ide_ai_runner_template.ps1                    # Dry-run mode (default)
#   .\ide_ai_runner_template.ps1 -Apply $true       # Apply mode (requires explicit authorization)
#
# Version: 1.0
# Last Updated: 2026-02-16

param(
    [bool]$Apply = $false,
    [string]$RepoRoot = "C:\Users\Aidor\Documents\orthogonal-engineering-clean",
    [string]$HandlingMetaPath = "",
    [bool]$Verbose = $false
)

# Timestamp for this run
$RunTimestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
$ReportTimestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Output paths
$OutputDir = Join-Path $RepoRoot "outputs"
$BackupDir = Join-Path $RepoRoot "backups"
$ReportPath = Join-Path $OutputDir "ide_ai_run_report_$ReportTimestamp.json"

# Initialize report structure
$Report = @{
    run_timestamp = $RunTimestamp
    mode = if ($Apply) { "APPLY" } else { "DRY-RUN" }
    unit_tests_passed = $false
    manifest_hash = ""
    merkle_root = ""
    backup_created = ""
    handling_dry_run_report = ""
    manifest_reproducible = $false
    errors = @()
    warnings = @()
    steps_completed = @()
}

# Helper function for logging
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    $prefix = switch ($Level) {
        "ERROR"   { "[ERROR]" }
        "WARNING" { "[WARN]" }
        "SUCCESS" { "[OK]" }
        default   { "[INFO]" }
    }
    
    if ($Apply -and $Level -eq "INFO") {
        $prefix = "[APPLY] $prefix"
    } elseif (-not $Apply -and $Level -eq "INFO") {
        $prefix = "[DRY-RUN] $prefix"
    }
    
    Write-Host "$timestamp $prefix $Message"
    
    if ($Verbose) {
        $logEntry = @{
            timestamp = $RunTimestamp
            level = $Level
            message = $Message
        }
        # Could write to log file here if needed
    }
}

# Helper function to add error to report
function Add-Error {
    param([string]$Message)
    Write-Log $Message "ERROR"
    $Report.errors += $Message
}

# Helper function to add warning to report
function Add-Warning {
    param([string]$Message)
    Write-Log $Message "WARNING"
    $Report.warnings += $Message
}

# Helper function to mark step complete
function Complete-Step {
    param([string]$StepName)
    Write-Log "Completed: $StepName" "SUCCESS"
    $Report.steps_completed += $StepName
}

# Main execution
try {
    Write-Log "=== Orthogonal Engineering IDE AI Runner ==="
    Write-Log "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY-RUN' })"
    Write-Log "Repository: $RepoRoot"
    Write-Log ""

    # Verify repository exists
    if (-Not (Test-Path $RepoRoot)) {
        Add-Error "Repository not found: $RepoRoot"
        throw "Repository path does not exist"
    }

    # Navigate to repository
    Push-Location $RepoRoot

    # Create output directory
    if (-Not (Test-Path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
        Write-Log "Created output directory: $OutputDir"
    }

    # STEP 1: Verify/activate virtual environment
    Write-Log "Step 1: Virtual environment setup"
    
    $venvPath = Join-Path $RepoRoot "venv"
    $venvActivate = Join-Path $venvPath "Scripts\Activate.ps1"
    
    if (-Not (Test-Path $venvPath)) {
        Write-Log "Creating virtual environment..."
        python -m venv venv
        if ($LASTEXITCODE -ne 0) {
            Add-Error "Failed to create virtual environment"
            throw "venv creation failed"
        }
    }
    
    Write-Log "Activating virtual environment..."
    & $venvActivate
    
    Complete-Step "virtual_environment_setup"

    # STEP 2: Install dependencies
    Write-Log "Step 2: Installing dependencies"
    
    $requirementsPath = Join-Path $RepoRoot "requirements.txt"
    if (Test-Path $requirementsPath) {
        Write-Log "Installing from requirements.txt..."
        pip install -r $requirementsPath --quiet
        if ($LASTEXITCODE -ne 0) {
            Add-Warning "Some dependencies failed to install"
        } else {
            Complete-Step "dependencies_installed"
        }
    } else {
        Add-Warning "requirements.txt not found"
    }

    # STEP 3: Run unit tests
    Write-Log "Step 3: Running unit tests"
    
    $testDirs = @("tests", "toolkit\tests")
    $allTestsPassed = $true
    
    foreach ($testDir in $testDirs) {
        $testPath = Join-Path $RepoRoot $testDir
        if (Test-Path $testPath) {
            Write-Log "Running tests in $testDir..."
            python -m pytest $testPath -v --tb=short
            if ($LASTEXITCODE -ne 0) {
                Add-Warning "Some tests failed in $testDir"
                $allTestsPassed = $false
            }
        }
    }
    
    $Report.unit_tests_passed = $allTestsPassed
    Complete-Step "unit_tests"

    # STEP 4: Generate SHA256 manifest
    Write-Log "Step 4: Generating SHA256 manifest"
    
    $manifestScript = Join-Path $RepoRoot "automation\generate_sha256_manifest.py"
    if (Test-Path $manifestScript) {
        $manifestOutput = Join-Path $OutputDir "manifest_preview.json"
        
        Write-Log "Generating manifest to $manifestOutput..."
        python $manifestScript --output $manifestOutput
        
        if ($LASTEXITCODE -eq 0 -and (Test-Path $manifestOutput)) {
            # Calculate manifest hash
            $manifestContent = Get-Content $manifestOutput -Raw | ConvertFrom-Json
            $manifestJson = $manifestContent | ConvertTo-Json -Compress -Depth 100
            $manifestBytes = [System.Text.Encoding]::UTF8.GetBytes($manifestJson)
            $manifestHash = [System.BitConverter]::ToString(
                [System.Security.Cryptography.SHA256]::Create().ComputeHash($manifestBytes)
            ).Replace("-", "").ToLower()
            
            $Report.manifest_hash = $manifestHash
            Write-Log "Manifest hash: $manifestHash"
            Complete-Step "manifest_generation"
        } else {
            Add-Error "Manifest generation failed"
        }
    } else {
        Add-Warning "Manifest generation script not found: $manifestScript"
    }

    # STEP 5: Calculate Merkle root
    Write-Log "Step 5: Calculating Merkle root"
    
    $manifestOutput = Join-Path $OutputDir "manifest_preview.json"
    if (Test-Path $manifestOutput) {
        $merkleScript = @"
import hashlib
import json
from pathlib import Path

manifest_file = Path('$($manifestOutput.Replace('\', '\\'))')
with open(manifest_file) as f:
    data = json.load(f)

hashes = [entry['sha256'] for entry in data.get('files', [])]
combined = ''.join(sorted(hashes))
merkle_root = hashlib.sha256(combined.encode()).hexdigest()
print(merkle_root)
"@
        
        $merkleRoot = python -c $merkleScript
        if ($LASTEXITCODE -eq 0 -and $merkleRoot) {
            $Report.merkle_root = $merkleRoot.Trim()
            Write-Log "Merkle root: $($Report.merkle_root)"
            Complete-Step "merkle_root_calculation"
        } else {
            Add-Error "Merkle root calculation failed"
        }
    } else {
        Add-Warning "Manifest file not found, skipping merkle calculation"
    }

    # STEP 6: Test manifest reproducibility
    Write-Log "Step 6: Testing manifest reproducibility"
    
    if (Test-Path $manifestScript) {
        $manifestCheck = Join-Path $OutputDir "manifest_check.json"
        python $manifestScript --output $manifestCheck
        
        if ((Test-Path $manifestOutput) -and (Test-Path $manifestCheck)) {
            $hash1 = Get-FileHash $manifestOutput -Algorithm SHA256
            $hash2 = Get-FileHash $manifestCheck -Algorithm SHA256
            
            if ($hash1.Hash -eq $hash2.Hash) {
                Write-Log "Manifest reproducibility: PASS" "SUCCESS"
                $Report.manifest_reproducible = $true
            } else {
                Add-Warning "Manifest hashes differ - may indicate file changes during run"
                $Report.manifest_reproducible = $false
            }
            Complete-Step "manifest_reproducibility_check"
        }
    }

    # STEP 7: Run handling.meta dry-run (if path provided)
    Write-Log "Step 7: Running handling.meta clamp (dry-run)"
    
    if ($HandlingMetaPath -and (Test-Path $HandlingMetaPath)) {
        $testSubset = Join-Path $OutputDir "handling_test_subset"
        New-Item -ItemType Directory -Path $testSubset -Force | Out-Null
        
        # Copy sample files
        $sampleFiles = @(
            "toolkit\oe\cli.py",
            "toolkit\oe\evidence_store.py"
        )
        
        foreach ($file in $sampleFiles) {
            $srcPath = Join-Path $RepoRoot $file
            if (Test-Path $srcPath) {
                Copy-Item $srcPath -Destination $testSubset
            }
        }
        
        $handlingReport = Join-Path $OutputDir "handling_dry_run_report.json"
        
        Write-Log "Running handling.meta on test subset..."
        & $HandlingMetaPath clamp --dry-run --input $testSubset --output $handlingReport
        
        if (Test-Path $handlingReport) {
            $Report.handling_dry_run_report = $handlingReport
            Write-Log "handling.meta dry-run report: $handlingReport"
            Complete-Step "handling_meta_dry_run"
        } else {
            Add-Warning "handling.meta did not produce expected report"
        }
    } else {
        Write-Log "handling.meta path not provided or not found, creating mock report"
        
        $mockReport = @{
            operation = "clamp_dry_run"
            timestamp = $RunTimestamp
            files_analyzed = 0
            would_modify = 0
            issues_detected = 0
            status = "mock_dry_run"
            note = "handling.meta not available - this is a mock report"
        } | ConvertTo-Json
        
        $handlingReport = Join-Path $OutputDir "handling_dry_run_report.json"
        $mockReport | Out-File -FilePath $handlingReport
        $Report.handling_dry_run_report = $handlingReport
        
        Complete-Step "handling_meta_mock_report"
    }

    # STEP 8: Create backup (if apply mode)
    if ($Apply) {
        Write-Log "Step 8: Creating backup (APPLY mode)"
        
        $backupTimestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupPath = Join-Path $BackupDir "backup_$backupTimestamp"
        New-Item -ItemType Directory -Path $backupPath -Force | Out-Null
        
        $itemsToBackup = @(
            "toolkit",
            "automation",
            "documentation",
            "examples",
            "tests",
            "requirements.txt"
        )
        
        foreach ($item in $itemsToBackup) {
            $srcPath = Join-Path $RepoRoot $item
            if (Test-Path $srcPath) {
                Copy-Item -Path $srcPath -Destination $backupPath -Recurse -Force
                Write-Log "Backed up: $item"
            }
        }
        
        $Report.backup_created = $backupPath
        Write-Log "Backup created: $backupPath" "SUCCESS"
        Complete-Step "backup_creation"
    } else {
        Write-Log "Step 8: Backup (skipped in DRY-RUN mode)"
        $Report.backup_created = "N/A - dry-run mode"
    }

    # STEP 9: Apply operations (if apply mode)
    if ($Apply) {
        Write-Log "Step 9: Applying changes (APPLY mode)" "WARNING"
        Write-Log "WARNING: This will modify repository files!" "WARNING"
        
        # Example: Apply manifest generation
        if (Test-Path $manifestScript) {
            Write-Log "Applying manifest generation..."
            python $manifestScript --apply
            if ($LASTEXITCODE -eq 0) {
                Complete-Step "manifest_apply"
            } else {
                Add-Error "Manifest apply failed"
            }
        }
        
        # Add more apply operations here as needed
        
    } else {
        Write-Log "Step 9: Apply (skipped in DRY-RUN mode)"
    }

    # FINAL STEP: Generate report
    Write-Log ""
    Write-Log "=== Run Summary ==="
    Write-Log "Mode: $($Report.mode)"
    Write-Log "Unit tests passed: $($Report.unit_tests_passed)"
    Write-Log "Manifest hash: $($Report.manifest_hash)"
    Write-Log "Merkle root: $($Report.merkle_root)"
    Write-Log "Backup created: $($Report.backup_created)"
    Write-Log "Steps completed: $($Report.steps_completed.Count)"
    Write-Log "Errors: $($Report.errors.Count)"
    Write-Log "Warnings: $($Report.warnings.Count)"
    
    # Write JSON report
    $Report | ConvertTo-Json -Depth 10 | Out-File -FilePath $ReportPath
    Write-Log ""
    Write-Log "Report written to: $ReportPath" "SUCCESS"
    
    # Exit with appropriate code
    if ($Report.errors.Count -gt 0) {
        exit 1
    } else {
        exit 0
    }

} catch {
    Add-Error "Fatal error: $_"
    Write-Log "Stack trace: $($_.ScriptStackTrace)" "ERROR"
    
    # Write error report
    $Report | ConvertTo-Json -Depth 10 | Out-File -FilePath $ReportPath
    Write-Log "Error report written to: $ReportPath" "ERROR"
    
    exit 1
} finally {
    # Return to original location
    Pop-Location
}
# IDE AI Runner Template (PowerShell)
# 
# This template demonstrates a complete dry-run workflow for IDE AI systems.
# It runs the finalizer, executes tests, computes manifest hashes, and generates
# an AI run report.
#
# SAFETY: Default mode is DRY-RUN. Use -Apply switch to enable apply mode.

param(
    [string]$VaultDir = $null,  # User must specify vault directory
    [string]$OutDir = ".\outputs",
    [switch]$Apply
)

# If no vault directory specified, show usage
if (-not $VaultDir) {
    Write-Host "ERROR: --VaultDir parameter is required" -ForegroundColor Red
    Write-Host ""
    Write-Host "Usage: .\ide_ai_runner_template.ps1 -VaultDir <path_to_vault> [-OutDir <output_path>] [-Apply]"
    Write-Host ""
    Write-Host "Example:"
    Write-Host '  .\ide_ai_runner_template.ps1 -VaultDir "C:\Users\YourName\Downloads\ai_exports"'
    exit 1
}

# Initialize report
$report = @{
    run_timestamp = (Get-Date).ToUniversalTime().ToString("o")
    mode = if ($Apply) { "apply" } else { "dry-run" }
    vault_path = $VaultDir
    output_path = $OutDir
    results = @{}
    warnings = @()
    errors = @()
    next_steps = @()
}

Write-Host "======================================================================"
Write-Host "IDE AI RUNNER - AlphaOmegaFinalizer (PowerShell)"
Write-Host "======================================================================"
Write-Host "Timestamp: $($report.run_timestamp)"
Write-Host "Mode: $($report.mode.ToUpper())"
Write-Host "Vault: $VaultDir"
Write-Host "Output: $OutDir"
Write-Host "======================================================================"
Write-Host ""

# Helper function to run commands
function Invoke-CommandWithOutput {
    param(
        [string]$Description,
        [string[]]$Command
    )
    
    Write-Host ""
    Write-Host "======================================================================"
    Write-Host $Description
    Write-Host "======================================================================"
    Write-Host "Command: $($Command -join ' ')"
    Write-Host ""
    
    $output = & $Command[0] $Command[1..($Command.Length-1)] 2>&1
    Write-Host $output
    
    return @{
        Output = $output
        ExitCode = $LASTEXITCODE
    }
}

# Step 1: Run unit tests
Write-Host "Step 1: Running Unit Tests"
$testResult = Invoke-CommandWithOutput `
    -Description "Running pytest on AlphaOmegaFinalizer tests" `
    -Command @("python", "-m", "pytest", "core/tests/test_alpha_omega_finalizer.py", "-v")

$report.results['tests_passed'] = ($testResult.ExitCode -eq 0)

if ($testResult.ExitCode -ne 0) {
    $report.errors += "Unit tests failed"
    $report.next_steps += "Fix failing unit tests before proceeding"
}

# Step 2: Run finalizer
$finalizerCmd = @(
    "python",
    "core/alpha_omega_finalizer.py",
    "--vault-dir", $VaultDir,
    "--out-dir", $OutDir
)

if ($Apply) {
    $finalizerCmd += "--apply"
    $report.warnings += "Running in APPLY mode - files will be written"
} else {
    $report.warnings += "Running in DRY-RUN mode - no files will be written"
}

$finalizerResult = Invoke-CommandWithOutput `
    -Description "Step 2: Running AlphaOmegaFinalizer" `
    -Command $finalizerCmd

$report.results['finalization_success'] = ($finalizerResult.ExitCode -eq 0)

if ($finalizerResult.ExitCode -ne 0) {
    $report.errors += "Finalization failed"
    $report.next_steps += "Review finalization errors above"
}

# Extract Merkle root from output
if ($finalizerResult.ExitCode -eq 0) {
    $outputText = $finalizerResult.Output | Out-String
    if ($outputText -match "Merkle Root:\s*([a-f0-9]+)") {
        $report.results['merkle_root'] = $Matches[1]
    }
}

# Step 3: Compute manifest hash (if apply mode)
if ($Apply) {
    $ledgerPath = Join-Path $OutDir "finalization_ledger.json"
    $masterRootPath = Join-Path $OutDir "master_root.txt"
    
    if (Test-Path $ledgerPath) {
        $manifestHash = (Get-FileHash -Path $ledgerPath -Algorithm SHA256).Hash.ToLower()
        $report.results['manifest_hash'] = $manifestHash
        Write-Host ""
        Write-Host "Manifest Hash (SHA-256): $manifestHash"
    } else {
        $report.errors += "Ledger file not found after finalization"
    }
    
    if (Test-Path $masterRootPath) {
        $masterRoot = (Get-Content -Path $masterRootPath -Raw).Trim()
        $report.results['master_root_file'] = $masterRoot
        
        # Verify consistency
        if ($report.results.ContainsKey('merkle_root')) {
            if ($masterRoot -eq $report.results['merkle_root']) {
                Write-Host "✓ Master root file matches Merkle root"
                $report.results['root_consistency'] = $true
            } else {
                Write-Host "✗ Master root file does NOT match Merkle root"
                $report.errors += "Root consistency check failed"
                $report.results['root_consistency'] = $false
            }
        }
    }
}

# Step 4: Verify integrity (if apply mode)
if ($Apply) {
    $ledgerPath = Join-Path $OutDir "finalization_ledger.json"
    
    if (Test-Path $ledgerPath) {
        $verifyResult = Invoke-CommandWithOutput `
            -Description "Step 4: Verifying Integrity" `
            -Command @(
                "python",
                "core/alpha_omega_finalizer.py",
                "--vault-dir", $VaultDir,
                "--verify", $ledgerPath
            )
        
        $report.results['integrity_verified'] = ($verifyResult.ExitCode -eq 0)
        
        if ($verifyResult.ExitCode -ne 0) {
            $report.errors += "Integrity verification failed"
            $report.next_steps += "Investigate integrity verification failure"
        }
    }
}

# Generate summary
Write-Host ""
Write-Host "======================================================================"
Write-Host "RUN SUMMARY"
Write-Host "======================================================================"

$allSuccess = $report.results['tests_passed'] -and $report.results['finalization_success']

if ($Apply) {
    $allSuccess = $allSuccess -and $report.results['integrity_verified']
}

if ($allSuccess) {
    Write-Host "✓ ALL CHECKS PASSED" -ForegroundColor Green
} else {
    Write-Host "✗ SOME CHECKS FAILED" -ForegroundColor Red
}

$testsStatus = if ($report.results['tests_passed']) { "✓" } else { "✗" }
$finalizationStatus = if ($report.results['finalization_success']) { "✓" } else { "✗" }

Write-Host ""
Write-Host "Tests Passed: $testsStatus"
Write-Host "Finalization: $finalizationStatus"

if ($Apply) {
    $integrityStatus = if ($report.results['integrity_verified']) { "✓" } else { "✗" }
    Write-Host "Integrity: $integrityStatus"
}

if ($report.results.ContainsKey('merkle_root')) {
    Write-Host ""
    Write-Host "Merkle Root: $($report.results['merkle_root'])"
}

# Add next steps
if ($report.mode -eq 'dry-run' -and $allSuccess) {
    $report.next_steps += "Review Merkle root and file counts"
    $report.next_steps += "Verify reproducibility (run again and compare)"
    $report.next_steps += "Consider running with -Apply if satisfied"
}

if ($report.mode -eq 'apply' -and $allSuccess) {
    $report.next_steps += "Review ledger and master root files"
    $report.next_steps += "Commit outputs to repository (NOT vault files)"
    $report.next_steps += "Update documentation with Merkle root"
}

# Write report
$reportPath = Join-Path $OutDir "ide_ai_run_report.json"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$reportJson = $report | ConvertTo-Json -Depth 10
$reportJson | Out-File -FilePath $reportPath -Encoding UTF8

Write-Host ""
Write-Host "✓ Report written to: $reportPath"

# Print warnings and next steps
if ($report.warnings.Count -gt 0) {
    Write-Host ""
    Write-Host "⚠ WARNINGS:" -ForegroundColor Yellow
    foreach ($warning in $report.warnings) {
        Write-Host "  - $warning" -ForegroundColor Yellow
    }
}

if ($report.errors.Count -gt 0) {
    Write-Host ""
    Write-Host "✗ ERRORS:" -ForegroundColor Red
    foreach ($error in $report.errors) {
        Write-Host "  - $error" -ForegroundColor Red
    }
}

if ($report.next_steps.Count -gt 0) {
    Write-Host ""
    Write-Host "→ NEXT STEPS:" -ForegroundColor Cyan
    foreach ($step in $report.next_steps) {
        Write-Host "  - $step" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "======================================================================"

# Exit with appropriate code
exit $(if ($allSuccess) { 0 } else { 1 })
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
