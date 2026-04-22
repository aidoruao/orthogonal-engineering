# Craftsman IDE Atomic Forensic Verification Script
# Zed IDE-AI Blueprint Implementation
# Version: 1.0.0
# Date: 2026-01-24
# Purpose: Perform atomic, repeatable forensic verification of Craftsman IDE folder

# ============================================
# CONFIGURATION
# ============================================
$TargetFolder = "C:\Users\Aidor\craftsman-ide"
$ExpectedMarkers = @(
    "Craftsman.exe",
    "config.json",
    "scripts",
    "backend",
    "package.json",
    "README.md"
)
$ReportPath = "C:\Users\Aidor\Documents\orthogonal-engineering-clean\logs\craftsman_forensic_report.json"

# ============================================
# STEP 1: INITIALIZATION
# ============================================
Write-Host "🔍 ATOMIC FORENSIC VERIFICATION FOR CRAFTSMAN IDE" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "Target: $TargetFolder" -ForegroundColor White
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White
Write-Host "Performed by: Zed IDE-AI Atomic Blueprint" -ForegroundColor White
Write-Host ""

# ============================================
# STEP 2: EXISTENCE VERIFICATION
# ============================================
Write-Host "✅ STEP 1: Existence Verification" -ForegroundColor Green
$FolderExists = Test-Path $TargetFolder

if (-not $FolderExists) {
    Write-Host "   ❌ ERROR: Target folder does not exist" -ForegroundColor Red
    Write-Host "   Path: $TargetFolder" -ForegroundColor Red

    $errorReport = [PSCustomObject]@{
        Verification = @{
            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            Status = "Failed"
            Error = "Folder not found"
        }
        Target = @{
            FolderPath = $TargetFolder
            Exists = $false
        }
    }

    # Ensure logs directory exists
    $logsDir = Split-Path $ReportPath -Parent
    if (-not (Test-Path $logsDir)) {
        New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
    }

    $errorReport | ConvertTo-Json -Depth 3 | Out-File $ReportPath -Encoding UTF8
    Write-Host "   📋 Error report saved to: $ReportPath" -ForegroundColor Yellow

    exit 2  # Exit code 2: Absent
}

Write-Host "   ✓ Folder exists: $TargetFolder" -ForegroundColor Green

# ============================================
# STEP 3: MARKER VALIDATION
# ============================================
Write-Host ""
Write-Host "✅ STEP 2: Marker Validation" -ForegroundColor Green
Write-Host "   Expected markers: $($ExpectedMarkers.Count)" -ForegroundColor White

$FoundMarkers = @()
$MissingMarkers = @()

foreach ($marker in $ExpectedMarkers) {
    $markerPath = Join-Path $TargetFolder $marker
    $markerExists = Test-Path $markerPath

    if ($markerExists) {
        $FoundMarkers += $marker
        Write-Host "   ✓ $marker" -ForegroundColor Green
    } else {
        $MissingMarkers += $marker
        Write-Host "   ✗ $marker" -ForegroundColor Yellow
    }
}

# ============================================
# STEP 4: STATUS DETERMINATION
# ============================================
Write-Host ""
Write-Host "📊 STEP 3: Status Determination" -ForegroundColor Cyan

if ($FoundMarkers.Count -eq $ExpectedMarkers.Count) {
    $Status = "Full"
    $StatusColor = "Green"
} elseif ($FoundMarkers.Count -ge 3) {
    $Status = "Partial"
    $StatusColor = "Yellow"
} else {
    $Status = "Absent"
    $StatusColor = "Red"
}

$CompletionRatio = [math]::Round(($FoundMarkers.Count / $ExpectedMarkers.Count) * 100, 2)

Write-Host "   Found: $($FoundMarkers.Count)/$($ExpectedMarkers.Count) markers" -ForegroundColor White
Write-Host "   Completion: $CompletionRatio%" -ForegroundColor White
Write-Host "   Status: $Status" -ForegroundColor $StatusColor

# ============================================
# STEP 5: FORENSIC DATA COLLECTION
# ============================================
Write-Host ""
Write-Host "🔍 STEP 4: Forensic Data Collection" -ForegroundColor Cyan

try {
    $FolderInfo = Get-Item $TargetFolder
    $CreationTime = $FolderInfo.CreationTime
    $LastWriteTime = $FolderInfo.LastWriteTime

    # Count files and directories
    $AllFiles = Get-ChildItem -Path $TargetFolder -Recurse -File -ErrorAction SilentlyContinue
    $AllDirectories = Get-ChildItem -Path $TargetFolder -Recurse -Directory -ErrorAction SilentlyContinue

    $FileCount = $AllFiles.Count
    $DirectoryCount = $AllDirectories.Count

    Write-Host "   Created: $CreationTime" -ForegroundColor White
    Write-Host "   Modified: $LastWriteTime" -ForegroundColor White
    Write-Host "   Total files: $FileCount" -ForegroundColor White
    Write-Host "   Total directories: $DirectoryCount" -ForegroundColor White

    # Check for IDE-specific patterns
    $IDEPatterns = @("*.exe", "*.bat", "*.js", "*.json", "*.md", "*.py", "*.txt")
    $PatternMatches = @{}

    foreach ($pattern in $IDEPatterns) {
        $matches = Get-ChildItem -Path $TargetFolder -Recurse -Include $pattern -ErrorAction SilentlyContinue
        if ($matches) {
            $PatternMatches[$pattern] = $matches.Count
        }
    }

    Write-Host "   IDE patterns detected: $($PatternMatches.Count)" -ForegroundColor White

} catch {
    Write-Host "   ⚠️  Warning: Could not collect all forensic data" -ForegroundColor Yellow
    Write-Host "   Error: $_" -ForegroundColor Yellow
    $FileCount = 0
    $DirectoryCount = 0
    $PatternMatches = @{}
}

# ============================================
# STEP 6: STRUCTURE SAMPLING
# ============================================
Write-Host ""
Write-Host "📁 STEP 5: Structure Sampling" -ForegroundColor Cyan

try {
    $TopLevelItems = Get-ChildItem -Path $TargetFolder -ErrorAction SilentlyContinue | Select-Object -First 10
    $SampleFiles = @()
    $SampleDirectories = @()

    foreach ($item in $TopLevelItems) {
        if ($item.PSIsContainer) {
            $SampleDirectories += $item.Name
        } else {
            $SampleFiles += $item.Name
        }
    }

    Write-Host "   Sample files: $($SampleFiles.Count)" -ForegroundColor White
    Write-Host "   Sample directories: $($SampleDirectories.Count)" -ForegroundColor White

    if ($SampleFiles.Count -gt 0) {
        Write-Host "   File examples: $($SampleFiles -join ', ')" -ForegroundColor Gray
    }

    if ($SampleDirectories.Count -gt 0) {
        Write-Host "   Directory examples: $($SampleDirectories -join ', ')" -ForegroundColor Gray
    }

} catch {
    Write-Host "   ⚠️  Could not sample structure" -ForegroundColor Yellow
    $SampleFiles = @()
    $SampleDirectories = @()
}

# ============================================
# STEP 7: ATOMIC REPORT GENERATION
# ============================================
Write-Host ""
Write-Host "📋 STEP 6: Atomic Report Generation" -ForegroundColor Green

$Report = [PSCustomObject]@{
    Metadata = @{
        GeneratedAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        PerformedBy = "Zed IDE-AI Atomic Blueprint"
        Version = "1.0.0"
        ScriptPath = $MyInvocation.MyCommand.Path
    }
    Target = @{
        FolderPath = $TargetFolder
        Exists = $true
        CreationTime = if ($CreationTime) { $CreationTime.ToString("yyyy-MM-dd HH:mm:ss") } else { $null }
        LastWriteTime = if ($LastWriteTime) { $LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss") } else { $null }
    }
    Validation = @{
        ExpectedMarkers = $ExpectedMarkers
        FoundMarkers = $FoundMarkers
        MissingMarkers = $MissingMarkers
        Status = $Status
        CompletionRatio = $CompletionRatio
        MarkerCount = @{
            Expected = $ExpectedMarkers.Count
            Found = $FoundMarkers.Count
            Missing = $MissingMarkers.Count
        }
    }
    ForensicData = @{
        FileSystem = @{
            TotalFiles = $FileCount
            TotalDirectories = $DirectoryCount
            TotalItems = $FileCount + $DirectoryCount
        }
        PatternDetection = $PatternMatches
        StructureSample = @{
            Files = $SampleFiles
            Directories = $SampleDirectories
        }
    }
    VerificationResult = @{
        OverallStatus = $Status
        IsComplete = ($Status -eq "Full")
        RequiresAttention = ($Status -ne "Full")
        Recommendations = if ($Status -eq "Full") { @("All markers present") }
                         elseif ($Status -eq "Partial") { @("Some markers missing", "Review installation") }
                         else { @("Major markers missing", "Consider reinstallation") }
    }
}

# ============================================
# STEP 8: REPORT SAVING
# ============================================
try {
    # Ensure logs directory exists
    $logsDir = Split-Path $ReportPath -Parent
    if (-not (Test-Path $logsDir)) {
        New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
    }

    # Save report as JSON
    $ReportJson = $Report | ConvertTo-Json -Depth 5
    $ReportJson | Out-File -FilePath $ReportPath -Encoding UTF8

    Write-Host "   ✓ Report saved to: $ReportPath" -ForegroundColor Green

} catch {
    Write-Host "   ❌ Error saving report: $_" -ForegroundColor Red
    $ReportPath = $null
}

# ============================================
# STEP 9: FINAL SUMMARY
# ============================================
Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "VERIFICATION COMPLETE" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan

Write-Host ""
Write-Host "🎯 FINAL RESULT: " -NoNewline
switch ($Status) {
    "Full" {
        Write-Host "FULL VERIFICATION ✓" -ForegroundColor Green
        Write-Host "   All expected markers found" -ForegroundColor Green
    }
    "Partial" {
        Write-Host "PARTIAL VERIFICATION ⚠️" -ForegroundColor Yellow
        Write-Host "   Found $($FoundMarkers.Count) of $($ExpectedMarkers.Count) markers" -ForegroundColor Yellow
        if ($MissingMarkers.Count -gt 0) {
            Write-Host "   Missing: $($MissingMarkers -join ', ')" -ForegroundColor Yellow
        }
    }
    "Absent" {
        Write-Host "ABSENT VERIFICATION ✗" -ForegroundColor Red
        Write-Host "   Found only $($FoundMarkers.Count) of $($ExpectedMarkers.Count) markers" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "📊 FORENSIC SUMMARY:" -ForegroundColor White
Write-Host "   Location: $TargetFolder" -ForegroundColor Gray
Write-Host "   Total items: $($FileCount + $DirectoryCount)" -ForegroundColor Gray
Write-Host "   Files: $FileCount" -ForegroundColor Gray
Write-Host "   Directories: $DirectoryCount" -ForegroundColor Gray
Write-Host "   Age: $(if ($CreationTime) { (New-TimeSpan -Start $CreationTime -End (Get-Date)).Days.ToString() + ' days' } else { 'Unknown' })" -ForegroundColor Gray

Write-Host ""
Write-Host "🔧 NEXT STEPS:" -ForegroundColor Cyan
switch ($Status) {
    "Full" {
        Write-Host "   1. Craftsman IDE is fully verified" -ForegroundColor Green
        Write-Host "   2. Ready for integration or use" -ForegroundColor Green
        Write-Host "   3. Review report for detailed analysis" -ForegroundColor Green
    }
    "Partial" {
        Write-Host "   1. Review missing markers: $($MissingMarkers -join ', ')" -ForegroundColor Yellow
        Write-Host "   2. Check installation integrity" -ForegroundColor Yellow
        Write-Host "   3. Consider repair or reinstallation" -ForegroundColor Yellow
    }
    "Absent" {
        Write-Host "   1. Major components missing" -ForegroundColor Red
        Write-Host "   2. Consider complete reinstallation" -ForegroundColor Red
        Write-Host "   3. Verify download source" -ForegroundColor Red
    }
}

if ($ReportPath) {
    Write-Host ""
    Write-Host "📄 REPORT:" -ForegroundColor White
    Write-Host "   Full forensic report available at:" -ForegroundColor Gray
    Write-Host "   $ReportPath" -ForegroundColor Gray
}

Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "Atomic forensic verification complete." -ForegroundColor Cyan
Write-Host "All operations performed via PowerShell commands only." -ForegroundColor Cyan
Write-Host "No manual navigation or assumptions required." -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan

# ============================================
# STEP 10: EXIT WITH APPROPRIATE CODE
# ============================================
switch ($Status) {
    "Full" { exit 0 }    # Success - Full verification
    "Partial" { exit 1 } # Warning - Partial verification
    "Absent" { exit 2 }  # Error - Absent verification
    default { exit 3 }   # Unknown error
}
