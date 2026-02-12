# JSONL DEPLOYMENT TO REPO
# Generated: 2026-02-12

$ErrorActionPreference = "Stop"

Write-Host "=== DEPLOYING JSONL FILES TO REPO ===" -ForegroundColor Cyan
Write-Host ""

# Source: Downloads (after you download from Claude)
$downloadsBase = "C:\Users\Aidor\Downloads"

# Destination: Repo
$repoBase = "C:\Users\Aidor\Documents\orthogonal-engineering-clean\GptAudit"

# Files to deploy
$files = @(
    "chatgpt_4a.jsonl",
    "chatgpt_4a_manifest.json",
    "notebooklm_1a.jsonl",
    "notebooklm_1a_manifest.json"
)

foreach ($file in $files) {
    $srcPath = Join-Path $downloadsBase $file
    $dstPath = Join-Path $repoBase $file
    
    if (Test-Path $srcPath) {
        Copy-Item -Path $srcPath -Destination $dstPath -Force
        $hash = (Get-FileHash -Path $dstPath -Algorithm SHA256).Hash
        Write-Host "✅ $file" -ForegroundColor Green
        Write-Host "   SHA-256: $($hash.Substring(0,16))..." -ForegroundColor Gray
    } else {
        Write-Host "✗ $file (not found in Downloads)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== CREATING DOWNLOAD PACKAGE ===" -ForegroundColor Cyan
Write-Host ""

# Create NotebookLM upload folder
$packageDir = "C:\Users\Aidor\Downloads\NotebookLM_NEW_FILES"
New-Item -ItemType Directory -Path $packageDir -Force | Out-Null

# Copy NEW files to package
$newFiles = @(
    "06_ChatGPT_Instance_4a_HASHED.md",
    "07_NotebookLM_Instance_1a_HASHED.md",
    "chatgpt_4a.jsonl",
    "chatgpt_4a_manifest.json",
    "notebooklm_1a.jsonl",
    "notebooklm_1a_manifest.json"
)

foreach ($file in $newFiles) {
    $srcPath = Join-Path $repoBase $file
    $dstPath = Join-Path $packageDir $file
    
    if (Test-Path $srcPath) {
        Copy-Item -Path $srcPath -Destination $dstPath -Force
        Write-Host "✅ $file → NotebookLM package" -ForegroundColor Green
    } else {
        Write-Host "⚠️  $file not found in repo" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=== COMPLETE ===" -ForegroundColor Green
Write-Host "Package location: $packageDir" -ForegroundColor White
Write-Host ""
Write-Host "UPLOAD TO NOTEBOOKLM:" -ForegroundColor Cyan
Get-ChildItem -Path $packageDir | ForEach-Object {
    Write-Host "  - $($_.Name)" -ForegroundColor White
}
