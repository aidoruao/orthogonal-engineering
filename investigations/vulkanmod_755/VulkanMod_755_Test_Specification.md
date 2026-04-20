---
tags: [investigations, vulkanmod-755, vulkanmod-755-test-specification]
register: audit
---

# VulkanMod #755 Test Specification
## Matrix-Aware Scissor Implementation

### Overview
This document specifies test cases to verify the matrix-aware scissor fix for VulkanMod issue #755.

### Test Environment Requirements
- Minecraft 1.21.1 with VulkanMod installed
- GUI Scale options: 1x, 2x, 3x, 4x
- Debug overlay enabled (F3)
- Various GUI contexts: Inventory, Pause Menu, Creative Menu, Mod Config Screens

---

## Test Cases

### TC-001: Identity Matrix (No Transformation)
**Purpose**: Verify backward compatibility when no transformation is applied

**Setup**:
- Launch Minecraft with default settings
- Set GUI Scale to 1x (no scaling)

**Steps**:
1. Open Inventory
2. Hover over items to trigger tooltips
3. Open Pause Menu
4. Navigate through options

**Expected Results**:
- Scissor rectangles clip correctly at original coordinates
- Tooltips display fully within screen bounds
- No visual glitches in menu rendering
- Behavior identical to pre-fix implementation

**Pass Criteria**:
- All GUI elements render correctly
- No missing or incorrectly clipped content

---

### TC-002: GUI Scale 2x
**Purpose**: Verify scissor works correctly with 2x GUI scaling

**Setup**:
- Set GUI Scale to 2x in Video Settings

**Steps**:
1. Open Inventory
2. Scroll through inventory with mouse wheel
3. Open item tooltips near screen edges
4. Open Creative inventory and scroll through tabs

**Expected Results**:
- Scissor rectangles correctly clip scaled GUI elements
- Inventory scrolling shows proper clipping at container boundaries
- Tooltips render fully without being clipped prematurely

**Pass Criteria**:
- Scissor boundaries align with scaled GUI element boundaries
- No content bleed outside container bounds
- No premature clipping of visible content

---

### TC-003: GUI Scale 3x/4x (High DPI)
**Purpose**: Verify scissor handles extreme scaling

**Setup**:
- Set GUI Scale to 3x or 4x (if display supports)

**Steps**:
1. Repeat TC-002 steps
2. Open mod config screens if available

**Expected Results**:
- Scissor rectangles correctly transform for high scaling factors
- All GUI elements render proportionally

**Pass Criteria**:
- No regression from TC-002
- Performance remains acceptable

---

### TC-004: Scrolled Containers
**Purpose**: Verify scissor works with scrollable content

**Setup**:
- Open Creative inventory
- Open Resource Pack selection screen
- Open any mod with scrollable lists

**Steps**:
1. Scroll through lists rapidly
2. Observe content at scroll boundaries

**Expected Results**:
- Content properly clipped at container boundaries during scroll
- No visible artifacts during rapid scrolling
- Smooth scrolling without flickering

**Pass Criteria**:
- Content clipped precisely at container edges
- No bleeding of off-screen content
- No missing on-screen content

---

### TC-005: Tooltip Boundaries
**Purpose**: Verify tooltips render correctly near screen edges

**Setup**:
- Open Inventory with various items

**Steps**:
1. Hover over items near left screen edge
2. Hover over items near right screen edge
3. Hover over items near top/bottom edges

**Expected Results**:
- Tooltips flip to stay on-screen when near edges
- Tooltips render completely without clipping
- Scissor regions follow tooltip positions

**Pass Criteria**:
- All tooltip text visible
- No tooltip truncation at screen boundaries

---

### TC-006: ModelView Translation
**Purpose**: Verify scissor follows translated geometry

**Setup**:
- Use mods or debug tools that apply GUI translations
- Test with potion effect overlays

**Steps**:
1. Apply translation offsets to GUI rendering
2. Observe scissor behavior

**Expected Results**:
- Scissor rectangles follow translated GUI elements
- Clipping boundaries move with translations

**Pass Criteria**:
- Scissor transforms match geometry transforms

---

### TC-007: Edge Cases
**Purpose**: Verify robustness with extreme values

**Test Scenarios**:
1. **Zero-size scissor**: width=0 or height=0
2. **Negative coordinates**: x<0 or y<0 (clamped to 0)
3. **Oversized scissor**: x+width > framebuffer width
4. **Rapid matrix changes**: Multiple GUI elements with different transforms

**Expected Results**:
- Zero-size scissor: No rendering (valid Vulkan behavior)
- Negative coordinates: Clamped to 0, no crash
- Oversized scissor: Handled by Vulkan extent limits
- Rapid changes: Each element uses correct matrix state

**Pass Criteria**:
- No crashes with extreme values
- Graceful degradation for invalid inputs

---

## Regression Tests

### RT-001: Replay Mod Compatibility
**Purpose**: Ensure fix doesn't break Replay Mod

**Reference**: GL11M.java line 22 mentions previous scissor issues with Replay Mod

**Steps**:
1. Install Replay Mod alongside VulkanMod
2. Record gameplay
3. Replay recording
4. Navigate replay UI

**Expected Results**:
- No invisible menus
- No rendering glitches
- Scissor works correctly in replay UI

---

## Performance Benchmarks

### PB-001: Matrix Transformation Overhead
**Purpose**: Measure performance impact of matrix operations

**Metrics**:
- Frame time with/without fix
- CPU time in setScissor method

**Acceptance Criteria**:
- < 1% frame time increase
- No stuttering during GUI navigation

---

## Debug Verification

### DV-001: Matrix State Inspection
Add temporary debug logging to verify:

```java
// In Renderer.setScissor()
System.out.printf("[Scissor] Input: (%d, %d, %d, %d)%n", x, y, width, height);
System.out.printf("[Scissor] ModelView: %s%n", modelView);
System.out.printf("[Scissor] Output: (%d, %d, %d, %d)%n", 
    transformedX, transformedY, transformedWidth, transformedHeight);
```

**Verify**:
- Identity matrix: Input equals Output
- Scale 2x: Output dimensions are 2x Input
- Translation: Output position is offset by translation

---

## Known Limitations

1. **Rotation**: If ModelView contains rotation, scissor uses bounding box approximation
   - This is acceptable as GUI rarely uses rotation
   - Bounding box ensures content is never clipped prematurely

2. **Non-uniform scale**: Scissor rectangle may be larger than optimal
   - Conservative clipping ensures correctness over precision

3. **Negative scales**: May produce unexpected results
   - Testing required for flipped coordinate systems

---

## Sign-off

| Role | Name | Date | Status |
|------|------|------|--------|
| Implementer | Kimi Code CLI | 2026-04-04 | Implemented |
| Tester | TBD | | Pending |
| Maintainer | xCollateral | | Review Pending |

---

## References

- Issue: VulkanMod #755
- Gap Analysis: `/home/idor/VulkanMod_755_Gap_Analysis.json`
- Implementation: `Renderer.java` method `setScissor()`
