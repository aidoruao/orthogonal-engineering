# L1 Claim Ledger

The published artifact of the Indictment corpus: a **claim** is a record that
commits to which document it came from, where in that document, the exact
words, and the hash of the source — so a hostile reader can fetch the source
themselves and check.

This directory contains the schema and the gate. It contains **no docket
rows**. See [`../docs/DATA_ISOLATION_BOUNDARY.md`](../docs/DATA_ISOLATION_BOUNDARY.md).

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

## Usage

```ts
import { admit, parseManifest } from "./src/index.js";

const manifest = parseManifest(manifestText);
const result = admit(candidate, manifest.hashes);

if (!result.ok) {
  for (const v of result.violations) {
    console.error(`${v.code} at ${v.path}: ${v.message}`);
  }
} else {
  // result.record is a ClaimRecord
}
```

`admit` never throws on bad input and never partially accepts. Violations are
sorted by path, so the same bad input always produces the same report.

## Verify

```bash
./verify.sh
```

Four required gates:

1. `tsc --noEmit` under `strict`, `exactOptionalPropertyTypes`,
   `noUncheckedIndexedAccess`.
2. 58 tests, including every rejection path.
3. `lean ../L1_LEDGER.lean` — the structural proof.
4. **The falsifier.** `negative/NEGATIVE_CONTROL.lean` attempts to build a
   `finding` on an `unverified` tier. It must fail to compile. If it ever
   succeeds, the invariant is vacuous and `verify.sh` exits non-zero.

A check that cannot fail is a comment. Gate 4 is what makes gates 1–3 mean
something.

## Scope

What this proves: the ledger's **structure**. A record cannot be malformed, and
an adjudication cannot rest on an allegation.

What this does not prove: that any filing exists, that any allegation is true,
or that any person did anything. Lean does not fetch PACER. Those are claims
about the world, and they must be fetched, hashed, and quoted — which is what
the ledger is for.
