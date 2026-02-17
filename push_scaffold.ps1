<#
push_scaffold.ps1
Create branch, stage explicit scaffold files, commit, push, and optionally open draft PR.
Run from: C:\Users\Aidor\Documents\orthogonal-engineering-clean
#>

param(
    [string]$RepoPath = "C:\Users\Aidor\Documents\orthogonal-engineering-clean",
    [string]$BranchName = "feature/merkle-scaffold",
    [switch]$CreatePR = $true
)

Set-StrictMode -Version Latest

# Ensure repo exists
if (-not (Test-Path $RepoPath)) {
    Write-Error "Repo path not found: $RepoPath"; exit 2
}
Push-Location $RepoPath

# Safety: abort if there are uncommitted changes
$unstaged = git status --porcelain
if ($unstaged) {
    Write-Host "Found uncommitted changes in repository:"
    Write-Host $unstaged
    Write-Host ""
    Write-Host "Please review, stash, or commit local changes you want to keep, then re-run this script."
    Pop-Location
    exit 3
}

# Create branch from origin/main
git fetch origin
git checkout -b $BranchName

# Explicit file list to stage (only stage scaffold/docs/examples/tests)
$files = @(
    "cli.py",
    "canonicalizer.py",
    "hasher.py",
    "merkle.py",
    "manifest.py",
    "logger.py",
    "handling_pipeline.py",
    "backup.py",
    "utils.py",
    "core/alpha_omega_finalizer.py",
    "config/schema.yaml",
    "requirements.txt",
    "README.md",
    "docs/IDE_AI_RUNBOOK.md",
    "docs/SAFE_OPERATIONS.md",
    "examples/ide_ai_runner_template.ps1",
    "examples/ide_ai_runner_template.py",
    "examples/cas_example.jsonl",
    "examples/log_analysis_example.py",
    "examples/sample_handling_snippet.meta",
    "tests/test_canonicalizer.py",
    "tests/test_hasher.py",
    "tests/test_merkle.py",
    "tests/test_manifest.py",
    "tests/test_handling_pipeline.py",
    "tests/test_alpha_omega_finalizer.py"
)

# Stage files that actually exist
$toAdd = @()
foreach ($f in $files) {
    if (Test-Path $f) {
        $toAdd += $f
    } else {
        Write-Host "Warning: file not found (skipping): $f"
    }
}

if ($toAdd.Count -eq 0) {
    Write-Error "No scaffold files found to add. Ensure files exist in $RepoPath"; Pop-Location; exit 4
}

Write-Host "Staging the following scaffold files:"
$toAdd | ForEach-Object { Write-Host " - $_" }

git add -- $toAdd

$commitMessage = "Add deterministic Merkle-rooted pipeline scaffold, AlphaOmegaFinalizer, runbook, examples, and tests (dry-run default; backups mandatory)"
git commit -m $commitMessage

git push -u origin $BranchName

if ($CreatePR) {
    $gh = Get-Command gh -ErrorAction SilentlyContinue
    if ($null -ne $gh) {
        $prTitle = "Add deterministic Merkle-rooted pipeline scaffold and runbook (dry-run default)"
        $prBody = @"
This PR adds the deterministic pipeline scaffold, a local-only AlphaOmegaFinalizer, runbook, examples and unit tests.

Safety notes:
- Default behavior is dry-run; --apply is required to make any modifications.
- Backups are mandatory before any destructive write and are created locally.
- Do NOT commit or include user chat exports (e.g., C:\Users\Aidor\Downloads\ai_exports) in this PR — that path is referenced in docs as an example only.
- Redaction hooks are included as disabled stubs; users must configure local classifiers for stronger redaction.
- No network auto-push or auto-merge operations are included.
"@
        gh pr create --title $prTitle --body $prBody --base main --draft
        Write-Host "Draft PR opened using gh."
    } else {
        Write-Host "gh CLI not found; branch pushed but PR not created. Use GitHub web UI or gh to open a PR."
    }
}

Pop-Location
Write-Host "Done. Branch pushed: $BranchName"