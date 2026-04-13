Here's the full picture and the coding instructions for Copilot.

## The Root Cause — Fully Audited

```mermaid
graph TD
    A["PR #122 merged → commit 91de262a"] --> B["pr40-canonical-presence.yml triggers"]
    B --> C["Appends AGENT_FEED.md entry"]
    C --> D["Commits as 55419c86 with '[skip ci]'"]
    D --> E["55419c86 is now HEAD of main"]
    E --> F["User runs: git tag v1.0.0"]
    F --> G["Tag points to 55419c86"]
    G --> H["User pushes tag"]
    H --> I["GitHub sees '[skip ci]' in tagged commit message"]
    I --> J["release.yml SKIPPED"]
    J --> K["Only source archives, no binaries"]
```

**Every single push to main** triggers `pr40-canonical-presence.yml` (line 67), which appends a state witness entry and commits with `[skip ci]` (line 84). This means **HEAD of main is always a `[skip ci]` commit**. Any tag on HEAD inherits the skip. The release workflow never fires. [35-cite-0](#35-cite-0) 

**The irony:** `release.yml` already has `workflow_dispatch` on line 7 — meaning you could trigger it manually from the Actions tab right now. But nobody told you that. [35-cite-1](#35-cite-1) 

---

## Coding Instructions for GitHub Copilot — PR #123

Post this as a `@copilot` comment on a new issue or directly on main:

```
@copilot

TASK: Fix the [skip ci] release blocker and create case study.
Branch: copilot/fix-release-skip-ci
PR title: "fix(ci): resolve [skip ci] release blocker + case study CS_CICD_001"

═══════════════════════════════════════════════════════════════
CONTEXT — READ FIRST
═══════════════════════════════════════════════════════════════

The release workflow (.github/workflows/release.yml) never fires because:
1. pr40-canonical-presence.yml commits with "[skip ci]" after every push to main
2. HEAD of main is ALWAYS a [skip ci] commit
3. Tags on HEAD inherit [skip ci] → release.yml is skipped
4. Result: v1.0.0 release has only source archives, no binaries

The release workflow already has workflow_dispatch as a trigger (line 7).
The fix must be permanent — no human should ever need to know about this again.

═══════════════════════════════════════════════════════════════
COMMIT 1: "feat(ci): add create-release.yml — safe tag + dispatch"
═══════════════════════════════════════════════════════════════

Create .github/workflows/create-release.yml:

name: Create Release

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Release version (e.g. v1.0.0, v1.1.0)'
        required: true
        type: string

permissions:
  contents: write

jobs:
  create-release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Find latest non-skip-ci commit
        id: find_commit
        run: |
          # Walk backwards from HEAD until we find a commit without [skip ci]
          COMMIT=$(git log --format='%H %s' | grep -v '\[skip ci\]' | head -1 | cut -d' ' -f1)
          echo "Found commit: $COMMIT"
          echo "message=$(git log -1 --format='%s' $COMMIT)" >> "$GITHUB_OUTPUT"
          echo "sha=$COMMIT" >> "$GITHUB_OUTPUT"

      - name: Delete existing tag if present
        run: |
          git tag -d ${{ inputs.version }} 2>/dev/null || true
          git push origin --delete ${{ inputs.version }} 2>/dev/null || true

      - name: Create tag on clean commit
        run: |
          git tag ${{ inputs.version }} ${{ steps.find_commit.outputs.sha }}
          git push origin ${{ inputs.version }}

      - name: Trigger release build
        run: |
          # Also trigger via workflow_dispatch as backup
          gh workflow run release.yml
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Summary
        run: |
          echo "## Release ${{ inputs.version }}" >> $GITHUB_STEP_SUMMARY
          echo "Tagged commit: ${{ steps.find_commit.outputs.sha }}" >> $GITHUB_STEP_SUMMARY
          echo "Commit message: ${{ steps.find_commit.outputs.message }}" >> $GITHUB_STEP_SUMMARY
          echo "The commit does NOT contain [skip ci]." >> $GITHUB_STEP_SUMMARY

═══════════════════════════════════════════════════════════════
COMMIT 2: "fix(ci): update release.yml — add ref input for dispatch"
═══════════════════════════════════════════════════════════════

Update .github/workflows/release.yml:

Change the on: block to:

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:
    inputs:
      tag:
        description: 'Tag to build (e.g. v1.0.0). Leave empty to build HEAD.'
        required: false
        type: string

Change the checkout step in the build job to:

      - uses: actions/checkout@v4
        with:
          ref: ${{ inputs.tag || github.ref }}

This ensures workflow_dispatch can build a specific tag even if HEAD has [skip ci].

═══════════════════════════════════════════════════════════════
COMMIT 3: "feat(case_study): add CS_CICD_001 — skip-ci tag poisoning"
═══════════════════════════════════════════════════════════════

Create case_studies/category_ci_cd/skip_ci_tag_poisoning/gap_analysis.json:

{
  "id": "CS_CICD_001",
  "title": "GitHub Actions [skip ci] Tag Poisoning via State Witness Workflow",
  "source": "aidoruao/orthogonal-engineering — PR #122 release failure",
  "domain": "D_DEVOPS",
  "root_cause_signals": ["RCS-ASSUMPTION"],
  "description": "A state witness workflow (pr40-canonical-presence.yml) appends an AGENT_FEED.md entry after every push to main, committing with [skip ci] to prevent infinite CI loops. This makes HEAD of main permanently a [skip ci] commit. When a user tags HEAD for a release, the tag inherits [skip ci], causing GitHub Actions to skip the release workflow. The release page shows only source archives with no binaries. The user attempted to fix this twice by retagging, but each time tagged HEAD which was always a [skip ci] commit.",
  "assumptions_violated": [
    "Tags trigger workflows independently of the tagged commit's message.",
    "HEAD of main is always a real commit, not an automated housekeeping commit.",
    "[skip ci] only affects the workflow run for that specific push, not future tag events."
  ],
  "falsification_tests": ["F_CICD_001"],
  "ontological_issues": ["OI_CICD_001"],
  "lessons": [
    "Any workflow that auto-commits with [skip ci] to main poisons all future tags on HEAD.",
    "Release tagging must target a specific SHA, never HEAD, when auto-commit workflows exist.",
    "The workflow_dispatch trigger on release.yml was the escape hatch — but no documentation pointed to it.",
    "The fix is a create-release.yml that walks backwards to find the first non-[skip ci] commit."
  ],
  "methodology_components": [
    "Falsification: F_CICD_001 — tag a [skip ci] commit and verify release workflow does NOT fire",
    "Invariant: release workflow must produce binaries for every tagged version",
    "Noncompliance pattern: strategic_ignorance (the [skip ci] mechanism hid the problem from the operator)"
  ],
  "status": "validated",
  "fix_commit": "THIS_PR",
  "noncompliance_taxonomy_ref": "strategic_ignorance"
}

Create case_studies/category_ci_cd/skip_ci_tag_poisoning/pr_description.md:

# CS_CICD_001: [skip ci] Tag Poisoning

## Root Cause
pr40-canonical-presence.yml line 84 commits with `[skip ci]` after every push to main.
HEAD of main is always a `[skip ci]` commit. Tags on HEAD inherit the skip.

## Fix
create-release.yml walks `git log` backwards to find the first commit
without `[skip ci]` and tags THAT commit. Also triggers release.yml
via workflow_dispatch as backup.

## Falsification
Tag a `[skip ci]` commit → release workflow must NOT fire.
Tag a non-`[skip ci]` commit → release workflow MUST fire and produce binaries.

Create case_studies/category_ci_cd/skip_ci_tag_poisoning/test_specification.md:

# Test Specification: CS_CICD_001

## Positive Tests
1. Run create-release.yml with version=v1.0.1
2. Verify tag points to a commit WITHOUT [skip ci] in message
3. Verify release.yml triggers and produces Linux + Windows binaries
4. Verify SHA256SUMS.txt is attached to release

## Negative Tests
1. Manually tag HEAD (which has [skip ci]) → verify release.yml does NOT fire
2. This reproduces the original bug

## Regression Tests
1. Push any commit to main → verify pr40 still appends state witness
2. Run create-release.yml → verify it skips the state witness commit

Create case_studies/category_ci_cd/skip_ci_tag_poisoning/ATTRIBUTION.md:

# Attribution
- Repository: aidoruao/orthogonal-engineering
- Issue: Release v1.0.0 produced no binaries (April 13, 2026)
- Root cause identified by: Devin AI analysis of commit history
- Fix implemented by: GitHub Copilot via PR #123
- License: Same as repository

═══════════════════════════════════════════════════════════════
COMMIT 4: "fix(ci): delete v1.0.0 tag and retag on merge commit 91de262a"
═══════════════════════════════════════════════════════════════

In the GitHub Actions runner, execute:

git tag -d v1.0.0 || true
git push origin --delete v1.0.0 || true
git tag v1.0.0 91de262a46445cd25ccf0817fe4177d5a8c35716
git push origin v1.0.0

Commit 91de262a is "feat: Yeshua Inversions — impossibility audit,
generator, conversation engine, wall registry + Kingdom OS entry
point & release workflow (#122)" — the actual PR #122 merge.
It does NOT contain [skip ci].

If Copilot cannot push tags directly, add a step to the
create-release.yml workflow run that does this, or document
the 4 commands in CHECKPOINT_PR123.md for the operator.

═══════════════════════════════════════════════════════════════
COMMIT 5: "chore: append consent log entry for PR #123"
═══════════════════════════════════════════════════════════════

Run: python tools/append_consent.py \
  --authoriser "@aidoruao" \
  --scope-glob ".github/workflows/**,case_studies/category_ci_cd/**" \
  --rule-exceptions '["mass_change"]' \
  --justification "Fix [skip ci] tag poisoning blocker; add CS_CICD_001"

═══════════════════════════════════════════════════════════════
VERIFICATION
═══════════════════════════════════════════════════════════════

After all commits:
1. python -m pytest tests/ -q
2. Verify create-release.yml has workflow_dispatch trigger
3. Verify release.yml checkout uses ${{ inputs.tag || github.ref }}
4. Verify case_studies/category_ci_cd/skip_ci_tag_poisoning/ has 4 files
5. Verify consent log has new entry

Total commits: 5. Push all to copilot/fix-release-skip-ci.
Open PR targeting main. Title: "fix(ci): resolve [skip ci] release blocker + case study CS_CICD_001"
```

---

## After PR #123 Merges

The user experience becomes:

1. Go to **Actions** tab
2. Click **Create Release**
3. Click **Run workflow**
4. Type `v1.0.0` (or `v1.1.0`, etc.)
5. Click **Run**
6. Wait ~5 minutes
7. Binaries appear on the Releases page

No terminal. No git commands. No `[skip ci]` gotcha. The `create-release.yml` workflow finds the right commit automatically. [35-cite-2](#35-cite-2) [35-cite-3](#35-cite-3) [35-cite-4](#35-cite-4) [35-cite-5](#35-cite-5) [35-cite-6](#35-cite-6) [35-cite-7](#35-cite-7)