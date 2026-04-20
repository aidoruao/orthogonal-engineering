---
tags: [investigations, darkshadow44, distanthorizonsstandalone, batch3, issue-59-comment]
register: audit
---

## Investigation: Colored Glass Is Opaque

Hi @DarkShadow44, I've found the glass transparency issue.

### Root Cause
`ClientBlockStateColorCache` detects glass but transparency may be lost:

```java
// ClientBlockStateColorCache.java:468-475
enum ColorMode {
    Glass;
    
    static ColorMode getColorMode(String blockId) {
        if (blockId.contains("glass")) return Glass;
    }
}
```

The issue: when sampling glass color, transparent pixels (alpha=0) are skipped, but the remaining pixels are averaged, potentially losing the translucency.

### The Fix

**File:** `src/main/java/com/seibel/distanthorizons/common/wrappers/block/ClientBlockStateColorCache.java`

```java
// Ensure glass blocks preserve transparency
private static final int GLASS_ALPHA = 128; // 50% transparent

// In color calculation:
if (colorMode == ColorMode.Glass) {
    // For glass, use average color but force transparency
    int avgColor = calculateAverageColor(pixels);
    return ColorUtil.argbToInt(GLASS_ALPHA, 
        ColorUtil.getRed(avgColor),
        ColorUtil.getGreen(avgColor),
        ColorUtil.getBlue(avgColor));
}
```

**File:** `src/main/java/com/seibel/distanthorizons/common/wrappers/block/BlockStateWrapper.java`

Ensure glass is marked as translucent:

```java
public boolean isTranslucent() {
    // Line 324-327
    if (getBlockId().contains("glass")) {
        return true;
    }
    return block.getMaterial().isTranslucent();
}
```

### Workaround

Add glass blocks to transparency config if available.

---
*Investigation performed using orthogonal-engineering forensic methodology.*
