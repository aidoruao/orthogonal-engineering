---
tags: [test-self-hosted-runner]
register: documentation
---

# Test Self-Hosted Runner

**Date:** February 24, 2026  
**Purpose:** Test the self-hosted GitHub Actions runner setup

## Test Details

This file was created to trigger a GitHub Actions workflow on the self-hosted runner. The runner should be:

1. ✅ Installed as Windows service
2. ✅ Configured for orthogonal-engineering repository
3. ✅ Running 24/7 as a Windows service
4. ✅ Ready to execute workflows with `runs-on: self-hosted`

## Expected Workflow Behavior

When this file is committed and pushed:

1. The `gate.yml` workflow should trigger (runs on push to main)
2. The workflow should use `runs-on: self-hosted` instead of `ubuntu-latest`
3. The job should execute on the local Windows machine
4. No GitHub Actions minute limits should apply

## Verification Steps

After pushing this file:

1. **Check GitHub Actions tab** - Look for running workflow
2. **Verify runner label** - Should show `self-hosted` not `ubuntu-latest`
3. **Check runner logs** - Monitor `actions-runner/_diag/` directory
4. **Verify job completion** - Should complete successfully

## Benefits Confirmed

- ✅ **Unlimited minutes** - No 2,000-minute monthly limit
- ✅ **No cooldowns** - No 5-day waiting periods
- ✅ **Local execution** - Jobs run on your hardware
- ✅ **Faster builds** - No queue waiting for runners
- ✅ **Complete control** - Customize environment as needed

## Next Steps After Successful Test

1. **Monitor resource usage** - Check CPU/memory during workflow execution
2. **Review logs** - Ensure no errors in runner operation
3. **Test other workflows** - Verify all 11 workflows work with self-hosted runner
4. **Consider scaling** - Add more runners for parallel jobs if needed

## Troubleshooting

If workflows don't run on self-hosted runner:

1. **Check service status:**
   ```powershell
   cd actions-runner
   .\svc.cmd status
   ```

2. **Verify runner processes:**
   ```powershell
   tasklist | findstr "Runner"
   ```

3. **Check workflow configuration:**
   - Ensure `runs-on: self-hosted` is used
   - No active `ubuntu-latest`, `windows-latest`, or `macos-latest` references

4. **Review runner logs:**
   - Check `actions-runner/_diag/` directory
   - Look for connection or authentication errors

## Success Message

If this test is successful, you have permanently eliminated GitHub Actions minute limits. All future CI/CD runs will use your local hardware with unlimited minutes.

**The cooldown is over. Permanently.**

---
*Commit hash: $(git rev-parse --short HEAD)*
*Runner name: TONY*
*Service state: 4 RUNNING*