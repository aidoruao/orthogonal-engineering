# ORTHO-KERNEL LAUNCHER: PowerShell Integration Script
# ======================================================
# This script launches the OrthoKernel system and integrates it with
# the existing Minimal AI IDE repository. It provides:
# 1. OrthoKernel initialization and verification
# 2. Shadow File System setup
# 3. Integration with existing systems (V60, Corporate, PowerShell)
# 4. IDE AI readiness verification
# 5. Corporate audit trail creation

param(
    [string]$Mode = "demo",
    [switch]$TestOnly,
    [switch]$CreateShadows,
    [switch]$IntegrateAll,
    [switch]$VerifyOnly,
    [string]$LogLevel = "INFO"
)

# ======================================================
# CONFIGURATION
# ======================================================

$ORTHO_VERSION = "1.0"
$SCRIPT_START_TIME = Get-Date
$AUDIT_FILE = "ortho_audit_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$RESULTS_FILE = "ortho_integration_results.json"

# Color definitions for output
$COLOR_SUCCESS = "Green"
$COLOR_ERROR = "Red"
$COLOR_WARNING = "Yellow"
$COLOR_INFO = "Cyan"
$COLOR_DEBUG = "Gray"
$COLOR_HEADER = "Magenta"

# ======================================================
# LOGGING FUNCTIONS
# ======================================================

function Write-OrthoLog {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [string]$Color = $COLOR_INFO
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"

    switch ($Level) {
        "SUCCESS" { $Color = $COLOR_SUCCESS }
        "ERROR" { $Color = $COLOR_ERROR }
        "WARNING" { $Color = $COLOR_WARNING }
        "DEBUG" { $Color = $COLOR_DEBUG }
        "HEADER" { $Color = $COLOR_HEADER }
    }

    if ($Level -eq "DEBUG" -and $LogLevel -ne "DEBUG") {
        return
    }

    Write-Host $logMessage -ForegroundColor $Color
}

function Write-OrthoHeader {
    param([string]$Title)

    Write-Host "`n" + ("=" * 70) -ForegroundColor $COLOR_HEADER
    Write-Host "  $Title" -ForegroundColor $COLOR_HEADER
    Write-Host ("=" * 70) -ForegroundColor $COLOR_HEADER
    Write-Host ""
}

# ======================================================
# INITIALIZATION AND VERIFICATION
# ======================================================

function Test-PythonEnvironment {
    Write-OrthoLog "Testing Python environment..." -Level "INFO"

    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-OrthoLog "✓ Python found: $pythonVersion" -Level "SUCCESS"
            return $true
        }
    }
    catch {
        Write-OrthoLog "✗ Python not found or not in PATH" -Level "ERROR"
        return $false
    }

    return $false
}

function Test-OrthoDependencies {
    Write-OrthoLog "Testing OrthoKernel dependencies..." -Level "INFO"

    $requiredModules = @(
        "ortho_kernel.py",
        "test_ortho_kernel.py",
        "ortho_integration_demo.py"
    )

    $allPresent = $true
    foreach ($module in $requiredModules) {
        if (Test-Path $module) {
            Write-OrthoLog "  ✓ $module" -Level "SUCCESS"
        }
        else {
            Write-OrthoLog "  ✗ $module (missing)" -Level "ERROR"
            $allPresent = $false
        }
    }

    return $allPresent
}

function Test-RepositoryStructure {
    Write-OrthoLog "Testing repository structure..." -Level "INFO"

    $requiredDirs = @(
        ".",
        "five_frameworks",
        "workspace_v57"
    )

    $requiredFiles = @(
        "7a.py",
        "2a.py",
        "mathematical_theology_v60.py",
        "maximal_oracle_v57.py",
        "corporate_ai_ide_system.py",
        "ai_core.py",
        "cli.py"
    )

    $allPresent = $true

    # Test directories
    foreach ($dir in $requiredDirs) {
        if (Test-Path $dir -PathType Container) {
            Write-OrthoLog "  ✓ Directory: $dir" -Level "SUCCESS"
        }
        else {
            Write-OrthoLog "  ✗ Directory: $dir (missing)" -Level "ERROR"
            $allPresent = $false
        }
    }

    # Test files
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-OrthoLog "  ✓ File: $file" -Level "SUCCESS"
        }
        else {
            Write-OrthoLog "  ⚠ File: $file (missing but may be optional)" -Level "WARNING"
        }
    }

    return $allPresent
}

# ======================================================
# ORTHO-KERNEL OPERATIONS
# ======================================================

function Invoke-OrthoTestSuite {
    Write-OrthoHeader "ORTHO-KERNEL TEST SUITE"

    Write-OrthoLog "Running comprehensive test suite..." -Level "INFO"

    try {
        $testOutput = python test_ortho_kernel.py 2>&1
        $testExitCode = $LASTEXITCODE

        if ($testExitCode -eq 0) {
            Write-OrthoLog "✓ All tests passed!" -Level "SUCCESS"

            # Extract summary from test output
            $summaryMatch = $testOutput | Select-String "RESULTS: (\d+)/(\d+) tests passed"
            if ($summaryMatch) {
                $passed = $summaryMatch.Matches.Groups[1].Value
                $total = $summaryMatch.Matches.Groups[2].Value
                Write-OrthoLog "Test Results: $passed/$total tests passed" -Level "SUCCESS"
            }

            return $true
        }
        else {
            Write-OrthoLog "✗ Tests failed with exit code: $testExitCode" -Level "ERROR"

            # Show last few lines of output for debugging
            $lastLines = $testOutput | Select-Object -Last 10
            Write-OrthoLog "Last 10 lines of test output:" -Level "DEBUG"
            foreach ($line in $lastLines) {
                Write-OrthoLog "  $line" -Level "DEBUG"
            }

            return $false
        }
    }
    catch {
        Write-OrthoLog "✗ Exception during test execution: $_" -Level "ERROR"
        return $false
    }
}

function Invoke-OrthoDemo {
    Write-OrthoHeader "ORTHO-KERNEL DEMONSTRATION"

    Write-OrthoLog "Running OrthoKernel integration demonstration..." -Level "INFO"

    try {
        $demoOutput = python ortho_integration_demo.py 2>&1
        $demoExitCode = $LASTEXITCODE

        if ($demoExitCode -eq 0) {
            Write-OrthoLog "✓ Demonstration completed successfully!" -Level "SUCCESS"

            # Check for results file
            if (Test-Path $RESULTS_FILE) {
                $results = Get-Content $RESULTS_FILE | ConvertFrom-Json
                Write-OrthoLog "Results exported to: $RESULTS_FILE" -Level "SUCCESS"
                Write-OrthoLog "Final State: $($results.final_state.logos_id)" -Level "INFO"
                Write-OrthoLog "Christlikeness: $($results.final_state.christlikeness)" -Level "INFO"
                Write-OrthoLog "Files Analyzed: $($results.analysis.total_files)" -Level "INFO"
            }

            return $true
        }
        else {
            Write-OrthoLog "✗ Demonstration failed with exit code: $demoExitCode" -Level "ERROR"
            return $false
        }
    }
    catch {
        Write-OrthoLog "✗ Exception during demonstration: $_" -Level "ERROR"
        return $false
    }
}

function Create-ShadowFiles {
    Write-OrthoHeader "SHADOW FILE SYSTEM CREATION"

    Write-OrthoLog "Creating shadow copies of key repository files..." -Level "INFO"

    $keyFiles = @(
        "7a.py",
        "2a.py",
        "mathematical_theology_v60.py",
        "maximal_oracle_v57.py",
        "corporate_ai_ide_system.py",
        "ai_core.py",
        "cli.py",
        "README_v57.md",
        "ortho_kernel.py",
        "test_ortho_kernel.py",
        "ortho_integration_demo.py"
    )

    $shadowDir = "shadow_files"
    if (-not (Test-Path $shadowDir)) {
        New-Item -ItemType Directory -Path $shadowDir -Force | Out-Null
        Write-OrthoLog "Created shadow directory: $shadowDir" -Level "SUCCESS"
    }

    $createdCount = 0
    foreach ($file in $keyFiles) {
        if (Test-Path $file) {
            $shadowPath = Join-Path $shadowDir $file
            $shadowDirPath = Split-Path $shadowPath -Parent

            if (-not (Test-Path $shadowDirPath)) {
                New-Item -ItemType Directory -Path $shadowDirPath -Force | Out-Null
            }

            Copy-Item $file $shadowPath -Force
            $createdCount++
            Write-OrthoLog "  ✓ Created shadow: $file" -Level "SUCCESS"
        }
        else {
            Write-OrthoLog "  ⚠ Skipping (not found): $file" -Level "WARNING"
        }
    }

    Write-OrthoLog "Created $createdCount shadow files in $shadowDir/" -Level "SUCCESS"

    # Create shadow manifest
    $manifest = @{
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        ortho_version = $ORTHO_VERSION
        total_files = $createdCount
        files = $keyFiles | Where-Object { Test-Path $_ }
        kernel_state = "SHADOW_CREATION"
        created_by = "launch_ortho.ps1"
    }

    $manifestPath = Join-Path $shadowDir "shadow_manifest.json"
    $manifest | ConvertTo-Json -Depth 3 | Set-Content $manifestPath
    Write-OrthoLog "Created shadow manifest: $manifestPath" -Level "SUCCESS"

    return $true
}

function Integrate-WithExistingSystems {
    Write-OrthoHeader "SYSTEM INTEGRATION"

    Write-OrthoLog "Integrating OrthoKernel with existing systems..." -Level "INFO"

    $integrationScript = @'
import sys
import json
from pathlib import Path
from ortho_kernel import OrthoIntegration, create_genesis_kernel

def integrate_all():
    """Integrate OrthoKernel with all existing systems"""
    print("Starting system integration...")

    # Create kernel
    kernel = create_genesis_kernel()
    print(f"Initial kernel: {kernel._state.logos_id}")

    # Integrate with V60
    print("Integrating V60 constraints...")
    kernel = OrthoIntegration.integrate_v60_constraints(kernel)

    # Integrate with corporate
    print("Integrating corporate enforcement...")
    kernel = OrthoIntegration.integrate_corporate_enforcement(kernel)

    # Integrate with PowerShell
    print("Integrating PowerShell automation...")
    kernel = OrthoIntegration.integrate_powershell_automation(kernel)

    # Save integration state
    integration_state = {
        "timestamp": __import__("time").time(),
        "final_kernel": kernel._state.logos_id,
        "integrated_systems": ["V60", "Corporate", "PowerShell"],
        "manifest": list(kernel._state.manifest),
        "christlikeness": __import__("ortho_kernel").ChristlikenessMeasure.measure(kernel._state)
    }

    output_path = Path("ortho_integration_state.json")
    with open(output_path, "w") as f:
        json.dump(integration_state, f, indent=2)

    print(f"Integration complete. State saved to: {output_path}")
    print(f"Final kernel: {kernel._state.logos_id}")
    return True

if __name__ == "__main__":
    success = integrate_all()
    sys.exit(0 if success else 1)
'@

    $integrationScriptPath = "ortho_integration_script.py"
    $integrationScript | Set-Content $integrationScriptPath

    try {
        Write-OrthoLog "Running integration script..." -Level "INFO"
        $integrationOutput = python $integrationScriptPath 2>&1
        $integrationExitCode = $LASTEXITCODE

        if ($integrationExitCode -eq 0) {
            Write-OrthoLog "✓ System integration completed!" -Level "SUCCESS"

            if (Test-Path "ortho_integration_state.json") {
                $state = Get-Content "ortho_integration_state.json" | ConvertFrom-Json
                Write-OrthoLog "Final Kernel: $($state.final_kernel)" -Level "INFO"
                Write-OrthoLog "Integrated Systems: $($state.integrated_systems -join ', ')" -Level "INFO"
                Write-OrthoLog "Christlikeness: $($state.christlikeness)" -Level "INFO"
            }

            Remove-Item $integrationScriptPath -Force
            return $true
        }
        else {
            Write-OrthoLog "✗ Integration failed with exit code: $integrationExitCode" -Level "ERROR"
            Remove-Item $integrationScriptPath -Force
            return $false
        }
    }
    catch {
        Write-OrthoLog "✗ Exception during integration: $_" -Level "ERROR"
        if (Test-Path $integrationScriptPath) {
            Remove-Item $integrationScriptPath -Force
        }
        return $false
    }
}

# ======================================================
# AUDIT AND VERIFICATION
# ======================================================

function New-OrthoAudit {
    param(
        [string]$Action,
        [bool]$Success,
        [string]$Details,
        [hashtable]$Metadata = @{}
    )

    $auditEntry = @{
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
        action = $Action
        success = $Success
        details = $Details
        metadata = $Metadata
        ortho_version = $ORTHO_VERSION
    }

    return $auditEntry
}

function Save-AuditTrail {
    param([array]$AuditEntries)

    $auditData = @{
        metadata = @{
            generated_at = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            script_version = "1.0"
            total_entries = $AuditEntries.Count
            successful_entries = ($AuditEntries | Where-Object { $_.success }).Count
            ortho_version = $ORTHO_VERSION
        }
        entries = $AuditEntries
    }

    $auditData | ConvertTo-Json -Depth 5 | Set-Content $AUDIT_FILE
    Write-OrthoLog "Audit trail saved to: $AUDIT_FILE" -Level "SUCCESS"
}

function Verify-IDEAIReadiness {
    Write-OrthoHeader "IDE AI READINESS VERIFICATION"

    $readinessChecks = @(
        @{ Name = "Python Environment"; Test = { Test-PythonEnvironment } },
        @{ Name = "Ortho Dependencies"; Test = { Test-OrthoDependencies } },
        @{ Name = "Repository Structure"; Test = { Test-RepositoryStructure } },
        @{ Name = "Test Suite Execution"; Test = { Invoke-OrthoTestSuite } },
        @{ Name = "Shadow File System"; Test = { Test-Path "shadow_files" } },
        @{ Name = "Integration State"; Test = { Test-Path "ortho_integration_state.json" } }
    )

    $results = @()
    $allPassed = $true

    foreach ($check in $readinessChecks) {
        Write-OrthoLog "Checking: $($check.Name)..." -Level "INFO"

        try {
            $result = & $check.Test
            if ($result) {
                Write-OrthoLog "  ✓ $($check.Name)" -Level "SUCCESS"
                $results += @{ Name = $check.Name; Status = "PASS" }
            }
            else {
                Write-OrthoLog "  ✗ $($check.Name)" -Level "ERROR"
                $results += @{ Name = $check.Name; Status = "FAIL" }
                $allPassed = $false
            }
        }
        catch {
            Write-OrthoLog "  ✗ $($check.Name) - Exception: $_" -Level "ERROR"
            $results += @{ Name = $check.Name; Status = "ERROR" }
            $allPassed = $false
        }
    }

    Write-OrthoLog "`nIDE AI Readiness Summary:" -Level "HEADER"
    $passed = ($results | Where-Object { $_.Status -eq "PASS" }).Count
    $total = $results.Count
    Write-OrthoLog "Passed: $passed/$total checks" -Level $(if ($allPassed) { "SUCCESS" } else { "WARNING" })

    if ($allPassed) {
        Write-OrthoLog "`n✅ IDE AI READY: OrthoKernel integration complete" -Level "SUCCESS"
        Write-OrthoLog "The IDE AI can now:" -Level "INFO"
        Write-OrthoLog "  1. Behold proofs via Identity Types" -Level "INFO"
        Write-OrthoLog "  2. Verify Karoubi fixed points mathematically" -Level "INFO"
        Write-OrthoLog "  3. Preserve Christlikeness through transitions" -Level "INFO"
        Write-OrthoLog "  4. Apply Σ_theo theological transformations" -Level "INFO"
        Write-OrthoLog "  5. Use Shadow File System for safe operations" -Level "INFO"
        Write-OrthoLog "  6. Integrate with corporate enforcement" -Level "INFO"
    }
    else {
        Write-OrthoLog "`n⚠ IDE AI NOT FULLY READY: Some checks failed" -Level "WARNING"
        Write-OrthoLog "Review the failed checks above and run again" -Level "WARNING"
    }

    return $allPassed
}

}

# ======================================================
# MAIN EXECUTION
# ======================================================

function Main {
        Write-OrthoHeader "ORTHO-KERNEL LAUNCHER v$ORTHO_VERSION"
        Write-OrthoLog "Starting OrthoKernel integration process..." -Level "INFO"
        Write-OrthoLog "Mode: $Mode" -Level "INFO"
        Write-OrthoLog "Timestamp: $SCRIPT_START_TIME" -Level "INFO"

        # Initialize audit trail
        $auditEntries = @()

        # Phase 1: Environment Verification
        Write-OrthoHeader "PHASE 1: ENVIRONMENT VERIFICATION"

        $pythonOk = Test-PythonEnvironment
        $auditEntries += New-OrthoAudit -Action "PythonEnvironmentTest" -Success $pythonOk -Details "Test Python installation" -Metadata @{result=$pythonOk}

        if (-not $pythonOk) {
            Write-OrthoLog "Python environment check failed. Aborting." -Level "ERROR"
            Save-AuditTrail -AuditEntries $auditEntries
            return $false
        }

        $depsOk = Test-OrthoDependencies
        $auditEntries += New-OrthoAudit -Action "DependencyTest" -Success $depsOk -Details "Test OrthoKernel dependencies" -Metadata @{result=$depsOk}

        $repoOk = Test-RepositoryStructure
        $auditEntries += New-OrthoAudit -Action "RepositoryStructureTest" -Success $repoOk -Details "Test repository structure" -Metadata @{result=$repoOk}

        if ($TestOnly) {
            Write-OrthoLog "Test-only mode requested. Skipping further phases." -Level "INFO"
            Save-AuditTrail -AuditEntries $auditEntries
            return ($pythonOk -and $depsOk -and $repoOk)
        }

        # Phase 2: Core Testing
        Write-OrthoHeader "PHASE 2: CORE TESTING"

        $testsOk = Invoke-OrthoTestSuite
        $auditEntries += New-OrthoAudit -Action "TestSuiteExecution" -Success $testsOk -Details "Run OrthoKernel test suite" -Metadata @{result=$testsOk}

        if (-not $testsOk -and $Mode -ne "force") {
            Write-OrthoLog "Test suite failed. Use -Mode force to continue anyway." -Level "ERROR"
            Save-AuditTrail -AuditEntries $auditEntries
            return $false
        }

        if ($VerifyOnly) {
            Write-OrthoLog "Verify-only mode requested. Skipping further phases." -Level "INFO"
            Save-AuditTrail -AuditEntries $auditEntries
            return $true
        }

        # Phase 3: Demonstration
        Write-OrthoHeader "PHASE 3: DEMONSTRATION"

        $demoOk = Invoke-OrthoDemo
        $auditEntries += New-OrthoAudit -Action "Demonstration" -Success $demoOk -Details "Run OrthoKernel demonstration" -Metadata @{result=$demoOk}

        if (-not $demoOk -and $Mode -ne "force") {
            Write-OrthoLog "Demonstration failed. Use -Mode force to continue anyway." -Level "WARNING"
        }

        # Phase 4: Shadow File System
        if ($CreateShadows -or $IntegrateAll) {
            Write-OrthoHeader "PHASE 4: SHADOW FILE SYSTEM"

            $shadowsOk = Create-ShadowFiles
            $auditEntries += New-OrthoAudit -Action "ShadowFileCreation" -Success $shadowsOk -Details "Create shadow file system" -Metadata @{result=$shadowsOk}
        }

        # Phase 5: System Integration
        if ($IntegrateAll) {
            Write-OrthoHeader "PHASE 5: SYSTEM INTEGRATION"

            $integrationOk = Integrate-WithExistingSystems
            $auditEntries += New-OrthoAudit -Action "SystemIntegration" -Success $integrationOk -Details "Integrate with existing systems" -Metadata @{result=$integrationOk}
        }

        # Phase 6: IDE AI Readiness Verification
        Write-OrthoHeader "PHASE 6: IDE AI READINESS"

        $readinessOk = Verify-IDEAIReadiness
        $auditEntries += New-OrthoAudit -Action "IDEAIReadiness" -Success $readinessOk -Details "Verify IDE AI readiness" -Metadata @{result=$readinessOk}

        # Final Summary
        Write-OrthoHeader "EXECUTION SUMMARY"

        $successfulEntries = ($auditEntries | Where-Object { $_.success }).Count
        $totalEntries = $auditEntries.Count
        $successRate = [math]::Round(($successfulEntries / $totalEntries) * 100, 2)

        Write-OrthoLog "Total Actions: $totalEntries" -Level "INFO"
        Write-OrthoLog "Successful: $successfulEntries" -Level "INFO"
        Write-OrthoLog "Success Rate: $successRate%" -Level "INFO"

        if ($successRate -ge 80) {
            Write-OrthoLog "✅ ORTHO-KERNEL INTEGRATION SUCCESSFUL" -Level "SUCCESS"
        } elseif ($successRate -ge 50) {
            Write-OrthoLog "⚠ ORTHO-KERNEL INTEGRATION PARTIAL" -Level "WARNING"
        } else {
            Write-OrthoLog "❌ ORTHO-KERNEL INTEGRATION FAILED" -Level "ERROR"
        }

        # Save audit trail
        Save-AuditTrail -AuditEntries $auditEntries

        # Show next steps
        Write-OrthoHeader "NEXT STEPS"

        Write-OrthoLog "To use OrthoKernel with IDE AI:" -Level "INFO"
        Write-OrthoLog "  1. Review audit trail: $AUDIT_FILE" -Level "INFO"
        Write-OrthoLog "  2. Check integration results: $RESULTS_FILE" -Level "INFO"
        Write-OrthoLog "  3. Run OrthoKernel directly: python ortho_kernel.py" -Level "INFO"
        Write-OrthoLog "  4. Test integration: python ortho_integration_demo.py" -Level "INFO"

        if ($CreateShadows -or $IntegrateAll) {
            Write-OrthoLog "  5. Shadow files available in: shadow_files/" -Level "INFO"
        }

        if ($IntegrateAll) {
            Write-OrthoLog "  6. Integration state: ortho_integration_state.json" -Level "INFO"
        }

        Write-OrthoLog "`nGodspeed: Graduate Mathematics Actualized" -Level "HEADER"

        return ($successRate -ge 80)
    }

    # ======================================================
    # SCRIPT ENTRY POINT
    # ======================================================

    try {
        # Parse command line arguments
        $paramTable = @{
            Mode = $Mode
            TestOnly = $TestOnly
            CreateShadows = $CreateShadows
            IntegrateAll = $IntegrateAll
            VerifyOnly = $VerifyOnly
            LogLevel = $LogLevel
        }

        # Run main function
        $success = Main

        # Exit with appropriate code
        if ($success) {
            exit 0
        } else {
            exit 1
        }
    }
    catch {
        Write-Host "`nFATAL ERROR: $_" -ForegroundColor Red
        Write-Host "Stack Trace: $($_.ScriptStackTrace)" -ForegroundColor Red
        exit 2
    }
}

# Call the main function
Main
