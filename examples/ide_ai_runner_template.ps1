# IDE AI Runner Template (PowerShell)
# 
# This template demonstrates a complete dry-run workflow for IDE AI systems.
# It runs the finalizer, executes tests, computes manifest hashes, and generates
# an AI run report.
#
# SAFETY: Default mode is DRY-RUN. Use -Apply switch to enable apply mode.

param(
    [string]$VaultDir = "C:\Users\Aidor\Downloads\ai_exports",
    [string]$OutDir = ".\outputs",
    [switch]$Apply
)

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
