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

## Verify

```bash
./verify.sh
```

Six required gates:

1. `tsc --noEmit` under `strict`, `exactOptionalPropertyTypes`,
   `noUncheckedIndexedAccess`.
2. 85 tests. The five real-corpus tests **skip explicitly** when the corpus is
   absent, so a CI run reports `skipped: 1` rather than a silent zero.
3. `lean ../L1_LEDGER.lean` — the structural proof.
4. **The falsifier.** `negative/NEGATIVE_CONTROL.lean` attempts to build a
   `finding` on an `unverified` tier. It must fail to compile. If it ever
   succeeds, the invariant is vacuous and the gate fails.
5. **The custody guard.** No `evidence/fleites/*.pdf`, `*.txt`, or `*.csv` may
   be tracked by git.
6. **Custody against commitment.** `src/corpus.ts` hashes every file on disk
   and compares it to the published manifest: mismatch, missing, unlisted, and
   malformed are each reported, never silently absorbed. Skipped explicitly
   when no corpus is present.

A check that cannot fail is a comment. Gate 4 is what makes the others mean
something, and gates 5–6 are what keep the boundary from eroding by accident.

## Scope

What this proves: the ledger's **structure**, and — locally — that each
admitted quote appears where it says it does.

What this does not prove: that any filing exists, that any allegation is true,
or that any person did anything. Lean does not fetch PACER, and a verified
quote only proves that the document says it. Those are different claims, and
the ledger keeps them different.
