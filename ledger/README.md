# L1 Claim Ledger

The published artifact of the Indictment corpus: a **claim** is a record that
commits to which document it came from, where in that document, the exact
words, and the hash of the source — so a hostile reader can fetch the source
themselves and check.

This directory contains the schema, the gate, and the local workbench. It
contains **no docket rows**. See
[`../docs/DATA_ISOLATION_BOUNDARY.md`](../docs/DATA_ISOLATION_BOUNDARY.md).

## Why a claim needs five things

| Field | What it stops |
| :--- | :--- |
| `docket` + `documentNumber` | A claim that cannot be located. |
| `page` | A quote that cannot be found. |
| `quote` | A summary masquerading as a quotation. |
| `sourceSha256` | A claim about a document the manifest does not commit to. |
| `nature` | An allegation presented as a finding. |

Drop any one and the record is not evidence. The gate rejects it.

## The rule that matters

`nature` is `allegation`, `order`, `finding`, `settlement`, or
`stated_intent`. Of these, **`order` and `finding` assert an adjudicated
outcome**, and both require a `fetched` tier.

A complaint asserts. A court decides. Treating those as the same thing is the
easiest way to publish something false while every quote is accurate, so the
rule is enforced twice:

- **At runtime** — `admit()` in `src/validate.ts` returns
  `adjudicated_requires_fetched`.
- **At the type level** — `L1_LEDGER.lean` gives `Record` a proof field, so an
  adjudicated record without a fetched source cannot be constructed.

`gate_matches_invariant` proves those two are the same proposition, so the
TypeScript and the Lean cannot silently drift apart.

## Two kinds of verification, deliberately separated

**Structural** (runs anywhere, including CI): is the record well formed, and
does its hash appear in the published manifest?

**Quotational** (runs only where the L0 corpus lives): does the quoted span
actually appear on the cited page of the file whose hash the claim names?

The split is the custody boundary. CI has no corpus and must not. Quote
verification happens on the machine that holds the evidence, before a claim is
ever committed — so the published artifact carries the verdict of a check that
could have failed.

## The selection is part of the record

Drafting locally and publishing some claims is only honest if the **selection**
is public too. Selective disclosure is a form of lying even when every
published quote is accurate.

Two published files, claim IDs only — never quote text, never source names:

- `candidates.jsonl` — every candidate that was drafted
- `selection.jsonl` — its disposition: `accepted`, `rejected` (with a code), or
  `withheld` (with a code)

`L1_SELECTION.lean` proves the invariant: `Selection` carries totality as a
proof field, so a ledger that drops a candidate or invents one **cannot be
constructed**. `partition_counts` proves accepted + rejected + withheld equals
the total, and `no_silent_drop` states the consequence — every drafted
candidate appears in the ledger.

A rejection is never anonymous: `rejected_has_code` requires a non-empty
reason. `SELECTION_DROP.lean` and `SELECTION_ANONYMOUS.lean` are the negative
controls, and both must fail to compile.

## Verification decays

A passing check is not a property of code. It is a claim indexed by the
environment it ran in — toolchain, lockfile, OS. When the environment moves the
claim does not become false; it becomes **unknown**.

`L1_DECAY.lean` proves the three consequences:

- **Staleness carries no information.** A verification at another environment
  reports `unknown`, whether it passed or failed. `stale_pass_is_unknown` and
  `stale_fail_is_unknown`.
- **Pinning works.** If the environment never moves, one verification covers
  every point. `pinned_one_verification_suffices`.
- **No finite schedule covers unbounded drift.** For any schedule there is an
  environment it never touched. `adversary_finds_a_gap`.

Hence the engineering rule, and gate 11:

> Pin what you can. Verify what you cannot pin. Know which is which.
> A stale pass is not a lie; treating it as current is.

`src/freshness.ts` records the environment a full verification passed in
(`VERIFIED_ENVIRONMENT.json`) and reports **STALE** — never failure, never a
pass — when the current environment differs.

## Usage

Structural admission:

```ts
import { admit, parseManifest } from "./src/index.js";

const manifest = parseManifest(manifestText);
const result = admit(candidate, manifest.hashes);
if (!result.ok) {
  for (const v of result.violations) {
    console.error(`${v.code} at ${v.path}: ${v.message}`);
  }
}
```

Local workbench, with quote verification:

```bash
node dist/src/workbench.js claim.json --sources ../evidence/fleites
```

Exit codes: `0` admitted and verified, `1` rejected, `2` usage or I/O error.
Without `--sources` the claim is admitted structurally and the tool says
plainly that the quote was **not** verified.

Check that local custody matches the published commitment:

```bash
node dist/src/corpus.js \
  --manifest ../evidence/fleites/FLEITES_MANIFEST.sha256 \
  --sources ../evidence/fleites
```

The corpus directory defaults to `../evidence/fleites` on this machine and can
be overridden with `OE_CORPUS_DIR`.

## Coverage compounds; claims accumulate

A ledger can grow in two ways that look identical by count and are opposite in
value: adding a claim about a document already covered, and adding a claim
about a document nobody has examined. Both increment "claims". Only one
increments "documents covered".

`L1_COVERAGE.lean` proves the distinction:

- **`addDoc_bounded`** — one claim adds at most one document.
- **`addDoc_zero_if_covered`** — a claim about a covered document adds nothing.
- **`addDoc_progress_if_dark`** — a claim about a dark document adds exactly one.
- **`snowball`** — from empty, N distinct documents cover exactly N.

`src/coverage.ts` reports both numbers, keeps them separate, and fails if any
claim cites a document the manifest does not commit to.

```bash
node dist/src/coverage.js --root ..
```

Current: **12 claims over 10 of 41 documents.** Two claims are redundant
(zero marginal coverage), and 31 documents are dark. The claim count is not the
measure of how much of the record has been read; the document count is.

## Verify

```bash
./verify.sh
```

Twelve required gates:

1. `tsc --noEmit` under `strict`, `exactOptionalPropertyTypes`,
   `noUncheckedIndexedAccess`.
2. **178 tests.** The five real-corpus tests skip explicitly when the corpus is
   absent, so a CI run reports a skip rather than a silent zero.
3. **Lean proofs** — `L1_LEDGER` (a finding cannot rest on an allegation),
   `L1_SELECTION` (a selection cannot drop a candidate), `L1_GATES` (adding a
   gate is weakly dominant; a vacuous or duplicate gate adds nothing), and
   `L1_DECAY` (a verification at another environment is `unknown`, not
   `failed`).
4. **Eight negative controls**, all of which must fail to compile. If any
   compiles, its invariant is vacuous and the gate fails:

   | Control | Asserted, and refuted |
   | :--- | :--- |
   | `NEGATIVE_CONTROL` | a finding on an unverified tier |
   | `SELECTION_DROP` | a ledger missing a candidate |
   | `SELECTION_ANONYMOUS` | a rejection with no reason |
   | `GATES_THEATRE` | a vacuous gate that rejects something |
   | `GATES_DOMINANCE` | adding a gate that increases evasion |
   | `DECAY_STALE` | a stale pass that still reports verified |
   | `DECAY_STALE_FAIL` | a stale failure that reports failed |
   | `COVERAGE_WASTE` | a repeat claim that adds a document |

5. **The custody guard.** No `evidence/fleites/*.pdf`, `*.txt`, or `*.csv` may
   be tracked by git.
6. **Custody against commitment.** `src/corpus.ts` hashes every file on disk
   and compares it to the published manifest: mismatch, missing, unlisted, and
   malformed are each reported, never silently absorbed.
7. **Claim coverage.** Claims and covered documents are reported separately.
   A claim citing a document outside the manifest fails the gate.
8. **Selection completeness.** If `candidates.jsonl` and `selection.jsonl`
   exist, every candidate must have exactly one disposition. A
   `selection.jsonl` without `candidates.jsonl` is a failure, not a skip.
9. **Citation audit.** Every published page cite must be verbatim or a
   `...`-marked elision. A paraphrase presented as a quotation fails the gate.
10. **Standards compliance** — 15 presence checks against the constitution and
   the corpus standards, including that `node_modules` is never tracked.
11. **Territory census** (optional, `OE_CENSUS_ROOT`) — a README's declared
    tree is compared to disk. Divergence is reported, never hidden.
12. **Verification freshness.** The current environment (node, TypeScript,
    Lean, lockfile hash) is compared to `VERIFIED_ENVIRONMENT.json`. A
    mismatch reports **STALE**, never failure — and never a pass.

```bash
# Record the environment in which a full verification actually passed.
node dist/src/freshness.js --root .. --update
```

A check that cannot fail is a comment. Gate 4 is what makes the others mean
something, and gates 5–12 are what keep the boundary from eroding by accident.

## Scope

What this proves: the ledger's **structure**, and — locally — that each
admitted quote appears where it says it does.

What this does not prove: that any filing exists, that any allegation is true,
or that any person did anything. Lean does not fetch PACER, and a verified
quote only proves that the document says it. Those are different claims, and
the ledger keeps them different.
