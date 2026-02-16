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
