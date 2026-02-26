# fix_windows_execution_policy.ps1
# Run as Administrator to fix self-hosted runner execution policy

Write-Host "🔧 Fixing Windows Execution Policy for GitHub Self-Hosted Runner" -ForegroundColor Cyan

# Check current policy
$current = Get-ExecutionPolicy
Write-Host "Current execution policy: $current" -ForegroundColor Yellow

if ($current -eq "Restricted") {
    Write-Host "Changing to RemoteSigned for CurrentUser..." -ForegroundColor Green
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    Write-Host "✅ Execution policy updated to RemoteSigned" -ForegroundColor Green
} elseif ($current -eq "RemoteSigned") {
    Write-Host "✅ Execution policy already correct (RemoteSigned)" -ForegroundColor Green
} else {
    Write-Host "⚠️ Current policy is $current. Recommended: RemoteSigned" -ForegroundColor Yellow
    $confirm = Read-Host "Change to RemoteSigned? (y/n)"
    if ($confirm -eq 'y') {
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Write-Host "✅ Execution policy updated" -ForegroundColor Green
    }
}

# Test runner script
$runnerScript = ".\run.cmd"
if (Test-Path $runnerScript) {
    Write-Host "`nTesting runner script..." -ForegroundColor Cyan
    & $runnerScript --check
} else {
    Write-Host "`n⚠️ run.cmd not found in current directory" -ForegroundColor Yellow
    Write-Host "Navigate to your runner directory and run this script again" -ForegroundColor Yellow
}

Write-Host "`n✅ Fix complete" -ForegroundColor Cyan
