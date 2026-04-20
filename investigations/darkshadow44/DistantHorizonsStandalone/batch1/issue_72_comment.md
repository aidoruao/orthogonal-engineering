---
tags: [investigations, darkshadow44, distanthorizonsstandalone, batch1, issue-72-comment]
register: audit
---

## Investigation: GTNH Crash on Load

Hi @DarkShadow44, I've investigated this GTNH compatibility issue. Here's my analysis:

### Root Cause
The `GTCompat` class is instantiated without version validation in `ForgeMain.java:97-99`:

```java
if (Loader.isModLoaded("gregtech") && enableGTCompat()) {
    gtCompat = new GTCompat();
}
```

The `enableGTCompat()` method only checks if `IBlockWithTextures` class exists:

```java
// ForgeMain.java:71-78
private boolean enableGTCompat() {
    try {
        Class.forName("gregtech.api.interfaces.IBlockWithTextures");
        return true;
    } catch (ClassNotFoundException e) {
        return false;
    }
}
```

**The problem:** Class existence doesn't guarantee API compatibility across GTNH versions.

### The Fix
Add version checking similar to `AngelicaCompat.verifyAngelicaVersion()`:

**File:** `src/main/java/com/seibel/distanthorizons/forge/ForgeMain.java`
```java
// Add near line 43:
public static final String MINIMUM_GT_VERSION = "5.09.51.0";

// Modify init() method around line 97:
if (Loader.isModLoaded("gregtech") && enableGTCompat()) {
    try {
        gtCompat = new GTCompat();
        gtCompat.verifyGTVersion(); // Add this method
    } catch (Exception e) {
        LOGGER.warn("GT compatibility disabled due to version mismatch: {}", e.getMessage());
        gtCompat = null;
    }
}
```

### Why This Works
- GTNH 5.09.50.x may have breaking API changes vs 5.09.51.x
- Graceful degradation allows the mod to function without GT-specific features
- Pattern already proven with Angelica version checking

### How to Verify
1. Test with GTNH 5.09.50.x → should no longer crash (GTCompat disabled)
2. Test with GTNH 5.09.51.x+ → should work with GTCompat enabled
3. Check `logs/fml-client-latest.log` for "GT compatibility disabled" message

### Request for More Info
Could you provide the crash log? Specifically looking for:
- `NoClassDefFoundError` or `NoSuchMethodError` mentioning GT classes
- Stack trace showing `GTCompat.<init>` or related methods

---
*Investigation performed using orthogonal-engineering forensic methodology.*
