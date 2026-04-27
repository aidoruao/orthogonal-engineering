$repoPath = "C:\Users\Aidor\oe-local"  
Set-Location $repoPath  
  
while ($true) {  
    # Auto-fix stuck rebase  
    if (Test-Path ".git\rebase-merge") {  
        git rebase --abort 2>$null  
        git checkout main 2>$null  
    }  
    $status = git status --porcelain  
    if ($status) {  
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"  
        $fileCount = ($status -split "`n").Count  
        git add -A  
        git commit -m "auto: $fileCount files changed at $timestamp"  
        $pullResult = git pull --rebase origin main 2>&1  
        if ($LASTEXITCODE -ne 0) {  
            git rebase --abort 2>$null  
            git checkout main 2>$null  
        } else {  
            git push origin main  
            Write-Host "[$timestamp] Pushed $fileCount changes"  
        }  
    }  
    Start-Sleep -Seconds 30  
}  
