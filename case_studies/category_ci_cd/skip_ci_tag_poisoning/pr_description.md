---
tags: [ci-cd, skip-ci, tag-poisoning, release, github-actions]
register: technical
---

# CS_CICD_001: [skip ci] Tag Poisoning

## Root Cause

`pr40-canonical-presence.yml` line 84 commits with `[skip ci]` after every push to main.
HEAD of main is always a `[skip ci]` commit. Tags on HEAD inherit the skip.

## Fix

`create-release.yml` walks `git log` backwards to find the first commit
without `[skip ci]` and tags THAT commit. Also triggers `release.yml`
via `workflow_dispatch` as backup.

`release.yml` is updated to accept a `tag` input on `workflow_dispatch`, allowing
a specific tag to be built even when HEAD contains `[skip ci]`.

## Falsification

Tag a `[skip ci]` commit → release workflow must NOT fire.
Tag a non-`[skip ci]` commit → release workflow MUST fire and produce binaries.
