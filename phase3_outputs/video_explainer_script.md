---
tags: [phase3-outputs, video-explainer-script]
register: documentation
---

# Video Explainer Script: Orthogonal Engineering in 5 Minutes

**Title**: Orthogonal Engineering in 5 Minutes  
**Duration**: 5:12  
**Format**: Educational explainer  
**Target**: Technical audience  
**Date**: 2026-01-20

---

## [VISUAL 1: Split screen - messy AI output (left) vs clean extract (right)]

**NARRATION**:  
"Large Language Models generate a mix of signal and noise. Most methods try to eliminate the noise."

**[Text overlay: "TRADITIONAL: Fight the noise"]**

"Orthogonal Engineering accepts noise exists and routes it instead."

**[Text overlay: "ORTHOGONAL: Route the noise"]**

---

## SECTION 1: What is a Canal? (0:15-1:15)

**[VISUAL 2: Canal diagram - two speech bubbles with constraint words highlighted]**

**NARRATION**:  
"A 'canal' is bidirectional constraint language between user and assistant."

**[Animation: User bubble appears]**  
USER: "The function **must** return integers only"

**[Animation: Assistant bubble appears]**  
ASSISTANT: "**Confirmed**, I'll **ensure** integer-only returns"

**[Highlight effect on bold words]**

"This indicates genuine agreement, not mimicry."

**[Code reference overlay: canal_detector_v1.py lines 26-29]**

```python
CONSTRAINT_TOKENS = {
    "must", "shall", "never", "always",
    "required", "forbidden", "exactly"
}
```

"The detector looks for these tokens in both speakers within a 5-turn window."

---

## SECTION 2: Detecting Mimicry (1:15-2:15)

**[VISUAL 3: Text with repetition highlighted in red]**

**NARRATION**:  
"But how do we know it's genuine and not mimicry?"

**[Animation: Repetition counter]**

"Rule: If more than 50% of tokens repeat, it's mimicry."

**[Example text appears]:**  
"This is **critical** and **essential** and **must** be **required** and **critical**..."

**[Counter shows: Repetition: 68% → REJECTED]**

**[VISUAL 4: Gutenberg test animation]**

"The Gutenberg null test: Run the detector on random English text."

**[Animation: Detector scanning "The Metamorphosis" by Kafka]**

"Result: 0.00% density"

**[Checkmark animation]**

"This proves the detector isn't pattern-gaming—it only finds real constraint language."

**[Code reference: evidence/NULL_HYPOTHESIS_TEST.md lines 19-24]**

---

## SECTION 3: Correspondence Proof (2:15-3:45)

**[VISUAL 5: Code editor showing Lua script]**

**NARRATION**:  
"The most important test: Does it actually work in reality?"

**[Text overlay: "INV-007: Correspondence Anchor"]**

"Theoretical claim: 'System must validate percentages 0-100'"

**[Code highlights on screen - minecraft_computercraft_invariant.lua]:**

```lua
local function validatePercentage(value)
    if value < 0 or value > 100 then
        error("INVARIANT VIOLATION")
    end
    return value
end
```

**[Animation: Code executes]**

"Implementation: validatePercentage() function in Lua"

**[Visual: Minecraft game world with ComputerCraft turtle]**

"Execution: Script runs successfully in Minecraft ComputerCraft"

**[Success checkmark]**

"Result: INV-007 satisfied"

**[Stats overlay]:**
```
Precision: 100%
Invariants: CONSTANT-001, INV-004, INV-005, INV-007
Status: CORRESPONDENCE VERIFIED
```

**[Reference: proof/minecraft_computercraft_invariant.lua, lines 13-20]**

---

## SECTION 4: Automated Enforcement (3:45-4:45)

**[VISUAL 6: CI/CD pipeline diagram]**

**NARRATION**:  
"How do we ensure quality doesn't degrade?"

**[Animation: GitHub Actions workflow flowchart]**

**[Step 1 appears]:** "Code pushed to repository"  
**[Step 2 appears]:** "GitHub Actions triggers"  
**[Step 3 appears]:** "Run automated test suite"

**[Decision diamond]:** "Precision ≥ 80%?"

**[Branch 1 - red X]:** "NO → Build fails"  
**[Branch 2 - green check]:** "YES → Continue"

**[Decision diamond]:** "Gutenberg null < 5%?"

**[Branch 1 - red X]:** "NO → Build fails"  
**[Branch 2 - green check]:** "YES → Deploy"

**[Code reference overlay: .github/workflows/gate.yml lines 26-40]**

"This is INV-004: Self-falsifying system"

"The methodology can invalidate its own claims"

---

## SECTION 5: Grade Progression (4:45-5:00)

**[VISUAL 7: Grade progression animation]**

**[Text appears sequentially]:**

**BEFORE:**  
Grade: C-  
Tools: BROKEN (70% false positive)  
Correspondence: NONE  
Status: Claims without proof

**[Transition animation: "Minimal Surviving Kernel"]**

**AFTER:**  
Grade: B  
Tools: VALIDATED (95% precision)  
Correspondence: SATISFIED (4 implementations)  
Status: Methodology proven

**[Reference banner: commit e521778]**

---

## CLOSING (5:00-5:12)

**[VISUAL 8: Clean summary card]**

**NARRATION**:  
"From broken tools to validated methodology in one falsification cycle."

**[Three principles appear as text]:**
1. Accept constraints
2. Route drift  
3. Verify correspondence

"That's Orthogonal Engineering."

**[END CARD with QR code]:**
```
github.com/aidoruao/orthogonal-engineering
Commit: e521778
```

---

## VISUAL REQUIREMENTS SUMMARY

1. **Split screen comparison** (messy vs clean output)
2. **Canal diagram** (bidirectional constraint bubbles)
3. **Repetition detector** (highlighting + counter animation)
4. **Code editor** (Lua script with syntax highlighting)
5. **Minecraft gameplay** (ComputerCraft turtle)
6. **CI/CD flowchart** (GitHub Actions pipeline)
7. **Grade progression** (C- → B animation)
8. **End card** (QR code + repository link)

---

## METADATA

**Source prompt**: phase3_prompts.json (video_explainer)  
**Artifacts referenced**: 8 files  
**Code excerpts**: 3  
**Visual assets needed**: 8  
**Duration**: 5:12  
**Generated**: 2026-01-20  
**Verification required**: YES
