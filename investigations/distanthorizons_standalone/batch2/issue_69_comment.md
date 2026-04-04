## Investigation: Renderer Error (Needs More Info)

Hi @DarkShadow44, the issue title "Distant Horizons Renderer Error" is too generic to identify the specific cause.

### Information Needed

To properly diagnose this, please provide:

1. **Full error message** from crash/logs
2. **latest.log** or **fml-client-latest.log** excerpt
3. **GPU model** and **driver version**
4. **When does it occur?**
   - At game startup?
   - When loading world?
   - Randomly during gameplay?
   - When changing settings?

### Common Causes

Based on code analysis, renderer errors typically come from:

| Cause | Symptom | Fix |
|-------|---------|-----|
| OpenGL 3.2 not supported | Crash at startup | Update GPU drivers |
| Shader compilation fail | Black screen/pink textures | Disable shaders |
| Out of VRAM | Crash with many mods | Reduce render distance |
| Driver bug | Random crashes | Update drivers |

### Immediate Steps

1. Update GPU drivers to latest
2. Check OpenGL version (should be 3.2+)
3. Try with shaders disabled
4. Try with lower render distance

Once you provide the error log, I can give a specific fix.

---
*Investigation performed using orthogonal-engineering forensic methodology.*
