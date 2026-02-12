# Craftsman IDE Simple Forensic Verification
# Zed IDE-AI Atomic Blueprint Implementation
# Version: 1.0.0
# Date: 2026-01-24

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "CRAFTSMAN IDE FORENSIC VERIFICATION" -ForegroundColor Cyan
Write-Host "Zed IDE-AI Atomic Blueprint" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$TargetFolder = "C:\Users\Aidor\craftsman-ide"
$ExpectedFiles = @("Craftsman.exe", "config.json", "scripts", "backend", "package.json", "README.md")
$ReportPath = "C:\Users\Aidor\Documents\orthogonal-engineering-clean\logs\craftsman_simple_report.json"

Write-Host "Target: $TargetFolder" -ForegroundColor White
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White
Write-Host ""

# Step 1: Check if folder exists
Write-Host "STEP 1: Existence Check" -ForegroundColor Green
$FolderExists = Test-Path $TargetFolder

if (-not $FolderExists) {
    Write-Host "  ERROR: Folder does not exist" -ForegroundColor Red
    Write-Host "  Path: $TargetFolder" -ForegroundColor Red

    # Create simple error report
    $ErrorReport = @{
        error = "Folder not found"
        path = $TargetFolder
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        status = "absent"
    }

    # Save report
    $ErrorReport | ConvertTo-Json | Out-File $ReportPath -Encoding UTF8
    Write-Host "  Report saved to: $ReportPath" -ForegroundColor Yellow

    exit 2
}

Write-Host "  SUCCESS: Folder exists" -ForegroundColor Green

# Step 2: Check for expected files
Write-Host ""
Write-Host "STEP 2: File Validation" -ForegroundColor Green

$FoundFiles = @()
$MissingFiles = @()

foreach ($file in $ExpectedFiles) {
    $filePath = Join-Path $TargetFolder $file
    if (Test-Path $filePath) {
        $FoundFiles += $file
        Write-Host "  FOUND: $file" -ForegroundColor Green
    } else {
        $MissingFiles += $file
        Write-Host "  MISSING: $file" -ForegroundColor Yellow
    }
}

# Step 3: Determine status
Write-Host ""
Write-Host "STEP 3: Status Determination" -ForegroundColor Cyan

if ($FoundFiles.Count -eq $ExpectedFiles.Count) {
    $Status = "full"
    $StatusColor = "Green"
} elseif ($FoundFiles.Count -ge 3) {
    $Status = "partial"
    $StatusColor = "Yellow"
} else {
    $Status = "absent"
    $StatusColor = "Red"
}

$CompletionPercent = [math]::Round(($FoundFiles.Count / $ExpectedFiles.Count) * 100, 1)

Write-Host "  Found: $($FoundFiles.Count)/$($ExpectedFiles.Count) files" -ForegroundColor White
Write-Host "  Completion: $CompletionPercent%" -ForegroundColor White
Write-Host "  Status: $Status" -ForegroundColor $StatusColor

# Step 4: Collect basic forensic data
Write-Host ""
Write-Host "STEP 4: Data Collection" -ForegroundColor Cyan

try {
    $FolderItem = Get-Item $TargetFolder
    $CreationTime = $FolderItem.CreationTime
    $ModifiedTime = $FolderItem.LastWriteTime

    # Count files and folders
    $AllItems = Get-ChildItem -Path $TargetFolder -Recurse -ErrorAction SilentlyContinue
    $FileCount = ($AllItems | Where-Object { -not $_.PSIsContainer }).Count
    $FolderCount = ($AllItems | Where-Object { $_.PSIsContainer }).Count

    Write-Host "  Created: $($CreationTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor White
    Write-Host "  Modified: $($ModifiedTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor White
    Write-Host "  Files: $FileCount" -ForegroundColor White
    Write-Host "  Folders: $FolderCount" -ForegroundColor White

} catch {
    Write-Host "  WARNING: Could not collect all data" -ForegroundColor Yellow
    $CreationTime = $null
    $ModifiedTime = $null
    $FileCount = 0
    $FolderCount = 0
}

# Step 5: Show top-level items
Write-Host ""
Write-Host "STEP 5: Structure Preview" -ForegroundColor Cyan

try {
    $TopItems = Get-ChildItem -Path $TargetFolder -ErrorAction SilentlyContinue | Select-Object -First 8
    if ($TopItems) {
        Write-Host "  Top items:" -ForegroundColor White
        foreach ($item in $TopItems) {
            $type = if ($item.PSIsContainer) { "[DIR]" } else { "[FILE]" }
            Write-Host "    $type $($item.Name)" -ForegroundColor Gray
        }
    } else {
        Write-Host "  No items found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  Could not list items" -ForegroundColor Yellow
}

# Step 6: Generate report
Write-Host ""
Write-Host "STEP 6: Report Generation" -ForegroundColor Green

$Report = @{
    metadata = @{
        generated_at = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        performed_by = "Zed IDE-AI Atomic Blueprint"
        version = "1.0.0"
    }
    target = @{
        folder_path = $TargetFolder
        exists = $true
        creation_time = if ($CreationTime) { $CreationTime.ToString("yyyy-MM-dd HH:mm:ss") } else { $null }
        modified_time = if ($ModifiedTime) { $ModifiedTime.ToString("yyyy-MM-dd HH:mm:ss") } else { $null }
    }
    validation = @{
        expected_files = $ExpectedFiles
        found_files = $FoundFiles
        missing_files = $MissingFiles
        status = $Status
        completion_percent = $CompletionPercent
        counts = @{
            expected = $ExpectedFiles.Count
            found = $FoundFiles.Count
            missing = $MissingFiles.Count
        }
    }
    forensic_data = @{
        file_system = @{
            total_files = $FileCount
            total_folders = $FolderCount
            total_items = $FileCount + $FolderCount
        }
    }
    verification_result = @{
        overall_status = $Status
        is_complete = ($Status -eq "full")
        requires_attention = ($Status -ne "full")
        exit_code = if ($Status -eq "full") { 0 } elseif ($Status -eq "partial") { 1 } else { 2 }
    }
}

# Ensure logs directory exists
$LogsDir = Split-Path $ReportPath -Parent
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
}

# Save report
$Report | ConvertTo-Json -Depth 4 | Out-File $ReportPath -Encoding UTF8
Write-Host "  Report saved to: $ReportPath" -ForegroundColor Green

# Step 7: Final summary
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "VERIFICATION COMPLETE" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "RESULT: $($Status.ToUpper())" -ForegroundColor $StatusColor
Write-Host ""

if ($Status -eq "full") {
    Write-Host "✓ All expected files found" -ForegroundColor Green
    Write-Host "✓ Craftsman IDE appears complete" -ForegroundColor Green
} elseif ($Status -eq "partial") {
    Write-Host "⚠ Some files missing: $($MissingFiles -join ', ')" -ForegroundColor Yellow
    Write-Host "⚠ Partial installation detected" -ForegroundColor Yellow
} else {
    Write-Host "✗ Major files missing" -ForegroundColor Red
    Write-Host "✗ Incomplete installation" -ForegroundColor Red
}

Write-Host ""
Write-Host "SUMMARY:" -ForegroundColor White
Write-Host "  Location: $TargetFolder" -ForegroundColor Gray
Write-Host "  Files found: $($FoundFiles.Count)/$($ExpectedFiles.Count)" -ForegroundColor Gray
Write-Host "  Total items: $($FileCount + $FolderCount)" -ForegroundColor Gray
Write-Host "  Report: $ReportPath" -ForegroundColor Gray

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Atomic verification complete" -ForegroundColor Cyan
Write-Host "PowerShell commands only - No manual navigation" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Exit with appropriate code
if ($Status -eq "full") { exit 0 }
elseif ($Status -eq "partial") { exit 1 }
else { exit 2 }
