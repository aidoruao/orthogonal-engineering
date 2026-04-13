---
tags: [ci-cd, skip-ci, tag-poisoning, test-specification]
register: technical
---

# Test Specification: CS_CICD_001

## Positive Tests

1. Run `create-release.yml` with `version=v1.0.1`
2. Verify tag points to a commit WITHOUT `[skip ci]` in message
3. Verify `release.yml` triggers and produces Linux + Windows binaries
4. Verify `SHA256SUMS.txt` is attached to release

## Negative Tests

1. Manually tag HEAD (which has `[skip ci]`) → verify `release.yml` does NOT fire
2. This reproduces the original bug

## Regression Tests

1. Push any commit to main → verify pr40 still appends state witness
2. Run `create-release.yml` → verify it skips the state witness commit
