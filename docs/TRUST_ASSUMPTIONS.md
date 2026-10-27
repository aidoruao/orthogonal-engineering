# Trust Assumptions in the Lean Surface

A Lean theorem is only as strong as what the kernel had to accept to check it.
Two things weaken that, and both are present in this repository. This file
inventories them so a reader can tell which claims are kernel-checked and which
are not.

## 1. `native_decide`

`decide` closes a goal by evaluating it inside the kernel. `native_decide`
compiles the proposition to native code, runs it, and accepts the result via an
axiom (`Lean.ofReduceBool`). It is fast and it is convenient, and it is **not a
kernel check**: it trusts the Lean compiler and the hardware that ran it.

That is a real, ordinary engineering trade-off. It is not a real problem until
someone describes the result as "mathematically verified" or "cannot be
refuted" without saying which of the two it is.

### Inventory — 18 files, 122 uses (2026-10-27)

| File | Uses | Disclosed in file |
| :--- | ---: | :--- |
| `L1_DOSSIER_CHECKS.lean` | 23 | yes, via `docs/TRUST_ASSUMPTIONS.md` |
| `RECONCILIATION_CHECKS.lean` | 14 | yes, via this file |
| `EPISTEMIC_POLICY.lean` | 13 | yes, via this file |
| `L3_FETCHED.lean` | 10 | yes, via this file |
| `L3_FAMILY.lean` | 8 | yes |
| `L1_ARCHITECTURE_MODULES_2_3.lean` | 8 | yes, via this file |
| `L3_GATHER.lean` | 7 | yes |
| `L3_DOCKET_TIMELINE.lean` | 6 | yes, via this file |
| `L1_LEDGER.lean` | 6 | yes |
| `D2_PLAYBOOK.lean` | 5 | yes |
| `L3_DEPOSITION_ENTRY.lean` | 4 | yes, via this file |
| `L3_MODEL.lean` | 4 | yes, via this file |
| `EVIDENCE_TIER.lean` | 4 | yes, via this file |
| `THE_INDICTMENT.lean` | 4 | yes, via this file |
| `L1_ARCHITECTURE.lean` | 3 | yes, via this file |
| `L3_PROBE.lean` | 3 | yes |
| `L3_ATTRIBUTION.lean` | 1 | yes — and see §3 |
| `L3_DISCHARGE.lean` | 2 | yes |

The count is a fact about the tree on that date. It will drift; the gate in
`bds/verify.sh` step 9 re-checks the disclosure requirement every run.

### Why the disclosure is enforced rather than encouraged

A silent trust assumption is indistinguishable, from a reader's position, from a
proof. The whole distinction the arc rests on — between a checked claim and a
confidence — collapses if the weaker mechanism is used without a note.

## 2. `sorry`

`sorry` closes any goal by admitting it. A file containing `sorry` compiles, and
what it compiles is not a proof of its theorems.

**Current state: `L3_MODEL.lean` has 8.** Its header calls them "the SHAPE" and
tracks them through `#print axioms`, which reports `sorryAx`. That disclosure is
correct and the gate requires it to remain.

The important qualification: **the attribution theorems do not rest on them.**
`#print axioms antoon_executive_attribution` returns no `sorryAx`. The concrete
attribution is discharged against real data even though the model file that
declares the shape still has open obligations.

## 3. What was actually improved on 2026-10-27

`L3_ATTRIBUTION.lean` names a real person, so it got more than disclosure:

- `antoon_couples_loop` was `native_decide`; it is now `decide`.
  `#print axioms` → **does not depend on any axioms.**
- `antoon_attribution_structural` and `antoon_mechanism_recorded` were added,
  giving the mechanism claim a kernel-checked witness. Both depend only on
  `propext`.
- `antoon_executive_attribution` still uses `native_decide` and now says so,
  because `executive_intent` matches a keyword inside free text and
  `String.contains` is not kernel-reducible.

So the file now carries two forms of the same claim: a strong structural one the
kernel checks, and a text-matching one that survives "where does the document say
that". Neither is dropped, and the difference between them is written down.

## 4. What a reader should conclude

- Claims closed by `decide`: checked by the kernel, modulo `propext`,
  `Classical.choice`, and `Quot.sound` where they appear.
- Claims closed by `native_decide`: true if the compiler and hardware behaved.
  Reasonable, and weaker. Treat them as high-confidence computation, not proof.
- Claims in a file with `sorry`: the file's other theorems may be fine; the
  sorried ones are unproven and are labelled as such.

The correct summary of this repository's Lean layer is: **a mix of
kernel-checked results and trusted computation, inventoried here.** Not
uniformly "mathematically verified". This file exists so nobody has to guess
which is which.
