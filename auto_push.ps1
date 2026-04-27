  
$repoPath = "C:\Users\Aidor\oe-local"  
Set-Location $repoPath  
  
while ($true) {  
    $status = git status --porcelain  
    if ($status) {  
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"  
        $fileCount = ($status -split "`n").Count  
        git add -A  
        git commit -m "auto: $fileCount files changed at $timestamp"  
        git pull --rebase origin main 
        git push origin main  
        Write-Host "[$timestamp] Pushed $fileCount changes"  
    }  
    Start-Sleep -Seconds 30  
}