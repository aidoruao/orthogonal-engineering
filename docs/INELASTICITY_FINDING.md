---
tags: [historical-tests, inelasticity, finding, verification]
register: documentation
---

# The Inelasticity Finding — the totals are not the mean of the levels

**Source examined:** `historical_tests/PHASE_4_TRUTH_INELASTICITY_REPORT.md`,
SHA-256 `ed9bcebe75aaa094fcf55ec0e507d32b68625ac2d986590b259f149aac2686b6`.

**Status of the four numbers after this file:** recorded judgements with a
localized gap in their derivation — not machine-checked output. The ordering
6.5 < 6.8 < 7.2 < 7.5 is untouched.

---

## Why this was built

The handoff carried an open item: *"Implementing a scorer that reproduces
6.5/6.8/7.2/7.5 would turn four documentary judgements into checkable output —
and would be the first test of whether the method survives implementation."*

A scorer written to reproduce four known numbers is circular: any weighting
chosen after seeing the targets will hit them. So the scoring was not
implemented. Instead the **reported**, checkable structure was tested: are the
published totals consistent with the published per-category levels, under the
aggregation the report itself names?

They are not.

## The data, as published

From "Debt Breakdown by Category", transcribed verbatim:

```
C₂ (6.5)  High, High, Medium, Medium, Low-Medium, Medium          (6 categories)
C₃ (6.8)  Medium-High, Medium, Medium-High, Low-Medium, Medium, Medium  (6)
C₄ (7.2)  High, High, Medium, Medium-High, Medium, Medium         (6)
C₁ (7.5)  Medium-High, High, Medium, Very High, Medium            (5)
```

C₁ lists **five** categories where the other three list six. A mean over five
and a mean over six are not the same scale, so C₁'s 7.5 is not comparable to the
rest unless a normalization is stated. The report states none. That is a second,
separate defect, and this file does not claim C₁'s total is wrong — it claims the
comparison as written lacks a common basis.

## The premise, and why it is the only reading available

Line 251 of the report:

> **Axis Weighting Implicit:** Equal weighting assumed but debatable

Line 233 of the same report:

> ✅ No hidden criteria or weighting

If the weighting is equal — the only weighting the report names — then each total
is the unweighted mean of its category levels. That is the premise the test
uses. It is an inference from the report's own words, not an assumption imported
from outside, and it is the *weakest* reading available: any other reading
implies a weighting the report does not publish.

## The result

`L1_INELASTICITY.lean` proves it, and the proof needs only C₂ and C₃:

> **`c3_cannot_exceed_c2`** — C₂ is `{H,H,M,M,LM,M}` and C₃ is
> `{MH,M,MH,LM,M,M}`. They differ in exactly two of six positions: two `High`
> became two `Medium-High`. Four levels are identical. Since the scale is
> ordered, `Medium-High ≤ High`, so C₃'s mean cannot exceed C₂'s. The report
> publishes C₃ 0.3 **above** C₂.

The arithmetic, in tenths of a point:

```
means differ by  (2·MH − 2·H) / 6
published gap    +3 tenths
forces           MH − H = +0.9 tenths  (Medium-High worth more than High)
monotonicity     MH ≤ H
```

`no_monotone_fit` states the negation: there is no ordered assignment of values
to the four level words that reproduces all three six-category totals.

### The independent arm

A theorem is evidence about a model. `burden/tools/inelasticity-check.ts`
encodes the same published data separately, computes the contradiction from the
integers, and carries a **round-trip control**: it converts a declared monotone
mapping into totals and back, and requires the mapping to be recovered. Without
that control, an arithmetic bug in the tool would look exactly like a defect in
the report.

```
the C2/C3 contradiction, computed:
  published gap            0.3
  forces Medium-High - High = 0.09
  monotonicity requires    Medium-High <= High

round-trip control:
  mappings that fail to reproduce their own totals: 0
```

`burden/negative/INELASTICITY_FIT_EXISTS.lean` asserts that a fit exists and must
fail to compile. It fails because `decide` proves the arithmetic false — not
because Lean cannot elaborate it; the gate now rejects a control that fails for
the wrong reason.

## What this does not show

- **Not** that the ordering is wrong. 6.5 < 6.8 < 7.2 < 7.5 is untouched: an
  ordering can hold while its derivation is missing.
- **Not** that C₂ is not truth-inelastic. The conclusion that rejecting C₂
  forces an alternative of equal or higher debt is a *comparative* claim under a
  published metric; this file neither supports nor refutes it.
- **Not** anything about theology. A bookkeeping defect in a report is a defect
  in the report.
- **Not** that a weighting cannot rescue the numbers. A deliberately uneven
  weighting could put C₃ above C₂ with `Medium-High < High`. But such a weighting
  would be hidden, which is precisely what line 233 denies. Either way, one of
  the two lines is inaccurate — and that conclusion needs no arithmetic at all.

## Three repairs, none of them chosen here

Which one is intended is the author's call, not this tool's:

1. **Publish the per-axis numeric scores.** Then the totals are derived and this
   test is replaced by the real derivation. This is the only repair that makes
   the scores machine-checkable.
2. **Revise the totals** to the means of the published levels.
3. **Revise the levels** to be consistent with the published totals, under a
   declared mapping.

The second defect — C₁'s five categories against six — needs a stated
normalization under any of the three.

## Reproduce

```bash
cd burden && ./verify.sh          # gate 13 compiles the proof and runs the check
node dist/tools/inelasticity-check.js
lean L1_INELASTICITY.lean
```

The check exits `1`: the published totals disagree with the published levels.
That exit is the finding, not a failure of the tool. Exit `2` means the tool's
own arithmetic broke, and the gate fails on it.
