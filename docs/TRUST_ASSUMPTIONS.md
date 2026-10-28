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

---

## 5. The TLC model checker

`bds/tla/check.sh` runs TLC over `LaborSchedule.tla`. TLC is a different kind of
tool from a proof assistant, and its guarantees are different in a way worth
stating.

**What TLC gives:** exhaustive exploration of a *finite* state space. When it
reports "No error has been found" and the state queue is empty, every reachable
state was visited. For the infeasible paid-only instance that means: there is no
interleaving of paid work that completes the specification — for the modelled
instance, not for a class of instances.

**What TLC does not give:** a proof about unbounded or parameterised systems. The
instances checked are concrete integers (4 service days, 60 minutes per shift,
two task kinds). The *structural* claim generalises by argument; the *checked*
claim is the instance. Conflating the two would be the same error as calling a
`native_decide` result a kernel proof.

**Why the instances are small:** exhaustive checking is the point. A larger
instance would explore fewer of its own states per unit time and buy nothing —
the question is whether *any* interleaving completes, and 71 states is a complete
answer for that instance.

**The toolchain itself** is a 2.2 MB jar fetched on demand into a gitignored
directory and verified against a pinned SHA-256
(`d532ba31aafe17afba1130f92410d9257454ff7393d1eb2fe032f0c07f352da5`). An unpinned
download would make the check depend on whatever the network served that day,
which is the same class of unverified dependency the rest of this file exists to
prevent.

**Run 3 is the honesty control.** Without a feasible instance in which completion
*is* reachable, run 1 would be indistinguishable from a model that can never
complete anything. The gate requires all three results, and it fails if any is
missing.

---

## 6. The one Python file, and what binds it

`cage/worker/infer.py` is the only new Python in this repository. It runs the
local LoRA adapter. It is bound in three layers, and the layers do different
jobs.

**TypeScript binds the process** (`cage/src/supervise.ts`). The supervisor
launches exactly one program with a fixed argument vector — the worker cannot
choose its own file. It enforces:

| Failure mode | Bound |
| :--- | :--- |
| The worker hangs | wall-clock timeout, then `SIGKILL` |
| The worker floods stdout | byte cap, then `SIGKILL` |
| The worker crashes | non-zero exit is a `Rejection`, never a throw |
| The worker lies | every field validated by `admit` |
| The worker replays an old reply | nonce must echo the request |
| The worker binary is swapped | file hashed before each call |
| The worker writes to the caller's log | stderr drained and discarded |
| The worker phones home | `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1` |

Every one produces a stable rejection code. None escalates.

**Lean binds the gate** (`L4_CAGE.lean`, kernel-checked, no `sorry`, no
`native_decide`):

- `accepts_iff_admissible` — the gate accepts exactly the stated conditions
- `acceptance_requires_nonce` — replay is impossible
- `accepted_is_nonempty` — a blank cannot be admitted
- `rejection_always_has_reason` — no anonymous refusal is representable
- `confidence_irrelevant` — **a model's self-assessment cannot flip the outcome**
- `proposal_shape` — a `Proposal` carries text, worker hash, and confidence; no verdict field exists
- `gate_is_total` — every input is classified

**Nothing binds the computation.** What the network generates inside Python is
unverified. That is not a gap to close; it is why the model may only *propose*.
A proposal is a candidate for someone else to check.

### The observation that matters

Run live on 2026-10-27 through the real worker, prompt "Reply with exactly the
word: ready":

```
ok: true, worker: 83cac2aca880, text: "Reply with exactly the word: ready"
```

The adapter **echoed the prompt** instead of answering. The binding worked — the
process ran, the gate admitted a well-formed proposal — but the model's output
was not an answer. That is a fact about the adapter's quality, not about the
cage, and it is recorded rather than smoothed over.

Its consequence: the local model cannot yet be trusted even to *propose*
usefully. `selfReportedConfidence` is emitted as `0.0` because the worker has no
basis for a number, and the gate records that honestly rather than inventing one.
