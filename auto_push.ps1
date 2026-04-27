$repoPath = "C:\Users\Aidor\oe-local"  
Set-Location $repoPath  
  
while ($true) {  
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
        git pull --rebase origin main 2>$null  
        if ($LASTEXITCODE -ne 0) {  
            git rebase --abort 2>$null  
            git fetch origin main  
            git reset --soft origin/main  
            git add -A  
            git commit -m "auto: $fileCount files changed at $timestamp"  
        }  
        git push origin main 2>$null  
        if ($LASTEXITCODE -ne 0) {  
            git push --force-with-lease origin main  
        }  
        Write-Host "[$timestamp] Pushed $fileCount changes"  
    }  
    Start-Sleep -Seconds 30  
}  
