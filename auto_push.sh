#!/bin/bash  
cd ~/oe-local  
while true; do  
    if [ -d ".git/rebase-merge" ]; then  
        git rebase --abort 2>/dev/null  
        git checkout main 2>/dev/null  
    fi  
    status=$(git status --porcelain)  
    if [ -n "$status" ]; then  
        timestamp=$(date '+%Y-%m-%d %H:%M:%S')  
        filecount=$(echo "$status" | wc -l)  
        git add -A  
        git commit -m "auto: $filecount files changed at $timestamp"  
        git pull --rebase origin main 2>/dev/null || {  
            git rebase --abort 2>/dev/null  
            git fetch origin main  
            git reset --soft origin/main  
            git add -A  
            git commit -m "auto: $filecount files changed at $timestamp"  
        }  
        git push origin main 2>/dev/null || git push --force-with-lease origin main  
        echo "[$timestamp] Pushed $filecount changes"  
    fi  
    sleep 30  
done
